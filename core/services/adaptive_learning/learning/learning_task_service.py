"""
Learning Task Service
====================

Clean architecture replacement for the monolithic LearningTaskService.
Delegates to specialized components while maintaining the original interface.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from core.services.adaptive_learning.protocols.learning_protocols import (
    LearningProgress,
    LearningProtocol,
    LearningStrategy,
    LearningTask,
)

from .learning_task_manager import LearningTaskManager, LearningTaskManagerConfig
from .model_training_executor import IncrementalLearningEngine, ModelTrainingExecutor
from .task_scheduler import TaskPriority

logger = logging.getLogger(__name__)


class LearningTaskService(LearningProtocol):
    """
    Clean, focused learning task service.

    Replaces the 830-line god object with a clean coordinator pattern.
    Maintains compatibility while delegating to specialized components.
    """

    def __init__(self, config: LearningTaskManagerConfig | None = None):
        # Create specialized components
        self.task_manager = LearningTaskManager(config)
        self.learning_engine = IncrementalLearningEngine()
        self.training_executor = ModelTrainingExecutor(self.learning_engine)

        # Service state
        self.is_running = False

        logger.info("🎯 Clean LearningTaskService initialized")

    async def start_learning_service(self) -> bool:
        """Start learning service"""
        try:
            # Start task manager
            if not await self.task_manager.start_manager():
                return False

            self.is_running = True
            logger.info("✅ LearningTaskService started")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start LearningTaskService: {e}")
            return False

    async def stop_learning_service(self) -> bool:
        """Stop learning service"""
        try:
            # Stop task manager
            await self.task_manager.stop_manager()

            self.is_running = False
            logger.info("⏹️ LearningTaskService stopped")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to stop LearningTaskService: {e}")
            return False

    async def create_learning_task(self, task: LearningTask) -> bool:
        """Create new learning task"""
        try:
            # Extract data from task object
            model_id = task.model_id
            strategy = task.strategy
            task_parameters = task.parameters or {}

            # Convert priority - assume normal for now
            task_priority = TaskPriority.NORMAL

            task_id = await self.task_manager.create_task(
                model_id=model_id,
                strategy=strategy,
                training_data=task_parameters.get("training_data", []),
                validation_data=task_parameters.get("validation_data"),
                priority=task_priority,
                dependencies=None,
                task_parameters=task_parameters,
            )

            return task_id is not None

        except Exception as e:
            logger.error(f"❌ Create learning task failed: {e}")
            return False

    async def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """Get task status"""
        return await self.task_manager.get_task_status(task_id)

    async def get_active_tasks(self, model_id: str | None = None) -> list[LearningTask]:
        """Get active learning tasks"""
        # For now, return empty list - would convert from internal format
        return []

    async def get_pending_tasks(self, model_id: str | None = None) -> list[dict[str, Any]]:
        """Get pending learning tasks"""
        return await self.task_manager.get_pending_tasks(model_id)

    async def cancel_task(self, task_id: str, reason: str = "User requested") -> bool:
        """Cancel learning task"""
        # Cancel in task manager
        manager_result = await self.task_manager.cancel_task(task_id, reason)

        # Cancel in training executor if active
        executor_result = await self.training_executor.cancel_execution(task_id)

        return manager_result or executor_result

    async def get_learning_statistics(self, model_id: str | None = None) -> dict[str, Any]:
        """Get learning statistics"""
        try:
            # Get statistics from task manager
            task_stats = await self.task_manager.get_task_statistics(model_id)

            # Get learning context information
            learning_contexts = {}
            if model_id:
                context = self.learning_engine.get_learning_context(model_id)
                if context:
                    learning_contexts[model_id] = {
                        "total_updates": context.learning_statistics.get("total_updates", 0),
                        "average_loss": context.learning_statistics.get("average_loss", 0.0),
                        "memory_buffer_size": len(context.memory_buffer),
                        "adaptation_history_length": len(context.adaptation_history),
                    }

            # Get execution statistics
            active_executions = self.training_executor.get_active_executions()

            return {
                "task_statistics": task_stats,
                "learning_contexts": learning_contexts,
                "active_executions": len(active_executions),
                "service_health": {
                    "task_manager": self.task_manager.get_service_health(),
                    "learning_engine": self.learning_engine.get_service_health(),
                    "training_executor": self.training_executor.get_service_health(),
                },
            }

        except Exception as e:
            logger.error(f"❌ Failed to get learning statistics: {e}")
            return {}

    # LearningProtocol implementation

    async def train_model(
        self,
        model_id: str,
        training_data: list[dict[str, Any]],
        validation_data: list[dict[str, Any]] | None = None,
        strategy: LearningStrategy = LearningStrategy.INCREMENTAL,
    ) -> LearningProgress:
        """Train model using specified strategy"""
        try:
            # Create task object
            from datetime import datetime

            from core.services.adaptive_learning.protocols.learning_protocols import (
                LearningTask,
            )

            task = LearningTask(
                task_id=f"train_{model_id}_{int(datetime.utcnow().timestamp())}",
                model_id=model_id,
                strategy=strategy,
                data_source="training_data",
                parameters={
                    "training_data": training_data,
                    "validation_data": validation_data,
                },
            )

            # Create task
            success = await self.create_learning_task(task)

            if not success:
                return LearningProgress(
                    task_id="",
                    model_id=model_id,
                    current_epoch=0,
                    total_epochs=0,
                    training_loss=float("inf"),
                    validation_metrics={},
                    timestamp=datetime.utcnow(),
                )

            # Wait for task to start and return initial progress
            await asyncio.sleep(0.1)  # Give task time to start

            status = await self.get_task_status(task.task_id)
            if status and "progress" in status:
                progress_data = status["progress"]
                return LearningProgress(
                    task_id=progress_data.get("task_id", task.task_id),
                    model_id=progress_data.get("model_id", model_id),
                    current_epoch=progress_data.get("current_epoch", 0),
                    total_epochs=progress_data.get("total_epochs", 10),
                    training_loss=progress_data.get("loss", 0.0),
                    validation_metrics=progress_data.get("metrics", {}),
                    timestamp=datetime.utcnow(),
                )

            # Fallback progress
            return LearningProgress(
                task_id=task.task_id,
                model_id=model_id,
                current_epoch=0,
                total_epochs=10,
                training_loss=0.0,
                validation_metrics={},
                timestamp=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"❌ Train model failed: {e}")
            return LearningProgress(
                task_id="",
                model_id=model_id,
                current_epoch=0,
                total_epochs=0,
                training_loss=float("inf"),
                validation_metrics={},
                timestamp=datetime.utcnow(),
            )

    async def get_learning_progress(self, task_id: str) -> LearningProgress | None:
        """Get learning progress for a task"""
        try:
            status = await self.get_task_status(task_id)
            if not status or "progress" not in status:
                return None

            progress_data = status["progress"]
            return LearningProgress(
                task_id=progress_data.get("task_id", task_id),
                model_id=progress_data.get("model_id", ""),
                current_epoch=progress_data.get("current_epoch", 0),
                total_epochs=progress_data.get("total_epochs", 0),
                training_loss=progress_data.get("loss", 0.0),
                validation_metrics=progress_data.get("metrics", {}),
                timestamp=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"❌ Failed to get learning progress: {e}")
            return None

    async def update_model_incremental(
        self,
        model_id: str,
        new_data: list[dict[str, Any]],
        learning_rate: float = 0.001,
    ) -> bool:
        """Update model incrementally with new data"""
        try:
            from core.services.adaptive_learning.protocols.learning_protocols import (
                LearningTask,
            )

            task = LearningTask(
                task_id=f"incremental_{model_id}_{int(datetime.utcnow().timestamp())}",
                model_id=model_id,
                strategy=LearningStrategy.INCREMENTAL,
                data_source="incremental_data",
                parameters={
                    "training_data": new_data,
                    "learning_rate": learning_rate,
                    "epochs": 1,  # Single epoch for incremental update
                },
            )

            success = await self.create_learning_task(task)
            return success

        except Exception as e:
            logger.error(f"❌ Incremental update failed: {e}")
            return False

    async def evaluate_model_performance(
        self, model_id: str, test_data: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Evaluate model performance on test data"""
        try:
            from core.services.adaptive_learning.protocols.learning_protocols import (
                LearningTask,
            )

            # Create evaluation task (using validation data field)
            task = LearningTask(
                task_id=f"eval_{model_id}_{int(datetime.utcnow().timestamp())}",
                model_id=model_id,
                strategy=LearningStrategy.INCREMENTAL,
                data_source="evaluation_data",
                parameters={
                    "training_data": [],  # No training, just evaluation
                    "validation_data": test_data,
                    "evaluation_only": True,
                },
            )

            success = await self.create_learning_task(task)

            if not success:
                return {}

            # Wait for evaluation to complete (simplified)
            max_wait = 30  # 30 seconds
            wait_time = 0

            while wait_time < max_wait:
                status = await self.get_task_status(task.task_id)
                if status and status.get("status") == "completed":
                    progress = status.get("progress", {})
                    return progress.get("metrics", {})
                elif status and status.get("status") == "failed":
                    logger.error(
                        f"❌ Evaluation failed: {status.get('error_message', 'Unknown error')}"
                    )
                    return {}

                await asyncio.sleep(1)
                wait_time += 1

            # Timeout
            await self.cancel_task(task.task_id, "Evaluation timeout")
            return {}

        except Exception as e:
            logger.error(f"❌ Model evaluation failed: {e}")
            return {}

    # Additional utility methods

    async def get_model_learning_context(self, model_id: str) -> dict[str, Any] | None:
        """Get learning context for a model"""
        try:
            context = self.learning_engine.get_learning_context(model_id)
            if not context:
                return None

            return {
                "model_id": context.model_id,
                "memory_buffer_size": len(context.memory_buffer),
                "task_boundaries": context.task_boundaries,
                "learning_statistics": context.learning_statistics,
                "adaptation_history_length": len(context.adaptation_history),
                "last_adaptation": (
                    context.adaptation_history[-1] if context.adaptation_history else None
                ),
            }

        except Exception as e:
            logger.error(f"❌ Failed to get learning context: {e}")
            return None

    async def clear_model_memory(self, model_id: str) -> bool:
        """Clear memory buffer for a model"""
        try:
            context = self.learning_engine.get_learning_context(model_id)
            if context:
                context.memory_buffer.clear()
                context.adaptation_history.clear()
                logger.info(f"🧹 Cleared memory for model: {model_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"❌ Failed to clear model memory: {e}")
            return False

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "service": "learning_task_service",
            "status": "healthy" if self.is_running else "stopped",
            "component_health": {
                "task_manager": self.task_manager.get_service_health(),
                "learning_engine": self.learning_engine.get_service_health(),
                "training_executor": self.training_executor.get_service_health(),
            },
        }

    async def shutdown(self) -> None:
        """Shutdown service"""
        try:
            await self.stop_learning_service()
            logger.info("🛑 LearningTaskService shutdown complete")

        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")
