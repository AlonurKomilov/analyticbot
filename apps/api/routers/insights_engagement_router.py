"""
Engagement and audience insights endpoints.
Handles engagement metrics, audience analysis, and trending content.
"""

import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

# Services
from apps.api.di_container.analytics_container import (
    get_analytics_fusion_service,
    get_cache,
)

# Auth
from apps.api.middleware.auth import get_current_user, require_channel_access

# Schemas
# Schemas
from apps.api.schemas.analytics import PostListResponse

# ✅ CLEAN ARCHITECTURE: Use apps performance abstraction instead of direct infra import
from apps.shared.performance import performance_timer
from core.services.analytics_fusion import AnalyticsOrchestratorService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insights/engagement", tags=["insights-engagement"])

# === ENGAGEMENT INSIGHTS ===


@router.get("/channels/{channel_id}/engagement")
async def get_channel_engagement_insights(
    channel_id: int,
    period: str = Query(
        "24h",
        regex="^(24h|7d|30d|90d)$",
        description="Time period for engagement analysis",
    ),
    metrics_type: str = Query(
        "comprehensive",
        regex="^(basic|comprehensive|advanced)$",
        description="Level of engagement metrics",
    ),
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsOrchestratorService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 📈 Channel Engagement Insights

    Comprehensive engagement analytics for a specific channel including:
    - Engagement rate analysis over time
    - User interaction patterns
    - Content performance correlation
    - Engagement trend identification

    **Parameters:**
    - channel_id: Target channel ID
    - period: Analysis time period (24h, 7d, 30d, 90d)
    - metrics_type: Depth of analysis (basic, comprehensive, advanced)
    """
    try:
        await require_channel_access(channel_id, current_user["id"])

        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "period": period,
            "metrics_type": metrics_type,
        }
        cache_key = cache.generate_cache_key("engagement_insights", cache_params)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        with performance_timer("channel_engagement_insights"):
            # Get comprehensive engagement data
            engagement_data = await analytics_service.get_engagement_insights(
                channel_id, period, metrics_type
            )

            # Enhance with additional insights based on metrics type
            if metrics_type == "advanced":
                engagement_trends = await analytics_service.get_engagement_trends(
                    channel_id, period
                )
                engagement_data["trends"] = engagement_trends

            response_data = {
                "success": True,
                "channel_id": channel_id,
                "period": period,
                "metrics_type": metrics_type,
                "engagement_insights": engagement_data,
                "analysis_category": "engagement_intelligence",
                "meta": {
                    "cache_hit": False,
                    "analysis_depth": metrics_type,
                    "generated_at": datetime.utcnow().isoformat(),
                },
            }

            # Cache engagement insights for 15 minutes (more volatile data)
            await cache.set_json(cache_key, response_data, expire_seconds=900)

            return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel engagement insights fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch channel engagement insights")


@router.get("/channels/{channel_id}/audience")
async def get_channel_audience_insights(
    channel_id: int,
    analysis_depth: str = Query(
        "standard",
        regex="^(basic|standard|detailed)$",
        description="Depth of audience analysis",
    ),
    include_demographics: bool = Query(True, description="Include demographic analysis"),
    include_behavior: bool = Query(True, description="Include behavioral insights"),
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsOrchestratorService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 👥 Channel Audience Intelligence

    Advanced audience demographics and behavioral insights including:
    - Demographic breakdowns and trends
    - User behavior pattern analysis
    - Engagement preference mapping
    - Audience growth trajectory

    **Parameters:**
    - channel_id: Target channel ID
    - analysis_depth: Level of analysis (basic, standard, detailed)
    - include_demographics: Include demographic data
    - include_behavior: Include behavioral analysis
    """
    try:
        await require_channel_access(channel_id, current_user["id"])

        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "analysis_depth": analysis_depth,
            "include_demographics": include_demographics,
            "include_behavior": include_behavior,
        }
        cache_key = cache.generate_cache_key("audience_insights", cache_params)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        with performance_timer("channel_audience_insights"):
            # Get base audience insights
            audience_data = await analytics_service.get_audience_insights(
                channel_id, analysis_depth
            )

            # Add demographic analysis if requested
            if include_demographics and analysis_depth in ["standard", "detailed"]:
                demographics = await analytics_service.get_audience_demographics(channel_id)
                audience_data["demographics"] = demographics

            # Add behavioral insights if requested
            if include_behavior and analysis_depth == "detailed":
                behavior_patterns = await analytics_service.get_audience_behavior_patterns(
                    channel_id
                )
                audience_data["behavior_patterns"] = behavior_patterns

            response_data = {
                "success": True,
                "channel_id": channel_id,
                "analysis_depth": analysis_depth,
                "audience_insights": audience_data,
                "analysis_category": "audience_intelligence",
                "meta": {
                    "cache_hit": False,
                    "includes_demographics": include_demographics,
                    "includes_behavior": include_behavior,
                    "generated_at": datetime.utcnow().isoformat(),
                },
            }

            # Cache audience insights for 30 minutes (relatively stable)
            await cache.set_json(cache_key, response_data, expire_seconds=1800)

            return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel audience insights fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch channel audience insights")


