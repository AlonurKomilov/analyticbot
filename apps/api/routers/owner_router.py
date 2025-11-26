"""
Owner Management Panel API Routes
Enterprise-grade owner endpoints with comprehensive security and functionality
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.di import get_db_connection
from core.security_engine import AdministrativeRole, UserStatus
from core.security_engine import User as AdminUser
from core.services.backup_service import BackupService
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
    user_agent = request.headers.get("User-Agent", "Unknown")

    # Authenticate user
    admin_session = await admin_service.authenticate_admin(
        login_request.username, login_request.password, ip_address
    )

    if not admin_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials or account locked"
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
            "last_login": admin_user.last_login.isoformat() if admin_user.last_login else None,
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
    ip_address = request.client.host if request.client else "unknown"

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
    ip_address = request.client.host if request.client else "unknown"

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
    ip_address = request.client.host if request.client else "unknown"

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
        "last_backup": {
            "filename": stats.last_backup.filename,
            "size": stats.last_backup.size_human,
            "created_at": stats.last_backup.created_at.isoformat(),
            "age_days": stats.last_backup.age_days,
        }
        if stats.last_backup
        else None,
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
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Backup not found: {filename}"
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


# ===== HEALTH AND STATUS ENDPOINTS =====

# NOTE: Health endpoint moved to health_system_router.py for consolidation
# SuperAdmin health is now monitored at /health/services
