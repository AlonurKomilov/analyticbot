"""
Analytics Insights Router - Advanced Analytics Intelligence
==========================================================

Handles advanced analytics insights, reports, and system comparisons.
Consolidates insight-related functionality from legacy routers.

Domain: Analytics insights, reports, capabilities analysis, system comparisons
Path: /analytics/insights/*
"""

import logging
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

# Core services
from apps.api.di_analytics import get_analytics_fusion_service, get_cache

# Auth
from apps.api.middleware.auth import get_current_user
from apps.api.schemas.analytics import PostListResponse
from core.services.analytics_fusion_service import AnalyticsFusionService

logger = logging.getLogger(__name__)

# === MODELS ===


class DataSourceHealth(BaseModel):
    """Health status of both analytics systems"""

    v1_status: str
    v2_status: str
    overall_status: str
    capabilities: dict[str, list[str]]


# Request models for advanced endpoints
class ChannelDataRequest(BaseModel):
    channel_id: str
    include_real_time: bool = True
    format: str = "detailed"


class PerformanceMetricsRequest(BaseModel):
    channels: list[str]
    period: str = "30d"


# Create router with insights prefix
router = APIRouter(
    prefix="/analytics/insights",
    tags=["Analytics Insights"],
    responses={
        404: {"description": "Resource not found"},
        500: {"description": "Internal server error"},
    },
)

# === DATA SOURCE CAPABILITIES ===


@router.get("/capabilities", response_model=DataSourceHealth)
async def get_data_source_capabilities():
    """Check capabilities and health of both analytics data sources"""
    logger.info("Checking data source capabilities...")

    # Check V1 (telegram-based) analytics
    v1_status = "healthy"

    try:
        # Quick health check - ensure core analytics service is accessible
        from core.di_container import get_container

        container_instance = get_container()
        container_instance.analytics_service()
        # If service instantiates without error, it's working
        logger.info("V1 analytics service accessible")

    except Exception as e:
        logger.warning(f"V1 analytics check failed: {e}")
        v1_status = "degraded"

    # Check V2 (database-backed) analytics
    v2_status = "degraded"  # Default to degraded

    try:
        # Try to initialize the V2 service
        v2_service = await get_analytics_fusion_service()
        if v2_service:
            # Test if we can actually query the database
            from apps.api.di_analytics import get_database_pool

            pool = await get_database_pool()

            if pool:
                try:
                    # Try different pool types
                    if hasattr(pool, "fetchval"):
                        # Direct pool test
                        result = await pool.fetchval("SELECT 1")  # type: ignore
                        v2_status = "healthy" if result == 1 else "degraded"
                    elif hasattr(pool, "acquire"):
                        # AsyncPG pool test
                        async with pool.acquire() as conn:  # type: ignore
                            result = await conn.fetchval("SELECT 1")
                            v2_status = "healthy" if result == 1 else "degraded"
                    else:
                        # Mock pool - limited functionality but working
                        v2_status = "limited"
                except Exception as pool_error:
                    logger.warning(f"V2 pool test failed: {pool_error}")
                    v2_status = "degraded"
            else:
                v2_status = "degraded"

        logger.info(f"V2 health check result: {v2_status}")

    except Exception as e:
        logger.warning(f"V2 health check failed: {e}")
        v2_status = "degraded"

    capabilities = {
        "v1_capabilities": [
            "Real-time monitoring",
            "Demo analytics data",
            "Basic post metrics",
            "Channel management",
            "AI recommendations",
        ],
        "v2_capabilities": [
            "Advanced growth analysis",
            "Reach optimization",
            "Trending detection",
            "Traffic source analysis",
            "MTProto data integration",
        ],
    }

    # Overall status is healthy if either system is working well
    overall_status = (
        "healthy" if v1_status == "healthy" or v2_status in ["healthy", "limited"] else "degraded"
    )


# === ADVANCED CHANNEL DATA ===


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
        )  # === ANALYTICAL REPORTS ===


