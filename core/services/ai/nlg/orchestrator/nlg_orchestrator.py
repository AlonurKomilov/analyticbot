"""
NLG Orchestrator - Natural Language Generation Coordinator

Orchestrates all NLG microservices to provide a unified interface
for natural language generation capabilities.

Part of NLG Service Refactoring (Priority #2)
"""

from __future__ import annotations

import logging
from typing import Any

from ..explanation.explanation_generator import ExplanationGenerator
from ..formatting.content_formatter import ContentFormatter
from ..narrative.narrative_generator import InsightNarrative, NarrativeGenerator
from ..templates.template_manager import InsightType, NarrativeStyle, TemplateManager

logger = logging.getLogger(__name__)


class NLGOrchestrator:
    """
    🎭 NLG Orchestrator

    Single Responsibility: Coordinate NLG microservices

    Responsibilities:
    - Initialize and manage all NLG microservices
    - Provide unified API for NLG operations
    - Route requests to appropriate services
    - Aggregate results from multiple services
    - Maintain backwards compatibility with old NLG service
    """

    def __init__(self):
        """Initialize all NLG microservices"""
        # Initialize shared dependencies first
        self.template_manager = TemplateManager()
        self.formatter = ContentFormatter()

        # Initialize specialized services with shared dependencies
        self.narrative_generator = NarrativeGenerator(self.template_manager, self.formatter)
        self.explanation_generator = ExplanationGenerator(self.template_manager, self.formatter)

        logger.info("NLGOrchestrator initialized with all microservices")

    # ============================================================
    # Main API Methods (Backwards Compatible with old NLG service)
    # ============================================================

    async def generate_insight_narrative(
        self,
        analytics_data: dict,
        insight_type: InsightType,
        style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL,
        channel_context: dict | None = None,
    ) -> InsightNarrative:
        """
        🎯 Generate Natural Language Insight from Analytics Data

        Delegates to NarrativeGenerator for insight narrative creation.

        Args:
            analytics_data: Raw analytics data from services
            insight_type: Type of insight to generate
            style: Narrative style for target audience
            channel_context: Additional context about the channel

        Returns:
            InsightNarrative with human-readable explanations
        """
        return await self.narrative_generator.generate_insight_narrative(
            analytics_data, insight_type, style, channel_context
        )

    async def generate_executive_summary(
        self, comprehensive_analytics: dict, time_period: str = "30 days"
    ) -> str:
        """
        📊 Generate Executive Summary

        Creates a one-paragraph AI summary for decision makers.
        Delegates to ExplanationGenerator.

        Args:
            comprehensive_analytics: Complete analytics data
            time_period: Time period for summary

        Returns:
            Executive summary paragraph
        """
        return await self.explanation_generator.generate_executive_summary(
            comprehensive_analytics, time_period
        )

    async def explain_anomaly(
        self,
        anomaly_data: dict,
        historical_context: dict,
        style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL,
    ) -> str:
        """
        🚨 Generate Human-Readable Anomaly Explanations

        Converts statistical anomalies into understandable narratives.
        Delegates to ExplanationGenerator.

        Args:
            anomaly_data: Anomaly detection data
            historical_context: Historical data for context
            style: Narrative style

        Returns:
            Human-readable anomaly explanation
        """
        return await self.explanation_generator.explain_anomaly(
            anomaly_data, historical_context, style
        )

    async def generate_trend_story(
        self, trend_data: dict, style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL
    ) -> str:
        """
        📈 Generate Trend Narratives

        Creates engaging stories about data trends and patterns.
        Delegates to ExplanationGenerator.

        Args:
            trend_data: Trend analysis data
            style: Narrative style

        Returns:
            Trend story narrative
        """
        return await self.explanation_generator.generate_trend_story(trend_data, style)

    async def generate_dynamic_report(
        self,
        analytics_suite: dict,
        report_type: str = "comprehensive",
        style: NarrativeStyle = NarrativeStyle.ANALYTICAL,
    ) -> dict[str, str]:
        """
        📋 Generate Dynamic Natural Language Reports

        Creates comprehensive multi-section reports with narratives.
        Delegates to ExplanationGenerator.

        Args:
            analytics_suite: Complete analytics data
            report_type: Type of report (comprehensive, summary, detailed)
            style: Narrative style

        Returns:
            Dictionary of section names to narrative content
        """
        return await self.explanation_generator.generate_dynamic_report(
            analytics_suite, report_type, style
        )

    # ============================================================
    # Convenience Methods (Enhanced API)
    # ============================================================

    async def generate_multi_insight_report(
        self,
        analytics_data: dict,
        insight_types: list[InsightType],
        style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL,
        channel_context: dict | None = None,
    ) -> list[InsightNarrative]:
        """
        Generate multiple insights in one call

        Args:
            analytics_data: Analytics data
            insight_types: List of insight types to generate
            style: Narrative style
            channel_context: Channel context

        Returns:
            List of generated insights
        """
        insights = []

        for insight_type in insight_types:
            try:
                insight = await self.generate_insight_narrative(
                    analytics_data, insight_type, style, channel_context
                )
                insights.append(insight)
            except Exception as e:
                logger.error(f"Failed to generate {insight_type.value} insight: {e}")
                continue

        return insights

    async def generate_comprehensive_narrative(
        self, analytics_suite: dict, style: NarrativeStyle = NarrativeStyle.ANALYTICAL
    ) -> dict[str, Any]:
        """
        Generate comprehensive narrative package with all sections

        Args:
            analytics_suite: Complete analytics data
            style: Narrative style

        Returns:
            Complete narrative package with multiple sections
        """
        try:
            result = {
                "executive_summary": None,
                "dynamic_report": {},
                "insights": [],
                "style": style.value,
            }

            # Generate executive summary
            if analytics_suite.get("overview"):
                result["executive_summary"] = await self.generate_executive_summary(
                    analytics_suite, "30 days"
                )

            # Generate dynamic report sections
            result["dynamic_report"] = await self.generate_dynamic_report(
                analytics_suite, "comprehensive", style
            )

            # Generate specific insights if data available
            insight_types = []
            if analytics_suite.get("trend_analysis"):
                insight_types.append(InsightType.TREND)
            if analytics_suite.get("anomalies"):
                insight_types.append(InsightType.ANOMALY)
            if analytics_suite.get("performance"):
                insight_types.append(InsightType.PERFORMANCE)

            if insight_types:
                result["insights"] = await self.generate_multi_insight_report(
                    analytics_suite, insight_types, style
                )

            return result

        except Exception as e:
            logger.error(f"Comprehensive narrative generation failed: {e}")
            return {
                "error": "Comprehensive narrative generation encountered an issue",
                "style": style.value,
            }

    # ============================================================
    # Template & Formatting Access (Direct service access)
    # ============================================================

    def get_narrative_template(self, insight_type: InsightType, style: NarrativeStyle) -> str:
        """Get narrative template - delegates to TemplateManager"""
        return self.template_manager.get_narrative_template(insight_type, style)

    def get_metric_description(self, metric: str) -> str:
        """Get metric description - delegates to TemplateManager"""
        return self.template_manager.get_metric_description(metric)

    def get_recommendation_patterns(self, scenario: str) -> list[str]:
        """Get recommendation patterns - delegates to TemplateManager"""
        return self.template_manager.get_recommendation_patterns(scenario)

    def clean_narrative(self, narrative: str) -> str:
        """Clean narrative text - delegates to ContentFormatter"""
        return self.formatter.clean_narrative(narrative)

    def format_percentage(self, value: float, decimals: int = 1) -> str:
        """Format percentage - delegates to ContentFormatter"""
        return self.formatter.format_percentage(value, decimals)

    def format_number(self, value: float, use_thousands_separator: bool = True) -> str:
        """Format number - delegates to ContentFormatter"""
        return self.formatter.format_number(value, use_thousands_separator)

    def format_list_items(self, items: list[str], style: str = "bullet") -> str:
        """Format list items - delegates to ContentFormatter"""
        return self.formatter.format_list_items(items, style)

    # ============================================================
    # Health Check & Status
    # ============================================================

    async def health_check(self) -> dict[str, Any]:
        """
        Comprehensive health check for all NLG services

        Returns:
            Health status of orchestrator and all microservices
        """
        try:
            # Check all microservices
            template_health = await self.template_manager.health_check()
            formatter_health = await self.formatter.health_check()
            narrative_health = await self.narrative_generator.health_check()
            explanation_health = await self.explanation_generator.health_check()

            # Aggregate health status
            all_healthy = all(
                [
                    template_health.get("status") == "healthy",
                    formatter_health.get("status") == "healthy",
                    narrative_health.get("status") == "healthy",
                    explanation_health.get("status") == "healthy",
                ]
            )

            return {
                "service": "NLGOrchestrator",
                "status": "healthy" if all_healthy else "degraded",
                "microservices": {
                    "template_manager": template_health,
                    "content_formatter": formatter_health,
                    "narrative_generator": narrative_health,
                    "explanation_generator": explanation_health,
                },
                "capabilities": [
                    "insight_narrative_generation",
                    "executive_summary_creation",
                    "anomaly_explanation",
                    "trend_storytelling",
                    "dynamic_report_generation",
                    "multi_insight_reports",
                    "comprehensive_narratives",
                ],
                "narrative_styles": [style.value for style in NarrativeStyle],
                "insight_types": [insight.value for insight in InsightType],
                "total_templates": template_health.get("templates_loaded", 0),
                "architecture": "microservices (4 services + orchestrator)",
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"service": "NLGOrchestrator", "status": "error", "error": str(e)}

    def get_service_info(self) -> dict[str, Any]:
        """Get information about orchestrator and microservices"""
        return {
            "orchestrator": "NLGOrchestrator",
            "architecture": "microservices",
            "services": {
                "template_manager": {
                    "class": "TemplateManager",
                    "responsibility": "Manage templates and patterns",
                },
                "content_formatter": {
                    "class": "ContentFormatter",
                    "responsibility": "Format and clean text content",
                },
                "narrative_generator": {
                    "class": "NarrativeGenerator",
                    "responsibility": "Generate narratives and insights",
                },
                "explanation_generator": {
                    "class": "ExplanationGenerator",
                    "responsibility": "Generate specialized explanations",
                },
            },
            "benefits": [
                "Single Responsibility per service",
                "Easy to test and maintain",
                "Independent service scaling",
                "Clear separation of concerns",
                "Backwards compatible API",
            ],
        }


# Alias for backwards compatibility with old service name
NaturalLanguageGenerationService = NLGOrchestrator
