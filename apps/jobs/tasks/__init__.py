# apps/jobs/tasks/__init__.py
"""
Background task definitions for jobs application.
These tasks are thin wrappers that call application services.
"""

import asyncio
import logging
from typing import Dict, Any

from apps.jobs.worker import celery_app, jobs_container

logger = logging.getLogger(__name__)


@celery_app.task(name="process_analytics_data")
def process_analytics_data_task(data: dict) -> dict:
    """Process analytics data using application service."""
    
    async def _run() -> Dict[str, Any]:
        try:
            analytics_service = jobs_container.analytics_job_service()
            result = await analytics_service.process_analytics_data(data)
            return result
        except Exception as e:
            logger.error(f"Analytics task failed: {e}", exc_info=True)
            return {"status": "failed", "error": str(e), "processed_items": 0}
    
    return asyncio.run(_run())


@celery_app.task(name="deliver_scheduled_content")  
def deliver_scheduled_content_task(schedule_id: int) -> dict:
    """Deliver scheduled content using application service."""
    
    async def _run() -> Dict[str, Any]:
        try:
            delivery_service = jobs_container.delivery_job_service()
            result = await delivery_service.deliver_scheduled_content(schedule_id)
            return result
        except Exception as e:
            logger.error(f"Delivery task failed for schedule {schedule_id}: {e}", exc_info=True)
            return {"status": "failed", "schedule_id": schedule_id, "error": str(e)}
    
    return asyncio.run(_run())


@celery_app.task(name="cleanup_old_data")
def cleanup_old_data_task(days: int = 30) -> dict:
    """Cleanup old analytics data using application service."""
    
    async def _run() -> Dict[str, Any]:
        try:
            analytics_service = jobs_container.analytics_job_service()
            result = await analytics_service.cleanup_old_analytics_data(days)
            return result
        except Exception as e:
            logger.error(f"Cleanup task failed: {e}", exc_info=True)
            return {"status": "failed", "error": str(e), "cleaned_items": 0}
    
    return asyncio.run(_run())