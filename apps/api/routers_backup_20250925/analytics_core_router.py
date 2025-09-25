"""
Analytics Core Router - Core Analytics Functionality
====================================================

Core analytics router providing essential metrics, dashboards, and data management.
Implements clean architecture patterns with proper domain separation.

Domain: Core analytics metrics, dashboards, trends, and data management
Path: /analytics/core/*
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

# Core services
from apps.api.di_analytics import get_analytics_fusion_service, get_cache
from core.services.analytics_fusion_service import AnalyticsFusionService
from core.di_container import container

# Performance monitoring
from apps.bot.database.performance import performance_timer

# Auth
from apps.api.middleware.auth import get_current_user

# Schemas
from apps.api.schemas.analytics import (
    OverviewResponse,
    PostListResponse, 
    SeriesResponse,
    ErrorResponse
)
from pydantic import BaseModel
from typing import Dict, List

# Auth
from apps.api.middleware.auth import get_current_user

logger = logging.getLogger(__name__)

# === MODELS ===

# Removed DataSourceHealth model - moved to analytics_insights_router.py

# Create router with core analytics prefix
router = APIRouter(
    prefix="/analytics/core",
    tags=["Analytics Core"],
    responses={
        404: {"model": ErrorResponse, "description": "Channel not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)

# === DASHBOARD FUNCTIONALITY (Consolidated) ===
# NOTE: System insights endpoints moved to analytics_insights_router.py
# - /capabilities → /analytics/insights/capabilities  
# - /reports/{channel_id} → /analytics/insights/reports/{channel_id}
# - /comparison/{channel_id} → /analytics/insights/comparison/{channel_id}

@router.get("/dashboard/{channel_id}")
async def get_core_dashboard(
    channel_id: int,
    period: int = Query(default=7, ge=1, le=365, description="Analysis period in days"),
    current_user: dict = Depends(get_current_user),
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 📋 Core Analytics Dashboard
    
    Comprehensive analytics dashboard combining:
    - Channel overview and metrics
    - Growth trends and engagement data  
    - Top performing posts
    - Summary insights
    
    **Features:**
    - Intelligent caching with ETag support
    - Clean Architecture dependency injection
    - Comprehensive metrics aggregation
    """
    try:
        with performance_timer("core_dashboard_generation"):
            # Get date range
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(days=period)
            
            # Fetch core analytics data
            overview_data = await service.get_channel_overview(channel_id, from_date, to_date)
            growth_data = await service.get_growth_metrics(channel_id, from_date, to_date)
            top_posts = await service.get_top_posts(channel_id, from_date, to_date, limit=10)
            
            # Generate dashboard response
            dashboard = {
                "channel_id": channel_id,
                "period": f"{period}d",
                "date_range": {
                    "from": from_date.isoformat(),
                    "to": to_date.isoformat()
                },
                "overview": {
                    "total_views": overview_data.get("total_views", 0),
                    "total_subscribers": overview_data.get("total_subscribers", 0),
                    "engagement_rate": overview_data.get("engagement_rate", 0.0),
                    "avg_post_views": overview_data.get("avg_post_views", 0)
                },
                "growth": {
                    "subscriber_growth": growth_data.get("subscriber_growth", 0),
                    "view_growth": growth_data.get("view_growth", 0),
                    "growth_rate": growth_data.get("growth_rate", 0.0)
                },
                "top_posts": top_posts,
                "generated_at": datetime.utcnow().isoformat(),
                "cache_info": {
                    "cached": False,
                    "ttl": 180
                }
            }
            
            return dashboard
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Core dashboard generation failed for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to generate core analytics dashboard"
        )

# === METRICS FUNCTIONALITY (Consolidated) ===

