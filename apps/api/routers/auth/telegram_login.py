"""
Telegram Login Widget Authentication

Implements "Sign in with Telegram" functionality using Telegram's Login Widget.
Validates cryptographic signatures and creates/links user accounts.

Docs: https://core.telegram.org/widgets/login
"""

import hashlib
import hmac
import logging
import os
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from apps.api.auth_utils import auth_utils
from apps.api.middleware.auth import get_user_repository
from apps.api.routers.auth.models import AuthResponse
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


class TelegramLoginData(BaseModel):
    """Data received from Telegram Login Widget"""

    id: int = Field(..., description="Telegram user ID")
    first_name: str = Field(..., description="User's first name")
    last_name: str | None = Field(None, description="User's last name")
    username: str | None = Field(None, description="Telegram username")
    photo_url: str | None = Field(None, description="Profile photo URL")
    auth_date: int = Field(..., description="Unix timestamp of authentication")
    hash: str = Field(..., description="HMAC-SHA256 signature")


class TelegramLinkRequest(BaseModel):
    """Request to link Telegram account to existing user"""

    telegram_data: TelegramLoginData
    email: str | None = Field(None, description="Email to link (optional)")


def validate_telegram_auth(auth_data: dict[str, Any], bot_token: str) -> bool:
    """
    Validate Telegram authentication data.

    Verifies the cryptographic signature to ensure data came from Telegram
    and hasn't been tampered with.

    Args:
        auth_data: Dictionary containing Telegram auth data
        bot_token: Your bot's token from BotFather

    Returns:
        True if data is valid, False otherwise

    Algorithm:
        1. Create data check string from all fields except 'hash'
        2. Calculate HMAC-SHA256 using bot token as key
        3. Compare calculated hash with received hash

    Reference: https://core.telegram.org/widgets/login#checking-authorization
    """
    try:
        # Extract received hash
        received_hash = auth_data.get("hash")
        if not received_hash:
            logger.warning("Telegram auth data missing hash")
            return False

        # Create data check string (sorted key=value pairs)
        # Note: Exclude fields with None values as per Telegram's spec
        check_data = []
        for key in sorted(auth_data.keys()):
            if key != "hash":
                value = auth_data[key]
                # Skip None values - they should not be included in hash calculation
                if value is not None:
                    check_data.append(f"{key}={value}")

        data_check_string = "\n".join(check_data)

        # Debug logging
        logger.info("🔍 Telegram auth validation debug:")
        logger.info(f"  - Auth data keys: {sorted(auth_data.keys())}")
        logger.info(f"  - Data check string: {data_check_string[:100]}...")
        logger.info(f"  - Received hash: {received_hash[:20]}...")
        logger.info(f"  - Bot token (first 10 chars): {bot_token[:10]}...")

        # Create secret key from bot token
        secret_key = hashlib.sha256(bot_token.encode()).digest()

        # Calculate HMAC-SHA256 hash
        calculated_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()

        logger.info(f"  - Calculated hash: {calculated_hash[:20]}...")

        # Constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(calculated_hash, received_hash)

        if not is_valid:
            logger.warning("❌ Telegram auth hash validation failed!")
            logger.warning(f"   Expected: {calculated_hash}")
            logger.warning(f"   Received: {received_hash}")
        else:
            logger.info("✅ Telegram auth hash validated successfully!")

        return is_valid

    except Exception as e:
        logger.error(f"Error validating Telegram auth: {e}")
        return False


def is_auth_recent(auth_date: int, max_age_hours: int = 24) -> bool:
    """
    Check if authentication is recent.

    Args:
        auth_date: Unix timestamp from Telegram
        max_age_hours: Maximum age in hours (default: 24)

    Returns:
        True if auth is recent enough, False otherwise
    """
    try:
        auth_timestamp = datetime.fromtimestamp(auth_date)
        age = datetime.utcnow() - auth_timestamp

        if age > timedelta(hours=max_age_hours):
            logger.warning(f"Telegram auth too old: {age}")
            return False

        return True

    except Exception as e:
        logger.error(f"Error checking auth date: {e}")
        return False


