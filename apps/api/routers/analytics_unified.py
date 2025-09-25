"""
Unified Analytics Router - Best of Both Worlds
Combines V1 (Bot API) real-time data with V2 (MTProto) deep analytics
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from apps.api.routers.analytics_router import (
    generate_ai_recommendations,
    generate_best_time_recommendations,
    generate_post_dynamics,
    generate_top_posts,
)

logger = logging.getLogger(__name__)

# Create unified router
router = APIRouter(
    prefix="/unified-analytics",
    tags=["Unified Analytics"],
    responses={404: {"description": "Not found"}},
)


# Response models for unified analytics
class UnifiedMetrics(BaseModel):
    """Unified metrics combining V1 and V2 data"""

    # Real-time data (V1)
    current_views: int
    recent_posts: int
    live_engagement: float

    # Historical data (V2 - when available)
    total_growth: int | None = None
    reach_trend: float | None = None
    trending_score: float | None = None

    # Metadata
    data_sources: list[str]
    last_updated: datetime
    v1_available: bool
    v2_available: bool


class UnifiedDashboardData(BaseModel):
    """Complete dashboard data from both systems"""

    metrics: UnifiedMetrics
    live_charts: dict[str, Any]
    historical_analysis: dict[str, Any] | None = None
    recommendations: list[dict[str, Any]]


class DataSourceHealth(BaseModel):
    """Health status of both analytics systems"""

    v1_status: str
    v2_status: str
    overall_status: str
    capabilities: dict[str, list[str]]


# NOTE: Health endpoint moved to health_system_router.py for consolidation
# This unified analytics router is being phased out


@router.get("/capabilities", response_model=DataSourceHealth)
async def get_data_source_capabilities():
    """Check capabilities and health of both analytics data sources"""
    logger.info("Checking data source capabilities...")

    # Check V1 (telegram-based) analytics
    v1_status = "healthy"

    try:
        # Quick health check - ensure core analytics service is accessible
        from core.di_container import get_container

        container = get_container()
        container.analytics_service()
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

    return DataSourceHealth(
        v1_status=v1_status,
        v2_status=v2_status,
        overall_status=overall_status,
        capabilities=capabilities,
    )


@router.get("/dashboard/{channel_id}", response_model=UnifiedDashboardData)
async def get_unified_dashboard(
    channel_id: str,
    period_hours: int = Query(24, ge=1, le=168, description="Time period in hours"),
):
    """Get unified dashboard combining real-time and historical data"""

    try:
        # V1 Data - Real-time and demo data (always available)
        live_post_dynamics = generate_post_dynamics(period_hours)
        recent_posts_count = len(
            [p for p in live_post_dynamics if p.timestamp > datetime.now() - timedelta(hours=6)]
        )
        current_views = sum(p.views for p in live_post_dynamics[-6:]) if live_post_dynamics else 0
        live_engagement = (
            sum(p.likes + p.shares + p.comments for p in live_post_dynamics[-6:])
            / max(current_views, 1)
            * 100
        )

        ai_recommendations = generate_ai_recommendations()

        # Create unified metrics
        metrics = UnifiedMetrics(
            current_views=current_views,
            recent_posts=recent_posts_count,
            live_engagement=round(live_engagement, 2),
            data_sources=["v1_demo"],
            last_updated=datetime.now(),
            v1_available=True,
            v2_available=False,  # Set to False until V2 is fully working
        )

        # Live charts data (V1)
        live_charts = {
            "post_dynamics": [
                {
                    "timestamp": p.timestamp.isoformat(),
                    "views": p.views,
                    "likes": p.likes,
                    "shares": p.shares,
                    "comments": p.comments,
                }
                for p in live_post_dynamics
            ],
            "top_posts": [
                {
                    "id": p.id,
                    "title": p.title,
                    "views": p.views,
                    "engagement": p.likes + p.shares + p.comments,
                }
                for p in generate_top_posts(5)
            ],
            "best_times": [
                {
                    "day": bt.day,
                    "hour": bt.hour,
                    "confidence": bt.confidence,
                    "engagement": bt.avg_engagement,
                }
                for bt in generate_best_time_recommendations()
            ],
        }

        # V2 Data - Try to get historical analysis (when working)
        historical_analysis = None
        try:
            # TODO: When V2 is fixed, add real historical data here
            # historical_analysis = await get_v2_historical_data(channel_id, period_hours)
            pass
        except Exception as e:
            logger.warning(f"V2 historical data not available: {e}")

        # Recommendations (V1)
        recommendations = [
            {
                "type": rec.type,
                "title": rec.title,
                "description": rec.description,
                "confidence": rec.confidence,
                "source": "v1_ai",
            }
            for rec in ai_recommendations
        ]

        return UnifiedDashboardData(
            metrics=metrics,
            live_charts=live_charts,
            historical_analysis=historical_analysis,
            recommendations=recommendations,
        )

    except Exception as e:
        logger.error(f"Failed to get unified dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load unified dashboard",
        )


@router.get("/live-metrics/{channel_id}")
async def get_live_metrics(
    channel_id: str,
    hours: int = Query(6, ge=1, le=24, description="Hours of recent data"),
):
    """Get real-time metrics optimized for live monitoring"""

    try:
        # Use V1 for real-time data
        recent_dynamics = generate_post_dynamics(hours)

        # Calculate live metrics
        if recent_dynamics:
            current_views = recent_dynamics[-1].views
            view_trend = (
                recent_dynamics[-1].views - recent_dynamics[-2].views
                if len(recent_dynamics) > 1
                else 0
            )
            engagement_rate = (
                (
                    recent_dynamics[-1].likes
                    + recent_dynamics[-1].shares
                    + recent_dynamics[-1].comments
                )
                / max(recent_dynamics[-1].views, 1)
                * 100
            )
        else:
            current_views = 0
            view_trend = 0
            engagement_rate = 0

        return {
            "channel_id": channel_id,
            "current_views": current_views,
            "view_trend": view_trend,
            "engagement_rate": round(engagement_rate, 2),
            "posts_last_hour": len(
                [p for p in recent_dynamics if p.timestamp > datetime.now() - timedelta(hours=1)]
            ),
            "data_freshness": "real-time",
            "source": "v1_optimized",
            "last_updated": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get live metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get live metrics",
        )


@router.get("/reports/{channel_id}")
async def get_analytical_report(
    channel_id: str,
    report_type: str = Query("growth", regex="^(growth|reach|trending|comprehensive)$"),
    days: int = Query(30, ge=7, le=365, description="Days of historical data"),
):
    """Get detailed analytical reports (will use V2 when available)"""

    try:
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate analytical report",
        )


@router.get("/comparison/{channel_id}")
async def get_data_source_comparison(channel_id: str):
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


# Smart routing utilities for future use
async def smart_route_request(request_type: str, channel_id: str, **params):
    """Smart routing between V1 and V2 based on request type and availability"""

    if request_type in ["real-time", "live", "current", "monitoring"]:
        # Use V1 for real-time data
        return "v1"
    elif request_type in ["historical", "growth", "trends", "analysis"]:
        # Try V2 first, fallback to V1
        try:
            # TODO: Test V2 availability
            return "v2"
        except:
            return "v1_fallback"
    else:
        # Default to V1 for unknown requests
        return "v1"


# Utility function for future V2 integration
async def get_v2_data_when_available(endpoint: str, **params):
    """Utility to safely call V2 endpoints when they become available"""
    try:
        # TODO: Call actual V2 endpoints when database is fixed
        # from apps.api.routers.analytics_v2 import some_v2_function
        # return await some_v2_function(**params)
        return None
    except Exception as e:
        logger.warning(f"V2 endpoint {endpoint} not available: {e}")
        return None


# Demo/Mock API endpoints - Single source of truth for frontend mock data
@router.get("/demo/post-dynamics")
async def get_demo_post_dynamics(
    channel_id: int = Query(default=1), hours: int = Query(default=24, ge=1, le=168)
):
    """Demo endpoint: Get mock post dynamics data from backend"""
    try:
        dynamics = generate_post_dynamics(hours)
        return {
            "success": True,
            "data": {
                "channel_id": channel_id,
                "time_range": f"{hours} hours",
                "dynamics": dynamics,
                "source": "backend_mock",
                "generated_at": datetime.utcnow(),
            },
        }
    except Exception as e:
        logger.error(f"Error generating demo post dynamics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate demo post dynamics",
        )


@router.get("/demo/top-posts")
async def get_demo_top_posts(
    channel_id: int = Query(default=1),
    limit: int = Query(default=10, ge=1, le=100),
    period: str = Query(default="today"),
    sort_by: str = Query(default="views"),
):
    """Demo endpoint: Get mock top posts data from backend"""
    try:
        posts = generate_top_posts(limit)
        return {
            "success": True,
            "data": {
                "channel_id": channel_id,
                "posts": posts,
                "total_count": len(posts),
                "period": period,
                "sort_by": sort_by,
                "source": "backend_mock",
                "generated_at": datetime.utcnow(),
            },
        }
    except Exception as e:
        logger.error(f"Error generating demo top posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate demo top posts",
        )


@router.get("/demo/best-time")
async def get_demo_best_time(
    channel_id: int = Query(default=1), timeframe: str = Query(default="week")
):
    """Demo endpoint: Get mock best time recommendations from backend"""
    try:
        recommendations = generate_best_time_recommendations()
        return {
            "success": True,
            "data": {
                "channel_id": channel_id,
                "timeframe": timeframe,
                **recommendations,
                "source": "backend_mock",
                "generated_at": datetime.utcnow(),
            },
        }
    except Exception as e:
        logger.error(f"Error generating demo best time recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate demo best time recommendations",
        )


@router.get("/demo/ai-recommendations")
async def get_demo_ai_recommendations(channel_id: int = Query(default=1)):
    """Demo endpoint: Get mock AI recommendations from backend"""
    try:
        recommendations = generate_ai_recommendations()
        return {
            "success": True,
            "data": {
                "channel_id": channel_id,
                "recommendations": recommendations,
                "source": "backend_mock",
                "generated_at": datetime.utcnow(),
            },
        }
    except Exception as e:
        logger.error(f"Error generating demo AI recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate demo AI recommendations",
        )
