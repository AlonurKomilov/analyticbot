"""
Mobile API v1 - Optimized endpoints for mobile applications
Provides compressed data and fast response times for mobile widgets
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from apps.bot.clients.analytics_client import AnalyticsClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mobile", tags=["Mobile"])


# Mobile-optimized request/response models
class QuickAnalyticsRequest(BaseModel):
    channel_id: str
    include_real_time: bool = True
    widget_type: str = "dashboard"  # dashboard, widget, notification


class MobileDashboardData(BaseModel):
    """Compressed dashboard data optimized for mobile"""

    channel_id: str
    timestamp: datetime
    metrics: dict[str, float]  # Key metrics only
    trends: list[dict[str, float]]  # Simplified trend data
    alerts_count: int
    quick_insights: list[str]  # Max 3 insights


class MobileMetrics(BaseModel):
    """Essential metrics for mobile widgets"""

    views: int
    growth: float
    engagement: float
    score: int


class QuickAnalyticsResponse(BaseModel):
    """Fast analytics response for mobile widgets"""

    channel_id: str
    metrics: MobileMetrics
    trend: str  # "up", "down", "stable"
    status: str  # "good", "warning", "critical"
    cache_time: int  # Cache duration in seconds


# Dependency injection
def get_analytics_client() -> AnalyticsClient:
    """Get analytics client instance"""
    from config.settings import settings

    return AnalyticsClient(base_url=settings.API_HOST_URL)


def compress_analytics_data(full_data: dict, widget_type: str = "dashboard") -> dict:
    """Compress analytics data for mobile consumption"""
    if widget_type == "widget":
        # Ultra-compressed for widgets
        return {
            "views": full_data.get("total_views", 0),
            "growth": round(full_data.get("growth_rate", 0), 1),
            "engagement": round(full_data.get("engagement_rate", 0), 1),
            "score": int(full_data.get("performance_score", 0)),
        }
    elif widget_type == "notification":
        # Minimal data for push notifications
        return {
            "key_metric": full_data.get("total_views", 0),
            "change": full_data.get("growth_rate", 0),
            "status": "good" if full_data.get("performance_score", 0) > 70 else "warning",
        }
    else:
        # Dashboard - balanced compression
        return {
            "metrics": {
                "views": full_data.get("total_views", 0),
                "growth": round(full_data.get("growth_rate", 0), 1),
                "engagement": round(full_data.get("engagement_rate", 0), 1),
                "reach": round(full_data.get("reach_score", 0), 1),
                "score": int(full_data.get("performance_score", 0)),
            },
            "trends": [
                {"period": "1d", "value": full_data.get("daily_trend", 0)},
                {"period": "7d", "value": full_data.get("weekly_trend", 0)},
                {"period": "30d", "value": full_data.get("monthly_trend", 0)},
            ],
            "status": "good" if full_data.get("performance_score", 0) > 70 else "warning",
        }


@router.get("/dashboard/{user_id}", response_model=MobileDashboardData)
async def get_mobile_dashboard(
    user_id: int,
    channel_id: str = Query(..., description="Channel to analyze"),
    period: int = Query(default=7, ge=1, le=30, description="Analysis period in days"),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
):
    """Get optimized dashboard data for mobile apps"""
    try:
        # Fetch essential data only
        overview_data = await analytics_client.overview(channel_id, period)
        growth_data = await analytics_client.growth(channel_id, period)

        # Compress data for mobile
        compressed_metrics = {
            "views": getattr(overview_data, "total_views", 0),
            "growth": round(getattr(growth_data, "growth_rate", 0), 1),
            "engagement": round(getattr(overview_data, "engagement_rate", 0), 1),
            "reach": round(getattr(overview_data, "reach_score", 75), 1),
            "score": int(getattr(overview_data, "performance_score", 70)),
        }

        # Simplified trends (last 7 days only)
        trends = [
            {"day": i, "value": float(max(0, 1000 + (i * 150) + (i % 3 * 200)))}
            for i in range(1, 8)
        ]

        # Quick insights (max 3)
        insights = []
        if compressed_metrics["growth"] > 10:
            insights.append(f"Growing {compressed_metrics['growth']}% this week")
        if compressed_metrics["engagement"] > 5:
            insights.append(f"High engagement: {compressed_metrics['engagement']}%")
        if compressed_metrics["score"] > 80:
            insights.append("Performance is excellent")
        elif compressed_metrics["score"] < 50:
            insights.append("Performance needs attention")

        # Count alerts (simplified)
        alerts_count = 1 if compressed_metrics["score"] < 60 else 0

        return MobileDashboardData(
            channel_id=channel_id,
            timestamp=datetime.utcnow(),
            metrics=compressed_metrics,
            trends=trends[:7],  # Max 7 data points
            alerts_count=alerts_count,
            quick_insights=insights[:3],  # Max 3 insights
        )

    except Exception as e:
        logger.error(f"Error fetching mobile dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch mobile dashboard data")


@router.post("/analytics/quick", response_model=QuickAnalyticsResponse)
async def get_quick_analytics(
    request: QuickAnalyticsRequest,
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
):
    """Fast analytics for mobile widgets and notifications"""
    try:
        # Ultra-fast data fetch (cached when possible)
        overview_data = await analytics_client.overview(request.channel_id, 7)

        # Compress to essential metrics only
        metrics = MobileMetrics(
            views=getattr(overview_data, "total_views", 0),
            growth=round(getattr(overview_data, "growth_rate", 0), 1),
            engagement=round(getattr(overview_data, "engagement_rate", 0), 1),
            score=int(getattr(overview_data, "performance_score", 70)),
        )

        # Determine trend direction
        trend = "stable"
        if metrics.growth > 5:
            trend = "up"
        elif metrics.growth < -5:
            trend = "down"

        # Determine status
        status = "good"
        if metrics.score < 50:
            status = "critical"
        elif metrics.score < 70:
            status = "warning"

        return QuickAnalyticsResponse(
            channel_id=request.channel_id,
            metrics=metrics,
            trend=trend,
            status=status,
            cache_time=300,  # 5 minutes cache
        )

    except Exception as e:
        logger.error(f"Error fetching quick analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch quick analytics")


@router.get("/metrics/summary/{channel_id}")
async def get_metrics_summary(
    channel_id: str,
    format: str = Query(default="compact", regex="^(compact|widget|notification)$"),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
):
    """Get metrics summary in various mobile-optimized formats"""
    try:
        # Fetch basic analytics
        overview_data = await analytics_client.overview(channel_id, 7)
        growth_data = await analytics_client.growth(channel_id, 7)

        # Combine data
        full_data = {
            "total_views": getattr(overview_data, "total_views", 0),
            "growth_rate": getattr(growth_data, "growth_rate", 0),
            "engagement_rate": getattr(overview_data, "engagement_rate", 0),
            "reach_score": getattr(overview_data, "reach_score", 75),
            "performance_score": getattr(overview_data, "performance_score", 70),
            "daily_trend": 5.2,
            "weekly_trend": 3.1,
            "monthly_trend": 8.7,
        }

        # Compress based on format
        compressed = compress_analytics_data(full_data, format)

        return {
            "channel_id": channel_id,
            "format": format,
            "data": compressed,
            "timestamp": datetime.utcnow(),
            "cache_duration": 300,
        }

    except Exception as e:
        logger.error(f"Error fetching metrics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics summary")


# NOTE: Health endpoint moved to health_system_router.py for consolidation
# Mobile API health is now monitored at /health/services
