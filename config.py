"""
Configuration module for HTML2PDF service.
All settings are configurable via environment variables for production deployment.
"""
import os
from typing import Optional


class Config:
    """Base configuration with sensible production defaults."""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32).hex())
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))

    # API Security
    API_KEY_REQUIRED = os.getenv('API_KEY_REQUIRED', 'True').lower() == 'true'
    API_KEYS = os.getenv('API_KEYS', '').split(',') if os.getenv('API_KEYS') else []

    # Rate limiting (requests per minute per API key)
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '1000'))

    # Upload limits (no artificial limits by default, make configurable)
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_UPLOAD_SIZE_MB', '100')) * 1024 * 1024  # Default 100MB
    MAX_HTML_SIZE = int(os.getenv('MAX_HTML_SIZE_MB', '50')) * 1024 * 1024  # Default 50MB

    # Job processing timeouts
    SYNC_JOB_TIMEOUT = int(os.getenv('SYNC_JOB_TIMEOUT_SEC', '30'))  # 30 seconds for sync
    ASYNC_JOB_TIMEOUT = int(os.getenv('ASYNC_JOB_TIMEOUT_SEC', '600'))  # 10 minutes for async

    # Celery configuration
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = ASYNC_JOB_TIMEOUT + 60  # Add buffer
    CELERY_WORKER_CONCURRENCY = int(os.getenv('CELERY_WORKER_CONCURRENCY', '4'))

    # Redis for caching and job status
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
    JOB_RESULT_TTL = int(os.getenv('JOB_RESULT_TTL_SEC', '3600'))  # 1 hour

    # Storage for generated PDFs
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local')  # local, s3, gcs
    STORAGE_PATH = os.getenv('STORAGE_PATH', '/tmp/html2pdf')
    S3_BUCKET = os.getenv('S3_BUCKET', '')
    S3_REGION = os.getenv('S3_REGION', 'us-east-1')
    GCS_BUCKET = os.getenv('GCS_BUCKET', '')

    # Playwright/Chromium settings
    CHROMIUM_ARGS = [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu',
    ]
    CHROMIUM_POOL_SIZE = int(os.getenv('CHROMIUM_POOL_SIZE', '4'))
    CHROMIUM_TIMEOUT = int(os.getenv('CHROMIUM_TIMEOUT_MS', '30000'))

    # Security settings for URL rendering
    ALLOW_URL_RENDERING = os.getenv('ALLOW_URL_RENDERING', 'True').lower() == 'true'
    URL_ALLOWLIST = os.getenv('URL_ALLOWLIST', '').split(',') if os.getenv('URL_ALLOWLIST') else []
    URL_DENYLIST = os.getenv('URL_DENYLIST', '127.0.0.1,localhost,0.0.0.0,169.254.169.254').split(',')
    DISABLE_JAVASCRIPT = os.getenv('DISABLE_JAVASCRIPT', 'False').lower() == 'true'
    NETWORK_ISOLATION = os.getenv('NETWORK_ISOLATION', 'False').lower() == 'true'

    # HTML sanitization
    SANITIZE_HTML = os.getenv('SANITIZE_HTML', 'True').lower() == 'true'
    ALLOW_INLINE_SCRIPTS = os.getenv('ALLOW_INLINE_SCRIPTS', 'False').lower() == 'true'

    # Default PDF settings
    DEFAULT_FORMAT = os.getenv('DEFAULT_FORMAT', 'A4')
    DEFAULT_DPI = int(os.getenv('DEFAULT_DPI', '96'))

    # Monitoring and logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    SENTRY_DSN = os.getenv('SENTRY_DSN', '')

    @classmethod
    def validate(cls):
        """Validate critical configuration settings."""
        if cls.API_KEY_REQUIRED and not cls.API_KEYS:
            raise ValueError("API_KEY_REQUIRED is True but no API_KEYS are configured!")

        os.makedirs(cls.STORAGE_PATH, exist_ok=True)

        return True


class DevelopmentConfig(Config):
    """Development configuration with debug enabled."""
    DEBUG = True
    API_KEY_REQUIRED = False
    RATE_LIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration with strict security."""
    DEBUG = False
    API_KEY_REQUIRED = True
    RATE_LIMIT_ENABLED = True


class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    DEBUG = True
    API_KEY_REQUIRED = False
    RATE_LIMIT_ENABLED = False
    CELERY_TASK_ALWAYS_EAGER = True


def get_config(env: Optional[str] = None) -> Config:
    """Get configuration based on environment."""
    env = env or os.getenv('FLASK_ENV', 'production')

    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'test': TestConfig,
    }

    config_class = configs.get(env, ProductionConfig)
    config_class.validate()

    return config_class
