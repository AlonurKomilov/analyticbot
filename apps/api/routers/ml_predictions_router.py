"""
ML Predictions Router
====================

API endpoints for Machine Learning predictions (Growth, Engagement, Content Analysis)
Uses Celery for background processing to avoid blocking the event loop.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from apps.celery.celery_app import celery_app
from core.services.deep_learning.growth.growth_forecaster_service import (
    GrowthForecasterService,
)
from core.services.deep_learning.infrastructure.gpu_config import GPUConfigService
from core.services.deep_learning.infrastructure.model_loader import ModelLoader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


# ==================== Pydantic Models ====================


class GrowthPredictionRequest(BaseModel):
    """Request model for growth prediction"""

    channel_id: int = Field(..., description="Telegram channel ID", ge=1)
    forecast_horizon: int = Field(7, description="Number of days to forecast", ge=1, le=30)
    include_uncertainty: bool = Field(True, description="Include confidence intervals")

    class Config:
        json_schema_extra = {
            "example": {
                "channel_id": 123,
                "forecast_horizon": 7,
                "include_uncertainty": True,
            }
        }


class TaskResponse(BaseModel):
    """Response model for task submission"""

    task_id: str = Field(..., description="Celery task ID for status checking")
    channel_id: int = Field(..., description="Channel ID")
    status: str = Field(..., description="Task status (processing, queued)")
    message: str = Field(..., description="Human-readable message")
    estimated_time: str = Field(..., description="Estimated completion time")
    check_status_at: str = Field(..., description="Endpoint to check task status")


class TaskStatusResponse(BaseModel):
    """Response model for task status check"""

    status: str = Field(..., description="Task status (queued, processing, complete, failed)")
    progress: int | None = Field(default=None, description="Progress percentage (0-100)")
    result: dict[str, Any] | None = Field(default=None, description="Task result (when complete)")
    error: str | None = Field(default=None, description="Error message (when failed)")


# ==================== Dependencies ====================


async def get_growth_forecaster() -> GrowthForecasterService:
    """Dependency to get GrowthForecasterService instance"""
    try:
        gpu_config = GPUConfigService()
        model_loader = ModelLoader()
        return GrowthForecasterService(gpu_config=gpu_config, model_loader=model_loader)
    except Exception as e:
        logger.error(f"Failed to initialize GrowthForecasterService: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML service temporarily unavailable",
        )


# ==================== Endpoints ====================


@router.post(
    "/predict-growth",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Predict Channel Growth",
    description="""
    Submit a growth prediction task for a Telegram channel.

    This endpoint returns immediately with a task_id. The actual prediction
    runs in the background (Celery worker) to avoid blocking the API.

    Use the task_id to check status at `/ml/task-status/{task_id}`.

    **Performance**:
    - API response: <100ms
    - Background processing: 30-60 seconds
    """,
)
async def predict_growth(
    request: GrowthPredictionRequest,
    service: GrowthForecasterService = Depends(get_growth_forecaster),
):
    """
    Submit growth prediction task to Celery.

    Returns task_id for status checking - does NOT block waiting for result.
    """
    try:
        # NOTE: In production, fetch actual historical data from database
        # For now, use a placeholder that Celery task will handle
        sample_data = {
            "data": [
                {"date": "2025-10-01", "subscribers": 1000, "views": 5000},
                {"date": "2025-10-02", "subscribers": 1010, "views": 5100},
                {"date": "2025-10-03", "subscribers": 1025, "views": 5300},
                {"date": "2025-10-04", "subscribers": 1040, "views": 5450},
                {"date": "2025-10-05", "subscribers": 1055, "views": 5600},
            ]
        }

        # Submit to Celery (non-blocking)
        result = await service.predict_growth_via_celery(
            channel_id=request.channel_id,
            data=sample_data,
            forecast_horizon=request.forecast_horizon,
            include_uncertainty=request.include_uncertainty,
        )

        return TaskResponse(**result)

    except Exception as e:
        logger.error(f"Failed to submit prediction task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit prediction task: {str(e)}",
        )


@router.get(
    "/task-status/{task_id}",
    response_model=TaskStatusResponse,
    summary="Check ML Task Status",
    description="""
    Check the status of a Machine Learning task.

    **Status Values**:
    - `queued`: Task waiting for worker
    - `processing`: Task currently running (includes progress %)
    - `complete`: Task finished successfully (includes result)
    - `failed`: Task failed (includes error message)
    """,
)
async def get_task_status(task_id: str):
    """
    Check status of ML prediction task.

    Returns current status and result (if complete).
    """
    try:
        # Get task from Celery
        task = celery_app.AsyncResult(task_id)

        # Check task state
        if task.state == "PENDING":
            return TaskStatusResponse(status="queued", progress=0)

        elif task.state == "PROGRESS":
            # Task is running with progress updates
            info = task.info or {}
            return TaskStatusResponse(status="processing", progress=info.get("progress", 0))

        elif task.state == "SUCCESS":
            # Task completed successfully
            return TaskStatusResponse(status="complete", progress=100, result=task.result)

        elif task.state == "FAILURE":
            # Task failed
            return TaskStatusResponse(status="failed", error=str(task.info))

        else:
            # Unknown state
            return TaskStatusResponse(status=task.state.lower(), progress=None)

    except Exception as e:
        logger.error(f"Failed to check task status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check task status: {str(e)}",
        )


@router.get(
    "/health",
    summary="ML Service Health",
    description="Check health and statistics of ML services",
)
async def ml_service_health(
    service: GrowthForecasterService = Depends(get_growth_forecaster),
):
    """
    Get ML service health statistics.

    Returns device info, model status, cache stats, etc.
    """
    try:
        health = service.get_service_health()
        return {"status": "healthy", "services": {"growth_forecaster": health}}
    except Exception as e:
        logger.error(f"Failed to get service health: {e}", exc_info=True)
        return {"status": "unhealthy", "error": str(e)}


# ==================== Admin Endpoints ====================


@router.post(
    "/clear-cache",
    summary="Clear ML Cache",
    description="Clear prediction cache (admin only)",
)
async def clear_ml_cache(
    service: GrowthForecasterService = Depends(get_growth_forecaster),
):
    """
    Clear ML prediction cache.

    Use this when models are updated or to free memory.
    """
    try:
        service.clear_cache()
        return {"status": "success", "message": "ML prediction cache cleared"}
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}",
        )
