"""
Celery Task Client Adapter
==========================

Infrastructure adapter that implements TaskClientProtocol for Celery task queue.

This adapter bridges the CORE layer (which defines the protocol) with the
APPS layer (which has the actual Celery tasks).
"""

import logging
from typing import Any

from core.ports.task_client_port import TaskClientProtocol, TaskSubmissionError

logger = logging.getLogger(__name__)


class CeleryTaskAdapter(TaskClientProtocol):
    """
    Adapter that implements TaskClientProtocol using Celery.

    This adapter lives in the INFRA layer and can import from APPS,
    allowing CORE to remain independent of APPS.
    """

    def __init__(self):
        """Initialize the Celery task adapter"""
        self._celery_available = self._check_celery_availability()
        if self._celery_available:
            logger.info("✅ Celery task adapter initialized")
        else:
            logger.warning("⚠️  Celery not available - tasks will fail")

    def _check_celery_availability(self) -> bool:
        """Check if Celery is available"""
        try:
            pass

            return True
        except ImportError as e:
            logger.warning(f"Celery tasks not available: {e}")
            return False

    def submit_task(self, task_name: str, **task_kwargs: Any) -> str:
        """
        Submit a task to Celery synchronously.

        Args:
            task_name: Name of the task to execute
            **task_kwargs: Keyword arguments to pass to the task

        Returns:
            Task ID for status checking

        Raises:
            TaskSubmissionError: If task submission fails
        """
        try:
            if not self._celery_available:
                raise TaskSubmissionError("Celery is not available")

            # Import here to avoid circular dependencies
            from apps.celery.tasks.ml_tasks import submit_ml_task_async

            task_id = submit_ml_task_async(task_name, **task_kwargs)
            logger.info(f"📤 Task submitted (sync): {task_id}")

            return task_id

        except Exception as e:
            logger.error(f"❌ Failed to submit task: {e}")
            raise TaskSubmissionError(f"Failed to submit task '{task_name}': {e}")

    async def submit_task_async(self, task_name: str, **task_kwargs: Any) -> str:
        """
        Submit a task to Celery asynchronously.

        Args:
            task_name: Name of the task to execute
            **task_kwargs: Keyword arguments to pass to the task

        Returns:
            Task ID for status checking

        Raises:
            TaskSubmissionError: If task submission fails
        """
        try:
            if not self._celery_available:
                raise TaskSubmissionError("Celery is not available")

            # Import here to avoid circular dependencies
            from apps.celery.tasks.ml_tasks import submit_ml_task_async

            task_id = submit_ml_task_async(task_name, **task_kwargs)
            logger.info(f"📤 Task submitted (async): {task_id}")

            return task_id

        except Exception as e:
            logger.error(f"❌ Failed to submit task: {e}")
            raise TaskSubmissionError(f"Failed to submit task '{task_name}': {e}")

    async def get_task_status(self, task_id: str) -> dict[str, Any]:
        """
        Get the status of a submitted Celery task.

        Args:
            task_id: Task ID to check

        Returns:
            Dictionary with task status information
        """
        try:
            if not self._celery_available:
                return {
                    "task_id": task_id,
                    "status": "error",
                    "error": "Celery is not available",
                }

            # Import Celery app
            from apps.celery.celery_app import celery_app

            # Get task result
            task_result = celery_app.AsyncResult(task_id)

            # Map Celery states to our protocol states
            status_map = {
                "PENDING": "pending",
                "STARTED": "processing",
                "SUCCESS": "completed",
                "FAILURE": "failed",
                "RETRY": "processing",
                "REVOKED": "cancelled",
            }

            status = status_map.get(task_result.state, "unknown")

            result_dict = {
                "task_id": task_id,
                "status": status,
                "result": None,
                "error": None,
            }

            # Add result or error if available
            if task_result.successful():
                result_dict["result"] = task_result.result
            elif task_result.failed():
                result_dict["error"] = str(task_result.info)

            return result_dict

        except Exception as e:
            logger.error(f"❌ Failed to get task status: {e}")
            return {"task_id": task_id, "status": "error", "error": str(e)}

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running Celery task.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if cancelled successfully, False otherwise
        """
        try:
            if not self._celery_available:
                logger.warning("Cannot cancel task - Celery not available")
                return False

            # Import Celery app
            from apps.celery.celery_app import celery_app

            # Revoke the task
            celery_app.control.revoke(task_id, terminate=True)

            logger.info(f"🛑 Task cancelled: {task_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to cancel task: {e}")
            return False


# Convenience function for creating the adapter
def create_celery_task_client() -> TaskClientProtocol:
    """
    Factory function to create a Celery task client adapter.

    Returns:
        TaskClientProtocol implementation using Celery
    """
    return CeleryTaskAdapter()
