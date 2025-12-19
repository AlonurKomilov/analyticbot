"""
Bot-Based Login Authentication

Implements login via Telegram bot deep link for domains where
Telegram Login Widget doesn't work (different domain than bot's web app).

Flow:
1. User clicks "Login via Telegram" on analyticbot.org
2. Frontend calls /auth/telegram/bot-login/init to get unique login code
3. User is redirected to t.me/bot_username?start=login_CODE
4. User starts the bot, bot receives the login code
5. Bot calls /auth/telegram/bot-login/confirm with code + user data
6. Frontend polls /auth/telegram/bot-login/status to check completion
7. Once confirmed, frontend gets tokens and user is logged in
"""

import json
import logging
import os
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
import redis.asyncio as redis

from apps.api.auth_utils import FastAPIAuthUtils, get_auth_utils
from apps.api.middleware.auth import get_user_repository
from core.ports.security_ports import AuthRequest
from core.repositories.interfaces import UserRepository
from core.security_engine import (
    AuthProvider,
    SecurityManager,
    User,
    UserStatus,
    get_security_manager,
)
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Redis connection for storing login codes
_redis_client = None

async def get_redis() -> redis.Redis:
    """Get Redis client for login code storage"""
    global _redis_client
    if _redis_client is None:
        redis_url = getattr(settings, 'REDIS_URL', None) or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        _redis_client = redis.from_url(redis_url, decode_responses=True)
    return _redis_client


# Constants
LOGIN_CODE_PREFIX = "bot_login:"
LOGIN_CODE_TTL = 300  # 5 minutes


class BotLoginInitResponse(BaseModel):
    """Response when initializing bot-based login"""
    login_code: str = Field(..., description="Unique login code")
    bot_username: str = Field(..., description="Bot username for deep link")
    deep_link: str = Field(..., description="Full Telegram deep link URL")
    expires_in: int = Field(..., description="Seconds until code expires")


class BotLoginInitRequest(BaseModel):
    """Request to initialize bot-based login with client info"""
    user_agent: str | None = Field(None, description="Browser user agent")
    client_ip: str | None = Field(None, description="Client IP address")


class BotLoginStatusResponse(BaseModel):
    """Response for login status check"""
    status: str = Field(..., description="pending, completed, expired, or error")
    access_token: str | None = Field(None, description="JWT access token if completed")
    refresh_token: str | None = Field(None, description="JWT refresh token if completed")
    user: dict | None = Field(None, description="User data if completed")


class BotLoginConfirmRequest(BaseModel):
    """Request from bot to confirm login"""
    login_code: str = Field(..., description="Login code from deep link")
    telegram_id: int = Field(..., description="Telegram user ID")
    first_name: str = Field(..., description="User's first name")
    last_name: str | None = Field(None, description="User's last name")
    username: str | None = Field(None, description="Telegram username")
    photo_url: str | None = Field(None, description="Profile photo URL")


@router.post("/telegram/bot-login/init", response_model=BotLoginInitResponse)
async def init_bot_login(
    request: Request,
    data: BotLoginInitRequest | None = None,
):
    """
    Initialize bot-based login flow.
    
    Generates a unique login code and returns deep link to bot.
    User will click this link to open Telegram and start the bot.
    """
    try:
        # Generate unique login code
        login_code = secrets.token_urlsafe(16)
        
        # Get bot username from settings
        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', None) or os.getenv('TELEGRAM_BOT_USERNAME', 'AnasAnalyticBot')
        
        # Get client info for session display
        client_ip = None
        user_agent = None
        
        # Try to get real IP from headers (behind proxy/cloudflare)
        if request:
            client_ip = (
                request.headers.get("cf-connecting-ip") or
                request.headers.get("x-real-ip") or
                request.headers.get("x-forwarded-for", "").split(",")[0].strip() or
                (request.client.host if request.client else None)
            )
            user_agent = request.headers.get("user-agent", "")
        
        # Override with explicitly passed data if available
        if data:
            if data.client_ip:
                client_ip = data.client_ip
            if data.user_agent:
                user_agent = data.user_agent
        
        # Store code in Redis with pending status and client info
        redis_client = await get_redis()
        login_data = {
            "status": "pending",
            "client_ip": client_ip,
            "user_agent": user_agent,
            "created_at": datetime.utcnow().isoformat(),
        }
        await redis_client.setex(
            f"{LOGIN_CODE_PREFIX}{login_code}",
            LOGIN_CODE_TTL,
            json.dumps(login_data)
        )
        
        logger.info(f"🔐 Bot login initiated with code: {login_code[:8]}... from IP: {client_ip}")
        
        return BotLoginInitResponse(
            login_code=login_code,
            bot_username=bot_username,
            deep_link=f"https://t.me/{bot_username}?start=login_{login_code}",
            expires_in=LOGIN_CODE_TTL
        )
        
    except Exception as e:
        logger.error(f"Error initializing bot login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize login"
        )


