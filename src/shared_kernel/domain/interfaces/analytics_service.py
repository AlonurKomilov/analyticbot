"""
AnalyticsService Interface - Public API for analytics module
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class AnalyticsService(Protocol):
    """AnalyticsService public interface"""

    async def get_channel_analytics(self, channel_id: int, date_range: tuple) -> dict:
        """get_channel_analytics operation"""
        ...

    async def get_engagement_metrics(self, channel_id: int) -> dict:
        """get_engagement_metrics operation"""
        ...

    async def generate_analytics_report(self, config: dict) -> dict:
        """generate_analytics_report operation"""
        ...

    async def get_growth_insights(self, channel_id: int) -> dict:
        """get_growth_insights operation"""
        ...
