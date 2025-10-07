# apps/jobs/worker.py
"""
Celery worker entry point for background jobs.
Composition root for jobs application.
"""

import logging

from celery import Celery

from apps.jobs.di import configure_jobs_container
from config.settings import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "analyticbot-jobs",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["apps.jobs.tasks"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Initialize DI container for jobs
jobs_container = configure_jobs_container()

# Export for tasks to use
__all__ = ["celery_app", "jobs_container"]


if __name__ == "__main__":
    celery_app.start()
