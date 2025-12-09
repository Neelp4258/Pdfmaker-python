"""Celery tasks for async PDF generation."""
from celery import Celery
from config import get_config

config = get_config()

celery_app = Celery(
    'html2pdf',
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer=config.CELERY_TASK_SERIALIZER,
    result_serializer=config.CELERY_RESULT_SERIALIZER,
    accept_content=config.CELERY_ACCEPT_CONTENT,
    timezone=config.CELERY_TIMEZONE,
    task_track_started=config.CELERY_TASK_TRACK_STARTED,
    task_time_limit=config.CELERY_TASK_TIME_LIMIT,
    worker_concurrency=config.CELERY_WORKER_CONCURRENCY,
)

# Import tasks to register them
from app.tasks import pdf_tasks

__all__ = ['celery_app']
