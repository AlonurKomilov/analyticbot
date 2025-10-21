"""
Core statistical analysis endpoints.
Handles historical metrics, trends, and growth analysis.
"""

import hashlib
import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse

# Services - NEW DI
from apps.api.di_analytics import get_analytics_fusion_service, get_cache

# Auth
from apps.api.middleware.auth import get_current_user

# Schemas
from apps.api.schemas.analytics import OverviewResponse, SeriesResponse
from apps.shared.performance import performance_timer
from core.protocols import AnalyticsFusionServiceProtocol

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/statistics/core", tags=["statistics-core"])

# === CORE STATISTICAL ENDPOINTS ===


@router.get("/overview/{channel_id}", response_model=OverviewResponse)
async def get_channel_overview(
    channel_id: int,
    request: Request,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📊 Historical Channel Overview

    Get detailed channel overview with historical metrics including:
    - Historical view counts and growth trends
    - Engagement statistics over time
    - Subscriber growth patterns
    - Content performance analytics
    """
    try:
        # Generate cache key and ETag
        cache_params = {"channel_id": channel_id, "from": from_.isoformat(), "to": to_.isoformat()}
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("core_overview", cache_params, last_updated)

        # ETag support for caching
        last_updated_str = last_updated.isoformat() if last_updated else ""
        etag = f'"{hashlib.sha256(f"{cache_key}:{last_updated_str}".encode()).hexdigest()}"'

        # Check If-None-Match header
        if_none_match = request.headers.get("if-none-match")
        if if_none_match and if_none_match == etag:
            return JSONResponse(content={}, status_code=304)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            response = JSONResponse(cached_data)
            response.headers["etag"] = etag
            response.headers["cache-control"] = "public, max-age=300"
            return response

        # Fetch fresh historical data
        overview_data = await service.get_channel_overview(channel_id, from_, to_)

        response_data = {
            "channel_id": channel_id,
            "overview": overview_data,
            "period": {
                "from": from_.isoformat(),
                "to": to_.isoformat(),
            },
            "statistics_type": "historical_overview",
            "last_updated": last_updated_str,
            "cache_key": cache_key,
        }

        # Cache the response (30 minutes for historical data)
        await cache.set_json(cache_key, response_data, expire_seconds=1800)

        response = JSONResponse(response_data)
        response.headers["etag"] = etag
        response.headers["cache-control"] = "public, max-age=300"
        return response

    except Exception as e:
        logger.error(f"Historical overview fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch historical overview")


@router.get("/growth/{channel_id}", response_model=SeriesResponse)
async def get_channel_growth_statistics(
    channel_id: int,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    window: str = Query(
        default="D", regex="^(D|H|W)$", description="Time window (D=Daily, W=Weekly, H=Hourly)"
    ),
    service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📈 Growth Statistics Time Series

    Get historical growth statistics including:
    - Subscriber growth trends
    - View growth patterns
    - Engagement growth metrics
    - Configurable time windows (Daily/Weekly/Hourly)
    """
    try:
        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "from": from_.isoformat(),
            "to": to_.isoformat(),
            "window": window,
        }
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("growth_statistics", cache_params, last_updated)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Fetch growth time series
        with performance_timer("growth_statistics_fetch"):
            # Convert window string to appropriate integer
            window_days = {"D": 1, "W": 7, "H": 1}.get(window, 1)
            growth_data = await service.get_growth_time_series(channel_id, from_, to_, window_days)

        response_data = {
            "channel_id": channel_id,
            "data": growth_data,
            "meta": {
                "from": from_.isoformat(),
                "to": to_.isoformat(),
                "window": window,
                "statistics_type": "growth_trends",
                "cache_hit": False,
                "last_updated": last_updated.isoformat() if last_updated else None,
            },
        }

        # Cache for 20 minutes (historical data)
        await cache.set_json(cache_key, response_data, expire_seconds=1200)

        return response_data

    except Exception as e:
        logger.error(f"Growth statistics fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch growth statistics")


@router.get("/metrics/{channel_id}")
async def get_historical_metrics(
    channel_id: int,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📊 Historical Metrics Analysis

    Get comprehensive historical metrics including:
    - View count trends over time
    - Engagement rate evolution
    - Subscriber count changes
    - Content performance history
    """
    try:
        # Generate cache key
        cache_params = {"channel_id": channel_id, "from": from_.isoformat(), "to": to_.isoformat()}
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("historical_metrics", cache_params, last_updated)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            return cached_data

        # Fetch historical metrics
        with performance_timer("historical_metrics_fetch"):
            metrics_data = await service.get_historical_metrics(channel_id, from_, to_)

        response_data = {
            "channel_id": channel_id,
            "metrics": metrics_data,
            "period": {
                "from": from_.isoformat(),
                "to": to_.isoformat(),
            },
            "analysis_type": "historical_trends",
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Cache for 25 minutes
        await cache.set_json(cache_key, response_data, expire_seconds=1500)

        return response_data

    except Exception as e:
        logger.error(f"Historical metrics fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch historical metrics")


@router.get("/top-posts/{channel_id}")
async def get_historical_top_posts(
    channel_id: int,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    limit: int = Query(10, ge=1, le=50, description="Number of top posts to return"),
    service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🏆 Historical Top Posts Analysis

    Get historical top-performing posts with statistical analysis:
    - Posts ranked by historical performance
    - Engagement metrics over time
    - Content type performance analysis
    - Historical trending patterns
    """
    try:
        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "from": from_.isoformat(),
            "to": to_.isoformat(),
            "limit": limit,
        }
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("historical_top_posts", cache_params, last_updated)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            return cached_data

        # Fetch top posts with historical context
        with performance_timer("historical_top_posts_fetch"):
            top_posts = await service.get_top_posts(channel_id, from_, to_, limit)

        response_data = {
            "channel_id": channel_id,
            "top_posts": top_posts,
            "period": {
                "from": from_.isoformat(),
                "to": to_.isoformat(),
            },
            "limit": limit,
            "analysis_type": "historical_performance",
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Cache for 30 minutes
        await cache.set_json(cache_key, response_data, expire_seconds=1800)

        return response_data

    except Exception as e:
        logger.error(f"Historical top posts fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch historical top posts")


@router.get("/sources/{channel_id}")
async def get_traffic_sources_statistics(
    channel_id: int,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🚦 Traffic Sources Statistics

    Get historical traffic source analysis:
    - Source attribution over time
    - Channel performance by source
    - Historical source trends
    - Source effectiveness metrics
    """
    try:
        # Generate cache key
        cache_params = {"channel_id": channel_id, "from": from_.isoformat(), "to": to_.isoformat()}
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("traffic_sources_stats", cache_params, last_updated)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            return cached_data

        # Fetch traffic sources statistics
        with performance_timer("traffic_sources_stats_fetch"):
            sources_data = await service.get_traffic_sources(channel_id, from_, to_)

        response_data = {
            "channel_id": channel_id,
            "sources": sources_data,
            "period": {
                "from": from_.isoformat(),
                "to": to_.isoformat(),
            },
            "analysis_type": "traffic_source_statistics",
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Cache for 35 minutes
        await cache.set_json(cache_key, response_data, expire_seconds=2100)

        return response_data

    except Exception as e:
        logger.error(f"Traffic sources statistics fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch traffic sources statistics")
