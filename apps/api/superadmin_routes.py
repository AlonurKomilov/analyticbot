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
from core.models.admin import AdminRole, AdminUser, UserStatus
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

router = APIRouter(prefix="/api/v1/superadmin", tags=["SuperAdmin Management"])
security = HTTPBearer()


# ===== DEPENDENCIES =====


async def get_superadmin_service(
    db: AsyncSession = Depends(get_db_connection),
) -> SuperAdminService:
    """Get SuperAdmin service with database dependency"""
    return SuperAdminService(db)


async def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None,
    admin_service: SuperAdminService = Depends(get_superadmin_service),
) -> AdminUser:
    """Validate admin session and return current admin user"""
    try:
        token = credentials.credentials
        ip_address = request.client.host if request else "unknown"

        admin_user = await admin_service.validate_admin_session(token, ip_address)
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return admin_user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin_role(
    min_role: AdminRole = AdminRole.ADMIN,
    current_admin: AdminUser = Depends(get_current_admin_user),
) -> AdminUser:
    """Require minimum admin role"""
    role_hierarchy = {
        AdminRole.SUPPORT: 1,
        AdminRole.MODERATOR: 2,
        AdminRole.ADMIN: 3,
        AdminRole.SUPER_ADMIN: 4,
    }

    user_role_level = role_hierarchy.get(AdminRole(current_admin.role), 0)
    required_role_level = role_hierarchy.get(min_role, 999)

    if user_role_level < required_role_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required: {min_role.value}",
        )

    return current_admin


# ===== AUTHENTICATION ENDPOINTS =====


@router.post("/auth/login", response_model=AdminLoginResponse)
async def admin_login(
    login_request: AdminLoginRequest,
    request: Request,
    admin_service: SuperAdminService = Depends(get_superadmin_service),
):
    """Authenticate admin user and create session"""
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent", "Unknown")

    # Authenticate user
    admin_user = await admin_service.authenticate_admin(
        login_request.username, login_request.password, ip_address
    )

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or account locked",
        )

    # Create session
    access_token = await admin_service.create_admin_session(admin_user, ip_address, user_agent)

    return AdminLoginResponse(
        access_token=access_token,
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
    users = await admin_service.get_system_users(skip, limit, status, search)

    return [
        SystemUserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            status=user.status,
            subscription_tier=user.subscription_tier,
            total_channels=user.total_channels,
            total_posts=user.total_posts,
            last_activity=user.last_activity,
            created_at=user.created_at,
            suspended_at=user.suspended_at,
            suspension_reason=user.suspension_reason,
        )
        for user in users
    ]


@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: UUID,
    suspension_request: UserSuspensionRequest,
    request: Request,
    current_admin: AdminUser = Depends(require_admin_role),
    admin_service: SuperAdminService = Depends(get_superadmin_service),
):
    """Suspend a system user"""
    ip_address = request.client.host

    success = await admin_service.suspend_user(
        user_id, current_admin.id, suspension_request.reason, ip_address
    )

    return {"message": "User suspended successfully", "success": success}


@router.post("/users/{user_id}/reactivate")
async def reactivate_user(
    user_id: UUID,
    request: Request,
    current_admin: AdminUser = Depends(require_admin_role),
    admin_service: SuperAdminService = Depends(get_superadmin_service),
):
    """Reactivate a suspended user"""
    ip_address = request.client.host

    success = await admin_service.reactivate_user(user_id, current_admin.id, ip_address)

    return {"message": "User reactivated successfully", "success": success}


# ===== SYSTEM ANALYTICS ENDPOINTS =====


@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
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
    current_admin: AdminUser = Depends(require_admin_role),
    admin_service: SuperAdminService = Depends(get_superadmin_service),
):
    """Get audit logs with filtering"""
    logs = await admin_service.get_audit_logs(
        skip, limit, admin_user_id, action, start_date, end_date
    )

    return [
        AuditLogResponse(
            id=log.id,
            admin_username=log.admin_user.username,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            success=log.success,
            error_message=log.error_message,
            old_values=log.old_values,
            new_values=log.new_values,
            created_at=log.created_at,
        )
        for log in logs
    ]


# ===== SYSTEM CONFIGURATION ENDPOINTS =====


@router.get("/config", response_model=list[SystemConfigResponse])
async def get_system_config(
    category: str | None = None,
    current_admin: AdminUser = Depends(lambda: require_admin_role(AdminRole.SUPER_ADMIN)),
    admin_service: SuperAdminService = Depends(get_superadmin_service),
):
    """Get system configuration (Super Admin only)"""
    configs = await admin_service.get_system_config(category)

    return [
        SystemConfigResponse(
            id=config.id,
            key=config.key,
            value=config.value if not config.is_sensitive else "***HIDDEN***",
            value_type=config.value_type,
            category=config.category,
            description=config.description,
            is_sensitive=config.is_sensitive,
            requires_restart=config.requires_restart,
        )
        for config in configs
    ]


@router.put("/config/{key}")
async def update_system_config(
    key: str,
    config_update: ConfigUpdateRequest,
    request: Request,
    current_admin: AdminUser = Depends(lambda: require_admin_role(AdminRole.SUPER_ADMIN)),
    admin_service: SuperAdminService = Depends(get_superadmin_service),
):
    """Update system configuration (Super Admin only)"""
    ip_address = request.client.host

    success = await admin_service.update_system_config(
        key, config_update.value, current_admin.id, ip_address
    )

    return {"message": "Configuration updated successfully", "success": success}


# ===== HEALTH AND STATUS ENDPOINTS =====


@router.get("/health")
async def superadmin_health_check():
    """Health check for SuperAdmin system"""
    return {
        "status": "healthy",
        "service": "SuperAdmin Management Panel",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
