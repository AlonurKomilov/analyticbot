"""
Explanation Generator Service - Specialized Explanations

Generates specialized explanations for anomalies, trends, executive summaries,
and dynamic reports.

Part of NLG Service Refactoring (Priority #2)
"""

from __future__ import annotations

import logging
from typing import Any

from ..formatting.content_formatter import ContentFormatter
from ..templates.template_manager import NarrativeStyle, TemplateManager

logger = logging.getLogger(__name__)


class ExplanationGenerator:
    """
    💬 Explanation Generator Service

    Single Responsibility: Generate specialized explanations

    Responsibilities:
    - Generate anomaly explanations
    - Create trend stories
    - Generate executive summaries
    - Create dynamic reports
    - Explain specific patterns and changes
    """

    def __init__(
        self,
        template_manager: TemplateManager | None = None,
        formatter: ContentFormatter | None = None,
    ):
        self.template_manager = template_manager or TemplateManager()
        self.formatter = formatter or ContentFormatter()
        logger.info("ExplanationGenerator initialized")

    async def explain_anomaly(
        self,
        anomaly_data: dict,
        historical_context: dict,
        style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL,
    ) -> str:
        """
        🚨 Generate Human-Readable Anomaly Explanations

        Converts statistical anomalies into understandable narratives.

        Args:
            anomaly_data: Anomaly detection data
            historical_context: Historical data for context
            style: Narrative style

        Returns:
            Human-readable anomaly explanation
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

            return self.formatter.clean_narrative(explanation)

        except Exception as e:
            logger.error(f"Anomaly explanation generation failed: {e}")
            return "An unusual pattern was detected in your analytics data that requires further investigation."

    async def generate_trend_story(
        self, trend_data: dict, style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL
    ) -> str:
        """
        📈 Generate Trend Narratives

        Creates engaging stories about data trends and patterns.

        Args:
            trend_data: Trend analysis data
            style: Narrative style

        Returns:
            Trend story narrative
        """
        try:
            direction = trend_data.get("trend_direction", "stable")
            strength = trend_data.get("trend_strength", 0.5)
            metric = trend_data.get("metric", "engagement")
            duration = trend_data.get("period_days", 30)

            # Get metric description
            metric_desc = self.template_manager.get_metric_description(metric)

            # Generate trend story based on direction and strength
            if direction in ["increasing", "growing", "up"]:
                story = self._generate_positive_trend_story(metric_desc, strength, duration, style)
            elif direction in ["decreasing", "declining", "down"]:
                story = self._generate_negative_trend_story(metric_desc, strength, duration, style)
            else:
                story = self._generate_stable_trend_story(metric_desc, duration, style)

            # Add context if available
            if trend_data.get("change_points"):
                change_context = self._explain_change_points(trend_data["change_points"])
                story += f" {change_context}"

            return self.formatter.clean_narrative(story)

        except Exception as e:
            logger.error(f"Trend story generation failed: {e}")
            metric = trend_data.get("metric", "analytics")
            return f"Your {metric} data shows patterns over the analyzed period."

    async def generate_executive_summary(
        self, comprehensive_analytics: dict, time_period: str = "30 days"
    ) -> str:
        """
        📊 Generate Executive Summary

        Creates a one-paragraph AI summary for decision makers.

        Args:
            comprehensive_analytics: Complete analytics data
            time_period: Time period for summary

        Returns:
            Executive summary paragraph
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
            {action_summary} Key metrics show {kpis.get('primary_metric', 'engagement')}
            at {kpis.get('current_level', 'baseline')} levels with
            {kpis.get('confidence', 'moderate')} confidence in continued trajectory.
            """.strip()

            # Clean up and format
            return self.formatter.clean_narrative(executive_summary)

        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return f"Executive summary unavailable for {time_period} period. Please review detailed analytics."

    async def generate_dynamic_report(
        self,
        analytics_suite: dict,
        report_type: str = "comprehensive",
        style: NarrativeStyle = NarrativeStyle.ANALYTICAL,
    ) -> dict[str, str]:
        """
        📋 Generate Dynamic Natural Language Reports

        Creates comprehensive multi-section reports with narratives.

        Args:
            analytics_suite: Complete analytics data
            report_type: Type of report (comprehensive, summary, detailed)
            style: Narrative style

        Returns:
            Dictionary of section names to narrative content
        """
        try:
            report_sections = {}

            # Overview section
            if analytics_suite.get("overview"):
                overview_narrative = await self._generate_overview_narrative(
                    analytics_suite["overview"], style
                )
                report_sections["overview"] = overview_narrative

            # Growth section
            if analytics_suite.get("growth"):
                growth_narrative = await self._generate_growth_narrative(
                    analytics_suite["growth"], style
                )
                report_sections["growth"] = growth_narrative

            # Engagement section
            if analytics_suite.get("engagement"):
                engagement_narrative = await self._generate_engagement_narrative(
                    analytics_suite["engagement"], style
                )
                report_sections["engagement"] = engagement_narrative

            # Predictions section (if available)
            if analytics_suite.get("predictions"):
                predictions_narrative = await self._generate_predictions_narrative(
                    analytics_suite["predictions"], style
                )
                report_sections["predictions"] = predictions_narrative

            return report_sections

        except Exception as e:
            logger.error(f"Dynamic report generation failed: {e}")
            return {
                "error": "Report generation encountered an issue. Please review raw analytics data."
            }

    # Private helper methods for anomaly explanations

    def _generate_executive_anomaly_explanation(
        self, anomaly_type: str, metric: str, change_percent: float, severity: str
    ) -> str:
        """Generate executive-level anomaly explanation"""
        metric_desc = self.template_manager.get_metric_description(metric)

        if abs(change_percent) > 50:
            magnitude = "significant"
        elif abs(change_percent) > 25:
            magnitude = "notable"
        else:
            magnitude = "moderate"

        direction = "increase" if change_percent > 0 else "decrease"

        return f"{severity.title()} {magnitude} {direction} in {metric_desc} ({abs(change_percent):.1f}%) requires executive attention."

    def _generate_technical_anomaly_explanation(
        self, anomaly_data: dict, historical_context: dict
    ) -> str:
        """Generate technical anomaly explanation"""
        z_score = anomaly_data.get("z_score", 0)
        p_value = anomaly_data.get("p_value", 0.05)
        metric = anomaly_data.get("metric", "metric")

        metric_desc = self.template_manager.get_metric_description(metric)

        return f"Statistical anomaly detected in {metric_desc}: z-score = {z_score:.2f}, p-value = {p_value:.4f}. Data point falls outside expected distribution bounds."

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
        metric_desc = self.template_manager.get_metric_description(metric)
        direction = "jumped up" if change_percent > 0 else "dropped down"

        if severity == "critical":
            excitement = "This is quite unusual and"
        elif severity == "high":
            excitement = "This is interesting and"
        else:
            excitement = "This"

        value_str = self.formatter.format_number(value)
        baseline_str = self.formatter.format_number(baseline)

        return f"{excitement} worth noting - your {metric_desc} {direction} by {abs(change_percent):.1f}% from the normal level of {baseline_str} to {value_str}."

    # Private helper methods for trend stories

    def _generate_positive_trend_story(
        self, metric: str, strength: float, duration: int, style: NarrativeStyle
    ) -> str:
        """Generate story for positive trends"""
        strength_desc = self.formatter.format_trend_description("increasing", strength)
        period = self.formatter.format_time_period(duration)

        if style == NarrativeStyle.EXECUTIVE:
            return f"{metric.title()} shows {strength_desc} trend over {period}."
        else:
            return f"Great news! Your {metric} has been on a {strength_desc} trend for the past {period}."

    def _generate_negative_trend_story(
        self, metric: str, strength: float, duration: int, style: NarrativeStyle
    ) -> str:
        """Generate story for negative trends"""
        period = self.formatter.format_time_period(duration)

        if strength > 0.8:
            urgency = "requires immediate attention"
        elif strength > 0.6:
            urgency = "needs strategic review"
        else:
            urgency = "should be monitored"

        if style == NarrativeStyle.EXECUTIVE:
            return f"{metric.title()} declining trend {urgency}."
        else:
            return f"Your {metric} has been declining over the past {period} and {urgency}."

    def _generate_stable_trend_story(
        self, metric: str, duration: int, style: NarrativeStyle
    ) -> str:
        """Generate story for stable trends"""
        period = self.formatter.format_time_period(duration)

        if style == NarrativeStyle.EXECUTIVE:
            return f"{metric.title()} remains stable over {period} period."
        else:
            return f"Your {metric} has been holding steady over the past {period}, showing consistent performance."

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

    # Private helper methods for executive summaries

    def _summarize_performance(self, kpis: dict) -> str:
        """Summarize performance for executive summary"""
        performance = kpis.get("overall_performance", "moderate")

        performance_map = {
            "excellent": "your channel has demonstrated exceptional performance",
            "good": "your channel has shown solid performance",
            "moderate": "your channel has maintained steady performance",
            "needs_improvement": "your channel performance requires attention",
        }

        return performance_map.get(performance, "your channel has shown activity")

    def _summarize_trends(self, kpis: dict) -> str:
        """Summarize trends for executive summary"""
        trend = kpis.get("primary_trend", "stable")

        trend_map = {
            "growing": "with consistent upward momentum.",
            "increasing": "with consistent upward momentum.",
            "declining": "though showing signs of decline that need addressing.",
            "decreasing": "though showing signs of decline that need addressing.",
            "stable": "with stable metrics across key indicators.",
        }

        return trend_map.get(trend, "with observable patterns.")

    def _summarize_actions(self, kpis: dict) -> str:
        """Summarize recommended actions for executive summary"""
        priority = kpis.get("action_priority", "monitor")

        priority_map = {
            "immediate": "Immediate action is recommended to address key metrics.",
            "planned": "Strategic planning should focus on optimization opportunities.",
            "monitor": "Continue monitoring with periodic strategy reviews.",
        }

        return priority_map.get(priority, "Review metrics regularly for insights.")

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
            trend in ["declining", "decreasing"] and kpis.get("trend_strength", 0) > 0.7
        ):
            kpis["action_priority"] = "immediate"
        elif performance in ["good", "excellent"] and trend in ["growing", "increasing"]:
            kpis["action_priority"] = "monitor"
        else:
            kpis["action_priority"] = "planned"

        kpis["confidence"] = "high" if kpis.get("trend_strength", 0) > 0.8 else "moderate"
        kpis["current_level"] = performance
        kpis["primary_metric"] = "engagement"

        return kpis

    # Private helper methods for dynamic reports

    async def _generate_overview_narrative(self, overview_data: dict, style: NarrativeStyle) -> str:
        """Generate narrative for overview section"""
        posts = overview_data.get("posts", 0)
        views = overview_data.get("views", 0)
        avg_reach = overview_data.get("avg_reach", views / posts if posts > 0 else 0)

        if style == NarrativeStyle.EXECUTIVE:
            return f"Channel published {posts} posts generating {self.formatter.format_number(views)} total views with {avg_reach:.0f} average reach per post."
        else:
            return f"Your channel was quite active with {posts} posts published. These posts reached a total of {self.formatter.format_number(views)} views, which means each post averaged about {avg_reach:.0f} views."

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

    async def health_check(self) -> dict[str, Any]:
        """Health check for explanation generator"""
        return {
            "service": "ExplanationGenerator",
            "status": "healthy",
            "capabilities": [
                "anomaly_explanation",
                "trend_storytelling",
                "executive_summary_creation",
                "dynamic_report_generation",
                "multi_style_support",
            ],
            "dependencies": {"template_manager": "initialized", "formatter": "initialized"},
        }
