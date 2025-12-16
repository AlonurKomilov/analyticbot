"""
Accuracy Validator Service
===========================

Microservice responsible for validating prediction accuracy and
generating learning insights from validation results.

Single Responsibility: Validate prediction accuracy only.
"""

import logging
from typing import Any

from ..models import ModelingConfig, ValidationResult

logger = logging.getLogger(__name__)


class AccuracyValidator:
    """
    Prediction accuracy validation microservice.

    Responsibilities:
    - Validate prediction accuracy against actual outcomes
    - Calculate accuracy metrics (MAE, RMSE, etc.)
    - Analyze prediction errors
    - Generate learning insights
    """

    def __init__(self, config: ModelingConfig | None = None):
        self.config = config or ModelingConfig()
        self.validation_history: list[ValidationResult] = []
        logger.info("🎯 Accuracy Validator initialized")

    async def validate_prediction_accuracy(
        self, predictions: dict[str, Any], actual_outcomes: dict[str, Any]
    ) -> ValidationResult:
        """
        Validate prediction accuracy against actual outcomes.

        Args:
            predictions: Original predictions
            actual_outcomes: Actual measured outcomes

        Returns:
            ValidationResult with metrics and insights
        """
        try:
            logger.info("🎯 Validating prediction accuracy")

            # Calculate accuracy metrics
            accuracy_metrics = self._calculate_accuracy_metrics(predictions, actual_outcomes)

            # Analyze prediction errors
            error_analysis = self._analyze_prediction_errors(predictions, actual_outcomes)

            # Generate learning insights
            learning_insights = self._generate_learning_insights(accuracy_metrics, error_analysis)

            # Build validation result
            validation_result = ValidationResult(
                overall_accuracy=accuracy_metrics["overall_accuracy"],
                accuracy_by_metric=accuracy_metrics,
                error_analysis=error_analysis,
                learning_insights=learning_insights,
            )

            # Store in history
            self.validation_history.append(validation_result)

            logger.info(
                f"✅ Validation complete: " f"{validation_result.overall_accuracy:.2%} accuracy"
            )
            return validation_result

        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return ValidationResult(
                overall_accuracy=0.0,
                accuracy_by_metric={},
                error_analysis={},
                learning_insights=[],
            )

    def _calculate_accuracy_metrics(
        self, predictions: dict[str, Any], actual_outcomes: dict[str, Any]
    ) -> dict[str, float]:
        """
        Calculate comprehensive accuracy metrics.

        Metrics:
        - Overall accuracy
        - Mean Absolute Error (MAE)
        - Root Mean Square Error (RMSE)
        - Mean Absolute Percentage Error (MAPE)
        """
        predicted_values = predictions.get("predictions", [])
        actual_values = actual_outcomes.get("values", [])

        # Ensure we have matching data
        if not predicted_values or not actual_values:
            return {
                "overall_accuracy": 0.0,
                "mae": 0.0,
                "rmse": 0.0,
                "mape": 0.0,
            }

        # Calculate errors
        errors = []
        percentage_errors = []

        min_len = min(len(predicted_values), len(actual_values))
        for i in range(min_len):
            pred = predicted_values[i]
            actual = actual_values[i]

            error = abs(pred - actual)
            errors.append(error)

            if actual != 0:
                percentage_errors.append(abs((pred - actual) / actual))

        # Calculate metrics
        mae = sum(errors) / len(errors) if errors else 0.0
        rmse = (sum(e**2 for e in errors) / len(errors)) ** 0.5 if errors else 0.0
        mape = sum(percentage_errors) / len(percentage_errors) if percentage_errors else 0.0

        # Calculate overall accuracy (inverse of MAPE)
        overall_accuracy = max(0.0, 1.0 - mape)

        return {
            "overall_accuracy": overall_accuracy,
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
        }

    def _analyze_prediction_errors(
        self, predictions: dict[str, Any], actual_outcomes: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Analyze patterns in prediction errors.

        Returns:
        - Error distribution
        - Systematic biases
        - Error trends
        """
        predicted_values = predictions.get("predictions", [])
        actual_values = actual_outcomes.get("values", [])

        if not predicted_values or not actual_values:
            return {
                "error_distribution": "insufficient_data",
                "systematic_bias": 0.0,
                "error_trend": "unknown",
            }

        # Calculate signed errors (positive = overestimation)
        signed_errors = []
        min_len = min(len(predicted_values), len(actual_values))

        for i in range(min_len):
            signed_errors.append(predicted_values[i] - actual_values[i])

        # Systematic bias (average signed error)
        systematic_bias = sum(signed_errors) / len(signed_errors) if signed_errors else 0.0

        # Error distribution
        overestimates = sum(1 for e in signed_errors if e > 0)
        underestimates = sum(1 for e in signed_errors if e < 0)

        if overestimates > underestimates * 1.2:
            error_distribution = "overestimating"
        elif underestimates > overestimates * 1.2:
            error_distribution = "underestimating"
        else:
            error_distribution = "balanced"

        # Error trend (improving/degrading)
        if len(signed_errors) >= 3:
            first_half_error = sum(abs(e) for e in signed_errors[: len(signed_errors) // 2])
            second_half_error = sum(abs(e) for e in signed_errors[len(signed_errors) // 2 :])

            if second_half_error < first_half_error * 0.9:
                error_trend = "improving"
            elif second_half_error > first_half_error * 1.1:
                error_trend = "degrading"
            else:
                error_trend = "stable"
        else:
            error_trend = "insufficient_data"

        return {
            "error_distribution": error_distribution,
            "systematic_bias": systematic_bias,
            "error_trend": error_trend,
            "overestimates": overestimates,
            "underestimates": underestimates,
        }

    def _generate_learning_insights(
        self, accuracy_metrics: dict[str, float], error_analysis: dict[str, Any]
    ) -> list[str]:
        """Generate actionable learning insights from validation."""
        insights = []

        # Accuracy insights
        overall_accuracy = accuracy_metrics.get("overall_accuracy", 0.0)
        if overall_accuracy >= 0.9:
            insights.append("Excellent accuracy - model is performing very well")
        elif overall_accuracy >= 0.75:
            insights.append("Good accuracy - model is reliable for most use cases")
        elif overall_accuracy >= 0.6:
            insights.append("Fair accuracy - consider model improvements or additional features")
        else:
            insights.append("Low accuracy - significant model improvements needed")

        # Bias insights
        error_distribution = error_analysis.get("error_distribution", "unknown")
        if error_distribution == "overestimating":
            insights.append("Model tends to overestimate - consider calibration adjustments")
        elif error_distribution == "underestimating":
            insights.append("Model tends to underestimate - consider recalibration")

        # Trend insights
        error_trend = error_analysis.get("error_trend", "unknown")
        if error_trend == "improving":
            insights.append(
                "Prediction accuracy is improving over time - continue current approach"
            )
        elif error_trend == "degrading":
            insights.append(
                "Prediction accuracy is degrading - investigate data quality or model drift"
            )

        # MAPE insights
        mape = accuracy_metrics.get("mape", 0.0)
        if mape > 0.2:
            insights.append(f"High percentage error ({mape:.1%}) - consider feature engineering")

        return insights

    def get_validation_summary(self) -> dict[str, Any]:
        """Get summary of validation history."""
        if not self.validation_history:
            return {
                "total_validations": 0,
                "average_accuracy": 0.0,
                "accuracy_trend": "no_data",
            }

        accuracies = [v.overall_accuracy for v in self.validation_history]

        return {
            "total_validations": len(self.validation_history),
            "average_accuracy": sum(accuracies) / len(accuracies),
            "best_accuracy": max(accuracies),
            "worst_accuracy": min(accuracies),
            "latest_accuracy": accuracies[-1],
            "accuracy_trend": (
                "improving"
                if accuracies[-1] > accuracies[0]
                else "stable"
                if accuracies[-1] == accuracies[0]
                else "degrading"
            ),
        }

    def clear_validation_history(self):
        """Clear validation history."""
        self.validation_history.clear()
        logger.info("🗑️ Validation history cleared")

    async def health_check(self) -> dict[str, Any]:
        """Health check for accuracy validator."""
        summary = self.get_validation_summary()

        return {
            "service": "AccuracyValidator",
            "status": "healthy",
            "validations_performed": summary["total_validations"],
            "average_accuracy": summary.get("average_accuracy", 0.0),
        }