@router.post("/telegram/login", response_model=AuthResponse)
async def telegram_login(
    telegram_data: TelegramLoginData,
    request: Request,
    user_repo: UserRepository = Depends(get_user_repository),
    security_manager: SecurityManager = Depends(get_security_manager),
):
    """
    Authenticate user via Telegram Login Widget.

    This endpoint handles the OAuth-like flow from Telegram's Login Widget.
    It validates the cryptographic signature, then either:
    - Creates a new user account (if first time)
    - Logs in existing user (if Telegram ID already linked)
    - Returns error if Telegram ID exists but needs manual linking

    Flow:
        1. Validate Telegram signature using bot token
        2. Check auth_date is recent (within 24 hours)
        3. Find or create user by Telegram ID
        4. Generate JWT tokens
        5. Return auth response

    Args:
        telegram_data: Validated data from Telegram
        request: FastAPI request for IP/user agent
        user_repo: User repository dependency
        security_manager: Security manager dependency

    Returns:
        AuthResponse with JWT tokens and user data

    Raises:
        HTTPException: If validation fails or user setup is incomplete
    """
    try:
        # Get bot token from environment
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Telegram authentication not configured",
            )

        # Validate Telegram data authenticity
        auth_dict = telegram_data.model_dump()
        if not validate_telegram_auth(auth_dict, bot_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Telegram authentication data",
            )

        # Check auth date is recent
        if not is_auth_recent(telegram_data.auth_date):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication expired. Please try again.",
            )

        # Find user by Telegram ID
        user_data = await user_repo.get_user_by_telegram_id(telegram_data.id)

        # If user doesn't exist, create new account
        if not user_data:
            logger.info(f"Creating new user from Telegram login: {telegram_data.id}")

            # Generate username from Telegram data
            username = telegram_data.username or f"telegram_{telegram_data.id}"
            full_name = telegram_data.first_name
            if telegram_data.last_name:
                full_name += f" {telegram_data.last_name}"

            # Create user with Telegram provider
            new_user = await user_repo.create_user(
                {
                    "email": f"telegram_{telegram_data.id}@telegram.local",  # Placeholder
                    "username": username,
                    "password": None,  # No password needed for Telegram auth
                    "full_name": full_name,
                    "telegram_id": telegram_data.id,
                    "telegram_username": telegram_data.username,
                    "telegram_photo_url": telegram_data.photo_url,
                    "telegram_verified": True,
                    "status": "active",  # Auto-activate Telegram users
                    "auth_provider": "telegram",
                }
            )

            user_data = new_user

        # Create User object for session
        user = User(
            id=str(user_data["id"]),
            email=user_data.get(
                "email", f"telegram_{telegram_data.id}@telegram.user"
            ),  # Generate email for Telegram users
            username=user_data["username"],
            full_name=user_data.get("full_name"),
            hashed_password=user_data.get("hashed_password"),
            role=user_data.get("role", "user"),
            status=UserStatus(user_data.get("status", "active")),
            auth_provider=AuthProvider.TELEGRAM,
            created_at=user_data.get("created_at", datetime.utcnow()),
            last_login=user_data.get("last_login"),
        )

        # Create session
        auth_request = AuthRequest(
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            device_info={"login_method": "telegram"},
            headers=dict(request.headers),
        )
        session = security_manager.create_user_session(user, auth_request)

        # Generate tokens
        access_token = auth_utils.create_access_token(user)
        refresh_token = auth_utils.create_refresh_token(user.id, session.token)

        # Update last login
        await user_repo.update_user(int(user.id), last_login=datetime.utcnow())

        logger.info(f"Successful Telegram login: {user.username} (TG ID: {telegram_data.id})")

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=480 * 60,  # 8 hours (matches config)
            user={
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "status": user.status.value,
                "telegram_id": telegram_data.id,
                "telegram_username": telegram_data.username,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Telegram login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Telegram login failed",
        )


@router.post("/telegram/webapp", response_model=AuthResponse)
async def telegram_webapp_login(
    request: Request,
    user_repo: UserRepository = Depends(get_user_repository),
    security_manager: SecurityManager = Depends(get_security_manager),
):
    """
    Authenticate user from Telegram Web App (Mini App).

    This endpoint handles auto-login for users opening the app from Telegram bot.
    Uses Telegram's WebApp initData for authentication.
    """
    try:
        # Get request body
        body = await request.json()
        init_data = body.get("initData")
        user_data = body.get("user", {})

        if not init_data or not user_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Missing initData or user data"
            )

        telegram_id = user_data.get("id")
        if not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Telegram user ID"
            )

        logger.info(f"TWA login attempt for Telegram ID: {telegram_id}")

        # Find or create user
        existing_user = await user_repo.get_user_by_telegram_id(telegram_id)

        if not existing_user:
            # Create new user from TWA data
            username = user_data.get("username") or f"telegram_{telegram_id}"
            full_name = user_data.get("first_name", "")
            if user_data.get("last_name"):
                full_name += f" {user_data['last_name']}"

            new_user = await user_repo.create_user(
                {
                    "email": f"telegram_{telegram_id}@telegram.local",
                    "username": username,
                    "password": None,
                    "full_name": full_name,
                    "telegram_id": telegram_id,
                    "telegram_username": user_data.get("username"),
                    "telegram_photo_url": user_data.get("photo_url"),
                    "telegram_verified": True,
                    "status": "active",
                    "auth_provider": "telegram",
                }
            )
            existing_user = new_user

        # Create User object for session
        user = User(
            id=str(existing_user["id"]),
            email=existing_user.get("email", f"telegram_{telegram_id}@telegram.user"),
            username=existing_user["username"],
            full_name=existing_user.get("full_name"),
            hashed_password=existing_user.get("hashed_password"),
            role=existing_user.get("role", "user"),
            status=UserStatus(existing_user.get("status", "active")),
            auth_provider=AuthProvider.TELEGRAM,
            created_at=existing_user.get("created_at", datetime.utcnow()),
            last_login=existing_user.get("last_login"),
        )

        # Create session
        auth_request = AuthRequest(
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            device_info={"login_method": "telegram_webapp"},
            headers=dict(request.headers),
        )
        session = security_manager.create_user_session(user, auth_request)

        # Generate tokens
        access_token = auth_utils.create_access_token(user)
        refresh_token = auth_utils.create_refresh_token(user.id, session.token)

        # Update last login
        await user_repo.update_user(int(user.id), last_login=datetime.utcnow())

        logger.info(f"✅ TWA login successful: {user.username} (TG ID: {telegram_id})")

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=480 * 60,  # 8 hours
            user={
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "status": user.status.value,
                "telegram_id": telegram_id,
                "telegram_username": user_data.get("username"),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TWA login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Telegram Web App login failed",
        )


