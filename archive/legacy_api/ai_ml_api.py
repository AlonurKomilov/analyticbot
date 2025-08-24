"""
🤖 AI/ML API - Advanced analytics and AI-powered insights API

Features:
- Content analysis and optimization
- Engagement prediction
- Churn risk assessment
- Real-time insights
- Performance analytics
- Automated recommendations
"""

import logging
from datetime import datetime
from typing import Any

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from apps.bot.services.ml.churn_predictor import ChurnPredictor
from apps.bot.services.ml.content_optimizer import ContentOptimizer
from apps.bot.services.ml.engagement_analyzer import EngagementAnalyzer
from apps.bot.services.ml.prediction_service import PredictionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentAnalysisRequest(BaseModel):
    text: str = Field(..., description="Content text to analyze", max_length=5000)
    media_urls: list[str] | None = Field(None, description="List of media URLs")
    target_audience: str = Field("general", description="Target audience type")
    channel_id: int | None = Field(None, description="Channel ID for context")
    scheduled_time: datetime | None = Field(None, description="Scheduled posting time")


class ContentAnalysisResponse(BaseModel):
    overall_score: float = Field(..., description="Overall content score (0-100)")
    content_analysis: dict[str, Any]
    engagement_prediction: dict[str, Any] | None
    optimization_recommendations: list[str]
    hashtag_suggestions: list[str]
    optimal_timing: dict[str, Any] | None
    publishing_score: dict[str, Any]
    timestamp: datetime


class ChurnRiskRequest(BaseModel):
    user_id: int = Field(..., description="User ID to analyze")
    channel_id: int = Field(..., description="Channel ID for context")
    force_refresh: bool = Field(False, description="Force fresh analysis")


class ChurnRiskResponse(BaseModel):
    user_id: int
    churn_probability: float = Field(..., description="Churn probability (0-1)")
    risk_level: str = Field(..., description="Risk level: low/medium/high/critical")
    confidence: float = Field(..., description="Prediction confidence (0-1)")
    primary_risk_factors: list[dict[str, Any]]
    retention_strategies: list[dict[str, Any]]
    immediate_actions: list[str]
    success_probability: float
    user_segment: str
    analysis_date: datetime


class PerformanceReportRequest(BaseModel):
    channel_id: int = Field(..., description="Channel ID to analyze")
    period_days: int = Field(30, description="Analysis period in days", ge=1, le=90)
    include_predictions: bool = Field(True, description="Include performance predictions")
    include_churn_analysis: bool = Field(True, description="Include churn risk analysis")


class RealTimeInsightsRequest(BaseModel):
    channel_id: int = Field(..., description="Channel ID for insights")
    lookback_hours: int = Field(24, description="Lookback period in hours", ge=1, le=168)


class HealthResponse(BaseModel):
    status: str
    services: dict[str, Any]
    timestamp: datetime
    version: str = "2.5.0"


