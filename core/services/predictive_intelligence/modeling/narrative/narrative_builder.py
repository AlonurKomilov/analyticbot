"""
Narrative Builder Service
==========================

Microservice responsible for generating natural language narratives
and explanations for predictions.

Single Responsibility: Generate prediction narratives only.
"""

import logging
from typing import Any

from ...protocols.predictive_protocols import ConfidenceLevel, PredictionNarrative
from ..models import EnhancedPrediction, ModelingConfig

logger = logging.getLogger(__name__)


class NarrativeBuilder:
    """
    Prediction narrative generation microservice.

    Responsibilities:
    - Generate prediction summaries
    - Generate detailed explanations
    - Extract key factors
    - Generate confidence explanations
    - Generate recommendations
    """

    def __init__(self, config: ModelingConfig | None = None, nlg_service: Any = None):
        self.config = config or ModelingConfig()
        self.nlg_service = nlg_service
        logger.info("📝 Narrative Builder initialized")

    async def generate_prediction_narrative(
        self, prediction: EnhancedPrediction
    ) -> PredictionNarrative:
        """
        Generate comprehensive natural language narrative for prediction.

        Args:
            prediction: Enhanced prediction with all factors

        Returns:
            PredictionNarrative with summary, explanation, and recommendations
        """
        try:
            logger.info(f"📝 Generating narrative for prediction {prediction.prediction_id}")

            # Generate components
            summary = self._generate_prediction_summary(prediction)
            explanation = self._generate_detailed_explanation(prediction)
            key_factors = self._extract_key_prediction_factors(prediction)
            confidence_explanation = self._generate_confidence_explanation(
                prediction.confidence_level
            )
            recommendations = self._generate_prediction_recommendations(prediction)

            narrative = PredictionNarrative(
                summary=summary,
                detailed_explanation=explanation,
                key_factors=key_factors,
                confidence_explanation=confidence_explanation,
                recommendations=recommendations,
            )

            logger.info("✅ Prediction narrative generated successfully")
            return narrative

        except Exception as e:
            logger.error(f"❌ Narrative generation failed: {e}")
            return PredictionNarrative(
                summary="Prediction narrative unavailable",
                detailed_explanation="",
                key_factors=[],
                confidence_explanation="",
                recommendations=[],
            )

    def _generate_prediction_summary(self, prediction: EnhancedPrediction) -> str:
        """Generate concise prediction summary."""
        confidence_text = prediction.confidence_level.value.replace("_", " ")
        enhancement_text = (
            f" (Enhanced by {prediction.enhancement_impact:.1%})"
            if prediction.enhancement_impact > 0
            else ""
        )

        summary = (
            f"Prediction with {confidence_text} confidence for "
            f"{prediction.prediction_horizon} {prediction.prediction_target}{enhancement_text}."
        )

        return summary

    def _generate_detailed_explanation(self, prediction: EnhancedPrediction) -> str:
        """Generate detailed prediction explanation with factors."""
        explanation_parts = []

        # Base prediction info
        explanation_parts.append(
            f"The prediction targets {prediction.prediction_target} "
            f"with a {prediction.prediction_horizon} time horizon."
        )

        # Contextual factors
        if prediction.contextual_factors:
            context_count = len(prediction.contextual_factors)
            explanation_parts.append(
                f"Analysis incorporated {context_count} contextual factors including: "
                + ", ".join(prediction.contextual_factors[:3])
                + ("..." if context_count > 3 else "")
            )

        # Temporal factors
        if prediction.temporal_factors:
            temporal_count = len(prediction.temporal_factors)
            explanation_parts.append(
                f"Temporal analysis considered {temporal_count} time-based patterns"
            )

        # Enhancement impact
        if prediction.enhancement_impact > 0:
            explanation_parts.append(
                f"Intelligence enhancements improved prediction accuracy "
                f"by {prediction.enhancement_impact:.1%}"
            )

        return " ".join(explanation_parts)

    def _extract_key_prediction_factors(self, prediction: EnhancedPrediction) -> list[str]:
        """Extract and format key factors influencing prediction."""
        key_factors = []

        # Add top contextual factors
        if prediction.contextual_factors:
            key_factors.extend(
                [f"Contextual: {factor}" for factor in prediction.contextual_factors[:3]]
            )

        # Add temporal factors
        if prediction.temporal_factors:
            key_factors.extend(
                [f"Temporal: {factor}" for factor in prediction.temporal_factors[:2]]
            )

        # Add confidence indicator
        key_factors.append(f"Confidence: {prediction.confidence_level.value.replace('_', ' ')}")

        return key_factors

    def _generate_confidence_explanation(self, confidence: ConfidenceLevel) -> str:
        """Generate explanation for confidence level."""
        explanations = {
            ConfidenceLevel.VERY_HIGH: (
                "This prediction has very high confidence due to strong data support, "
                "favorable contextual conditions, and consistent historical patterns"
            ),
            ConfidenceLevel.HIGH: (
                "This prediction has high confidence with reliable data quality "
                "and supportive contextual factors"
            ),
            ConfidenceLevel.MEDIUM: (
                "This prediction has medium confidence. While data is available, "
                "there is some uncertainty in contextual or temporal factors"
            ),
            ConfidenceLevel.LOW: (
                "This prediction has low confidence due to limited data, "
                "variable contextual conditions, or inconsistent patterns"
            ),
        }

        return explanations.get(confidence, "Confidence assessment unavailable")

    def _generate_prediction_recommendations(self, prediction: EnhancedPrediction) -> list[str]:
        """Generate actionable recommendations based on prediction."""
        recommendations = []

        # Confidence-based recommendations
        if prediction.confidence_level == ConfidenceLevel.VERY_HIGH:
            recommendations.append(
                "Confidence is very high - this prediction can be used confidently "
                "for planning and decision-making"
            )
        elif prediction.confidence_level == ConfidenceLevel.HIGH:
            recommendations.append(
                "Confidence is high - prediction is reliable for strategic decisions"
            )
        elif prediction.confidence_level == ConfidenceLevel.MEDIUM:
            recommendations.append(
                "Confidence is moderate - consider gathering more data or "
                "waiting for better conditions before acting"
            )
        else:
            recommendations.append(
                "Confidence is low - use this prediction with caution and "
                "seek additional validation"
            )

        # Contextual recommendations
        if prediction.contextual_factors:
            recommendations.append(
                f"Monitor {len(prediction.contextual_factors)} contextual factors "
                "that may affect outcomes"
            )

        # Temporal recommendations
        if prediction.temporal_factors:
            recommendations.append(
                "Consider temporal patterns when planning actions based on this prediction"
            )

        return recommendations

    async def generate_bulk_narratives(
        self, predictions: list[EnhancedPrediction]
    ) -> list[PredictionNarrative]:
        """
        Generate narratives for multiple predictions efficiently.

        Args:
            predictions: List of enhanced predictions

        Returns:
            List of prediction narratives
        """
        narratives = []
        for prediction in predictions:
            narrative = await self.generate_prediction_narrative(prediction)
            narratives.append(narrative)

        logger.info(f"✅ Generated {len(narratives)} prediction narratives")
        return narratives

    def customize_narrative_style(
        self, narrative: PredictionNarrative, style: str = "formal"
    ) -> PredictionNarrative:
        """
        Customize narrative style (formal, casual, technical).

        Args:
            narrative: Original narrative
            style: Target style ("formal", "casual", "technical")

        Returns:
            Customized narrative
        """
        # In real implementation, would use NLG service to transform style
        # For now, return original
        logger.info(f"📝 Customizing narrative to {style} style")
        return narrative

    async def health_check(self) -> dict[str, Any]:
        """Health check for narrative builder."""
        return {
            "service": "NarrativeBuilder",
            "status": "healthy",
            "nlg_service_available": self.nlg_service is not None,
            "supported_styles": self.config.narrative_styles,
        }
