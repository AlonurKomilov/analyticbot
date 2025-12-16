"""
Task Processor Service
=====================

Microservice responsible for async task processing.
Handles background prediction tasks via Celery integration.
"""

import logging
from datetime import datetime
from typing import Any

from core.ports.task_client_port import TaskClientProtocol

from .models import (
    HealthMetrics,
    PredictionRequest,
    ServiceHealth,
    TaskProcessorProtocol,
)

logger = logging.getLogger(__name__)


class TaskProcessor(TaskProcessorProtocol):
    """
    Async task processing service for growth predictions.

    Single responsibility: Handle background task queue processing.
    """

    def __init__(self, task_client: TaskClientProtocol | None = None):
        self.task_client = task_client

        # Health tracking
        self.health_metrics = HealthMetrics()
        self.tasks_submitted = 0
        self.tasks_completed = 0

        logger.info("🔄 Task Processor initialized")

    async def process_async_prediction(self, request: PredictionRequest) -> str:
        """
        Submit prediction request to async task queue

        Args:
            request: Prediction request to process asynchronously

        Returns:
            Task ID for tracking the async operation
        """
        try:
            logger.info("📤 Submitting prediction task to queue")

            if self.task_client is None:
                raise RuntimeError("Task client not configured")

            # Prepare task parameters
            task_params = {
                "data": self._serialize_request_data(request),
                "forecast_periods": request.forecast_periods,
                "confidence_interval": request.confidence_interval,
                "include_uncertainty": request.include_uncertainty,
                "submitted_at": datetime.utcnow().isoformat(),
            }

            # Submit to task queue
            task_id = await self.task_client.submit_task_async(
                task_name="growth_prediction", **task_params
            )

            # Update metrics
            self.tasks_submitted += 1
            self.health_metrics.successful_predictions += 1
            self.health_metrics.last_prediction_time = datetime.utcnow()

            logger.info(f"✅ Task submitted with ID: {task_id}")
            return task_id

        except Exception as e:
            self.health_metrics.failed_predictions += 1
            logger.error(f"❌ Task submission failed: {e}")
            raise

    async def get_task_status(self, task_id: str) -> dict[str, Any]:
        """
        Get status of async prediction task

        Args:
            task_id: ID of the task to check

        Returns:
            Task status information
        """
        try:
            if self.task_client is None:
                raise RuntimeError("Task client not configured")

            status = await self.task_client.get_task_status(task_id)

            logger.debug(f"📊 Task {task_id} status: {status.get('state', 'unknown')}")
            return status

        except Exception as e:
            logger.error(f"❌ Task status check failed: {e}")
            return {"state": "error", "error": str(e)}

    async def get_task_result(self, task_id: str) -> dict[str, Any] | None:
        """
        Get result of completed async prediction task

        Args:
            task_id: ID of the completed task

        Returns:
            Task result if available, None otherwise
        """
        try:
            if self.task_client is None:
                raise RuntimeError("Task client not configured")

            status = await self.task_client.get_task_status(task_id)

            if status and status.get("status") == "completed":
                result = status.get("result")
                if result:
                    self.tasks_completed += 1
                    logger.info(f"✅ Retrieved result for task: {task_id}")
                return result

            return None

        except Exception as e:
            logger.error(f"❌ Task result retrieval failed: {e}")
            return None

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending async prediction task

        Args:
            task_id: ID of the task to cancel

        Returns:
            True if cancellation successful
        """
        try:
            if self.task_client is None:
                raise RuntimeError("Task client not configured")

            success = await self.task_client.cancel_task(task_id)

            if success:
                logger.info(f"🚫 Task cancelled: {task_id}")
            else:
                logger.warning(f"⚠️ Task cancellation failed: {task_id}")

            return success

        except Exception as e:
            logger.error(f"❌ Task cancellation failed: {e}")
            return False

    def get_task_stats(self) -> dict[str, Any]:
        """Get task processing statistics"""
        try:
            completion_rate = (
                self.tasks_completed / self.tasks_submitted if self.tasks_submitted > 0 else 0.0
            )

            return {
                "tasks_submitted": self.tasks_submitted,
                "tasks_completed": self.tasks_completed,
                "completion_rate": completion_rate,
                "pending_tasks": self.tasks_submitted - self.tasks_completed,
                "client_available": self.task_client is not None,
            }

        except Exception as e:
            logger.error(f"❌ Task stats calculation failed: {e}")
            return {}

    def get_health(self) -> ServiceHealth:
        """Get task processor health status"""
        try:
            stats = self.get_task_stats()

            # Healthy if client is available and completion rate is reasonable
            is_healthy = (
                self.task_client is not None
                and stats.get("completion_rate", 0) >= 0.8
                or stats.get("tasks_submitted", 0) < 5
            )

            return ServiceHealth(
                service_name="task_processor",
                is_healthy=is_healthy,
                metrics=self.health_metrics,
                last_check=datetime.utcnow(),
            )

        except Exception as e:
            return ServiceHealth(
                service_name="task_processor",
                is_healthy=False,
                metrics=HealthMetrics(),
                error_message=str(e),
            )

    # Private helper methods

    def _serialize_request_data(self, request: PredictionRequest) -> Any:
        """Serialize request data for task queue"""
        try:
            import pandas as pd

            if isinstance(request.data, pd.DataFrame):
                return request.data.to_dict("records")
            elif isinstance(request.data, (list, dict)):
                return request.data
            else:
                return str(request.data)

        except Exception as e:
            logger.error(f"❌ Request data serialization failed: {e}")
            return {}