@router.get("/reports/{channel_id}")
async def get_analytical_report(
    channel_id: int,
    report_type: str = Query("growth", regex="^(growth|reach|trending|comprehensive)$"),
    days: int = Query(30, ge=7, le=365, description="Days of historical data"),
    current_user: dict = Depends(get_current_user),
):
    """Generate comprehensive analytical reports"""

    try:
        # Import demo data generators
        from apps.api.__mocks__.analytics_mock import (
            generate_post_dynamics,
            generate_top_posts,
        )

        # For now, provide V1-based reporting with enhanced analytics
        base_data = generate_post_dynamics(days * 24)  # Convert days to hours
        generate_top_posts(20)

        if report_type == "growth":
            # Simulate growth analysis
            daily_views = []
            for day in range(days):
                day_start = len(base_data) - (day + 1) * 24
                day_end = len(base_data) - day * 24
                if day_start >= 0:
                    day_views = sum(p.views for p in base_data[day_start:day_end])
                    daily_views.append(
                        {
                            "date": (datetime.now() - timedelta(days=day)).date().isoformat(),
                            "views": day_views,
                        }
                    )

            # Calculate growth rate
            if len(daily_views) >= 2:
                recent_avg = sum(d["views"] for d in daily_views[:7]) / 7
                previous_avg = (
                    sum(d["views"] for d in daily_views[7:14]) / 7
                    if len(daily_views) >= 14
                    else recent_avg
                )
                growth_rate = ((recent_avg - previous_avg) / max(previous_avg, 1)) * 100
            else:
                growth_rate = 0

            return {
                "report_type": "growth",
                "channel_id": channel_id,
                "period_days": days,
                "growth_rate_percent": round(growth_rate, 2),
                "daily_views": daily_views,
                "trend_analysis": (
                    "improving"
                    if growth_rate > 5
                    else "stable"
                    if growth_rate > -5
                    else "declining"
                ),
                "data_source": "v1_enhanced",
                "note": "Enhanced V1 analysis. V2 MTProto analysis coming soon.",
                "generated_at": datetime.now().isoformat(),
            }

        # Add other report types...
        return {
            "report_type": report_type,
            "channel_id": channel_id,
            "message": f"{report_type.title()} report will be available when V2 MTProto integration is complete",
            "fallback_available": True,
            "data_source": "v1_fallback",
        }

    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate analytical report")


# === SYSTEM COMPARISON ===


@router.get("/comparison/{channel_id}")
async def get_data_source_comparison(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Compare data availability between V1 and V2 systems"""

    v1_features = {
        "available": [
            "Real-time post dynamics",
            "Demo analytics data",
            "Top posts ranking",
            "Best posting times",
            "AI recommendations",
            "Channel management",
        ],
        "limitations": [
            "Mock data only",
            "No official Telegram stats",
            "Limited historical analysis",
            "No MTProto integration",
        ],
    }

    v2_features = {
        "potential": [
            "Official Telegram analytics",
            "MTProto data access",
            "Advanced growth analysis",
            "Reach optimization",
            "Trending detection",
            "Traffic source analysis",
        ],
        "current_issues": [
            "Database connection problems",
            "Service initialization errors",
            "Missing data collection",
            "API endpoints not functional",
        ],
    }

    return {
        "channel_id": channel_id,
        "v1_system": v1_features,
        "v2_system": v2_features,
        "integration_status": "partial",
        "recommendation": "Use V1 for current operations, V2 development in progress",
        "next_steps": [
            "Fix V2 database connection",
            "Enable MTProto data collection",
            "Test V2 endpoints",
            "Implement smart routing",
        ],
    }


# === CHANNEL TRENDING ANALYTICS ===


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
    """
    Get trending posts using statistical analysis

    Identifies posts with exceptional performance using advanced analytics methods.
    Supports Z-score and exponentially weighted moving average (EWMA) detection.
    """
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

        # Get fresh trending data
        trending_data = await service.get_trending_posts(
            channel_id, from_, to_, window_hours, method
        )

        response_data = PostListResponse(data=trending_data)  # type: ignore
        response_dict = response_data.dict()

        # Cache the response
        await cache.set_json(cache_key, response_dict, ttl_s=300)  # 5 minutes

        return response_data

    except Exception as e:
        logger.error(f"Error getting trending posts for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trending posts data",
        )
