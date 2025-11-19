"""
Statistical reports and analysis endpoints.
Handles report generation, comparisons, and trending analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

# Auth
from apps.api.middleware.auth import get_current_user

# Services - NEW DI
from apps.di.analytics_container import get_analytics_fusion_service, get_cache
from apps.shared.performance import performance_timer
from core.protocols import AnalyticsFusionServiceProtocol

# Schemas

logger = logging.getLogger(__name__)

# ✅ FIXED: Removed prefix - now configured in main.py
router = APIRouter(tags=["statistics-reports"])

# === STATISTICAL REPORTS ===


@router.get("/analytical/{channel_id}")
async def get_analytical_report(
    channel_id: int,
    report_type: str = Query(
        "growth",
        regex="^(growth|reach|trending|comprehensive)$",
        description="Type of statistical report",
    ),
    days: int = Query(30, ge=7, le=365, description="Days of historical data for analysis"),
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 📊 Generate Comprehensive Statistical Reports

    Generate detailed statistical analysis reports including:
    - Growth trend analysis over time
    - Reach effectiveness statistics
    - Trending pattern analysis
    - Comprehensive performance reports
    """
    try:
        # Generate cache key
        cache_params = {"channel_id": channel_id, "report_type": report_type, "days": days}
        cache_key = cache.generate_cache_key("statistical_report", cache_params)

        # Try cache first (reports can be cached longer)
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Generate statistical report
        with performance_timer(f"statistical_report_{report_type}"):
            report_data = await analytics_service.generate_analytical_report(
                channel_id, report_type, days
            )

        response_data = {
            "channel_id": channel_id,
            "report": report_data,
            "report_type": report_type,
            "analysis_period_days": days,
            "report_category": "statistical_analysis",
            "generated_at": datetime.utcnow().isoformat(),
            "meta": {
                "cache_hit": False,
                "analysis_depth": "comprehensive" if report_type == "comprehensive" else "focused",
            },
        }

        # Cache statistical reports for 45 minutes (less volatile than real-time data)
        await cache.set_json(cache_key, response_data, expire_seconds=2700)

        return response_data

    except Exception as e:
        logger.error(f"Failed to generate statistical report for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate statistical report")


@router.get("/comparison/{channel_id}")
async def get_data_source_comparison(
    channel_id: int,
    comparison_type: str = Query(
        "systems", regex="^(systems|periods|metrics)$", description="Type of comparison analysis"
    ),
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 🔍 Statistical Data Comparison Analysis

    Compare statistical data across different dimensions:
    - Systems comparison (V1 vs V2 analytics)
    - Period-over-period analysis
    - Cross-metric correlation analysis
    """
    try:
        # Generate cache key
        cache_params = {"channel_id": channel_id, "comparison_type": comparison_type}
        cache_key = cache.generate_cache_key("comparison_analysis", cache_params)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            return cached_data

        if comparison_type == "systems":
            # Systems comparison data
            comparison_data = {
                "v1_analytics": {
                    "available_features": [
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
                        "Limited historical data",
                        "Demo environment constraints",
                    ],
                    "data_sources": ["Mock generator", "Demo database"],
                    "accuracy": "Simulated",
                    "update_frequency": "Real-time (simulated)",
                },
                "v2_analytics": {
                    "available_features": [
                        "Official Telegram statistics",
                        "Real historical data",
                        "Advanced forecasting",
                        "Multi-channel analysis",
                        "Custom report generation",
                        "API-driven insights",
                    ],
                    "advantages": [
                        "Authentic Telegram data",
                        "Production-ready metrics",
                        "Comprehensive analytics",
                        "Scalable architecture",
                    ],
                    "data_sources": ["Telegram Bot API", "Official analytics"],
                    "accuracy": "Official",
                    "update_frequency": "Real-time (official)",
                },
            }
        elif comparison_type == "periods":
            # Period comparison would be implemented here
            comparison_data = await analytics_service.get_period_comparison(channel_id)
        else:
            # Metrics comparison
            comparison_data = await analytics_service.get_metrics_comparison(channel_id)

        response_data = {
            "channel_id": channel_id,
            "comparison_type": comparison_type,
            "comparison_data": comparison_data,
            "analysis_category": "statistical_comparison",
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Cache comparisons for 60 minutes (relatively stable)
        await cache.set_json(cache_key, response_data, expire_seconds=3600)

        return response_data

    except Exception as e:
        logger.error(f"Failed to generate comparison analysis for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate comparison analysis")


@router.get("/trends/top-posts")
async def get_top_posts_trends(
    period: int = Query(default=7, ge=1, le=30, description="Period in days for trend analysis"),
    limit: int = Query(default=10, ge=1, le=50, description="Number of top posts to analyze"),
    channel_id: int | None = Query(default=None, description="Specific channel ID (optional)"),
    trend_type: str = Query(
        "performance",
        regex="^(performance|engagement|growth)$",
        description="Type of trend analysis",
    ),
    service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📈 Top Posts Trending Analysis

    Analyze trending patterns in top-performing posts:
    - Performance trend analysis over time
    - Engagement pattern recognition
    - Growth trajectory analysis
    - Cross-channel trending comparison
    """
    try:
        # Generate cache key
        cache_params = {
            "period": period,
            "limit": limit,
            "channel_id": channel_id,
            "trend_type": trend_type,
        }
        cache_key = cache.generate_cache_key("trends-top-posts", cache_params)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Get trending posts data with statistical analysis
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=period)

        with performance_timer("top_posts_trends_analysis"):
            if channel_id:
                # Get top posts trends for specific channel
                posts_data = await service.get_top_posts(channel_id, from_date, to_date, limit)
                trends_data = posts_data
            else:
                # Generate cross-channel trending analysis
                trends_data = await generate_cross_channel_trends(
                    service, from_date, to_date, limit, trend_type
                )

        response_data = {
            "trends": trends_data,
            "meta": {
                "period_days": period,
                "limit": limit,
                "channel_id": channel_id,
                "trend_type": trend_type,
                "analysis_period": {"from": from_date.isoformat(), "to": to_date.isoformat()},
                "cache_hit": False,
                "analysis_category": "trending_statistics",
            },
        }

        # Cache trending analysis for 20 minutes
        await cache.set_json(cache_key, response_data, expire_seconds=1200)

        return response_data

    except Exception as e:
        logger.error(f"Failed to get top posts trends analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze top posts trends")


