"""
Template Manager Service - NLG Templates and Patterns

Manages narrative templates, metric descriptions, and recommendation patterns
for the Natural Language Generation system.

Part of NLG Service Refactoring (Priority #2)
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class InsightType(Enum):
    """Types of insights that can be narrated"""

    TREND = "trend"
    ANOMALY = "anomaly"
    COMPARISON = "comparison"
    FORECAST = "forecast"
    PERFORMANCE = "performance"
    AUDIENCE = "audience"
    ENGAGEMENT = "engagement"
    GROWTH = "growth"


class NarrativeStyle(Enum):
    """Different narrative styles for different audiences"""

    EXECUTIVE = "executive"  # Brief, business-focused
    ANALYTICAL = "analytical"  # Detailed, technical
    CONVERSATIONAL = "conversational"  # Casual, easy to understand
    TECHNICAL = "technical"  # Deep, data-focused


class TemplateManager:
    """
    📝 Template Manager Service

    Single Responsibility: Manage all NLG templates, patterns, and descriptions

    Responsibilities:
    - Initialize and store narrative templates
    - Manage metric descriptions
    - Provide recommendation patterns
    - Template retrieval and validation
    """

    def __init__(self):
        self._narrative_templates = self._initialize_narrative_templates()
        self._metric_descriptions = self._initialize_metric_descriptions()
        self._recommendation_patterns = self._initialize_recommendation_patterns()
        logger.info("TemplateManager initialized with templates loaded")

    def get_narrative_template(self, insight_type: InsightType, style: NarrativeStyle) -> str:
        """
        Get narrative template for specific insight type and style

        Args:
            insight_type: Type of insight
            style: Narrative style

        Returns:
            Template string with placeholders
        """
        try:
            templates = self._narrative_templates.get(insight_type.value, {})
            template = templates.get(style.value)

            if template:
                return template

            # Fallback to conversational style if not found
            return templates.get(
                NarrativeStyle.CONVERSATIONAL.value, "Your {metric} shows {status}."
            )

        except Exception as e:
            logger.error(f"Template retrieval failed: {e}")
            return "Analytics data analysis complete for {metric}."

    def get_metric_description(self, metric: str) -> str:
        """
        Get human-readable description for a metric

        Args:
            metric: Technical metric name

        Returns:
            Human-readable metric description
        """
        return self._metric_descriptions.get(metric, metric)

    def get_recommendation_patterns(self, scenario: str) -> list[str]:
        """
        Get recommendation patterns for a specific scenario

        Args:
            scenario: Scenario key (e.g., 'high_engagement', 'declining_trend')

        Returns:
            List of recommendation templates
        """
        patterns = self._recommendation_patterns.get(scenario, [])

        if not patterns:
            logger.warning(f"No recommendation patterns found for scenario: {scenario}")
            return ["Monitor metrics and adjust strategy as needed"]

        return patterns

    def get_all_templates(self) -> dict[str, dict[str, str]]:
        """Get all narrative templates"""
        return self._narrative_templates.copy()

    def get_all_metric_descriptions(self) -> dict[str, str]:
        """Get all metric descriptions"""
        return self._metric_descriptions.copy()

    def get_all_recommendation_patterns(self) -> dict[str, list[str]]:
        """Get all recommendation patterns"""
        return self._recommendation_patterns.copy()

    def _initialize_narrative_templates(self) -> dict[str, dict[str, str]]:
        """Initialize narrative templates for different insight types and styles"""
        return {
            InsightType.TREND.value: {
                NarrativeStyle.EXECUTIVE.value: "Your {metric} shows a {direction} trend of {magnitude}% over {period}.",
                NarrativeStyle.CONVERSATIONAL.value: "Good news! Your {metric} has been {direction} by {magnitude}% over the past {period}.",
                NarrativeStyle.ANALYTICAL.value: "{metric} demonstrates {direction} pattern with {strength} consistency over {period}.",
                NarrativeStyle.TECHNICAL.value: "{metric} demonstrates {direction} trajectory with {strength} trend strength (p<{p_value}).",
            },
            InsightType.ANOMALY.value: {
                NarrativeStyle.EXECUTIVE.value: "{severity} anomaly detected in {metric} ({change}% deviation).",
                NarrativeStyle.CONVERSATIONAL.value: "Something interesting happened with your {metric} - it {direction} by {change}%.",
                NarrativeStyle.ANALYTICAL.value: "{metric} anomaly identified: {change}% deviation from baseline with {severity} severity level.",
                NarrativeStyle.TECHNICAL.value: "Statistical anomaly: {metric} outside {sigma}σ bounds, z-score: {z_score}.",
            },
            InsightType.PERFORMANCE.value: {
                NarrativeStyle.EXECUTIVE.value: "Performance {status}: {metric} at {level}% of target.",
                NarrativeStyle.CONVERSATIONAL.value: "Your {metric} is performing {status} - currently at {level}% of your goal.",
                NarrativeStyle.ANALYTICAL.value: "{metric} performance assessment: {status} status with {level}% achievement rate.",
                NarrativeStyle.TECHNICAL.value: "Performance metrics: {metric} = {value}, benchmark = {benchmark}, ratio = {ratio}.",
            },
            InsightType.GROWTH.value: {
                NarrativeStyle.EXECUTIVE.value: "{metric} growth: {rate}% over {period}.",
                NarrativeStyle.CONVERSATIONAL.value: "Your {metric} has grown by {rate}% - that's {status} progress!",
                NarrativeStyle.ANALYTICAL.value: "{metric} growth analysis: {rate}% rate over {period} with {trajectory} trajectory.",
                NarrativeStyle.TECHNICAL.value: "Growth rate: {rate}%, CAGR: {cagr}%, trend: {trend_type}.",
            },
            InsightType.ENGAGEMENT.value: {
                NarrativeStyle.EXECUTIVE.value: "Engagement: {rate}% ({status}).",
                NarrativeStyle.CONVERSATIONAL.value: "Your audience is {engagement_level} engaged with {rate}% interaction rate.",
                NarrativeStyle.ANALYTICAL.value: "Engagement metrics: {rate}% rate, {interactions} interactions, {status} level.",
                NarrativeStyle.TECHNICAL.value: "Engagement rate: {rate}%, z-score: {z_score}, percentile: {percentile}.",
            },
            InsightType.AUDIENCE.value: {
                NarrativeStyle.EXECUTIVE.value: "Audience: {size} ({growth}% growth).",
                NarrativeStyle.CONVERSATIONAL.value: "Your audience has reached {size} people, growing by {growth}%!",
                NarrativeStyle.ANALYTICAL.value: "Audience analysis: {size} total, {growth}% growth, {retention}% retention.",
                NarrativeStyle.TECHNICAL.value: "Audience size: {size}, growth: {growth}%, churn: {churn}%, DAU/MAU: {ratio}.",
            },
            InsightType.COMPARISON.value: {
                NarrativeStyle.EXECUTIVE.value: "{metric}: {value} vs benchmark {benchmark} ({difference}%).",
                NarrativeStyle.CONVERSATIONAL.value: "Your {metric} is {comparison} the benchmark by {difference}%.",
                NarrativeStyle.ANALYTICAL.value: "{metric} comparison: current {value}, benchmark {benchmark}, variance {difference}%.",
                NarrativeStyle.TECHNICAL.value: "{metric}: observed={value}, expected={benchmark}, delta={difference}%, p={p_value}.",
            },
            InsightType.FORECAST.value: {
                NarrativeStyle.EXECUTIVE.value: "{metric} forecast: {predicted_value} ({confidence}% confidence).",
                NarrativeStyle.CONVERSATIONAL.value: "We predict your {metric} will reach {predicted_value} with {confidence}% confidence.",
                NarrativeStyle.ANALYTICAL.value: "{metric} forecast: {predicted_value} (range: {lower_bound}-{upper_bound}, {confidence}% CI).",
                NarrativeStyle.TECHNICAL.value: "Forecast: {predicted_value}, CI: [{lower_bound}, {upper_bound}], MAPE: {mape}%.",
            },
        }

    def _initialize_metric_descriptions(self) -> dict[str, str]:
        """Initialize human-readable descriptions for metrics"""
        return {
            "views": "content views",
            "engagement": "audience engagement",
            "followers": "follower count",
            "growth": "growth rate",
            "reach": "content reach",
            "err": "engagement rate",
            "forwards": "content shares",
            "replies": "audience responses",
            "reactions": "content reactions",
            "mentions": "channel mentions",
            "avg_views": "average views per post",
            "total_views": "total content views",
            "unique_viewers": "unique audience members",
            "retention": "audience retention",
            "churn": "audience churn rate",
            "active_users": "active users",
            "impressions": "content impressions",
            "clicks": "content clicks",
            "ctr": "click-through rate",
            "conversion": "conversion rate",
        }

    def _initialize_recommendation_patterns(self) -> dict[str, list[str]]:
        """Initialize recommendation patterns for different scenarios"""
        return {
            "high_engagement": [
                "Continue your current content strategy - it's working well",
                "Consider increasing posting frequency to capitalize on momentum",
                "Replicate successful content patterns across more posts",
                "Document what's working for future reference",
            ],
            "low_engagement": [
                "Review content timing and format for optimization opportunities",
                "Analyze successful competitor strategies for insights",
                "Consider audience engagement tactics like polls or questions",
                "Test different content types to identify what resonates",
                "Review audience demographics for content-market fit",
            ],
            "growing_trend": [
                "Capitalize on positive momentum with consistent posting",
                "Scale successful content types and topics",
                "Monitor trend sustainability with key metrics",
                "Consider expanding to related content areas",
                "Document growth drivers for replication",
            ],
            "declining_trend": [
                "Investigate root causes of decline immediately",
                "Implement recovery strategies based on data analysis",
                "Review content-market fit and audience preferences",
                "Consider A/B testing new content approaches",
                "Engage directly with audience for feedback",
            ],
            "anomaly_detected": [
                "Investigate unusual patterns to understand root causes",
                "Monitor closely for continued deviations",
                "Review recent content or strategy changes",
                "Consider external factors that may be influencing metrics",
            ],
            "stable_performance": [
                "Maintain current strategy while exploring optimization",
                "Test incremental improvements to key metrics",
                "Monitor for early signs of change",
                "Plan strategic initiatives for growth",
            ],
            "high_growth": [
                "Scale infrastructure to support continued growth",
                "Maintain content quality during expansion",
                "Monitor key quality metrics during growth phase",
                "Document success factors for sustainable growth",
            ],
            "negative_growth": [
                "Conduct urgent analysis of churn factors",
                "Implement retention-focused strategies",
                "Review competitive landscape for threats",
                "Consider audience feedback and sentiment",
                "Plan content refresh or pivot if needed",
            ],
        }

    async def health_check(self) -> dict[str, Any]:
        """Health check for template manager"""
        return {
            "service": "TemplateManager",
            "status": "healthy",
            "templates_loaded": len(self._narrative_templates),
            "metric_descriptions": len(self._metric_descriptions),
            "recommendation_patterns": len(self._recommendation_patterns),
            "insight_types_supported": len(InsightType),
            "narrative_styles_supported": len(NarrativeStyle),
        }
