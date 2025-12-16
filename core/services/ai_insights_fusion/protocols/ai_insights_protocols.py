"""
AI Insights Fusion Protocols
============================

Service protocol interfaces for AI insights fusion microservices.
These protocols define clean contracts for dependency injection and service interaction.

Protocols:
- CoreInsightsProtocol: Core AI insights generation
- PatternAnalysisProtocol: Content and behavior pattern analysis
- PredictiveAnalysisProtocol: AI predictions and forecasting
- ServiceIntegrationProtocol: Integration with external AI services
- AIInsightsOrchestratorProtocol: Service coordination

Key Benefits:
- Clean separation of concerns
- Dependency injection support
- Easy testing with mock implementations
- Clear service contracts
- Type safety and documentation
"""

from typing import Any, Protocol


class CoreInsightsProtocol(Protocol):
    """
    Protocol for core AI insights generation.

    Single responsibility: Core AI-powered analytics and insights
    """

    async def generate_ai_insights(
        self, channel_id: int, analysis_type: str = "comprehensive", days: int = 30
    ) -> dict[str, Any]:
        """
        Generate core AI-powered analytics insights.

        Args:
            channel_id: Target channel ID
            analysis_type: Type of analysis ('content', 'audience', 'performance', 'comprehensive')
            days: Number of days of historical data to analyze

        Returns:
            Comprehensive AI insights with recommendations and predictions
        """
        ...

    async def generate_insights_with_narrative(
        self, channel_id: int, narrative_style: str = "executive", days: int = 30
    ) -> dict[str, Any]:
        """
        Generate insights with natural language narrative.

        Args:
            channel_id: Target channel ID
            narrative_style: Style of narrative (executive, technical, conversational)
            days: Number of days to analyze

        Returns:
            Insights with natural language explanations
        """
        ...

    async def health_check(self) -> dict[str, Any]:
        """Health check for core insights service"""
        ...


class PatternAnalysisProtocol(Protocol):
    """
    Protocol for pattern analysis and recognition.

    Single responsibility: Content patterns, audience behavior patterns
    """

    async def analyze_content_patterns(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze content patterns from data.

        Args:
            data: Content data for analysis

        Returns:
            Content pattern analysis results
        """
        ...

    async def analyze_audience_behavior(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze audience behavior patterns.

        Args:
            data: Audience data for analysis

        Returns:
            Audience behavior analysis results
        """
        ...

    async def analyze_performance_patterns(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze performance patterns.

        Args:
            data: Performance data for analysis

        Returns:
            Performance pattern analysis results
        """
        ...

    async def extract_key_patterns(
        self, data: dict[str, Any], insights_report: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Extract key patterns from analysis.

        Args:
            data: Raw data
            insights_report: Generated insights

        Returns:
            List of key patterns identified
        """
        ...

    async def health_check(self) -> dict[str, Any]:
        """Health check for pattern analysis service"""
        ...


class PredictiveAnalysisProtocol(Protocol):
    """
    Protocol for AI predictions and forecasting.

    Single responsibility: AI-powered predictions and recommendations
    """

    async def generate_ai_predictions(
        self, data: dict[str, Any], channel_id: int
    ) -> dict[str, Any]:
        """
        Generate AI-powered predictions.

        Args:
            data: Historical data for predictions
            channel_id: Target channel ID

        Returns:
            AI predictions and forecasts
        """
        ...

    async def generate_ai_recommendations(
        self,
        content_insights: dict[str, Any],
        audience_insights: dict[str, Any],
        performance_insights: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Generate AI-powered recommendations.

        Args:
            content_insights: Content analysis results
            audience_insights: Audience analysis results
            performance_insights: Performance analysis results

        Returns:
            List of AI-generated recommendations
        """
        ...

    async def health_check(self) -> dict[str, Any]:
        """Health check for predictive analysis service"""
        ...


class ServiceIntegrationProtocol(Protocol):
    """
    Protocol for service integration and coordination.

    Single responsibility: Integration with existing AI services
    """

    async def integrate_nlg_services(
        self, insights_data: dict[str, Any], narrative_style: str = "executive"
    ) -> dict[str, Any]:
        """
        Integrate with NLG services for narrative generation.

        Args:
            insights_data: Insights data for narrative
            narrative_style: Style of narrative

        Returns:
            Narrative-enhanced insights
        """
        ...

    async def integrate_chat_services(
        self, user_query: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Integrate with AI chat services.

        Args:
            user_query: User's query
            context: Analysis context

        Returns:
            AI chat response
        """
        ...

    async def integrate_anomaly_services(
        self, channel_id: int, time_period: str = "24h"
    ) -> dict[str, Any]:
        """
        Integrate with anomaly detection services.

        Args:
            channel_id: Target channel ID
            time_period: Time period for anomaly detection

        Returns:
            Anomaly detection results
        """
        ...

    async def health_check(self) -> dict[str, Any]:
        """Health check for service integration"""
        ...


class AIInsightsOrchestratorProtocol(Protocol):
    """
    Protocol for AI insights orchestration service.

    Single responsibility: Service coordination and workflow orchestration
    """

    async def coordinate_comprehensive_analysis(
        self, channel_id: int, analysis_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Coordinate comprehensive AI analysis.

        Args:
            channel_id: Target channel ID
            analysis_config: Analysis configuration

        Returns:
            Coordinated comprehensive analysis result
        """
        ...

    async def coordinate_pattern_insights(
        self, channel_id: int, pattern_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Coordinate pattern analysis workflow.

        Args:
            channel_id: Target channel ID
            pattern_config: Pattern analysis configuration

        Returns:
            Coordinated pattern analysis result
        """
        ...

    async def coordinate_predictive_workflow(
        self, channel_id: int, prediction_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Coordinate predictive analysis workflow.

        Args:
            channel_id: Target channel ID
            prediction_config: Prediction configuration

        Returns:
            Coordinated predictive analysis result
        """
        ...

    async def health_check(self) -> dict[str, Any]:
        """Health check for AI insights orchestrator service"""
        ...


# Data models for type safety
class AIInsightsData:
    """AI insights data model"""


class PatternAnalysisResult:
    """Pattern analysis result data model"""


class PredictionResult:
    """Prediction result data model"""
