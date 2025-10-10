"""
Shared Clients - Framework-Independent HTTP/Service Clients

Clients in this module are framework-independent and can be used
by both API and Bot layers. They handle external service communication.

Moved from apps.bot.clients as part of Phase 1.5 to break cross-dependencies.
"""

from apps.shared.clients.analytics_client import (
    AnalyticsClient,
    AnalyticsClientError,
    AnalyticsOverview,
    AnalyticsResponse,
    GrowthData,
    GrowthResponse,
    OverviewResponse,
    ReachData,
    ReachResponse,
    SourceData,
    SourcesResponse,
    TopPost,
    TopPostsResponse,
    TrendingData,
    TrendingResponse,
)

__all__ = [
    "AnalyticsClient",
    "AnalyticsClientError",
    "AnalyticsOverview",
    "AnalyticsResponse",
    "GrowthData",
    "GrowthResponse",
    "OverviewResponse",
    "ReachData",
    "ReachResponse",
    "SourceData",
    "SourcesResponse",
    "TopPost",
    "TopPostsResponse",
    "TrendingData",
    "TrendingResponse",
]