@router.get("/telegram/bot-login/status/{login_code}", response_model=BotLoginStatusResponse)
async def check_bot_login_status(login_code: str):
    """
    Check the status of a bot-based login attempt.
    
    Frontend polls this endpoint to know when login is complete.
    """
    try:
        redis_client = await get_redis()
        
        # Check if code exists
        status_data = await redis_client.get(f"{LOGIN_CODE_PREFIX}{login_code}")
        
        if not status_data:
            return BotLoginStatusResponse(status="expired")
        
        # Try to parse as JSON
        try:
            data = json.loads(status_data)
            
            # Check if it's still pending (new format)
            if data.get("status") == "pending":
                return BotLoginStatusResponse(status="pending")
            
            # It's completed - has auth data
            if data.get("access_token"):
                # Delete the code after successful retrieval (one-time use)
                await redis_client.delete(f"{LOGIN_CODE_PREFIX}{login_code}")
                
                return BotLoginStatusResponse(
                    status="completed",
                    access_token=data.get("access_token"),
                    refresh_token=data.get("refresh_token"),
                    user=data.get("user")
                )
            
            return BotLoginStatusResponse(status="pending")
            
        except json.JSONDecodeError:
            # Old format - plain "pending" string
            if status_data == "pending":
                return BotLoginStatusResponse(status="pending")
            return BotLoginStatusResponse(status="error")
            
    except Exception as e:
        logger.error(f"Error checking bot login status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check login status"
        )


@router.post("/telegram/bot-login/confirm")
async def confirm_bot_login(
    request: Request,
    data: BotLoginConfirmRequest,
    user_repo: UserRepository = Depends(get_user_repository),
    security_manager: SecurityManager = Depends(get_security_manager),
    auth_utils: FastAPIAuthUtils = Depends(get_auth_utils),
):
    """
    Confirm bot-based login (called by the bot after user starts it).
    
    This endpoint is called by the bot when user clicks the deep link
    and starts the bot with the login code.
    """
    try:
        redis_client = await get_redis()
        
        # Verify code exists and get stored data
        code_data_raw = await redis_client.get(f"{LOGIN_CODE_PREFIX}{data.login_code}")
        
        if not code_data_raw:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Login code not found or expired"
            )
        
        # Parse the stored data to get client info
        client_info = {}
        try:
            code_data = json.loads(code_data_raw)
            if code_data.get("status") != "pending":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Login code already used"
                )
            client_info = {
                "client_ip": code_data.get("client_ip"),
                "user_agent": code_data.get("user_agent"),
            }
        except json.JSONDecodeError:
            # Old format - plain "pending" string
            if code_data_raw != "pending":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Login code already used"
                )
        
        # Find or create user by Telegram ID
        user_data = await user_repo.get_user_by_telegram_id(data.telegram_id)
        
        if not user_data:
            # Create new user
            logger.info(f"Creating new user for bot login: telegram_id={data.telegram_id}")
            
            full_name = data.first_name
            if data.last_name:
                full_name = f"{data.first_name} {data.last_name}"
            
            new_user_data = {
                "email": f"telegram_{data.telegram_id}@telegram.local",
                "username": data.username or f"tg_{data.telegram_id}",
                "full_name": full_name,
                "plan_id": 1,  # Free plan
                "telegram_id": data.telegram_id,
                "telegram_username": data.username,
                "telegram_photo_url": data.photo_url,
                "auth_provider": "telegram",
                "status": "active",
            }
            
            await user_repo.create_user(new_user_data)
            user_data = await user_repo.get_user_by_telegram_id(data.telegram_id)
            logger.info(f"✅ Created new user via bot login: {user_data.get('id')}")
        else:
            # Update existing user's photo and info from Telegram
            full_name = data.first_name
            if data.last_name:
                full_name = f"{data.first_name} {data.last_name}"
            
            update_data = {
                "telegram_photo_url": data.photo_url,
                "full_name": full_name,
            }
            if data.username:
                update_data["telegram_username"] = data.username
            
            await user_repo.update_user(user_data["id"], **update_data)
            # Refresh user data after update
            user_data = await user_repo.get_user_by_telegram_id(data.telegram_id)
            logger.info(f"✅ Updated existing user via bot login: {user_data.get('id')}")
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Create User object for security manager (matching telegram_login.py)
        user = User(
            id=str(user_data["id"]),
            email=user_data.get("email", f"telegram_{data.telegram_id}@telegram.user"),
            username=user_data.get("username"),
            full_name=user_data.get("full_name"),
            hashed_password=user_data.get("hashed_password"),
            role=user_data.get("role", "user"),
            status=UserStatus(user_data.get("status", "active")),
            auth_provider=AuthProvider.TELEGRAM,
            created_at=user_data.get("created_at", datetime.utcnow()),
            last_login=user_data.get("last_login"),
        )
        
        # Create session (matching telegram_login.py)
        auth_request = AuthRequest(
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            device_info={"login_method": "telegram_bot"},
            headers=dict(request.headers),
        )
        session = security_manager.create_user_session(user, auth_request)
        
        # Generate tokens
        access_token = auth_utils.create_access_token(user)
        refresh_token = auth_utils.create_refresh_token(user.id, session.token)
        
        # Prepare user response data
        user_response = {
            "id": int(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "first_name": data.first_name,
            "last_name": data.last_name,
            "telegram_id": data.telegram_id,
            "photo_url": data.photo_url,
            "credit_balance": float(user_data.get("credit_balance", 0) or 0),
            "role": user_data.get("role", "user"),
        }
        
        # Store auth data in Redis for frontend to retrieve
        auth_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_response
        }
        
        await redis_client.setex(
            f"{LOGIN_CODE_PREFIX}{data.login_code}",
            60,  # Keep for 1 minute for frontend to retrieve
            json.dumps(auth_data)
        )
        
        # Store the access token for later revocation (keyed by telegram_id)
        # This allows the "Terminate session" button to revoke the exact token
        await redis_client.setex(
            f"bot_login_token:{data.telegram_id}",
            86400,  # Keep for 24 hours
            access_token
        )
        
        logger.info(f"✅ Bot login confirmed for telegram_id={data.telegram_id}")
        
        # Return client info for the bot to display
        return {
            "status": "success",
            "message": "Login confirmed",
            "client_info": client_info,
            "session_token": session.token,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming bot login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm login"
        )


