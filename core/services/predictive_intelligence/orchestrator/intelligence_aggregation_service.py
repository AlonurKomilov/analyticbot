"""
Intelligence Aggregation Service
================================

Responsible for aggregating and synthesizing intelligence from multiple services.

Single Responsibility:
- Aggregate intelligence from all predictive services
- Calculate confidence scores and weights
- Categorize intelligence data
- Generate intelligence summaries
- Extract key insights and recommendations
"""

import logging
from datetime import datetime
from typing import Any

from ..protocols.predictive_protocols import ConfidenceLevel

logger = logging.getLogger(__name__)


class IntelligenceAggregationService:
    """
    Intelligence aggregation microservice for synthesizing predictive intelligence.

    Single responsibility: Aggregate and synthesize intelligence from multiple sources.
    """

    def __init__(self, config_manager=None):
        """Initialize intelligence aggregation service"""
        self.config_manager = config_manager

        # Aggregation configuration
        self.aggregation_config = {
            "confidence_weighting": {
                "contextual": 0.25,
                "temporal": 0.30,
                "modeling": 0.35,
                "cross_channel": 0.10,
            },
            "minimum_service_threshold": 2,  # Minimum services for valid intelligence
            "quality_thresholds": {"high": 0.8, "medium": 0.6, "low": 0.4},
        }

    async def aggregate_predictive_intelligence(
        self, intelligence_results: dict[str, Any], request: dict[str, Any], context: str
    ) -> dict[str, Any]:
        """
        Aggregate intelligence from all services.

        Args:
            intelligence_results: Results from all services
            request: Original request information
            context: Intelligence context value

        Returns:
            Aggregated intelligence with summary, confidence, insights
        """

        aggregated = {
            "aggregation_metadata": {
                "request": request,
                "context": context,
                "services_included": [],
                "services_failed": [],
                "aggregation_timestamp": datetime.now().isoformat(),
            },
            "intelligence_summary": {},
            "confidence_analysis": {},
            "key_insights": [],
            "recommendations": [],
            "overall_confidence": 0.0,
        }

        # Process results from each service
        confidence_scores = []

        # Process contextual intelligence
        contextual_confidence = self._process_contextual_intelligence(
            intelligence_results, aggregated
        )
        if contextual_confidence is not None:
            confidence_scores.append(contextual_confidence)

        # Process temporal intelligence
        temporal_confidence = self._process_temporal_intelligence(intelligence_results, aggregated)
        if temporal_confidence is not None:
            confidence_scores.append(temporal_confidence)

        # Process predictive modeling
        modeling_confidence = self._process_modeling_intelligence(intelligence_results, aggregated)
        if modeling_confidence is not None:
            confidence_scores.append(modeling_confidence)

        # Process cross-channel analysis
        cross_channel_confidence = self._process_cross_channel_intelligence(
            intelligence_results, aggregated
        )
        if cross_channel_confidence is not None:
            confidence_scores.append(cross_channel_confidence)

        # Calculate overall confidence
        if confidence_scores:
            aggregated["overall_confidence"] = sum(confidence_scores) / len(confidence_scores)
        else:
            aggregated["overall_confidence"] = 0.0

        # Generate key insights
        aggregated["key_insights"] = self.generate_aggregated_insights(intelligence_results)

        # Generate recommendations
        aggregated["recommendations"] = self.generate_aggregated_recommendations(
            intelligence_results
        )

        return aggregated

    def _process_contextual_intelligence(
        self, intelligence_results: dict[str, Any], aggregated: dict[str, Any]
    ) -> float | None:
        """Process contextual intelligence results"""
        if "contextual" not in intelligence_results:
            return None

        contextual_result = intelligence_results["contextual"]
        if contextual_result.get("status") == "completed":
            aggregated["aggregation_metadata"]["services_included"].append("contextual")
            contextual_intel = contextual_result.get("contextual_intelligence")

            if contextual_intel:
                aggregated["intelligence_summary"]["contextual"] = {
                    "context_confidence": contextual_intel.context_confidence,
                    "environmental_factors_count": len(contextual_intel.environmental_factors),
                    "competitive_insights_count": len(contextual_intel.competitive_landscape),
                    "behavioral_insights_count": len(contextual_intel.behavioral_insights),
                }
                return contextual_intel.context_confidence
        else:
            aggregated["aggregation_metadata"]["services_failed"].append("contextual")

        return None

    def _process_temporal_intelligence(
        self, intelligence_results: dict[str, Any], aggregated: dict[str, Any]
    ) -> float | None:
        """Process temporal intelligence results"""
        if "temporal" not in intelligence_results:
            return None

        temporal_result = intelligence_results["temporal"]
        if temporal_result.get("status") == "completed":
            aggregated["aggregation_metadata"]["services_included"].append("temporal")
            temporal_intel = temporal_result.get("temporal_intelligence")

            if temporal_intel:
                aggregated["intelligence_summary"]["temporal"] = {
                    "daily_patterns_detected": len(temporal_intel.daily_patterns),
                    "weekly_cycles_detected": len(temporal_intel.weekly_cycles),
                    "seasonal_trends_count": len(temporal_intel.seasonal_trends),
                    "anomalies_detected": len(temporal_intel.temporal_anomalies),
                }
                # Calculate temporal confidence from patterns
                temporal_confidence = min(
                    1.0,
                    (len(temporal_intel.daily_patterns) + len(temporal_intel.weekly_cycles)) / 10.0,
                )
                return temporal_confidence
        else:
            aggregated["aggregation_metadata"]["services_failed"].append("temporal")

        return None

    def _process_modeling_intelligence(
        self, intelligence_results: dict[str, Any], aggregated: dict[str, Any]
    ) -> float | None:
        """Process predictive modeling results"""
        if "modeling" not in intelligence_results:
            return None

        modeling_result = intelligence_results["modeling"]
        if modeling_result.get("status") == "completed":
            aggregated["aggregation_metadata"]["services_included"].append("modeling")
            enhanced_predictions = modeling_result.get("enhanced_predictions", {})
            prediction_narrative = modeling_result.get("prediction_narrative")

            aggregated["intelligence_summary"]["modeling"] = {
                "predictions_generated": len(
                    enhanced_predictions.get("enhanced_predictions", {}).get("predictions", {})
                ),
                "confidence_level": enhanced_predictions.get(
                    "confidence_analysis", ConfidenceLevel.MEDIUM
                ).value,
                "narrative_available": prediction_narrative is not None,
            }

            # Extract confidence from modeling
            confidence_analysis = enhanced_predictions.get(
                "confidence_analysis", ConfidenceLevel.MEDIUM
            )
            confidence_mapping = {
                ConfidenceLevel.VERY_HIGH: 0.9,
                ConfidenceLevel.HIGH: 0.75,
                ConfidenceLevel.MEDIUM: 0.6,
                ConfidenceLevel.LOW: 0.45,
            }
            return confidence_mapping.get(confidence_analysis, 0.6)
        else:
            aggregated["aggregation_metadata"]["services_failed"].append("modeling")

        return None

    def _process_cross_channel_intelligence(
        self, intelligence_results: dict[str, Any], aggregated: dict[str, Any]
    ) -> float | None:
        """Process cross-channel analysis results"""
        if "cross_channel" not in intelligence_results:
            return None

        cross_channel_result = intelligence_results["cross_channel"]
        if cross_channel_result.get("status") == "completed":
            aggregated["aggregation_metadata"]["services_included"].append("cross_channel")
            cross_channel_intel = cross_channel_result.get("cross_channel_intelligence")

            if cross_channel_intel:
                aggregated["intelligence_summary"]["cross_channel"] = {
                    "correlations_found": len(cross_channel_intel.correlation_matrix),
                    "influence_relationships": len(cross_channel_intel.influence_relationships),
                    "integration_opportunities": len(cross_channel_intel.integration_opportunities),
                    "correlation_confidence": cross_channel_intel.correlation_confidence,
                }
                return cross_channel_intel.correlation_confidence
        else:
            aggregated["aggregation_metadata"]["services_failed"].append("cross_channel")

        return None

    def generate_aggregated_insights(self, intelligence_results: dict[str, Any]) -> list[str]:
        """
        Generate key insights from aggregated intelligence.

        Args:
            intelligence_results: Results from all services

        Returns:
            List of key insights
        """
        insights = []

        # From contextual analysis
        if "contextual" in intelligence_results:
            contextual_result = intelligence_results["contextual"]
            if contextual_result.get("status") == "completed":
                insights.append(
                    "Environmental and competitive factors analyzed for strategic context"
                )

        # From temporal intelligence
        if "temporal" in intelligence_results:
            temporal_result = intelligence_results["temporal"]
            if temporal_result.get("status") == "completed":
                insights.append(
                    "Temporal patterns and cyclical trends identified for timing optimization"
                )

        # From predictive modeling
        if "modeling" in intelligence_results:
            modeling_result = intelligence_results["modeling"]
            if modeling_result.get("status") == "completed":
                insights.append("Enhanced predictions generated with intelligence-driven modeling")

        # From cross-channel analysis
        if "cross_channel" in intelligence_results:
            cross_channel_result = intelligence_results["cross_channel"]
            if cross_channel_result.get("status") == "completed":
                insights.append("Cross-channel correlations and influence patterns mapped")

        return insights

    def generate_aggregated_recommendations(
        self, intelligence_results: dict[str, Any]
    ) -> list[str]:
        """
        Generate recommendations from aggregated intelligence.

        Args:
            intelligence_results: Results from all services

        Returns:
            List of strategic recommendations
        """
        recommendations = []

        successful_services = [
            name
            for name, result in intelligence_results.items()
            if result.get("status") == "completed"
        ]

        if len(successful_services) >= 3:
            recommendations.append(
                "Leverage comprehensive intelligence insights for strategic decision making"
            )
        elif len(successful_services) >= 2:
            recommendations.append(
                "Combine available intelligence sources for informed decision making"
            )
        else:
            recommendations.append(
                "Consider additional data sources to improve intelligence quality"
            )

        # Service-specific recommendations
        if "modeling" in successful_services:
            recommendations.append(
                "Implement predictive insights for proactive strategy adjustment"
            )

        if "cross_channel" in successful_services:
            recommendations.append("Explore cross-channel integration opportunities identified")

        return recommendations

    def categorize_intelligence_data(
        self, intelligence_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Categorize intelligence data by type.

        Args:
            intelligence_data: List of intelligence data items

        Returns:
            Categorized intelligence data
        """
        categories = {
            "contextual": [],
            "temporal": [],
            "predictive": [],
            "cross_channel": [],
            "uncategorized": [],
        }

        for data_item in intelligence_data:
            data_type = data_item.get("type", "unknown")

            if "contextual" in data_type.lower():
                categories["contextual"].append(data_item)
            elif "temporal" in data_type.lower():
                categories["temporal"].append(data_item)
            elif "predictive" in data_type.lower() or "prediction" in data_type.lower():
                categories["predictive"].append(data_item)
            elif "cross" in data_type.lower() or "channel" in data_type.lower():
                categories["cross_channel"].append(data_item)
            else:
                categories["uncategorized"].append(data_item)

        return categories

    def calculate_intelligence_scores(
        self, categorized_intelligence: dict[str, Any]
    ) -> dict[str, float]:
        """
        Calculate intelligence scores by category.

        Args:
            categorized_intelligence: Categorized intelligence data

        Returns:
            Intelligence scores by category
        """
        scores = {}
        weights = self.aggregation_config["confidence_weighting"]

        for category, weight in weights.items():
            category_data = categorized_intelligence.get(category, [])
            if category_data:
                # Calculate average score for category
                category_scores = [
                    item.get("confidence", 0.5) for item in category_data if "confidence" in item
                ]
                if category_scores:
                    scores[category] = sum(category_scores) / len(category_scores)
                else:
                    scores[category] = 0.5
            else:
                scores[category] = 0.0

        return scores

    def extract_key_insights(self, categorized_intelligence: dict[str, Any]) -> list[str]:
        """
        Extract key insights from categorized intelligence.

        Args:
            categorized_intelligence: Categorized intelligence data

        Returns:
            List of key insights
        """
        insights = []

        for category, data_items in categorized_intelligence.items():
            if data_items:
                insight_count = len(data_items)
                insights.append(
                    f"{category.title()} intelligence: {insight_count} insights available"
                )

        return insights

    def generate_intelligence_summary(
        self,
        categorized_intelligence: dict[str, Any],
        intelligence_scores: dict[str, float],
        key_insights: list[str],
    ) -> str:
        """
        Generate intelligence summary text.

        Args:
            categorized_intelligence: Categorized intelligence data
            intelligence_scores: Scores by category
            key_insights: List of key insights

        Returns:
            Intelligence summary text
        """
        summary_parts = []

        total_insights = sum(len(items) for items in categorized_intelligence.values())
        summary_parts.append(
            f"Aggregated {total_insights} intelligence insights across multiple dimensions"
        )

        # Highlight strongest categories
        sorted_scores = sorted(intelligence_scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_scores:
            strongest_category = sorted_scores[0][0]
            summary_parts.append(f"Strongest intelligence in {strongest_category} domain")

        return ". ".join(summary_parts) + "."

    def calculate_overall_confidence(self, intelligence_scores: dict[str, float]) -> float:
        """
        Calculate overall confidence from intelligence scores.

        Args:
            intelligence_scores: Scores by category

        Returns:
            Overall confidence score (0.0-1.0)
        """
        weights = self.aggregation_config["confidence_weighting"]

        weighted_sum = 0.0
        total_weight = 0.0

        for category, score in intelligence_scores.items():
            weight = weights.get(category, 0.25)
            weighted_sum += score * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def map_to_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """
        Map confidence score to confidence level.

        Args:
            confidence_score: Confidence score (0.0-1.0)

        Returns:
            ConfidenceLevel enum
        """
        thresholds = self.aggregation_config["quality_thresholds"]

        if confidence_score >= thresholds["high"]:
            return ConfidenceLevel.HIGH
        elif confidence_score >= thresholds["medium"]:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def assess_aggregation_quality(self, categorized_intelligence: dict[str, Any]) -> str:
        """
        Assess quality of intelligence aggregation.

        Args:
            categorized_intelligence: Categorized intelligence data

        Returns:
            Quality assessment (high/medium/low)
        """
        categories_with_data = sum(1 for items in categorized_intelligence.values() if items)
        total_categories = len(categorized_intelligence)

        coverage_ratio = categories_with_data / total_categories

        if coverage_ratio >= 0.75:
            return "high"
        elif coverage_ratio >= 0.5:
            return "medium"
        else:
            return "low"

    def create_analysis_summary(self, aggregated_intelligence: dict[str, Any]) -> str:
        """
        Create analysis summary text.

        Args:
            aggregated_intelligence: Aggregated intelligence results

        Returns:
            Analysis summary text
        """
        services_count = len(aggregated_intelligence["aggregation_metadata"]["services_included"])
        confidence = aggregated_intelligence["overall_confidence"]

        return f"Comprehensive predictive intelligence analysis completed using {services_count} intelligence services with {confidence:.1%} overall confidence."

    def create_confidence_breakdown(
        self, aggregated_intelligence: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create confidence breakdown by service.

        Args:
            aggregated_intelligence: Aggregated intelligence results

        Returns:
            Confidence breakdown by service
        """
        breakdown = {"overall": aggregated_intelligence["overall_confidence"], "by_service": {}}

        summary = aggregated_intelligence.get("intelligence_summary", {})

        # Extract confidence from each service
        if "contextual" in summary:
            breakdown["by_service"]["contextual"] = summary["contextual"].get(
                "context_confidence", 0.0
            )
        if "cross_channel" in summary:
            breakdown["by_service"]["cross_channel"] = summary["cross_channel"].get(
                "correlation_confidence", 0.0
            )

        return breakdown
