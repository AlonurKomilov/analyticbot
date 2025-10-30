"""
Analytics Orchestration Router v2 - Fully Integrated with Microservices
========================================================================

Provides API endpoints using the new analytics_fusion microservices architecture.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from apps.api.di_analytics import get_analytics_fusion_service
from core.protocols import AnalyticsFusionServiceProtocol

# ✅ FIXED: Removed prefix - now configured in main.py
router = APIRouter(tags=["Analytics Orchestration v2"])
logger = logging.getLogger(__name__)


class ComprehensiveAnalyticsRequest(BaseModel):
    """Request for comprehensive analytics pipeline"""

    channel_id: int = Field(..., description="Channel ID for analytics")
    analysis_scope: list[str] = Field(default_factory=list, description="Scope of analysis")
    time_range_days: int = Field(default=30, description="Time range in days")


class WorkflowStatusResponse(BaseModel):
    """Response for workflow status"""

    request_id: str
    status: str
    progress: dict[str, Any]
    results: dict[str, Any] | None = None
    error_message: str | None = None
    timestamp: str


async def get_orchestration_service() -> AnalyticsFusionServiceProtocol:
    """Get analytics orchestrator service instance"""
    return await get_analytics_fusion_service()


@router.post("/workflows/comprehensive", response_model=WorkflowStatusResponse)
async def execute_comprehensive_analytics(
    request: ComprehensiveAnalyticsRequest,
    orchestrator: AnalyticsFusionServiceProtocol = Depends(get_orchestration_service),
):
    """Execute comprehensive analytics workflow using new microservices"""
    try:
        logger.info(f"🎼 Starting comprehensive analytics for channel {request.channel_id}")

        parameters = {
            "analysis_scope": request.analysis_scope,
            "time_range_days": request.time_range_days,
        }

        result = await orchestrator.coordinate_comprehensive_analysis(
            channel_id=request.channel_id, parameters=parameters
        )

        return WorkflowStatusResponse(
            request_id=result.get("request_id", f"req_{request.channel_id}"),
            status="completed" if result.get("success", False) else "failed",
            progress={
                "services_used": result.get("services_used", []),
                "execution_time_ms": result.get("execution_time_ms", 0),
            },
            results=result.get("results") if result.get("success", False) else None,
            error_message=result.get("errors", [None])[0] if result.get("errors") else None,
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"❌ Comprehensive analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Comprehensive analytics failed: {str(e)}")


@router.get("/health", response_model=dict[str, Any])
async def get_orchestration_health(
    orchestrator: AnalyticsFusionServiceProtocol = Depends(get_orchestration_service),
):
    """Get orchestration health status"""
    try:
        logger.info("🏥 Checking orchestration health")

        health_data = await orchestrator.health_check()

        return {
            "service_status": health_data.get("status", "unknown"),
            "health_details": health_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@router.get("/services", response_model=dict[str, Any])
async def get_available_services(
    orchestrator: AnalyticsFusionServiceProtocol = Depends(get_orchestration_service),
):
    """Get available microservices information"""
    try:
        health_data = await orchestrator.health_check()

        return {
            "service_name": orchestrator.get_service_name(),
            "health_status": health_data.get("status", "unknown"),
            "services_info": health_data.get("services", {}),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Failed to get services: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get services: {str(e)}")
