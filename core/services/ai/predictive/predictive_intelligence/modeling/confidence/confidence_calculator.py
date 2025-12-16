"""
Confidence Calculator Service
==============================

Microservice responsible for calculating prediction confidence levels
based on multiple factors and context.

Single Responsibility: Calculate and calibrate confidence only.
"""

import logging
from typing import Any

from ...protocols.predictive_protocols import ConfidenceLevel
from ..models import ModelingConfig

logger = logging.getLogger(__name__)


class ConfidenceCalculator:
    """
    Confidence calculation and calibration microservice.

    Responsibilities:
    - Calculate overall prediction confidence
    - Assess contextual confidence
    - Assess temporal confidence
    - Assess data quality confidence
    - Map numeric scores to confidence levels
    """

    def __init__(self, config: ModelingConfig | None = None):
        self.config = config or ModelingConfig()
        logger.info("📊 Confidence Calculator initialized")

    async def calculate_prediction_confidence(
        self, predictions: dict[str, Any], context_factors: dict[str, Any]
    ) -> ConfidenceLevel:
        """
        Calculate overall prediction confidence based on multiple factors.

        Args:
            predictions: Prediction data with base confidence
            context_factors: Contextual and temporal intelligence

        Returns:
            ConfidenceLevel enum value
        """
        try:
            logger.info("📊 Calculating prediction confidence")

            # Extract confidence factors
            contextual_intelligence = context_factors.get("contextual_intelligence", {})
            temporal_intelligence = context_factors.get("temporal_intelligence", {})

            # Calculate component confidence scores
            contextual_confidence = self._calculate_contextual_confidence(contextual_intelligence)
            temporal_confidence = self._calculate_temporal_confidence(temporal_intelligence)
            data_quality_confidence = self._calculate_data_quality_confidence(predictions)
            model_confidence = self._calculate_model_confidence(predictions)

            # Weighted overall confidence
            weights = self.config.context_weight_factors
            overall_confidence = (
                contextual_confidence * weights["environmental"]
                + temporal_confidence * weights["temporal"]
                + data_quality_confidence * weights["competitive"]
                + model_confidence * weights["behavioral"]
            )

            # Map to confidence level
            confidence_level = self._map_to_confidence_level(overall_confidence)

            logger.info(f"✅ Prediction confidence calculated: {confidence_level.value}")
            return confidence_level

        except Exception as e:
            logger.error(f"❌ Confidence calculation failed: {e}")
            return ConfidenceLevel.LOW

    def _calculate_contextual_confidence(self, contextual_intelligence: dict[str, Any]) -> float:
        """Calculate confidence from contextual intelligence."""
        return contextual_intelligence.get("context_confidence", 0.5)

    def _calculate_temporal_confidence(self, temporal_intelligence: dict[str, Any]) -> float:
        """Calculate confidence from temporal intelligence."""
        daily_consistency = temporal_intelligence.get("daily_patterns", {}).get(
            "consistency_score", 0.5
        )
        weekly_strength = temporal_intelligence.get("weekly_cycles", {}).get(
            "cyclical_strength", 0.5
        )

        return (daily_consistency + weekly_strength) / 2

    def _calculate_data_quality_confidence(self, predictions: dict[str, Any]) -> float:
        """
        Calculate confidence from data quality.

        Assesses:
        - Completeness of data
        - Freshness of data
        - Data consistency
        """
        # Check if predictions have required fields
        has_predictions = bool(predictions.get("predictions"))
        has_confidence = "base_confidence" in predictions
        has_horizon = "prediction_horizon" in predictions

        # Calculate quality score
        completeness = sum([has_predictions, has_confidence, has_horizon]) / 3

        # Mock freshness (would check data timestamps in real implementation)
        freshness = 0.8

        # Average quality factors
        quality_confidence = (completeness + freshness) / 2

        return quality_confidence

    def _calculate_model_confidence(self, predictions: dict[str, Any]) -> float:
        """
        Calculate confidence from model performance.

        Uses base confidence from prediction model.
        """
        base_confidence = predictions.get("base_confidence", 0.75)
        return base_confidence

    def _map_to_confidence_level(self, overall_confidence: float) -> ConfidenceLevel:
        """
        Map numeric confidence score to ConfidenceLevel enum.

        Args:
            overall_confidence: Float between 0 and 1

        Returns:
            ConfidenceLevel enum
        """
        thresholds = self.config.confidence_thresholds

        if overall_confidence >= thresholds["very_high"]:
            return ConfidenceLevel.VERY_HIGH
        elif overall_confidence >= thresholds["high"]:
            return ConfidenceLevel.HIGH
        elif overall_confidence >= thresholds["medium"]:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def calculate_confidence_calibration(
        self, predicted_confidence: ConfidenceLevel, accuracy_metrics: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Calculate how well confidence predictions match actual accuracy.

        Used for model calibration and improvement.

        Args:
            predicted_confidence: Original predicted confidence level
            accuracy_metrics: Actual accuracy results

        Returns:
            Calibration analysis dictionary
        """
        overall_accuracy = accuracy_metrics.get("overall_accuracy", 0.0)

        # Expected accuracy for each confidence level
        confidence_values = {
            ConfidenceLevel.VERY_HIGH: 0.9,
            ConfidenceLevel.HIGH: 0.75,
            ConfidenceLevel.MEDIUM: 0.6,
            ConfidenceLevel.LOW: 0.45,
        }

        expected_accuracy = confidence_values.get(predicted_confidence, 0.6)
        calibration_error = abs(expected_accuracy - overall_accuracy)

        return {
            "predicted_confidence": predicted_confidence.value,
            "expected_accuracy": expected_accuracy,
            "actual_accuracy": overall_accuracy,
            "calibration_error": calibration_error,
            "calibration_quality": (
                "good" if calibration_error < 0.1 else "fair" if calibration_error < 0.2 else "poor"
            ),
        }

    def generate_confidence_explanation(self, confidence: ConfidenceLevel) -> str:
        """
        Generate human-readable explanation of confidence level.

        Args:
            confidence: ConfidenceLevel enum

        Returns:
            Explanation string
        """
        explanations = {
            ConfidenceLevel.VERY_HIGH: (
                "Very high confidence - predictions are well-supported by data, "
                "strong contextual factors, and consistent temporal patterns"
            ),
            ConfidenceLevel.HIGH: (
                "High confidence - predictions are reliable with good data quality "
                "and favorable contextual conditions"
            ),
            ConfidenceLevel.MEDIUM: (
                "Medium confidence - predictions are reasonable but with some "
                "uncertainty in contextual or temporal factors"
            ),
            ConfidenceLevel.LOW: (
                "Low confidence - predictions have significant uncertainty due to "
                "limited data, variable context, or inconsistent patterns"
            ),
        }

        return explanations.get(confidence, "Confidence level assessment unavailable")

    async def health_check(self) -> dict[str, Any]:
        """Health check for confidence calculator."""
        return {
            "service": "ConfidenceCalculator",
            "status": "healthy",
            "confidence_levels": [level.value for level in ConfidenceLevel],
            "thresholds_configured": bool(self.config.confidence_thresholds),
        }
