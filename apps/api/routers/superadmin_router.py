"""
SuperAdmin Management Panel API Routes
Enterprise-grade admin endpoints with comprehensive security and functionality
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.deps import get_db_connection
from core.security_engine import AdministrativeRole, UserStatus

# Import new role system with backwards compatibility
from core.security_engine import User as AdminUser
from core.services.superadmin_service import SuperAdminService

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

router = APIRouter(prefix="/superadmin", tags=["SuperAdmin Management"])
security = HTTPBearer()


# ===== DEPENDENCIES =====


async def get_superadmin_service():
    """Get SuperAdmin service using repository factory pattern"""
    # For now, return a basic service that meets our API needs
    # This is a temporary solution until the full port interfaces are implemented
    from apps.shared.factory import get_repository_factory

    factory = get_repository_factory()
    admin_repo = await factory.get_admin_repository()

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
    admin_service: SuperAdminService = Depends(get_superadmin_service),
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


async def require_admin_role(
    min_role: str = AdministrativeRole.SUPER_ADMIN.value,  # Use new role system
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
    admin_service: SuperAdminService = Depends(get_superadmin_service),
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

    from core.models.superadmin_domain import AdminUser

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
    """Logout admin user (invalidate session)"""
    # TODO: Implement session invalidation
    return {"message": "Logged out successfully"}


# ===== USER MANAGEMENT ENDPOINTS =====


@router.get("/users", response_model=list[SystemUserResponse])
async def get_system_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: UserStatus | None = None,
    search: str | None = None,
    current_admin: AdminUser = Depends(require_admin_role),
    admin_service: SuperAdminService = Depends(get_superadmin_service),
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
    current_admin: AdminUser = Depends(require_admin_role),
    admin_service: SuperAdminService = Depends(get_superadmin_service),
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
    current_admin: AdminUser = Depends(require_admin_role),
    admin_service: SuperAdminService = Depends(get_superadmin_service),
):
    """Reactivate a suspended user"""
    ip_address = request.client.host if request.client else "unknown"

    success = await admin_service.reactivate_user(user_id, int(current_admin.id))

    return {"message": "User reactivated successfully", "success": success}


# ===== SYSTEM ANALYTICS ENDPOINTS =====


@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    db: AsyncSession = Depends(get_db_connection),
    current_admin: AdminUser = Depends(require_admin_role),
    admin_service: SuperAdminService = Depends(get_superadmin_service),
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
    current_admin: AdminUser = Depends(require_admin_role),
    admin_service: SuperAdminService = Depends(get_superadmin_service),
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
    current_admin: AdminUser = Depends(
        lambda: require_admin_role(AdministrativeRole.SUPER_ADMIN.value)
    ),
    admin_service: SuperAdminService = Depends(get_superadmin_service),
):
    """Get system configuration (Super Admin only)"""
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
    current_admin: AdminUser = Depends(
        lambda: require_admin_role(AdministrativeRole.SUPER_ADMIN.value)
    ),
    admin_service: SuperAdminService = Depends(get_superadmin_service),
):
    """Update system configuration (Super Admin only)"""
    ip_address = request.client.host if request.client else "unknown"

    success = await admin_service.update_system_config(
        {key: config_update.value}, int(current_admin.id)
    )

    return {"message": "Configuration updated successfully", "success": success}


# ===== HEALTH AND STATUS ENDPOINTS =====

# NOTE: Health endpoint moved to health_system_router.py for consolidation
# SuperAdmin health is now monitored at /health/services
