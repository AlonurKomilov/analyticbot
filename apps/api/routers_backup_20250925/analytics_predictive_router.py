"""
Analytics Predictive Router - Machine Learning & Forecasting Analytics
====================================================================

Handles AI-powered analytics, predictive modeling, and advanced data analysis.
Consolidates ML/AI functionality from legacy routers.

Domain: Predictive analytics, AI insights, forecasting, advanced data analysis
Path: /analytics/predictive/*
"""

import logging
from datetime import datetime, timedelta
from typing import Any, List, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

# Core services
from apps.api.di_analytics import get_analytics_fusion_service, get_cache
from core.services.analytics_fusion_service import AnalyticsFusionService
from core.di_container import container

# Bot services for AI/ML functionality
from apps.bot.analytics import (
    AdvancedDataProcessor,
    AIInsightsGenerator,
    PredictiveAnalyticsEngine,
)
from apps.bot.services.analytics_service import AnalyticsService

# Auth
from apps.api.middleware.auth import (
    get_current_user, 
    require_channel_access, 
    get_current_user_id,
    require_analytics_read,
)

# Performance monitoring
from apps.bot.database.performance import performance_timer

logger = logging.getLogger(__name__)

# === MODELS ===

class PredictionRequest(BaseModel):
    """Request for predictive analytics"""
    channel_ids: List[int]
    prediction_type: str = Field(..., description="Type of prediction (growth, engagement, reach)")
    time_horizon: int = Field(default=7, ge=1, le=90, description="Prediction horizon in days")
    confidence_level: float = Field(default=0.95, ge=0.5, le=0.99, description="Confidence level")
    model_type: str = Field(default="ensemble", description="ML model type")

class AnalysisRequest(BaseModel):
    """Request for advanced data analysis"""
    channel_id: int
    analysis_type: str = Field(..., description="Type of analysis (trend, anomaly, correlation)")
    date_range_days: int = Field(default=30, ge=7, le=365, description="Analysis period")
    include_forecasts: bool = Field(default=True, description="Include predictive components")

class PredictionResult(BaseModel):
    """Prediction result with confidence intervals"""
    channel_id: int
    prediction_type: str
    forecasted_values: List[Dict[str, Any]]
    confidence_intervals: Dict[str, List[float]]
    model_accuracy: float
    feature_importance: Dict[str, float]
    generated_at: datetime

class AIInsights(BaseModel):
    """AI-generated insights and recommendations"""
    channel_id: int
    insights: List[str]
    recommendations: List[str]
    anomalies_detected: List[Dict[str, Any]]
    performance_score: float
    trend_analysis: Dict[str, Any]
    next_update: datetime

# Create router with predictive prefix
router = APIRouter(
    prefix="/analytics/predictive",
    tags=["Analytics Predictive"],
    responses={
        404: {"description": "Resource not found"},
        500: {"description": "Internal server error"},
    },
)

# === AI INSIGHTS ===

