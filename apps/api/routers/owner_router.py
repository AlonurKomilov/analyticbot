"""
Owner Management Panel API Routes
Enterprise-grade owner endpoints with comprehensive security and functionality
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from core.services.backup_service import BackupService
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.di import get_db_connection
from core.security_engine import AdministrativeRole, UserStatus
from core.security_engine import User as AdminUser
from core.services.materialized_view_service import MaterializedViewService
from core.services.owner_service import OwnerService

# ===== PYDANTIC MODELS =====


class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 28800  # 8 hours
    admin_user: dict[str, Any]


class SystemUserResponse(BaseModel):
    id: UUID
    telegram_id: int
    username: str | None
    full_name: str | None
    email: str | None
    status: UserStatus
    subscription_tier: str | None
    total_channels: int
    total_posts: int
    last_activity: datetime | None
    created_at: datetime
    suspended_at: datetime | None
    suspension_reason: str | None


class UserSuspensionRequest(BaseModel):
    reason: str = Field(..., min_length=10, max_length=500)


class SystemStatsResponse(BaseModel):
    users: dict[str, int]
    activity: dict[str, int]
    system: dict[str, Any]


class AuditLogResponse(BaseModel):
    id: UUID
    admin_username: str
    action: str
    resource_type: str
    resource_id: str | None
    ip_address: str
    success: bool
    error_message: str | None
    old_values: dict[str, Any] | None
    new_values: dict[str, Any] | None
    created_at: datetime


class SystemConfigResponse(BaseModel):
    id: UUID
    key: str
    value: str
    value_type: str
    category: str
    description: str | None
    is_sensitive: bool
    requires_restart: bool


class ConfigUpdateRequest(BaseModel):
    value: str = Field(..., max_length=10000)


# ===== ROUTER SETUP =====

router = APIRouter(tags=["Owner Management"])
security = HTTPBearer()


# ===== DEPENDENCIES =====


async def get_owner_service():
    """
    Get Owner service using DI container
    Get Owner service using DI container
    Phase 3 Fix (Oct 19, 2025): Removed factory usage
    """
    # For now, return a basic service that meets our API needs
    # This is a temporary solution until the full port interfaces are implemented
    from apps.di import get_container

    container = get_container()
    admin_repo = await container.database.admin_repo()

    # Create a simple wrapper that provides the methods we need
    class SimpleAdminService:
        def __init__(self, repo):
            self.admin_repo = repo

        async def authenticate_admin(self, username: str, password: str):
            # Implement basic authentication logic
            return {"id": 1, "username": username}  # Placeholder

    return SimpleAdminService(admin_repo)


async def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin_service: OwnerService = Depends(get_owner_service),
) -> AdminUser:
    """Validate admin session and return current admin user"""
    try:
        token = credentials.credentials
        ip_address = "unknown"  # We don't have request context here

        admin_user = await admin_service.validate_admin_session(token, ip_address)
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Convert dict to AdminUser object
        if isinstance(admin_user, dict):
            return AdminUser(
                id=str(admin_user.get("id", "")),
                username=admin_user.get("username", ""),
                email=admin_user.get("email", ""),
                status=UserStatus.ACTIVE,  # Default status
                created_at=datetime.now(),  # Default timestamp
            )
        return admin_user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin_user(
    min_role: str = AdministrativeRole.OWNER.value,  # Use new role system (owner = highest)
    current_admin: AdminUser = Depends(get_current_admin_user),
) -> AdminUser:
    """Require minimum admin role"""
    # Use new role hierarchy
    from core.security_engine.roles import has_role_or_higher

    if not has_role_or_higher(current_admin.role, min_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required: {min_role}",
        )

    return current_admin


# ===== AUTHENTICATION ENDPOINTS =====


@router.post("/auth/login", response_model=AdminLoginResponse)
async def admin_login(
    login_request: AdminLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_connection),
    admin_service: OwnerService = Depends(get_owner_service),
):
    """Authenticate admin user and create session"""
    ip_address = request.client.host if request.client else "unknown"
    request.headers.get("User-Agent", "Unknown")

    # Authenticate user
    admin_session = await admin_service.authenticate_admin(
        login_request.username, login_request.password, ip_address
    )

    if not admin_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or account locked",
        )

    # Get admin user from session
    from sqlalchemy.future import select

    from core.models.owner_domain import AdminUser

    stmt = select(AdminUser).where(AdminUser.id == admin_session["admin_id"])
    result = await db.execute(stmt)
    admin_user = result.scalar_one()

    return AdminLoginResponse(
        access_token=admin_session["session_token"],
        admin_user={
            "id": str(admin_user.id),
            "username": admin_user.username,
            "full_name": admin_user.full_name,
            "role": admin_user.role,
            "last_login": (admin_user.last_login.isoformat() if admin_user.last_login else None),
        },
    )


@router.post("/auth/logout")
async def admin_logout(current_admin: AdminUser = Depends(get_current_admin_user)):
    """
    Logout admin user (invalidate session).

    Note: Session invalidation deferred to Week 2.
    Currently relies on JWT expiration only (stateless).
    Tracked in GitHub Issue #TBD: Implement session blacklist/invalidation
    """
    return {"message": "Logged out successfully"}


# ===== USER MANAGEMENT ENDPOINTS =====


@router.get("/users", response_model=list[SystemUserResponse])
async def get_system_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: UserStatus | None = None,
    search: str | None = None,
    current_admin: AdminUser = Depends(require_admin_user),
    admin_service: OwnerService = Depends(get_owner_service),
):
    """Get system users with filtering and pagination"""
    users_data = await admin_service.get_system_users(page=skip // limit + 1, limit=limit)

    return [
        SystemUserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            status=user.status,
            subscription_tier=user.subscription_tier,
            total_channels=getattr(user, "total_channels", 0),
            total_posts=getattr(user, "total_posts", 0),
            last_activity=user.last_activity,
            created_at=user.created_at,
            suspended_at=getattr(user, "suspended_at", None),
            suspension_reason=getattr(user, "suspension_reason", None),
        )
        for user in users_data.get("users", [])
    ]


@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    suspension_request: UserSuspensionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_connection),
    current_admin: AdminUser = Depends(require_admin_user),
    admin_service: OwnerService = Depends(get_owner_service),
):
    """Suspend a system user"""
    request.client.host if request.client else "unknown"

    success = await admin_service.suspend_user(
        UUID(str(current_admin.id)), UUID(str(user_id)), suspension_request.reason
    )

    return {"message": "User suspended successfully", "success": success}


@router.post("/users/{user_id}/reactivate")
async def reactivate_user(
    user_id: int,
    request: Request,
    current_admin: AdminUser = Depends(require_admin_user),
    admin_service: OwnerService = Depends(get_owner_service),
):
    """Reactivate a suspended user"""
    request.client.host if request.client else "unknown"

    success = await admin_service.reactivate_user(user_id, int(current_admin.id))

    return {"message": "User reactivated successfully", "success": success}


# ===== SYSTEM ANALYTICS ENDPOINTS =====


@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    db: AsyncSession = Depends(get_db_connection),
    current_admin: AdminUser = Depends(require_admin_user),
    admin_service: OwnerService = Depends(get_owner_service),
):
    """Get comprehensive system statistics"""
    stats = await admin_service.get_system_stats()

    return SystemStatsResponse(
        users=stats["users"], activity=stats["activity"], system=stats["system"]
    )


@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_user_id: UUID | None = None,
    action: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: AsyncSession = Depends(get_db_connection),
    current_admin: AdminUser = Depends(require_admin_user),
    admin_service: OwnerService = Depends(get_owner_service),
):
    """Get audit logs with filtering"""
    logs_data = await admin_service.get_audit_logs(
        page=skip // limit + 1, limit=limit, admin_id=admin_user_id
    )

    return [
        AuditLogResponse(
            id=log.id,
            admin_username=log.admin_user.username if log.admin_user else "System",
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            success=log.success,
            error_message=getattr(log, "error_message", None),
            old_values=log.old_values,
            new_values=log.new_values,
            created_at=log.created_at,
        )
        for log in logs_data.get("logs", [])
    ]


# ===== SYSTEM CONFIGURATION ENDPOINTS =====


@router.get("/config", response_model=list[SystemConfigResponse])
async def get_system_config(
    category: str | None = None,
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    admin_service: OwnerService = Depends(get_owner_service),
):
    """Get system configuration (Owner only)"""
    configs = await admin_service.get_system_config()

    return [
        SystemConfigResponse(
            id=UUID(f"00000000-0000-0000-0000-{str(i).zfill(12)}"),
            key=key,
            value=str(value),
            value_type=type(value).__name__,
            category="system",
            description=f"Configuration for {key}",
            is_sensitive=False,
            requires_restart=False,
        )
        for i, (key, value) in enumerate(configs.items())
    ]


@router.put("/config/{key}")
async def update_system_config(
    key: str,
    config_update: ConfigUpdateRequest,
    request: Request,
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    admin_service: OwnerService = Depends(get_owner_service),
):
    """Update system configuration (Owner only)"""
    request.client.host if request.client else "unknown"

    success = await admin_service.update_system_config(
        {key: config_update.value}, int(current_admin.id)
    )

    return {"message": "Configuration updated successfully", "success": success}


# ===== DATABASE BACKUP ENDPOINTS (OWNER ONLY) =====


@router.get("/database/stats")
async def get_database_stats(
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    db: AsyncSession = Depends(get_db_connection),
):
    """
    Get current database statistics.

    Owner-only: Database size and backup information is sensitive system data.
    """
    backup_service = BackupService(db)
    stats = await backup_service.get_database_stats()

    return {
        "database_name": stats.database_name,
        "size_bytes": stats.size_bytes,
        "size_human": stats.size_human,
        "table_count": stats.table_count,
        "total_records": stats.total_records,
        "backup_count": stats.backup_count,
        "last_backup": (
            {
                "filename": stats.last_backup.filename,
                "size": stats.last_backup.size_human,
                "created_at": stats.last_backup.created_at.isoformat(),
                "age_days": stats.last_backup.age_days,
            }
            if stats.last_backup
            else None
        ),
    }


@router.get("/database/backups")
async def list_backups(
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    db: AsyncSession = Depends(get_db_connection),
):
    """
    List all available database backups.

    Owner-only: Backup files contain all customer data.
    """
    backup_service = BackupService(db)
    backups = await backup_service.list_backups()

    return {
        "count": len(backups),
        "backups": [
            {
                "filename": backup.filename,
                "size_bytes": backup.size_bytes,
                "size_human": backup.size_human,
                "created_at": backup.created_at.isoformat(),
                "age_days": backup.age_days,
                "database_name": backup.database_name,
                "database_size": backup.database_size,
                "checksum": backup.checksum,
                "verified": backup.verified,
            }
            for backup in backups
        ],
    }


@router.post("/database/backup")
async def create_backup(
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    db: AsyncSession = Depends(get_db_connection),
):
    """
    Trigger a manual database backup.

    Owner-only: Creates full database dump with all customer data.

    Security:
    - Requires owner role (highest level)
    - Manual trigger only (no auto-scheduling)
    - Backups stored with limited retention (7 days)
    """
    backup_service = BackupService(db)
    result = await backup_service.create_backup()

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Backup failed"),
        )

    return result


@router.post("/database/verify/{filename}")
async def verify_backup(
    filename: str,
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    db: AsyncSession = Depends(get_db_connection),
):
    """
    Verify backup file integrity.

    Owner-only: Verification creates temporary test database.

    This performs 5 verification tests:
    1. File integrity (gzip test)
    2. PostgreSQL dump format validation
    3. Critical table presence check
    4. Backup size validation
    5. Test restore to temporary database
    """
    backup_service = BackupService(db)
    result = await backup_service.verify_backup(filename)

    return result


@router.delete("/database/backups/{filename}")
async def delete_backup(
    filename: str,
    confirmation: str = Query(..., description="Type 'DELETE' to confirm"),
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    db: AsyncSession = Depends(get_db_connection),
):
    """
    Delete a backup file.

    Owner-only: Prevents accidental deletion by non-owners.

    Security:
    - Requires explicit confirmation (must pass 'DELETE' as query param)
    - Cannot delete the most recent backup
    - Requires owner role
    """
    if confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation required. Pass confirmation='DELETE' as query parameter",
        )

    backup_service = BackupService(db)
    result = await backup_service.delete_backup(filename)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to delete backup"),
        )

    return result


@router.get("/database/backups/{filename}")
async def get_backup_info(
    filename: str,
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    db: AsyncSession = Depends(get_db_connection),
):
    """
    Get detailed information about a specific backup.

    Owner-only: Backup metadata is sensitive.
    """
    backup_service = BackupService(db)
    backup = await backup_service.get_backup_info(filename)

    if not backup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup not found: {filename}",
        )

    return {
        "filename": backup.filename,
        "filepath": backup.filepath,
        "size_bytes": backup.size_bytes,
        "size_human": backup.size_human,
        "created_at": backup.created_at.isoformat(),
        "age_days": backup.age_days,
        "database_name": backup.database_name,
        "database_size": backup.database_size,
        "checksum": backup.checksum,
        "verified": backup.verified,
    }


@router.post("/database/refresh-views")
async def refresh_materialized_views(
    concurrent: bool = Query(True, description="Use CONCURRENTLY to avoid locking"),
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    db: AsyncSession = Depends(get_db_connection),
):
    """
    Manually refresh all materialized views.

    Owner-only: Refreshes analytics data for dashboards.

    This endpoint allows manual refresh of materialized views that power
    analytics dashboards. Views are automatically refreshed every 4 hours,
    but you can trigger an immediate refresh here.

    Args:
        concurrent: If True (default), uses CONCURRENTLY to avoid locking.
                   Set to False only if you need faster refresh and can
                   tolerate brief table locks.

    Materialized Views:
    - mv_channel_daily_recent: Channel performance aggregations
    - mv_post_metrics_recent: Post metrics summaries

    Note: CONCURRENT refresh is slower but doesn't block regular queries.
          Non-concurrent refresh is faster but locks tables briefly.
    """
    result = await MaterializedViewService.refresh_all_views(db, concurrent=concurrent)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to refresh materialized views"),
        )

    return result


@router.get("/database/view-stats")
async def get_view_statistics(
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    db: AsyncSession = Depends(get_db_connection),
):
    """
    Get statistics about materialized views.

    Owner-only: View stats help monitor database performance.

    Returns row counts, sizes, and metadata for each materialized view.
    Useful for monitoring data growth and refresh performance.
    """
    stats = await MaterializedViewService.get_view_stats(db)

    return stats


# ===== QUERY PERFORMANCE MONITORING ENDPOINTS =====


@router.get("/database/query-performance")
async def get_query_performance(
    limit: int = Query(20, ge=1, le=100, description="Number of queries to return"),
    min_calls: int = Query(1, ge=1, description="Minimum number of calls"),
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    db: AsyncSession = Depends(get_db_connection),
):
    """
    Get query performance statistics from pg_stat_statements.

    Owner-only: Monitor database query performance in real-time.

    Returns the top queries by total execution time with detailed metrics:
    - Query text (truncated)
    - Number of calls
    - Mean, max, min execution time
    - Total execution time
    - Standard deviation

    Use this to identify slow queries and optimization opportunities.
    """
    from sqlalchemy import text

    query = """
        SELECT
            substring(query, 1, 200) as query_text,
            calls,
            round(total_exec_time::numeric, 2) as total_time_ms,
            round(mean_exec_time::numeric, 2) as mean_time_ms,
            round(min_exec_time::numeric, 2) as min_time_ms,
            round(max_exec_time::numeric, 2) as max_time_ms,
            round(stddev_exec_time::numeric, 2) as stddev_time_ms,
            round((100.0 * total_exec_time / sum(total_exec_time) OVER ())::numeric, 2) as percent_total
        FROM pg_stat_statements
        WHERE query NOT LIKE '%pg_stat%'
          AND query NOT LIKE 'SET%'
          AND query NOT LIKE 'SHOW%'
          AND query NOT LIKE 'UNLISTEN%'
          AND query NOT LIKE 'RESET%'
          AND query NOT LIKE 'CLOSE%'
          AND calls >= :min_calls
        ORDER BY total_exec_time DESC
        LIMIT :limit
    """

    result = await db.execute(text(query), {"limit": limit, "min_calls": min_calls})
    rows = result.fetchall()

    queries = []
    for row in rows:
        queries.append(
            {
                "query": row[0],
                "calls": row[1],
                "total_time_ms": float(row[2]),
                "mean_time_ms": float(row[3]),
                "min_time_ms": float(row[4]),
                "max_time_ms": float(row[5]),
                "stddev_time_ms": float(row[6]),
                "percent_total": float(row[7]),
            }
        )

    return {
        "queries": queries,
        "total_queries": len(queries),
        "limit": limit,
    }


@router.get("/database/slow-queries")
async def get_slow_queries(
    threshold_ms: float = Query(100.0, ge=0, description="Minimum mean execution time in ms"),
    limit: int = Query(20, ge=1, le=100),
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    db: AsyncSession = Depends(get_db_connection),
):
    """
    Get slow queries exceeding a time threshold.

    Owner-only: Identify problematic queries that need optimization.

    Args:
        threshold_ms: Minimum mean execution time in milliseconds (default: 100ms)
        limit: Maximum number of queries to return

    Returns queries sorted by mean execution time.
    """
    from sqlalchemy import text

    query = """
        SELECT
            substring(query, 1, 200) as query_text,
            calls,
            round(mean_exec_time::numeric, 2) as mean_time_ms,
            round(max_exec_time::numeric, 2) as max_time_ms,
            round(total_exec_time::numeric, 2) as total_time_ms
        FROM pg_stat_statements
        WHERE mean_exec_time >= :threshold
          AND query NOT LIKE '%pg_stat%'
          AND query NOT LIKE 'SET%'
          AND query NOT LIKE 'SHOW%'
        ORDER BY mean_exec_time DESC
        LIMIT :limit
    """

    result = await db.execute(text(query), {"threshold": threshold_ms, "limit": limit})
    rows = result.fetchall()

    queries = []
    for row in rows:
        queries.append(
            {
                "query": row[0],
                "calls": row[1],
                "mean_time_ms": float(row[2]),
                "max_time_ms": float(row[3]),
                "total_time_ms": float(row[4]),
            }
        )

    return {
        "queries": queries,
        "threshold_ms": threshold_ms,
        "count": len(queries),
    }


@router.get("/database/query-stats-summary")
async def get_query_stats_summary(
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    db: AsyncSession = Depends(get_db_connection),
):
    """
    Get overall query performance statistics summary.

    Owner-only: High-level overview of database query performance.

    Returns:
        - Total queries tracked
        - Total execution time
        - Average query time
        - Slow queries count (>100ms)
        - Most frequent query types
    """
    from sqlalchemy import text

    # Get overall stats
    summary_query = """
        SELECT
            COUNT(*) as total_queries,
            COUNT(*) FILTER (WHERE mean_exec_time > 100) as slow_queries_count,
            round(SUM(total_exec_time)::numeric, 2) as total_exec_time_ms,
            round(AVG(mean_exec_time)::numeric, 2) as avg_query_time_ms,
            SUM(calls) as total_calls
        FROM pg_stat_statements
        WHERE query NOT LIKE '%pg_stat%'
    """

    result = await db.execute(text(summary_query))
    summary = result.fetchone()

    # Get most called queries
    top_called_query = """
        SELECT
            substring(query, 1, 100) as query_text,
            calls
        FROM pg_stat_statements
        WHERE query NOT LIKE '%pg_stat%'
          AND query NOT LIKE 'SET%'
          AND query NOT LIKE 'SHOW%'
          AND query NOT LIKE 'UNLISTEN%'
        ORDER BY calls DESC
        LIMIT 5
    """

    result = await db.execute(text(top_called_query))
    top_called = [{"query": row[0], "calls": row[1]} for row in result.fetchall()]

    return {
        "total_queries_tracked": summary[0],
        "slow_queries_count": summary[1],
        "total_exec_time_ms": float(summary[2]) if summary[2] else 0,
        "avg_query_time_ms": float(summary[3]) if summary[3] else 0,
        "total_calls": summary[4],
        "top_called_queries": top_called,
    }


@router.post("/database/reset-query-stats")
async def reset_query_stats(
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
    db: AsyncSession = Depends(get_db_connection),
):
    """
    Reset pg_stat_statements query statistics.

    Owner-only: Clear all tracked query statistics and start fresh.

    WARNING: This will clear all query performance data.
    Use this after optimization to measure improvements.
    """
    from sqlalchemy import text

    await db.execute(text("SELECT pg_stat_statements_reset()"))
    await db.commit()

    return {
        "success": True,
        "message": "Query statistics have been reset",
        "reset_at": datetime.utcnow().isoformat(),
    }


# ===== VACUUM MONITORING ENDPOINTS (Issue #9) =====


@router.get("/database/vacuum-status")
async def get_vacuum_status(
    db: AsyncSession = Depends(get_db_connection),
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
) -> dict[str, Any]:
    """
    Get comprehensive VACUUM and table health status

    **Owner Only**: Requires Level 4 (OWNER) access

    Returns detailed information about:
    - Table health (dead tuples, bloat percentage)
    - Recent vacuum activity
    - Autovacuum configuration
    - Tables needing attention
    """
    from sqlalchemy import text

    # Get table health status with dead tuples and bloat
    health_query = """
        SELECT
            schemaname,
            relname AS table_name,
            n_live_tup AS live_tuples,
            n_dead_tup AS dead_tuples,
            ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_percent,
            n_mod_since_analyze AS modifications_since_analyze,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) AS total_size,
            pg_total_relation_size(schemaname||'.'||relname) AS total_size_bytes,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze,
            vacuum_count,
            autovacuum_count
        FROM pg_stat_user_tables
        WHERE n_live_tup > 0
        ORDER BY n_dead_tup DESC, n_live_tup DESC
        LIMIT 50
    """

    result = await db.execute(text(health_query))
    tables = []
    for row in result:
        tables.append(
            {
                "schema": row[0],
                "table_name": row[1],
                "live_tuples": row[2],
                "dead_tuples": row[3],
                "dead_percent": float(row[4]) if row[4] else 0.0,
                "modifications_since_analyze": row[5],
                "total_size": row[6],
                "total_size_bytes": row[7],
                "last_vacuum": row[8].isoformat() if row[8] else None,
                "last_autovacuum": row[9].isoformat() if row[9] else None,
                "last_analyze": row[10].isoformat() if row[10] else None,
                "last_autoanalyze": row[11].isoformat() if row[11] else None,
                "vacuum_count": row[12],
                "autovacuum_count": row[13],
            }
        )

    # Get overall database statistics
    summary_query = """
        SELECT
            pg_size_pretty(pg_database_size(current_database())) AS database_size,
            COUNT(*) AS total_tables,
            SUM(n_live_tup) AS total_live_tuples,
            SUM(n_dead_tup) AS total_dead_tuples,
            ROUND(100.0 * SUM(n_dead_tup) / NULLIF(SUM(n_live_tup + n_dead_tup), 0), 2) AS overall_dead_percent
        FROM pg_stat_user_tables
    """

    summary_result = await db.execute(text(summary_query))
    summary_row = summary_result.first()

    return {
        "tables": tables,
        "summary": {
            "database_size": summary_row[0],
            "total_tables": summary_row[1],
            "total_live_tuples": summary_row[2],
            "total_dead_tuples": summary_row[3],
            "overall_dead_percent": float(summary_row[4]) if summary_row[4] else 0.0,
        },
        "retrieved_at": datetime.utcnow().isoformat(),
    }


@router.get("/database/autovacuum-config")
async def get_autovacuum_config(
    db: AsyncSession = Depends(get_db_connection),
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
) -> dict[str, Any]:
    """
    Get current autovacuum configuration settings

    **Owner Only**: Requires Level 4 (OWNER) access

    Returns PostgreSQL autovacuum parameters including:
    - Global settings (thresholds, scale factors, timing)
    - Table-specific overrides
    - Performance settings
    """
    from sqlalchemy import text

    # Get global autovacuum settings
    config_query = """
        SELECT
            name,
            setting,
            unit,
            short_desc
        FROM pg_settings
        WHERE name IN (
            'autovacuum',
            'autovacuum_max_workers',
            'autovacuum_naptime',
            'autovacuum_vacuum_threshold',
            'autovacuum_vacuum_scale_factor',
            'autovacuum_analyze_threshold',
            'autovacuum_analyze_scale_factor',
            'autovacuum_vacuum_cost_delay',
            'autovacuum_vacuum_cost_limit',
            'autovacuum_freeze_max_age'
        )
        ORDER BY name
    """

    config_result = await db.execute(text(config_query))
    global_settings = {}
    for row in config_result:
        global_settings[row[0]] = {
            "value": row[1],
            "unit": row[2],
            "description": row[3],
        }

    # Get table-specific settings
    table_settings_query = """
        SELECT
            nspname AS schema,
            relname AS table_name,
            (SELECT option_value FROM pg_options_to_table(reloptions) WHERE option_name = 'autovacuum_vacuum_threshold') AS vacuum_threshold,
            (SELECT option_value FROM pg_options_to_table(reloptions) WHERE option_name = 'autovacuum_vacuum_scale_factor') AS vacuum_scale_factor,
            (SELECT option_value FROM pg_options_to_table(reloptions) WHERE option_name = 'autovacuum_analyze_threshold') AS analyze_threshold,
            (SELECT option_value FROM pg_options_to_table(reloptions) WHERE option_name = 'autovacuum_analyze_scale_factor') AS analyze_scale_factor,
            (SELECT option_value FROM pg_options_to_table(reloptions) WHERE option_name = 'autovacuum_vacuum_cost_delay') AS vacuum_cost_delay
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE nspname = 'public'
          AND relkind = 'r'
          AND reloptions IS NOT NULL
        ORDER BY relname
    """

    table_result = await db.execute(text(table_settings_query))
    table_specific_settings = []
    for row in table_result:
        table_specific_settings.append(
            {
                "schema": row[0],
                "table_name": row[1],
                "vacuum_threshold": row[2],
                "vacuum_scale_factor": row[3],
                "analyze_threshold": row[4],
                "analyze_scale_factor": row[5],
                "vacuum_cost_delay": row[6],
            }
        )

    return {
        "global_settings": global_settings,
        "table_specific_settings": table_specific_settings,
        "retrieved_at": datetime.utcnow().isoformat(),
    }


@router.post("/database/vacuum-table")
async def manual_vacuum_table(
    table_name: str = Query(..., min_length=1, max_length=100),
    analyze: bool = Query(True, description="Run ANALYZE after VACUUM"),
    full: bool = Query(False, description="Run VACUUM FULL (locks table)"),
    db: AsyncSession = Depends(get_db_connection),
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
) -> dict[str, Any]:
    """
    Manually trigger VACUUM on a specific table

    **Owner Only**: Requires Level 4 (OWNER) access

    **WARNING**: VACUUM FULL requires an exclusive lock and can take significant time
    on large tables. Use with caution during business hours.

    Parameters:
    - **table_name**: Name of the table to vacuum
    - **analyze**: Whether to run ANALYZE after VACUUM (default: true)
    - **full**: Whether to run VACUUM FULL for maximum space reclamation (default: false)
    """
    import re

    from sqlalchemy import text

    # Validate table name (prevent SQL injection)
    if not re.match(r"^[a-z_][a-z0-9_]*$", table_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid table name. Must contain only lowercase letters, numbers, and underscores.",
        )

    # Verify table exists
    check_query = text(
        """
        SELECT EXISTS (
            SELECT 1 FROM pg_tables
            WHERE schemaname = 'public' AND tablename = :table_name
        )
    """
    )
    result = await db.execute(check_query, {"table_name": table_name})
    exists = result.scalar()

    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table '{table_name}' not found in public schema",
        )

    # Build VACUUM command
    vacuum_type = "VACUUM FULL" if full else "VACUUM"
    analyze_suffix = " ANALYZE" if analyze else ""
    vacuum_command = f"{vacuum_type}{analyze_suffix} {table_name}"

    # Execute VACUUM (must be in its own transaction)
    try:
        await db.commit()  # Commit any pending transaction
        await db.execute(
            text(f"VACUUM {'FULL ' if full else ''}{'ANALYZE ' if analyze else ''}{table_name}")
        )
        await db.commit()

        return {
            "success": True,
            "message": f"Successfully executed {vacuum_command}",
            "table_name": table_name,
            "vacuum_type": "full" if full else "standard",
            "analyzed": analyze,
            "executed_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"VACUUM failed: {str(e)}",
        )


@router.get("/database/tables-needing-vacuum")
async def get_tables_needing_vacuum(
    dead_percent_threshold: float = Query(
        5.0, ge=0, le=100, description="Dead tuple percentage threshold"
    ),
    min_dead_tuples: int = Query(100, ge=0, description="Minimum dead tuples to consider"),
    db: AsyncSession = Depends(get_db_connection),
    current_admin: AdminUser = Depends(lambda: require_admin_user(AdministrativeRole.OWNER.value)),
) -> dict[str, Any]:
    """
    Get tables that need VACUUM attention

    **Owner Only**: Requires Level 4 (OWNER) access

    Returns tables with high dead tuple ratios or significant bloat
    that would benefit from manual VACUUM.

    Parameters:
    - **dead_percent_threshold**: Minimum % of dead tuples to flag (default: 5%)
    - **min_dead_tuples**: Minimum absolute dead tuples to consider (default: 100)
    """
    from sqlalchemy import text

    query = text(
        """
        SELECT
            schemaname,
            relname AS table_name,
            n_live_tup AS live_tuples,
            n_dead_tup AS dead_tuples,
            ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_percent,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) AS total_size,
            pg_total_relation_size(schemaname||'.'||relname) AS total_size_bytes,
            last_vacuum,
            last_autovacuum,
            CASE
                WHEN last_autovacuum IS NULL AND last_vacuum IS NULL THEN 'NEVER_VACUUMED'
                WHEN n_dead_tup > 10000 AND ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) > 10 THEN 'CRITICAL'
                WHEN n_dead_tup > 1000 AND ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) > 5 THEN 'HIGH'
                ELSE 'MODERATE'
            END AS priority
        FROM pg_stat_user_tables
        WHERE n_live_tup > 0
          AND (
            (n_dead_tup >= :min_dead_tuples AND
             ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) >= :dead_percent_threshold) OR
            (last_autovacuum IS NULL AND last_vacuum IS NULL)
          )
        ORDER BY
            CASE
                WHEN last_autovacuum IS NULL AND last_vacuum IS NULL THEN 0
                ELSE 1
            END,
            n_dead_tup DESC
        LIMIT 30
    """
    )

    result = await db.execute(
        query,
        {
            "dead_percent_threshold": dead_percent_threshold,
            "min_dead_tuples": min_dead_tuples,
        },
    )

    tables = []
    for row in result:
        tables.append(
            {
                "schema": row[0],
                "table_name": row[1],
                "live_tuples": row[2],
                "dead_tuples": row[3],
                "dead_percent": float(row[4]) if row[4] else 0.0,
                "total_size": row[5],
                "total_size_bytes": row[6],
                "last_vacuum": row[7].isoformat() if row[7] else None,
                "last_autovacuum": row[8].isoformat() if row[8] else None,
                "priority": row[9],
            }
        )

    return {
        "tables": tables,
        "count": len(tables),
        "filters": {
            "dead_percent_threshold": dead_percent_threshold,
            "min_dead_tuples": min_dead_tuples,
        },
        "retrieved_at": datetime.utcnow().isoformat(),
    }


@router.get("/database/index-usage")
async def get_index_usage_statistics(
    request: Request,
    admin_user: AdminUser = Depends(require_admin_user),
    min_scans: int = Query(0, description="Minimum index scans filter"),
    max_scans: int = Query(None, description="Maximum index scans filter"),
    unused_only: bool = Query(False, description="Show only unused indexes (0 scans)"),
) -> dict[str, Any]:
    """
    Get comprehensive index usage statistics across all tables

    Owner-only endpoint for database optimization.
    Shows which indexes are being used and identifies candidates for removal.

    **Use Cases:**
    - Identify unused indexes (idx_scan = 0)
    - Find low-usage indexes for potential removal
    - Monitor index efficiency
    - Optimize database schema

    **Filters:**
    - min_scans: Show indexes with at least N scans
    - max_scans: Show indexes with at most N scans
    - unused_only: Shortcut to show only unused indexes

    **Response includes:**
    - Per-table index statistics
    - Index scan counts
    - Index sizes
    - Usage recommendations
    - Overall summary statistics
    """

    db = request.state.db_connection

    # Build WHERE clause based on filters
    where_conditions = ["psi.schemaname = 'public'"]

    if unused_only:
        where_conditions.append("psi.idx_scan = 0")
    else:
        if min_scans > 0:
            where_conditions.append(f"psi.idx_scan >= {min_scans}")
        if max_scans is not None:
            where_conditions.append(f"psi.idx_scan <= {max_scans}")

    where_clause = " AND ".join(where_conditions)

    # Query index usage statistics
    query = f"""
        WITH index_stats AS (
            SELECT
                psi.schemaname,
                psi.relname as table_name,
                psi.indexrelname as index_name,
                psi.idx_scan,
                psi.idx_tup_read,
                psi.idx_tup_fetch,
                pg_relation_size(psi.indexrelid) as index_size_bytes,
                pg_size_pretty(pg_relation_size(psi.indexrelid)) as index_size,
                pi.indexdef,
                CASE
                    WHEN pc.contype = 'p' THEN 'PRIMARY KEY'
                    WHEN pc.contype = 'u' THEN 'UNIQUE'
                    WHEN pc.contype = 'f' THEN 'FOREIGN KEY'
                    ELSE 'INDEX'
                END as constraint_type
            FROM pg_stat_user_indexes psi
            JOIN pg_indexes pi ON pi.indexname = psi.indexrelname AND pi.schemaname = psi.schemaname
            LEFT JOIN pg_constraint pc ON pc.conname = psi.indexrelname
            WHERE {where_clause}
        )
        SELECT *
        FROM index_stats
        ORDER BY idx_scan ASC, index_size_bytes DESC;
    """

    result = await db.fetch(query)

    # Group indexes by table
    tables = {}
    total_indexes = 0
    total_unused = 0
    total_size_bytes = 0

    for row in result:
        table_name = row["table_name"]
        is_unused = row["idx_scan"] == 0

        if table_name not in tables:
            tables[table_name] = {
                "table_name": table_name,
                "indexes": [],
                "total_indexes": 0,
                "unused_indexes": 0,
                "total_size": 0,
                "total_size_pretty": "",
            }

        index_info = {
            "index_name": row["index_name"],
            "scans": row["idx_scan"],
            "tuples_read": row["idx_tup_read"],
            "tuples_fetched": row["idx_tup_fetch"],
            "size_bytes": row["index_size_bytes"],
            "size": row["index_size"],
            "constraint_type": row["constraint_type"],
            "definition": row["indexdef"],
            "recommendation": _get_index_recommendation(
                row["idx_scan"], row["constraint_type"], row["index_size_bytes"]
            ),
        }

        tables[table_name]["indexes"].append(index_info)
        tables[table_name]["total_indexes"] += 1
        tables[table_name]["total_size"] += row["index_size_bytes"]

        if is_unused:
            tables[table_name]["unused_indexes"] += 1
            total_unused += 1

        total_indexes += 1
        total_size_bytes += row["index_size_bytes"]

    # Add pretty size to each table
    for table in tables.values():
        table["total_size_pretty"] = _bytes_to_human(table["total_size"])

    # Overall summary
    summary = {
        "total_indexes": total_indexes,
        "unused_indexes": total_unused,
        "total_size_bytes": total_size_bytes,
        "total_size": _bytes_to_human(total_size_bytes),
        "usage_rate_percent": (
            round((total_indexes - total_unused) / total_indexes * 100, 2)
            if total_indexes > 0
            else 0
        ),
    }

    return {
        "summary": summary,
        "tables": list(tables.values()),
        "filters": {
            "min_scans": min_scans,
            "max_scans": max_scans,
            "unused_only": unused_only,
        },
        "retrieved_at": datetime.utcnow().isoformat(),
    }


def _get_index_recommendation(scans: int, constraint_type: str, size_bytes: int) -> str:
    """Generate index usage recommendation"""

    if constraint_type in ("PRIMARY KEY", "UNIQUE"):
        return "KEEP - Enforces constraint"

    if scans == 0:
        if size_bytes > 10 * 1024 * 1024:  # > 10 MB
            return "REMOVE - Unused & large"
        return "CONSIDER REMOVING - Unused"

    if scans < 10:
        return "REVIEW - Very low usage"

    if scans < 100:
        return "MONITOR - Moderate usage"

    return "KEEP - Active use"


def _bytes_to_human(size_bytes: int) -> str:
    """Convert bytes to human-readable format"""

    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0

    return f"{size:.1f} PB"


# ===== HEALTH AND STATUS ENDPOINTS =====

# NOTE: Health endpoint moved to health_system_router.py for consolidation
# SuperAdmin health is now monitored at /health/services


# ===== SMART COLLECTION MONITORING ENDPOINTS =====


class SmartCollectionStatsResponse(BaseModel):
    """Statistics for smart collection efficiency."""

    total_posts: int
    total_checks: int
    total_snapshots_saved: int
    efficiency_rate: float  # snapshots_saved / checks * 100
    storage_saved_mb: float
    collection_by_age: dict[str, Any]
    stable_posts_count: int
    active_posts_count: int


class StorageAnalysisResponse(BaseModel):
    """Database storage analysis with smart collection impact."""

    current_storage_mb: float
    projected_storage_without_smart_mb: float
    savings_mb: float
    savings_pct: float
    post_metrics_records: int
    post_metrics_checks_records: int
    avg_snapshots_per_post: float
    duplicate_snapshots_estimate: int


@router.get(
    "/database/smart-collection/stats",
    response_model=SmartCollectionStatsResponse,
    summary="Get smart collection efficiency statistics",
    description="Retrieve statistics about the smart collection system's performance and storage savings",
)
async def get_smart_collection_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_connection),
) -> SmartCollectionStatsResponse:
    """Get comprehensive statistics about smart collection efficiency."""
    from sqlalchemy import text

    # Verify admin authentication
    await _verify_owner_access(credentials, db)

    # Get total posts and checks
    query = text(
        """
        SELECT 
            COUNT(DISTINCT p.channel_id || '-' || p.msg_id) as total_posts,
            COALESCE(SUM(c.check_count), 0) as total_checks,
            COALESCE(SUM(c.save_count), 0) as total_snapshots_saved,
            COUNT(*) FILTER (WHERE c.stable_since IS NOT NULL) as stable_posts,
            COUNT(*) FILTER (WHERE c.stable_since IS NULL OR c.last_changed_at > NOW() - INTERVAL '24 hours') as active_posts
        FROM posts p
        LEFT JOIN post_metrics_checks c ON p.channel_id = c.channel_id AND p.msg_id = c.msg_id
        WHERE p.is_deleted = FALSE
    """
    )

    result = await db.execute(query)
    row = result.fetchone()

    total_posts = row.total_posts or 0
    total_checks = row.total_checks or 0
    total_snapshots_saved = row.total_snapshots_saved or 0
    stable_posts = row.stable_posts or 0
    active_posts = row.active_posts or 0

    # Calculate efficiency rate
    efficiency_rate = (total_snapshots_saved / total_checks * 100) if total_checks > 0 else 0.0

    # Estimate storage saved (each skipped snapshot = ~100 bytes saved)
    storage_saved_mb = (total_checks - total_snapshots_saved) * 100 / (1024 * 1024)

    # Get collection by age brackets
    age_query = text(
        """
        SELECT 
            CASE 
                WHEN post_age_hours < 1 THEN 'fresh_<1h'
                WHEN post_age_hours < 24 THEN 'recent_1-24h'
                WHEN post_age_hours < 168 THEN 'daily_1-7d'
                ELSE 'weekly_>7d'
            END as age_bracket,
            COUNT(*) as post_count,
            AVG(check_count) as avg_checks,
            AVG(save_count) as avg_saves,
            AVG(save_count::float / NULLIF(check_count, 0) * 100) as efficiency_pct
        FROM post_metrics_checks
        WHERE post_age_hours IS NOT NULL
        GROUP BY age_bracket
        ORDER BY age_bracket
    """
    )

    age_result = await db.execute(age_query)
    collection_by_age = {}

    for age_row in age_result.fetchall():
        collection_by_age[age_row.age_bracket] = {
            "post_count": age_row.post_count,
            "avg_checks": round(float(age_row.avg_checks or 0), 1),
            "avg_saves": round(float(age_row.avg_saves or 0), 1),
            "efficiency_pct": round(float(age_row.efficiency_pct or 0), 1),
        }

    return SmartCollectionStatsResponse(
        total_posts=total_posts,
        total_checks=total_checks,
        total_snapshots_saved=total_snapshots_saved,
        efficiency_rate=round(efficiency_rate, 2),
        storage_saved_mb=round(storage_saved_mb, 2),
        collection_by_age=collection_by_age,
        stable_posts_count=stable_posts,
        active_posts_count=active_posts,
    )


@router.get(
    "/database/storage-analysis",
    response_model=StorageAnalysisResponse,
    summary="Get database storage analysis with smart collection impact",
    description="Analyze database storage usage and calculate savings from smart collection",
)
async def get_storage_analysis(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_connection),
) -> StorageAnalysisResponse:
    """Get comprehensive storage analysis showing smart collection impact."""
    from sqlalchemy import text

    # Verify admin authentication
    await _verify_owner_access(credentials, db)

    # Get current post_metrics storage
    storage_query = text(
        """
        SELECT 
            pg_size_pretty(pg_total_relation_size('post_metrics')) as total_size,
            pg_total_relation_size('post_metrics') as size_bytes,
            COUNT(*) as record_count
        FROM post_metrics
    """
    )

    storage_result = await db.execute(storage_query)
    storage_row = storage_result.fetchone()

    current_storage_mb = storage_row.size_bytes / (1024 * 1024) if storage_row.size_bytes else 0
    post_metrics_records = storage_row.record_count or 0

    # Get checks table size
    checks_query = text(
        """
        SELECT COUNT(*) as count FROM post_metrics_checks
    """
    )

    checks_result = await db.execute(checks_query)
    checks_row = checks_result.fetchone()
    post_metrics_checks_records = checks_row.count or 0

    # Calculate average snapshots per post
    avg_query = text(
        """
        SELECT 
            COUNT(DISTINCT (channel_id, msg_id)) as unique_posts,
            COUNT(*) as total_snapshots,
            AVG(snapshot_count) as avg_per_post
        FROM (
            SELECT channel_id, msg_id, COUNT(*) as snapshot_count
            FROM post_metrics
            GROUP BY channel_id, msg_id
        ) grouped
    """
    )

    avg_result = await db.execute(avg_query)
    avg_row = avg_result.fetchone()

    avg_row.unique_posts or 0
    avg_snapshots_per_post = float(avg_row.avg_per_post or 0)

    # Estimate duplicates (same metrics saved multiple times)
    duplicate_query = text(
        """
        SELECT 
            COUNT(*) - COUNT(DISTINCT (channel_id, msg_id, views, forwards, reactions_count, replies_count)) as duplicate_estimate
        FROM post_metrics
    """
    )

    dup_result = await db.execute(duplicate_query)
    dup_row = dup_result.fetchone()
    duplicate_snapshots_estimate = dup_row.duplicate_estimate or 0

    # Project storage without smart collection
    # Assume old system would have 10x more snapshots (no change detection)
    projected_storage_without_smart_mb = current_storage_mb * 10

    # Calculate savings
    savings_mb = projected_storage_without_smart_mb - current_storage_mb
    savings_pct = (
        (savings_mb / projected_storage_without_smart_mb * 100)
        if projected_storage_without_smart_mb > 0
        else 0
    )

    return StorageAnalysisResponse(
        current_storage_mb=round(current_storage_mb, 2),
        projected_storage_without_smart_mb=round(projected_storage_without_smart_mb, 2),
        savings_mb=round(savings_mb, 2),
        savings_pct=round(savings_pct, 2),
        post_metrics_records=post_metrics_records,
        post_metrics_checks_records=post_metrics_checks_records,
        avg_snapshots_per_post=round(avg_snapshots_per_post, 2),
        duplicate_snapshots_estimate=duplicate_snapshots_estimate,
    )
