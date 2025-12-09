"""Celery tasks for PDF generation with retry logic and error handling."""
import logging
import os
import uuid
from typing import Dict, Any
from celery import Task
from app.tasks import celery_app
from app.renderer.engine import render_pdf_sync
from app.utils.storage import StorageBackend
from config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class PDFGenerationTask(Task):
    """Base task with retry logic and error handling."""

    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 5}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True


@celery_app.task(base=PDFGenerationTask, bind=True, name='app.tasks.render_pdf')
def render_pdf_task(self, job_id: str, render_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async task to render PDF.

    Args:
        self: Celery task instance
        job_id: Unique job identifier
        render_params: Parameters for PDF rendering

    Returns:
        Dict with job status and result
    """
    try:
        logger.info(f"Starting PDF rendering for job {job_id}")

        # Update job metadata
        self.update_state(
            state='PROCESSING',
            meta={'job_id': job_id, 'status': 'rendering'}
        )

        # Add config to params
        render_params['config'] = config

        # Render PDF
        pdf_bytes = render_pdf_sync(**render_params)

        # Store PDF
        storage = StorageBackend(config)
        file_path = storage.save_pdf(job_id, pdf_bytes)

        # Generate download URL
        download_url = storage.get_download_url(job_id)

        logger.info(f"PDF rendering completed for job {job_id}: {len(pdf_bytes)} bytes")

        return {
            'job_id': job_id,
            'status': 'completed',
            'file_path': file_path,
            'download_url': download_url,
            'size_bytes': len(pdf_bytes),
        }

    except Exception as e:
        logger.error(f"PDF rendering failed for job {job_id}: {e}", exc_info=True)

        # Update state to failed
        self.update_state(
            state='FAILURE',
            meta={'job_id': job_id, 'status': 'failed', 'error': str(e)}
        )

        raise


@celery_app.task(name='app.tasks.cleanup_old_pdfs')
def cleanup_old_pdfs():
    """Periodic task to cleanup old PDF files."""
    try:
        storage = StorageBackend(config)
        deleted_count = storage.cleanup_old_files(max_age_hours=config.JOB_RESULT_TTL // 3600)
        logger.info(f"Cleaned up {deleted_count} old PDF files")
        return {'deleted_count': deleted_count}
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}", exc_info=True)
        raise
