"""
Flask API routes for HTML2PDF service.
Provides sync and async PDF rendering endpoints with comprehensive parameter support.
"""
import logging
import uuid
import asyncio
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.exceptions import BadRequest
from app.middleware.auth import require_api_key
from app.middleware.rate_limiter import rate_limit
from app.renderer.engine import PDFRenderer, render_pdf_sync
from app.tasks.pdf_tasks import render_pdf_task
from app.utils.storage import StorageBackend
from celery.result import AsyncResult
from app.tasks import celery_app
import io

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)


def parse_render_params(data: dict) -> dict:
    """
    Parse and validate rendering parameters from request.

    Args:
        data: Request data dict

    Returns:
        Validated parameters dict

    Raises:
        BadRequest: If parameters are invalid
    """
    # Validate required fields
    html = data.get('html')
    url = data.get('url')

    if not html and not url:
        raise BadRequest("Either 'html' or 'url' must be provided")

    if html and url:
        raise BadRequest("Provide either 'html' or 'url', not both")

    # Check HTML size limit
    if html and len(html.encode('utf-8')) > current_app.config['MAX_HTML_SIZE']:
        raise BadRequest(f"HTML size exceeds limit of {current_app.config['MAX_HTML_SIZE'] // (1024*1024)}MB")

    # Build params
    params = {
        'html': html,
        'url': url,
        'format': data.get('format', current_app.config['DEFAULT_FORMAT']),
        'width': data.get('width'),
        'height': data.get('height'),
        'aspect': data.get('aspect'),
        'landscape': data.get('landscape', False),
        'margin': data.get('margin'),
        'scale': float(data.get('scale', 1.0)),
        'page_ranges': data.get('page_ranges'),
        'css': data.get('css'),
        'wait_for': data.get('wait_for'),
        'headers': data.get('headers', {}),
    }

    # Validate scale
    if not 0.1 <= params['scale'] <= 2.0:
        raise BadRequest("Scale must be between 0.1 and 2.0")

    return params


