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
        return {'status': 'healthy', 'service': 'html2pdf'}, 200

    return app
