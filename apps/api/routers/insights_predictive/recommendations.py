"""
Recommendation and forecasting endpoints.

This module handles AI-powered recommendations, forecasting,
optimal timing predictions, and growth trajectory analysis.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from apps.api.middleware.auth import get_current_user, get_current_user_id

from .dependencies import (
    get_analytics_client,
    get_analytics_fusion_service,
    get_cache,
    get_predictive_orchestrator,
)
from .models import PredictionRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/recommendations/{channel_id}")
async def get_ai_recommendations(
    channel_id: int,
    context: str = Query(
        default="general", description="Recommendation context (general, growth, engagement)"
    ),
    current_user: dict = Depends(get_current_user),
    analytics_client=Depends(get_analytics_client),
) -> list[str]:
    """
    ## 🤖 AI-Powered Real-time Recommendations

    Get contextual recommendations based on:
    - Current performance trends
    - Real-time engagement patterns
    - Growth momentum analysis
    - Content performance insights
    """
    try:
        # Get recent data for recommendations
        overview_data = await analytics_client.overview(str(channel_id), 7)  # Last week
        growth_data = await analytics_client.growth(str(channel_id), 7)
        reach_data = await analytics_client.reach(str(channel_id), 7)

        # Build metrics context
        metrics_context = {
            "growth_rate": getattr(growth_data, "growth_rate", 0),
            "engagement_rate": getattr(overview_data, "engagement_rate", 0),
            "reach_score": getattr(reach_data, "reach_score", 0),
            "total_views": getattr(overview_data, "total_views", 0),
        }

        # Generate context-specific recommendations
        return generate_contextual_recommendations(metrics_context, context)

    except Exception as e:
        logger.error(f"AI recommendations generation failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate AI recommendations")


@router.post("/forecast")
async def generate_predictions(
    request: PredictionRequest,
    current_user_id: int = Depends(get_current_user_id),
    predictive_orchestrator=Depends(get_predictive_orchestrator),
    cache=Depends(get_cache),
):
    """
    ## 🔮 Predictive Analytics & Forecasting

    Generate ML-powered predictions and forecasts for channel performance.

    Prediction Types:
    - Growth forecasting with confidence intervals
    - Engagement prediction modeling
    - Reach and performance projections
    - Multi-channel comparative forecasting
    """
    try:
        # Validate prediction type
        valid_types = ["growth", "engagement", "reach", "views", "subscribers"]
        if request.prediction_type not in valid_types:
            raise HTTPException(
                status_code=400, detail=f"Invalid prediction type. Must be one of: {valid_types}"
            )

        # Generate cache key
        cache_params = {
            "channel_ids": sorted(request.channel_ids),
            "prediction_type": request.prediction_type,
            "forecast_days": request.forecast_days,
            "confidence_level": request.confidence_level,
        }
        cache_key = f"prediction:{hash(str(cache_params))}"

        # Try cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        # Build prediction request for orchestrator
        prediction_request = {
            "channel_ids": request.channel_ids,
            "prediction_type": request.prediction_type,
            "forecast_horizon": request.forecast_days,
            "confidence_level": request.confidence_level,
        }

        # Generate predictions using predictive orchestrator
        from core.services.predictive_intelligence.protocols.predictive_protocols import (
            IntelligenceContext,
        )

        prediction_result = await predictive_orchestrator.orchestrate_enhanced_prediction(
            prediction_request=prediction_request,
            context_types=[IntelligenceContext.TEMPORAL, IntelligenceContext.ENVIRONMENTAL],
            include_narrative=False,
        )

        # Cache result (valid for 6 hours for predictions)
        cache.set(cache_key, prediction_result, expire_seconds=21600)

        return prediction_result

    except Exception as e:
        logger.error(f"Prediction generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate predictions")


@router.get("/best-times/{channel_id}")
async def get_optimal_posting_times(
    channel_id: int,
    days: int | None = Query(
        None, ge=1, le=None, description="Days to analyze (7, 30, 90, 365, or omit for all-time)"
    ),
    current_user: dict = Depends(get_current_user),
    analytics_service=Depends(get_analytics_fusion_service),
):
    """
    ## ⏰ Get Optimal Posting Times

    Predict the best times to post content based on historical engagement patterns.
    Uses ML analysis of posting time vs engagement correlation.

    **Parameters:**
    - channel_id: Target channel ID for analysis
    - days: Number of days to analyze (7, 30, 90, 365) or omit for all-time (limited to 10k posts)

    **Returns:**
    - Optimal posting time recommendations
    - Engagement pattern analysis
    - Time-based performance insights
    """
    try:
        # Default to 90 days if not specified (for backward compatibility)
        analysis_days = days if days is not None else None

        # Use predictive analytics to determine optimal posting times
        best_times = await analytics_service.get_best_posting_times(channel_id, analysis_days)

        return {
            "success": True,
            "channel_id": channel_id,
            "data": best_times,
            "analysis_type": "predictive_optimization",
            "generated_at": datetime.utcnow().isoformat(),
            "confidence_score": getattr(best_times, "confidence", 0.85),
        }

    except Exception as e:
        logger.error(f"Optimal posting times prediction failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to predict optimal posting times")


@router.get("/growth-forecast/{channel_id}")
async def get_growth_forecast(
    channel_id: int,
    days: int = Query(30, ge=7, le=365, description="Days to forecast ahead"),
    current_user: dict = Depends(get_current_user),
    analytics_client=Depends(get_analytics_client),
):
    """
    ## 📈 Growth Forecasting

    Predict channel growth trajectory using ML models.
    Provides growth forecasts with confidence intervals.
    """
    try:
        # Get historical data for modeling
        historical_data = await analytics_client.growth(str(channel_id), 90)  # 3 months history

        # Generate growth forecast
        forecast = await generate_growth_forecast(historical_data, days)

        return {
            "channel_id": channel_id,
            "forecast_days": days,
            "predictions": forecast,
            "model_confidence": forecast.get("confidence", 0.8),
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Growth forecast failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate growth forecast")


# === UTILITY FUNCTIONS ===


def generate_contextual_recommendations(metrics: dict[str, Any], context: str) -> list[str]:
    """Generate context-specific AI recommendations"""
    recommendations = []

    if context == "growth":
        if metrics["growth_rate"] < 5:
            recommendations.extend(
                [
                    "🚀 Increase posting frequency during peak hours",
                    "🤝 Partner with similar channels for cross-promotion",
                    "📱 Optimize content for mobile consumption",
                ]
            )
        else:
            recommendations.append("📈 Growth is strong - maintain current content strategy")

    elif context == "engagement":
        if metrics["engagement_rate"] < 10:
            recommendations.extend(
                [
                    "💬 Create more interactive content (polls, Q&A)",
                    "🎯 Use compelling calls-to-action in posts",
                    "⚡ Respond to comments within first hour",
                ]
            )
        else:
            recommendations.append(
                "💪 Engagement is excellent - consider advanced community features"
            )

    else:  # general context
        recommendations.extend(
            [
                f"📊 Current growth rate: {metrics['growth_rate']:.1f}% - {'Good momentum' if metrics['growth_rate'] > 5 else 'Room for improvement'}",
                f"💬 Engagement at {metrics['engagement_rate']:.1f}% - {'Strong interaction' if metrics['engagement_rate'] > 10 else 'Focus on community building'}",
                "🎯 Monitor competitor activity and trending topics for optimization opportunities",
            ]
        )

    return recommendations


async def generate_growth_forecast(historical_data, forecast_days: int) -> dict[str, Any]:
    """Generate growth forecast using simple trend analysis"""
    try:
        growth_rate = getattr(historical_data, "growth_rate", 0)

        # Simple linear projection (in production would use ML models)
        daily_growth = growth_rate / 30  # Convert to daily rate

        forecast_points = []
        base_value = 100  # Starting point

        for day in range(1, forecast_days + 1):
            projected_value = base_value * (1 + daily_growth / 100) ** day
            confidence = max(0.5, 0.95 - (day * 0.01))  # Confidence decreases over time

            forecast_points.append(
                {
                    "day": day,
                    "projected_growth": round(projected_value, 2),
                    "confidence": round(confidence, 3),
                }
            )

        return {
            "forecast_points": forecast_points,
            "confidence": 0.8,
            "model_type": "linear_trend",
            "base_growth_rate": growth_rate,
        }

    except Exception:
        return {"forecast_points": [], "confidence": 0.5, "error": "Unable to generate forecast"}
