"""
Analytics Adapter Protocol
===========================

Defines the contract for analytics data source adapters.
This is a core protocol - implementations belong in infra layer.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class AnalyticsAdapter(ABC):
    """
    Abstract base class for analytics data adapters

    Infrastructure implementations:
    - infra.adapters.analytics.telegram_adapter
    - infra.adapters.analytics.mock_adapter
    """

    @abstractmethod
    def get_adapter_name(self) -> str:
        """Return the adapter name"""
        pass

    @abstractmethod
    async def get_channel_analytics(
        self, channel_id: str, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Get analytics data for a specific channel"""
        pass

    @abstractmethod
    async def get_post_analytics(self, post_id: str, channel_id: str) -> dict[str, Any]:
        """Get analytics data for a specific post"""
        pass

    @abstractmethod
    async def get_audience_demographics(self, channel_id: str) -> dict[str, Any]:
        """Get audience demographics for a channel"""
        pass

    @abstractmethod
    async def get_engagement_metrics(
        self, channel_id: str, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Get engagement metrics for a date range"""
        pass

    @abstractmethod
    async def get_growth_metrics(
        self, channel_id: str, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Get growth metrics for a date range"""
        pass

    @abstractmethod
    async def get_best_posting_times(self, channel_id: str) -> dict[str, Any]:
        """Get best posting times for a channel"""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check if the analytics adapter is healthy"""
        pass

    @abstractmethod
    async def close(self):
        """Close adapter and clean up resources"""
        pass
