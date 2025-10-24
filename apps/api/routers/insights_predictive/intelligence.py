"""
Intelligence analysis endpoints.

This module handles advanced predictive intelligence including contextual analysis,
temporal patterns, cross-channel intelligence, narratives, and health monitoring.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from apps.api.middleware.auth import get_current_user_id

from .dependencies import get_predictive_orchestrator
from .models import ContextualIntelligenceRequest, CrossChannelIntelligenceRequest

logger = logging.getLogger(__name__)

router = APIRouter()


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