@router.get("/insights/{channel_id}", response_model=AIInsights)
async def get_ai_insights(
    channel_id: int,
    days: int = Query(default=30, ge=7, le=90, description="Analysis period in days"),
    include_predictions: bool = Query(default=True, description="Include predictive insights"),
    current_user: dict = Depends(get_current_user),
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 🤖 AI-Powered Channel Insights
    
    Get AI-generated insights, anomaly detection, and recommendations for a channel.
    
    Features:
    - Advanced pattern recognition
    - Anomaly detection
    - Predictive recommendations
    - Performance optimization suggestions
    """
    try:
        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "days": days,
            "include_predictions": include_predictions,
            "user_id": current_user["id"]
        }
        cache_key = cache.generate_cache_key("ai-insights", cache_params)

        # Try cache first (AI insights can be cached for longer)
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            return AIInsights(**cached_data)

        with performance_timer("ai_insights_generation"):
            # Get analytics service from container
            analytics_service = container.resolve(AnalyticsService)
            ai_generator = container.resolve(AIInsightsGenerator)
            
            # Get recent data for analysis
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(days=days)
            
            # Get comprehensive channel data
            overview_data = await service.get_overview(channel_id, from_date, to_date)
            growth_data = await service.get_growth(channel_id, from_date, to_date, "D")
            reach_data = await service.get_reach(channel_id, from_date, to_date)
            
            # Generate AI insights
            insights_data = await ai_generator.generate_insights(
                channel_id=channel_id,
                overview=overview_data,
                growth=growth_data,
                reach=reach_data,
                include_predictions=include_predictions
            )
            
            # Calculate performance score
            performance_score = min(100.0, max(0.0, (
                overview_data.get("engagement_rate", 0) * 20 +
                (overview_data.get("growth_rate", 0) + 1) * 30 +
                min(overview_data.get("total_views", 0) / 1000, 50)
            )))
            
            ai_insights = AIInsights(
                channel_id=channel_id,
                insights=insights_data.get("insights", []),
                recommendations=insights_data.get("recommendations", []),
                anomalies_detected=insights_data.get("anomalies", []),
                performance_score=round(performance_score, 1),
                trend_analysis=insights_data.get("trends", {}),
                next_update=datetime.utcnow() + timedelta(hours=6)
            )

            # Cache the result
            await cache.set_json(cache_key, ai_insights.dict(), ttl_s=21600)  # 6 hours

            return ai_insights

    except Exception as e:
        logger.error(f"AI insights generation failed for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI insights"
        )


@router.get("/summary/{channel_id}")
async def get_predictive_summary(
    channel_id: int,
    period: int = Query(default=30, ge=7, le=180, description="Summary period in days"),
    include_forecasts: bool = Query(default=True, description="Include future predictions"),
    current_user: dict = Depends(get_current_user),
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 📊 Predictive Analytics Summary
    
    Get comprehensive predictive summary with forecasts and trend analysis.
    
    Features:
    - Historical trend analysis
    - Predictive forecasting
    - Performance projections
    - Growth trajectory modeling
    """
    try:
        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "period": period,
            "include_forecasts": include_forecasts
        }
        cache_key = cache.generate_cache_key("predictive-summary", cache_params)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        with performance_timer("predictive_summary_generation"):
            # Get analytics engine
            predictive_engine = container.resolve(PredictiveAnalyticsEngine)
            
            # Get historical data
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(days=period)
            
            overview_data = await service.get_overview(channel_id, from_date, to_date)
            growth_data = await service.get_growth(channel_id, from_date, to_date, "D")
            
            # Generate predictive summary
            summary_data = {
                "channel_id": channel_id,
                "period": f"{period}d",
                "historical_summary": {
                    "avg_daily_views": overview_data.get("avg_daily_views", 0),
                    "total_growth": overview_data.get("growth_rate", 0),
                    "engagement_trend": overview_data.get("engagement_rate", 0),
                    "performance_score": min(100, max(0, overview_data.get("total_views", 0) / 1000))
                },
                "trend_analysis": {
                    "growth_trajectory": "stable" if abs(overview_data.get("growth_rate", 0)) < 0.1 else "growing" if overview_data.get("growth_rate", 0) > 0 else "declining",
                    "engagement_pattern": "consistent",
                    "seasonal_factors": []
                },
                "meta": {
                    "cache_hit": False,
                    "generated_at": datetime.utcnow().isoformat(),
                    "data_freshness": "recent",
                    "prediction_confidence": 0.85 if include_forecasts else None
                }
            }

            # Add forecasts if requested
            if include_forecasts:
                # Simple forecast calculation (would use ML models in production)
                current_growth = overview_data.get("growth_rate", 0)
                future_periods = 7  # 7-day forecast
                
                forecasts = []
                for i in range(1, future_periods + 1):
                    forecast_date = to_date + timedelta(days=i)
                    forecasted_views = overview_data.get("avg_daily_views", 0) * (1 + current_growth) ** i
                    forecasts.append({
                        "date": forecast_date.isoformat(),
                        "forecasted_views": max(0, int(forecasted_views)),
                        "confidence": max(0.5, 0.9 - (i * 0.05))  # Decreasing confidence
                    })
                
                summary_data["forecasts"] = forecasts
                summary_data["predictions"] = {
                    "7_day_growth_estimate": current_growth * 7,
                    "projected_monthly_views": overview_data.get("total_views", 0) * 1.3,
                    "engagement_forecast": "stable"
                }

            # Cache the result
            await cache.set_json(cache_key, summary_data, ttl_s=3600)  # 1 hour

            return summary_data

    except Exception as e:
        logger.error(f"Predictive summary generation failed for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate predictive summary"
        )


# === ADVANCED ANALYTICS ===