@router.post("/telegram/bot-login/terminate-session")
async def terminate_bot_login_session(
    telegram_id: int,
    session_token: str,
    security_manager: SecurityManager = Depends(get_security_manager),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Terminate a session created via bot login.
    Called when user clicks "Terminate session" button in bot.
    
    Note: session_token is the access token (possibly truncated to first 50 chars).
    We look up the user by telegram_id and terminate all their sessions.
    """
    try:
        redis_client = await get_redis()
        
        # Get the full access token stored during login
        stored_token = await redis_client.get(f"bot_login_token:{telegram_id}")
        if stored_token:
            full_token = stored_token.decode() if isinstance(stored_token, bytes) else stored_token
            logger.info(f"🔐 Found stored token for telegram_id={telegram_id}")
            
            # Revoke the full token
            security_manager.revoke_token(full_token)
            logger.info(f"🔐 Revoked full access token for telegram_id={telegram_id}")
            
            # Clean up the stored token
            await redis_client.delete(f"bot_login_token:{telegram_id}")
        
        # Look up user by telegram_id to get the actual user_id
        user_data = await user_repo.get_user_by_telegram_id(telegram_id)
        
        if user_data:
            user_id = user_data.get("id")
            logger.info(f"🔐 Found user_id={user_id} for telegram_id={telegram_id}")
            
            # Terminate all sessions for this user
            try:
                count = security_manager.terminate_all_user_sessions(str(user_id))
                logger.info(f"🔐 Terminated {count} sessions for user_id={user_id}")
            except Exception as e:
                logger.warning(f"Failed to terminate user sessions: {e}")
            
            # Revoke all cached tokens for this user
            try:
                security_manager.revoke_user_sessions(str(user_id))
                logger.info(f"🔐 Revoked all sessions for user_id={user_id}")
            except Exception as e:
                logger.warning(f"Failed to revoke user sessions: {e}")
        else:
            logger.warning(f"⚠️ No user found for telegram_id={telegram_id}")
        
        return {"status": "success", "message": "Session terminated"}
    except Exception as e:
        logger.error(f"Error terminating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to terminate session"
        )
