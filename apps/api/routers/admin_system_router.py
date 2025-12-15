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
from apps.di.analytics_container import get_analytics_fusion_service, get_database_pool
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
    admin_username: str | None = None
    target_type: str | None = None
    target_id: str | None = None
    timestamp: datetime
    details: dict[str, Any] = Field(default_factory=dict)
    ip_address: str | None = None
    success: bool = True
    error_message: str | None = None


class AuditLogResponse(BaseModel):
    """Response model for paginated audit logs"""

    logs: list[AuditLogEntry]
    total: int
    page: int
    page_size: int
    has_more: bool


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
        await require_admin_user(current_user)

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


@router.get("/audit-logs", response_model=AuditLogResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    action_filter: str | None = Query(None, description="Filter by action type"),
    admin_id_filter: int | None = Query(None, description="Filter by admin user ID"),
    start_date: datetime | None = Query(None, description="Filter from date"),
    end_date: datetime | None = Query(None, description="Filter to date"),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📋 Get Audit Logs (Admin)

    Retrieve admin audit logs with filtering and pagination.

    **Admin Only**: Requires admin role

    **Parameters:**
    - page: Page number (default: 1)
    - page_size: Items per page (1-100, default: 50)
    - action_filter: Filter by action type (optional)
    - admin_id_filter: Filter by admin user ID (optional)
    - start_date: Filter from date (optional)
    - end_date: Filter to date (optional)

    **Returns:**
    - Paginated list of audit log entries
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Build query with filters
            where_clauses = []
            params = []
            param_idx = 1

            if action_filter:
                where_clauses.append(f"a.action ILIKE ${param_idx}")
                params.append(f"%{action_filter}%")
                param_idx += 1

            if admin_id_filter:
                where_clauses.append(f"a.admin_user_id = ${param_idx}")
                params.append(admin_id_filter)
                param_idx += 1

            if start_date:
                where_clauses.append(f"a.timestamp >= ${param_idx}")
                params.append(start_date)
                param_idx += 1

            if end_date:
                where_clauses.append(f"a.timestamp <= ${param_idx}")
                params.append(end_date)
                param_idx += 1

            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            # Get total count
            count_query = f"""
                SELECT COUNT(*) as total
                FROM admin_audit_log a
                WHERE {where_sql}
            """
            total_row = await conn.fetchrow(count_query, *params)
            total = total_row["total"] if total_row else 0

            # Get paginated results
            offset = (page - 1) * page_size
            query = f"""
                SELECT
                    a.id,
                    a.admin_user_id,
                    u.username as admin_username,
                    a.action,
                    a.resource_type as target_type,
                    a.resource_id as target_id,
                    a.details,
                    a.ip_address,
                    a.timestamp,
                    a.success,
                    a.error_message
                FROM admin_audit_log a
                LEFT JOIN users u ON a.admin_user_id = u.id
                WHERE {where_sql}
                ORDER BY a.timestamp DESC
                LIMIT ${param_idx} OFFSET ${param_idx + 1}
            """
            params.extend([page_size, offset])

            rows = await conn.fetch(query, *params)

            logs = [
                AuditLogEntry(
                    id=row["id"],
                    action=row["action"],
                    admin_user_id=row["admin_user_id"],
                    admin_username=row["admin_username"],
                    target_type=row["target_type"],
                    target_id=row["target_id"],
                    timestamp=row["timestamp"],
                    details=row["details"] or {},
                    ip_address=row["ip_address"],
                    success=row["success"],
                    error_message=row["error_message"],
                )
                for row in rows
            ]

            return AuditLogResponse(
                logs=logs,
                total=total,
                page=page,
                page_size=page_size,
                has_more=(page * page_size) < total,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin audit logs fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch admin audit logs")


@router.get("/audit-logs/actions")
async def get_audit_log_actions(
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📋 Get Available Audit Actions

    Get list of unique action types in audit logs for filtering.

    **Admin Only**: Requires admin role
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT DISTINCT action, COUNT(*) as count
                FROM admin_audit_log
                GROUP BY action
                ORDER BY count DESC
            """
            )

            return {"actions": [{"action": row["action"], "count": row["count"]} for row in rows]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audit actions fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch audit actions")


# Keep legacy endpoint for backward compatibility
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
        await require_admin_user(current_user)

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
):
    """
    ## 🏥 Get System Health (Admin)

    Check overall system health and component status.

    **Admin Only**: Requires admin role

    **Returns:**
    - Detailed system health information including database, redis, api, bot, and system metrics
    """
    import platform
    import time as time_module

    import psutil

    try:
        await require_admin_user(current_user)
    except HTTPException:
        raise

    # Initialize all values with defaults
    db_status = "unknown"
    db_latency = 0
    db_connections = 0
    redis_status = "unknown"
    redis_latency = 0
    redis_memory = None
    issues = []

    # Get detailed system resources first (this should always work)
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count() or 1
        cpu_count_logical = psutil.cpu_count(logical=True) or 1
        cpu_freq = psutil.cpu_freq()

        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        disk = psutil.disk_usage("/")

        # Get load average (Unix only)
        try:
            load_avg = psutil.getloadavg()
        except (AttributeError, OSError):
            load_avg = (0, 0, 0)

        # Get boot time for uptime calculation
        boot_time = psutil.boot_time()
        uptime_seconds = datetime.now().timestamp() - boot_time

        system_info = {
            "cpu": {
                "percent": round(cpu_percent, 1),
                "cores_physical": cpu_count,
                "cores_logical": cpu_count_logical,
                "frequency_mhz": round(cpu_freq.current, 0) if cpu_freq else None,
                "load_avg_1m": round(load_avg[0], 2),
                "load_avg_5m": round(load_avg[1], 2),
                "load_avg_15m": round(load_avg[2], 2),
            },
            "memory": {
                "percent": round(memory.percent, 1),
                "total_gb": round(memory.total / 1024 / 1024 / 1024, 1),
                "used_gb": round(memory.used / 1024 / 1024 / 1024, 1),
                "available_gb": round(memory.available / 1024 / 1024 / 1024, 1),
                "swap_percent": round(swap.percent, 1),
                "swap_total_gb": round(swap.total / 1024 / 1024 / 1024, 1),
            },
            "disk": {
                "percent": round(disk.percent, 1),
                "total_gb": round(disk.total / 1024 / 1024 / 1024, 1),
                "used_gb": round(disk.used / 1024 / 1024 / 1024, 1),
                "free_gb": round(disk.free / 1024 / 1024 / 1024, 1),
            },
            "uptime_hours": round(uptime_seconds / 3600, 1),
            "platform": platform.system(),
            "hostname": platform.node(),
        }
    except Exception as e:
        logger.error(f"Failed to get system resources: {e}")
        issues.append(f"System metrics error: {str(e)}")
        system_info = {
            "cpu": {
                "percent": 0,
                "cores_physical": 1,
                "cores_logical": 1,
                "frequency_mhz": None,
                "load_avg_1m": 0,
                "load_avg_5m": 0,
                "load_avg_15m": 0,
            },
            "memory": {
                "percent": 0,
                "total_gb": 0,
                "used_gb": 0,
                "available_gb": 0,
                "swap_percent": 0,
                "swap_total_gb": 0,
            },
            "disk": {"percent": 0, "total_gb": 0, "used_gb": 0, "free_gb": 0},
            "uptime_hours": 0,
            "platform": "Unknown",
            "hostname": "Unknown",
        }

    # Check database health
    try:
        from apps.di import get_db_connection

        pool = await get_db_connection()
        if pool:
            start = time_module.time()
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                # Try to get connection count
                try:
                    result = await conn.fetchval(
                        "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
                    )
                    db_connections = result or 0
                except:
                    pass
            db_latency = int((time_module.time() - start) * 1000)
            db_status = "healthy"
        else:
            db_status = "unavailable"
            issues.append("Database pool not initialized")
    except Exception as e:
        db_status = "error"
        issues.append(f"Database: {str(e)[:100]}")
        logger.warning(f"Database health check failed: {e}")

    # Check Redis health
    try:
        from apps.di.analytics_container import get_redis_client

        redis_client = await get_redis_client()
        if redis_client:
            start = time_module.time()
            await redis_client.ping()
            redis_latency = int((time_module.time() - start) * 1000)
            redis_status = "healthy"
            # Try to get Redis memory info
            try:
                info = await redis_client.info("memory")
                redis_memory = {
                    "used_mb": round(info.get("used_memory", 0) / 1024 / 1024, 1),
                    "peak_mb": round(info.get("used_memory_peak", 0) / 1024 / 1024, 1),
                }
            except:
                pass
        else:
            redis_status = "unavailable"
    except Exception as e:
        redis_status = "error"
        issues.append(f"Redis: {str(e)[:100]}")
        logger.warning(f"Redis health check failed: {e}")

    # Check User Bots - count active user bot credentials
    user_bots_status = "unknown"
    user_bots_count = 0
    user_bots_total = 0
    try:
        if pool:
            async with pool.acquire() as conn:
                # Count total user bots
                user_bots_total = (
                    await conn.fetchval("SELECT COUNT(*) FROM user_bot_credentials") or 0
                )
                # Count verified/active user bots (status = 'active' or 'verified')
                user_bots_count = (
                    await conn.fetchval(
                        "SELECT COUNT(*) FROM user_bot_credentials WHERE status IN ('active', 'verified') OR is_verified = true"
                    )
                    or 0
                )
                user_bots_status = "healthy" if user_bots_total > 0 else "idle"
    except Exception as e:
        user_bots_status = "error"
        logger.warning(f"User bots health check failed: {e}")

    # Check User MTProto Sessions - count users with MTProto enabled
    user_mtproto_status = "unknown"
    user_mtproto_count = 0
    user_mtproto_total = 0
    try:
        if pool:
            async with pool.acquire() as conn:
                # Count users with MTProto enabled on channels
                user_mtproto_count = (
                    await conn.fetchval(
                        "SELECT COUNT(DISTINCT user_id) FROM channel_mtproto_settings WHERE mtproto_enabled = true"
                    )
                    or 0
                )
                # Count total MTProto settings
                user_mtproto_total = (
                    await conn.fetchval("SELECT COUNT(*) FROM channel_mtproto_settings") or 0
                )
                # Also check user_bot_credentials for mtproto_enabled
                mtproto_bots = (
                    await conn.fetchval(
                        "SELECT COUNT(*) FROM user_bot_credentials WHERE mtproto_enabled = true"
                    )
                    or 0
                )
                user_mtproto_count = max(user_mtproto_count, mtproto_bots)
                user_mtproto_status = "healthy" if user_mtproto_count > 0 else "idle"
    except Exception as e:
        user_mtproto_status = "error"
        logger.warning(f"User MTProto health check failed: {e}")

    # Determine overall status
    all_healthy = (
        db_status == "healthy"
        and redis_status in ("healthy", "unavailable")
        and system_info["cpu"]["percent"] < 90
        and system_info["memory"]["percent"] < 90
    )

    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.now().isoformat(),
        "database": {
            "status": db_status,
            "latency_ms": db_latency,
            "connections": db_connections,
        },
        "redis": {
            "status": redis_status,
            "latency_ms": redis_latency,
            "memory": redis_memory,
        },
        "api": {
            "status": "healthy",
            "uptime_hours": round(
                (
                    datetime.now() - datetime.now().replace(hour=0, minute=0, second=0)
                ).total_seconds()
                / 3600,
                1,
            ),
        },
        "user_bots": {
            "status": user_bots_status,
            "active_count": user_bots_count,
            "total_count": user_bots_total,
        },
        "user_mtproto": {
            "status": user_mtproto_status,
            "active_sessions": user_mtproto_count,
            "total_configured": user_mtproto_total,
        },
        "system": system_info,
        "overall_score": 100 if all_healthy else 75,
        "issues": issues,
        "checked_by": current_user["id"],
    }


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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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
                "last_success": (
                    metrics.last_success.isoformat() if metrics.last_success else None
                ),
                "last_failure": (
                    metrics.last_failure.isoformat() if metrics.last_failure else None
                ),
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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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
        description="Perform live validation (test connection to Telegram)",
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
            token=request.token, live_check=request.live_check, timeout_seconds=10
        )

        return TokenValidationResponse(
            is_valid=result.is_valid,
            status=result.status.value,
            message=result.message,
            bot_username=result.bot_username,
            bot_id=result.bot_id,
            validated_at=result.validated_at.isoformat(),
        )

    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Token validation failed: {str(e)}")


# === MTPROTO CONNECTION POOL CONFIGURATION ===


class MTProtoPoolConfig(BaseModel):
    """MTProto Connection Pool Configuration"""

    max_concurrent_users: int = Field(
        ...,
        description="Maximum concurrent user sessions (system-wide limit)",
        ge=1,
        le=200,
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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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


# ==================== Admin MTProto Management Endpoints ====================


class MTProtoSessionInfo(BaseModel):
    """MTProto session information for admin"""

    id: int
    user_id: int
    user_email: str | None = None
    user_name: str | None = None  # full_name or username
    mtproto_id: int | None = None  # Telegram user ID from MTProto
    mtproto_username: str | None = None  # Telegram username from MTProto
    channel_id: int
    channel_name: str | None = None
    channel_username: str | None = None
    mtproto_enabled: bool  # User toggle - wants to use MTProto
    session_active: bool = False  # Actually has working session
    created_at: datetime
    updated_at: datetime


class MTProtoSessionListResponse(BaseModel):
    """Response for MTProto session list"""

    total: int
    page: int
    page_size: int
    sessions: list[MTProtoSessionInfo]


class MTProtoStatsResponse(BaseModel):
    """MTProto statistics response"""

    total_sessions: int
    active_sessions: int  # Actually working (has session + verified)
    not_setup_sessions: int  # Enabled but not completed setup
    disabled_sessions: int  # Turned off
    users_with_mtproto: int


@router.get("/mtproto/sessions", response_model=MTProtoSessionListResponse)
async def list_mtproto_sessions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page"),
    user_id: int | None = Query(None, description="Filter by user ID"),
    status_filter: str | None = Query(
        None, description="Filter by status: active, not_setup, disabled"
    ),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📋 List MTProto Sessions (Admin Only)

    Get paginated list of MTProto sessions across all users.

    **Admin Only**: Requires admin role

    **Parameters:**
    - page: Page number (default: 1)
    - page_size: Items per page (1-100, default: 25)
    - user_id: Filter by user ID (optional)
    - status_filter: Filter by status - active, not_setup, disabled (optional)

    **Returns:**
    - Paginated list of MTProto sessions with user and channel info
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Build query with filters
            where_clauses = []
            params = []
            param_idx = 1

            if user_id is not None:
                where_clauses.append(f"cms.user_id = ${param_idx}")
                params.append(user_id)
                param_idx += 1

            # Status filter logic
            if status_filter == "active":
                # Has session and is verified
                where_clauses.append("(ubc.session_string IS NOT NULL AND ubc.is_verified = true)")
            elif status_filter == "not_setup":
                # Enabled but no session or not verified
                where_clauses.append(
                    "(cms.mtproto_enabled = true AND (ubc.session_string IS NULL OR ubc.is_verified = false))"
                )
            elif status_filter == "disabled":
                where_clauses.append("cms.mtproto_enabled = false")

            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            # Get total count - need to join for status filter
            count_query = f"""
                SELECT COUNT(*) FROM channel_mtproto_settings cms
                LEFT JOIN user_bot_credentials ubc ON cms.user_id = ubc.user_id
                {where_clause}
            """
            total = await conn.fetchval(count_query, *params) or 0

            # Get paginated results
            offset = (page - 1) * page_size

            # Build paginated query with correct parameter indices
            limit_param = f"${param_idx}"
            offset_param = f"${param_idx + 1}"

            query = f"""
                SELECT
                    cms.id,
                    cms.user_id,
                    u.email as user_email,
                    COALESCE(u.full_name, u.username, 'Unknown') as user_name,
                    ubc.mtproto_id,
                    ubc.mtproto_username,
                    cms.channel_id,
                    c.title as channel_name,
                    c.username as channel_username,
                    cms.mtproto_enabled,
                    (ubc.session_string IS NOT NULL AND ubc.is_verified = true) as session_active,
                    cms.created_at,
                    cms.updated_at
                FROM channel_mtproto_settings cms
                LEFT JOIN users u ON cms.user_id = u.id
                LEFT JOIN channels c ON cms.channel_id = c.id
                LEFT JOIN user_bot_credentials ubc ON cms.user_id = ubc.user_id
                {where_clause}
                ORDER BY cms.updated_at DESC
                LIMIT {limit_param} OFFSET {offset_param}
            """

            # Add pagination params
            query_params = params + [page_size, offset]
            rows = await conn.fetch(query, *query_params)

            sessions = [
                MTProtoSessionInfo(
                    id=row["id"],
                    user_id=row["user_id"],
                    user_email=row["user_email"],
                    user_name=row["user_name"],
                    mtproto_id=row["mtproto_id"],
                    mtproto_username=row["mtproto_username"],
                    channel_id=row["channel_id"],
                    channel_name=row["channel_name"],
                    channel_username=row["channel_username"],
                    mtproto_enabled=row["mtproto_enabled"],
                    session_active=row["session_active"] or False,
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in rows
            ]

            return MTProtoSessionListResponse(
                total=total,
                page=page,
                page_size=page_size,
                sessions=sessions,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list MTProto sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list MTProto sessions")


@router.get("/mtproto/stats", response_model=MTProtoStatsResponse)
async def get_mtproto_stats(
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📊 Get MTProto Statistics (Admin Only)

    Get overall MTProto statistics.

    **Admin Only**: Requires admin role

    **Returns:**
    - Total sessions, enabled/disabled counts, user/channel counts
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Get session counts with accurate status
            stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as total_sessions,
                    COUNT(*) FILTER (WHERE cms.mtproto_enabled = true AND ubc.session_string IS NOT NULL AND ubc.is_verified = true) as active_sessions,
                    COUNT(*) FILTER (WHERE cms.mtproto_enabled = true AND (ubc.session_string IS NULL OR ubc.is_verified = false)) as not_setup_sessions,
                    COUNT(*) FILTER (WHERE cms.mtproto_enabled = false) as disabled_sessions,
                    COUNT(DISTINCT cms.user_id) as users_with_mtproto
                FROM channel_mtproto_settings cms
                LEFT JOIN user_bot_credentials ubc ON cms.user_id = ubc.user_id
            """
            )

            return MTProtoStatsResponse(
                total_sessions=stats["total_sessions"] or 0,
                active_sessions=stats["active_sessions"] or 0,
                not_setup_sessions=stats["not_setup_sessions"] or 0,
                disabled_sessions=stats["disabled_sessions"] or 0,
                users_with_mtproto=stats["users_with_mtproto"] or 0,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get MTProto stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get MTProto statistics")


@router.patch("/mtproto/sessions/{session_id}/toggle")
async def toggle_mtproto_session(
    session_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🔄 Toggle MTProto Session (Admin Only)

    Enable or disable an MTProto session.

    **Admin Only**: Requires admin role

    **Returns:**
    - Updated session status
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Get current status
            current = await conn.fetchrow(
                "SELECT mtproto_enabled FROM channel_mtproto_settings WHERE id = $1",
                session_id,
            )

            if not current:
                raise HTTPException(status_code=404, detail="MTProto session not found")

            # Toggle status
            new_status = not current["mtproto_enabled"]
            await conn.execute(
                "UPDATE channel_mtproto_settings SET mtproto_enabled = $1, updated_at = NOW() WHERE id = $2",
                new_status,
                session_id,
            )

            return {"success": True, "mtproto_enabled": new_status}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle MTProto session: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle MTProto session")


@router.delete("/mtproto/sessions/{user_id}")
async def delete_mtproto_session(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🗑️ Delete MTProto Session (Admin Only)

    Delete all MTProto configuration for a user including:
    - All channel_mtproto_settings entries
    - Clear MTProto credentials from user_bot_credentials

    **Admin Only**: Requires admin role

    **Returns:**
    - Success status
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Check if user has MTProto settings
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM channel_mtproto_settings WHERE user_id = $1",
                user_id,
            )

            if count == 0:
                raise HTTPException(
                    status_code=404, detail="No MTProto sessions found for this user"
                )

            # Delete all channel_mtproto_settings for this user
            deleted_channels = await conn.execute(
                "DELETE FROM channel_mtproto_settings WHERE user_id = $1", user_id
            )

            # Clear MTProto credentials from user_bot_credentials (but keep bot credentials)
            await conn.execute(
                """
                UPDATE user_bot_credentials
                SET
                    mtproto_id = NULL,
                    mtproto_username = NULL,
                    mtproto_api_id = NULL,
                    telegram_api_hash = NULL,
                    mtproto_phone = NULL,
                    session_string = NULL,
                    mtproto_enabled = false,
                    is_verified = false
                WHERE user_id = $1
            """,
                user_id,
            )

            # Log the deletion in audit log
            await conn.execute(
                """
                INSERT INTO mtproto_audit_log (user_id, channel_id, action, metadata, timestamp)
                VALUES ($1, 0, 'mtproto_deleted', '{"deleted_by": "admin"}'::jsonb, NOW())
            """,
                user_id,
            )

            logger.info(f"Admin deleted MTProto for user {user_id}")

            return {
                "success": True,
                "message": f"MTProto configuration deleted for user {user_id}",
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete MTProto session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete MTProto session")


class MTProtoSessionDetail(BaseModel):
    """Detailed MTProto session information"""

    id: int
    user_id: int
    user_email: str | None = None
    channel_id: int
    channel_name: str | None = None
    mtproto_enabled: bool
    created_at: datetime
    updated_at: datetime
    # Collection stats
    total_collection_runs: int = 0
    last_collection_at: datetime | None = None
    total_messages_collected: int = 0
    avg_messages_per_run: float = 0
    # Recent activity
    recent_actions: list[dict] = []


class MTProtoCollectionRun(BaseModel):
    """Single collection run info"""

    started_at: datetime
    ended_at: datetime | None = None
    messages_collected: int = 0
    duration_seconds: float | None = None
    status: str = "unknown"
    speed_msg_per_sec: float | None = None


@router.get("/mtproto/sessions/{session_id}/details")
async def get_mtproto_session_details(
    session_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📊 Get MTProto Session Details (Admin Only)

    Get detailed information about an MTProto session including collection history.

    **Admin Only**: Requires admin role

    **Returns:**
    - Session details with collection statistics
    - Total runs, messages collected, average performance
    - Recent collection activities
    - All channels connected to this user's MTProto
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Get session info with user and bot details
            session = await conn.fetchrow(
                """
                SELECT
                    cms.id,
                    cms.user_id,
                    u.email as user_email,
                    COALESCE(u.full_name, u.username, 'Unknown') as user_name,
                    u.telegram_id as user_telegram_id,
                    ubc.mtproto_id,
                    ubc.mtproto_username,
                    cms.channel_id,
                    c.title as channel_name,
                    c.username as channel_username,
                    cms.mtproto_enabled,
                    cms.created_at,
                    cms.updated_at
                FROM channel_mtproto_settings cms
                LEFT JOIN users u ON cms.user_id = u.id
                LEFT JOIN channels c ON cms.channel_id = c.id
                LEFT JOIN user_bot_credentials ubc ON cms.user_id = ubc.user_id
                WHERE cms.id = $1
            """,
                session_id,
            )

            if not session:
                raise HTTPException(status_code=404, detail="MTProto session not found")

            session["channel_id"]
            user_id = session["user_id"]

            # Get ALL channels connected to this user's MTProto (up to 5 per user)
            channels = await conn.fetch(
                """
                SELECT
                    cms.id as mtproto_id,
                    cms.channel_id,
                    c.title as channel_name,
                    c.username as channel_username,
                    cms.mtproto_enabled,
                    cms.created_at
                FROM channel_mtproto_settings cms
                LEFT JOIN channels c ON cms.channel_id = c.id
                WHERE cms.user_id = $1
                ORDER BY cms.created_at DESC
            """,
                user_id,
            )

            connected_channels = [
                {
                    "mtproto_id": ch["mtproto_id"],
                    "channel_id": ch["channel_id"],
                    "channel_name": ch["channel_name"] or "Unknown",
                    "channel_username": ch["channel_username"],
                    "mtproto_enabled": ch["mtproto_enabled"],
                    "connected_at": (ch["created_at"].isoformat() if ch["created_at"] else None),
                }
                for ch in channels
            ]

            # Get collection stats from audit log - aggregate for ALL user's channels
            stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) FILTER (WHERE action = 'collection_progress') as total_runs,
                    MIN(timestamp) FILTER (WHERE action = 'collection_progress') as first_run,
                    MAX(timestamp) FILTER (WHERE action = 'collection_progress') as last_run,
                    SUM((metadata::json->>'errors')::int) FILTER (WHERE action = 'collection_progress') as total_errors
                FROM mtproto_audit_log
                WHERE user_id = $1
            """,
                user_id,
            )

            total_runs = stats["total_runs"] or 0
            first_run = stats["first_run"]
            last_run = stats["last_run"]
            total_errors = stats["total_errors"] or 0

            # Calculate average interval between runs
            avg_interval_minutes = None
            if total_runs > 1 and first_run and last_run:
                total_seconds = (last_run - first_run).total_seconds()
                avg_interval_minutes = round(total_seconds / (total_runs - 1) / 60, 1)

            # Get recent activities - only enabled/disabled for status changes
            recent = await conn.fetch(
                """
                SELECT
                    action,
                    timestamp,
                    channel_id
                FROM mtproto_audit_log
                WHERE user_id = $1
                AND action IN ('enabled', 'disabled')
                ORDER BY timestamp DESC
                LIMIT 10
            """,
                user_id,
            )

            recent_actions = []
            for r in recent:
                recent_actions.append(
                    {
                        "action": r["action"],
                        "timestamp": (r["timestamp"].isoformat() if r["timestamp"] else None),
                        "channel_id": r["channel_id"],
                    }
                )

            return {
                "id": session["id"],
                "user_id": session["user_id"],
                "user_email": session["user_email"],
                "user_name": session["user_name"],
                "user_telegram_id": session["user_telegram_id"],
                "mtproto_id": session["mtproto_id"],
                "mtproto_username": session["mtproto_username"],
                "channel_name": session["channel_name"],
                "channel_username": session["channel_username"],
                "mtproto_enabled": session["mtproto_enabled"],
                "created_at": (
                    session["created_at"].isoformat() if session["created_at"] else None
                ),
                "updated_at": (
                    session["updated_at"].isoformat() if session["updated_at"] else None
                ),
                "connected_channels": connected_channels,
                "stats": {
                    "total_runs": total_runs,
                    "first_run_at": first_run.isoformat() if first_run else None,
                    "last_run_at": last_run.isoformat() if last_run else None,
                    "avg_interval_minutes": avg_interval_minutes,
                    "total_errors": total_errors,
                },
                "recent_status_changes": recent_actions,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get MTProto session details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get MTProto session details")


@router.get("/mtproto/sessions/{session_id}/collection-history")
async def get_mtproto_collection_history(
    session_id: int,
    limit: int = Query(50, ge=1, le=500, description="Number of collection runs to return"),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📜 Get MTProto Collection History (Admin Only)

    Get detailed history of all collection runs for a session.

    **Admin Only**: Requires admin role

    **Returns:**
    - List of collection runs with start/end times
    - Messages collected per run
    - Duration and speed statistics
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Get session info for channel_id
            session = await conn.fetchrow(
                """
                SELECT channel_id, user_id FROM channel_mtproto_settings WHERE id = $1
            """,
                session_id,
            )

            if not session:
                raise HTTPException(status_code=404, detail="MTProto session not found")

            channel_id = session["channel_id"]
            user_id = session["user_id"]

            # Get collection runs (start and end pairs)
            runs = await conn.fetch(
                """
                WITH starts AS (
                    SELECT
                        id,
                        timestamp as started_at,
                        metadata,
                        ROW_NUMBER() OVER (ORDER BY timestamp DESC) as rn
                    FROM mtproto_audit_log
                    WHERE channel_id = $1 AND user_id = $2 AND action = 'collection_start'
                    ORDER BY timestamp DESC
                    LIMIT $3
                ),
                ends AS (
                    SELECT
                        id,
                        timestamp as ended_at,
                        metadata,
                        ROW_NUMBER() OVER (ORDER BY timestamp DESC) as rn
                    FROM mtproto_audit_log
                    WHERE channel_id = $1 AND user_id = $2 AND action = 'collection_end'
                    ORDER BY timestamp DESC
                    LIMIT $3
                )
                SELECT
                    s.started_at,
                    e.ended_at,
                    s.metadata as start_meta,
                    e.metadata as end_meta
                FROM starts s
                LEFT JOIN ends e ON s.rn = e.rn
                ORDER BY s.started_at DESC
            """,
                channel_id,
                user_id,
                limit,
            )

            collection_runs = []
            for r in runs:
                end_meta = r["end_meta"]
                if isinstance(end_meta, str):
                    import json

                    try:
                        end_meta = json.loads(end_meta)
                    except:
                        end_meta = {}

                started_at = r["started_at"]
                ended_at = r["ended_at"]
                duration = None
                if started_at and ended_at:
                    duration = (ended_at - started_at).total_seconds()

                collection_runs.append(
                    {
                        "started_at": started_at.isoformat() if started_at else None,
                        "ended_at": ended_at.isoformat() if ended_at else None,
                        "duration_seconds": round(duration, 1) if duration else None,
                        "messages_collected": (
                            end_meta.get("messages_current") if end_meta else None
                        ),
                        "speed_msg_per_sec": (
                            end_meta.get("speed_messages_per_second") if end_meta else None
                        ),
                        "status": "completed" if ended_at else "in_progress",
                    }
                )

            return {
                "session_id": session_id,
                "channel_id": channel_id,
                "total_runs": len(collection_runs),
                "collection_runs": collection_runs,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get MTProto collection history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get MTProto collection history")


# ==================== System Settings Endpoints ====================


class SystemSetting(BaseModel):
    """System setting model"""

    key: str
    value: str | None
    description: str | None
    data_type: str
    is_system: bool
    updated_by: int | None
    updated_at: datetime | None


class SettingUpdate(BaseModel):
    """Request model for updating a setting"""

    value: str


class SettingsResponse(BaseModel):
    """Response model for settings list"""

    settings: list[SystemSetting]
    total: int


@router.get("/settings", response_model=SettingsResponse)
async def get_system_settings(
    current_user: dict = Depends(get_current_user),
    include_system: bool = Query(False, description="Include system-level settings"),
):
    """
    ## ⚙️ Get System Settings (Admin Only)

    Retrieve all configurable system settings.

    **Admin Only**: Requires admin role

    **Parameters:**
    - include_system: Include system-level settings (default: false)

    **Returns:**
    - List of system settings
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            if include_system:
                query = "SELECT * FROM system_settings ORDER BY key"
                rows = await conn.fetch(query)
            else:
                query = "SELECT * FROM system_settings WHERE is_system = FALSE ORDER BY key"
                rows = await conn.fetch(query)

            settings = [
                SystemSetting(
                    key=row["key"],
                    value=row["value"],
                    description=row["description"],
                    data_type=row["data_type"],
                    is_system=row["is_system"],
                    updated_by=row["updated_by"],
                    updated_at=row["updated_at"],
                )
                for row in rows
            ]

            return SettingsResponse(settings=settings, total=len(settings))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Settings fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch settings")


@router.get("/settings/{key}", response_model=SystemSetting)
async def get_setting(
    key: str,
    current_user: dict = Depends(get_current_user),
):
    """
    ## ⚙️ Get Single Setting (Admin Only)

    Retrieve a specific setting by key.

    **Admin Only**: Requires admin role
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM system_settings WHERE key = $1", key)

            if not row:
                raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")

            return SystemSetting(
                key=row["key"],
                value=row["value"],
                description=row["description"],
                data_type=row["data_type"],
                is_system=row["is_system"],
                updated_by=row["updated_by"],
                updated_at=row["updated_at"],
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Setting fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch setting")


@router.put("/settings/{key}")
async def update_setting(
    key: str,
    update: SettingUpdate,
    current_user: dict = Depends(get_current_user),
):
    """
    ## ⚙️ Update Setting (Admin Only)

    Update a system setting value.

    **Admin Only**: Requires admin role

    **Note**: System-level settings cannot be modified through this endpoint.
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Check if setting exists and is not system-level
            existing = await conn.fetchrow("SELECT * FROM system_settings WHERE key = $1", key)

            if not existing:
                raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")

            if existing["is_system"]:
                raise HTTPException(
                    status_code=403,
                    detail="System-level settings cannot be modified through API",
                )

            # Update the setting
            await conn.execute(
                """
                UPDATE system_settings
                SET value = $1, updated_by = $2, updated_at = NOW()
                WHERE key = $3
                """,
                update.value,
                current_user["id"],
                key,
            )

            # Log the action
            from apps.api.utils.audit_logger import (
                AdminActions,
                ResourceTypes,
                log_admin_action,
            )

            await log_admin_action(
                admin_user_id=current_user["id"],
                action=AdminActions.SETTINGS_UPDATE,
                resource_type=ResourceTypes.SETTINGS,
                resource_id=key,
                details={"old_value": existing["value"], "new_value": update.value},
                success=True,
            )

            return {
                "success": True,
                "message": f"Setting '{key}' updated successfully",
                "key": key,
                "value": update.value,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Setting update failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to update setting")


@router.post("/settings")
async def create_setting(
    setting: SystemSetting,
    current_user: dict = Depends(get_current_user),
):
    """
    ## ⚙️ Create Setting (Admin Only)

    Create a new system setting.

    **Admin Only**: Requires admin role
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Check if setting already exists
            existing = await conn.fetchrow(
                "SELECT key FROM system_settings WHERE key = $1", setting.key
            )

            if existing:
                raise HTTPException(
                    status_code=409, detail=f"Setting '{setting.key}' already exists"
                )

            # Create the setting
            await conn.execute(
                """
                INSERT INTO system_settings (key, value, description, data_type, is_system, updated_by, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
                """,
                setting.key,
                setting.value,
                setting.description,
                setting.data_type,
                False,  # User-created settings are not system-level
                current_user["id"],
            )

            # Log the action
            from apps.api.utils.audit_logger import (
                AdminActions,
                ResourceTypes,
                log_admin_action,
            )

            await log_admin_action(
                admin_user_id=current_user["id"],
                action=AdminActions.SETTINGS_UPDATE,
                resource_type=ResourceTypes.SETTINGS,
                resource_id=setting.key,
                details={"action": "created", "value": setting.value},
                success=True,
            )

            return {
                "success": True,
                "message": f"Setting '{setting.key}' created successfully",
                "key": setting.key,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Setting creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create setting")


@router.delete("/settings/{key}")
async def delete_setting(
    key: str,
    current_user: dict = Depends(get_current_user),
):
    """
    ## ⚙️ Delete Setting (Admin Only)

    Delete a system setting.

    **Admin Only**: Requires admin role

    **Note**: System-level settings cannot be deleted.
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Check if setting exists and is not system-level
            existing = await conn.fetchrow("SELECT * FROM system_settings WHERE key = $1", key)

            if not existing:
                raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")

            if existing["is_system"]:
                raise HTTPException(
                    status_code=403, detail="System-level settings cannot be deleted"
                )

            # Delete the setting
            await conn.execute("DELETE FROM system_settings WHERE key = $1", key)

            # Log the action
            from apps.api.utils.audit_logger import (
                AdminActions,
                ResourceTypes,
                log_admin_action,
            )

            await log_admin_action(
                admin_user_id=current_user["id"],
                action=AdminActions.SETTINGS_UPDATE,
                resource_type=ResourceTypes.SETTINGS,
                resource_id=key,
                details={"action": "deleted", "old_value": existing["value"]},
                success=True,
            )

            return {
                "success": True,
                "message": f"Setting '{key}' deleted successfully",
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Setting deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete setting")
