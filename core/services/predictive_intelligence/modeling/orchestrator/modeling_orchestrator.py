"""
Modeling Orchestrator Service
==============================

Facade/Orchestrator that coordinates all predictive modeling microservices.
Provides backwards compatibility with original PredictiveModelingService.

Single Responsibility: Coordinate microservices and maintain backwards compatibility.
"""

import logging
from datetime import datetime
from typing import Any

from ...protocols.predictive_protocols import (
    ConfidenceLevel,
    ContextualIntelligence,
    PredictionNarrative,
    TemporalIntelligence,
)
from ..confidence.confidence_calculator import ConfidenceCalculator
from ..models import EnhancedPrediction, ModelingConfig
from ..narrative.narrative_builder import NarrativeBuilder
from ..prediction.prediction_generator import PredictionGenerator
from ..validation.accuracy_validator import AccuracyValidator

logger = logging.getLogger(__name__)


class ModelingOrchestrator:
    """
    Orchestrator for all predictive modeling microservices.

    Coordinates:
    - PredictionGenerator (generate enhanced predictions)
    - ConfidenceCalculator (calculate confidence levels)
    - NarrativeBuilder (generate natural language narratives)
    - AccuracyValidator (validate prediction accuracy)

    Provides backwards compatibility with original PredictiveModelingService.
    """

    def __init__(
        self,
        config: ModelingConfig | None = None,
        nlg_service: Any = None,
        analytics_service: Any = None,
        # Support legacy parameter names for backwards compatibility
        predictive_analytics_service: Any = None,
        config_manager: Any = None,
    ):
        self.config = config or ModelingConfig()

        # Use new or legacy parameter names
        analytics = analytics_service or predictive_analytics_service

        # Initialize all microservices
        self.prediction_generator = PredictionGenerator(
            config=self.config,
            analytics_service=analytics,
        )

        self.confidence_calculator = ConfidenceCalculator(
            config=self.config,
        )

        self.narrative_builder = NarrativeBuilder(
            config=self.config,
            nlg_service=nlg_service,
        )

        self.accuracy_validator = AccuracyValidator(
            config=self.config,
        )

        logger.info("🎭 Modeling Orchestrator initialized with all microservices")

    async def generate_enhanced_predictions(
        self,
        prediction_request: dict[str, Any],
        contextual_intelligence: ContextualIntelligence,
        temporal_intelligence: TemporalIntelligence,
    ) -> dict[str, Any]:
        """
        Generate enhanced predictions with full intelligence.

        Orchestrates prediction generation, confidence calculation,
        and narrative generation.

        Args:
            prediction_request: Prediction parameters
            contextual_intelligence: Contextual intelligence service
            temporal_intelligence: Temporal intelligence service

        Returns:
            Complete prediction result with enhancements
        """
        try:
            logger.info("🎭 Orchestrating enhanced prediction generation")

            # Step 1: Generate enhanced predictions
            prediction_result = await self.prediction_generator.generate_enhanced_predictions(
                prediction_request, contextual_intelligence, temporal_intelligence
            )

            # Step 2: Calculate confidence
            context_factors = {
                "contextual_intelligence": contextual_intelligence,
                "temporal_intelligence": temporal_intelligence,
            }
            confidence_level = await self.confidence_calculator.calculate_prediction_confidence(
                prediction_result, context_factors
            )

            # Add confidence to result
            prediction_result["confidence_level"] = confidence_level

            logger.info("✅ Enhanced predictions generated successfully")
            return prediction_result

        except Exception as e:
            logger.error(f"❌ Enhanced prediction generation failed: {e}")
            raise

    async def generate_prediction_narrative(
        self, predictions: dict[str, Any], intelligence_context: dict[str, Any]
    ) -> PredictionNarrative:
        """
        Generate natural language narrative for prediction.

        Protocol-compatible method that accepts dict arguments.

        Args:
            predictions: Prediction data dictionary
            intelligence_context: Intelligence context data

        Returns:
            PredictionNarrative with summary, explanation, and recommendations
        """
        # Build EnhancedPrediction from dict
        prediction = EnhancedPrediction(
            prediction_id=predictions.get("prediction_id", "unknown"),
            base_predictions=predictions,
            enhanced_predictions=predictions,
            intelligence_enhancements=intelligence_context,
            confidence_analysis={},
            prediction_metadata={},
            generated_at=datetime.now().isoformat(),
        )
        return await self.narrative_builder.generate_prediction_narrative(prediction)

    async def calculate_prediction_confidence(
        self, predictions: dict[str, Any], context_factors: dict[str, Any]
    ) -> ConfidenceLevel:
        """
        Calculate overall prediction confidence.

        Args:
            predictions: Prediction data
            context_factors: Contextual and temporal factors

        Returns:
            ConfidenceLevel enum
        """
        return await self.confidence_calculator.calculate_prediction_confidence(
            predictions, context_factors
        )

    async def validate_prediction_accuracy(
        self, prediction_id: str, actual_results: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validate prediction accuracy against actual outcomes.

        Protocol-compatible method that accepts prediction_id and actual_results.

        Args:
            prediction_id: ID of the prediction to validate
            actual_results: Actual measured outcomes

        Returns:
            Dict with validation results
        """
        # Retrieve the prediction
        prediction = self.get_prediction_by_id(prediction_id)
        if not prediction:
            return {
                "prediction_id": prediction_id,
                "validation_status": "failed",
                "error": "Prediction not found",
            }

        # Validate using the validator service
        validation_result = await self.accuracy_validator.validate_prediction_accuracy(
            prediction, actual_results
        )

        # Return as dict for protocol compatibility
        return {
            "prediction_id": prediction_id,
            "validation_status": "completed",
            "overall_accuracy": validation_result.overall_accuracy,
            "accuracy_metrics": validation_result.accuracy_by_metric,
            "error_analysis": validation_result.error_analysis,
            "learning_insights": validation_result.learning_insights,
        }

    async def generate_complete_prediction(
        self,
        prediction_request: dict[str, Any],
        contextual_intelligence: ContextualIntelligence,
        temporal_intelligence: TemporalIntelligence,
    ) -> dict[str, Any]:
        """
        Generate complete prediction with all enhancements and narrative.

        Convenience method that orchestrates all services in one call.

        Args:
            prediction_request: Prediction parameters
            contextual_intelligence: Contextual intelligence service
            temporal_intelligence: Temporal intelligence service

        Returns:
            Complete prediction with narrative
        """
        # Generate enhanced predictions
        prediction_result = await self.generate_enhanced_predictions(
            prediction_request, contextual_intelligence, temporal_intelligence
        )

        # Build EnhancedPrediction object
        enhanced_prediction = EnhancedPrediction(
            prediction_id=prediction_result["prediction_id"],
            base_predictions=prediction_result,
            enhanced_predictions=prediction_result,
            intelligence_enhancements={
                "contextual_intelligence": contextual_intelligence,
                "temporal_intelligence": temporal_intelligence,
            },
            confidence_analysis=prediction_result["confidence_level"],
            prediction_metadata=prediction_request,
            generated_at=datetime.now().isoformat(),
            prediction_target=prediction_request.get("target", "unknown"),
            prediction_horizon=prediction_request.get("horizon", "unknown"),
            confidence_level=prediction_result["confidence_level"],
            contextual_factors=prediction_result.get("contextual_factors", []),
            temporal_factors=prediction_result.get("temporal_factors", []),
            enhancement_impact=prediction_result.get("enhancement_impact", 0.0),
        )

        # Generate narrative (protocol-compatible)
        narrative = await self.generate_prediction_narrative(
            prediction_result,
            {
                "contextual_intelligence": contextual_intelligence,
                "temporal_intelligence": temporal_intelligence,
            },
        )

        # Combine results
        prediction_result["narrative"] = {
            "summary": narrative.summary,
            "detailed_explanation": narrative.detailed_explanation,
            "key_factors": narrative.key_factors,
            "confidence_explanation": narrative.confidence_explanation,
            "recommendations": narrative.recommendations,
        }

        return prediction_result

    def get_validation_summary(self) -> dict[str, Any]:
        """Get summary of validation history."""
        return self.accuracy_validator.get_validation_summary()

    def get_prediction_by_id(self, prediction_id: str) -> dict[str, Any] | None:
        """Retrieve tracked prediction by ID."""
        return self.prediction_generator.get_prediction(prediction_id)

    async def health_check(self) -> dict[str, Any]:
        """
        Comprehensive health check for all microservices.

        Returns:
            Health status of orchestrator and all microservices
        """
        # Check all microservices
        prediction_health = await self.prediction_generator.health_check()
        confidence_health = await self.confidence_calculator.health_check()
        narrative_health = await self.narrative_builder.health_check()
        validation_health = await self.accuracy_validator.health_check()

        # Aggregate health status
        all_healthy = all(
            [
                prediction_health["status"] == "healthy",
                confidence_health["status"] == "healthy",
                narrative_health["status"] == "healthy",
                validation_health["status"] == "healthy",
            ]
        )

        return {
            "service": "ModelingOrchestrator",
            "status": "healthy" if all_healthy else "degraded",
            "microservices": {
                "prediction_generator": prediction_health,
                "confidence_calculator": confidence_health,
                "narrative_builder": narrative_health,
                "accuracy_validator": validation_health,
            },
            "validations_performed": validation_health.get("validations_performed", 0),
        }


# Backwards compatibility alias
PredictiveModelingService = ModelingOrchestrator
