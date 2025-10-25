"""
Context Management Service
==========================

Microservice responsible for managing learning contexts and
tracking learning progression across different scenarios.

Single Responsibility: Manage learning context only.
"""

import logging
from datetime import datetime
from typing import Any

from core.services.adaptive_learning.learning.models import LearningConfig

# Use absolute imports to avoid relative path issues
from core.services.adaptive_learning.protocols.learning_protocols import (
    LearningContext,
    LearningStrategy,
)

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Learning context management microservice.

    Responsibilities:
    - Track learning contexts across sessions
    - Manage context transitions
    - Maintain context history
    - Provide context-based learning insights
    """

    def __init__(self, config: LearningConfig | None = None):
        self.config = config or LearningConfig()
        self.active_contexts: dict[str, LearningContext] = {}
        self.context_history: list[LearningContext] = []
        logger.info("🎯 Context Manager initialized")

    def create_learning_context(
        self, context_id: str, learning_scenario: str, initial_data: dict[str, Any]
    ) -> LearningContext:
        """
        Create new learning context for a scenario.

        Args:
            context_id: Unique identifier for context
            learning_scenario: Type of learning scenario
            initial_data: Initial context data

        Returns:
            LearningContext object
        """
        try:
            logger.info(f"🎯 Creating learning context: {context_id}")

            context = LearningContext(
                model_id="",  # Will be set when associated with model
                task_id=context_id,  # Use context_id as task_id for now
                strategy=LearningStrategy.INCREMENTAL,  # Default strategy
                context_id=context_id,
                learning_scenario=learning_scenario,
                context_data=initial_data,
                performance_metrics={},
                learning_progression={},
                last_updated=datetime.now().isoformat(),
            )

            self.active_contexts[context_id] = context
            self.context_history.append(context)

            logger.info(f"✅ Learning context created: {context_id}")
            return context

        except Exception as e:
            logger.error(f"❌ Failed to create learning context {context_id}: {e}")
            raise

    def update_learning_context(
        self,
        context_id: str,
        performance_update: dict[str, Any],
        progression_update: dict[str, Any] | None = None,
    ) -> LearningContext:
        """
        Update existing learning context with new performance data.

        Args:
            context_id: Context identifier
            performance_update: Performance metrics update
            progression_update: Learning progression update

        Returns:
            Updated LearningContext
        """
        if context_id not in self.active_contexts:
            raise ValueError(f"Learning context not found: {context_id}")

        context = self.active_contexts[context_id]

        # Update performance metrics
        context.performance_metrics.update(performance_update)

        # Update learning progression if provided
        if progression_update:
            context.learning_progression.update(progression_update)

        # Update timestamp
        context.last_updated = datetime.now().isoformat()

        logger.info(f"📊 Updated learning context: {context_id}")
        return context

    def get_learning_context(self, context_id: str) -> LearningContext | None:
        """Retrieve learning context by ID."""
        return self.active_contexts.get(context_id)

    def get_contexts_by_scenario(self, learning_scenario: str) -> list[LearningContext]:
        """Get all contexts for a specific learning scenario."""
        return [
            context
            for context in self.active_contexts.values()
            if context.learning_scenario == learning_scenario
        ]

    def analyze_context_performance(self, context_id: str) -> dict[str, Any]:
        """
        Analyze performance trends within a learning context.

        Args:
            context_id: Context identifier

        Returns:
            Performance analysis dictionary
        """
        context = self.get_learning_context(context_id)
        if not context:
            return {"error": f"Context not found: {context_id}"}

        metrics = context.performance_metrics

        # Calculate performance trends
        accuracy_trend = self._calculate_metric_trend(metrics.get("accuracy_history", []))
        loss_trend = self._calculate_metric_trend(metrics.get("loss_history", []))

        # Calculate learning velocity
        learning_velocity = self._calculate_learning_velocity(context)

        return {
            "context_id": context_id,
            "scenario": context.learning_scenario,
            "performance_trends": {
                "accuracy": accuracy_trend,
                "loss": loss_trend,
            },
            "learning_velocity": learning_velocity,
            "total_updates": len(metrics.get("accuracy_history", [])),
            "current_performance": {
                "accuracy": metrics.get("current_accuracy", 0.0),
                "loss": metrics.get("current_loss", 0.0),
            },
        }

    def get_cross_context_insights(self) -> dict[str, Any]:
        """
        Generate insights across all learning contexts.

        Returns:
            Cross-context analysis
        """
        if not self.active_contexts:
            return {"message": "No active learning contexts"}

        # Group contexts by scenario
        scenario_groups = {}
        for context in self.active_contexts.values():
            scenario = context.learning_scenario
            if scenario not in scenario_groups:
                scenario_groups[scenario] = []
            scenario_groups[scenario].append(context)

        # Analyze each scenario group
        scenario_insights = {}
        for scenario, contexts in scenario_groups.items():
            scenario_insights[scenario] = self._analyze_scenario_group(contexts)

        return {
            "total_contexts": len(self.active_contexts),
            "scenarios": list(scenario_groups.keys()),
            "scenario_insights": scenario_insights,
            "best_performing_scenario": self._find_best_scenario(scenario_insights),
        }

    def cleanup_inactive_contexts(self, max_age_hours: int = 24) -> int:
        """
        Clean up old inactive contexts.

        Args:
            max_age_hours: Maximum age in hours before cleanup

        Returns:
            Number of contexts cleaned up
        """
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        contexts_to_remove = []

        for context_id, context in self.active_contexts.items():
            # Parse last_updated timestamp
            try:
                last_updated = datetime.fromisoformat(context.last_updated).timestamp()
                if last_updated < cutoff_time:
                    contexts_to_remove.append(context_id)
            except ValueError:
                # If timestamp parsing fails, consider it old
                contexts_to_remove.append(context_id)

        # Remove old contexts
        for context_id in contexts_to_remove:
            del self.active_contexts[context_id]

        logger.info(f"🧹 Cleaned up {len(contexts_to_remove)} inactive contexts")
        return len(contexts_to_remove)

    def _calculate_metric_trend(self, metric_history: list[float]) -> dict[str, Any]:
        """Calculate trend for a metric history."""
        if len(metric_history) < 2:
            return {"trend": "insufficient_data", "change": 0.0}

        recent_avg = sum(metric_history[-3:]) / min(3, len(metric_history))
        early_avg = sum(metric_history[:3]) / min(3, len(metric_history))

        change = recent_avg - early_avg

        if abs(change) < 0.01:
            trend = "stable"
        elif change > 0:
            trend = "improving"
        else:
            trend = "declining"

        return {
            "trend": trend,
            "change": change,
            "recent_average": recent_avg,
            "early_average": early_avg,
        }

    def _calculate_learning_velocity(self, context: LearningContext) -> float:
        """Calculate learning velocity for a context."""
        metrics = context.performance_metrics
        accuracy_history = metrics.get("accuracy_history", [])

        if len(accuracy_history) < 2:
            return 0.0

        # Calculate improvement rate per update
        total_improvement = accuracy_history[-1] - accuracy_history[0]
        updates = len(accuracy_history) - 1

        return total_improvement / updates if updates > 0 else 0.0

    def _analyze_scenario_group(self, contexts: list[LearningContext]) -> dict[str, Any]:
        """Analyze a group of contexts from the same scenario."""
        if not contexts:
            return {}

        # Calculate average performance
        total_accuracy = 0.0
        total_contexts = 0

        for context in contexts:
            current_accuracy = context.performance_metrics.get("current_accuracy", 0.0)
            if current_accuracy > 0:
                total_accuracy += current_accuracy
                total_contexts += 1

        avg_accuracy = total_accuracy / total_contexts if total_contexts > 0 else 0.0

        return {
            "context_count": len(contexts),
            "average_accuracy": avg_accuracy,
            "active_contexts": total_contexts,
        }

    def _find_best_scenario(self, scenario_insights: dict[str, Any]) -> str:
        """Find the best performing scenario."""
        best_scenario = None
        best_accuracy = 0.0

        for scenario, insights in scenario_insights.items():
            accuracy = insights.get("average_accuracy", 0.0)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_scenario = scenario

        return best_scenario or "none"

    async def health_check(self) -> dict[str, Any]:
        """Health check for context manager."""
        return {
            "service": "ContextManager",
            "status": "healthy",
            "active_contexts": len(self.active_contexts),
            "total_context_history": len(self.context_history),
            "scenarios_tracked": len(
                {context.learning_scenario for context in self.active_contexts.values()}
            ),
        }
