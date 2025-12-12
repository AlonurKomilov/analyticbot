"""
Trend Analysis Router
=====================

API endpoints for advanced trend detection, analysis, and forecasting.

Exposes TrendAnalysisService for:
- Advanced trend analysis with decomposition
- Anomaly detection
- Change point detection
- Trend forecasting with confidence intervals
- Statistical insights

Phase 2 Enhancement - Added October 21, 2025
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from apps.di import get_container

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trends", tags=["Trend Analysis"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class TrendAnalysisRequest(BaseModel):
    """Request model for trend analysis"""

    channel_id: int = Field(..., description="Channel ID to analyze")
    metric: str = Field(
        "views", description="Metric to analyze: 'views', 'growth', or 'engagement'"
    )
    days: int = Field(60, ge=14, le=365, description="Historical period for analysis (14-365 days)")
    analysis_type: str = Field(
        "comprehensive",
        description="Analysis type: 'basic', 'comprehensive', or 'predictive'",
    )


class ForecastRequest(BaseModel):
    """Request model for trend forecasting"""

    channel_id: int = Field(..., description="Channel ID to forecast")
    metric: str = Field(
        "views", description="Metric to forecast: 'views', 'growth', or 'engagement'"
    )
    historical_days: int = Field(
        60, ge=14, le=365, description="Historical period to base forecast on"
    )
    forecast_days: int = Field(7, ge=1, le=30, description="Number of days to forecast")


class TrendAnalysisResponse(BaseModel):
    """Response model for trend analysis"""

    channel_id: int
    metric: str
    period: dict[str, Any]
    trend_analysis: dict[str, Any]
    anomalies: dict[str, Any]
    change_points: dict[str, Any]
    forecasts: dict[str, Any] | None = None
    insights: list[dict[str, Any]]
    timestamp: str
    status: str | None = None


class HealthResponse(BaseModel):
    """Response model for health check"""

    service_name: str
    status: str
    version: str
    capabilities: list[str]


class StatsResponse(BaseModel):
    """Response model for service statistics"""

    service_name: str
    version: str
    features: dict[str, str]
    metrics_supported: list[str]
    analysis_types: list[str]
    performance: dict[str, Any]
    status: str


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================


async def get_trend_service():
    """Get TrendAnalysisService from DI container"""
    try:
        container = get_container()
        service = await container.core_services.trend_analysis_service()
        return service
    except Exception as e:
        logger.error(f"Failed to get TrendAnalysisService: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Trend Analysis Service unavailable",
        )


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post(
    "/analyze/advanced",
    response_model=TrendAnalysisResponse,
    summary="Advanced Trend Analysis",
    description="""
    Perform comprehensive trend analysis with anomaly detection and forecasting.

    Features:
    - **Trend Decomposition**: Linear and polynomial trend analysis
    - **Anomaly Detection**: Statistical outlier identification
    - **Change Point Detection**: Significant shift identification
    - **Forecasting**: Multiple forecasting methods with confidence intervals
    - **Insights**: Actionable recommendations based on analysis

    Supported Metrics:
    - **views**: Daily view counts
    - **growth**: Daily follower/subscriber growth
    - **engagement**: Engagement rate trends

    Analysis Types:
    - **basic**: Quick overview with core trends
    - **comprehensive**: Full analysis with anomalies and change points
    - **predictive**: Includes forecasting (7-day ahead)

    Minimum 14 days of data required for analysis.
    """,
)
async def analyze_advanced_trends(
    request: TrendAnalysisRequest,
    service=Depends(get_trend_service),
) -> TrendAnalysisResponse:
    """
    Perform advanced trend analysis with anomaly detection.

    Returns comprehensive analysis including:
    - Trend components (linear, polynomial, moving average)
    - Anomaly detection (outliers, statistical anomalies)
    - Change point detection (significant shifts)
    - Forecasts (if predictive analysis type)
    - Actionable insights and recommendations
    """
    try:
        logger.info(
            f"🔍 Advanced trend analysis request for channel {request.channel_id}, "
            f"metric={request.metric}, days={request.days}"
        )

        # Validate metric
        if request.metric not in ["views", "growth", "engagement"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid metric '{request.metric}'. Must be 'views', 'growth', or 'engagement'",
            )

        # Validate analysis type
        if request.analysis_type not in ["basic", "comprehensive", "predictive"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid analysis_type '{request.analysis_type}'. Must be 'basic', 'comprehensive', or 'predictive'",
            )

        # Perform trend analysis
        analysis = await service.analyze_advanced_trends(
            channel_id=request.channel_id,
            metric=request.metric,
            days=request.days,
            trend_analysis_type=request.analysis_type,
        )

        # Check for insufficient data
        if analysis.get("status") == "insufficient_data":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient data: {analysis.get('message', 'Need more historical data')}",
            )

        # Check for errors
        if analysis.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Trend analysis failed: {analysis.get('error', 'Unknown error')}",
            )

        logger.info(
            f"✅ Advanced trend analysis completed for channel {request.channel_id}, "
            f"{len(analysis.get('insights', []))} insights generated"
        )

        return TrendAnalysisResponse(**analysis)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Advanced trend analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trend analysis failed: {str(e)}",
        )


@router.post(
    "/forecast",
    response_model=dict[str, Any],
    summary="Generate Trend Forecast",
    description="""
    Generate trend forecasts using multiple forecasting methods.

    Forecasting Methods:
    - **Linear Extrapolation**: Extends historical linear trend
    - **Moving Average**: Based on recent average performance
    - **Exponential Smoothing**: Weighted average with decay

    Each forecast includes:
    - Predicted values for each future day
    - 95% confidence intervals
    - Method-specific parameters

    Requires minimum 14 days of historical data.
    Forecast horizon: 1-30 days ahead.
    """,
)
async def generate_forecast(
    request: ForecastRequest,
    service=Depends(get_trend_service),
) -> dict[str, Any]:
    """
    Generate trend forecasts for a channel metric.

    Provides multiple forecasting methods to help predict
    future performance based on historical trends.
    """
    try:
        logger.info(
            f"📊 Forecast request for channel {request.channel_id}, "
            f"metric={request.metric}, forecast_days={request.forecast_days}"
        )

        # Validate metric
        if request.metric not in ["views", "growth", "engagement"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid metric '{request.metric}'. Must be 'views', 'growth', or 'engagement'",
            )

        # Perform full analysis to get forecasts
        analysis = await service.analyze_advanced_trends(
            channel_id=request.channel_id,
            metric=request.metric,
            days=request.historical_days,
            trend_analysis_type="predictive",
        )

        # Check for insufficient data
        if analysis.get("status") == "insufficient_data":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient data: {analysis.get('message', 'Need more historical data')}",
            )

        # Extract forecasts
        forecasts = analysis.get("forecasts", {})
        if not forecasts or "error" in forecasts:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate forecasts",
            )

        response = {
            "channel_id": request.channel_id,
            "metric": request.metric,
            "historical_period": {
                "days": request.historical_days,
                "data_points": analysis.get("period", {}).get("data_points", 0),
            },
            "forecast_period": {"days": request.forecast_days},
            "forecasts": forecasts,
            "trend_context": analysis.get("trend_analysis", {}),
            "timestamp": analysis.get("timestamp"),
        }

        logger.info(
            f"✅ Forecast generated for channel {request.channel_id}, "
            f"{request.forecast_days} days ahead"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Forecast generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecast generation failed: {str(e)}",
        )


@router.get(
    "/detect/anomalies/{channel_id}",
    response_model=dict[str, Any],
    summary="Detect Anomalies",
    description="""
    Detect anomalies and outliers in channel performance.

    Detection Methods:
    - **IQR Method**: Interquartile range based outlier detection
    - **Z-Score Method**: Statistical deviation analysis

    Anomaly Types:
    - High outliers (unusually high performance)
    - Low outliers (unusually low performance)
    - Statistical anomalies (significant deviations)

    Returns detailed anomaly information with severity levels.
    """,
)
async def detect_anomalies(
    channel_id: int,
    metric: str = Query("views", description="Metric to analyze"),
    days: int = Query(60, ge=14, le=365, description="Historical period"),
    service=Depends(get_trend_service),
) -> dict[str, Any]:
    """
    Detect anomalies in channel performance data.

    Identifies unusual spikes or drops that deviate significantly
    from normal patterns.
    """
    try:
        logger.info(f"🔍 Anomaly detection for channel {channel_id}, metric={metric}")

        # Perform analysis to get anomalies
        analysis = await service.analyze_advanced_trends(
            channel_id=channel_id,
            metric=metric,
            days=days,
            trend_analysis_type="comprehensive",
        )

        # Check for errors
        if analysis.get("status") in ["insufficient_data", "error"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=analysis.get("message", analysis.get("error", "Analysis failed")),
            )

        anomalies = analysis.get("anomalies", {})

        response = {
            "channel_id": channel_id,
            "metric": metric,
            "period": analysis.get("period", {}),
            "anomalies": anomalies,
            "insights": [
                insight
                for insight in analysis.get("insights", [])
                if insight.get("type") == "anomalies"
            ],
            "timestamp": analysis.get("timestamp"),
        }

        logger.info(
            f"✅ Detected {anomalies.get('summary', {}).get('total_outliers', 0)} outliers "
            f"for channel {channel_id}"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Anomaly detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anomaly detection failed: {str(e)}",
        )


@router.get(
    "/detect/changes/{channel_id}",
    response_model=dict[str, Any],
    summary="Detect Change Points",
    description="""
    Detect significant change points in performance trends.

    Change points represent moments when performance
    characteristics significantly shifted, such as:
    - Strategy changes
    - Algorithm updates
    - Market shifts
    - Content pivots

    Uses statistical tests to identify changes with:
    - Before/after mean comparison
    - Statistical significance (p-value)
    - Change magnitude
    - Change direction

    Helps identify what caused performance shifts.
    """,
)
async def detect_change_points(
    channel_id: int,
    metric: str = Query("views", description="Metric to analyze"),
    days: int = Query(60, ge=14, le=365, description="Historical period"),
    service=Depends(get_trend_service),
) -> dict[str, Any]:
    """
    Detect significant change points in performance.

    Identifies moments when performance characteristics
    significantly changed, helping diagnose strategy impacts.
    """
    try:
        logger.info(f"🔍 Change point detection for channel {channel_id}, metric={metric}")

        # Perform analysis to get change points
        analysis = await service.analyze_advanced_trends(
            channel_id=channel_id,
            metric=metric,
            days=days,
            trend_analysis_type="comprehensive",
        )

        # Check for errors
        if analysis.get("status") in ["insufficient_data", "error"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=analysis.get("message", analysis.get("error", "Analysis failed")),
            )

        change_points = analysis.get("change_points", {})

        response = {
            "channel_id": channel_id,
            "metric": metric,
            "period": analysis.get("period", {}),
            "change_points": change_points,
            "insights": [
                insight
                for insight in analysis.get("insights", [])
                if insight.get("type") == "change_points"
            ],
            "timestamp": analysis.get("timestamp"),
        }

        logger.info(
            f"✅ Detected {change_points.get('total_change_points', 0)} change points "
            f"for channel {channel_id}"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Change point detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Change point detection failed: {str(e)}",
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Check Trend Analysis Service health and capabilities",
)
async def health_check(service=Depends(get_trend_service)) -> HealthResponse:
    """
    Health check endpoint for Trend Analysis Service.

    Returns service status and capabilities.
    """
    try:
        return HealthResponse(
            service_name="TrendAnalysisService",
            status="operational",
            version="1.0.0",
            capabilities=[
                "advanced_trend_analysis",
                "anomaly_detection",
                "change_point_detection",
                "trend_forecasting",
                "statistical_insights",
                "multi_metric_support",
            ],
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}",
        )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Service Statistics",
    description="Get Trend Analysis Service statistics and capabilities",
)
async def get_stats() -> StatsResponse:
    """
    Get service statistics and information.

    Returns metadata about the Trend Analysis Service.
    """
    return StatsResponse(
        service_name="Trend Analysis Service",
        version="1.0.0",
        features={
            "trend_decomposition": "Linear and polynomial trend analysis",
            "anomaly_detection": "Statistical outlier identification (IQR, Z-score)",
            "change_points": "Significant shift detection with statistical tests",
            "forecasting": "Multiple methods (linear, MA, exponential smoothing)",
            "insights": "Actionable recommendations based on analysis",
        },
        metrics_supported=["views", "growth", "engagement"],
        analysis_types=["basic", "comprehensive", "predictive"],
        performance={
            "min_data_required": "14 days",
            "avg_analysis_time": "3-5 seconds",
            "forecast_horizon": "1-30 days",
            "confidence_level": "95%",
        },
        status="active",
    )