app = FastAPI(
    title="🤖 AnalyticBot AI/ML API",
    description="Advanced analytics and AI-powered insights for AnalyticBot",
    version="2.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
ml_services = {}


async def get_ml_services():
    """Dependency to get ML services"""
    if not ml_services:
        raise HTTPException(status_code=503, detail="ML services not initialized")
    return ml_services


@app.on_event("startup")
async def startup_event():
    """Initialize ML services on startup"""
    try:
        logger.info("🚀 Starting AI/ML API services...")
        prediction_service = PredictionService()
        content_optimizer = ContentOptimizer()
        churn_predictor = ChurnPredictor()
        await prediction_service.initialize_models()
        await churn_predictor.initialize_model()
        engagement_analyzer = EngagementAnalyzer(
            prediction_service=prediction_service,
            content_optimizer=content_optimizer,
            churn_predictor=churn_predictor,
        )
        ml_services.update(
            {
                "prediction_service": prediction_service,
                "content_optimizer": content_optimizer,
                "churn_predictor": churn_predictor,
                "engagement_analyzer": engagement_analyzer,
            }
        )
        logger.info("✅ AI/ML services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize ML services: {e}")
        raise


@app.get("/", response_model=dict[str, str])
async def root():
    """API root endpoint"""
    return {
        "service": "AnalyticBot AI/ML API",
        "version": "2.5.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "content_analysis": "/analyze/content",
            "churn_prediction": "/analyze/churn",
            "performance_report": "/analytics/performance",
            "real_time_insights": "/analytics/insights",
        },
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(services: dict = Depends(get_ml_services)):
    """🏥 Comprehensive health check for all ML services"""
    try:
        service_health = {}
        for service_name, service in services.items():
            if hasattr(service, "health_check"):
                service_health[service_name] = await service.health_check()
            else:
                service_health[service_name] = {"status": "available"}
        all_healthy = all(health.get("status") == "healthy" for health in service_health.values())
        return HealthResponse(
            status="healthy" if all_healthy else "degraded",
            services=service_health,
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@app.post("/analyze/content", response_model=ContentAnalysisResponse)
async def analyze_content(
    request: ContentAnalysisRequest, services: dict = Depends(get_ml_services)
):
    """
    🎯 Comprehensive content analysis with optimization recommendations

    Provides:
    - Content scoring and sentiment analysis
    - Engagement prediction
    - Optimization recommendations
    - Hashtag suggestions
    - Optimal timing recommendations
    """
    try:
        logger.info(f"📝 Analyzing content: {len(request.text)} characters")
        engagement_analyzer = services["engagement_analyzer"]
        analysis = await engagement_analyzer.analyze_content_before_publishing(
            content_text=request.text,
            media_urls=request.media_urls,
            channel_id=request.channel_id,
            scheduled_time=request.scheduled_time,
        )
        if "error" in analysis:
            raise HTTPException(status_code=422, detail=analysis["error"])
        return ContentAnalysisResponse(
            overall_score=analysis["publishing_score"]["overall_score"],
            content_analysis=analysis["content_analysis"],
            engagement_prediction=analysis.get("engagement_prediction"),
            optimization_recommendations=analysis["optimization_recommendations"],
            hashtag_suggestions=analysis["hashtag_suggestions"],
            optimal_timing=analysis.get("optimal_timing"),
            publishing_score=analysis["publishing_score"],
            timestamp=datetime.now(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Content analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/churn", response_model=ChurnRiskResponse)
async def analyze_churn_risk(request: ChurnRiskRequest, services: dict = Depends(get_ml_services)):
    """
    ⚠️ Predict user churn risk with retention recommendations

    Provides:
    - Churn probability prediction
    - Risk level assessment
    - Key risk factors identification
    - Personalized retention strategies
    - Immediate action recommendations
    """
    try:
        logger.info(f"⚠️ Analyzing churn risk for user {request.user_id}")
        churn_predictor = services["churn_predictor"]
        assessment = await churn_predictor.predict_churn_risk(
            user_id=request.user_id,
            channel_id=request.channel_id,
            force_refresh=request.force_refresh,
        )
        return ChurnRiskResponse(
            user_id=assessment.user_id,
            churn_probability=assessment.churn_probability,
            risk_level=assessment.risk_level,
            confidence=assessment.confidence,
            primary_risk_factors=assessment.primary_risk_factors,
            retention_strategies=assessment.retention_strategies,
            immediate_actions=assessment.immediate_actions,
            success_probability=assessment.success_probability,
            user_segment=assessment.user_segment,
            analysis_date=assessment.analysis_date,
        )
    except Exception as e:
        logger.error(f"❌ Churn analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Churn analysis failed: {str(e)}")


@app.post("/analytics/performance")
async def generate_performance_report(
    request: PerformanceReportRequest,
    background_tasks: BackgroundTasks,
    services: dict = Depends(get_ml_services),
):
    """
    📊 Generate comprehensive performance analysis report

    Provides:
    - Complete performance metrics
    - Content analysis insights
    - User behavior patterns
    - Churn risk analysis
    - Growth predictions
    - Actionable recommendations
    """
    try:
        logger.info(f"📊 Generating performance report for channel {request.channel_id}")
        engagement_analyzer = services["engagement_analyzer"]
        report = await engagement_analyzer.generate_performance_report(
            channel_id=request.channel_id,
            period_days=request.period_days,
            include_predictions=request.include_predictions,
            include_churn_analysis=request.include_churn_analysis,
        )
        return {
            "report_id": f"report_{request.channel_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "channel_id": report.channel_id,
            "period": {
                "start": report.period_start.isoformat(),
                "end": report.period_end.isoformat(),
                "days": request.period_days,
            },
            "metrics": {
                "total_engagement": report.total_engagement,
                "engagement_growth": report.engagement_growth,
                "content_performance_score": report.content_performance_score,
                "audience_retention_rate": report.audience_retention_rate,
            },
            "insights": [
                {
                    "type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "impact_level": insight.impact_level,
                    "confidence": insight.confidence,
                    "recommendations": insight.recommendations,
                }
                for insight in report.key_insights
            ],
            "recommendations": {
                "content": report.content_recommendations,
                "optimal_timing": report.optimal_posting_times,
                "priority_actions": report.priority_actions,
            },
            "predictions": {
                "performance_forecast": report.performance_forecast,
                "growth_predictions": report.growth_predictions,
            },
            "churn_analysis": report.churn_risk_summary if request.include_churn_analysis else None,
            "quality": {
                "analysis_completeness": report.analysis_completeness,
                "data_quality_score": report.data_quality_score,
            },
            "metadata": {
                "report_version": report.report_version,
                "generated_at": report.generated_at.isoformat(),
            },
        }
    except Exception as e:
        logger.error(f"❌ Performance report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.post("/analytics/insights")
async def get_real_time_insights(
    request: RealTimeInsightsRequest, services: dict = Depends(get_ml_services)
):
    """
    ⚡ Get real-time engagement insights and alerts

    Provides:
    - Real-time performance insights
    - Engagement trend alerts
    - Content performance anomalies
    - User behavior changes
    - Immediate optimization opportunities
    """
    try:
        logger.info(f"⚡ Getting real-time insights for channel {request.channel_id}")
        engagement_analyzer = services["engagement_analyzer"]
        insights = await engagement_analyzer.get_real_time_insights(
            channel_id=request.channel_id, lookback_hours=request.lookback_hours
        )
        return {
            "channel_id": request.channel_id,
            "lookback_hours": request.lookback_hours,
            "insights_count": len(insights),
            "insights": [
                {
                    "type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "impact_level": insight.impact_level,
                    "confidence": insight.confidence,
                    "data_points": insight.data_points,
                    "recommendations": insight.recommendations,
                    "timestamp": insight.timestamp.isoformat(),
                }
                for insight in insights
            ],
            "summary": {
                "critical_insights": len([i for i in insights if i.impact_level == "critical"]),
                "high_impact_insights": len([i for i in insights if i.impact_level == "high"]),
                "total_recommendations": sum(len(i.recommendations) for i in insights),
            },
            "generated_at": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"❌ Real-time insights failed: {e}")
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")


@app.post("/optimize/content")
async def optimize_content_real_time(text: str, services: dict = Depends(get_ml_services)):
    """⚡ Real-time content optimization for live editing"""
    try:
        content_optimizer = services["content_optimizer"]
        scores = await content_optimizer.score_content_realtime(text)
        return {
            "scores": scores,
            "recommendations": await content_optimizer._generate_optimization_tips(
                await content_optimizer._extract_content_metrics(text),
                scores.get("sentiment_score", 0.5) * 2 - 1,
                70.0,
                scores.get("overall_score", 0.5) * 100,
            )
            if hasattr(content_optimizer, "_generate_optimization_tips")
            else [],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"❌ Real-time optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": [
            "/health",
            "/analyze/content",
            "/analyze/churn",
            "/analytics/performance",
            "/analytics/insights",
        ],
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "suggestion": "Check service health at /health endpoint",
    }


if __name__ == "__main__":
    uvicorn.run("ai_ml_api:app", host="0.0.0.0", port=8002, reload=True, log_level="info")