@router.get("/metrics/{channel_id}")
async def get_core_metrics(
    channel_id: int,
    period: int = Query(default=7, ge=1, le=90, description="Period in days"),
    metric_types: list[str] = Query(default=["views", "subscribers", "engagement"]),
    current_user: dict = Depends(get_current_user),
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
):
    """
    ## 📈 Core Channel Metrics
    
    Get consolidated metrics for a channel including:
    - View metrics and trends
    - Subscriber metrics and growth
    - Engagement rates and patterns
    """
    try:
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=period)
        
        metrics = {}
        
        if "views" in metric_types:
            metrics["views"] = await service.get_view_metrics(channel_id, from_date, to_date)
            
        if "subscribers" in metric_types:
            metrics["subscribers"] = await service.get_subscriber_metrics(channel_id, from_date, to_date)
            
        if "engagement" in metric_types:
            metrics["engagement"] = await service.get_engagement_metrics(channel_id, from_date, to_date)
            
        return {
            "channel_id": channel_id,
            "period": f"{period}d",
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Core metrics fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch core metrics")

# === OVERVIEW FUNCTIONALITY ===

@router.get("/overview/{channel_id}", response_model=OverviewResponse)
async def get_channel_overview(
    channel_id: int,
    request: Request,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """Get detailed channel overview with caching and ETag support"""
    try:
        # Generate cache key and ETag
        cache_params = {"channel_id": channel_id, "from": from_.isoformat(), "to": to_.isoformat()}
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("core_overview", cache_params, last_updated)
        
        # ETag support
        last_updated_str = last_updated.isoformat() if last_updated else ""
        etag = f'"{hashlib.sha256(f"{cache_key}:{last_updated_str}".encode()).hexdigest()}"'
        
        # Check If-None-Match header
        if_none_match = request.headers.get("if-none-match")
        if if_none_match and if_none_match == etag:
            return JSONResponse(status_code=304)
            
        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            response = JSONResponse(cached_data)
            response.headers["etag"] = etag
            response.headers["cache-control"] = "public, max-age=300"
            return response
            
        # Fetch fresh data
        overview_data = await service.get_channel_overview(channel_id, from_, to_)
        
        response_data = {
            "channel_id": channel_id,
            "overview": overview_data,
            "period": {
                "from": from_.isoformat(),
                "to": to_.isoformat()
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Cache the response
        await cache.set_json(cache_key, response_data, ttl_s=300)
        
        response = JSONResponse(response_data)
        response.headers["etag"] = etag
        response.headers["cache-control"] = "public, max-age=300"
        return response
        
    except Exception as e:
        logger.error(f"Channel overview failed for {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get channel overview")

# === TOP POSTS & SOURCES ===

@router.get("/channels/{channel_id}/top-posts")
async def get_channel_top_posts(
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

        response_data = {
            "data": posts_data,
            "meta": {
                "cache_hit": False,
                "total_posts": len(posts_data) if posts_data else 0,
                "channel_id": channel_id,
                "date_range": {
                    "from": from_.isoformat(),
                    "to": to_.isoformat()
                },
                "limit": limit
            }
        }

        # Cache the response
        await cache.set_json(cache_key, response_data, ttl_s=60)

        return response_data

    except Exception as e:
        logger.error(f"Error getting top posts for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to get top posts"
        )


@router.get("/channels/{channel_id}/sources")
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
        if kind not in ("mention", "forward"):
            raise HTTPException(status_code=400, detail="kind must be 'mention' or 'forward'")
        
        sources_data = await service.get_sources(channel_id, from_, to_, kind)

        response_data = {
            "data": sources_data,
            "meta": {
                "cache_hit": False,
                "channel_id": channel_id,
                "kind": kind,
                "date_range": {
                    "from": from_.isoformat(),
                    "to": to_.isoformat()
                },
                "total_sources": len(sources_data) if sources_data else 0
            }
        }

        # Cache the response
        await cache.set_json(cache_key, response_data, ttl_s=180)

        return response_data

    except Exception as e:
        logger.error(f"Error getting sources for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get channel sources",
        )

# === DATA MANAGEMENT ===

@router.post("/refresh/{channel_id}")
async def refresh_channel_data(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
):
    """Force refresh analytics data for a channel"""
    try:
        with performance_timer("core_data_refresh"):
            refresh_result = await service.refresh_channel_data(
                channel_id=channel_id,
                user_id=current_user["id"]
            )
            
            return {
                "channel_id": channel_id,
                "status": "refreshed",
                "records_updated": refresh_result.get("records_updated", 0),
                "last_refresh": datetime.utcnow().isoformat(),
                "next_auto_refresh": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                "metrics_summary": refresh_result.get("summary", {})
            }
            
    except Exception as e:
        logger.error(f"Data refresh failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh channel data")


# === CHANNEL GROWTH ANALYTICS ===

@router.get("/channels/{channel_id}/growth", response_model=SeriesResponse)
async def get_channel_growth(
    channel_id: int,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    window: str = Query(default="D", regex="^(D|H|W)$"),
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    Get channel growth time series data
    
    Provides subscriber growth, view growth, and engagement growth metrics
    over specified time periods with configurable time windows.
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
        cache_key = cache.generate_cache_key("growth", cache_params, last_updated)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Get fresh growth data
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


# === NOTES ===
# Insights functionality moved to analytics_insights_router.py:
# - /reports/{channel_id} → /analytics/insights/reports/{channel_id}  
# - /comparison/{channel_id} → /analytics/insights/comparison/{channel_id}