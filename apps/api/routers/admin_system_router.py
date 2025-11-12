"""
Admin System Router - System Administration

Handles administrative system operations including statistics, monitoring, audit logs, and health checks.
Clean architecture: Single responsibility for system administration.

Domain: Admin system management operations
Path: /admin/system/*
"""

import logging
import os
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from apps.api.di_analytics import get_analytics_fusion_service
from apps.api.middleware.auth import (
    get_current_user,
    require_admin_user,
)
from apps.shared.performance import performance_timer

# Updated import to use new microservices
from core.protocols import AnalyticsFusionServiceProtocol

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
    analytics_service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
):
    """
    ## 📊 Get System Statistics (Admin)

    Retrieve comprehensive system statistics and health metrics.

    **Admin Only**: Requires admin role

    **Returns:**
    - System-wide statistics and health status
    """
    try:
        await require_admin_user(current_user["id"])

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
    analytics_service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
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
        await require_admin_user(current_user["id"])

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
    analytics_service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
):
    """
    ## 🏥 Get System Health (Admin)

    Check overall system health and component status.

    **Admin Only**: Requires admin role

    **Returns:**
    - Detailed system health information
    """
    try:
        await require_admin_user(current_user["id"])

        with performance_timer("admin_system_health_check"):
            health_data = await analytics_service.check_system_health()

            return {
                "status": "healthy"
                if health_data.get("all_systems_operational", False)
                else "degraded",
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


# === MTPROTO CONNECTION POOL CONFIGURATION ===


class MTProtoPoolConfig(BaseModel):
    """MTProto Connection Pool Configuration"""

    max_concurrent_users: int = Field(
        ..., description="Maximum concurrent user sessions (system-wide limit)", ge=1, le=200
    )
    max_connections_per_user: int = Field(
        ..., description="Maximum connections per user", ge=1, le=5
    )
    session_timeout: int = Field(..., description="Session timeout in seconds", ge=60, le=3600)
    connection_timeout: int = Field(..., description="Connection timeout in seconds", ge=30, le=600)
    idle_timeout: int = Field(..., description="Idle timeout in seconds", ge=30, le=600)


class MTProtoPoolStatus(BaseModel):
    """Current MTProto Connection Pool Status"""

    active_sessions: int
    max_concurrent_users: int
    max_connections_per_user: int
    session_timeout: int
    connection_timeout: int
    idle_timeout: int
    metrics: dict[str, Any] = Field(default_factory=dict)


@router.get("/mtproto/pool/config", response_model=MTProtoPoolConfig)
async def get_mtproto_pool_config(
    current_user: dict = Depends(get_current_user),
):
    """
    ## ⚙️ Get MTProto Connection Pool Configuration (Admin Only)

    Retrieve current connection pool settings.

    **Admin Only**: Requires admin role

    **Returns:**
    - Current pool configuration settings
    """
    try:
        await require_admin_user(current_user["id"])

        # Read from environment
        return MTProtoPoolConfig(
            max_concurrent_users=int(os.getenv("MTPROTO_MAX_CONNECTIONS", "10")),
            max_connections_per_user=int(os.getenv("MTPROTO_MAX_CONNECTIONS_PER_USER", "1")),
            session_timeout=int(os.getenv("MTPROTO_SESSION_TIMEOUT", "600")),
            connection_timeout=int(os.getenv("MTPROTO_CONNECTION_TIMEOUT", "300")),
            idle_timeout=int(os.getenv("MTPROTO_IDLE_TIMEOUT", "180")),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get MTProto pool config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get MTProto pool configuration")


@router.put("/mtproto/pool/config", response_model=MTProtoPoolConfig)
async def update_mtproto_pool_config(
    config: MTProtoPoolConfig,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🔧 Update MTProto Connection Pool Configuration (Admin Only)

    Update connection pool settings. Changes require MTProto worker restart to take effect.

    **Admin Only**: Requires admin role

    **Parameters:**
    - max_concurrent_users: System-wide user limit (1-200)
    - max_connections_per_user: Per-user connection limit (1-5)
    - session_timeout: Max session duration in seconds (60-3600)
    - connection_timeout: Connection establishment timeout (30-600)
    - idle_timeout: Idle disconnect timeout (30-600)

    **Returns:**
    - Updated configuration

    **Note:** Requires MTProto worker restart to apply changes
    """
    try:
        await require_admin_user(current_user["id"])

        # Update .env.development file
        env_file = ".env.development"
        if not os.path.exists(env_file):
            raise HTTPException(status_code=404, detail="Environment file not found")

        # Read existing file
        with open(env_file) as f:
            lines = f.readlines()

        # Update or add settings
        settings = {
            "MTPROTO_MAX_CONNECTIONS": str(config.max_concurrent_users),
            "MTPROTO_MAX_CONNECTIONS_PER_USER": str(config.max_connections_per_user),
            "MTPROTO_SESSION_TIMEOUT": str(config.session_timeout),
            "MTPROTO_CONNECTION_TIMEOUT": str(config.connection_timeout),
            "MTPROTO_IDLE_TIMEOUT": str(config.idle_timeout),
        }

        updated_lines = []
        found_keys = set()

        for line in lines:
            updated = False
            for key, value in settings.items():
                if line.startswith(f"{key}="):
                    updated_lines.append(f"{key}={value}\n")
                    found_keys.add(key)
                    updated = True
                    break
            if not updated:
                updated_lines.append(line)

        # Add missing settings
        for key, value in settings.items():
            if key not in found_keys:
                updated_lines.append(f"{key}={value}\n")

        # Write back
        with open(env_file, "w") as f:
            f.writelines(updated_lines)

        logger.info(
            f"Admin {current_user['id']} updated MTProto pool config: "
            f"max_users={config.max_concurrent_users}"
        )

        return config

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update MTProto pool config: {e}")
        raise HTTPException(status_code=500, detail="Failed to update MTProto pool configuration")


@router.get("/mtproto/pool/status", response_model=MTProtoPoolStatus)
async def get_mtproto_pool_status(
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📊 Get MTProto Connection Pool Status (Admin Only)

    Get current pool status including active sessions and metrics.

    **Admin Only**: Requires admin role

    **Returns:**
    - Current pool status and metrics
    """
    try:
        await require_admin_user(current_user["id"])

        # Get current configuration
        config = {
            "max_concurrent_users": int(os.getenv("MTPROTO_MAX_CONNECTIONS", "10")),
            "max_connections_per_user": int(os.getenv("MTPROTO_MAX_CONNECTIONS_PER_USER", "1")),
            "session_timeout": int(os.getenv("MTPROTO_SESSION_TIMEOUT", "600")),
            "connection_timeout": int(os.getenv("MTPROTO_CONNECTION_TIMEOUT", "300")),
            "idle_timeout": int(os.getenv("MTPROTO_IDLE_TIMEOUT", "180")),
        }

        # Try to get metrics from connection pool (if available)
        try:
            from apps.mtproto.connection_pool import get_connection_pool

            pool = get_connection_pool()
            metrics = pool.get_metrics_summary()
            active_sessions = pool.get_active_sessions_count()
        except Exception:
            # Pool not initialized yet
            metrics = {}
            active_sessions = 0

        return MTProtoPoolStatus(
            active_sessions=active_sessions,
            metrics=metrics,
            **config,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get MTProto pool status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get MTProto pool status")