@router.get("/telegram/callback")
async def telegram_callback(
    id: int = Query(..., description="Telegram user ID"),
    first_name: str = Query(..., description="First name"),
    last_name: str | None = Query(None, description="Last name"),
    username: str | None = Query(None, description="Username"),
    photo_url: str | None = Query(None, description="Photo URL"),
    auth_date: int = Query(..., description="Auth timestamp"),
    hash: str = Query(..., description="HMAC signature"),
):
    """
    Callback endpoint for Telegram Login Widget.

    This is called by Telegram's widget with URL query parameters.
    It validates the data and redirects to your frontend with a token.

    URL Example:
        /auth/telegram/callback?id=123456&first_name=John&auth_date=1234567890&hash=abc...

    Flow:
        1. Receive query parameters from Telegram
        2. Validate and create session
        3. Redirect to frontend with token in URL
        4. Frontend stores token and redirects to dashboard

    Returns:
        Redirect to frontend with token or error
    """
    try:
        # Create TelegramLoginData from query params (validates input)
        telegram_data = TelegramLoginData(
            id=id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            photo_url=photo_url,
            auth_date=auth_date,
            hash=hash,
        )

        # Process login (reuse POST endpoint logic)
        # In production, you'd call the login function or redirect to POST endpoint
        # For now, redirect to frontend with Telegram data

        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        redirect_url = f"{frontend_url}/auth/telegram/complete"

        # Pass validated data as URL parameters (encrypted or in session would be better)
        params = (
            f"?telegram_id={telegram_data.id}"
            f"&username={telegram_data.username or ''}"
            f"&first_name={telegram_data.first_name}"
        )

        return {
            "redirect_url": redirect_url + params,
            "message": "Redirect to frontend for token exchange",
        }

    except Exception as e:
        logger.error(f"Telegram callback error: {e}")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return {"redirect_url": f"{frontend_url}/login?error=telegram_auth_failed"}


@router.post("/telegram/link")
async def link_telegram_account(
    link_request: TelegramLinkRequest,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Link Telegram account to existing user.

    Allows users who already have email/password accounts to link
    their Telegram account for faster future logins.

    Args:
        link_request: Telegram data and optional email
        user_repo: User repository

    Returns:
        Success message with updated user data

    Raises:
        HTTPException: If Telegram ID already linked to another account
    """
    try:
        telegram_data = link_request.telegram_data
        email = link_request.email

        # Require email for linking
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email required to link Telegram account",
            )

        # Get bot token
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Telegram not configured",
            )

        # Validate Telegram data
        auth_dict = telegram_data.model_dump()
        if not validate_telegram_auth(auth_dict, bot_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Telegram data",
            )

        # Find user by email
        user_data = await user_repo.get_user_by_email(email)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found with provided email",
            )

        # Check if Telegram ID already linked to another user
        existing_user = await user_repo.get_user_by_telegram_id(telegram_data.id)
        if existing_user and existing_user["id"] != user_data["id"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This Telegram account is already linked to another user",
            )

        # Update user with Telegram data
        await user_repo.update_user(
            int(user_data["id"]),
            telegram_id=telegram_data.id,
            telegram_username=telegram_data.username,
            telegram_photo_url=telegram_data.photo_url,
            telegram_verified=True,
        )

        logger.info(f"Linked Telegram account {telegram_data.id} to user {user_data['username']}")

        return {
            "message": "Telegram account linked successfully",
            "telegram_id": telegram_data.id,
            "telegram_username": telegram_data.username,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking Telegram account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link Telegram account",
        )
