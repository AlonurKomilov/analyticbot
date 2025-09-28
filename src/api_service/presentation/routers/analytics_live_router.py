"""
Real-time live analytics endpoints.
Handles current/live data metrics and monitoring.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from src.api_service.deps import get_analytics_fusion_service

# Auth
from src.api_service.middleware.auth import get_current_user

# Services
from src.bot_service.clients.analytics_client import AnalyticsClient
from src.shared_kernel.domain.services.analytics_fusion_service import (
    AnalyticsFusionService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics/live", tags=["analytics-live"])


# Analytics Client Dependency
def get_analytics_client() -> AnalyticsClient:
    from config.settings import settings

    return AnalyticsClient(settings.ANALYTICS_V2_BASE_URL)


# === LIVE METRICS ENDPOINTS ===


@router.get("/metrics/{channel_id}")
async def get_realtime_metrics(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
):
    """
    ## ⚡ Real-time Channel Metrics

    Get current live metrics for a channel including:
    - Live view counts and growth rates
    - Real-time engagement metrics
    - Current reach and active user counts
    - Trending score calculations

    **Note**: No caching - always returns fresh real-time data
    """
    try:
        # Fetch latest real-time data (last hour)
        overview_data = await analytics_client.overview(channel_id, 0.04)  # ~1 hour
        growth_data = await analytics_client.growth(channel_id, 0.04)
        reach_data = await analytics_client.reach(channel_id, 0.04)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_views": getattr(overview_data, "total_views", 0),
            "growth_rate": getattr(growth_data, "growth_rate", 0.0),
            "engagement_rate": getattr(overview_data, "engagement_rate", 0.0),
            "reach_score": getattr(reach_data, "reach_score", 0),
            "active_users": getattr(reach_data, "active_users", 0),
            "trending_score": calculate_trending_score(overview_data, growth_data, reach_data),
            "metrics_type": "real_time",
        }

    except Exception as e:
        logger.error(f"Real-time metrics fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch real-time metrics")


@router.get("/performance/{channel_id}")
async def get_performance_score(
    channel_id: int,
    period: int = Query(
        default=1, ge=1, le=7, description="Period in days for performance calculation"
    ),
    current_user: dict = Depends(get_current_user),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
):
    """
    ## 📊 Real-time Performance Scoring

    Calculate performance score based on:
    - Growth velocity (40% weight)
    - Engagement quality (35% weight)
    - Reach effectiveness (25% weight)
    """
    try:
        # Get data for the specified period
        period_days = period / 365.25  # Convert to fractional years for API

        overview_data = await analytics_client.overview(channel_id, period_days)
        growth_data = await analytics_client.growth(channel_id, period_days)
        reach_data = await analytics_client.reach(channel_id, period_days)

        # Calculate component scores (0-100)
        growth_score = calculate_growth_score(growth_data)
        engagement_score = calculate_engagement_score(overview_data)
        reach_score = calculate_reach_score(reach_data)

        # Weighted overall score
        overall_score = int(growth_score * 0.4 + engagement_score * 0.35 + reach_score * 0.25)

        # Performance classification
        performance_level = classify_performance(overall_score)

        # Generate actionable recommendations
        recommendations = generate_performance_recommendations(
            overall_score, growth_score, engagement_score, reach_score
        )

        return {
            "overall_score": overall_score,
            "growth_score": growth_score,
            "engagement_score": engagement_score,
            "reach_score": reach_score,
            "performance_level": performance_level,
            "recommendations": recommendations,
            "period_days": period,
            "analysis_type": "performance_scoring",
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Performance score calculation failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate performance score")


@router.get("/monitor/{channel_id}")
async def get_live_monitoring_data(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
):
    """
    ## 📡 Live Channel Monitoring

    Real-time monitoring dashboard data including:
    - Current activity levels
    - Performance alerts
    - Trend indicators
    - Health metrics
    """
    try:
        # Get very recent data (last 2 hours)
        recent_overview = await analytics_client.overview(channel_id, 0.083)  # ~2 hours
        recent_growth = await analytics_client.growth(channel_id, 0.083)
        recent_reach = await analytics_client.reach(channel_id, 0.083)

        # Calculate monitoring metrics
        activity_level = calculate_activity_level(recent_overview, recent_growth, recent_reach)
        performance_alerts = generate_performance_alerts(
            recent_overview, recent_growth, recent_reach
        )
        trend_indicators = calculate_trend_indicators(recent_overview, recent_growth, recent_reach)

        return {
            "status": "live",
            "last_updated": datetime.utcnow().isoformat(),
            "activity_level": activity_level,
            "performance_alerts": performance_alerts,
            "trend_indicators": trend_indicators,
            "health_score": calculate_health_score(recent_overview, recent_growth, recent_reach),
        }

    except Exception as e:
        logger.error(f"Live monitoring data fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get live monitoring data")


@router.get("/live-metrics/{channel_id}")
async def get_live_metrics_optimized(
    channel_id: int,
    hours: int = Query(6, ge=1, le=24, description="Hours of recent data"),
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
):
    """
    ## ⚡ Optimized Live Metrics

    Get real-time metrics optimized for live monitoring with:
    - Configurable time window
    - Performance optimization
    - Data freshness guarantee
    """
    try:
        # Use real analytics service instead of mock data
        live_metrics = await analytics_service.get_live_metrics(channel_id, hours)

        return live_metrics

    except Exception as e:
        logger.error(f"Failed to get live metrics for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get live metrics")


# === UTILITY FUNCTIONS ===


def calculate_trending_score(overview_data, growth_data, reach_data) -> float:
    """Calculate trending score from real-time data"""
    try:
        growth_rate = getattr(growth_data, "growth_rate", 0)
        engagement_rate = getattr(overview_data, "engagement_rate", 0)
        reach_score = getattr(reach_data, "reach_score", 0)

        # Weighted trending calculation
        trending = growth_rate * 0.5 + engagement_rate * 0.3 + reach_score * 0.2
        return round(min(100.0, max(0.0, trending)), 2)
    except:
        return 50.0  # Default moderate trending score


def calculate_growth_score(growth_data) -> int:
    """Calculate growth component score"""
    try:
        growth_rate = getattr(growth_data, "growth_rate", 0)
        return min(100, max(0, int(growth_rate * 10)))  # Scale to 0-100
    except:
        return 50


def calculate_engagement_score(overview_data) -> int:
    """Calculate engagement component score"""
    try:
        engagement_rate = getattr(overview_data, "engagement_rate", 0)
        return min(100, max(0, int(engagement_rate * 2)))  # Scale to 0-100
    except:
        return 50


def calculate_reach_score(reach_data) -> int:
    """Calculate reach component score"""
    try:
        reach_score = getattr(reach_data, "reach_score", 0)
        return min(100, max(0, int(reach_score)))
    except:
        return 50


def classify_performance(score: int) -> str:
    """Classify performance level"""
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    elif score >= 40:
        return "average"
    else:
        return "needs_improvement"


def generate_performance_recommendations(
    overall_score: int, growth_score: int, engagement_score: int, reach_score: int
) -> list[str]:
    """Generate recommendations based on performance scores"""
    recommendations = []

    if overall_score < 40:
        recommendations.append(
            "📉 Performance needs immediate attention - consider content strategy review"
        )

    if growth_score < 30:
        recommendations.append(
            "📈 Focus on growth tactics: collaborations, hashtag optimization, posting frequency"
        )

    if engagement_score < 30:
        recommendations.append(
            "💬 Improve engagement: ask questions, use polls, respond to comments quickly"
        )

    if reach_score < 30:
        recommendations.append(
            "🎯 Expand reach: optimize post timing, use trending topics, cross-platform promotion"
        )

    if not recommendations:
        recommendations.append("✅ Great performance! Keep up the consistent quality content")

    return recommendations


def calculate_activity_level(overview_data, growth_data, reach_data) -> str:
    """Calculate current activity level"""
    try:
        engagement = getattr(overview_data, "engagement_rate", 0)
        if engagement > 5:
            return "high"
        elif engagement > 2:
            return "medium"
        else:
            return "low"
    except:
        return "unknown"


def generate_performance_alerts(overview_data, growth_data, reach_data) -> list[str]:
    """Generate performance alerts"""
    alerts = []
    try:
        growth_rate = getattr(growth_data, "growth_rate", 0)
        engagement_rate = getattr(overview_data, "engagement_rate", 0)

        if growth_rate < 0:
            alerts.append("⚠️ Negative growth detected")
        if engagement_rate < 1:
            alerts.append("⚠️ Low engagement rate")
    except:
        pass

    return alerts


def calculate_trend_indicators(overview_data, growth_data, reach_data) -> dict[str, str]:
    """Calculate trend indicators"""
    try:
        growth_rate = getattr(growth_data, "growth_rate", 0)
        engagement_rate = getattr(overview_data, "engagement_rate", 0)

        return {
            "growth_trend": ("📈" if growth_rate > 0 else "📉" if growth_rate < 0 else "➡️"),
            "engagement_trend": (
                "📈" if engagement_rate > 2 else "📉" if engagement_rate < 1 else "➡️"
            ),
        }
    except:
        return {"growth_trend": "❓", "engagement_trend": "❓"}


def calculate_health_score(overview_data, growth_data, reach_data) -> int:
    """Calculate overall health score"""
    try:
        growth_rate = getattr(growth_data, "growth_rate", 0)
        engagement_rate = getattr(overview_data, "engagement_rate", 0)
        reach_score = getattr(reach_data, "reach_score", 0)

        health = growth_rate * 0.4 + engagement_rate * 0.4 + reach_score * 0.2
        return min(100, max(0, int(health * 10)))
    except:
        return 50
