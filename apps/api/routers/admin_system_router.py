"""
Admin System Router - System Administration

Handles administrative system operations including statistics, monitoring, audit logs, and health checks.
Clean architecture: Single responsibility for system administration.

Domain: Admin system management operations
Path: /admin/system/*
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from apps.api.di_container.analytics_container import get_analytics_fusion_service
from apps.api.middleware.auth import (
    get_current_user,
    require_admin_role,
)

# ✅ CLEAN ARCHITECTURE: Use apps performance abstraction instead of direct infra import
from apps.shared.performance import performance_timer
from core.services.analytics_fusion_service import AnalyticsFusionService

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/admin/system",
    tags=["Admin - System Management"],
    responses={404: {"description": "Not found"}},
)

# === ADMIN SYSTEM MODELS ===


class SystemStats(BaseModel):
    total_users: int
    total_channels: int
    total_posts: int
    total_views: int
    active_channels: int
    system_health: str


class AuditLogEntry(BaseModel):
    id: int
    action: str
    admin_user_id: int
    target_type: str
    target_id: int | None = None
    timestamp: datetime
    details: dict[str, Any] = Field(default_factory=dict)


# === ADMIN SYSTEM ENDPOINTS ===


@router.get("/stats", response_model=SystemStats)
async def get_system_statistics(
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
):
    """
    ## 📊 Get System Statistics (Admin)

    Retrieve comprehensive system statistics and health metrics.

    **Admin Only**: Requires admin role

    **Returns:**
    - System-wide statistics and health status
    """
    try:
        await require_admin_role(current_user["id"])

        with performance_timer("admin_system_stats_fetch"):
            stats = await analytics_service.get_system_statistics_admin()

            return SystemStats(
                total_users=stats.get("total_users", 0),
                total_channels=stats.get("total_channels", 0),
                total_posts=stats.get("total_posts", 0),
                total_views=stats.get("total_views", 0),
                active_channels=stats.get("active_channels", 0),
                system_health=stats.get("system_health", "unknown"),
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin system stats fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch system statistics")


@router.get("/audit/recent", response_model=list[AuditLogEntry])
async def get_recent_admin_actions(
    limit: int = Query(50, ge=1, le=500),
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
):
    """
    ## 📋 Get Recent Admin Actions

    Retrieve recent administrative actions and audit logs.

    **Admin Only**: Requires admin role

    **Parameters:**
    - limit: Maximum number of audit entries to return (1-500)

    **Returns:**
    - List of recent administrative actions
    """
    try:
        await require_admin_role(current_user["id"])

        with performance_timer("admin_audit_logs_fetch"):
            audit_logs = await analytics_service.get_admin_audit_logs(limit=limit)

            return [
                AuditLogEntry(
                    id=log["id"],
                    action=log["action"],
                    admin_user_id=log["admin_user_id"],
                    target_type=log["target_type"],
                    target_id=log.get("target_id"),
                    timestamp=log["timestamp"],
                    details=log.get("details", {}),
                )
                for log in audit_logs
            ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin audit logs fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch admin audit logs")


@router.get("/health")
async def get_system_health(
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
):
    """
    ## 🏥 Get System Health (Admin)

    Check overall system health and component status.

    **Admin Only**: Requires admin role

    **Returns:**
    - Detailed system health information
    """
    try:
        await require_admin_role(current_user["id"])

        with performance_timer("admin_system_health_check"):
            health_data = await analytics_service.check_system_health()

            return {
                "status": (
                    "healthy" if health_data.get("all_systems_operational", False) else "degraded"
                ),
                "timestamp": datetime.now().isoformat(),
                "components": health_data.get("components", {}),
                "overall_score": health_data.get("health_score", 0),
                "issues": health_data.get("issues", []),
                "checked_by": current_user["id"],
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to check system health")
