"""
Analytics Overview Service
==========================

Provides comprehensive channel overview metrics similar to TGStat dashboard.
Aggregates data from posts, post_metrics, and channels tables.
Also integrates with Telegram Statistics API for demographics and traffic data.
"""

from .overview_service import AnalyticsOverviewService
from .overview_models import (
    ChannelOverviewMetrics,
    SubscriberStats,
    PostsStats,
    EngagementStats,
    ReachStats,
    ChannelInfo,
)
from .telegram_stats_service import (
    TelegramStatsService,
    TelegramChannelStats,
    LanguageStats,
    CountryStats,
    DeviceStats,
    TrafficSource,
    GrowthPoint,
    InteractionStats,
)

__all__ = [
    "AnalyticsOverviewService",
    "ChannelOverviewMetrics",
    "SubscriberStats",
    "PostsStats",
    "EngagementStats",
    "ReachStats",
    "ChannelInfo",
    # Telegram Stats API
    "TelegramStatsService",
    "TelegramChannelStats",
    "LanguageStats",
    "CountryStats",
    "DeviceStats",
    "TrafficSource",
    "GrowthPoint",
    "InteractionStats",
]
