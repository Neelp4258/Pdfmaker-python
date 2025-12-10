"""HTML2PDF Flask application factory."""
from flask import Flask
from config import get_config
import logging
import os


def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)

    # Initialize extensions
    from app.middleware.auth import init_auth
    from app.middleware.rate_limiter import init_rate_limiter

    init_auth(app)
    init_rate_limiter(app)

    # Health check endpoint
    @app.route('/health')
    def health():
        health_status = {
            'status': 'healthy',
            'service': 'html2pdf',
            'celery': 'unknown',
            'redis': 'unknown'
        }

        # Check Redis/Celery availability
        try:
            from app.tasks import celery_app
            # Try to inspect Celery
            inspect = celery_app.control.inspect(timeout=1.0)
            if inspect and inspect.ping():
                health_status['celery'] = 'available'
                health_status['redis'] = 'connected'
            else:
                health_status['celery'] = 'no workers'
                health_status['redis'] = 'connected'
        except Exception as e:
            health_status['celery'] = 'unavailable'
            health_status['redis'] = 'disconnected'
            health_status['async_mode'] = 'disabled'

        return health_status, 200

    return app
