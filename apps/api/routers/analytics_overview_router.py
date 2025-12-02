"""
Analytics Overview Router
=========================

API endpoints for the comprehensive channel overview dashboard.
Provides TGStat-style metrics and charts.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from apps.api.middleware.auth import get_current_user
from apps.di.analytics_container import get_cache, get_database_pool

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Analytics - Overview"])


# ============================================================================
# Response Models
# ============================================================================


class SubscriberStatsResponse(BaseModel):
    """Subscriber statistics response"""

    total: int = Field(description="Total subscribers")
    today_change: int = Field(description="Change today (+/-)")
    week_change: int = Field(description="Change this week (+/-)")
    month_change: int = Field(description="Change this month (+/-)")
    growth_rate: float = Field(description="Growth rate percentage")


class PostsStatsResponse(BaseModel):
    """Posts statistics response"""

    total: int = Field(description="Total posts")
    today: int = Field(description="Posts today")
    week: int = Field(description="Posts this week")
    month: int = Field(description="Posts this month")
    avg_per_day: float = Field(description="Average posts per day")


class EngagementStatsResponse(BaseModel):
    """Engagement statistics response"""

    total_views: int = Field(description="Total views")
    total_reactions: int = Field(description="Total reactions")
    total_forwards: int = Field(description="Total forwards/shares")
    total_comments: int = Field(description="Total comments")
    avg_views_per_post: float = Field(description="Average views per post")
    avg_reactions_per_post: float = Field(description="Average reactions per post")
    engagement_rate: float = Field(description="Engagement rate percentage")
    err: float = Field(description="Engagement Rate Ratio")
    err_24h: float = Field(description="ERR for last 24 hours")


class ReachStatsResponse(BaseModel):
    """Reach statistics response"""

    avg_post_reach: int = Field(description="Average post reach")
    avg_ad_reach: int = Field(description="Average advertising reach")
    reach_12h: int = Field(description="Reach in last 12 hours")
    reach_24h: int = Field(description="Reach in last 24 hours")
    reach_48h: int = Field(description="Reach in last 48 hours")
    citation_index: float = Field(description="Citation index score")


class ChannelInfoResponse(BaseModel):
    """Channel information response"""

    id: int = Field(description="Channel ID")
    title: str = Field(description="Channel title")
    username: str | None = Field(description="Channel username")
    description: str | None = Field(description="Channel description")
    created_at: str | None = Field(description="Channel creation date")
    age_days: int = Field(description="Channel age in days")
    age_formatted: str = Field(description="Channel age formatted")
    is_active: bool = Field(description="Whether channel is active")


class DataPointResponse(BaseModel):
    """Single data point for charts"""

    date: str = Field(description="Date in ISO format")
    value: int = Field(description="Value for this date")


class ChannelOverviewResponse(BaseModel):
    """Complete channel overview response"""

    channel_info: ChannelInfoResponse
    subscribers: SubscriberStatsResponse
    posts: PostsStatsResponse
    engagement: EngagementStatsResponse
    reach: ReachStatsResponse
    views_history: list[DataPointResponse] = Field(description="Daily views for charts")
    posts_history: list[DataPointResponse] = Field(description="Daily posts for charts")
    generated_at: str = Field(description="When this data was generated")
    data_freshness: str = Field(description="Data freshness indicator")


# ============================================================================
# Endpoints
# ============================================================================


@router.get(
    "/dashboard/{channel_id}",
    response_model=ChannelOverviewResponse,
    summary="Get Channel Overview Dashboard",
    description="""
    Get comprehensive channel overview metrics for the dashboard.
    
    Returns TGStat-style metrics including:
    - **Subscribers**: Total count and growth
    - **Posts**: Count by period (today, week, month)
    - **Engagement**: Views, reactions, forwards, comments, ERR
    - **Reach**: Average reach, citation index
    - **Charts Data**: Daily views and posts history
    
    **Period options:**
    - `today` - Data from today only
    - `last_7_days` - Data from the last 7 days (default)
    - `last_30_days` - Data from the last 30 days
    - `last_90_days` - Data from the last 90 days
    - `all_time` - All historical data
    """,
)
async def get_channel_overview_dashboard(
    channel_id: int,
    period: str = "last_7_days",
    pool=Depends(get_database_pool),
    cache=Depends(get_cache),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get complete channel overview for dashboard"""
    try:
        logger.info(f"📊 Getting overview dashboard for channel {channel_id}, period={period}")

        # Validate period
        valid_periods = [
            "today",
            "last_7_days",
            "last_30_days",
            "last_90_days",
            "all_time",
        ]
        if period not in valid_periods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid period. Must be one of: {', '.join(valid_periods)}",
            )

        # Try cache first (5 minute TTL for dashboard)
        cache_key = f"analytics_overview:dashboard:{channel_id}:{period}"
        cached = await cache.get_json(cache_key)
        if cached:
            logger.info(f"📦 Returning cached dashboard for channel {channel_id}, period={period}")
            cached["data_freshness"] = "cached"
            return cached

        # Import here to avoid circular imports
        from core.services.analytics_fusion.overview import AnalyticsOverviewService

        # Create service and get metrics with period
        service = AnalyticsOverviewService(pool)
        metrics = await service.get_channel_overview(channel_id, period=period)

        # Convert to response format
        response_data = metrics.to_dict()

        # Cache the response
        await cache.set_json(cache_key, response_data, expire_seconds=300)

        logger.info(f"✅ Generated fresh dashboard for channel {channel_id}, period={period}")
        return response_data

    except Exception as e:
        logger.error(f"❌ Error getting overview dashboard for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get channel overview: {str(e)}")


