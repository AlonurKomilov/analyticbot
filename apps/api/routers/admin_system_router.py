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

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field

from apps.api.middleware.auth import (
    get_current_user,
    require_admin_user,
)
from apps.api.middleware.rate_limiter import RateLimitConfig, limiter
from apps.bot.multi_tenant.token_validator import (
    get_token_validator,
)
from apps.di.analytics_container import get_analytics_fusion_service
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
@limiter.limit(RateLimitConfig.ADMIN_OPERATIONS)  # 30 admin requests per minute per IP
async def get_system_statistics(
    request: Request,
    response: Response,
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


@router.get("/rate-limiter/stats")
async def get_rate_limiter_statistics(
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🚦 Get Rate Limiter Statistics (Admin)

    Retrieve statistics about global rate limiting across all bot instances.

    **Admin Only**: Requires admin role

    **Returns:**
    - Total requests processed
    - Rate limited request count
    - Backoff events count
    - Current backoff status
    - Active method statistics

    **Use Case:**
    Monitor system-wide Telegram API usage to prevent hitting rate limits.
    """
    try:
        await require_admin_user(current_user["id"])

        from apps.bot.multi_tenant.global_rate_limiter import GlobalRateLimiter

        # Get rate limiter instance
        limiter = await GlobalRateLimiter.get_instance()
        stats = limiter.get_stats()

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_requests": stats["total_requests"],
                "rate_limited_count": stats["rate_limited_count"],
                "backoff_count": stats["backoff_count"],
                "backoff_active": stats["backoff_active"],
                "backoff_remaining_seconds": round(stats["backoff_remaining"], 2),
            },
            "active_methods": stats["active_methods"],
            "health_status": "backoff" if stats["backoff_active"] else "normal",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rate limiter stats fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch rate limiter statistics")


@router.get("/bot-health/summary")
async def get_bot_health_summary(
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🏥 Get Bot Health Summary (Admin)

    Retrieve health summary for all user bots.

    **Admin Only**: Requires admin role

    **Returns:**
    - Total bot count
    - Healthy/degraded/unhealthy counts
    - Overall health status
    - Global metrics

    **Use Case:**
    Monitor overall bot system health and identify problematic bots.
    """
    try:
        await require_admin_user(current_user["id"])

        from apps.bot.multi_tenant.bot_health import get_health_monitor

        health_monitor = get_health_monitor()
        summary = health_monitor.get_health_summary()

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bot health summary fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch bot health summary")


@router.get("/bot-health/unhealthy")
async def get_unhealthy_bots(
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🚨 Get Unhealthy Bots (Admin)

    Get list of bots with health issues (degraded or unhealthy status).

    **Admin Only**: Requires admin role

    **Returns:**
    - List of user IDs with unhealthy bots
    - Detailed metrics for each unhealthy bot

    **Use Case:**
    Identify and investigate bots that need attention.
    """
    try:
        await require_admin_user(current_user["id"])

        from apps.bot.multi_tenant.bot_health import get_health_monitor

        health_monitor = get_health_monitor()
        unhealthy_user_ids = health_monitor.get_unhealthy_bots()

        # Get detailed metrics for unhealthy bots
        unhealthy_details = []
        for user_id in unhealthy_user_ids:
            metrics = health_monitor.get_metrics(user_id)
            if metrics:
                unhealthy_details.append(
                    {
                        "user_id": user_id,
                        "status": metrics.status.value,
                        "error_rate": round(metrics.error_rate * 100, 2),
                        "consecutive_failures": metrics.consecutive_failures,
                        "avg_response_time_ms": round(metrics.avg_response_time_ms, 2),
                        "is_rate_limited": metrics.is_rate_limited,
                        "last_error_type": metrics.last_error_type,
                        "last_success": (
                            metrics.last_success.isoformat() if metrics.last_success else None
                        ),
                        "last_failure": (
                            metrics.last_failure.isoformat() if metrics.last_failure else None
                        ),
                    }
                )

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "unhealthy_count": len(unhealthy_user_ids),
            "unhealthy_bots": unhealthy_details,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhealthy bots fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch unhealthy bots")


@router.get("/bot-health/{user_id}")
async def get_bot_health_metrics(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📊 Get Bot Health Metrics (Admin)

    Get detailed health metrics for a specific user's bot.

    **Admin Only**: Requires admin role

    **Returns:**
    - Complete health metrics for the specified bot
    - Status, error rates, response times, etc.

    **Use Case:**
    Deep dive into a specific bot's health and performance.
    """
    try:
        await require_admin_user(current_user["id"])

        from apps.bot.multi_tenant.bot_health import get_health_monitor

        health_monitor = get_health_monitor()
        metrics = health_monitor.get_metrics(user_id)

        if not metrics:
            raise HTTPException(
                status_code=404, detail=f"No health metrics found for user {user_id}"
            )

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "metrics": {
                "status": metrics.status.value,
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "error_rate_percent": round(metrics.error_rate * 100, 2),
                "avg_response_time_ms": round(metrics.avg_response_time_ms, 2),
                "consecutive_failures": metrics.consecutive_failures,
                "is_rate_limited": metrics.is_rate_limited,
                "last_error_type": metrics.last_error_type,
                "last_success": metrics.last_success.isoformat() if metrics.last_success else None,
                "last_failure": metrics.last_failure.isoformat() if metrics.last_failure else None,
                "last_check": metrics.last_check.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bot health metrics fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch bot health metrics")


@router.get("/circuit-breakers/summary")
async def get_circuit_breakers_summary(
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🔌 Get Circuit Breakers Summary (Admin)

    Get summary of all circuit breaker states.

    **Admin Only**: Requires admin role

    **Returns:**
    - Open circuit breakers (bots being blocked)
    - Half-open circuit breakers (recovery testing)
    - Closed circuit breakers (normal operation)

    **Use Case:**
    Monitor which bots are being protected by circuit breakers.
    """
    try:
        await require_admin_user(current_user["id"])

        from apps.bot.multi_tenant.circuit_breaker import get_circuit_breaker_registry

        registry = get_circuit_breaker_registry()
        all_states = registry.get_all_states()
        open_breakers = registry.get_open_breakers()
        half_open_breakers = registry.get_half_open_breakers()

        # Count by state
        state_counts = {"closed": 0, "open": 0, "half_open": 0}
        for state_info in all_states.values():
            state = state_info["state"]
            state_counts[state] = state_counts.get(state, 0) + 1

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_breakers": len(all_states),
                "closed": state_counts["closed"],
                "open": state_counts["open"],
                "half_open": state_counts["half_open"],
                "open_user_ids": open_breakers,
                "half_open_user_ids": half_open_breakers,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Circuit breakers summary fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch circuit breakers summary")


@router.get("/circuit-breakers/{user_id}")
async def get_circuit_breaker_state(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🔌 Get Circuit Breaker State (Admin)

    Get detailed circuit breaker state for a specific user.

    **Admin Only**: Requires admin role

    **Returns:**
    - Current state (closed/open/half_open)
    - Failure/success counts
    - Timeout information
    - Thresholds

    **Use Case:**
    Investigate why a specific bot is being blocked.
    """
    try:
        await require_admin_user(current_user["id"])

        from apps.bot.multi_tenant.circuit_breaker import get_circuit_breaker_registry

        registry = get_circuit_breaker_registry()
        breaker = registry.get_breaker(user_id)
        state = breaker.get_state()

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "circuit_breaker": state,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Circuit breaker state fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch circuit breaker state")


@router.post("/circuit-breakers/{user_id}/reset")
async def reset_circuit_breaker(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🔄 Reset Circuit Breaker (Admin)

    Manually reset circuit breaker for a user (close it).

    **Admin Only**: Requires admin role

    **Use Case:**
    Override circuit breaker protection to allow requests again.
    Use when bot issue has been manually resolved.

    **Returns:**
    - Success status
    - New circuit breaker state
    """
    try:
        await require_admin_user(current_user["id"])

        from apps.bot.multi_tenant.circuit_breaker import get_circuit_breaker_registry

        registry = get_circuit_breaker_registry()
        registry.reset_breaker(user_id)

        # Get new state
        breaker = registry.get_breaker(user_id)
        state = breaker.get_state()

        logger.info(f"Admin {current_user['id']} reset circuit breaker for user {user_id}")

        return {
            "status": "ok",
            "message": f"Circuit breaker reset for user {user_id}",
            "timestamp": datetime.now().isoformat(),
            "circuit_breaker": state,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Circuit breaker reset failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset circuit breaker")


@router.get("/retry-statistics")
async def get_retry_statistics(
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🔄 Get Retry Statistics (Admin)

    Get statistics about retry attempts and failures.

    **Admin Only**: Requires admin role

    **Returns:**
    - Total retry attempts
    - Successful vs failed retries
    - Success rate
    - Errors by category

    **Use Case:**
    Monitor retry behavior and identify problematic error patterns.
    """
    try:
        await require_admin_user(current_user["id"])

        from apps.bot.multi_tenant.retry_logic import get_retry_statistics

        stats = get_retry_statistics()
        statistics = stats.get_statistics()

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "retry_statistics": statistics,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Retry statistics fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch retry statistics")


@router.post("/retry-statistics/reset")
async def reset_retry_statistics(
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🔄 Reset Retry Statistics (Admin)

    Reset retry statistics counters.

    **Admin Only**: Requires admin role

    **Use Case:**
    Reset statistics after deploying fixes or for clean monitoring periods.

    **Returns:**
    - Success status
    """
    try:
        await require_admin_user(current_user["id"])

        from apps.bot.multi_tenant.retry_logic import get_retry_statistics

        stats = get_retry_statistics()
        stats.reset()

        logger.info(f"Admin {current_user['id']} reset retry statistics")

        return {
            "status": "ok",
            "message": "Retry statistics reset successfully",
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Retry statistics reset failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset retry statistics")


@router.get("/bot-health/history/{user_id}")
async def get_bot_health_history(
    user_id: int,
    hours: int = Query(24, ge=1, le=168, description="Hours of history to retrieve (max 7 days)"),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📊 Get Bot Health History (Admin)

    Get historical health metrics for a specific user bot.

    **Admin Only**: Requires admin role

    **Parameters:**
    - user_id: User ID to get history for
    - hours: Hours of history to retrieve (1-168, default 24)

    **Returns:**
    - Time series of health metrics
    - Error rate trends
    - Response time trends
    - Circuit breaker state changes

    **Use Case:**
    Analyze bot health trends, identify patterns, diagnose recurring issues.
    """
    try:
        await require_admin_user(current_user["id"])

        from apps.bot.multi_tenant.bot_health_persistence import get_persistence_service

        persistence_service = get_persistence_service()
        history = await persistence_service.get_user_history(user_id, hours)

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "hours": hours,
            "data_points": len(history),
            "history": history,
        }

    except RuntimeError as e:
        # Persistence service not initialized
        logger.warning(f"Persistence service not available: {e}")
        raise HTTPException(
            status_code=503,
            detail="Health metrics persistence not enabled",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bot health history fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch bot health history")


@router.get("/bot-health/unhealthy-history")
async def get_unhealthy_bot_history(
    hours: int = Query(24, ge=1, le=168, description="Hours of history to retrieve (max 7 days)"),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🚨 Get Unhealthy Bot History (Admin)

    Get historical data for all unhealthy bots.

    **Admin Only**: Requires admin role

    **Parameters:**
    - hours: Hours of history to retrieve (1-168, default 24)

    **Returns:**
    - List of unhealthy bot incidents
    - Frequency of issues per user
    - Common error patterns

    **Use Case:**
    Identify users with chronic bot health issues, detect system-wide problems.
    """
    try:
        await require_admin_user(current_user["id"])

        from apps.bot.multi_tenant.bot_health_persistence import get_persistence_service

        persistence_service = get_persistence_service()
        history = await persistence_service.get_unhealthy_history(hours)

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "hours": hours,
            "incident_count": len(history),
            "history": history,
        }

    except RuntimeError as e:
        # Persistence service not initialized
        logger.warning(f"Persistence service not available: {e}")
        raise HTTPException(
            status_code=503,
            detail="Health metrics persistence not enabled",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhealthy bot history fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch unhealthy bot history")


@router.post("/bot-health/persist-now")
async def persist_health_metrics_now(
    current_user: dict = Depends(get_current_user),
):
    """
    ## 💾 Persist Health Metrics Now (Admin)

    Manually trigger immediate persistence of current health metrics.

    **Admin Only**: Requires admin role

    **Use Case:**
    Force immediate snapshot before maintenance, testing, or system changes.

    **Returns:**
    - Success status
    - Number of metrics persisted
    """
    try:
        await require_admin_user(current_user["id"])

        from apps.bot.multi_tenant.bot_health_persistence import get_persistence_service

        persistence_service = get_persistence_service()
        await persistence_service.persist_all_metrics()

        logger.info(f"Admin {current_user['id']} triggered manual health metrics persistence")

        return {
            "status": "ok",
            "message": "Health metrics persisted successfully",
            "timestamp": datetime.now().isoformat(),
        }

    except RuntimeError as e:
        # Persistence service not initialized
        logger.warning(f"Persistence service not available: {e}")
        raise HTTPException(
            status_code=503,
            detail="Health metrics persistence not enabled",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual persistence failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to persist health metrics")


# === TOKEN VALIDATION ADMIN ENDPOINTS ===


class TokenValidationRequest(BaseModel):
    """Request to validate a bot token"""
    token: str = Field(..., description="Bot token to validate")
    live_check: bool = Field(
        default=True,
        description="Perform live validation (test connection to Telegram)"
    )


class TokenValidationResponse(BaseModel):
    """Token validation result"""
    is_valid: bool
    status: str
    message: str
    bot_username: str | None = None
    bot_id: int | None = None
    validated_at: str


@router.post("/token/validate")
async def validate_token(
    request: TokenValidationRequest,
    _current_user: dict = Depends(require_admin_user),
):
    """
    ## 🔐 Validate Bot Token (Admin)

    Validates a bot token without creating a bot.
    Useful for testing tokens before deployment.

    **Validation Types:**
    - **Format validation:** Checks token format (fast)
    - **Live validation:** Tests connection to Telegram (slower but thorough)

    **Returns:**
    - Validation status
    - Bot username and ID (if valid)
    - Detailed error message (if invalid)
    """
    try:
        validator = get_token_validator()

        result = await validator.validate(
            token=request.token,
            live_check=request.live_check,
            timeout_seconds=10
        )

        return TokenValidationResponse(
            is_valid=result.is_valid,
            status=result.status.value,
            message=result.message,
            bot_username=result.bot_username,
            bot_id=result.bot_id,
            validated_at=result.validated_at.isoformat()
        )

    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Token validation failed: {str(e)}"
        )


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
