"""
Celery worker entry point.
Run with: celery -A celery_worker.celery_app worker --loglevel=info
"""
from app.tasks import celery_app
from config import get_config

# Load config
config = get_config()

if __name__ == '__main__':
    celery_app.start()