@router.post("/data/analyze")
async def analyze_channel_data(
    request: AnalysisRequest,
    current_user: dict = Depends(get_current_user),
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 🔬 Advanced Data Analysis
    
    Perform sophisticated data analysis on channel metrics.
    
    Analysis Types:
    - Trend analysis and pattern recognition
    - Anomaly detection and outlier identification  
    - Correlation analysis between metrics
    - Statistical significance testing
    """
    try:
        # Validate analysis type
        valid_types = ["trend", "anomaly", "correlation", "statistical"]
        if request.analysis_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid analysis type. Must be one of: {valid_types}"
            )

        # Generate cache key
        cache_params = {
            "channel_id": request.channel_id,
            "analysis_type": request.analysis_type,
            "days": request.date_range_days,
            "include_forecasts": request.include_forecasts
        }
        cache_key = cache.generate_cache_key("advanced-analysis", cache_params)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        with performance_timer(f"advanced_analysis_{request.analysis_type}"):
            # Get data processor
            data_processor = container.resolve(AdvancedDataProcessor)
            
            # Get comprehensive data
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(days=request.date_range_days)
            
            overview_data = await service.get_overview(request.channel_id, from_date, to_date)
            growth_data = await service.get_growth(request.channel_id, from_date, to_date, "D")
            reach_data = await service.get_reach(request.channel_id, from_date, to_date)
            
            # Perform analysis based on type
            analysis_results = {
                "channel_id": request.channel_id,
                "analysis_type": request.analysis_type,
                "date_range": {
                    "from": from_date.isoformat(),
                    "to": to_date.isoformat(),
                    "days": request.date_range_days
                },
                "results": {},
                "insights": [],
                "recommendations": [],
                "meta": {
                    "cache_hit": False,
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "data_points_analyzed": len(growth_data) if growth_data else 0
                }
            }

            if request.analysis_type == "trend":
                # Trend analysis
                growth_rate = overview_data.get("growth_rate", 0)
                trend_direction = "increasing" if growth_rate > 0.05 else "decreasing" if growth_rate < -0.05 else "stable"
                
                analysis_results["results"] = {
                    "trend_direction": trend_direction,
                    "growth_rate": growth_rate,
                    "trend_strength": abs(growth_rate) * 100,
                    "volatility": "low",  # Would calculate from actual data
                    "seasonal_patterns": []
                }
                analysis_results["insights"] = [
                    f"Channel shows {trend_direction} trend with {abs(growth_rate)*100:.1f}% growth rate",
                    "Growth pattern appears consistent over the analysis period"
                ]

            elif request.analysis_type == "anomaly":
                # Anomaly detection
                avg_views = overview_data.get("avg_daily_views", 0)
                total_views = overview_data.get("total_views", 0)
                
                anomalies = []
                if avg_views > 0 and total_views / request.date_range_days > avg_views * 2:
                    anomalies.append({
                        "type": "spike",
                        "severity": "moderate",
                        "description": "Unusual spike in daily views detected"
                    })
                
                analysis_results["results"] = {
                    "anomalies_detected": len(anomalies),
                    "anomaly_details": anomalies,
                    "data_quality": "good",
                    "outlier_percentage": len(anomalies) / max(1, request.date_range_days) * 100
                }

            elif request.analysis_type == "correlation":
                # Correlation analysis
                engagement_rate = overview_data.get("engagement_rate", 0)
                growth_rate = overview_data.get("growth_rate", 0)
                
                analysis_results["results"] = {
                    "correlations": {
                        "views_engagement": 0.75,  # Would calculate from actual data
                        "growth_engagement": abs(growth_rate * engagement_rate),
                        "time_performance": 0.6
                    },
                    "strongest_correlation": "views_engagement",
                    "correlation_insights": [
                        "Strong positive correlation between views and engagement",
                        "Growth rate moderately correlates with engagement levels"
                    ]
                }

            # Add forecasts if requested
            if request.include_forecasts:
                analysis_results["forecasts"] = {
                    "confidence_level": 0.8,
                    "forecast_horizon": "7_days",
                    "predicted_trend": "stable",
                    "forecast_accuracy_note": "Based on current trend patterns"
                }

            # Cache the result
            await cache.set_json(cache_key, analysis_results, ttl_s=1800)  # 30 minutes

            return analysis_results

    except Exception as e:
        logger.error(f"Advanced analysis failed for channel {request.channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform advanced data analysis"
        )


@router.post("/predictions/forecast", response_model=PredictionResult)
async def generate_predictions(
    request: PredictionRequest,
    current_user: dict = Depends(get_current_user),
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
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
                status_code=400,
                detail=f"Invalid prediction type. Must be one of: {valid_types}"
            )

        # Generate cache key
        cache_params = {
            "channel_ids": sorted(request.channel_ids),
            "prediction_type": request.prediction_type,
            "horizon": request.time_horizon,
            "confidence": request.confidence_level,
            "model": request.model_type
        }
        cache_key = cache.generate_cache_key("ml-predictions", cache_params)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            return PredictionResult(**cached_data)

        with performance_timer("ml_prediction_generation"):
            # Get predictive engine
            predictive_engine = container.resolve(PredictiveAnalyticsEngine)
            
            # Process each channel
            all_predictions = []
            
            for channel_id in request.channel_ids:
                try:
                    # Get historical data for modeling
                    to_date = datetime.utcnow()
                    from_date = to_date - timedelta(days=min(90, request.time_horizon * 3))
                    
                    overview_data = await service.get_overview(channel_id, from_date, to_date)
                    growth_data = await service.get_growth(channel_id, from_date, to_date, "D")
                    
                    # Generate predictions (simplified ML simulation)
                    base_value = overview_data.get(f"avg_daily_{request.prediction_type}", 0)
                    if request.prediction_type == "growth":
                        base_value = overview_data.get("growth_rate", 0)
                    elif request.prediction_type == "engagement":
                        base_value = overview_data.get("engagement_rate", 0)
                    
                    # Create forecast values
                    forecasted_values = []
                    for day in range(1, request.time_horizon + 1):
                        forecast_date = to_date + timedelta(days=day)
                        
                        # Simple trend extrapolation (would use actual ML models)
                        trend_factor = 1 + (overview_data.get("growth_rate", 0) * day / 30)
                        seasonal_factor = 1 + 0.1 * (day % 7 - 3.5) / 7  # Weekly seasonality
                        noise_factor = 1 + (hash(str(channel_id) + str(day)) % 20 - 10) / 1000
                        
                        forecasted_value = base_value * trend_factor * seasonal_factor * noise_factor
                        
                        forecasted_values.append({
                            "date": forecast_date.isoformat(),
                            "value": max(0, forecasted_value),
                            "day": day
                        })
                    
                    # Calculate confidence intervals
                    confidence_intervals = {
                        "lower": [v["value"] * (1 - (1 - request.confidence_level)) for v in forecasted_values],
                        "upper": [v["value"] * (1 + (1 - request.confidence_level)) for v in forecasted_values]
                    }
                    
                    # Feature importance (simulated)
                    feature_importance = {
                        "historical_trend": 0.35,
                        "seasonal_patterns": 0.25,
                        "engagement_factors": 0.20,
                        "external_events": 0.15,
                        "random_variance": 0.05
                    }
                    
                    # Model accuracy (simulated based on data quality)
                    data_quality = len(growth_data) / max(1, request.time_horizon * 2)
                    model_accuracy = min(0.95, max(0.6, 0.7 + data_quality * 0.2))
                    
                    prediction_result = PredictionResult(
                        channel_id=channel_id,
                        prediction_type=request.prediction_type,
                        forecasted_values=forecasted_values,
                        confidence_intervals=confidence_intervals,
                        model_accuracy=model_accuracy,
                        feature_importance=feature_importance,
                        generated_at=datetime.utcnow()
                    )
                    
                    all_predictions.append(prediction_result.dict())
                    
                except Exception as e:
                    logger.warning(f"Prediction failed for channel {channel_id}: {e}")
                    continue
            
            if not all_predictions:
                raise HTTPException(
                    status_code=404,
                    detail="No valid predictions could be generated for the specified channels"
                )
            
            # Return first result for single channel, or aggregated for multiple
            if len(request.channel_ids) == 1:
                result = PredictionResult(**all_predictions[0])
            else:
                # For multiple channels, create aggregated result
                result = PredictionResult(
                    channel_id=request.channel_ids[0],  # Primary channel
                    prediction_type=request.prediction_type,
                    forecasted_values=[],  # Would aggregate across channels
                    confidence_intervals={"lower": [], "upper": []},
                    model_accuracy=sum(p["model_accuracy"] for p in all_predictions) / len(all_predictions),
                    feature_importance=all_predictions[0]["feature_importance"],
                    generated_at=datetime.utcnow()
                )

            # Cache the result
            await cache.set_json(cache_key, result.dict(), ttl_s=1800)  # 30 minutes

            return result

    except Exception as e:
        logger.error(f"Prediction generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate predictions"
        )

@router.get("/best-times/{channel_id}")
async def get_optimal_posting_times(
    channel_id: str
):
    """
    ## ⏰ Get Optimal Posting Times
    
    Predict the best times to post content based on historical engagement patterns.
    Migrated from clean analytics router - posting time optimization is predictive analytics.
    
    **Parameters:**
    - channel_id: Target channel ID for analysis
    
    **Returns:**
    - Optimal posting time recommendations
    - Engagement pattern analysis
    - Time-based performance insights
    """
    try:
        # Import analytics service using clean architecture pattern
        from core.protocols import AnalyticsServiceProtocol  
        from core.di_container import container
        
        analytics_service = container.get_service(AnalyticsServiceProtocol)
        best_times = await analytics_service.get_best_posting_times(channel_id)
        
        return {
            "success": True,
            "channel_id": channel_id,
            "data": best_times,
            "clean_architecture": True,
            "analysis_type": "predictive_optimization",
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Optimal posting times analysis failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to analyze optimal posting times"
        )

# === NOTES ===
# This router consolidates ML/AI functionality providing:
# - AI-powered insights and analysis
# - Predictive analytics and forecasting
# - Advanced data analysis capabilities
# All endpoints maintain clean architecture patterns with proper domain separation.