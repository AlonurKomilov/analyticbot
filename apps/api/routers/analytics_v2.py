"""
Analytics V2 Router - Unified Analytics Fusion API
Combines MTProto data with existing analytics in stable API v2 surface
"""

import hashlib
import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.di_analytics_v2 import get_analytics_fusion_service, get_cache
from apps.api.schemas.analytics_v2 import (
    EdgeListResponse,
    ErrorResponse,
    HealthResponse,
    OverviewResponse,
    PostListResponse,
    SeriesResponse,
)
from core.services.analytics_fusion_service import AnalyticsFusionService

logger = logging.getLogger(__name__)

# Create router with v2 prefix
router = APIRouter(
    prefix="/analytics/v2",
    tags=["Analytics V2"],
    responses={
        404: {"model": ErrorResponse, "description": "Channel not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)


# Dependencies - now imported from DI module
# (Placeholder implementations removed)


# Request models for new endpoints
class ChannelDataRequest(BaseModel):
    channel_id: str
    include_real_time: bool = True
    format: str = "detailed"


class PerformanceMetricsRequest(BaseModel):
    channels: list[str]
    period: str = "30d"


# Route implementations


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for analytics fusion service"""
    return HealthResponse(status="healthy", service="analytics-fusion", version="2.0.0")


@router.post("/channel-data")
async def get_channel_data(
    request: ChannelDataRequest,
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """Get real-time channel analytics data with configurable format"""
    try:
        channel_id = int(request.channel_id)

        # Generate cache key for real-time data (shorter TTL)
        cache_params = {
            "channel_id": channel_id,
            "format": request.format,
            "real_time": request.include_real_time,
        }
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("channel-data", cache_params, last_updated)

        # Try cache first (shorter TTL for real-time data)
        cached_data = await cache.get_json(cache_key)
        if cached_data and not request.include_real_time:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Get fresh data with real-time components
        from datetime import datetime, timedelta

        # Default to last 30 days for comprehensive data
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=30)

        # Get overview and growth data
        overview_data = await service.get_overview(channel_id, from_date, to_date)
        growth_data = await service.get_growth(channel_id, from_date, to_date, "D")

        # Enhance with real-time components if requested
        response_data = {
            "channel_id": request.channel_id,
            "timestamp": datetime.utcnow().isoformat(),
            "overview": overview_data,
            "growth": growth_data,
            "real_time": request.include_real_time,
            "format": request.format,
            "connection_status": "connected",
            "meta": {
                "cache_hit": False,
                "last_updated": last_updated.isoformat() if last_updated else None,
                "data_freshness": ("real_time" if request.include_real_time else "cached"),
            },
        }

        # Cache the response (shorter TTL for real-time data)
        cache_ttl = 30 if request.include_real_time else 300
        await cache.set_json(cache_key, response_data, ttl_s=cache_ttl)

        return response_data

    except Exception as e:
        logger.error(f"Error getting channel data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get channel data",
        )


@router.post("/metrics/performance")
async def get_performance_metrics(
    request: PerformanceMetricsRequest,
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """Get performance metrics for specified channels"""
    try:
        # Parse period (e.g., "30d" -> 30 days)
        period_days = 30
        if request.period.endswith("d"):
            period_days = int(request.period[:-1])

        # Generate cache key
        cache_params = {
            "channels": request.channels,
            "period": request.period,
        }
        cache_key = cache.generate_cache_key("performance-metrics", cache_params)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Get performance data for each channel
        from datetime import datetime, timedelta

        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=period_days)

        channels_metrics = []
        for channel_id_str in request.channels:
            try:
                channel_id = int(channel_id_str)

                # Get overview and reach data for performance calculation
                overview_data = await service.get_overview(channel_id, from_date, to_date)
                reach_data = await service.get_reach(channel_id, from_date, to_date)

                # Calculate performance score
                total_views = overview_data.get("total_views", 0)
                avg_reach = reach_data.get("avg_reach", 0)

                # Simple performance scoring algorithm
                performance_score = min(100, max(0, (total_views / 1000) + (avg_reach / 100)))

                channel_metrics = {
                    "channel_id": channel_id_str,
                    "total_views": total_views,
                    "avg_reach": avg_reach,
                    "performance_score": round(performance_score, 1),
                    "period": request.period,
                    "growth_rate": overview_data.get("growth_rate", 0),
                    "engagement_rate": overview_data.get("engagement_rate", 0),
                }

                channels_metrics.append(channel_metrics)

            except (ValueError, Exception) as e:
                logger.warning(f"Failed to get metrics for channel {channel_id_str}: {e}")
                continue

        response_data = {
            "channels": channels_metrics,
            "period": request.period,
            "timestamp": datetime.utcnow().isoformat(),
            "performance_score": (
                sum(m["performance_score"] for m in channels_metrics) / len(channels_metrics)
                if channels_metrics
                else 0
            ),
            "meta": {
                "cache_hit": False,
                "channels_processed": len(channels_metrics),
                "channels_requested": len(request.channels),
            },
        }

        # Cache the response
        await cache.set_json(cache_key, response_data, ttl_s=300)

        return response_data

    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance metrics",
        )


@router.get("/trends/posts/top")
async def get_top_posts_trends(
    period: int = Query(default=7, ge=1, le=30, description="Period in days"),
    limit: int = Query(default=10, ge=1, le=50, description="Number of top posts"),
    channel_id: int | None = Query(default=None, description="Specific channel ID"),
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """Get trending top posts across channels or for a specific channel"""
    try:
        # Generate cache key
        cache_params = {
            "period": period,
            "limit": limit,
            "channel_id": channel_id,
        }
        cache_key = cache.generate_cache_key("trends-top-posts", cache_params)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Get trending posts data
        from datetime import datetime, timedelta

        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=period)

        if channel_id:
            # Get top posts for specific channel
            posts_data = await service.get_top_posts(channel_id, from_date, to_date, limit)
            trends_data = posts_data
        else:
            # For now, return sample trending data across all channels
            # In a real implementation, this would aggregate across multiple channels
            trends_data = [
                {
                    "post_id": f"post_{i}",
                    "channel_id": f"channel_{i % 3 + 1}",
                    "title": f"Trending Post #{i}",
                    "views": 10000 - (i * 500),
                    "engagement_rate": round(5.0 - (i * 0.2), 1),
                    "trend_score": round(100 - (i * 5), 1),
                    "publish_date": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                }
                for i in range(1, limit + 1)
            ]

        response_data = {
            "trends": trends_data,
            "period": f"{period}d",
            "limit": limit,
            "channel_id": channel_id,
            "timestamp": datetime.utcnow().isoformat(),
            "meta": {
                "cache_hit": False,
                "total_posts": len(trends_data),
                "date_range": {
                    "from": from_date.isoformat(),
                    "to": to_date.isoformat(),
                },
            },
        }

        # Cache the response
        await cache.set_json(cache_key, response_data, ttl_s=180)

        return response_data

    except Exception as e:
        logger.error(f"Error getting trends top posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trending posts",
        )


@router.get("/channels/{channel_id}/overview", response_model=OverviewResponse)
async def get_channel_overview(
    channel_id: int,
    request: Request,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """Get channel overview analytics"""
    try:
        # Generate cache key and ETag
        cache_params = {
            "channel_id": channel_id,
            "from": from_.isoformat(),
            "to": to_.isoformat(),
        }
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("overview", cache_params, last_updated)
        last_updated_str = last_updated.isoformat() if last_updated else ""
        etag = (
            f'"{hashlib.sha256(f"{cache_key}:{last_updated_str}".encode()).hexdigest()}"'
            if last_updated
            else None
        )

        # Check If-None-Match header for 304 response
        if_none_match = request.headers.get("if-none-match")
        if etag and if_none_match == etag:
            return Response(
                status_code=304,
                headers={"Cache-Control": "public, max-age=60", "ETag": etag},
            )

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
        # Create proper headers dict without None values
        headers = {"Cache-Control": "public, max-age=60"}
        if etag:
            headers["ETag"] = etag

        return JSONResponse(content=cached_data, headers=headers)  # Get fresh data
        overview_data = await service.get_overview(channel_id, from_, to_)

        response_data = OverviewResponse(data=overview_data)  # type: ignore
        response_dict = response_data.dict()

        # Cache the response
        await cache.set_json(cache_key, response_dict, ttl_s=120)

        # Return with cache headers
        # Create proper headers dict without None values
        headers = {"Cache-Control": "public, max-age=60"}
        if etag:
            headers["ETag"] = etag

        return JSONResponse(content=response_dict, headers=headers)

    except Exception as e:
        logger.error(f"Error getting overview for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get channel overview",
        )


@router.get("/channels/{channel_id}/growth", response_model=SeriesResponse)
async def get_channel_growth(
    channel_id: int,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    window: str = Query(default="D", regex="^(D|H|W)$"),
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """Get channel growth time series"""
    try:
        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "from": from_.isoformat(),
            "to": to_.isoformat(),
            "window": window,
        }
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("growth", cache_params, last_updated)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Get fresh data
        growth_data = await service.get_growth(channel_id, from_, to_, window)

        response_data = SeriesResponse(data=growth_data)  # type: ignore
        response_dict = response_data.dict()

        # Cache the response
        await cache.set_json(cache_key, response_dict, ttl_s=120)

        return response_data

    except Exception as e:
        logger.error(f"Error getting growth for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get channel growth data",
        )


@router.get("/channels/{channel_id}/reach", response_model=SeriesResponse)
async def get_channel_reach(
    channel_id: int,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """Get channel reach time series (avg views per post)"""
    try:
        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "from": from_.isoformat(),
            "to": to_.isoformat(),
        }
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("reach", cache_params, last_updated)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Get fresh data
        reach_data = await service.get_reach(channel_id, from_, to_)

        response_data = SeriesResponse(data=reach_data)  # type: ignore
        response_dict = response_data.dict()

        # Cache the response
        await cache.set_json(cache_key, response_dict, ttl_s=90)

        return response_data

    except Exception as e:
        logger.error(f"Error getting reach for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get channel reach data",
        )


@router.get("/channels/{channel_id}/top-posts", response_model=PostListResponse)
async def get_top_posts(
    channel_id: int,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    limit: int = Query(default=10, ge=1, le=50),
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """Get top posts by views for the channel"""
    try:
        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "from": from_.isoformat(),
            "to": to_.isoformat(),
            "limit": limit,
        }
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("top-posts", cache_params, last_updated)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Get fresh data
        posts_data = await service.get_top_posts(channel_id, from_, to_, limit)

        response_data = PostListResponse(data=posts_data)  # type: ignore
        response_dict = response_data.dict()

        # Cache the response
        await cache.set_json(cache_key, response_dict, ttl_s=60)

        return response_data

    except Exception as e:
        logger.error(f"Error getting top posts for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get top posts",
        )


@router.get("/channels/{channel_id}/sources", response_model=EdgeListResponse)
async def get_channel_sources(
    channel_id: int,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    kind: str = Query(..., regex="^(mention|forward)$"),
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """Get traffic sources (mentions or forwards) for the channel"""
    try:
        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "from": from_.isoformat(),
            "to": to_.isoformat(),
            "kind": kind,
        }
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("sources", cache_params, last_updated)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Get fresh data
        # Validate kind parameter
        if kind not in ("mention", "forward"):
            raise HTTPException(status_code=400, detail="kind must be 'mention' or 'forward'")

        sources_data = await service.get_sources(channel_id, from_, to_, kind)  # type: ignore

        response_data = EdgeListResponse(data=sources_data)  # type: ignore
        response_dict = response_data.dict()

        # Cache the response
        await cache.set_json(cache_key, response_dict, ttl_s=180)

        return response_data

    except Exception as e:
        logger.error(f"Error getting sources for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get channel sources",
        )


@router.get("/channels/{channel_id}/trending", response_model=PostListResponse)
async def get_trending_posts(
    channel_id: int,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    window_hours: int = Query(default=48, ge=1, le=168),
    method: str = Query(default="zscore", regex="^(zscore|ewma)$"),
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """Get trending posts using statistical analysis"""
    try:
        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "from": from_.isoformat(),
            "to": to_.isoformat(),
            "window_hours": window_hours,
            "method": method,
        }
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("trending", cache_params, last_updated)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Get fresh data
        trending_data = await service.get_trending(channel_id, from_, to_, method, window_hours)

        response_data = PostListResponse(data=trending_data)  # type: ignore
        response_dict = response_data.dict()

        # Cache the response
        await cache.set_json(cache_key, response_dict, ttl_s=60)

        return response_data

    except Exception as e:
        logger.error(f"Error getting trending posts for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trending posts",
        )


# Note: Exception handlers should be added to the main FastAPI app, not APIRouter
# These have been moved to apps.api.main for proper error handling
