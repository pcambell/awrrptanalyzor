"""Celery Application Configuration"""

from celery import Celery
from app.config import settings

# Create Celery instance
celery_app = Celery(
    "awrrptanalyzor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.parse_tasks",
        "app.tasks.analysis_tasks",
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=540,  # 9 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.parse_tasks.*": {"queue": "parse"},
    "app.tasks.analysis_tasks.*": {"queue": "analysis"},
}
