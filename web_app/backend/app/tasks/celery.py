"""
Celery application configuration for PDF processing tasks
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "pdf_extractor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.tasks.pdf_tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# Task routing (optional)
celery_app.conf.task_routes = {
    'app.tasks.pdf_tasks.*': {'queue': 'pdf_processing'},
}

# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    'cleanup-old-files': {
        'task': 'app.tasks.pdf_tasks.cleanup_old_files_task',
        'schedule': 86400.0,  # Run daily (every 24 hours)
    },
    'reset-monthly-usage': {
        'task': 'app.tasks.pdf_tasks.reset_monthly_usage_task',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),  # First day of each month at midnight
    },
}

celery_app.conf.timezone = 'UTC'

if __name__ == '__main__':
    celery_app.start()