@router.get("/performance-summary/{channel_id}")
async def get_performance_summary_report(
    channel_id: int,
    days: int = Query(30, ge=7, le=90, description="Days for performance summary"),
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 📋 Performance Summary Report

    Generate comprehensive performance summary including:
    - Key performance indicators (KPIs)
    - Growth statistics summary
    - Engagement metrics overview
    - Performance benchmarks
    """
    try:
        # Generate cache key
        cache_params = {"channel_id": channel_id, "days": days}
        cache_key = cache.generate_cache_key("performance_summary", cache_params)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            return cached_data

        # Generate performance summary
        with performance_timer("performance_summary_generation"):
            summary_data = await analytics_service.get_performance_summary(channel_id, days)

        response_data = {
            "channel_id": channel_id,
            "summary": summary_data,
            "report_period_days": days,
            "report_type": "performance_summary",
            "generated_at": datetime.utcnow().isoformat(),
            "kpi_categories": ["growth", "engagement", "reach", "content_performance"],
        }

        # Cache performance summaries for 40 minutes
        await cache.set_json(cache_key, response_data, expire_seconds=2400)

        return response_data

    except Exception as e:
        logger.error(f"Failed to generate performance summary for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate performance summary")


# === UTILITY FUNCTIONS ===


async def generate_cross_channel_trends(
    service, from_date: datetime, to_date: datetime, limit: int, trend_type: str
) -> list[dict[str, Any]]:
    """Generate cross-channel trending analysis"""
    try:
        # In a real implementation, this would aggregate across multiple channels
        # For now, return sample trending data with statistical focus
        trends_data = []

        for i in range(limit):
            trend_item = {
                "post_id": f"post_{i + 1}",
                "channel_id": f"channel_{(i % 3) + 1}",
                "title": f"Trending Post #{i + 1}",
                "views": 10000 - (i * 500),
                "engagement_rate": round(15.5 - (i * 0.3), 2),
                "trend_score": round(100 - (i * 2.5), 1),
                "growth_velocity": round(8.5 - (i * 0.2), 2),
                "statistical_rank": i + 1,
                "trend_category": trend_type,
                "performance_percentile": round(100 - (i * 2.5), 1),
            }
            trends_data.append(trend_item)

        return trends_data

    except Exception as e:
        logger.error(f"Failed to generate cross-channel trends: {e}")
        return []