@router.get(
    "/stats/{channel_id}",
    summary="Get Channel Quick Stats",
    description="Get quick channel statistics without chart data (lighter endpoint)",
)
async def get_channel_quick_stats(
    channel_id: int,
    pool=Depends(get_database_pool),
    cache=Depends(get_cache),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get quick channel statistics (without chart data)"""
    try:
        logger.info(f"📊 Getting quick stats for channel {channel_id}")

        # Try cache first (2 minute TTL for quick stats)
        cache_key = f"analytics_overview:quick_stats:{channel_id}"
        cached = await cache.get_json(cache_key)
        if cached:
            return cached

        from core.services.analytics_fusion.overview import AnalyticsOverviewService

        service = AnalyticsOverviewService(pool)
        metrics = await service.get_channel_overview(channel_id)

        # Return only stats without chart data
        response_data = {
            "channel_info": metrics.channel_info.to_dict(),
            "subscribers": metrics.subscribers.to_dict(),
            "posts": metrics.posts.to_dict(),
            "engagement": metrics.engagement.to_dict(),
            "reach": metrics.reach.to_dict(),
            "generated_at": metrics.generated_at.isoformat(),
        }

        # Cache the response
        await cache.set_json(cache_key, response_data, expire_seconds=120)

        return response_data

    except Exception as e:
        logger.error(f"❌ Error getting quick stats for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get channel stats: {str(e)}")


@router.get(
    "/charts/{channel_id}",
    summary="Get Channel Charts Data",
    description="Get chart data for views and posts history",
)
async def get_channel_charts(
    channel_id: int,
    days: int = 30,
    pool=Depends(get_database_pool),
    cache=Depends(get_cache),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get chart data for the channel"""
    try:
        logger.info(f"📈 Getting charts for channel {channel_id} ({days} days)")

        # Try cache first
        cache_key = f"analytics_overview:charts:{channel_id}:{days}"
        cached = await cache.get_json(cache_key)
        if cached:
            return cached

        from core.services.analytics_fusion.overview import AnalyticsOverviewService

        service = AnalyticsOverviewService(pool)

        # Get chart data
        async with pool.acquire() as conn:
            views_history = await service._get_views_history(conn, channel_id, days)
            posts_history = await service._get_posts_history(conn, channel_id, days)

        response_data = {
            "channel_id": channel_id,
            "days": days,
            "views_history": views_history,
            "posts_history": posts_history,
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Cache for 10 minutes
        await cache.set_json(cache_key, response_data, expire_seconds=600)

        return response_data

    except Exception as e:
        logger.error(f"❌ Error getting charts for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chart data: {str(e)}")


# ============================================================================
# Telegram Statistics API Endpoints (Phase 3)
# ============================================================================


class LanguageStatsResponse(BaseModel):
    """Language distribution statistics"""

    language_code: str = Field(description="ISO language code")
    language_name: str = Field(description="Human-readable language name")
    percentage: float = Field(description="Percentage of subscribers")


class CountryStatsResponse(BaseModel):
    """Country distribution statistics"""

    country_code: str = Field(description="ISO country code")
    country_name: str = Field(description="Human-readable country name")
    percentage: float = Field(description="Percentage of subscribers")


class DeviceStatsResponse(BaseModel):
    """Device type distribution statistics"""

    device_type: str = Field(description="Device type (android, ios, desktop, web)")
    percentage: float = Field(description="Percentage of subscribers")


class TrafficSourceResponse(BaseModel):
    """Traffic source statistics"""

    source_type: str = Field(
        description="Source category (search, mentions, links, other_channels, direct)"
    )
    source_name: str = Field(description="Source name")
    subscribers_count: int = Field(description="Number of subscribers from this source")
    percentage: float = Field(description="Percentage of total subscribers")


class GrowthPointResponse(BaseModel):
    """Single point in growth chart"""

    date: str = Field(description="Date in ISO format")
    subscribers: int = Field(description="Total subscribers on this date")
    joined: int = Field(description="Number of new subscribers")
    left: int = Field(description="Number of subscribers who left")


class InteractionStatsResponse(BaseModel):
    """Interaction statistics per post"""

    views_per_post: float = Field(description="Average views per post")
    shares_per_post: float = Field(description="Average shares per post")
    reactions_per_post: float = Field(description="Average reactions per post")
    comments_per_post: float = Field(description="Average comments per post")


class TelegramStatsResponse(BaseModel):
    """Complete Telegram Statistics API response"""

    channel_id: int = Field(description="Channel ID")
    is_available: bool = Field(description="Whether stats are available for this channel")
    error_message: str | None = Field(description="Error message if stats unavailable")

    # Basic stats from Telegram API
    subscriber_count: int = Field(description="Current subscriber count")
    mean_view_count: int = Field(description="Average views per post")
    mean_share_count: int = Field(description="Average shares per post")
    mean_reaction_count: int = Field(description="Average reactions per post")

    # Demographics
    languages: list[LanguageStatsResponse] = Field(description="Language distribution")
    countries: list[CountryStatsResponse] = Field(description="Country distribution")
    devices: list[DeviceStatsResponse] = Field(description="Device type distribution")

    # Traffic sources
    traffic_sources: list[TrafficSourceResponse] = Field(description="Where subscribers come from")

    # Growth data
    growth_history: list[GrowthPointResponse] = Field(description="Historical growth data")
    followers_growth_rate: float = Field(description="Growth rate percentage")

    # Interactions
    interactions: InteractionStatsResponse | None = Field(description="Interaction statistics")

    # Metadata
    fetched_at: str = Field(description="When this data was fetched")
    period_start: str | None = Field(description="Start of statistics period")
    period_end: str | None = Field(description="End of statistics period")


@router.get(
    "/telegram-stats/{channel_id}",
    response_model=TelegramStatsResponse,
    summary="Get Telegram Statistics API Data",
    description="""
    Get channel statistics from Telegram's official Statistics API.
    
    **Requirements:**
    - Channel must have 500+ subscribers
    - User must be an admin of the channel
    - MTProto connection must be active
    
    **Returns:**
    - **Demographics**: Language, country distribution
    - **Traffic Sources**: Where subscribers come from
    - **Growth Data**: Historical subscriber growth
    - **Engagement**: Average views, shares, reactions per post
    
    **Note:** This data comes directly from Telegram's Statistics API,
    not from our collected metrics. It may take a few seconds to fetch.
    """,
)
async def get_telegram_stats(
    channel_id: int,
    pool=Depends(get_database_pool),
    cache=Depends(get_cache),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get Telegram Statistics API data for a channel"""
    try:
        logger.info(f"📊 Getting Telegram stats for channel {channel_id}")

        # Try cache first (10 minute TTL - Telegram stats don't change frequently)
        cache_key = f"analytics_overview:telegram_stats:{channel_id}"
        cached = await cache.get_json(cache_key)
        if cached:
            logger.info(f"📦 Returning cached Telegram stats for channel {channel_id}")
            return cached

        # Get user_id from the channel
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        # Import and create the service
        from apps.di import get_container
        from core.services.analytics_fusion.overview import TelegramStatsService

        container = get_container()

        # Get the MTProto service from the container
        user_mtproto_service = await container.mtproto.user_mtproto_service()

        # Create the stats service
        stats_service = TelegramStatsService(user_mtproto_service)

        # Fetch the stats
        stats = await stats_service.get_channel_stats(user_id, channel_id)

        # Convert to response format
        response_data = stats.to_dict()

        # Cache successful responses for 10 minutes
        if stats.is_available:
            await cache.set_json(cache_key, response_data, expire_seconds=600)

        logger.info(
            f"✅ Fetched Telegram stats for channel {channel_id}: available={stats.is_available}"
        )
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting Telegram stats for channel {channel_id}: {e}")
        # Return a response indicating stats are unavailable
        return {
            "channel_id": channel_id,
            "is_available": False,
            "error_message": f"Failed to fetch Telegram statistics: {str(e)}",
            "subscriber_count": 0,
            "mean_view_count": 0,
            "mean_share_count": 0,
            "mean_reaction_count": 0,
            "languages": [],
            "countries": [],
            "devices": [],
            "traffic_sources": [],
            "growth_history": [],
            "followers_growth_rate": 0.0,
            "interactions": None,
            "fetched_at": datetime.utcnow().isoformat(),
            "period_start": None,
            "period_end": None,
        }
