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

from apps.api.di_container.analytics_container import get_analytics_fusion_service
from core.services.analytics_fusion import AnalyticsOrchestratorService

router = APIRouter(prefix="/insights/orchestration", tags=["Analytics Orchestration v2"])
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


async def get_orchestration_service() -> AnalyticsOrchestratorService:
    """Get analytics orchestrator service instance"""
    return await get_analytics_fusion_service()


@router.post("/workflows/comprehensive", response_model=WorkflowStatusResponse)
async def execute_comprehensive_analytics(
    request: ComprehensiveAnalyticsRequest,
    orchestrator: AnalyticsOrchestratorService = Depends(get_orchestration_service),
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
            request_id=result.request_id,
            status="completed" if result.success else "failed",
            progress={
                "services_used": result.services_used,
                "execution_time_ms": result.execution_time_ms,
            },
            results=result.results if result.success else None,
            error_message=result.errors[0] if result.errors else None,
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"❌ Comprehensive analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Comprehensive analytics failed: {str(e)}")


@router.get("/health", response_model=dict[str, Any])
async def get_orchestration_health(
    orchestrator: AnalyticsOrchestratorService = Depends(get_orchestration_service),
):
    """Get orchestration health status"""
    try:
        logger.info("🏥 Checking orchestration health")

        services_health = await orchestrator.get_service_health()
        healthy_services = sum(1 for health in services_health.values() if health.is_healthy)
        total_services = len(services_health)

        return {
            "service_status": ("healthy" if healthy_services == total_services else "degraded"),
            "total_requests": orchestrator.request_count,
            "services_health": {
                name: "healthy" if health.is_healthy else "unhealthy"
                for name, health in services_health.items()
            },
            "orchestrator_running": orchestrator.is_running,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@router.get("/services", response_model=dict[str, Any])
async def get_available_services(
    orchestrator: AnalyticsOrchestratorService = Depends(get_orchestration_service),
):
    """Get available microservices information"""
    try:
        from core.services.analytics_fusion import MICROSERVICES

        services_health = await orchestrator.get_service_health()

        services_info = {}
        for service_name, service_config in MICROSERVICES.items():
            health = services_health.get(service_name)
            services_info[service_name] = {
                "description": service_config["description"],
                "responsibility": service_config["responsibility"],
                "status": "healthy" if health and health.is_healthy else "unknown",
            }

        return {
            "available_services": services_info,
            "total_services": len(services_info),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Failed to get services: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get services: {str(e)}")
