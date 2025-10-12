"""
🔒 Authentication Router - User Login/Register Endpoints

Provides JWT-based authentication endpoints using the existing SecurityManager.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from apps.api.auth_utils import auth_utils
from apps.api.middleware.auth import (
    get_current_user,
    get_security_manager,
    get_user_repository,
)

# ✅ CLEAN ARCHITECTURE: Use repository factory instead of direct infra import
# ✅ CLEAN ARCHITECTURE: Use core interface instead of infra implementation
from core.repositories.interfaces import UserRepository

# Import new role system with backwards compatibility
# Import permission decorators
from core.security_engine import (
    ApplicationRole,
    AuthProvider,
    Permission,
    SecurityManager,
    User,
    UserStatus,
    require_analytics_access,
    require_permission,
)
from core.security_engine.mfa import MFAManager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)


class LoginRequest(BaseModel):
    """Login request model"""

    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """User registration request model"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str | None = None


class AuthResponse(BaseModel):
    """Authentication response model"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict[str, Any]


class UserResponse(BaseModel):
    """User response model"""

    id: str
    email: str
    username: str
    full_name: str | None
    role: str
    status: str
    created_at: datetime
    last_login: datetime | None


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    user_repo: UserRepository = Depends(get_user_repository),
    security_manager: SecurityManager = Depends(get_security_manager),
):
    """
    Authenticate user with email and password

    Returns JWT access token and refresh token for successful authentication.
    """
    try:
        # Find user by email
        user_data = await user_repo.get_user_by_email(login_data.email)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Create User object for SecurityManager - Updated for new role system
        user_role = user_data.get("role", "user")

        user = User(
            id=str(user_data["id"]),
            email=user_data["email"],
            username=user_data["username"],
            full_name=user_data.get("full_name"),
            hashed_password=user_data.get("hashed_password"),
            role=user_role,  # Use string directly for new role system
            status=UserStatus(user_data.get("status", "active")),
            auth_provider=AuthProvider.LOCAL,
            created_at=user_data.get("created_at", datetime.utcnow()),
            last_login=user_data.get("last_login"),
            additional_permissions=user_data.get("additional_permissions", []),
            migration_profile=user_data.get("migration_profile"),
        )

        # Verify password
        if not user.verify_password(login_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Check if user account is active
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Account is {user.status.value}. Please contact support.",
            )

        # Create session
        session = get_security_manager().create_user_session(user, request)

        # Generate tokens using centralized auth utilities
        access_token = auth_utils.create_access_token(user)
        refresh_token = auth_utils.create_refresh_token(user.id, session.token)  # Update last login
        await user_repo.update_user(int(user.id), last_login=datetime.utcnow())

        logger.info(f"Successful login for user: {user.username}")

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
            user={
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,  # role is now a string, no .value needed
                "status": user.status.value,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Register new user account

    Creates a new user with email verification required.
    """
    print(f"🎯 Registration endpoint received: {register_data}")
    print(f"🎯 Email: {register_data.email}")
    print(f"🎯 Username: {register_data.username}")
    print(f"🎯 Full name: {register_data.full_name}")
    try:
        # Check if email already exists
        existing_user = await user_repo.get_user_by_email(register_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Check if username already exists
        existing_username = await user_repo.get_user_by_username(register_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

        # Create User object
        print("🏗️ Creating User object with:")
        print(f"   email: {register_data.email}")
        print(f"   username: {register_data.username}")
        print(f"   full_name: {register_data.full_name}")

        user = User(
            email=register_data.email,
            username=register_data.username,
            full_name=register_data.full_name,
            role=ApplicationRole.USER.value,  # Use new role system
            status=UserStatus.PENDING_VERIFICATION,
            auth_provider=AuthProvider.LOCAL,
        )

        # Set password
        user.set_password(register_data.password)

        # Save to database
        user_data = {
            "id": int(user.id) if user.id.isdigit() else hash(user.id) % (10**9),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "hashed_password": user.hashed_password,
            "role": user.role,  # role is now a string, no .value needed
            "status": user.status.value,
            "plan_id": 1,  # Default plan
        }

        created_user = await user_repo.create_user(user_data)

        logger.info(f"New user registered: {user.username}")

        return {
            "message": "Registration successful. Please check your email for verification.",
            "user_id": created_user["id"],
            "email": user.email,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    security_manager: SecurityManager = Depends(get_security_manager),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Refresh access token using refresh token
    """
    try:
        # Validate refresh token and get new access token
        new_access_token = auth_utils.refresh_access_token(refresh_token)

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 30 * 60,
        }

    except Exception as e:
        logger.warning(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(
    current_user: dict[str, Any] = Depends(get_current_user),
    security_manager: SecurityManager = Depends(get_security_manager),
):
    """
    Logout user and invalidate tokens
    """
    try:
        user_id = current_user["id"]
        # Revoke all user sessions
        auth_utils.revoke_user_sessions(str(user_id))

        logger.info(f"User logged out: {current_user.get('username', user_id)}")

        return {"message": "Successfully logged out"}

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Get current user's profile information
    """
    return UserResponse(
        id=str(current_user["id"]),
        email=current_user["email"],
        username=current_user["username"],
        full_name=current_user.get("full_name"),
        role=current_user.get("role", "user"),
        status=current_user.get("status", "active"),
        created_at=current_user.get("created_at", datetime.utcnow()),
        last_login=current_user.get("last_login"),
    )


# Helper functions for user operations
async def get_user_by_email(email: str, user_repository: UserRepository) -> dict | None:
    """Get user by email from the repository"""
    # For production users, query the database
    # Demo user logic is handled by middleware, not here
    try:
        # TODO: Implement actual database lookup
        # user = await user_repository.get_by_email(email)
        # return user if user else None
        return None
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None


async def update_user_password(
    user_id: str, hashed_password: str, user_repository: UserRepository
) -> bool:
    """Update user password in the repository"""
    # This is a placeholder - we need to implement password update
    # For now, we'll just log the operation
    logger.info(f"Password updated for user {user_id}")
    return True


# Password Reset Models
class ForgotPasswordRequest(BaseModel):
    """Forgot password request model"""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request model"""

    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


@router.post("/password/forgot")
async def forgot_password(
    request: ForgotPasswordRequest,
    security_manager: SecurityManager = Depends(get_security_manager),
    user_repository: UserRepository = Depends(get_user_repository),
):
    """
    Send password reset email

    This endpoint always returns success to prevent email enumeration attacks,
    but only sends reset emails to valid registered users.
    """
    try:
        # Check if user exists (but don't reveal this information)
        user = await get_user_by_email(request.email, user_repository)

        if user:
            # Generate reset token
            reset_token = get_security_manager().generate_password_reset_token(request.email)

            # In a production system, you would send an email here
            # For now, we'll just log the token (remove this in production!)
            logger.info(f"Password reset token for {request.email}: {reset_token}")

            # TODO: Send email with reset link
            # await send_password_reset_email(user.email, reset_token)

        return {
            "message": "If a user with that email exists, a password reset link has been sent.",
            "success": True,
        }

    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        # Always return success message to prevent information disclosure
        return {
            "message": "If a user with that email exists, a password reset link has been sent.",
            "success": True,
        }


@router.post("/password/reset")
async def reset_password(
    request: ResetPasswordRequest,
    security_manager: SecurityManager = Depends(get_security_manager),
    user_repository: UserRepository = Depends(get_user_repository),
):
    """
    Reset user password using reset token
    """
    try:
        # Verify reset token
        reset_data = get_security_manager().verify_password_reset_token(request.token)
        if not reset_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        user_email = reset_data["email"]

        # Get user by email
        user = await get_user_by_email(user_email, user_repository)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token"
            )

        # Hash new password
        from core.security_engine.models import pwd_context

        hashed_password = pwd_context.hash(request.new_password)

        # Update user password
        await update_user_password(user["id"], hashed_password, user_repository)

        # Consume the reset token (mark as used)
        get_security_manager().consume_password_reset_token(request.token)

        # Terminate all user sessions for security
        get_security_manager().terminate_all_user_sessions(str(user["id"]))
        logger.info(f"Password reset successful for user: {user_email}")

        return {
            "message": "Password reset successful. Please log in with your new password.",
            "success": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed",
        )


# MFA Management Models
class MFASetupRequest(BaseModel):
    """MFA setup initiation request"""


class MFAVerifySetupRequest(BaseModel):
    """MFA setup verification request"""

    token: str = Field(..., min_length=6, max_length=6)


class MFAVerifyRequest(BaseModel):
    """MFA token verification request"""

    token: str = Field(..., min_length=6, max_length=6)


class MFABackupCodeRequest(BaseModel):
    """MFA backup code usage request"""

    backup_code: str = Field(..., min_length=8)


# MFA manager instance
mfa_manager = MFAManager()


def get_mfa_manager() -> MFAManager:
    """Get MFA manager instance"""
    return mfa_manager


@router.get("/mfa/status")
async def get_mfa_status(
    current_user: dict[str, Any] = Depends(get_current_user),
    mfa_manager: MFAManager = Depends(get_mfa_manager),
):
    """
    Get MFA status for current user
    """
    try:
        # Check if MFA is enabled
        import json

        mfa_data_str = mfa_manager.redis_client.get(f"mfa_data:{current_user['id']}")

        if mfa_data_str and isinstance(mfa_data_str, str):
            mfa_data = json.loads(mfa_data_str)
            return {
                "enabled": True,
                "enabled_at": mfa_data.get("enabled_at"),
                "backup_codes_remaining": len(mfa_data.get("backup_codes", [])),
            }
        else:
            return {"enabled": False, "enabled_at": None, "backup_codes_remaining": 0}

    except Exception as e:
        logger.error(f"MFA status check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get MFA status",
        )


@router.get("/profile/permissions", response_model=dict)
@require_permission(Permission.VIEW_CONTENT)
async def get_user_permissions(current_user: dict = Depends(get_current_user)):
    """
    Get current user's permissions - demonstrates new permission system.

    Requires: Permission.VIEW_CONTENT
    """
    try:
        from core.security_engine.role_hierarchy import role_hierarchy_service

        user_info = role_hierarchy_service.get_user_role_info(
            role=current_user.get("role", "user"),
            additional_permissions=current_user.get("additional_permissions", []),
            migration_profile=current_user.get("migration_profile"),
        )

        return {
            "user_id": current_user.get("id"),
            "username": current_user.get("username"),
            "role": user_info.role,
            "role_level": user_info.role_level,
            "is_administrative": user_info.is_administrative,
            "permissions": [perm.value for perm in user_info.permissions],
            "migration_profile": user_info.migration_profile,
            "total_permissions": len(user_info.permissions),
        }

    except Exception as e:
        logger.error(f"Permission check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user permissions",
        )


@router.get("/admin/user-roles", response_model=dict)
@require_analytics_access()
async def get_role_hierarchy(current_user: dict = Depends(get_current_user)):
    """
    Get role hierarchy information - demonstrates analytics permission.

    Requires: Permission.VIEW_ANALYTICS (via @require_analytics_access)
    """
    try:
        from core.security_engine.role_hierarchy import role_hierarchy_service

        hierarchy = role_hierarchy_service.get_role_hierarchy_display()
        available_roles = role_hierarchy_service.get_available_roles(include_deprecated=True)

        return {
            "current_user": current_user.get("username"),
            "role_hierarchy": hierarchy,
            "available_roles": available_roles,
            "new_role_system": True,
            "permission_count": len(Permission),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Role hierarchy error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get role hierarchy",
        )
