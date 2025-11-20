"""
Alerts Fusion Protocols
=======================

Service protocol interfaces for alerts fusion microservices.
These protocols define clean contracts for dependency injection and service interaction.

Protocols:
- LiveMonitoringProtocol: Real-time metrics and monitoring
- AlertsManagementProtocol: Alert setup, checking, and management
- CompetitiveIntelligenceProtocol: Competitor analysis and insights
- AlertsOrchestratorProtocol: Service coordination

Key Benefits:
- Clean separation of concerns
- Dependency injection support
- Easy testing with mock implementations
- Clear service contracts
- Type safety and documentation
"""

from typing import Any, Protocol


class LiveMonitoringProtocol(Protocol):
    """
    Protocol for live monitoring and real-time metrics collection.

    Single responsibility: Real-time data collection and live metrics
    """

    async def get_live_metrics(self, channel_id: int, hours: int = 6) -> dict[str, Any]:
        """
        Get real-time live metrics for a channel.

        Args:
            channel_id: Channel to monitor
            hours: Hours of data to retrieve

        Returns:
            Live metrics data including views, engagement, trends
        """
        ...

    async def get_current_metrics(self, channel_id: int) -> dict[str, Any]:
        """
        Get current real-time metrics.

        Args:
            channel_id: Channel to analyze

        Returns:
            Current metrics snapshot
        """
        ...

    async def health_check(self) -> dict[str, Any]:
        """Health check for live monitoring service"""
        ...


class AlertsManagementProtocol(Protocol):
    """
    Protocol for alerts management and intelligent alerting.

    Single responsibility: Alert configuration, rules, and checking
    """

    async def setup_intelligent_alerts(
        self, channel_id: int, alert_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Setup intelligent alert system for a channel.

        Args:
            channel_id: Channel to setup alerts for
            alert_config: Alert configuration parameters

        Returns:
            Alert setup result and configuration
        """
        ...

    async def check_real_time_alerts(self, channel_id: int) -> dict[str, Any]:
        """
        Check for real-time alerts.

        Args:
            channel_id: Channel to check alerts for

        Returns:
            Active alerts and status
        """
        ...

    async def establish_alert_baselines(self, channel_id: int) -> dict[str, Any]:
        """
        Establish baseline metrics for alert thresholds.

        Args:
            channel_id: Channel to analyze

        Returns:
            Baseline metrics and thresholds
        """
        ...

    async def health_check(self) -> dict[str, Any]:
        """Health check for alerts management service"""
        ...


class CompetitiveIntelligenceProtocol(Protocol):
    """
    Protocol for competitive intelligence and market analysis.

    Single responsibility: Competitor analysis and market insights
    """

    async def generate_competitive_intelligence(
        self,
        channel_id: int,
        competitor_ids: list[int] | None = None,
        analysis_depth: str = "standard",
    ) -> dict[str, Any]:
        """
        Generate comprehensive competitive intelligence analysis.

        Args:
            channel_id: Channel to analyze
            competitor_ids: List of competitor channel IDs
            analysis_depth: Depth of analysis (quick, standard, deep)

        Returns:
            Competitive intelligence report
        """
        ...

    async def discover_competitor_channels(
        self, channel_id: int, max_competitors: int = 5
    ) -> list[dict[str, Any]]:
        """
        Discover competitor channels automatically.

        Args:
            channel_id: Channel to find competitors for
            max_competitors: Maximum number of competitors to identify

        Returns:
            List of competitor channel information
        """
        ...

    async def get_channel_profile(self, channel_id: int) -> dict[str, Any]:
        """
        Get comprehensive channel profile for analysis.

        Args:
            channel_id: Channel to profile

        Returns:
            Channel profile data
        """
        ...

    async def health_check(self) -> dict[str, Any]:
        """Health check for competitive intelligence service"""
        ...


class AlertsOrchestratorProtocol(Protocol):
    """
    Protocol for alerts orchestration service.

    Single responsibility: Service coordination and workflow orchestration
    """

    async def coordinate_live_monitoring(
        self, channel_id: int, monitoring_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Coordinate live monitoring across services.

        Args:
            channel_id: Channel to monitor
            monitoring_config: Monitoring configuration

        Returns:
            Coordinated monitoring result
        """
        ...

    async def coordinate_alert_analysis(
        self, channel_id: int, analysis_type: str = "comprehensive"
    ) -> dict[str, Any]:
        """
        Coordinate comprehensive alert analysis.

        Args:
            channel_id: Channel to analyze
            analysis_type: Type of analysis to perform

        Returns:
            Coordinated analysis result
        """
        ...

    async def coordinate_competitive_monitoring(
        self, channel_id: int, competitive_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Coordinate competitive monitoring workflow.

        Args:
            channel_id: Channel to monitor
            competitive_config: Competitive analysis configuration

        Returns:
            Coordinated competitive monitoring result
        """
        ...

    async def health_check(self) -> dict[str, Any]:
        """Health check for alerts orchestrator service"""
        ...


# Data models for type safety
class AlertConfig:
    """Alert configuration data model"""


class LiveMetrics:
    """Live metrics data model"""


class CompetitiveAnalysis:
    """Competitive analysis data model"""
