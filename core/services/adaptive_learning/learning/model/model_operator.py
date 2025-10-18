"""
Model Operations Service
========================

Microservice responsible for model evaluation, weight calculations,
and model performance optimization.

Single Responsibility: Manage model operations only.
"""

import logging
from typing import Any

import numpy as np

from ..models import LearningConfig, ModelEvaluation

logger = logging.getLogger(__name__)


class ModelOperator:
    """
    Model operations microservice.

    Responsibilities:
    - Evaluate model performance
    - Calculate model weights and adjustments
    - Optimize model parameters
    - Track model metrics
    - Generate model insights
    """

    def __init__(self, config: LearningConfig | None = None):
        self.config = config or LearningConfig()
        self.model_evaluations: list[ModelEvaluation] = []
        self.performance_cache: dict[str, float] = {}
        logger.info("⚙️ Model Operator initialized")

    def evaluate_model_performance(
        self,
        model: Any,
        evaluation_data: dict[str, Any],
        metrics: list[str] | None = None,
    ) -> ModelEvaluation:
        """
        Comprehensive model performance evaluation.

        Args:
            model: Model instance to evaluate
            evaluation_data: Data for evaluation (X, y)
            metrics: List of metrics to calculate

        Returns:
            ModelEvaluation with comprehensive metrics
        """
        try:
            logger.info("⚙️ Evaluating model performance")

            metrics = metrics or ["accuracy", "loss", "precision", "recall"]

            # Extract evaluation data
            X_eval = evaluation_data.get("X", [])
            y_eval = evaluation_data.get("y", [])

            if not X_eval or not y_eval:
                raise ValueError("Evaluation data must include X and y")

            # Calculate metrics
            performance_metrics = self._calculate_performance_metrics(
                model, X_eval, y_eval, metrics
            )

            # Calculate model complexity
            complexity_score = self._calculate_model_complexity(model)

            # Calculate efficiency metrics
            efficiency_metrics = self._calculate_efficiency_metrics(
                model, X_eval, performance_metrics
            )

            # Create evaluation object
            evaluation = ModelEvaluation(
                model_id=getattr(model, "model_id", "unknown"),
                performance_metrics=performance_metrics,
                complexity_score=complexity_score,
                efficiency_metrics=efficiency_metrics,
                evaluation_timestamp=self._get_timestamp(),
                data_size=len(X_eval),
            )

            # Store evaluation
            self.model_evaluations.append(evaluation)

            # Update performance cache
            self.performance_cache[evaluation.model_id] = performance_metrics.get(
                "overall_score", 0.0
            )

            logger.info(f"✅ Model evaluation complete: {evaluation.model_id}")
            return evaluation

        except Exception as e:
            logger.error(f"❌ Model evaluation failed: {e}")
            raise

    def calculate_learning_weights(
        self,
        current_performance: dict[str, float],
        historical_performance: list[dict[str, float]],
        learning_context: dict[str, Any] | None = None,
    ) -> dict[str, float]:
        """
        Calculate dynamic learning weights based on performance.

        Args:
            current_performance: Current model performance metrics
            historical_performance: Historical performance data
            learning_context: Additional context for weight calculation

        Returns:
            Dictionary of calculated weights
        """
        logger.info("⚙️ Calculating learning weights")

        # Base weights from configuration
        base_weights = self.config.learning_weights.copy()

        # Performance-based adjustments
        performance_factor = self._calculate_performance_factor(
            current_performance, historical_performance
        )

        # Context-based adjustments
        context_factor = self._calculate_context_factor(learning_context or {})

        # Stability factor (reduces weights if performance is unstable)
        stability_factor = self._calculate_stability_factor(historical_performance)

        # Calculate final weights
        adjusted_weights = {}
        for weight_name, base_value in base_weights.items():
            adjusted_value = base_value * performance_factor * context_factor * stability_factor
            # Clamp weights to reasonable ranges
            adjusted_weights[weight_name] = max(0.01, min(2.0, adjusted_value))

        logger.info(f"📊 Learning weights calculated: {adjusted_weights}")
        return adjusted_weights

    def optimize_model_parameters(
        self,
        model: Any,
        optimization_data: dict[str, Any],
        optimization_strategy: str = "adaptive",
    ) -> dict[str, Any]:
        """
        Optimize model parameters for better performance.

        Args:
            model: Model to optimize
            optimization_data: Data for optimization
            optimization_strategy: Strategy to use ("adaptive", "aggressive", "conservative")

        Returns:
            Optimization results and recommendations
        """
        logger.info(f"⚙️ Optimizing model with {optimization_strategy} strategy")

        # Get current model state
        current_params = self._extract_model_parameters(model)

        # Calculate optimization suggestions
        if optimization_strategy == "adaptive":
            suggestions = self._adaptive_optimization(model, optimization_data)
        elif optimization_strategy == "aggressive":
            suggestions = self._aggressive_optimization(model, optimization_data)
        else:  # conservative
            suggestions = self._conservative_optimization(model, optimization_data)

        # Apply optimizations if within safety bounds
        applied_changes = self._apply_safe_optimizations(model, suggestions)

        return {
            "strategy": optimization_strategy,
            "suggestions": suggestions,
            "applied_changes": applied_changes,
            "optimization_score": self._calculate_optimization_score(
                current_params, applied_changes
            ),
        }

    def calculate_model_confidence(self, model: Any, prediction_data: dict[str, Any]) -> float:
        """
        Calculate confidence score for model predictions.

        Args:
            model: Model instance
            prediction_data: Data for confidence calculation

        Returns:
            Confidence score (0.0 to 1.0)
        """
        try:
            # Get model predictions
            predictions = self._get_model_predictions(model, prediction_data)

            # Calculate prediction variance
            prediction_variance = np.var(predictions) if predictions else 0.0

            # Calculate historical accuracy
            model_id = getattr(model, "model_id", "unknown")
            historical_accuracy = self.performance_cache.get(model_id, 0.75)

            # Calculate data quality factor
            data_quality = self._assess_data_quality(prediction_data)

            # Combine factors into confidence score
            confidence = (
                historical_accuracy * 0.5
                + (1.0 - min(prediction_variance, 1.0)) * 0.3
                + data_quality * 0.2
            )

            return float(max(0.0, min(1.0, confidence)))

        except Exception as e:
            logger.error(f"❌ Confidence calculation failed: {e}")
            return 0.5  # Default medium confidence

    def get_model_insights(self, model_id: str, time_window_hours: int = 24) -> dict[str, Any]:
        """
        Generate insights for a specific model.

        Args:
            model_id: Model identifier
            time_window_hours: Time window for analysis

        Returns:
            Model insights and recommendations
        """
        # Filter evaluations for this model within time window
        relevant_evaluations = [
            eval
            for eval in self.model_evaluations
            if eval.model_id == model_id
            and self._is_within_time_window(eval.evaluation_timestamp, time_window_hours)
        ]

        if not relevant_evaluations:
            return {"message": f"No recent evaluations for model {model_id}"}

        # Calculate performance trends
        performance_trend = self._calculate_performance_trend(relevant_evaluations)

        # Calculate stability metrics
        stability_metrics = self._calculate_stability_metrics(relevant_evaluations)

        # Generate recommendations
        recommendations = self._generate_model_recommendations(
            relevant_evaluations, performance_trend, stability_metrics
        )

        return {
            "model_id": model_id,
            "evaluation_count": len(relevant_evaluations),
            "performance_trend": performance_trend,
            "stability_metrics": stability_metrics,
            "recommendations": recommendations,
            "latest_performance": relevant_evaluations[-1].performance_metrics,
        }

    # Private helper methods

    def _calculate_performance_metrics(
        self, model: Any, X_eval: list[Any], y_eval: list[Any], metrics: list[str]
    ) -> dict[str, float]:
        """Calculate various performance metrics."""
        # Mock implementation - would use actual model evaluation in practice
        results = {}

        for metric in metrics:
            if metric == "accuracy":
                results["accuracy"] = 0.85  # Mock accuracy
            elif metric == "loss":
                results["loss"] = 0.15  # Mock loss
            elif metric == "precision":
                results["precision"] = 0.82
            elif metric == "recall":
                results["recall"] = 0.88

        # Calculate overall score
        results["overall_score"] = sum(results.values()) / len(results)
        return results

    def _calculate_model_complexity(self, model: Any) -> float:
        """Calculate model complexity score."""
        # Mock implementation - would analyze actual model structure
        return 0.65  # Medium complexity

    def _calculate_efficiency_metrics(
        self, model: Any, X_eval: list[Any], performance_metrics: dict[str, float]
    ) -> dict[str, float]:
        """Calculate model efficiency metrics."""
        return {
            "inference_time": 0.05,  # Mock inference time
            "memory_usage": 0.3,  # Mock memory usage
            "throughput": 200.0,  # Mock throughput
        }

    def _calculate_performance_factor(
        self, current: dict[str, float], historical: list[dict[str, float]]
    ) -> float:
        """Calculate performance-based adjustment factor."""
        if not historical:
            return 1.0

        current_score = current.get("overall_score", 0.5)
        avg_historical = np.mean([h.get("overall_score", 0.5) for h in historical])

        # Higher current performance relative to history = higher factor
        return float(max(0.5, min(1.5, current_score / max(avg_historical, 0.1))))

    def _calculate_context_factor(self, context: dict[str, Any]) -> float:
        """Calculate context-based adjustment factor."""
        # Mock implementation - would analyze learning context
        difficulty = context.get("difficulty_level", "medium")
        factor_map = {"easy": 1.2, "medium": 1.0, "hard": 0.8}
        return factor_map.get(difficulty, 1.0)

    def _calculate_stability_factor(self, historical: list[dict[str, float]]) -> float:
        """Calculate stability-based adjustment factor."""
        if len(historical) < 3:
            return 1.0

        scores = [h.get("overall_score", 0.5) for h in historical]
        variance = np.var(scores)

        # Lower variance = higher stability = higher factor
        return float(max(0.7, min(1.3, 1.0 - variance)))

    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime

        return datetime.now().isoformat()

    def _adaptive_optimization(self, model: Any, data: dict[str, Any]) -> dict[str, Any]:
        """Adaptive optimization strategy."""
        return {"learning_rate": 0.01, "batch_size": 32}

    def _aggressive_optimization(self, model: Any, data: dict[str, Any]) -> dict[str, Any]:
        """Aggressive optimization strategy."""
        return {"learning_rate": 0.05, "batch_size": 64}

    def _conservative_optimization(self, model: Any, data: dict[str, Any]) -> dict[str, Any]:
        """Conservative optimization strategy."""
        return {"learning_rate": 0.005, "batch_size": 16}

    def _extract_model_parameters(self, model: Any) -> dict[str, Any]:
        """Extract current model parameters."""
        return {"learning_rate": 0.01, "batch_size": 32}  # Mock

    def _apply_safe_optimizations(self, model: Any, suggestions: dict[str, Any]) -> dict[str, Any]:
        """Apply optimizations within safety bounds."""
        return suggestions  # Mock implementation

    def _calculate_optimization_score(self, before: dict[str, Any], after: dict[str, Any]) -> float:
        """Calculate optimization effectiveness score."""
        return 0.15  # Mock 15% improvement

    def _get_model_predictions(self, model: Any, data: dict[str, Any]) -> list[float]:
        """Get model predictions."""
        return [0.8, 0.9, 0.7, 0.85]  # Mock predictions

    def _assess_data_quality(self, data: dict[str, Any]) -> float:
        """Assess quality of input data."""
        return 0.8  # Mock data quality score

    def _is_within_time_window(self, timestamp: str, hours: int) -> bool:
        """Check if timestamp is within time window."""
        from datetime import datetime, timedelta

        try:
            eval_time = datetime.fromisoformat(timestamp)
            cutoff = datetime.now() - timedelta(hours=hours)
            return eval_time > cutoff
        except ValueError:
            return False

    def _calculate_performance_trend(self, evaluations: list[ModelEvaluation]) -> dict[str, Any]:
        """Calculate performance trend from evaluations."""
        if len(evaluations) < 2:
            return {"trend": "insufficient_data"}

        scores = [e.performance_metrics.get("overall_score", 0.0) for e in evaluations]
        trend_direction = "improving" if scores[-1] > scores[0] else "declining"

        return {
            "trend": trend_direction,
            "change": scores[-1] - scores[0],
            "stability": 1.0 - np.var(scores),
        }

    def _calculate_stability_metrics(self, evaluations: list[ModelEvaluation]) -> dict[str, float]:
        """Calculate stability metrics."""
        scores = [e.performance_metrics.get("overall_score", 0.0) for e in evaluations]
        return {
            "variance": float(np.var(scores)),
            "std_deviation": float(np.std(scores)),
            "stability_score": float(max(0.0, 1.0 - np.var(scores))),
        }

    def _generate_model_recommendations(
        self,
        evaluations: list[ModelEvaluation],
        performance_trend: dict[str, Any],
        stability_metrics: dict[str, float],
    ) -> list[str]:
        """Generate recommendations based on model analysis."""
        recommendations = []

        if performance_trend.get("trend") == "declining":
            recommendations.append("Consider retraining or parameter adjustment")

        if stability_metrics.get("stability_score", 1.0) < 0.7:
            recommendations.append("Model performance is unstable - investigate data quality")

        if not recommendations:
            recommendations.append("Model is performing well - continue current approach")

        return recommendations

    async def health_check(self) -> dict[str, Any]:
        """Health check for model operator."""
        return {
            "service": "ModelOperator",
            "status": "healthy",
            "evaluations_performed": len(self.model_evaluations),
            "models_in_cache": len(self.performance_cache),
        }
