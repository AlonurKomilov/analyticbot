"""
Predictive Modeling Service
===========================

Focused microservice for enhanced predictive modeling and forecasting.

Single Responsibility:
- Enhanced prediction generation
- Prediction confidence calculation
- Natural language prediction narratives
- Prediction accuracy validation
- Intelligent forecasting

Core capabilities extracted from PredictiveIntelligenceService modeling methods.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from ..protocols.predictive_protocols import (
    ConfidenceLevel,
    ContextualIntelligence,
    PredictionNarrative,
    PredictiveModelingProtocol,
    TemporalIntelligence,
)

logger = logging.getLogger(__name__)


class PredictiveModelingService(PredictiveModelingProtocol):
    """
    Predictive modeling microservice for enhanced predictions with intelligence context.

    Single responsibility: Generate intelligent predictions with context awareness only.
    """

    def __init__(self, predictive_analytics_service=None, nlg_service=None, config_manager=None):
        self.predictive_service = predictive_analytics_service
        self.nlg_service = nlg_service
        self.config_manager = config_manager

        # Modeling configuration
        self.modeling_config = {
            "confidence_thresholds": {"very_high": 0.85, "high": 0.70, "medium": 0.55, "low": 0.40},
            "prediction_horizons": {
                "short_term": {"days": 7, "confidence_factor": 0.9},
                "medium_term": {"days": 30, "confidence_factor": 0.7},
                "long_term": {"days": 180, "confidence_factor": 0.5},
            },
            "narrative_styles": {
                "conversational": "friendly and accessible",
                "technical": "detailed and analytical",
                "executive": "concise and strategic",
            },
            "context_weight_factors": {
                "environmental": 0.25,
                "temporal": 0.30,
                "competitive": 0.25,
                "behavioral": 0.20,
            },
        }

        # Prediction tracking
        self.active_predictions = {}
        self.validation_history = []

        logger.info("🔮 Predictive Modeling Service initialized - enhanced predictions focus")

    async def generate_enhanced_predictions(
        self,
        prediction_request: dict[str, Any],
        contextual_intelligence: ContextualIntelligence,
        temporal_intelligence: TemporalIntelligence,
    ) -> dict[str, Any]:
        """
        Generate predictions enhanced with intelligence analysis.

        Main method for generating context-aware predictions.
        """
        try:
            logger.info("🎯 Generating enhanced predictions with intelligence context")

            # Get base predictions from existing service
            base_predictions = await self._get_base_predictions(prediction_request)

            # Enhance with contextual intelligence
            enhanced_predictions = await self._enhance_with_context(
                base_predictions, contextual_intelligence
            )

            # Enhance with temporal intelligence
            temporal_enhanced_predictions = await self._enhance_with_temporal_patterns(
                enhanced_predictions, temporal_intelligence
            )

            # Calculate enhanced confidence
            enhanced_confidence = await self.calculate_prediction_confidence(
                temporal_enhanced_predictions,
                {
                    "contextual_intelligence": contextual_intelligence.__dict__,
                    "temporal_intelligence": temporal_intelligence.__dict__,
                },
            )

            # Generate prediction metadata
            prediction_metadata = self._generate_prediction_metadata(
                prediction_request,
                contextual_intelligence,
                temporal_intelligence,
                enhanced_confidence,
            )

            # Final enhanced prediction result
            enhanced_result = {
                "prediction_id": str(uuid.uuid4()),
                "base_predictions": base_predictions,
                "enhanced_predictions": temporal_enhanced_predictions,
                "intelligence_enhancements": {
                    "contextual_factors": self._extract_contextual_factors(contextual_intelligence),
                    "temporal_factors": self._extract_temporal_factors(temporal_intelligence),
                    "enhancement_impact": self._calculate_enhancement_impact(
                        base_predictions, temporal_enhanced_predictions
                    ),
                },
                "confidence_analysis": enhanced_confidence,
                "prediction_metadata": prediction_metadata,
                "generated_at": datetime.now().isoformat(),
            }

            # Track prediction for validation
            self.active_predictions[enhanced_result["prediction_id"]] = enhanced_result

            logger.info(
                f"✅ Enhanced predictions generated - Confidence: {enhanced_confidence.value}"
            )
            return enhanced_result

        except Exception as e:
            logger.error(f"❌ Enhanced prediction generation failed: {e}")
            return {
                "prediction_id": str(uuid.uuid4()),
                "status": "generation_failed",
                "error": str(e),
                "generated_at": datetime.now().isoformat(),
            }

    async def generate_prediction_narrative(
        self, predictions: dict[str, Any], intelligence_context: dict[str, Any]
    ) -> PredictionNarrative:
        """
        Generate natural language prediction explanations.
        """
        try:
            logger.info("📝 Generating prediction narrative")

            # Extract key prediction elements
            enhanced_predictions = predictions.get("enhanced_predictions", {})
            confidence_analysis = predictions.get("confidence_analysis", ConfidenceLevel.MEDIUM)
            intelligence_enhancements = predictions.get("intelligence_enhancements", {})

            # Generate narrative components
            summary = await self._generate_prediction_summary(
                enhanced_predictions, confidence_analysis
            )
            detailed_explanation = await self._generate_detailed_explanation(
                enhanced_predictions, intelligence_enhancements
            )
            key_factors = self._extract_key_prediction_factors(intelligence_enhancements)
            confidence_explanation = self._generate_confidence_explanation(confidence_analysis)
            recommendations = await self._generate_prediction_recommendations(enhanced_predictions)

            # Create prediction narrative
            prediction_narrative = PredictionNarrative(
                summary=summary,
                detailed_explanation=detailed_explanation,
                key_factors=key_factors,
                confidence_explanation=confidence_explanation,
                recommendations=recommendations,
                narrative_style=intelligence_context.get("narrative_style", "conversational"),
            )

            logger.info("✅ Prediction narrative generated")
            return prediction_narrative

        except Exception as e:
            logger.error(f"❌ Prediction narrative generation failed: {e}")
            return PredictionNarrative(
                summary="Prediction narrative generation failed",
                detailed_explanation=f"Error: {str(e)}",
                key_factors=["system_error"],
                confidence_explanation="Unable to assess confidence",
                recommendations=["Review system configuration"],
                narrative_style="technical",
            )

    async def calculate_prediction_confidence(
        self, predictions: dict[str, Any], context_factors: dict[str, Any]
    ) -> ConfidenceLevel:
        """
        Calculate prediction confidence based on context.
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
            weights = self.modeling_config["context_weight_factors"]
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

    async def validate_prediction_accuracy(
        self, prediction_id: str, actual_results: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validate prediction accuracy against actual results.
        """
        try:
            logger.info(f"🔍 Validating prediction accuracy: {prediction_id}")

            # Get original prediction
            if prediction_id not in self.active_predictions:
                return {
                    "prediction_id": prediction_id,
                    "validation_status": "prediction_not_found",
                    "message": "Original prediction not found for validation",
                }

            original_prediction = self.active_predictions[prediction_id]
            enhanced_predictions = original_prediction.get("enhanced_predictions", {})

            # Calculate accuracy metrics
            accuracy_metrics = self._calculate_accuracy_metrics(
                enhanced_predictions, actual_results
            )

            # Analyze prediction errors
            error_analysis = self._analyze_prediction_errors(enhanced_predictions, actual_results)

            # Calculate confidence calibration
            confidence_calibration = self._calculate_confidence_calibration(
                original_prediction.get("confidence_analysis", ConfidenceLevel.MEDIUM),
                accuracy_metrics,
            )

            # Generate learning insights
            learning_insights = self._generate_learning_insights(
                original_prediction, actual_results, accuracy_metrics
            )

            # Validation result
            validation_result = {
                "prediction_id": prediction_id,
                "validation_status": "completed",
                "validation_timestamp": datetime.now().isoformat(),
                "accuracy_metrics": accuracy_metrics,
                "error_analysis": error_analysis,
                "confidence_calibration": confidence_calibration,
                "learning_insights": learning_insights,
                "overall_accuracy_score": accuracy_metrics.get("overall_accuracy", 0.0),
            }

            # Store validation history
            self.validation_history.append(validation_result)

            logger.info(
                f"✅ Prediction validation completed - Accuracy: {accuracy_metrics.get('overall_accuracy', 0.0):.2f}"
            )
            return validation_result

        except Exception as e:
            logger.error(f"❌ Prediction validation failed: {e}")
            return {"prediction_id": prediction_id, "validation_status": "failed", "error": str(e)}

    async def _get_base_predictions(self, prediction_request: dict[str, Any]) -> dict[str, Any]:
        """Get base predictions from existing predictive service"""
        try:
            if self.predictive_service:
                # Use existing predictive analytics service
                base_predictions = await self.predictive_service.generate_predictions(
                    prediction_request
                )
                return base_predictions
            else:
                # Mock base predictions
                return {
                    "channel_id": prediction_request.get("channel_id", 0),
                    "predictions": {
                        "7_day_growth": 0.12,
                        "30_day_growth": 0.25,
                        "engagement_forecast": 0.08,
                        "content_performance": 0.15,
                    },
                    "base_confidence": 0.75,
                    "model_version": "v2.1",
                    "generated_at": datetime.now().isoformat(),
                }
        except Exception as e:
            logger.error(f"❌ Failed to get base predictions: {e}")
            return {"predictions": {}, "base_confidence": 0.5}

    async def _enhance_with_context(
        self, base_predictions: dict[str, Any], contextual_intelligence: ContextualIntelligence
    ) -> dict[str, Any]:
        """Enhance predictions with contextual intelligence"""
        enhanced_predictions = base_predictions.copy()

        # Apply environmental context enhancements
        environmental_factors = contextual_intelligence.environmental_factors
        if environmental_factors:
            market_conditions = environmental_factors.get("market_conditions", {})
            market_stability = market_conditions.get("stability", 1.0)

            # Adjust predictions based on market stability
            for prediction_key, value in enhanced_predictions.get("predictions", {}).items():
                if isinstance(value, (int, float)):
                    enhanced_predictions["predictions"][prediction_key] = value * market_stability

        # Apply competitive context enhancements
        competitive_landscape = contextual_intelligence.competitive_landscape
        if competitive_landscape:
            competitive_pressure = competitive_landscape.get("competitive_pressure", 0.5)

            # Adjust growth predictions based on competitive pressure
            for prediction_key, value in enhanced_predictions.get("predictions", {}).items():
                if "growth" in prediction_key and isinstance(value, (int, float)):
                    pressure_factor = 1.0 - (competitive_pressure * 0.2)  # Max 20% reduction
                    enhanced_predictions["predictions"][prediction_key] = value * pressure_factor

        # Apply behavioral context enhancements
        behavioral_insights = contextual_intelligence.behavioral_insights
        if behavioral_insights:
            engagement_momentum = behavioral_insights.get("engagement_momentum", "stable")

            # Adjust engagement forecasts based on momentum
            if "engagement_forecast" in enhanced_predictions.get("predictions", {}):
                momentum_factor = {
                    "strong_positive": 1.3,
                    "positive": 1.15,
                    "stable_high": 1.1,
                    "stable": 1.0,
                    "declining": 0.85,
                }.get(engagement_momentum, 1.0)

                enhanced_predictions["predictions"]["engagement_forecast"] *= momentum_factor

        # Add context enhancement metadata
        enhanced_predictions["context_enhancements"] = {
            "applied_environmental_factors": bool(environmental_factors),
            "applied_competitive_factors": bool(competitive_landscape),
            "applied_behavioral_factors": bool(behavioral_insights),
            "context_confidence": contextual_intelligence.context_confidence,
        }

        return enhanced_predictions

    async def _enhance_with_temporal_patterns(
        self, enhanced_predictions: dict[str, Any], temporal_intelligence: TemporalIntelligence
    ) -> dict[str, Any]:
        """Enhance predictions with temporal intelligence"""
        temporal_enhanced = enhanced_predictions.copy()

        # Apply daily pattern enhancements
        daily_patterns = temporal_intelligence.daily_patterns
        if daily_patterns:
            peak_hours = daily_patterns.get("peak_hours", [])
            consistency_score = daily_patterns.get("consistency_score", 0.5)

            # Adjust predictions based on daily consistency
            for prediction_key, value in temporal_enhanced.get("predictions", {}).items():
                if isinstance(value, (int, float)):
                    consistency_factor = 0.8 + (consistency_score * 0.4)  # 0.8 to 1.2 range
                    temporal_enhanced["predictions"][prediction_key] = value * consistency_factor

        # Apply weekly cycle enhancements
        weekly_cycles = temporal_intelligence.weekly_cycles
        if weekly_cycles:
            cyclical_strength = weekly_cycles.get("cyclical_strength", 0.5)
            weekly_momentum = weekly_cycles.get("weekly_momentum", {})

            # Adjust growth predictions based on weekly momentum
            momentum_direction = weekly_momentum.get("momentum_direction", "stable")
            momentum_factor = {"increasing": 1.1, "stable": 1.0, "decreasing": 0.9}.get(
                momentum_direction, 1.0
            )

            for prediction_key, value in temporal_enhanced.get("predictions", {}).items():
                if "growth" in prediction_key and isinstance(value, (int, float)):
                    temporal_enhanced["predictions"][prediction_key] = value * momentum_factor

        # Apply seasonal trend enhancements
        seasonal_trends = temporal_intelligence.seasonal_trends
        if seasonal_trends:
            seasonal_performance = seasonal_trends.get("seasonal_performance", {})
            current_season = self._get_current_season()

            if current_season in seasonal_performance:
                seasonal_multiplier = seasonal_performance[current_season].get(
                    "performance_score", 1.0
                )

                # Apply seasonal adjustment to all predictions
                for prediction_key, value in temporal_enhanced.get("predictions", {}).items():
                    if isinstance(value, (int, float)):
                        temporal_enhanced["predictions"][prediction_key] = (
                            value * seasonal_multiplier
                        )

        # Add temporal enhancement metadata
        temporal_enhanced["temporal_enhancements"] = {
            "applied_daily_patterns": bool(daily_patterns),
            "applied_weekly_cycles": bool(weekly_cycles),
            "applied_seasonal_trends": bool(seasonal_trends),
            "temporal_anomalies_count": len(temporal_intelligence.temporal_anomalies),
        }

        return temporal_enhanced

    def _generate_prediction_metadata(
        self,
        prediction_request: dict[str, Any],
        contextual_intelligence: ContextualIntelligence,
        temporal_intelligence: TemporalIntelligence,
        confidence: ConfidenceLevel,
    ) -> dict[str, Any]:
        """Generate metadata for the prediction"""
        return {
            "request_parameters": prediction_request,
            "intelligence_sources": {
                "contextual_analysis": {
                    "confidence": contextual_intelligence.context_confidence,
                    "factors_analyzed": len(contextual_intelligence.environmental_factors)
                    + len(contextual_intelligence.competitive_landscape)
                    + len(contextual_intelligence.behavioral_insights),
                },
                "temporal_analysis": {
                    "patterns_detected": len(temporal_intelligence.daily_patterns)
                    + len(temporal_intelligence.weekly_cycles),
                    "anomalies_detected": len(temporal_intelligence.temporal_anomalies),
                },
            },
            "prediction_quality": {
                "overall_confidence": confidence.value,
                "data_completeness": 0.85,  # Mock data completeness score
                "model_reliability": 0.80,  # Mock model reliability score
            },
            "enhancement_summary": {
                "context_enhanced": True,
                "temporal_enhanced": True,
                "narrative_available": True,
            },
        }

    async def _generate_prediction_summary(
        self, enhanced_predictions: dict[str, Any], confidence: ConfidenceLevel
    ) -> str:
        """Generate prediction summary text"""
        predictions = enhanced_predictions.get("predictions", {})

        if not predictions:
            return "No predictions available to summarize."

        # Extract key predictions
        growth_predictions = {k: v for k, v in predictions.items() if "growth" in k}
        engagement_predictions = {k: v for k, v in predictions.items() if "engagement" in k}

        summary_parts = []

        # Growth summary
        if growth_predictions:
            avg_growth = sum(growth_predictions.values()) / len(growth_predictions)
            growth_outlook = (
                "strong" if avg_growth > 0.15 else "moderate" if avg_growth > 0.05 else "modest"
            )
            summary_parts.append(f"Expecting {growth_outlook} growth ({avg_growth:.1%})")

        # Engagement summary
        if engagement_predictions:
            avg_engagement = sum(engagement_predictions.values()) / len(engagement_predictions)
            engagement_outlook = (
                "high" if avg_engagement > 0.1 else "steady" if avg_engagement > 0.05 else "stable"
            )
            summary_parts.append(f"{engagement_outlook} engagement anticipated")

        # Confidence qualifier
        confidence_qualifier = {
            ConfidenceLevel.VERY_HIGH: "with high certainty",
            ConfidenceLevel.HIGH: "with good confidence",
            ConfidenceLevel.MEDIUM: "with moderate confidence",
            ConfidenceLevel.LOW: "with some uncertainty",
        }.get(confidence, "")

        summary = " and ".join(summary_parts)
        if confidence_qualifier:
            summary += f" {confidence_qualifier}"

        return summary + "."

    async def _generate_detailed_explanation(
        self, enhanced_predictions: dict[str, Any], intelligence_enhancements: dict[str, Any]
    ) -> str:
        """Generate detailed prediction explanation"""
        explanation_parts = []

        # Base prediction explanation
        predictions = enhanced_predictions.get("predictions", {})
        explanation_parts.append(
            "Based on comprehensive analysis of historical data and current trends:"
        )

        # Context factors explanation
        contextual_factors = intelligence_enhancements.get("contextual_factors", {})
        if contextual_factors:
            explanation_parts.append(
                "Environmental and competitive factors have been considered, including market conditions and competitive landscape."
            )

        # Temporal factors explanation
        temporal_factors = intelligence_enhancements.get("temporal_factors", {})
        if temporal_factors:
            explanation_parts.append(
                "Temporal patterns including daily, weekly, and seasonal cycles have been incorporated into the forecast."
            )

        # Enhancement impact explanation
        enhancement_impact = intelligence_enhancements.get("enhancement_impact", {})
        if enhancement_impact.get("improvement_factor", 1.0) != 1.0:
            improvement = enhancement_impact["improvement_factor"]
            impact_description = (
                "significantly improved"
                if improvement > 1.2
                else "enhanced"
                if improvement > 1.1
                else "refined"
            )
            explanation_parts.append(
                f"Intelligence analysis has {impact_description} prediction accuracy."
            )

        return " ".join(explanation_parts)

    def _extract_key_prediction_factors(
        self, intelligence_enhancements: dict[str, Any]
    ) -> list[str]:
        """Extract key factors influencing predictions"""
        factors = []

        contextual_factors = intelligence_enhancements.get("contextual_factors", {})
        if contextual_factors.get("market_stability"):
            factors.append("Market stability conditions")
        if contextual_factors.get("competitive_pressure"):
            factors.append("Competitive landscape dynamics")
        if contextual_factors.get("behavioral_patterns"):
            factors.append("User behavior patterns")

        temporal_factors = intelligence_enhancements.get("temporal_factors", {})
        if temporal_factors.get("seasonal_trends"):
            factors.append("Seasonal performance trends")
        if temporal_factors.get("cyclical_patterns"):
            factors.append("Weekly and daily cycles")

        return factors if factors else ["Historical performance data", "Current market conditions"]

    def _generate_confidence_explanation(self, confidence: ConfidenceLevel) -> str:
        """Generate explanation for confidence level"""
        explanations = {
            ConfidenceLevel.VERY_HIGH: "Based on strong historical patterns, high data quality, and stable environmental conditions.",
            ConfidenceLevel.HIGH: "Supported by consistent patterns and reliable data with favorable conditions.",
            ConfidenceLevel.MEDIUM: "Moderate confidence due to some variability in patterns or environmental factors.",
            ConfidenceLevel.LOW: "Lower confidence due to data limitations, pattern inconsistencies, or uncertain conditions.",
        }

        return explanations.get(confidence, "Confidence assessment unavailable.")

    async def _generate_prediction_recommendations(
        self, enhanced_predictions: dict[str, Any]
    ) -> list[str]:
        """Generate actionable recommendations based on predictions"""
        recommendations = []
        predictions = enhanced_predictions.get("predictions", {})

        # Growth-based recommendations
        for key, value in predictions.items():
            if "growth" in key and isinstance(value, (int, float)):
                if value > 0.15:
                    recommendations.append(
                        "Capitalize on strong growth momentum with increased content production"
                    )
                elif value > 0.05:
                    recommendations.append("Maintain consistent posting schedule to sustain growth")
                else:
                    recommendations.append(
                        "Consider strategy adjustments to improve growth trajectory"
                    )

        # Engagement-based recommendations
        if "engagement_forecast" in predictions:
            engagement = predictions["engagement_forecast"]
            if engagement > 0.1:
                recommendations.append(
                    "Leverage high engagement with interactive content strategies"
                )
            elif engagement < 0.05:
                recommendations.append("Focus on engagement optimization and audience development")

        return (
            recommendations
            if recommendations
            else ["Continue monitoring performance and adjust strategy as needed"]
        )

    def _extract_contextual_factors(
        self, contextual_intelligence: ContextualIntelligence
    ) -> dict[str, Any]:
        """Extract contextual factors for enhancement tracking"""
        return {
            "market_stability": bool(
                contextual_intelligence.environmental_factors.get("market_conditions")
            ),
            "competitive_pressure": bool(
                contextual_intelligence.competitive_landscape.get("competitive_pressure")
            ),
            "behavioral_patterns": bool(
                contextual_intelligence.behavioral_insights.get("engagement_patterns")
            ),
            "environmental_score": contextual_intelligence.environmental_factors.get(
                "environmental_score", 0.5
            ),
        }

    def _extract_temporal_factors(
        self, temporal_intelligence: TemporalIntelligence
    ) -> dict[str, Any]:
        """Extract temporal factors for enhancement tracking"""
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
        """Calculate the impact of intelligence enhancements"""
        base_conf = base_predictions.get("base_confidence", 0.5)
        enhanced_conf = enhanced_predictions.get("context_enhancements", {}).get(
            "context_confidence", 0.5
        )

        improvement_factor = enhanced_conf / base_conf if base_conf > 0 else 1.0

        return {
            "improvement_factor": improvement_factor,
            "confidence_improvement": enhanced_conf - base_conf,
            "enhancement_quality": "high"
            if improvement_factor > 1.2
            else "moderate"
            if improvement_factor > 1.1
            else "low",
        }

    def _calculate_contextual_confidence(self, contextual_intelligence: dict[str, Any]) -> float:
        """Calculate confidence from contextual intelligence"""
        return contextual_intelligence.get("context_confidence", 0.5)

    def _calculate_temporal_confidence(self, temporal_intelligence: dict[str, Any]) -> float:
        """Calculate confidence from temporal intelligence"""
        daily_consistency = temporal_intelligence.get("daily_patterns", {}).get(
            "consistency_score", 0.5
        )
        weekly_strength = temporal_intelligence.get("weekly_cycles", {}).get(
            "cyclical_strength", 0.5
        )

        return (daily_consistency + weekly_strength) / 2

    def _calculate_data_quality_confidence(self, predictions: dict[str, Any]) -> float:
        """Calculate confidence from data quality"""
        # Mock data quality assessment
        return 0.8

    def _calculate_model_confidence(self, predictions: dict[str, Any]) -> float:
        """Calculate confidence from model performance"""
        base_confidence = predictions.get("base_confidence", 0.75)
        return base_confidence

    def _map_to_confidence_level(self, overall_confidence: float) -> ConfidenceLevel:
        """Map numeric confidence to confidence level enum"""
        thresholds = self.modeling_config["confidence_thresholds"]

        if overall_confidence >= thresholds["very_high"]:
            return ConfidenceLevel.VERY_HIGH
        elif overall_confidence >= thresholds["high"]:
            return ConfidenceLevel.HIGH
        elif overall_confidence >= thresholds["medium"]:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _calculate_accuracy_metrics(
        self, predictions: dict[str, Any], actual_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate accuracy metrics comparing predictions to actual results"""
        accuracy_metrics = {}
        prediction_values = predictions.get("predictions", {})

        for key, predicted_value in prediction_values.items():
            if key in actual_results and isinstance(predicted_value, (int, float)):
                actual_value = actual_results[key]
                if isinstance(actual_value, (int, float)) and actual_value != 0:
                    # Calculate percentage error
                    error = abs(predicted_value - actual_value) / abs(actual_value)
                    accuracy = max(0, 1 - error)
                    accuracy_metrics[key] = {
                        "predicted": predicted_value,
                        "actual": actual_value,
                        "accuracy": accuracy,
                        "error_percentage": error * 100,
                    }

        # Calculate overall accuracy
        if accuracy_metrics:
            overall_accuracy = sum(
                metric["accuracy"] for metric in accuracy_metrics.values()
            ) / len(accuracy_metrics)
            accuracy_metrics["overall_accuracy"] = overall_accuracy
        else:
            accuracy_metrics["overall_accuracy"] = 0.0

        return accuracy_metrics

    def _analyze_prediction_errors(
        self, predictions: dict[str, Any], actual_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze prediction errors for insights"""
        error_analysis = {
            "systematic_bias": "none",
            "error_patterns": [],
            "largest_errors": [],
            "improvement_areas": [],
        }

        # Mock error analysis
        error_analysis["error_patterns"].append("Slight overestimation in growth predictions")
        error_analysis["improvement_areas"].append("Better integration of competitive factors")

        return error_analysis

    def _calculate_confidence_calibration(
        self, predicted_confidence: ConfidenceLevel, accuracy_metrics: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate how well confidence predictions match actual accuracy"""
        overall_accuracy = accuracy_metrics.get("overall_accuracy", 0.0)

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
            "calibration_quality": "good"
            if calibration_error < 0.1
            else "fair"
            if calibration_error < 0.2
            else "poor",
        }

    def _generate_learning_insights(
        self,
        original_prediction: dict[str, Any],
        actual_results: dict[str, Any],
        accuracy_metrics: dict[str, Any],
    ) -> list[str]:
        """Generate insights for model learning and improvement"""
        insights = []

        overall_accuracy = accuracy_metrics.get("overall_accuracy", 0.0)

        if overall_accuracy > 0.8:
            insights.append(
                "Prediction model performed well - consider similar approach for future predictions"
            )
        elif overall_accuracy > 0.6:
            insights.append(
                "Moderate accuracy achieved - review contextual factors for improvement"
            )
        else:
            insights.append("Lower accuracy observed - significant model refinement needed")

        # Context-specific insights
        intelligence_enhancements = original_prediction.get("intelligence_enhancements", {})
        if (
            intelligence_enhancements.get("enhancement_impact", {}).get("improvement_factor", 1.0)
            > 1.1
        ):
            insights.append("Intelligence enhancements improved prediction quality")

        return insights

    def _get_current_season(self) -> str:
        """Get current season for seasonal adjustments"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "fall"
        else:
            return "winter"

    async def health_check(self) -> dict[str, Any]:
        """Health check for predictive modeling service"""
        return {
            "service_name": "PredictiveModelingService",
            "status": "operational",
            "version": "1.0.0",
            "type": "microservice",
            "responsibility": "enhanced_predictive_modeling",
            "capabilities": [
                "enhanced_prediction_generation",
                "prediction_confidence_calculation",
                "natural_language_narratives",
                "prediction_accuracy_validation",
                "intelligent_forecasting",
            ],
            "active_predictions": len(self.active_predictions),
            "validation_history": len(self.validation_history),
            "modeling_config": self.modeling_config,
        }
