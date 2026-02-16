"""
Analytics Overview Service
==========================

Provides comprehensive channel overview metrics similar to TGStat dashboard.
Aggregates data from posts, post_metrics, and channels tables.
Also integrates with Telegram Statistics API for demographics and traffic data.
"""

from .overview_models import (
    ChannelInfo,
    ChannelOverviewMetrics,
    EngagementStats,
    PostsStats,
    ReachStats,
    SubscriberStats,
)
from .overview_service import AnalyticsOverviewService
from .telegram_stats_service import (
    CountryStats,
    DeviceStats,
    GrowthPoint,
    InteractionStats,
    LanguageStats,
    TelegramChannelStats,
    TelegramStatsService,
    TrafficSource,
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
