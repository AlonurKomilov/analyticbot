# Prometheus metrics task - append to tasks.py
import asyncio
import logging
from bot.celery_app import celery_app, resilient_task
from bot.utils.error_handler import ErrorHandler, ErrorContext

logger = logging.getLogger(__name__)

async def cleanup_resources():
    """Clean up resources after task completion"""
    try:
        # Add any cleanup logic here
        pass
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

@resilient_task(name="bot.tasks.update_prometheus_metrics", bind=True)
def update_prometheus_metrics(self):  # type: ignore[override]
    """Periodic task to update Prometheus metrics"""
    async def _run() -> str:
        context = ErrorContext().add("task", "update_prometheus_metrics")
        
        try:
            from bot.services.prometheus_service import collect_system_metrics
            
            logger.info("Collecting Prometheus metrics")
            
            # Collect system and application metrics
            await collect_system_metrics()
            
            logger.info("Prometheus metrics collection completed")
            
            return "metrics-updated"
            
        except Exception as e:
            ErrorHandler.log_error(e, context)
            return "metrics-failed"
        finally:
            await cleanup_resources()

    return asyncio.run(_run())
