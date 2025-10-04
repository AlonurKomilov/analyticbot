"""
🗣️ Natural Language Generation (NLG) Service

This service transforms analytics data into human-readable insights and narratives.
Converts metrics, trends, and patterns into natural language explanations.

Part of Phase 3: AI-First Intelligence Transformation
Integrates with AIInsightsService to provide narrative intelligence.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime
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


class NaturalLanguageGenerationService:
    """
    🗣️ Natural Language Generation Service

    Transforms analytics data into human-readable insights:
    - Converts metrics into stories
    - Generates executive summaries
    - Creates dynamic reports
    - Explains trends and anomalies
    - Provides actionable recommendations
    """

    def __init__(self):
        self._narrative_templates = self._initialize_narrative_templates()
        self._metric_descriptions = self._initialize_metric_descriptions()
        self._recommendation_patterns = self._initialize_recommendation_patterns()

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

    async def generate_executive_summary(
        self, comprehensive_analytics: dict, time_period: str = "30 days"
    ) -> str:
        """
        📊 Generate Executive Summary

        Creates a one-paragraph AI summary for decision makers.
        """
        try:
            # Extract key performance indicators
            kpis = self._extract_executive_kpis(comprehensive_analytics)

            # Generate summary components
            performance_summary = self._summarize_performance(kpis)
            trend_summary = self._summarize_trends(kpis)
            action_summary = self._summarize_actions(kpis)

            # Combine into executive narrative
            executive_summary = f"""
            Over the past {time_period}, {performance_summary} {trend_summary} 
            {action_summary} Key metrics show {kpis.get("primary_metric", "engagement")} 
            at {kpis.get("current_level", "baseline")} levels with 
            {kpis.get("confidence", "moderate")} confidence in continued trajectory.
            """.strip()

            # Clean up and format
            return self._clean_narrative(executive_summary)

        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return f"Executive summary unavailable for {time_period} period. Please review detailed analytics."

    async def explain_anomaly(
        self,
        anomaly_data: dict,
        historical_context: dict,
        style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL,
    ) -> str:
        """
        🚨 Generate Human-Readable Anomaly Explanations

        Converts statistical anomalies into understandable narratives.
        """
        try:
            anomaly_type = anomaly_data.get("type", "unknown")
            severity = anomaly_data.get("severity", "moderate")
            metric = anomaly_data.get("metric", "engagement")
            value = anomaly_data.get("current_value", 0)
            baseline = anomaly_data.get("baseline_value", 0)

            # Calculate change magnitude
            if baseline > 0:
                change_percent = ((value - baseline) / baseline) * 100
            else:
                change_percent = 0

            # Generate anomaly explanation based on style
            if style == NarrativeStyle.EXECUTIVE:
                explanation = self._generate_executive_anomaly_explanation(
                    anomaly_type, metric, change_percent, severity
                )
            elif style == NarrativeStyle.TECHNICAL:
                explanation = self._generate_technical_anomaly_explanation(
                    anomaly_data, historical_context
                )
            else:  # CONVERSATIONAL or ANALYTICAL
                explanation = self._generate_conversational_anomaly_explanation(
                    anomaly_type, metric, value, baseline, change_percent, severity
                )

            return explanation

        except Exception as e:
            logger.error(f"Anomaly explanation generation failed: {e}")
            return "An unusual pattern was detected in your analytics data that requires further investigation."

    async def generate_trend_story(
        self, trend_data: dict, style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL
    ) -> str:
        """
        📈 Generate Trend Narratives

        Creates engaging stories about data trends and patterns.
        """
        try:
            direction = trend_data.get("trend_direction", "stable")
            strength = trend_data.get("trend_strength", 0.5)
            metric = trend_data.get("metric", "engagement")
            duration = trend_data.get("period_days", 30)

            # Generate trend story based on direction and strength
            if direction == "increasing":
                story = self._generate_positive_trend_story(metric, strength, duration, style)
            elif direction == "decreasing":
                story = self._generate_negative_trend_story(metric, strength, duration, style)
            else:
                story = self._generate_stable_trend_story(metric, duration, style)

            # Add context if available
            if trend_data.get("change_points"):
                change_context = self._explain_change_points(trend_data["change_points"])
                story += f" {change_context}"

            return story

        except Exception as e:
            logger.error(f"Trend story generation failed: {e}")
            return f"Your {trend_data.get('metric', 'analytics')} data shows patterns over the analyzed period."

    async def generate_dynamic_report(
        self,
        analytics_suite: dict,
        report_type: str = "comprehensive",
        style: NarrativeStyle = NarrativeStyle.ANALYTICAL,
    ) -> dict[str, str]:
        """
        📋 Generate Dynamic Natural Language Reports

        Creates comprehensive reports with natural language sections.
        """
        try:
            report_sections = {}

            # Overview Section
            if analytics_suite.get("overview"):
                report_sections["overview"] = await self._generate_overview_narrative(
                    analytics_suite["overview"], style
                )

            # Growth Section
            if analytics_suite.get("growth_data"):
                report_sections["growth"] = await self._generate_growth_narrative(
                    analytics_suite["growth_data"], style
                )

            # Engagement Section
            if analytics_suite.get("engagement_data"):
                report_sections["engagement"] = await self._generate_engagement_narrative(
                    analytics_suite["engagement_data"], style
                )

            # Trends Section
            if analytics_suite.get("trend_analysis"):
                report_sections["trends"] = await self.generate_trend_story(
                    analytics_suite["trend_analysis"], style
                )

            # Predictions Section
            if analytics_suite.get("predictions"):
                report_sections["predictions"] = await self._generate_predictions_narrative(
                    analytics_suite["predictions"], style
                )

            # Executive Summary (always generated last)
            report_sections["executive_summary"] = await self.generate_executive_summary(
                analytics_suite
            )

            return report_sections

        except Exception as e:
            logger.error(f"Dynamic report generation failed: {e}")
            return {"error": "Unable to generate natural language report at this time."}

    # === PRIVATE METHODS ===

    def _initialize_narrative_templates(self) -> dict[str, dict[str, str]]:
        """Initialize narrative templates for different insight types and styles"""
        return {
            InsightType.TREND.value: {
                NarrativeStyle.EXECUTIVE.value: "Your {metric} shows a {direction} trend of {magnitude}% over {period}.",
                NarrativeStyle.CONVERSATIONAL.value: "Good news! Your {metric} has been {direction} by {magnitude}% over the past {period}.",
                NarrativeStyle.TECHNICAL.value: "{metric} demonstrates {direction} trajectory with {strength} trend strength (p<{p_value}).",
            },
            InsightType.ANOMALY.value: {
                NarrativeStyle.EXECUTIVE.value: "{severity} anomaly detected in {metric} ({change}% deviation).",
                NarrativeStyle.CONVERSATIONAL.value: "Something interesting happened with your {metric} - it {direction} by {change}%.",
                NarrativeStyle.TECHNICAL.value: "Statistical anomaly: {metric} outside {sigma}σ bounds, z-score: {z_score}.",
            },
            InsightType.PERFORMANCE.value: {
                NarrativeStyle.EXECUTIVE.value: "Performance {status}: {metric} at {level}% of target.",
                NarrativeStyle.CONVERSATIONAL.value: "Your {metric} is performing {status} - currently at {level}% of your goal.",
                NarrativeStyle.TECHNICAL.value: "Performance metrics: {metric} = {value}, benchmark = {benchmark}, ratio = {ratio}.",
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
        }

    def _initialize_recommendation_patterns(self) -> dict[str, list[str]]:
        """Initialize recommendation patterns for different scenarios"""
        return {
            "high_engagement": [
                "Continue your current content strategy",
                "Consider increasing posting frequency",
                "Replicate successful content patterns",
            ],
            "low_engagement": [
                "Review content timing and format",
                "Analyze successful competitor strategies",
                "Consider audience engagement tactics",
            ],
            "growing_trend": [
                "Capitalize on positive momentum",
                "Scale successful content types",
                "Monitor trend sustainability",
            ],
            "declining_trend": [
                "Investigate causes of decline",
                "Implement recovery strategies",
                "Review content-market fit",
            ],
        }

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
                    }
                )

            elif insight_type == InsightType.PERFORMANCE:
                key_metrics.update(
                    {
                        "current_value": analytics_data.get("current_value", 0),
                        "baseline_value": analytics_data.get("baseline_value", 0),
                        "metric": analytics_data.get("metric", "views"),
                        "performance_score": analytics_data.get("performance_score", 0.5),
                    }
                )

            elif insight_type == InsightType.ANOMALY:
                key_metrics.update(
                    {
                        "anomaly_type": analytics_data.get("type", "statistical"),
                        "severity": analytics_data.get("severity", "moderate"),
                        "deviation": analytics_data.get("deviation", 0),
                        "metric": analytics_data.get("metric", "engagement"),
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
            return {"error": "Unable to extract key metrics"}

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
            template = self._narrative_templates.get(insight_type.value, {}).get(
                style.value, "Analytics data shows {metric} patterns in your channel."
            )

            # Format template with metrics
            narrative = template.format(**key_metrics)

            # Add context if available
            if channel_context and channel_context.get("name"):
                narrative = f"For {channel_context['name']}: {narrative}"

            # Add confidence qualifier if needed
            confidence = key_metrics.get("confidence", 0.7)
            if confidence < 0.6:
                narrative += " (preliminary analysis)"
            elif confidence > 0.9:
                narrative += " (high confidence)"

            return narrative

        except Exception as e:
            logger.error(f"Narrative generation failed: {e}")
            return f"Analytics insights available for {key_metrics.get('metric', 'your channel')}."

    def _generate_title(
        self, insight_type: InsightType, key_metrics: dict, style: NarrativeStyle
    ) -> str:
        """Generate appropriate title for the insight"""
        try:
            metric = key_metrics.get("metric", "Analytics")
            metric_desc = self._metric_descriptions.get(metric, metric)

            if insight_type == InsightType.TREND:
                direction = key_metrics.get("direction", "stable")
                if direction == "increasing":
                    return f"📈 {metric_desc.title()} Growing Steadily"
                elif direction == "decreasing":
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

            return round(base_confidence, 3)

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
                direction = key_metrics.get("direction")
                if direction == "increasing":
                    recommendations.extend(self._recommendation_patterns["growing_trend"])
                elif direction == "decreasing":
                    recommendations.extend(self._recommendation_patterns["declining_trend"])
                else:
                    recommendations.append("Maintain current strategy and monitor for changes")

            elif insight_type == InsightType.PERFORMANCE:
                score = key_metrics.get("performance_score", 0.5)
                if score > 0.7:
                    recommendations.extend(self._recommendation_patterns["high_engagement"])
                else:
                    recommendations.extend(self._recommendation_patterns["low_engagement"])

            elif insight_type == InsightType.ANOMALY:
                severity = key_metrics.get("severity")
                if severity in ["high", "critical"]:
                    recommendations.extend(
                        [
                            "Investigate root cause immediately",
                            "Review recent content changes",
                            "Monitor closely for pattern continuation",
                        ]
                    )
                else:
                    recommendations.extend(
                        [
                            "Monitor trend development",
                            "Review contributing factors",
                            "Consider strategy adjustments",
                        ]
                    )

            return recommendations[:3]  # Limit to top 3 recommendations

        except Exception as e:
            logger.error(f"Recommendations generation failed: {e}")
            return ["Review analytics data for optimization opportunities"]

    def _determine_severity(self, key_metrics: dict, insight_type: InsightType) -> str:
        """Determine severity level of the insight"""
        try:
            if insight_type == InsightType.ANOMALY:
                return key_metrics.get("severity", "medium")

            elif insight_type == InsightType.PERFORMANCE:
                score = key_metrics.get("performance_score", 0.5)
                if score < 0.3:
                    return "high"
                elif score < 0.6:
                    return "medium"
                else:
                    return "low"

            elif insight_type == InsightType.TREND:
                direction = key_metrics.get("direction")
                strength = key_metrics.get("strength", 0.5)

                if direction == "decreasing" and strength > 0.7:
                    return "high"
                elif direction == "increasing" and strength > 0.7:
                    return "low"  # Good news, low severity
                else:
                    return "medium"

            return "medium"

        except Exception as e:
            logger.error(f"Severity determination failed: {e}")
            return "medium"

    def _generate_fallback_narrative(
        self, insight_type: InsightType, analytics_data: dict
    ) -> InsightNarrative:
        """Generate fallback narrative when main generation fails"""
        return InsightNarrative(
            insight_type=insight_type,
            title="📊 Analytics Insight Available",
            narrative="Analytics data is available for review. Please check detailed metrics for insights.",
            confidence=0.5,
            key_metrics={"metric": "general", "status": "available"},
            recommendations=["Review detailed analytics dashboard"],
            severity="low",
            generated_at=datetime.now(),
        )

    def _clean_narrative(self, narrative: str) -> str:
        """Clean and format narrative text"""
        # Remove extra whitespace
        narrative = re.sub(r"\s+", " ", narrative)

        # Ensure proper sentence endings
        narrative = narrative.strip()
        if not narrative.endswith("."):
            narrative += "."

        return narrative

    # Additional helper methods for specific narrative types...

    def _summarize_performance(self, kpis: dict) -> str:
        """Summarize performance for executive summary"""
        performance = kpis.get("overall_performance", "moderate")
        if performance == "excellent":
            return "your channel has demonstrated exceptional performance"
        elif performance == "good":
            return "your channel has shown solid performance"
        elif performance == "moderate":
            return "your channel has maintained steady performance"
        else:
            return "your channel performance requires attention"

    def _summarize_trends(self, kpis: dict) -> str:
        """Summarize trends for executive summary"""
        trend = kpis.get("primary_trend", "stable")
        if trend == "growing":
            return "with consistent upward momentum."
        elif trend == "declining":
            return "though showing signs of decline that need addressing."
        else:
            return "with stable metrics across key indicators."

    def _summarize_actions(self, kpis: dict) -> str:
        """Summarize recommended actions for executive summary"""
        priority = kpis.get("action_priority", "monitor")
        if priority == "immediate":
            return "Immediate action is recommended to address key metrics."
        elif priority == "planned":
            return "Strategic planning should focus on optimization opportunities."
        else:
            return "Continue monitoring with periodic strategy reviews."

    def _extract_executive_kpis(self, analytics: dict) -> dict:
        """Extract key performance indicators for executive summary"""
        kpis = {}

        # Extract from overview
        if analytics.get("overview"):
            overview = analytics["overview"]
            kpis["posts"] = overview.get("posts", 0)
            kpis["views"] = overview.get("views", 0)
            kpis["engagement_rate"] = overview.get("err", 0)

        # Extract from trends
        if analytics.get("trend_analysis"):
            trends = analytics["trend_analysis"]
            kpis["primary_trend"] = trends.get("trend_direction", "stable")
            kpis["trend_strength"] = trends.get("trend_strength", 0.5)

        # Determine overall performance
        engagement = kpis.get("engagement_rate", 0)
        if engagement > 8.0:
            kpis["overall_performance"] = "excellent"
        elif engagement > 5.0:
            kpis["overall_performance"] = "good"
        elif engagement > 2.0:
            kpis["overall_performance"] = "moderate"
        else:
            kpis["overall_performance"] = "needs_improvement"

        # Determine action priority
        trend = kpis.get("primary_trend", "stable")
        performance = kpis.get("overall_performance", "moderate")

        if performance == "needs_improvement" or (
            trend == "declining" and kpis.get("trend_strength", 0) > 0.7
        ):
            kpis["action_priority"] = "immediate"
        elif performance in ["good", "excellent"] and trend == "growing":
            kpis["action_priority"] = "monitor"
        else:
            kpis["action_priority"] = "planned"

        kpis["confidence"] = "high" if kpis.get("trend_strength", 0) > 0.8 else "moderate"
        kpis["current_level"] = performance
        kpis["primary_metric"] = "engagement"

        return kpis

    # More helper methods for different narrative types...
    async def _generate_overview_narrative(self, overview_data: dict, style: NarrativeStyle) -> str:
        """Generate narrative for overview section"""
        posts = overview_data.get("posts", 0)
        views = overview_data.get("views", 0)
        avg_reach = overview_data.get("avg_reach", 0)

        if style == NarrativeStyle.EXECUTIVE:
            return f"Channel published {posts} posts generating {views:,} total views with {avg_reach:.0f} average reach per post."
        else:
            return f"Your channel was quite active with {posts} posts published. These posts reached a total of {views:,} views, which means each post averaged about {avg_reach:.0f} views."

    async def _generate_growth_narrative(self, growth_data: dict, style: NarrativeStyle) -> str:
        """Generate narrative for growth section"""
        growth_rate = growth_data.get("growth_rate", 0)

        if growth_rate > 5:
            return f"Your channel experienced strong growth at {growth_rate:.1f}% rate, indicating healthy audience expansion."
        elif growth_rate > 0:
            return f"Your channel showed positive growth of {growth_rate:.1f}%, building your audience steadily."
        elif growth_rate == 0:
            return "Your channel maintained its audience size with stable follower numbers."
        else:
            return f"Your channel experienced a {abs(growth_rate):.1f}% decline in followers that warrants attention."

    async def _generate_engagement_narrative(
        self, engagement_data: dict, style: NarrativeStyle
    ) -> str:
        """Generate narrative for engagement section"""
        engagement_rate = engagement_data.get("engagement_rate", 0)

        if engagement_rate > 10:
            return "Your audience is highly engaged with exceptional interaction rates."
        elif engagement_rate > 5:
            return "Your audience shows good engagement levels with regular interactions."
        elif engagement_rate > 2:
            return "Your audience engagement is moderate with room for improvement."
        else:
            return "Your audience engagement is below average and needs strategic focus."

    async def _generate_predictions_narrative(
        self, predictions_data: dict, style: NarrativeStyle
    ) -> str:
        """Generate narrative for predictions section"""
        confidence = predictions_data.get("confidence_score", 0.5)

        if confidence > 0.8:
            return (
                "Predictive models show high confidence in forecasted trends and recommendations."
            )
        elif confidence > 0.6:
            return "Predictive analysis provides reliable insights for strategic planning."
        else:
            return "Predictive models suggest trends with moderate confidence requiring validation."

    # Anomaly explanation methods
    def _generate_executive_anomaly_explanation(
        self, anomaly_type: str, metric: str, change_percent: float, severity: str
    ) -> str:
        """Generate executive-level anomaly explanation"""
        if abs(change_percent) > 50:
            magnitude = "significant"
        elif abs(change_percent) > 25:
            magnitude = "notable"
        else:
            magnitude = "moderate"

        direction = "increase" if change_percent > 0 else "decrease"

        return f"{severity.title()} {magnitude} {direction} in {metric} ({abs(change_percent):.1f}%) requires executive attention."

    def _generate_technical_anomaly_explanation(
        self, anomaly_data: dict, historical_context: dict
    ) -> str:
        """Generate technical anomaly explanation"""
        z_score = anomaly_data.get("z_score", 0)
        p_value = anomaly_data.get("p_value", 0.05)

        return f"Statistical anomaly detected: z-score = {z_score:.2f}, p-value = {p_value:.4f}. Data point falls outside expected distribution bounds."

    def _generate_conversational_anomaly_explanation(
        self,
        anomaly_type: str,
        metric: str,
        value: float,
        baseline: float,
        change_percent: float,
        severity: str,
    ) -> str:
        """Generate conversational anomaly explanation"""
        direction = "jumped up" if change_percent > 0 else "dropped down"

        if severity == "critical":
            excitement = "This is quite unusual and"
        elif severity == "high":
            excitement = "This is interesting and"
        else:
            excitement = "This"

        return f"{excitement} worth noting - your {metric} {direction} by {abs(change_percent):.1f}% from the normal level of {baseline:.0f} to {value:.0f}."

    def _explain_change_points(self, change_points: list[dict]) -> str:
        """Explain detected change points in trends"""
        if not change_points:
            return ""

        if len(change_points) == 1:
            point = change_points[0]
            direction = "increase" if point.get("change_direction") == "increase" else "decrease"
            return f"A significant {direction} occurred around day {point.get('index', 'unknown')}."
        else:
            return f"Multiple trend changes were detected with {len(change_points)} significant shift points."

    def _generate_positive_trend_story(
        self, metric: str, strength: float, duration: int, style: NarrativeStyle
    ) -> str:
        """Generate story for positive trends"""
        metric_desc = self._metric_descriptions.get(metric, metric)

        if strength > 0.8:
            strength_desc = "strong"
        elif strength > 0.6:
            strength_desc = "steady"
        else:
            strength_desc = "gradual"

        if style == NarrativeStyle.EXECUTIVE:
            return f"{metric_desc.title()} shows {strength_desc} upward trend over {duration} days."
        else:
            return f"Great news! Your {metric_desc} has been on a {strength_desc} upward trend for the past {duration} days."

    def _generate_negative_trend_story(
        self, metric: str, strength: float, duration: int, style: NarrativeStyle
    ) -> str:
        """Generate story for negative trends"""
        metric_desc = self._metric_descriptions.get(metric, metric)

        if strength > 0.8:
            urgency = "requires immediate attention"
        elif strength > 0.6:
            urgency = "needs strategic review"
        else:
            urgency = "should be monitored"

        if style == NarrativeStyle.EXECUTIVE:
            return f"{metric_desc.title()} declining trend {urgency}."
        else:
            return f"Your {metric_desc} has been declining over the past {duration} days and {urgency}."

    def _generate_stable_trend_story(
        self, metric: str, duration: int, style: NarrativeStyle
    ) -> str:
        """Generate story for stable trends"""
        metric_desc = self._metric_descriptions.get(metric, metric)

        if style == NarrativeStyle.EXECUTIVE:
            return f"{metric_desc.title()} remains stable over {duration}-day period."
        else:
            return f"Your {metric_desc} has been holding steady over the past {duration} days, showing consistent performance."

    async def health_check(self) -> dict[str, Any]:
        """Health check for NLG service"""
        return {
            "service": "NaturalLanguageGenerationService",
            "status": "healthy",
            "capabilities": [
                "insight_narrative_generation",
                "executive_summary_creation",
                "anomaly_explanation",
                "trend_storytelling",
                "dynamic_report_generation",
            ],
            "narrative_styles": [style.value for style in NarrativeStyle],
            "insight_types": [insight.value for insight in InsightType],
            "templates_loaded": len(self._narrative_templates),
            "timestamp": datetime.now().isoformat(),
        }
