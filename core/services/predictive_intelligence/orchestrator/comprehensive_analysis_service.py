"""
Comprehensive Analysis Service
==============================

Responsible for generating comprehensive analysis reports and strategic insights.

Single Responsibility:
- Generate comprehensive analysis reports
- Create predictive outlooks
- Generate strategic recommendations
- Assess risks and identify opportunities
- Create next steps and action plans
"""

import logging
from typing import Any

from ..protocols.predictive_protocols import ConfidenceLevel

logger = logging.getLogger(__name__)


class ComprehensiveAnalysisService:
    """
    Comprehensive analysis microservice for generating strategic intelligence reports.

    Single responsibility: Generate comprehensive analysis reports and insights.
    """

    def __init__(self, config_manager=None):
        """Initialize comprehensive analysis service"""
        self.config_manager = config_manager

    async def generate_comprehensive_analysis(
        self,
        aggregated_intelligence: dict[str, Any],
        intelligence_results: dict[str, Any],
        request: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate comprehensive predictive analysis.

        Args:
            aggregated_intelligence: Aggregated intelligence data
            intelligence_results: Raw intelligence results from services
            request: Original analysis request

        Returns:
            Comprehensive analysis report
        """

        analysis = {
            "analysis_summary": self.create_analysis_summary(aggregated_intelligence),
            "predictive_outlook": self.create_predictive_outlook(intelligence_results),
            "strategic_recommendations": self.create_strategic_recommendations(
                aggregated_intelligence
            ),
            "risk_assessment": self.create_risk_assessment(intelligence_results),
            "opportunity_identification": self.create_opportunity_identification(
                intelligence_results
            ),
            "confidence_breakdown": self.create_confidence_breakdown(aggregated_intelligence),
            "next_steps": self.create_next_steps(aggregated_intelligence, request),
        }

        return analysis

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

    def create_predictive_outlook(self, intelligence_results: dict[str, Any]) -> str:
        """
        Create predictive outlook text.

        Args:
            intelligence_results: Results from all services

        Returns:
            Predictive outlook text
        """
        if (
            "modeling" in intelligence_results
            and intelligence_results["modeling"].get("status") == "completed"
        ):
            return "Enhanced predictions generated with contextual and temporal intelligence integration."
        else:
            return "Predictive modeling data not available for comprehensive outlook."

    def create_strategic_recommendations(
        self, aggregated_intelligence: dict[str, Any]
    ) -> list[str]:
        """
        Create strategic recommendations.

        Args:
            aggregated_intelligence: Aggregated intelligence results

        Returns:
            List of strategic recommendations
        """
        recommendations = aggregated_intelligence.get("recommendations", [])
        return (
            recommendations
            if recommendations
            else ["Monitor intelligence quality and expand data sources"]
        )

    def create_risk_assessment(self, intelligence_results: dict[str, Any]) -> str:
        """
        Create risk assessment text.

        Args:
            intelligence_results: Results from all services

        Returns:
            Risk assessment text
        """
        failed_services = sum(
            1 for result in intelligence_results.values() if result.get("status") == "failed"
        )

        if failed_services == 0:
            return "Low risk - all intelligence services operational"
        elif failed_services <= 2:
            return "Medium risk - some intelligence services unavailable"
        else:
            return "High risk - multiple intelligence services failed"

    def create_opportunity_identification(self, intelligence_results: dict[str, Any]) -> list[str]:
        """
        Create opportunity identification.

        Args:
            intelligence_results: Results from all services

        Returns:
            List of identified opportunities
        """
        opportunities = []

        if "cross_channel" in intelligence_results:
            result = intelligence_results["cross_channel"]
            if result.get("status") == "completed":
                cross_channel_intel = result.get("cross_channel_intelligence")
                if cross_channel_intel and hasattr(
                    cross_channel_intel, "integration_opportunities"
                ):
                    if cross_channel_intel.integration_opportunities:
                        opportunities.extend(
                            [
                                f"Integration opportunity: {opp.get('type', 'unknown')}"
                                for opp in cross_channel_intel.integration_opportunities[:3]
                            ]
                        )

        # Add temporal opportunities
        if "temporal" in intelligence_results:
            result = intelligence_results["temporal"]
            if result.get("status") == "completed":
                temporal_intel = result.get("temporal_intelligence")
                if temporal_intel and hasattr(temporal_intel, "optimal_timing_windows"):
                    if temporal_intel.optimal_timing_windows:
                        opportunities.append(
                            "Optimal timing windows identified for strategic actions"
                        )

        # Add modeling opportunities
        if "modeling" in intelligence_results:
            result = intelligence_results["modeling"]
            if result.get("status") == "completed":
                enhanced_predictions = result.get("enhanced_predictions", {})
                if enhanced_predictions.get("status") != "not_implemented":
                    opportunities.append(
                        "Predictive insights available for proactive decision-making"
                    )

        return opportunities if opportunities else ["Explore cross-channel synergies"]

    def create_confidence_breakdown(
        self, aggregated_intelligence: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create confidence breakdown by service.

        Args:
            aggregated_intelligence: Aggregated intelligence results

        Returns:
            Confidence breakdown dictionary
        """
        overall_confidence = aggregated_intelligence["overall_confidence"]

        # Map confidence to level
        if overall_confidence >= 0.8:
            confidence_level = ConfidenceLevel.VERY_HIGH
        elif overall_confidence >= 0.7:
            confidence_level = ConfidenceLevel.HIGH
        elif overall_confidence >= 0.5:
            confidence_level = ConfidenceLevel.MEDIUM
        else:
            confidence_level = ConfidenceLevel.LOW

        return {
            "overall_confidence": overall_confidence,
            "confidence_level": confidence_level.value,
            "services_contributing": len(
                aggregated_intelligence["aggregation_metadata"]["services_included"]
            ),
            "quality_assessment": (
                "high"
                if overall_confidence > 0.7
                else "medium"
                if overall_confidence > 0.5
                else "low"
            ),
        }

    def create_next_steps(
        self, aggregated_intelligence: dict[str, Any], request: dict[str, Any]
    ) -> list[str]:
        """
        Create next steps recommendations.

        Args:
            aggregated_intelligence: Aggregated intelligence results
            request: Original analysis request

        Returns:
            List of recommended next steps
        """
        next_steps = []

        confidence = aggregated_intelligence["overall_confidence"]

        if confidence > 0.7:
            next_steps.append("Implement intelligence insights in strategic planning")
            next_steps.append("Execute high-confidence recommendations immediately")
        elif confidence > 0.5:
            next_steps.append("Validate insights with additional data sources")
            next_steps.append("Implement medium-confidence recommendations with monitoring")
        else:
            next_steps.append("Improve data quality and intelligence service coverage")
            next_steps.append("Defer major decisions until intelligence quality improves")

        next_steps.append("Schedule regular intelligence updates")
        next_steps.append("Monitor prediction accuracy for model improvement")

        # Add service-specific recommendations
        services_included = aggregated_intelligence["aggregation_metadata"]["services_included"]
        if "cross_channel" in services_included:
            next_steps.append("Explore cross-channel integration opportunities")
        if "temporal" in services_included:
            next_steps.append("Leverage timing insights for optimal execution")

        return next_steps

    def create_executive_summary(
        self,
        aggregated_intelligence: dict[str, Any],
        intelligence_results: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Create executive summary for leadership.

        Args:
            aggregated_intelligence: Aggregated intelligence results
            intelligence_results: Raw intelligence results

        Returns:
            Executive summary dictionary
        """
        services_count = len(aggregated_intelligence["aggregation_metadata"]["services_included"])
        confidence = aggregated_intelligence["overall_confidence"]

        # Count insights
        total_insights = len(aggregated_intelligence.get("key_insights", []))
        recommendations_count = len(aggregated_intelligence.get("recommendations", []))

        # Determine overall status
        if confidence >= 0.7 and services_count >= 3:
            status = "excellent"
        elif confidence >= 0.5 and services_count >= 2:
            status = "good"
        else:
            status = "needs_improvement"

        return {
            "status": status,
            "services_analyzed": services_count,
            "overall_confidence": confidence,
            "total_insights": total_insights,
            "total_recommendations": recommendations_count,
            "risk_level": self._determine_risk_level(intelligence_results),
            "priority_actions": self._determine_priority_actions(aggregated_intelligence),
            "summary_text": self._create_executive_summary_text(
                services_count, confidence, total_insights, status
            ),
        }

    def _determine_risk_level(self, intelligence_results: dict[str, Any]) -> str:
        """Determine overall risk level"""
        failed_services = sum(
            1 for result in intelligence_results.values() if result.get("status") == "failed"
        )

        if failed_services == 0:
            return "low"
        elif failed_services <= 2:
            return "medium"
        else:
            return "high"

    def _determine_priority_actions(self, aggregated_intelligence: dict[str, Any]) -> list[str]:
        """Determine priority actions from intelligence"""
        priority_actions = []

        confidence = aggregated_intelligence["overall_confidence"]
        recommendations = aggregated_intelligence.get("recommendations", [])

        if confidence > 0.7:
            # High confidence: focus on execution
            priority_actions.append("Execute high-confidence recommendations")
            if recommendations:
                priority_actions.append(f"Implement: {recommendations[0]}")
        else:
            # Lower confidence: focus on improvement
            priority_actions.append("Improve intelligence data quality")
            priority_actions.append("Expand intelligence service coverage")

        return priority_actions[:3]  # Top 3 priority actions

    def _create_executive_summary_text(
        self, services_count: int, confidence: float, insights_count: int, status: str
    ) -> str:
        """Create executive summary text"""
        return (
            f"Predictive intelligence analysis completed with {status} results. "
            f"Analyzed {services_count} intelligence services producing {insights_count} insights "
            f"with {confidence:.0%} overall confidence. "
            f"Ready for {'immediate action' if confidence > 0.7 else 'validation and review'}."
        )
