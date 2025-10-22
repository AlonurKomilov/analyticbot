"""
Login & Authentication Endpoints

Handles user login, token refresh, logout, and Telegram verification.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import EmailStr

from apps.api.auth_utils import auth_utils
from apps.api.middleware.auth import get_current_user, get_user_repository
from apps.api.routers.auth.models import AuthResponse, LoginRequest
from core.ports.security_ports import AuthRequest
from core.repositories.interfaces import UserRepository
from core.security_engine import (
    AuthProvider,
    SecurityManager,
    User,
    UserStatus,
    get_security_manager,
)

logger = logging.getLogger(__name__)

router = APIRouter()


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
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
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

        # Debug logging
        logger.debug(f"User object created: {user.email}")
        logger.debug(f"Username: {user.username}, Status: {user.status}")

        # Verify password
        password_valid = user.verify_password(login_data.password)
        logger.debug(f"Password verification result: {password_valid}")

        if not password_valid:
            logger.warning(f"Password verification FAILED for {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
            )

        logger.info(f"Password verified successfully for {user.email}")

        # Check if user account is active or pending verification (allow both for now)
        if user.status not in [UserStatus.ACTIVE, UserStatus.PENDING_VERIFICATION]:
            status_str = user.status.value if isinstance(user.status, UserStatus) else user.status
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Account is {status_str}. Please contact support.",
            )

        # Create session - convert FastAPI Request to AuthRequest
        auth_request = AuthRequest(
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            device_info={},
            headers=dict(request.headers),
        )
        session = get_security_manager().create_user_session(user, auth_request)

        # Generate tokens using centralized auth utilities
        access_token = auth_utils.create_access_token(user)
        refresh_token = auth_utils.create_refresh_token(user.id, session.token)

        # Update last login
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
                "status": user.status.value if isinstance(user.status, UserStatus) else user.status,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
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

        return {"access_token": new_access_token, "token_type": "bearer", "expires_in": 30 * 60}

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


@router.post("/verify-telegram")
async def verify_telegram(
    telegram_id: int,
    email: EmailStr,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Verify user account via Telegram.

    When a user connects their Telegram account, this endpoint activates their account.
    Can be called from the Telegram bot after user authentication.
    """
    try:
        # Find user by email
        user_data = await user_repo.get_user_by_email(email)
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Update user status to active and link Telegram ID
        await user_repo.update_user(
            user_id=user_data["id"], status="active", telegram_id=telegram_id
        )

        logger.info(f"✅ User verified via Telegram: {email} (TG ID: {telegram_id})")

        return {
            "message": "Account verified successfully via Telegram",
            "status": "active",
            "telegram_linked": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Telegram verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to verify account"
        )
