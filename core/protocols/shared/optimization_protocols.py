"""
Shared Optimization Protocols
============================

Protocol interfaces for optimization services to break cross-god-object dependencies.
Allows different optimization services to be injected without tight coupling.
"""

from datetime import datetime
from typing import Any, Protocol


class OptimizationProtocol(Protocol):
    """
    Protocol for optimization services.

    Breaks dependency between PredictiveIntelligenceService and AutonomousOptimizationService.
    Any optimization service can implement this protocol.
    """

    async def optimize_performance(
        self,
        channel_id: int,
        metrics: dict[str, Any],
        optimization_type: str = "general",
    ) -> dict[str, Any]:
        """
        Optimize performance for given metrics.

        Args:
            channel_id: Channel to optimize
            metrics: Current performance metrics
            optimization_type: Type of optimization (general, content, timing, etc.)

        Returns:
            Optimization recommendations and results
        """
        ...

    async def generate_recommendations(
        self, channel_id: int, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Generate optimization recommendations.

        Args:
            channel_id: Channel to analyze
            context: Analysis context

        Returns:
            List of optimization recommendations
        """
        ...

    async def health_check(self) -> dict[str, Any]:
        """
        Health check for optimization service.

        Returns:
            Health status information
        """
        ...


class PredictiveProtocol(Protocol):
    """
    Protocol for predictive intelligence services.

    Allows other services to depend on predictive capabilities without tight coupling.
    """

    async def analyze_with_context(
        self, prediction_request: dict[str, Any], context_types: list[Any] | None = None
    ) -> dict[str, Any]:
        """
        Analyze predictions with contextual intelligence.

        Args:
            prediction_request: Prediction request parameters
            context_types: Types of context to include

        Returns:
            Enhanced prediction with context
        """
        ...

    async def generate_temporal_intelligence(
        self, channel_id: int, time_range: dict[str, datetime]
    ) -> dict[str, Any]:
        """
        Generate temporal intelligence analysis.

        Args:
            channel_id: Channel to analyze
            time_range: Time range for analysis

        Returns:
            Temporal intelligence insights
        """
        ...

    async def health_check(self) -> dict[str, Any]:
        """Health check for predictive service"""
        ...


class AlertsProtocol(Protocol):
    """
    Protocol for alerts intelligence services.

    Allows other services to depend on alerting capabilities without tight coupling.
    """

    async def get_live_metrics(self, channel_id: int, hours: int = 6) -> dict[str, Any]:
        """
        Get live metrics for monitoring.

        Args:
            channel_id: Channel to monitor
            hours: Hours of data to retrieve

        Returns:
            Live metrics data
        """
        ...

    async def setup_alert_system(
        self, channel_id: int, alert_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Setup alert system for channel.

        Args:
            channel_id: Channel to setup alerts for
            alert_config: Alert configuration

        Returns:
            Alert system setup result
        """
        ...

    async def health_check(self) -> dict[str, Any]:
        """Health check for alerts service"""
        ...