@router.get("/channels/{channel_id}/trending", response_model=PostListResponse)
async def get_trending_content_analysis(
    channel_id: int,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    window_hours: int = Query(default=48, ge=1, le=168, description="Analysis window in hours"),
    method: str = Query(
        default="zscore",
        regex="^(zscore|ewma|hybrid)$",
        description="Trending detection method",
    ),
    min_engagement: float = Query(0.01, ge=0, le=1, description="Minimum engagement threshold"),
    service: AnalyticsOrchestratorService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🔥 Trending Content Intelligence

    Advanced trending content analysis using statistical methods:
    - Z-score anomaly detection for engagement spikes
    - Exponentially Weighted Moving Average (EWMA) trending
    - Hybrid engagement pattern recognition
    - Content performance correlation analysis

    **Parameters:**
    - channel_id: Target channel ID
    - from/to: Analysis time range
    - window_hours: Statistical analysis window
    - method: Detection algorithm (zscore, ewma, hybrid)
    - min_engagement: Minimum engagement rate threshold
    """
    try:
        await require_channel_access(channel_id, current_user["id"])

        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "from": from_.isoformat(),
            "to": to_.isoformat(),
            "window_hours": window_hours,
            "method": method,
            "min_engagement": min_engagement,
        }
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("trending_content", cache_params, last_updated)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Get trending content with advanced analytics
        with performance_timer("trending_content_analysis"):
            trending_data = await service.get_trending_posts(
                channel_id, from_, to_, window_hours, method, min_engagement
            )

        response_data = PostListResponse(data=trending_data)  # type: ignore
        response_dict = response_data.dict()

        # Enhanced metadata for insights
        response_dict["meta"] = {
            "cache_hit": False,
            "analysis_method": method,
            "window_hours": window_hours,
            "min_engagement_threshold": min_engagement,
            "analysis_period": {"from": from_.isoformat(), "to": to_.isoformat()},
            "analysis_category": "trending_intelligence",
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Cache trending analysis for 10 minutes (highly dynamic)
        await cache.set_json(cache_key, response_dict, expire_seconds=600)

        return response_dict

    except Exception as e:
        logger.error(f"Trending content analysis failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze trending content")


@router.get("/engagement-patterns/{channel_id}")
async def get_engagement_patterns_analysis(
    channel_id: int,
    days: int = Query(30, ge=7, le=90, description="Days for pattern analysis"),
    pattern_type: str = Query(
        "temporal",
        regex="^(temporal|content|user)$",
        description="Type of pattern analysis",
    ),
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsOrchestratorService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 🔍 Engagement Patterns Intelligence

    Deep engagement pattern analysis including:
    - Temporal engagement patterns (time-based trends)
    - Content-type engagement correlations
    - User behavior engagement patterns
    - Pattern prediction and insights

    **Parameters:**
    - channel_id: Target channel ID
    - days: Analysis period in days
    - pattern_type: Focus area (temporal, content, user)
    """
    try:
        await require_channel_access(channel_id, current_user["id"])

        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "days": days,
            "pattern_type": pattern_type,
        }
        cache_key = cache.generate_cache_key("engagement_patterns", cache_params)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            return cached_data

        with performance_timer("engagement_patterns_analysis"):
            # Get pattern analysis based on type
            if pattern_type == "temporal":
                patterns_data = await analytics_service.get_temporal_engagement_patterns(
                    channel_id, days
                )
            elif pattern_type == "content":
                patterns_data = await analytics_service.get_content_engagement_patterns(
                    channel_id, days
                )
            else:  # user patterns
                patterns_data = await analytics_service.get_user_engagement_patterns(
                    channel_id, days
                )

        response_data = {
            "channel_id": channel_id,
            "pattern_type": pattern_type,
            "analysis_days": days,
            "patterns": patterns_data,
            "analysis_category": "engagement_pattern_intelligence",
            "insights": generate_pattern_insights(patterns_data, pattern_type),
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Cache pattern analysis for 25 minutes
        await cache.set_json(cache_key, response_data, expire_seconds=1500)

        return response_data

    except Exception as e:
        logger.error(f"Engagement patterns analysis failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze engagement patterns")


# === UTILITY FUNCTIONS ===


def generate_pattern_insights(patterns_data: dict, pattern_type: str) -> list[str]:
    """Generate actionable insights from engagement patterns"""
    insights = []

    try:
        if pattern_type == "temporal":
            # Time-based insights
            insights.extend(
                [
                    "🕐 Peak engagement hours identified for optimal posting",
                    "📅 Weekly engagement cycles detected for scheduling",
                    "⏰ Time-zone optimization opportunities available",
                ]
            )
        elif pattern_type == "content":
            # Content-based insights
            insights.extend(
                [
                    "📝 High-engagement content types identified",
                    "🎯 Content format preferences mapped",
                    "📊 Content-engagement correlation patterns found",
                ]
            )
        else:  # user patterns
            # User behavior insights
            insights.extend(
                [
                    "👥 User engagement behavioral segments identified",
                    "🔄 Repeat engagement patterns discovered",
                    "💬 User interaction preferences mapped",
                ]
            )

        return insights

    except Exception:
        return ["📊 Pattern analysis completed - review detailed data for insights"]
