"""
Prediction Generator Service
============================

Microservice responsible for core prediction generation and enhancement
with contextual and temporal intelligence.

Single Responsibility: Generate and enhance predictions only.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from ...protocols.predictive_protocols import (
    ContextualIntelligence,
    TemporalIntelligence,
)
from ..models import ModelingConfig

logger = logging.getLogger(__name__)


class PredictionGenerator:
    """
    Core prediction generation and enhancement microservice.

    Responsibilities:
    - Generate base predictions
    - Enhance with contextual intelligence
    - Enhance with temporal patterns
    - Extract enhancement factors
    """

    def __init__(
        self,
        config: ModelingConfig | None = None,
        predictive_analytics_service: Any = None,
        analytics_service: Any = None,  # Accept both parameter names
    ):
        self.config = config or ModelingConfig()
        # Support both parameter names for backwards compatibility
        self.analytics_service = analytics_service or predictive_analytics_service
        self.prediction_tracker: dict[str, dict[str, Any]] = {}
        logger.info("🎯 Prediction Generator initialized")
        self.predictive_service = predictive_analytics_service
        self.config = config or ModelingConfig()

        # Track active predictions
        self.active_predictions: dict[str, dict[str, Any]] = {}

        logger.info("🎯 Prediction Generator initialized")

    async def generate_enhanced_predictions(
        self,
        prediction_request: dict[str, Any],
        contextual_intelligence: ContextualIntelligence,
        temporal_intelligence: TemporalIntelligence,
    ) -> dict[str, Any]:
        """
        Generate predictions enhanced with intelligence analysis.

        Args:
            prediction_request: Request parameters for prediction
            contextual_intelligence: Contextual analysis data
            temporal_intelligence: Temporal pattern data

        Returns:
            Enhanced prediction result dictionary
        """
        try:
            logger.info("🎯 Generating enhanced predictions with intelligence context")

            # Get base predictions
            base_predictions = await self._get_base_predictions(prediction_request)

            # Enhance with contextual intelligence
            enhanced_predictions = await self._enhance_with_context(
                base_predictions, contextual_intelligence
            )

            # Enhance with temporal intelligence
            temporal_enhanced_predictions = await self._enhance_with_temporal_patterns(
                enhanced_predictions, temporal_intelligence
            )

            # Create prediction ID
            prediction_id = str(uuid.uuid4())

            # Build enhancement tracking
            intelligence_enhancements = {
                "contextual_factors": self._extract_contextual_factors(contextual_intelligence),
                "temporal_factors": self._extract_temporal_factors(temporal_intelligence),
                "enhancement_impact": self._calculate_enhancement_impact(
                    base_predictions, temporal_enhanced_predictions
                ),
            }

            # Final enhanced prediction result
            enhanced_result = {
                "prediction_id": prediction_id,
                "base_predictions": base_predictions,
                "enhanced_predictions": temporal_enhanced_predictions,
                "intelligence_enhancements": intelligence_enhancements,
                "generated_at": datetime.now().isoformat(),
            }

            # Track prediction
            self.active_predictions[prediction_id] = enhanced_result

            logger.info(f"✅ Enhanced predictions generated: {prediction_id}")
            return enhanced_result

        except Exception as e:
            logger.error(f"❌ Enhanced prediction generation failed: {e}")
            return {
                "prediction_id": str(uuid.uuid4()),
                "status": "generation_failed",
                "error": str(e),
                "generated_at": datetime.now().isoformat(),
            }

    async def _get_base_predictions(self, prediction_request: dict[str, Any]) -> dict[str, Any]:
        """
        Get base predictions from predictive analytics service.
        """
        if self.predictive_service:
            try:
                return await self.predictive_service.generate_predictions(prediction_request)
            except Exception as e:
                logger.warning(f"Base prediction service failed: {e}")

        # Fallback to mock predictions
        return {
            "predictions": {
                "growth_rate": 0.15,
                "engagement_score": 0.75,
                "reach_estimate": 10000,
            },
            "base_confidence": 0.7,
            "prediction_horizon": "30_days",
        }

    async def _enhance_with_context(
        self,
        base_predictions: dict[str, Any],
        contextual_intelligence: ContextualIntelligence,
    ) -> dict[str, Any]:
        """
        Enhance predictions with contextual intelligence.
        """
        enhanced = base_predictions.copy()

        # Apply contextual enhancements
        context_confidence = contextual_intelligence.context_confidence
        environmental_factors = contextual_intelligence.environmental_factors

        # Adjust predictions based on context
        predictions = enhanced.get("predictions", {})
        for key, value in predictions.items():
            if isinstance(value, (int, float)):
                # Apply context adjustment
                adjustment_factor = 1 + (context_confidence - 0.5) * 0.2
                predictions[key] = value * adjustment_factor

        # Add context metadata
        enhanced["context_enhancements"] = {
            "context_confidence": context_confidence,
            "environmental_score": environmental_factors.get("environmental_score", 0.5),
            "adjusted_by_context": True,
        }

        logger.debug(f"Context enhanced predictions with confidence: {context_confidence}")
        return enhanced

    async def _enhance_with_temporal_patterns(
        self,
        enhanced_predictions: dict[str, Any],
        temporal_intelligence: TemporalIntelligence,
    ) -> dict[str, Any]:
        """
        Further enhance predictions with temporal patterns.
        """
        temporal_enhanced = enhanced_predictions.copy()

        # Extract temporal factors
        seasonal_trends = temporal_intelligence.seasonal_trends
        temporal_intelligence.cyclical_patterns
        daily_patterns = temporal_intelligence.daily_patterns
        weekly_cycles = temporal_intelligence.weekly_cycles

        # Apply temporal adjustments
        predictions = temporal_enhanced.get("predictions", {})

        # Seasonal adjustment
        if seasonal_trends:
            current_season = self._get_current_season()
            seasonal_factor = seasonal_trends.get(f"{current_season}_trend", {}).get(
                "trend_strength", 1.0
            )

            for key, value in predictions.items():
                if isinstance(value, (int, float)):
                    predictions[key] = value * seasonal_factor

        # Daily consistency factor
        daily_consistency = daily_patterns.get("consistency_score", 0.5)
        weekly_strength = weekly_cycles.get("cyclical_strength", 0.5)

        # Add temporal metadata
        temporal_enhanced["temporal_enhancements"] = {
            "seasonal_adjusted": bool(seasonal_trends),
            "daily_consistency": daily_consistency,
            "weekly_strength": weekly_strength,
            "temporal_confidence": (daily_consistency + weekly_strength) / 2,
        }

        logger.debug("Temporal pattern enhancements applied")
        return temporal_enhanced

    def _extract_contextual_factors(
        self, contextual_intelligence: ContextualIntelligence
    ) -> dict[str, Any]:
        """Extract contextual factors for enhancement tracking."""
        return {
            "context_confidence": contextual_intelligence.context_confidence,
            "behavioral_confidence": contextual_intelligence.behavioral_insights.get(
                "confidence_score", 0.5
            ),
            "environmental_score": contextual_intelligence.environmental_factors.get(
                "environmental_score", 0.5
            ),
        }

    def _extract_temporal_factors(
        self, temporal_intelligence: TemporalIntelligence
    ) -> dict[str, Any]:
        """Extract temporal factors for enhancement tracking."""
        return {
            "seasonal_trends": bool(temporal_intelligence.seasonal_trends),
            "cyclical_patterns": bool(temporal_intelligence.cyclical_patterns),
            "daily_consistency": temporal_intelligence.daily_patterns.get("consistency_score", 0.5),
            "weekly_strength": temporal_intelligence.weekly_cycles.get("cyclical_strength", 0.5),
            "anomalies_detected": len(temporal_intelligence.temporal_anomalies),
        }

    def _calculate_enhancement_impact(
        self, base_predictions: dict[str, Any], enhanced_predictions: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate the impact of intelligence enhancements."""
        base_conf = base_predictions.get("base_confidence", 0.5)
        enhanced_conf = enhanced_predictions.get("context_enhancements", {}).get(
            "context_confidence", 0.5
        )

        improvement_factor = enhanced_conf / base_conf if base_conf > 0 else 1.0

        return {
            "improvement_factor": improvement_factor,
            "confidence_improvement": enhanced_conf - base_conf,
            "enhancement_quality": (
                "high"
                if improvement_factor > 1.2
                else "moderate"
                if improvement_factor > 1.1
                else "low"
            ),
        }

    def _get_current_season(self) -> str:
        """Get current season for seasonal adjustments."""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "fall"
        else:
            return "winter"

    def get_prediction(self, prediction_id: str) -> dict[str, Any] | None:
        """Retrieve a tracked prediction by ID."""
        return self.prediction_tracker.get(prediction_id)

    async def health_check(self) -> dict[str, Any]:
        """Health check for prediction generator."""
        return {
            "service": "PredictionGenerator",
            "status": "healthy",
            "active_predictions": len(self.prediction_tracker),
            "has_predictive_service": self.predictive_service is not None,
        }
