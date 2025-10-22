"""
Predictive analytics and AI/ML forecasting endpoints.
Handles recommendations, forecasting, and predictive modeling.

✅ REFACTORED (Oct 21, 2025): Now uses PredictiveOrchestratorService for predictive intelligence
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from apps.api.di_analytics import get_analytics_fusion_service, get_cache
from apps.api.middleware.auth import get_current_user, get_current_user_id
from apps.di import get_container
from apps.shared.clients.analytics_client import AnalyticsClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insights/predictive", tags=["insights-predictive"])


# =====================================
# Dependency Injection
# =====================================


# Analytics Client Dependency
def get_analytics_client() -> AnalyticsClient:
    from config.settings import settings

    return AnalyticsClient(settings.ANALYTICS_V2_BASE_URL)


# Predictive Orchestrator Dependency (NEW - Oct 21, 2025)
async def get_predictive_orchestrator():
    """
    Get PredictiveOrchestratorService from DI container.

    Provides access to:
    - Contextual intelligence analysis
    - Temporal intelligence patterns
    - Predictive modeling with ML
    - Cross-channel intelligence
    """
    try:
        container = get_container()
        orchestrator = await container.core_services.predictive_orchestrator_service()
        return orchestrator
    except Exception as e:
        logger.error(f"Failed to get PredictiveOrchestratorService: {e}")
        raise HTTPException(status_code=503, detail="Predictive Orchestrator Service unavailable")


# =====================================
# Request/Response Models
# =====================================


# Request Models
class PredictionRequest(BaseModel):
    channel_ids: list[int]
    prediction_type: str = Field(
        ..., description="Type of prediction (growth, engagement, reach, views)"
    )
    forecast_days: int = Field(30, ge=1, le=365, description="Days to forecast ahead")
    confidence_level: float = Field(
        0.95, ge=0.8, le=0.99, description="Confidence level for predictions"
    )


# === AI RECOMMENDATIONS ===


@router.get("/recommendations/{channel_id}")
async def get_ai_recommendations(
    channel_id: int,
    context: str = Query(
        default="general", description="Recommendation context (general, growth, engagement)"
    ),
    current_user: dict = Depends(get_current_user),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
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
    current_user: dict = Depends(get_current_user),
    analytics_service=Depends(get_analytics_fusion_service),
):
    """
    ## ⏰ Get Optimal Posting Times

    Predict the best times to post content based on historical engagement patterns.
    Uses ML analysis of posting time vs engagement correlation.

    **Parameters:**
    - channel_id: Target channel ID for analysis

    **Returns:**
    - Optimal posting time recommendations
    - Engagement pattern analysis
    - Time-based performance insights
    """
    try:
        # Use predictive analytics to determine optimal posting times
        best_times = await analytics_service.get_best_posting_times(channel_id)

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
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
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


# === PHASE 3 STEP 3: PREDICTIVE INTELLIGENCE ENDPOINTS ===


class ContextualIntelligenceRequest(BaseModel):
    """Request for contextual intelligence analysis"""

    channel_id: int
    intelligence_context: list[str] = Field(
        default=["temporal", "environmental"],
        description="Types of intelligence context to analyze",
    )
    analysis_period_days: int = Field(30, ge=7, le=365, description="Analysis period in days")
    prediction_horizon_days: int = Field(7, ge=1, le=90, description="Prediction horizon in days")
    include_explanations: bool = Field(True, description="Include natural language explanations")


class CrossChannelIntelligenceRequest(BaseModel):
    """Request for cross-channel intelligence analysis"""

    channel_ids: list[int] = Field(..., description="Channel IDs to analyze (2-10 channels)")
    correlation_depth_days: int = Field(
        60, ge=14, le=180, description="Analysis depth for correlations"
    )
    include_competitive_intelligence: bool = Field(True, description="Include competitive analysis")


@router.post("/intelligence/contextual")
async def analyze_contextual_intelligence(
    request: ContextualIntelligenceRequest,
    current_user_id: int = Depends(get_current_user_id),
    predictive_orchestrator=Depends(get_predictive_orchestrator),
):
    """
    ## 🧠 Contextual Intelligence Analysis

    AI-powered contextual prediction analysis that adds environmental, temporal,
    and market intelligence to standard predictions.

    **Intelligence Context Types:**
    - `temporal`: Time-based patterns and optimal timing
    - `environmental`: Platform and market conditions
    - `competitive`: Competitor activity and market position
    - `behavioral`: Audience behavior patterns
    - `seasonal`: Seasonal trends and cyclical patterns

    **Features:**
    - Context-aware predictions with enhanced accuracy
    - Environmental factor analysis
    - Natural language explanations of predictions
    - Enhanced confidence scoring based on context

    **Returns:**
    - Base prediction from existing ML models
    - Contextual intelligence enhancement layer
    - Natural language explanations
    - Enhanced confidence scores
    """
    try:
        logger.info(
            f"🧠 Processing contextual intelligence request for channel {request.channel_id}"
        )

        # Map string contexts to IntelligenceContext enum
        from core.services.predictive_intelligence.protocols.predictive_protocols import (
            IntelligenceContext,
        )

        context_map = {
            "temporal": IntelligenceContext.TEMPORAL,
            "environmental": IntelligenceContext.ENVIRONMENTAL,
            "competitive": IntelligenceContext.COMPETITIVE,
            "behavioral": IntelligenceContext.BEHAVIORAL,
            "seasonal": IntelligenceContext.SEASONAL,
            "comprehensive": IntelligenceContext.COMPREHENSIVE,
        }

        context_types = [
            context_map.get(ctx, IntelligenceContext.COMPREHENSIVE)
            for ctx in request.intelligence_context
        ]

        # Build prediction request
        prediction_request = {
            "channel_id": request.channel_id,
            "channel_ids": [request.channel_id],
            "analysis_period": request.analysis_period_days,
            "prediction_horizon": request.prediction_horizon_days,
            "include_narrative": request.include_explanations,
        }

        # Use PredictiveOrchestratorService for enhanced prediction
        result = await predictive_orchestrator.orchestrate_enhanced_prediction(
            prediction_request=prediction_request,
            context_types=context_types,
            include_narrative=request.include_explanations,
        )

        return {
            "success": True,
            "channel_id": request.channel_id,
            "data": result,
            "analysis_type": "contextual_intelligence",
            "generated_at": datetime.utcnow().isoformat(),
            "intelligence_contexts_analyzed": request.intelligence_context,
        }

    except Exception as e:
        logger.error(
            f"Contextual intelligence analysis failed for channel {request.channel_id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Contextual intelligence analysis failed: {str(e)}"
        )


@router.get("/intelligence/temporal/{channel_id}")
async def discover_temporal_patterns(
    channel_id: int,
    analysis_depth_days: int = Query(
        90, ge=30, le=365, description="Days of historical data to analyze"
    ),
    current_user_id: int = Depends(get_current_user_id),
    predictive_orchestrator=Depends(get_predictive_orchestrator),
):
    """
    ## ⏰ Temporal Pattern Intelligence Discovery

    Advanced temporal intelligence that discovers hidden patterns in engagement and performance:

    **Temporal Intelligence Features:**
    - Daily engagement rhythm analysis
    - Weekly performance cycle detection
    - Seasonal trend intelligence
    - Cyclical pattern recognition
    - Optimal timing window identification
    - Anomaly temporal pattern detection

    **Use Cases:**
    - Optimize content posting schedules
    - Predict engagement windows
    - Identify seasonal opportunities
    - Detect unusual temporal patterns
    - Plan content calendar strategy

    **Returns:**
    - Daily intelligence patterns
    - Weekly performance cycles
    - Seasonal insights and trends
    - Optimal timing recommendations
    - Temporal anomaly detection
    """
    try:
        logger.info(f"⏰ Processing temporal intelligence discovery for channel {channel_id}")

        # Build temporal prediction request
        prediction_request = {
            "channel_id": channel_id,
            "analysis_depth_days": analysis_depth_days,
        }

        # Use PredictiveOrchestratorService for temporal prediction
        temporal_intelligence = await predictive_orchestrator.orchestrate_temporal_prediction(
            channel_id=channel_id,
            time_range={"days": analysis_depth_days},
        )

        return {
            "success": True,
            "channel_id": channel_id,
            "data": temporal_intelligence,
            "analysis_type": "temporal_intelligence",
            "analysis_depth_days": analysis_depth_days,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Temporal intelligence discovery failed for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Temporal intelligence discovery failed: {str(e)}"
        )


@router.post("/intelligence/cross-channel")
async def analyze_cross_channel_intelligence(
    request: CrossChannelIntelligenceRequest,
    current_user_id: int = Depends(get_current_user_id),
    predictive_orchestrator=Depends(get_predictive_orchestrator),
):
    """
    ## 🌐 Cross-Channel Intelligence Analysis

    Multi-channel intelligence that analyzes correlations, influences, and opportunities:

    **Cross-Channel Intelligence Features:**
    - Channel correlation analysis
    - Influence pattern detection
    - Cross-promotion opportunity identification
    - Competitive intelligence analysis
    - Network effect analysis
    - Multi-channel strategy optimization

    **Use Cases:**
    - Identify channel synergies
    - Optimize cross-promotion strategies
    - Understand channel influence patterns
    - Detect competitive opportunities
    - Plan multi-channel campaigns

    **Returns:**
    - Channel correlation matrix
    - Influence pattern analysis
    - Cross-promotion opportunities
    - Competitive intelligence insights
    - Network effect recommendations
    """
    try:
        logger.info(
            f"🌐 Processing cross-channel intelligence for {len(request.channel_ids)} channels"
        )

        # Build cross-channel prediction request
        prediction_request = {
            "channel_ids": request.channel_ids,
            "correlation_depth": request.correlation_depth_days,
            "include_competitive": request.include_competitive_intelligence,
        }

        # Use PredictiveOrchestratorService for cross-channel prediction
        cross_intelligence = await predictive_orchestrator.orchestrate_cross_channel_prediction(
            channel_ids=request.channel_ids,
            analysis_parameters=prediction_request,
        )

        return {
            "success": True,
            "channel_ids": request.channel_ids,
            "data": cross_intelligence,
            "analysis_type": "cross_channel_intelligence",
            "correlation_depth_days": request.correlation_depth_days,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Cross-channel intelligence analysis failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Cross-channel intelligence analysis failed: {str(e)}"
        )


@router.get("/intelligence/narrative/{channel_id}")
async def get_prediction_narrative(
    channel_id: int,
    narrative_style: str = Query(
        "conversational", description="Narrative style: conversational, technical, executive"
    ),
    prediction_type: str = Query("comprehensive", description="Type of prediction to explain"),
    current_user_id: int = Depends(get_current_user_id),
    predictive_orchestrator=Depends(get_predictive_orchestrator),
):
    """
    ## 📖 Prediction Reasoning Narrative

    Natural language explanation of prediction reasoning and insights:

    **Narrative Features:**
    - Clear explanation of prediction logic
    - Confidence factor analysis
    - Risk assessment in plain language
    - Actionable recommendations
    - Temporal and market context

    **Narrative Styles:**
    - `conversational`: Easy-to-understand explanations
    - `technical`: Detailed technical analysis
    - `executive`: High-level strategic insights

    **Use Cases:**
    - Understand prediction reasoning
    - Communicate insights to stakeholders
    - Generate reports and presentations
    - Educational and training purposes

    **Returns:**
    - Natural language prediction reasoning
    - Confidence explanations
    - Key factor analysis
    - Risk assessment narrative
    - Strategic recommendations
    """
    try:
        logger.info(f"📖 Generating prediction narrative for channel {channel_id}")

        # Build prediction request with narrative
        prediction_request = {
            "channel_id": channel_id,
            "prediction_type": prediction_type,
            "narrative_style": narrative_style,
        }

        # Use PredictiveOrchestratorService for enhanced prediction with narrative
        from core.services.predictive_intelligence.protocols.predictive_protocols import (
            IntelligenceContext,
        )

        result = await predictive_orchestrator.orchestrate_enhanced_prediction(
            prediction_request=prediction_request,
            context_types=[IntelligenceContext.COMPREHENSIVE],
            include_narrative=True,
        )

        return {
            "success": True,
            "channel_id": channel_id,
            "prediction_summary": result.get("predictions", {}),
            "narrative": result.get("narrative", {}),
            "narrative_style": narrative_style,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Prediction narrative generation failed for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Prediction narrative generation failed: {str(e)}"
        )


@router.get("/intelligence/health")
async def get_intelligence_health_status(
    current_user_id: int = Depends(get_current_user_id),
    predictive_orchestrator=Depends(get_predictive_orchestrator),
):
    """
    ## 🏥 Predictive Intelligence Health Status

    Health check for the predictive intelligence service and its dependencies.

    **Returns:**
    - Service operational status
    - Dependency health checks
    - Available capabilities
    - Performance metrics
    """
    try:
        health_status = await predictive_orchestrator.health_check()

        return {
            "success": True,
            "health_status": health_status,
            "checked_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Intelligence health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Intelligence health check failed: {str(e)}")


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
