"""
Login & Authentication Endpoints

Handles user login, token refresh, logout, and Telegram verification.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status
from pydantic import EmailStr

from apps.api.auth_utils import FastAPIAuthUtils, get_auth_utils
from apps.api.middleware.auth import get_current_user, get_user_repository
from apps.api.middleware.csrf import get_csrf_token_for_response
from apps.api.middleware.rate_limiter import RateLimitConfig, limiter
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
@limiter.limit(RateLimitConfig.AUTH_LOGIN)  # 10 login attempts per minute per IP
async def login(
    login_data: LoginRequest,
    request: Request,
    response: Response,
    user_repo: UserRepository = Depends(get_user_repository),
    security_manager: SecurityManager = Depends(get_security_manager),
    auth_utils: FastAPIAuthUtils = Depends(get_auth_utils),
):
    """
    Authenticate user with email and password

    Returns JWT access token and refresh token for successful authentication.
    For admin panel requests (X-Admin-Request header), tokens are also set as httpOnly cookies.
    """
    try:
        # Check if this is an admin panel request
        is_admin_request = request.headers.get("X-Admin-Request") == "true"
        
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

        # 🆕 Phase 3.2: Create refresh token with remember_me parameter
        refresh_token = auth_utils.create_refresh_token(
            user.id,
            session.token,
            remember_me=login_data.remember_me,  # Pass remember_me from request
        )

        # Update last login
        await user_repo.update_user(int(user.id), last_login=datetime.utcnow())

        logger.info(
            f"Successful login for user: {user.username} " f"(remember_me={login_data.remember_me})"
        )

        # 🔒 SECURITY: Set httpOnly cookies for admin panel requests
        if is_admin_request:
            # Access token cookie - short lived (30 minutes)
            response.set_cookie(
                key="access_token",
                value=access_token,
                max_age=30 * 60,  # 30 minutes
                httponly=True,  # Not accessible via JavaScript
                secure=True,    # Only send over HTTPS
                samesite="strict",  # Strict same-site policy
                path="/",
            )
            
            # Refresh token cookie - longer lived
            refresh_max_age = 30 * 24 * 3600 if login_data.remember_me else 24 * 3600
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                max_age=refresh_max_age,
                httponly=True,
                secure=True,
                samesite="strict",
                path="/auth",  # Only sent to auth endpoints
            )
            
            logger.info(f"Set httpOnly cookies for admin user: {user.username}")

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
                "credit_balance": float(user_data.get("credit_balance", 0)),  # Include credit balance
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
    refresh_token: str = Body(..., embed=True),
    security_manager: SecurityManager = Depends(get_security_manager),
    user_repo: UserRepository = Depends(get_user_repository),
    auth_utils: FastAPIAuthUtils = Depends(get_auth_utils),
):
    """
    Refresh access token using refresh token

    🔄 NEW: Returns rotated refresh token for enhanced security
    """
    try:
        # Validate refresh token and get new tokens (with rotation)
        token_response = auth_utils.refresh_access_token(refresh_token)

        return {
            "access_token": token_response["access_token"],
            "refresh_token": token_response["refresh_token"],  # 🔄 Rotated token
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
    request: Request,
    response: Response,
    current_user: dict[str, Any] = Depends(get_current_user),
    security_manager: SecurityManager = Depends(get_security_manager),
):
    """
    Logout user and invalidate tokens.
    Also clears httpOnly cookies for admin panel.
    """
    try:
        user_id = current_user["id"]
        # Revoke all user sessions
        auth_utils.revoke_user_sessions(str(user_id))

        logger.info(f"User logged out: {current_user.get('username', user_id)}")

        # 🔒 SECURITY: Clear httpOnly cookies
        response.delete_cookie(
            key="access_token",
            path="/",
            secure=True,
            httponly=True,
            samesite="strict",
        )
        response.delete_cookie(
            key="refresh_token",
            path="/auth",
            secure=True,
            httponly=True,
            samesite="strict",
        )
        response.delete_cookie(
            key="csrf_token",
            path="/",
            secure=True,
            samesite="strict",
        )

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


@router.get("/csrf-token")
async def get_csrf_token(request: Request, response: Response):
    """
    Get a CSRF token for the current session.
    
    This endpoint should be called when the admin panel loads to get
    a valid CSRF token for subsequent state-changing requests.
    
    The token is also set as a cookie for the double-submit pattern.
    """
    token = get_csrf_token_for_response()
    
    # Set the token as a cookie
    response.set_cookie(
        key="csrf_token",
        value=token,
        max_age=24 * 3600,  # 24 hours
        httponly=False,  # Must be readable by JavaScript
        secure=True,
        samesite="strict",
        path="/",
    )
    
    return {
        "csrf_token": token,
        "expires_in": 24 * 3600,
        "header_name": "X-CSRF-Token"
    }

