"""
Result Formatter Service
=======================

Microservice responsible for formatting prediction results.
Handles result processing, feature creation, and output standardization.
"""

import logging
from datetime import datetime
from typing import Any

import numpy as np

from .models import (
    HealthMetrics,
    ResultFormatterProtocol,
    ServiceHealth,
)

logger = logging.getLogger(__name__)


class ResultFormatter(ResultFormatterProtocol):
    """
    Result formatting and processing service.

    Single responsibility: Format and standardize prediction results.
    """

    def __init__(self):
        # Health tracking
        self.health_metrics = HealthMetrics()

        logger.info("📋 Result Formatter initialized")

    def format_result(self, prediction: np.ndarray, metadata: dict[str, Any]) -> dict[str, Any]:
        """
        Format prediction result into standardized output

        Args:
            prediction: Raw prediction array
            metadata: Additional metadata for the result

        Returns:
            Formatted result dictionary
        """
        try:
            logger.debug("📊 Formatting prediction result")

            # Extract basic prediction info
            forecast_values = prediction.flatten().tolist() if prediction.size > 0 else []
            forecast_periods = len(forecast_values)

            # Calculate statistics
            stats = self._calculate_prediction_stats(prediction)

            # Format confidence intervals if available
            confidence_info = self._format_confidence_intervals(metadata)

            # Create formatted result
            formatted_result = {
                "predictions": {
                    "values": forecast_values,
                    "periods": forecast_periods,
                    "statistics": stats,
                },
                "confidence": confidence_info,
                "metadata": {
                    "model_version": metadata.get("model_version", "unknown"),
                    "execution_time_ms": metadata.get("execution_time_ms", 0),
                    "uncertainty_score": metadata.get("uncertainty_score"),
                    "cached": metadata.get("cached", False),
                    "generated_at": datetime.utcnow().isoformat(),
                },
                "quality_indicators": self._assess_prediction_quality(prediction, metadata),
            }

            # Update health metrics
            self.health_metrics.successful_predictions += 1
            self.health_metrics.last_prediction_time = datetime.utcnow()

            logger.debug(f"✅ Result formatted for {forecast_periods} periods")
            return formatted_result

        except Exception as e:
            self.health_metrics.failed_predictions += 1
            logger.error(f"❌ Result formatting failed: {e}")
            raise

    def create_features(self, prediction: np.ndarray) -> np.ndarray:
        """
        Create feature vector from prediction for next step forecasting

        Args:
            prediction: Prediction array

        Returns:
            Feature array for next prediction step
        """
        try:
            logger.debug("🔧 Creating features from prediction")

            if prediction.size == 0:
                logger.warning("⚠️ Empty prediction array, returning zero features")
                return np.zeros((1, 3))

            # Extract prediction value
            pred_value = float(prediction.flatten()[0])

            # Create derived features
            features = np.array(
                [
                    pred_value,  # Raw prediction
                    pred_value * 0.1,  # 10% of prediction (momentum proxy)
                    pred_value * 0.05,  # 5% of prediction (volatility proxy)
                    np.log(abs(pred_value) + 1e-8),  # Log-scaled value
                    pred_value**2 if abs(pred_value) < 10 else pred_value,  # Quadratic feature
                    np.tanh(pred_value),  # Bounded feature
                ]
            ).reshape(1, -1)

            logger.debug(f"✅ Created {features.shape[1]} features")
            return features

        except Exception as e:
            logger.error(f"❌ Feature creation failed: {e}")
            # Return zero features as fallback
            return np.zeros((1, 6))

    def format_batch_results(
        self, predictions: list[np.ndarray], metadata_list: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Format multiple prediction results

        Args:
            predictions: List of prediction arrays
            metadata_list: List of metadata dictionaries

        Returns:
            List of formatted results
        """
        try:
            logger.debug(f"📊 Formatting {len(predictions)} batch results")

            formatted_results = []

            for i, (prediction, metadata) in enumerate(
                zip(predictions, metadata_list, strict=False)
            ):
                try:
                    result = self.format_result(prediction, metadata)
                    result["batch_index"] = i
                    formatted_results.append(result)

                except Exception as e:
                    logger.error(f"❌ Batch result {i} formatting failed: {e}")
                    # Add error result
                    error_result = {
                        "predictions": {"values": [], "periods": 0},
                        "error": str(e),
                        "batch_index": i,
                        "metadata": {"generated_at": datetime.utcnow().isoformat()},
                    }
                    formatted_results.append(error_result)

            logger.debug(f"✅ Formatted {len(formatted_results)} batch results")
            return formatted_results

        except Exception as e:
            logger.error(f"❌ Batch formatting failed: {e}")
            return []

    def create_summary_report(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Create summary report from multiple results

        Args:
            results: List of formatted prediction results

        Returns:
            Summary report
        """
        try:
            logger.debug(f"📋 Creating summary report for {len(results)} results")

            if not results:
                return {"error": "No results to summarize"}

            # Extract statistics
            all_predictions = []
            execution_times = []
            error_count = 0

            for result in results:
                if "error" in result:
                    error_count += 1
                else:
                    all_predictions.extend(result.get("predictions", {}).get("values", []))
                    execution_times.append(result.get("metadata", {}).get("execution_time_ms", 0))

            summary = {
                "total_results": len(results),
                "successful_results": len(results) - error_count,
                "error_count": error_count,
                "success_rate": (len(results) - error_count) / len(results) if results else 0,
                "performance": {
                    "average_execution_time_ms": np.mean(execution_times) if execution_times else 0,
                    "total_execution_time_ms": sum(execution_times),
                },
                "predictions_summary": self._summarize_predictions(all_predictions),
                "generated_at": datetime.utcnow().isoformat(),
            }

            logger.debug("✅ Summary report created")
            return summary

        except Exception as e:
            logger.error(f"❌ Summary report creation failed: {e}")
            return {"error": str(e)}

    def get_health(self) -> ServiceHealth:
        """Get result formatter health status"""
        try:
            success_rate = (
                self.health_metrics.successful_predictions
                / (
                    self.health_metrics.successful_predictions
                    + self.health_metrics.failed_predictions
                )
                if (
                    self.health_metrics.successful_predictions
                    + self.health_metrics.failed_predictions
                )
                > 0
                else 1.0
            )

            is_healthy = success_rate >= 0.95

            return ServiceHealth(
                service_name="result_formatter",
                is_healthy=is_healthy,
                metrics=self.health_metrics,
                last_check=datetime.utcnow(),
            )

        except Exception as e:
            return ServiceHealth(
                service_name="result_formatter",
                is_healthy=False,
                metrics=HealthMetrics(),
                error_message=str(e),
            )

    # Private helper methods

    def _calculate_prediction_stats(self, prediction: np.ndarray) -> dict[str, Any]:
        """Calculate statistics for prediction array"""
        try:
            if prediction.size == 0:
                return {}

            values = prediction.flatten()

            return {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "median": float(np.median(values)),
                "range": float(np.max(values) - np.min(values)),
            }

        except Exception as e:
            logger.error(f"❌ Prediction stats calculation failed: {e}")
            return {}

    def _format_confidence_intervals(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Format confidence interval information"""
        try:
            confidence_info = {
                "interval": metadata.get("confidence_interval", 0.95),
                "uncertainty_score": metadata.get("uncertainty_score"),
            }

            if "confidence_lower" in metadata and metadata["confidence_lower"] is not None:
                confidence_info["lower_bounds"] = metadata["confidence_lower"].flatten().tolist()

            if "confidence_upper" in metadata and metadata["confidence_upper"] is not None:
                confidence_info["upper_bounds"] = metadata["confidence_upper"].flatten().tolist()

            return confidence_info

        except Exception as e:
            logger.error(f"❌ Confidence interval formatting failed: {e}")
            return {}

    def _assess_prediction_quality(
        self, prediction: np.ndarray, metadata: dict[str, Any]
    ) -> dict[str, str]:
        """Assess quality of predictions"""
        try:
            if prediction.size == 0:
                return {"overall": "poor", "reason": "no_predictions"}

            # Check for reasonable values
            values = prediction.flatten()
            has_nan = np.isnan(values).any()
            has_inf = np.isinf(values).any()
            extreme_values = np.any(np.abs(values) > 1e6)

            uncertainty_score = metadata.get("uncertainty_score", 0)

            if has_nan or has_inf:
                return {"overall": "poor", "reason": "invalid_values"}
            elif extreme_values:
                return {"overall": "poor", "reason": "extreme_values"}
            elif uncertainty_score and uncertainty_score > 0.5:
                return {"overall": "moderate", "reason": "high_uncertainty"}
            elif len(values) < 3:
                return {"overall": "moderate", "reason": "insufficient_periods"}
            else:
                return {"overall": "good", "reason": "normal_range"}

        except Exception as e:
            logger.error(f"❌ Quality assessment failed: {e}")
            return {"overall": "unknown", "reason": "assessment_error"}

    def _summarize_predictions(self, all_predictions: list[float]) -> dict[str, Any]:
        """Summarize prediction values across multiple results"""
        try:
            if not all_predictions:
                return {}

            predictions_array = np.array(all_predictions)

            return {
                "count": len(all_predictions),
                "mean": float(np.mean(predictions_array)),
                "std": float(np.std(predictions_array)),
                "min": float(np.min(predictions_array)),
                "max": float(np.max(predictions_array)),
                "percentiles": {
                    "25th": float(np.percentile(predictions_array, 25)),
                    "50th": float(np.percentile(predictions_array, 50)),
                    "75th": float(np.percentile(predictions_array, 75)),
                },
            }

        except Exception as e:
            logger.error(f"❌ Predictions summary failed: {e}")
            return {}
