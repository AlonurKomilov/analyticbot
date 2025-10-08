"""
Learning Orchestrator Service
==============================

Facade/Orchestrator that coordinates all incremental learning microservices.
Provides backwards compatibility with original IncrementalLearningEngine.

Single Responsibility: Coordinate microservices and maintain backwards compatibility.
"""

import logging
from datetime import datetime
from typing import Any

from core.services.adaptive_learning.learning.context.context_manager import ContextManager
from core.services.adaptive_learning.learning.data.data_processor import DataProcessor
from core.services.adaptive_learning.learning.memory.memory_manager import MemoryManager
from core.services.adaptive_learning.learning.model.model_operator import ModelOperator
from core.services.adaptive_learning.learning.models import (
    LearningConfig,
    MemoryBuffer,
    ModelEvaluation,
)
from core.services.adaptive_learning.learning.strategy.learning_strategy import LearningStrategy

logger = logging.getLogger(__name__)


class LearningOrchestrator:
    """
    Orchestrator for all incremental learning microservices.

    Coordinates:
    - LearningStrategy (learning algorithms and strategies)
    - MemoryManager (memory buffer operations)
    - ContextManager (learning context tracking)
    - ModelOperator (model evaluation and operations)
    - DataProcessor (data preparation and batching)

    Provides backwards compatibility with original IncrementalLearningEngine.
    """

    def __init__(
        self,
        config: LearningConfig | None = None,
        model_service: Any = None,
        data_service: Any = None,
        # Support legacy parameter names for backwards compatibility
        analytics_service: Any = None,
        config_manager: Any = None,
    ):
        self.config = config or LearningConfig()

        # Initialize all microservices
        self.learning_strategy = LearningStrategy(
            config=self.config,
            model_service=model_service,
        )

        self.memory_manager = MemoryManager()

        self.context_manager = ContextManager(config=self.config)

        self.model_operator = ModelOperator(config=self.config)

        self.data_processor = DataProcessor(config=self.config)

        # Store references for coordination
        self.model_service = model_service
        self.data_service = data_service

        logger.info("🎭 Learning Orchestrator initialized with all microservices")

    async def execute_incremental_learning(
        self,
        new_data: list[dict[str, Any]],
        learning_context: dict[str, Any] | None = None,
        strategy: str = "adaptive",
    ) -> dict[str, Any]:
        """
        Execute complete incremental learning pipeline.

        Orchestrates: data processing → memory management → learning → evaluation

        Args:
            new_data: New training data
            learning_context: Context information for learning
            strategy: Learning strategy to use

        Returns:
            Complete learning result with metrics and insights
        """
        try:
            logger.info(f"🎭 Orchestrating incremental learning with {strategy} strategy")

            # Step 1: Create learning context
            context_id = f"learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            context = self.context_manager.create_learning_context(
                context_id=context_id,
                learning_scenario=strategy,
                initial_data=learning_context or {},
            )

            # Step 2: Process data
            data_batch = self.data_processor.create_learning_batch(new_data)

            # Step 3: Manage memory (store new data, get relevant samples)
            memory_result = await self.memory_manager.store_learning_data(
                data_batch.data_batches[0] if data_batch.data_batches else new_data
            )

            # Step 4: Get balanced training data from memory
            balanced_data = self.memory_manager.get_balanced_samples(
                sample_size=self.config.batch_size * 2
            )

            # Step 5: Execute learning strategy
            learning_result = await self.learning_strategy.execute_incremental_learning(
                new_data=new_data,
                existing_data=balanced_data,
                strategy=strategy,
            )

            # Step 6: Update context with results
            self.context_manager.update_learning_context(
                context_id=context_id,
                performance_update=learning_result.get("performance_metrics", {}),
                progression_update=learning_result.get("learning_progression", {}),
            )

            # Step 7: Get comprehensive insights
            context_insights = self.context_manager.analyze_context_performance(context_id)
            memory_insights = self.memory_manager.get_memory_insights()

            # Combine all results
            complete_result = {
                "learning_context_id": context_id,
                "strategy_used": strategy,
                "data_processed": {
                    "batch_id": data_batch.batch_id,
                    "samples_processed": data_batch.processed_data_size,
                    "quality_score": data_batch.quality_score,
                },
                "memory_management": {
                    "samples_stored": memory_result.get("samples_stored", 0),
                    "memory_utilization": memory_insights.get("utilization_percentage", 0),
                },
                "learning_results": learning_result,
                "context_insights": context_insights,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info("✅ Incremental learning orchestration complete")
            return complete_result

        except Exception as e:
            logger.error(f"❌ Incremental learning orchestration failed: {e}")
            raise

    async def evaluate_learning_performance(
        self, model: Any, evaluation_data: dict[str, Any]
    ) -> ModelEvaluation:
        """
        Comprehensive learning performance evaluation.

        Args:
            model: Model to evaluate
            evaluation_data: Data for evaluation

        Returns:
            ModelEvaluation with comprehensive metrics
        """
        return self.model_operator.evaluate_model_performance(
            model=model,
            evaluation_data=evaluation_data,
        )

    async def optimize_learning_parameters(
        self,
        performance_history: list[dict[str, float]],
        learning_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Optimize learning parameters based on performance history.

        Args:
            performance_history: Historical performance data
            learning_context: Current learning context

        Returns:
            Optimization results and recommendations
        """
        if not performance_history:
            return {"message": "No performance history available for optimization"}

        # Get current performance
        current_performance = performance_history[-1] if performance_history else {}

        # Calculate optimized weights
        optimized_weights = self.model_operator.calculate_learning_weights(
            current_performance=current_performance,
            historical_performance=performance_history[:-1],
            learning_context=learning_context,
        )

        # Get memory optimization suggestions
        memory_stats = self.memory_manager.get_memory_insights()
        memory_suggestions = self._generate_memory_optimization_suggestions(memory_stats)

        # Get data processing optimization suggestions
        data_stats = self.data_processor.get_data_statistics()
        data_suggestions = self._generate_data_optimization_suggestions(data_stats)

        return {
            "optimized_weights": optimized_weights,
            "memory_optimization": memory_suggestions,
            "data_optimization": data_suggestions,
            "performance_trend": self._analyze_performance_trend(performance_history),
        }

    async def manage_learning_memory(self, operation: str, **kwargs) -> dict[str, Any]:
        """
        Manage learning memory operations.

        Args:
            operation: Operation type ("store", "retrieve", "clear", "optimize")
            **kwargs: Operation-specific parameters

        Returns:
            Operation result
        """
        if operation == "store":
            data = kwargs.get("data", [])
            return await self.memory_manager.store_learning_data(data)

        elif operation == "retrieve":
            sample_size = kwargs.get("sample_size", 100)
            samples = self.memory_manager.get_balanced_samples(sample_size)
            return {"samples": samples, "count": len(samples)}

        elif operation == "clear":
            retention_strategy = kwargs.get("strategy", "keep_recent")
            return self.memory_manager.clear_memory_buffer(retention_strategy)

        elif operation == "optimize":
            return self.memory_manager.optimize_memory_usage()

        else:
            raise ValueError(f"Unknown memory operation: {operation}")

    async def process_streaming_data(
        self,
        data_stream: list[dict[str, Any]],
        window_size: int | None = None,
        learning_strategy: str = "adaptive",
    ) -> dict[str, Any]:
        """
        Process streaming data for continuous learning.

        Args:
            data_stream: Continuous data stream
            window_size: Size of processing windows
            learning_strategy: Strategy for learning from stream

        Returns:
            Streaming processing results
        """
        logger.info(f"🌊 Processing streaming data: {len(data_stream)} samples")

        # Create streaming batches
        streaming_batches = self.data_processor.create_streaming_batches(
            data_stream=data_stream,
            window_size=window_size,
        )

        # Process each batch incrementally
        results = []
        for i, batch in enumerate(streaming_batches):
            batch_data = batch.data_batches[0] if batch.data_batches else []

            # Execute incremental learning for this batch
            result = await self.execute_incremental_learning(
                new_data=batch_data,
                learning_context={"batch_index": i, "stream_processing": True},
                strategy=learning_strategy,
            )

            results.append(result)

        return {
            "total_batches_processed": len(results),
            "stream_length": len(data_stream),
            "processing_results": results,
            "streaming_insights": self._analyze_streaming_results(results),
        }

    def get_learning_insights(
        self, context_id: str | None = None, time_window_hours: int = 24
    ) -> dict[str, Any]:
        """
        Get comprehensive learning insights.

        Args:
            context_id: Specific context ID (optional)
            time_window_hours: Time window for analysis

        Returns:
            Comprehensive learning insights
        """
        insights = {}

        # Context insights
        if context_id:
            insights["context_analysis"] = self.context_manager.analyze_context_performance(
                context_id
            )
        else:
            insights["cross_context_analysis"] = self.context_manager.get_cross_context_insights()

        # Memory insights
        insights["memory_analysis"] = self.memory_manager.get_memory_insights()

        # Data processing insights
        insights["data_analysis"] = self.data_processor.get_data_statistics()

        # Model insights (if models available)
        if (
            hasattr(self.model_operator, "model_evaluations")
            and self.model_operator.model_evaluations
        ):
            latest_model_id = self.model_operator.model_evaluations[-1].model_id
            insights["model_analysis"] = self.model_operator.get_model_insights(
                model_id=latest_model_id,
                time_window_hours=time_window_hours,
            )

        return insights

    # Backwards compatibility methods

    async def learn_incrementally(
        self, new_data: list[dict[str, Any]], model: Any = None, learning_rate: float | None = None
    ) -> dict[str, Any]:
        """Legacy method for backwards compatibility."""
        learning_context = {"learning_rate": learning_rate} if learning_rate else {}
        return await self.execute_incremental_learning(
            new_data=new_data,
            learning_context=learning_context,
        )

    def get_memory_buffer(self) -> MemoryBuffer:
        """Legacy method for backwards compatibility."""
        return MemoryBuffer(
            buffer_id="default",
            max_size=1000,
            current_size=len(self.memory_manager.memory_buffer),
            retention_strategy="keep_recent",
            stored_data=list(self.memory_manager.memory_buffer.values()),
            metadata={},
            created_at="",
            last_accessed="",
        )

    def clear_learning_memory(self) -> None:
        """Legacy method for backwards compatibility."""
        self.memory_manager.clear_memory_buffer()

    # Private helper methods

    def _generate_memory_optimization_suggestions(self, memory_stats: dict[str, Any]) -> list[str]:
        """Generate memory optimization suggestions."""
        suggestions = []

        utilization = memory_stats.get("utilization_percentage", 0)
        if utilization > 90:
            suggestions.append("Memory utilization is high - consider clearing old data")
        elif utilization < 30:
            suggestions.append("Memory utilization is low - consider reducing buffer size")

        return suggestions

    def _generate_data_optimization_suggestions(self, data_stats: dict[str, Any]) -> list[str]:
        """Generate data processing optimization suggestions."""
        suggestions = []

        avg_quality = data_stats.get("average_quality_score", 0)
        if avg_quality < 0.7:
            suggestions.append("Data quality is low - improve data validation")

        return suggestions

    def _analyze_performance_trend(
        self, performance_history: list[dict[str, float]]
    ) -> dict[str, Any]:
        """Analyze performance trend."""
        if len(performance_history) < 2:
            return {"trend": "insufficient_data"}

        scores = [p.get("overall_score", 0.0) for p in performance_history]
        trend = "improving" if scores[-1] > scores[0] else "declining"

        return {
            "trend": trend,
            "improvement": scores[-1] - scores[0],
            "stability": 1.0 - (max(scores) - min(scores)),
        }

    def _analyze_streaming_results(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze streaming processing results."""
        total_samples = sum(r["data_processed"]["samples_processed"] for r in results)
        avg_quality = sum(r["data_processed"]["quality_score"] for r in results) / len(results)

        return {
            "total_samples_processed": total_samples,
            "average_quality_score": avg_quality,
            "processing_efficiency": len(results) / max(1, total_samples / 100),
        }

    async def health_check(self) -> dict[str, Any]:
        """
        Comprehensive health check for all microservices.

        Returns:
            Health status of orchestrator and all microservices
        """
        # Check all microservices
        strategy_health = await self.learning_strategy.health_check()
        memory_health = await self.memory_manager.health_check()
        context_health = await self.context_manager.health_check()
        model_health = await self.model_operator.health_check()
        data_health = await self.data_processor.health_check()

        # Aggregate health status
        all_healthy = all(
            [
                strategy_health["status"] == "healthy",
                memory_health["status"] == "healthy",
                context_health["status"] == "healthy",
                model_health["status"] == "healthy",
                data_health["status"] == "healthy",
            ]
        )

        return {
            "service": "LearningOrchestrator",
            "status": "healthy" if all_healthy else "degraded",
            "microservices": {
                "learning_strategy": strategy_health,
                "memory_manager": memory_health,
                "context_manager": context_health,
                "model_operator": model_health,
                "data_processor": data_health,
            },
        }


# Backwards compatibility alias
IncrementalLearningEngine = LearningOrchestrator
