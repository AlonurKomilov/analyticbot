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
    prefix="/api/v2/analytics",
    tags=["analytics-v2"],
    responses={
        404: {"model": ErrorResponse, "description": "Channel not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)


# Dependencies - now imported from DI module
# (Placeholder implementations removed)


# Route implementations


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for analytics fusion service"""
    return HealthResponse(status="healthy", service="analytics-fusion", version="2.0.0")


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
        cache_params = {"channel_id": channel_id, "from": from_.isoformat(), "to": to_.isoformat()}
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("overview", cache_params, last_updated)
        etag = (
            f'"{hashlib.sha1(f"{cache_key}:{last_updated}".encode()).hexdigest()}"'
            if last_updated
            else None
        )

        # Check If-None-Match header for 304 response
        if_none_match = request.headers.get("if-none-match")
        if etag and if_none_match == etag:
            return Response(
                status_code=304, headers={"Cache-Control": "public, max-age=60", "ETag": etag}
            )

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return JSONResponse(
                content=cached_data, headers={"Cache-Control": "public, max-age=60", "ETag": etag}
            )

        # Get fresh data
        overview_data = await service.get_overview(channel_id, from_, to_)

        response_data = OverviewResponse(data=overview_data)
        response_dict = response_data.dict()

        # Cache the response
        await cache.set_json(cache_key, response_dict, ttl_s=120)

        # Return with cache headers
        return JSONResponse(
            content=response_dict, headers={"Cache-Control": "public, max-age=60", "ETag": etag}
        )

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

        response_data = SeriesResponse(data=growth_data)
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
        cache_params = {"channel_id": channel_id, "from": from_.isoformat(), "to": to_.isoformat()}
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("reach", cache_params, last_updated)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Get fresh data
        reach_data = await service.get_reach(channel_id, from_, to_)

        response_data = SeriesResponse(data=reach_data)
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

        response_data = PostListResponse(data=posts_data)
        response_dict = response_data.dict()

        # Cache the response
        await cache.set_json(cache_key, response_dict, ttl_s=60)

        return response_data

    except Exception as e:
        logger.error(f"Error getting top posts for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get top posts"
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
        sources_data = await service.get_sources(channel_id, from_, to_, kind)

        response_data = EdgeListResponse(data=sources_data)
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

        response_data = PostListResponse(data=trending_data)
        response_dict = response_data.dict()

        # Cache the response
        await cache.set_json(cache_key, response_dict, ttl_s=60)

        return response_data

    except Exception as e:
        logger.error(f"Error getting trending posts for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get trending posts"
        )


# Note: Exception handlers should be added to the main FastAPI app, not APIRouter
# These have been moved to apps.api.main for proper error handling
