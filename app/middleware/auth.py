"""API key authentication middleware."""
from functools import wraps
from flask import request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)


def require_api_key(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config['API_KEY_REQUIRED']:
            return f(*args, **kwargs)

        # Get API key from header or query param
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')

        if not api_key:
            logger.warning(f"Missing API key from {request.remote_addr}")
            return jsonify({
                'error': 'Missing API key',
                'message': 'Provide API key in X-API-Key header or api_key query parameter'
            }), 401

        if api_key not in current_app.config['API_KEYS']:
            logger.warning(f"Invalid API key from {request.remote_addr}")
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 403

        # Store API key in request context
        request.api_key = api_key

        return f(*args, **kwargs)

    return decorated_function


def init_auth(app):
    """Initialize authentication for the app."""
    logger.info(f"API key authentication: {'enabled' if app.config['API_KEY_REQUIRED'] else 'disabled'}")

    if app.config['API_KEY_REQUIRED'] and not app.config['API_KEYS']:
        logger.warning("API_KEY_REQUIRED is True but no API keys are configured!")