@api_bp.route('/render', methods=['POST'])
@require_api_key
@rate_limit
def render_pdf_async():
    """
    Async PDF rendering endpoint - queues job and returns job_id.

    Request body (JSON or multipart):
    {
        "html": "HTML content" OR "url": "https://example.com",
        "format": "A4|A3|Letter|Legal|receipt",
        "width": "210mm|8.5in|800px",
        "height": "297mm|11in|1200px",
        "aspect": "16:9|16:10|4:3",
        "landscape": false,
        "margin": "10mm" or "10mm,20mm,10mm,20mm",
        "scale": 1.0,
        "page_ranges": "1-5, 8, 11-13",
        "css": "additional CSS to inject",
        "wait_for": "#selector" or "5000" (ms),
        "headers": {"Header": "Value"}
    }

    Returns:
        {
            "job_id": "uuid",
            "status": "queued",
            "status_url": "/status/<job_id>"
        }
    """
    try:
        # Parse request data (support both JSON and form data)
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        # Parse and validate parameters
        render_params = parse_render_params(data)

        # Generate job ID
        job_id = str(uuid.uuid4())

        logger.info(f"Queueing PDF render job {job_id}")

        # Queue async task
        task = render_pdf_task.apply_async(
            args=[job_id, render_params],
            task_id=job_id
        )

        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'status_url': f'/status/{job_id}',
            'task_id': task.id
        }), 202

    except BadRequest as e:
        logger.warning(f"Bad request: {e}")
        return jsonify({'error': 'Bad request', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Error queueing render job: {e}", exc_info=True)
        return jsonify({'error': 'Internal error', 'message': 'Failed to queue render job'}), 500


@api_bp.route('/render-sync', methods=['POST'])
@require_api_key
@rate_limit
def render_pdf_sync_endpoint():
    """
    Synchronous PDF rendering endpoint - returns PDF immediately.
    Suitable for small jobs with timeout limit.

    Request body: Same as /render

    Returns:
        PDF file stream (application/pdf)
    """
    try:
        # Parse request data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        # Parse and validate parameters
        render_params = parse_render_params(data)

        # Add config
        render_params['config'] = current_app.config

        logger.info(f"Rendering PDF synchronously")

        # Render PDF with timeout
        try:
            pdf_bytes = render_pdf_sync(**render_params)
        except Exception as e:
            logger.error(f"Rendering failed: {e}", exc_info=True)
            return jsonify({
                'error': 'Rendering failed',
                'message': str(e)
            }), 500

        # Return PDF as response
        pdf_io = io.BytesIO(pdf_bytes)
        pdf_io.seek(0)

        # Generate filename
        filename = f"document-{uuid.uuid4().hex[:8]}.pdf"

        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except BadRequest as e:
        logger.warning(f"Bad request: {e}")
        return jsonify({'error': 'Bad request', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Error rendering PDF: {e}", exc_info=True)
        return jsonify({'error': 'Internal error', 'message': 'Failed to render PDF'}), 500


@api_bp.route('/status/<job_id>', methods=['GET'])
@require_api_key
def get_job_status(job_id: str):
    """
    Get status of PDF generation job.

    Returns:
        {
            "job_id": "uuid",
            "status": "queued|running|completed|failed",
            "download_url": "/download/<job_id>",  // if completed
            "error": "error message",  // if failed
            "progress": {
                "current": 1,
                "total": 5
            }
        }
    """
    try:
        # Get task result
        task_result = AsyncResult(job_id, app=celery_app)

        status_map = {
            'PENDING': 'queued',
            'STARTED': 'running',
            'PROCESSING': 'running',
            'SUCCESS': 'completed',
            'FAILURE': 'failed',
            'RETRY': 'running',
        }

        status = status_map.get(task_result.state, 'unknown')

        response = {
            'job_id': job_id,
            'status': status,
            'state': task_result.state,
        }

        if status == 'completed':
            result = task_result.result
            response['download_url'] = f'/download/{job_id}'
            response['size_bytes'] = result.get('size_bytes')

        elif status == 'failed':
            response['error'] = str(task_result.info)

        elif status == 'running':
            if task_result.info:
                response['progress'] = task_result.info.get('progress', {})

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error getting job status: {e}", exc_info=True)
        return jsonify({'error': 'Internal error', 'message': 'Failed to get job status'}), 500


@api_bp.route('/download/<job_id>', methods=['GET'])
@require_api_key
def download_pdf(job_id: str):
    """
    Download generated PDF file.

    Returns:
        PDF file stream
    """
    try:
        # Get PDF from storage
        storage = StorageBackend(current_app.config)
        pdf_bytes = storage.get_pdf(job_id)

        if not pdf_bytes:
            return jsonify({
                'error': 'Not found',
                'message': 'PDF not found. It may have expired or the job may not be completed yet.'
            }), 404

        pdf_io = io.BytesIO(pdf_bytes)
        pdf_io.seek(0)

        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{job_id}.pdf'
        )

    except Exception as e:
        logger.error(f"Error downloading PDF: {e}", exc_info=True)
        return jsonify({'error': 'Internal error', 'message': 'Failed to download PDF'}), 500


@api_bp.route('/batch', methods=['POST'])
@require_api_key
@rate_limit
def render_batch():
    """
    Batch PDF rendering endpoint - queue multiple jobs at once.

    Request body:
    {
        "jobs": [
            {"html": "...", "format": "A4", ...},
            {"url": "...", "format": "Letter", ...}
        ]
    }

    Returns:
        {
            "jobs": [
                {"job_id": "uuid", "status_url": "/status/<job_id>"},
                ...
            ]
        }
    """
    try:
        data = request.get_json()
        jobs = data.get('jobs', [])

        if not jobs:
            raise BadRequest("No jobs provided")

        if len(jobs) > 100:
            raise BadRequest("Maximum 100 jobs per batch")

        results = []

        for job_data in jobs:
            try:
                render_params = parse_render_params(job_data)
                job_id = str(uuid.uuid4())

                task = render_pdf_task.apply_async(
                    args=[job_id, render_params],
                    task_id=job_id
                )

                results.append({
                    'job_id': job_id,
                    'status': 'queued',
                    'status_url': f'/status/{job_id}'
                })

            except Exception as e:
                results.append({
                    'error': str(e),
                    'status': 'failed'
                })

        return jsonify({'jobs': results}), 202

    except BadRequest as e:
        return jsonify({'error': 'Bad request', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Error queueing batch jobs: {e}", exc_info=True)
        return jsonify({'error': 'Internal error', 'message': 'Failed to queue batch jobs'}), 500


@api_bp.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors."""
    return jsonify({
        'error': 'Request too large',
        'message': f'Request size exceeds {current_app.config["MAX_CONTENT_LENGTH"] // (1024*1024)}MB limit'
    }), 413


@api_bp.errorhandler(500)
def internal_error(error):
    """Handle internal errors."""
    logger.error(f"Internal error: {error}", exc_info=True)
    return jsonify({
        'error': 'Internal error',
        'message': 'An internal error occurred'
    }), 500
