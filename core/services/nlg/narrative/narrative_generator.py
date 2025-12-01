"""
Narrative Generator Service - Core NLG Logic

Generates narratives, titles, recommendations, and assessments
for analytics insights.

Part of NLG Service Refactoring (Priority #2)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ..formatting.content_formatter import ContentFormatter
from ..templates.template_manager import InsightType, NarrativeStyle, TemplateManager

logger = logging.getLogger(__name__)


@dataclass
class InsightNarrative:
    """Structure for a single insight narrative"""

    insight_type: InsightType
    title: str
    narrative: str
    confidence: float
    key_metrics: dict[str, Any]
    recommendations: list[str]
    severity: str  # low, medium, high, critical
    generated_at: datetime


class NarrativeGenerator:
    """
    📝 Narrative Generator Service

    Single Responsibility: Generate narratives and insights

    Responsibilities:
    - Generate insight narratives from analytics data
    - Create titles for insights
    - Calculate confidence scores
    - Generate recommendations
    - Determine severity levels
    - Extract key metrics from analytics data
    """

    def __init__(
        self,
        template_manager: TemplateManager | None = None,
        formatter: ContentFormatter | None = None,
    ):
        self.template_manager = template_manager or TemplateManager()
        self.formatter = formatter or ContentFormatter()
        logger.info("NarrativeGenerator initialized")

    async def generate_insight_narrative(
        self,
        analytics_data: dict,
        insight_type: InsightType,
        style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL,
        channel_context: dict | None = None,
    ) -> InsightNarrative:
        """
        🎯 Generate Natural Language Insight from Analytics Data

        Args:
            analytics_data: Raw analytics data from services
            insight_type: Type of insight to generate
            style: Narrative style for target audience
            channel_context: Additional context about the channel

        Returns:
            InsightNarrative with human-readable explanations
        """
        try:
            # Extract key metrics based on insight type
            key_metrics = self._extract_key_metrics(analytics_data, insight_type)

            # Generate narrative based on type and style
            narrative = await self._generate_narrative(
                analytics_data, insight_type, style, key_metrics, channel_context
            )

            # Generate title
            title = self._generate_title(insight_type, key_metrics, style)

            # Calculate confidence score
            confidence = self._calculate_narrative_confidence(analytics_data, insight_type)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                analytics_data, insight_type, key_metrics
            )

            # Determine severity
            severity = self._determine_severity(key_metrics, insight_type)

            return InsightNarrative(
                insight_type=insight_type,
                title=title,
                narrative=narrative,
                confidence=confidence,
                key_metrics=key_metrics,
                recommendations=recommendations,
                severity=severity,
                generated_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f"NLG insight generation failed: {e}")
            return self._generate_fallback_narrative(insight_type, analytics_data)

    async def _generate_narrative(
        self,
        analytics_data: dict,
        insight_type: InsightType,
        style: NarrativeStyle,
        key_metrics: dict,
        channel_context: dict | None,
    ) -> str:
        """Generate the main narrative text"""
        try:
            # Get template for this insight type and style
            template = self.template_manager.get_narrative_template(insight_type, style)

            # Prepare metrics for formatting
            formatted_metrics = self._format_metrics_for_template(key_metrics)

            # Format template with metrics
            try:
                narrative = template.format(**formatted_metrics)
            except KeyError as e:
                logger.warning(f"Template formatting failed: {e}, using fallback")
                metric = key_metrics.get("metric", "metric")
                narrative = f"Analytics insights available for {metric}."

            # Add context if available
            if channel_context and channel_context.get("name"):
                narrative = f"For {channel_context['name']}: {narrative}"

            # Add confidence qualifier if needed
            confidence = key_metrics.get("confidence", 0.7)
            if confidence < 0.6:
                narrative += " (preliminary analysis)"
            elif confidence > 0.9:
                narrative += " (high confidence)"

            # Clean the narrative
            return self.formatter.clean_narrative(narrative)

        except Exception as e:
            logger.error(f"Narrative generation failed: {e}")
            metric = key_metrics.get("metric", "your channel")
            return f"Analytics insights available for {metric}."

    def _generate_title(
        self, insight_type: InsightType, key_metrics: dict, style: NarrativeStyle
    ) -> str:
        """Generate appropriate title for the insight"""
        try:
            metric = key_metrics.get("metric", "Analytics")
            metric_desc = self.template_manager.get_metric_description(metric)

            if insight_type == InsightType.TREND:
                direction = key_metrics.get("direction", "stable")
                if direction in ["increasing", "growing", "up"]:
                    return f"📈 {metric_desc.title()} Growing Steadily"
                elif direction in ["decreasing", "declining", "down"]:
                    return f"📉 {metric_desc.title()} Needs Attention"
                else:
                    return f"📊 {metric_desc.title()} Remains Stable"

            elif insight_type == InsightType.ANOMALY:
                severity = key_metrics.get("severity", "moderate")
                if severity in ["high", "critical"]:
                    return f"🚨 Significant {metric_desc.title()} Change Detected"
                else:
                    return f"🔍 Unusual {metric_desc.title()} Pattern"

            elif insight_type == InsightType.PERFORMANCE:
                score = key_metrics.get("performance_score", 0.5)
                if score > 0.8:
                    return f"🎯 Excellent {metric_desc.title()} Performance"
                elif score > 0.6:
                    return f"✅ Good {metric_desc.title()} Performance"
                else:
                    return f"⚠️ {metric_desc.title()} Below Expectations"

            elif insight_type == InsightType.GROWTH:
                rate = key_metrics.get("rate", 0)
                if rate > 10:
                    return f"🚀 Rapid {metric_desc.title()} Growth"
                elif rate > 0:
                    return f"📈 Positive {metric_desc.title()} Growth"
                else:
                    return f"📉 {metric_desc.title()} Decline"

            elif insight_type == InsightType.ENGAGEMENT:
                rate = key_metrics.get("rate", 0)
                if rate > 10:
                    return f"⭐ Exceptional {metric_desc.title()} Engagement"
                elif rate > 5:
                    return f"✅ Strong {metric_desc.title()} Engagement"
                else:
                    return f"💡 {metric_desc.title()} Engagement Insights"

            else:
                return f"📊 {metric_desc.title()} Insights"

        except Exception as e:
            logger.error(f"Title generation failed: {e}")
            return "📊 Analytics Insights"

    def _calculate_narrative_confidence(
        self, analytics_data: dict, insight_type: InsightType
    ) -> float:
        """Calculate confidence score for the narrative"""
        try:
            base_confidence = analytics_data.get("confidence", 0.7)

            # Adjust based on data quality
            data_points = analytics_data.get("data_points", 10)
            if data_points < 5:
                base_confidence *= 0.8
            elif data_points > 30:
                base_confidence = min(1.0, base_confidence * 1.1)

            # Adjust based on insight type
            if insight_type == InsightType.ANOMALY:
                significance = analytics_data.get("statistical_significance", 0.05)
                if significance < 0.01:
                    base_confidence = min(1.0, base_confidence * 1.2)
                elif significance > 0.1:
                    base_confidence *= 0.9

            elif insight_type == InsightType.FORECAST:
                # Forecasts inherently have more uncertainty
                base_confidence *= 0.9

            return round(min(1.0, max(0.0, base_confidence)), 3)

        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5

    def _generate_recommendations(
        self, analytics_data: dict, insight_type: InsightType, key_metrics: dict
    ) -> list[str]:
        """Generate actionable recommendations"""
        try:
            recommendations = []

            if insight_type == InsightType.TREND:
                direction = key_metrics.get("direction", "stable")
                if direction in ["increasing", "growing"]:
                    patterns = self.template_manager.get_recommendation_patterns("growing_trend")
                    recommendations.extend(patterns)
                elif direction in ["decreasing", "declining"]:
                    patterns = self.template_manager.get_recommendation_patterns("declining_trend")
                    recommendations.extend(patterns)
                else:
                    patterns = self.template_manager.get_recommendation_patterns(
                        "stable_performance"
                    )
                    recommendations.extend(patterns)

            elif insight_type == InsightType.PERFORMANCE:
                score = key_metrics.get("performance_score", 0.5)
                if score > 0.7:
                    patterns = self.template_manager.get_recommendation_patterns("high_engagement")
                    recommendations.extend(patterns)
                else:
                    patterns = self.template_manager.get_recommendation_patterns("low_engagement")
                    recommendations.extend(patterns)

            elif insight_type == InsightType.ANOMALY:
                severity = key_metrics.get("severity", "moderate")
                patterns = self.template_manager.get_recommendation_patterns("anomaly_detected")
                recommendations.extend(patterns)

                if severity in ["high", "critical"]:
                    recommendations.insert(0, "Investigate root cause immediately")
                    recommendations.insert(1, "Review recent content or strategy changes")

            elif insight_type == InsightType.GROWTH:
                rate = key_metrics.get("rate", 0)
                if rate > 10:
                    patterns = self.template_manager.get_recommendation_patterns("high_growth")
                    recommendations.extend(patterns)
                elif rate < 0:
                    patterns = self.template_manager.get_recommendation_patterns("negative_growth")
                    recommendations.extend(patterns)
                else:
                    patterns = self.template_manager.get_recommendation_patterns("growing_trend")
                    recommendations.extend(patterns)

            else:
                recommendations.append("Review analytics data for optimization opportunities")
                recommendations.append("Monitor key metrics regularly")

            # Limit to top 3-5 recommendations
            return recommendations[:5]

        except Exception as e:
            logger.error(f"Recommendations generation failed: {e}")
            return ["Review analytics data for optimization opportunities"]

    def _determine_severity(self, key_metrics: dict, insight_type: InsightType) -> str:
        """Determine severity level of the insight"""
        try:
            # Check for explicit severity
            if "severity" in key_metrics:
                return key_metrics["severity"]

            # Determine based on insight type and metrics
            if insight_type == InsightType.ANOMALY:
                deviation = abs(key_metrics.get("deviation", 0))
                if deviation > 50:
                    return "critical"
                elif deviation > 30:
                    return "high"
                elif deviation > 15:
                    return "medium"
                else:
                    return "low"

            elif insight_type == InsightType.TREND:
                direction = key_metrics.get("direction", "stable")
                strength = key_metrics.get("strength", 0.5)

                if direction in ["decreasing", "declining"] and strength > 0.7:
                    return "high"
                elif direction in ["increasing", "growing"] and strength > 0.8:
                    return "low"  # Good news, low severity
                else:
                    return "medium"

            elif insight_type == InsightType.PERFORMANCE:
                score = key_metrics.get("performance_score", 0.5)
                if score < 0.3:
                    return "high"
                elif score < 0.6:
                    return "medium"
                else:
                    return "low"

            else:
                return "medium"

        except Exception as e:
            logger.error(f"Severity determination failed: {e}")
            return "medium"

    def _extract_key_metrics(
        self, analytics_data: dict, insight_type: InsightType
    ) -> dict[str, Any]:
        """Extract relevant metrics based on insight type"""
        try:
            key_metrics = {}

            if insight_type == InsightType.TREND:
                key_metrics.update(
                    {
                        "direction": analytics_data.get("trend_direction", "stable"),
                        "strength": analytics_data.get("trend_strength", 0.0),
                        "metric": analytics_data.get("metric", "engagement"),
                        "period": analytics_data.get("period_days", 30),
                        "magnitude": analytics_data.get("change_percent", 0),
                    }
                )

            elif insight_type == InsightType.PERFORMANCE:
                current = analytics_data.get("current_value", 0)
                baseline = analytics_data.get("baseline_value", 0)

                key_metrics.update(
                    {
                        "current_value": current,
                        "baseline_value": baseline,
                        "metric": analytics_data.get("metric", "views"),
                        "performance_score": analytics_data.get("performance_score", 0.5),
                        "value": current,
                        "benchmark": baseline,
                        "ratio": (current / baseline) if baseline > 0 else 0,
                    }
                )

            elif insight_type == InsightType.ANOMALY:
                key_metrics.update(
                    {
                        "anomaly_type": analytics_data.get("type", "statistical"),
                        "severity": analytics_data.get("severity", "moderate"),
                        "deviation": analytics_data.get("deviation", 0),
                        "metric": analytics_data.get("metric", "engagement"),
                        "change": analytics_data.get("change_percent", 0),
                        "direction": (
                            "increased"
                            if analytics_data.get("change_percent", 0) > 0
                            else "decreased"
                        ),
                    }
                )

            elif insight_type == InsightType.GROWTH:
                key_metrics.update(
                    {
                        "rate": analytics_data.get("growth_rate", 0),
                        "metric": analytics_data.get("metric", "followers"),
                        "period": analytics_data.get("period_days", 30),
                        "status": self._assess_growth_status(analytics_data.get("growth_rate", 0)),
                    }
                )

            elif insight_type == InsightType.ENGAGEMENT:
                key_metrics.update(
                    {
                        "rate": analytics_data.get("engagement_rate", 0),
                        "metric": analytics_data.get("metric", "engagement"),
                        "interactions": analytics_data.get("total_interactions", 0),
                        "status": self._assess_engagement_level(
                            analytics_data.get("engagement_rate", 0)
                        ),
                    }
                )

            # Add common metrics
            key_metrics.update(
                {
                    "confidence": analytics_data.get("confidence", 0.7),
                    "timestamp": analytics_data.get("timestamp", datetime.now().isoformat()),
                }
            )

            return key_metrics

        except Exception as e:
            logger.error(f"Key metrics extraction failed: {e}")
            return {
                "error": "Unable to extract key metrics",
                "metric": analytics_data.get("metric", "unknown"),
            }

    def _format_metrics_for_template(self, key_metrics: dict) -> dict[str, Any]:
        """Format metrics for template substitution"""
        formatted = {}

        for key, value in key_metrics.items():
            if isinstance(value, float):
                # Format floats to 1-2 decimal places
                formatted[key] = f"{value:.1f}" if value < 100 else f"{value:.0f}"
            elif isinstance(value, int) and value > 1000:
                # Format large numbers with commas
                formatted[key] = f"{value:,}"
            else:
                formatted[key] = value

        return formatted

    def _assess_growth_status(self, growth_rate: float) -> str:
        """Assess growth status from rate"""
        if growth_rate > 20:
            return "exceptional"
        elif growth_rate > 10:
            return "strong"
        elif growth_rate > 5:
            return "good"
        elif growth_rate > 0:
            return "moderate"
        elif growth_rate == 0:
            return "stable"
        else:
            return "declining"

    def _assess_engagement_level(self, engagement_rate: float) -> str:
        """Assess engagement level from rate"""
        if engagement_rate > 15:
            return "exceptional"
        elif engagement_rate > 10:
            return "very high"
        elif engagement_rate > 5:
            return "high"
        elif engagement_rate > 2:
            return "moderate"
        else:
            return "low"

    def _generate_fallback_narrative(
        self, insight_type: InsightType, analytics_data: dict
    ) -> InsightNarrative:
        """Generate fallback narrative when main generation fails"""
        metric = analytics_data.get("metric", "analytics")

        return InsightNarrative(
            insight_type=insight_type,
            title=f"📊 {metric.title()} Insights",
            narrative=f"Analytics data available for {metric}. Please review detailed metrics for more information.",
            confidence=0.3,
            key_metrics={"metric": metric, "status": "available"},
            recommendations=[
                "Review detailed analytics dashboard",
                "Monitor key performance indicators",
            ],
            severity="low",
            generated_at=datetime.now(),
        )

    async def health_check(self) -> dict[str, Any]:
        """Health check for narrative generator"""
        return {
            "service": "NarrativeGenerator",
            "status": "healthy",
            "capabilities": [
                "insight_narrative_generation",
                "title_generation",
                "confidence_calculation",
                "recommendation_generation",
                "severity_assessment",
            ],
            "dependencies": {
                "template_manager": "initialized",
                "formatter": "initialized",
            },
        }
