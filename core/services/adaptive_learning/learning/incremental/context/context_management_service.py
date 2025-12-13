"""
Context Management Service
==========================

Microservice responsible for managing learning contexts and adaptation history.

Single Responsibility: Learning context operations only.
"""

import logging
from datetime import datetime
from typing import Any

from ....protocols.learning_protocols import LearningContext, LearningStrategy
from ..models import (
    IncrementalLearningConfig,
    LearningResult,
)

logger = logging.getLogger(__name__)


class ContextManagementService:
    """
    Learning context management microservice.

    Responsibilities:
    - Initialize learning contexts for new models
    - Update learning contexts with results
    - Track adaptation history
    - Provide context statistics and health
    """

    def __init__(self, config: IncrementalLearningConfig | None = None):
        self.config = config or IncrementalLearningConfig()
        self.learning_contexts: dict[str, LearningContext] = {}
        logger.info("📝 Context Management Service initialized")

    async def initialize_context(
        self,
        model_id: str,
        initial_model_state: dict[str, Any] | None = None,
        initial_data: list[dict[str, Any]] | None = None,
    ) -> bool:
        """
        Initialize learning context for a new model.

        Args:
            model_id: Unique identifier for the model
            initial_model_state: Initial model state dict
            initial_data: Initial training data for memory buffer

        Returns:
            Success status
        """
        try:
            # Create new learning context
            context = LearningContext(
                model_id=model_id,
                task_id=f"task_{model_id}",  # Generate task_id
                strategy=LearningStrategy.INCREMENTAL,  # Default strategy
                memory_buffer=(
                    initial_data[: self.config.memory_buffer_size] if initial_data else []
                ),
                task_boundaries={},  # Should be dict, not list
                learning_statistics={
                    "total_updates": 0,
                    "total_epochs": 0,
                    "total_samples_processed": 0,
                    "average_loss": 0.0,
                    "recent_losses": [],
                    "best_loss": float("inf"),
                    "learning_rate_adjustments": 0,
                },
                adaptation_history=[],
                metadata=(
                    {"initial_model_state": initial_model_state} if initial_model_state else {}
                ),
            )

            self.learning_contexts[model_id] = context

            logger.info(f"📝 Initialized learning context for model: {model_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize context for {model_id}: {e}")
            return False

    async def update_context(
        self,
        model_id: str,
        learning_result: LearningResult,
        task_info: dict[str, Any] | None = None,
    ) -> bool:
        """
        Update learning context with results from a learning operation.

        Args:
            model_id: Model identifier
            learning_result: Result from learning strategy execution
            task_info: Additional task information

        Returns:
            Success status
        """
        try:
            if model_id not in self.learning_contexts:
                logger.warning(f"⚠️ Context for {model_id} not found, initializing new one")
                await self.initialize_context(model_id)

            context = self.learning_contexts[model_id]

            # Update learning statistics
            await self._update_learning_statistics(context, learning_result)

            # Add to adaptation history
            await self._add_adaptation_record(context, learning_result, task_info)

            # Update task boundaries if this was a new task
            if task_info and task_info.get("is_new_task", False):
                current_samples = context.learning_statistics["total_samples_processed"]
                # Store as dict entry instead of list append
                task_key = f"task_{len(context.task_boundaries)}"
                context.task_boundaries[task_key] = current_samples

            logger.debug(f"📊 Updated context for {model_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update context for {model_id}: {e}")
            return False

    async def get_context(self, model_id: str) -> LearningContext | None:
        """
        Retrieve learning context for a model.

        Args:
            model_id: Model identifier

        Returns:
            LearningContext or None if not found
        """
        return self.learning_contexts.get(model_id)

    async def remove_context(self, model_id: str) -> bool:
        """
        Remove learning context for a model.

        Args:
            model_id: Model identifier

        Returns:
            Success status
        """
        try:
            if model_id in self.learning_contexts:
                del self.learning_contexts[model_id]
                logger.info(f"🗑️ Removed context for model: {model_id}")
                return True
            else:
                logger.warning(f"⚠️ Context for {model_id} not found")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to remove context for {model_id}: {e}")
            return False

    async def get_context_summary(self, model_id: str) -> dict[str, Any] | None:
        """
        Get summary statistics for a model's learning context.

        Args:
            model_id: Model identifier

        Returns:
            Summary statistics or None if context not found
        """
        try:
            context = self.learning_contexts.get(model_id)
            if not context:
                return None

            stats = context.learning_statistics

            # Calculate derived metrics
            recent_performance_trend = "stable"
            recent_losses = stats.get("recent_losses", [])
            if len(recent_losses) >= 3:
                if recent_losses[-1] < recent_losses[-3]:
                    recent_performance_trend = "improving"
                elif recent_losses[-1] > recent_losses[-3]:
                    recent_performance_trend = "degrading"

            # Memory utilization
            memory_utilization = len(context.memory_buffer) / self.config.memory_buffer_size

            # Task progression
            total_tasks = len(context.task_boundaries) + 1  # +1 for current task

            return {
                "model_id": model_id,
                "total_updates": stats.get("total_updates", 0),
                "total_epochs": stats.get("total_epochs", 0),
                "total_samples_processed": stats.get("total_samples_processed", 0),
                "current_loss": recent_losses[-1] if recent_losses else None,
                "best_loss": stats.get("best_loss", float("inf")),
                "average_loss": stats.get("average_loss", 0.0),
                "recent_performance_trend": recent_performance_trend,
                "memory_utilization": memory_utilization,
                "memory_buffer_size": len(context.memory_buffer),
                "total_tasks_learned": total_tasks,
                "adaptation_history_length": len(context.adaptation_history),
                "learning_rate_adjustments": stats.get("learning_rate_adjustments", 0),
            }

        except Exception as e:
            logger.error(f"❌ Failed to get context summary for {model_id}: {e}")
            return None

    async def get_all_contexts_summary(self) -> dict[str, Any]:
        """
        Get summary for all managed learning contexts.

        Returns:
            Overall summary statistics
        """
        try:
            total_contexts = len(self.learning_contexts)

            if total_contexts == 0:
                return {
                    "total_contexts": 0,
                    "active_models": [],
                    "total_updates": 0,
                    "total_samples_processed": 0,
                    "average_memory_utilization": 0.0,
                }

            # Aggregate statistics
            total_updates = 0
            total_samples = 0
            memory_utilizations = []
            active_models = []

            for model_id, context in self.learning_contexts.items():
                stats = context.learning_statistics
                total_updates += stats.get("total_updates", 0)
                total_samples += stats.get("total_samples_processed", 0)

                memory_util = len(context.memory_buffer) / self.config.memory_buffer_size
                memory_utilizations.append(memory_util)

                active_models.append(
                    {
                        "model_id": model_id,
                        "updates": stats.get("total_updates", 0),
                        "current_loss": stats.get("recent_losses", [None])[-1],
                    }
                )

            avg_memory_util = sum(memory_utilizations) / len(memory_utilizations)

            return {
                "total_contexts": total_contexts,
                "active_models": active_models,
                "total_updates": total_updates,
                "total_samples_processed": total_samples,
                "average_memory_utilization": avg_memory_util,
                "max_memory_capacity": self.config.memory_buffer_size,
            }

        except Exception as e:
            logger.error(f"❌ Failed to get all contexts summary: {e}")
            return {"error": str(e)}

    async def cleanup_old_contexts(self, max_age_hours: int = 24) -> int:
        """
        Remove old, inactive learning contexts.

        Args:
            max_age_hours: Maximum age in hours before cleanup

        Returns:
            Number of contexts removed
        """
        try:
            current_time = datetime.now()
            removed_count = 0
            contexts_to_remove = []

            for model_id, context in self.learning_contexts.items():
                # Check if context has recent activity
                if context.adaptation_history:
                    last_activity = context.adaptation_history[-1].get("timestamp")
                    if last_activity:
                        try:
                            last_activity_time = datetime.fromisoformat(last_activity)
                            age_hours = (current_time - last_activity_time).total_seconds() / 3600

                            if age_hours > max_age_hours:
                                contexts_to_remove.append(model_id)
                        except ValueError:
                            # If timestamp parsing fails, keep the context
                            pass
                else:
                    # No adaptation history, consider for removal
                    contexts_to_remove.append(model_id)

            # Remove old contexts
            for model_id in contexts_to_remove:
                await self.remove_context(model_id)
                removed_count += 1

            if removed_count > 0:
                logger.info(f"🧹 Cleaned up {removed_count} old learning contexts")

            return removed_count

        except Exception as e:
            logger.error(f"❌ Failed to cleanup old contexts: {e}")
            return 0

    # Private helper methods

    async def _update_learning_statistics(self, context: LearningContext, result: LearningResult):
        """Update learning statistics with new result."""

        stats = context.learning_statistics

        # Update counters
        stats["total_updates"] += 1
        stats["total_epochs"] += result.epochs_completed
        stats["total_samples_processed"] += result.processed_samples

        # Update loss tracking
        current_loss = result.final_loss
        if current_loss != float("inf"):
            recent_losses = stats.get("recent_losses", [])
            recent_losses.append(current_loss)

            # Keep only recent losses (last 10)
            if len(recent_losses) > 10:
                recent_losses = recent_losses[-10:]
            stats["recent_losses"] = recent_losses

            # Update best loss
            if current_loss < stats.get("best_loss", float("inf")):
                stats["best_loss"] = current_loss

            # Update average loss
            if recent_losses:
                stats["average_loss"] = sum(recent_losses) / len(recent_losses)

        # Track learning rate adjustments
        if "adaptive_lr_used" in result.metrics or "lr_adjustment_factor" in result.metrics:
            stats["learning_rate_adjustments"] += 1

    async def _add_adaptation_record(
        self,
        context: LearningContext,
        result: LearningResult,
        task_info: dict[str, Any] | None,
    ):
        """Add adaptation record to history."""

        adaptation_record = {
            "timestamp": datetime.now().isoformat(),
            "strategy_used": result.strategy_used,
            "final_loss": result.final_loss,
            "epochs_completed": result.epochs_completed,
            "processed_samples": result.processed_samples,
            "success": result.success,
            "task_info": task_info or {},
            "metrics_summary": {
                key: value
                for key, value in result.metrics.items()
                if isinstance(value, (int, float, str, bool))
            },
        }

        context.adaptation_history.append(adaptation_record)

        # Keep only recent history (last 100 records)
        if len(context.adaptation_history) > 100:
            context.adaptation_history = context.adaptation_history[-100:]

    async def health_check(self) -> dict[str, Any]:
        """Health check for context management service."""

        summary = await self.get_all_contexts_summary()

        return {
            "service": "ContextManagementService",
            "status": "healthy",
            "active_contexts": summary.get("total_contexts", 0),
            "total_updates_managed": summary.get("total_updates", 0),
            "memory_buffer_capacity": self.config.memory_buffer_size,
        }
