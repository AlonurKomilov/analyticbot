"""
User MTProto API Router - FastAPI endpoints for user MTProto management.

Provides endpoints for users to configure their personal MTProto credentials
for reading channel history and analyzing posts.
"""

import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, validator
from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    SessionPasswordNeededError,
)
from telethon.sessions import StringSession

from apps.api.middleware.auth import get_current_user_id
from apps.mtproto.multi_tenant.user_mtproto_service import get_user_mtproto_service
from core.services.encryption_service import get_encryption_service
from infra.db.repositories.user_bot_repository_factory import UserBotRepositoryFactory

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/user-mtproto",
    tags=["User MTProto Management"],
)

# ============================================================================
# TEMPORARY SESSION STORAGE
# Store pending verification sessions to fix phone_code_hash expiry issue
# Key: user_id, Value: (session_string, timestamp)
# ============================================================================
from typing import Dict, Tuple
from time import time

_pending_sessions: Dict[int, Tuple[str, float]] = {}

def store_pending_session(user_id: int, session_string: str):
    """Store session string for pending verification (expires after 10 minutes)"""
    _pending_sessions[user_id] = (session_string, time())
    # Clean up old sessions (older than 10 minutes)
    current_time = time()
    expired_users = [uid for uid, (_, timestamp) in _pending_sessions.items() if current_time - timestamp > 600]
    for uid in expired_users:
        del _pending_sessions[uid]

def get_pending_session(user_id: int) -> str | None:
    """Get pending session string if exists and not expired"""
    if user_id in _pending_sessions:
        session_string, timestamp = _pending_sessions[user_id]
        if time() - timestamp < 600:  # 10 minutes
            return session_string
        else:
            del _pending_sessions[user_id]
    return None

def clear_pending_session(user_id: int):
    """Clear pending session after successful verification"""
    if user_id in _pending_sessions:
        del _pending_sessions[user_id]


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class MTProtoSetupRequest(BaseModel):
    """Initial MTProto setup with API credentials"""

    telegram_api_id: int = Field(..., description="Telegram API ID from my.telegram.org", gt=0)
    telegram_api_hash: str = Field(
        ..., description="Telegram API Hash from my.telegram.org", min_length=32
    )
    telegram_phone: str = Field(..., description="Phone number with country code")

    @validator("telegram_phone")
    def validate_phone(cls, v):
        # Basic validation
        if not v.startswith("+"):
            raise ValueError("Phone must start with +")
        if len(v) < 10:
            raise ValueError("Phone number too short")
        # Remove spaces and dashes for validation
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) < 10:
            raise ValueError("Phone must contain at least 10 digits")
        return v


class MTProtoVerifyRequest(BaseModel):
    """Verification code from Telegram"""

    verification_code: str = Field(
        ..., description="Code received via Telegram", min_length=5, max_length=6
    )
    phone_code_hash: str = Field(..., description="Hash from initial request")
    password: str | None = Field(None, description="2FA password if enabled")


class MTProtoStatusResponse(BaseModel):
    """Current MTProto configuration status"""

    configured: bool
    verified: bool
    phone: str | None = None  # Masked
    api_id: int | None = None
    connected: bool = False
    last_used: datetime | None = None
    can_read_history: bool = False
    mtproto_enabled: bool = True  # New field for toggle state


class MTProtoSetupResponse(BaseModel):
    """Response after initiating setup"""

    success: bool
    phone_code_hash: str
    message: str


class MTProtoActionResponse(BaseModel):
    """Generic success response"""

    success: bool
    message: str


class MTProtoToggleRequest(BaseModel):
    """Toggle MTProto functionality"""

    enabled: bool = Field(..., description="Enable or disable MTProto functionality")


class ChannelMTProtoSettingResponse(BaseModel):
    """Per-channel MTProto setting"""

    channel_id: int
    mtproto_enabled: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ChannelMTProtoSettingsListResponse(BaseModel):
    """List of all channel MTProto settings"""

    global_enabled: bool
    settings: list[ChannelMTProtoSettingResponse]


class ErrorResponse(BaseModel):
    """Error response"""

    detail: str


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


async def safe_disconnect(client: TelegramClient):
    """Safely disconnect Telethon client"""
    try:
        if client.is_connected():
            result = client.disconnect()
            if result is not None:
                await result
    except Exception as e:
        logger.warning(f"Error disconnecting client: {e}")


# ============================================================================
# DEPENDENCIES
# ============================================================================


async def get_user_bot_repository() -> UserBotRepositoryFactory:
    """Get user bot repository factory instance."""
    from apps.di import get_container

    container = get_container()
    session_factory = await container.database.async_session_maker()
    return UserBotRepositoryFactory(session_factory)


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get(
    "/status",
    response_model=MTProtoStatusResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_mtproto_status(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[UserBotRepositoryFactory, Depends(get_user_bot_repository)],
):
    """
    Get user's MTProto configuration status

    Returns information about whether MTProto is configured and working.
    """
    try:
        # Get credentials from database
        credentials = await repository.get_by_user_id(user_id)

        if not credentials:
            return MTProtoStatusResponse(
                configured=False,
                verified=False,
                can_read_history=False,
            )

        has_api_id = credentials.telegram_api_id is not None
        has_api_hash = credentials.telegram_api_hash is not None
        has_session = credentials.session_string is not None

        configured = has_api_id and has_api_hash
        verified = configured and has_session

        # Check if client is connected (only check pool, don't connect)
        connected = False
        last_used = None

        if verified:
            try:
                mtproto_service = get_user_mtproto_service()
                # Only check if client exists in pool, don't try to connect
                if user_id in mtproto_service._client_pool:
                    client = mtproto_service._client_pool[user_id]
                    connected = client._is_connected
                    last_used = client.last_used
            except Exception as e:
                logger.warning(f"Error checking MTProto connection for user {user_id}: {e}")

        # Mask phone number
        phone = credentials.telegram_phone
        if phone and len(phone) > 6:
            phone = phone[:4] + "****" + phone[-3:]

        # Check if MTProto is enabled
        mtproto_enabled = getattr(credentials, 'mtproto_enabled', True)

        return MTProtoStatusResponse(
            configured=configured,
            verified=verified,
            phone=phone,
            api_id=credentials.telegram_api_id if configured else None,
            connected=connected and mtproto_enabled,
            last_used=last_used,
            can_read_history=verified and connected and mtproto_enabled,
            mtproto_enabled=mtproto_enabled,  # Return the actual toggle state
        )

    except Exception as e:
        logger.error(f"Error getting MTProto status for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get MTProto status"
        )


@router.post(
    "/setup",
    response_model=MTProtoSetupResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid credentials"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def setup_mtproto(
    request: MTProtoSetupRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[UserBotRepositoryFactory, Depends(get_user_bot_repository)],
):
    """
    Initiate MTProto setup by sending verification code to phone

    Steps:
    1. User provides API ID, API Hash, and Phone
    2. System sends verification code to phone
    3. User receives code and calls /verify endpoint
    """
    try:
        # Create temporary Telethon client with empty session
        session = StringSession()
        client = TelegramClient(
            session,
            api_id=request.telegram_api_id,
            api_hash=request.telegram_api_hash,
        )

        await client.connect()

        # Send code request
        logger.info(f"Sending initial verification code to phone: {request.telegram_phone[:4]}****{request.telegram_phone[-3:]}")
        result = await client.send_code_request(request.telegram_phone)
        phone_code_hash = result.phone_code_hash
        
        # Store session string for later verification (CRITICAL FIX for phone_code_hash expiry)
        session_string = session.save()
        store_pending_session(user_id, session_string)
        logger.info(f"Stored pending session for user {user_id} (session will expire in 10 minutes)")
        
        # Log delivery method
        delivery_info = f"code_type={type(result.type).__name__}"
        if hasattr(result, 'next_type') and result.next_type:
            delivery_info += f", next_type={type(result.next_type).__name__}"
        logger.info(f"Initial code sent for user {user_id}, {delivery_info}, phone_code_hash={phone_code_hash[:8]}...")

        # Check if email setup is required
        if type(result.type).__name__ == 'SentCodeTypeSetUpEmailRequired':
            await safe_disconnect(client)
            logger.warning(f"User {user_id} needs to complete email verification in Telegram account")
            
            # Check if alternative sign-in methods are available
            alt_methods = []
            if hasattr(result.type, 'google_signin_allowed') and getattr(result.type, 'google_signin_allowed', False):
                alt_methods.append("Google Sign-In")
            if hasattr(result.type, 'apple_signin_allowed') and getattr(result.type, 'apple_signin_allowed', False):
                alt_methods.append("Apple Sign-In")
            
            detail_msg = (
                "⚠️ Email Verification Required\n\n"
                "Telegram requires email verification before API access. This is a one-time security check.\n\n"
                "Steps to fix:\n"
                "1. Open Telegram app → Settings → Privacy and Security → Two-Step Verification →Email\n"
                "2. If email is already added, check for a verification email and click the link\n"
                "3. Make sure the email shows as 'Verified' (not just added)\n"
                "4. Wait a few minutes, then try again\n\n"
                f"Note: SMS code will be sent after email verification (next_type: {type(result.next_type).__name__})"
            )
            
            if alt_methods:
                detail_msg += f"\n\nAlternative: Use {' or '.join(alt_methods)} in Telegram app for instant verification."
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail_msg,
            )

        await safe_disconnect(client)

        # Get or create credentials record
        credentials = await repository.get_by_user_id(user_id)

        encryption = get_encryption_service()
        encrypted_api_hash = encryption.encrypt(request.telegram_api_hash)

        if credentials:
            # Update existing record
            credentials.telegram_api_id = request.telegram_api_id
            credentials.telegram_api_hash = encrypted_api_hash
            credentials.telegram_phone = request.telegram_phone
            # Don't clear session_string yet - keep old one until verified
            await repository.update(credentials)
        else:
            # Create new record
            from core.models.user_bot_domain import BotStatus, UserBotCredentials

            credentials = UserBotCredentials(
                id=None,  # Will be set by database
                user_id=user_id,
                bot_token=encryption.encrypt("PENDING_BOT_TOKEN"),  # Placeholder
                bot_username="pending",
                bot_id=0,
                telegram_api_id=request.telegram_api_id,
                telegram_api_hash=encrypted_api_hash,
                telegram_phone=request.telegram_phone,
                session_string=None,
                status=BotStatus.PENDING,
                is_verified=False,
                rate_limit_rps=1.0,
                max_concurrent_requests=3,
            )
            await repository.create(credentials)

        logger.info(f"MTProto setup initiated for user {user_id}")

        return MTProtoSetupResponse(
            success=True,
            phone_code_hash=phone_code_hash,
            message="Verification code sent! Check your Telegram app for a message from 'Telegram'.",
        )

    except HTTPException:
        # Re-raise HTTPException without wrapping (preserves status code)
        raise
    except Exception as e:
        logger.error(f"Error setting up MTProto for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup MTProto: {str(e)}",
        )


@router.post(
    "/resend",
    response_model=MTProtoSetupResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "No pending setup found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def resend_mtproto_code(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[UserBotRepositoryFactory, Depends(get_user_bot_repository)],
):
    """
    Resend verification code using stored credentials

    This endpoint retrieves the user's stored MTProto credentials
    and re-sends the verification code without requiring them to 
    re-enter their API credentials.
    """
    try:
        # Get stored credentials
        credentials = await repository.get_by_user_id(user_id)

        if not credentials or not credentials.telegram_api_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending MTProto setup found. Please call /setup first.",
            )

        # Decrypt credentials
        encryption = get_encryption_service()
        if not credentials.telegram_api_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MTProto API hash not configured",
            )
        
        if not credentials.telegram_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number not configured",
            )

        api_hash = encryption.decrypt(credentials.telegram_api_hash)
        phone = credentials.telegram_phone

        # Try to reuse pending session first (CRITICAL FIX for phone_code_hash expiry)
        pending_session_str = get_pending_session(user_id)
        if pending_session_str:
            logger.info(f"Reusing existing session for user {user_id}")
            session = StringSession(pending_session_str)
        else:
            logger.info(f"Creating new session for user {user_id}")
            session = StringSession()
            
        client = TelegramClient(
            session,
            api_id=credentials.telegram_api_id,
            api_hash=api_hash,
        )

        await client.connect()

        try:
            # Request new verification code
            logger.info(f"Sending verification code to phone: {phone[:4]}****{phone[-3:]}")
            result = await client.send_code_request(phone)
            phone_code_hash = result.phone_code_hash
            
            # Store/update session string
            session_string = session.save()
            store_pending_session(user_id, session_string)

            # Log delivery method
            delivery_info = f"code_type={type(result.type).__name__}"
            if hasattr(result, 'next_type') and result.next_type:
                delivery_info += f", next_type={type(result.next_type).__name__}"
            logger.info(f"Verification code resent for user {user_id}, {delivery_info}, phone_code_hash={phone_code_hash[:8]}...")

            # Check if email setup is required
            if type(result.type).__name__ == 'SentCodeTypeSetUpEmailRequired':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Your Telegram account requires an email address to be set up. Please open your Telegram app, go to Settings → Privacy and Security → Email, and add an email address. Then try again.",
                )

            return MTProtoSetupResponse(
                success=True,
                phone_code_hash=phone_code_hash,
                message="Verification code sent! Check your Telegram app for a message from 'Telegram'.",
            )

        finally:
            await safe_disconnect(client)

    except HTTPException:
        raise
    except FloodWaitError as e:
        logger.error(f"FloodWaitError while resending code for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Please wait {e.seconds} seconds before trying again.",
        )
    except Exception as e:
        logger.error(f"Error resending verification code for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend verification code: {str(e)}",
        )


@router.post(
    "/verify",
    response_model=MTProtoActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid verification code or password"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def verify_mtproto(
    request: MTProtoVerifyRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[UserBotRepositoryFactory, Depends(get_user_bot_repository)],
):
    """
    Verify MTProto setup with code from Telegram

    Completes the authentication flow and stores the session.
    """
    try:
        # Get pending credentials
        credentials = await repository.get_by_user_id(user_id)

        if not credentials or not credentials.telegram_api_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending MTProto setup found. Call /setup first.",
            )

        # Decrypt credentials
        encryption = get_encryption_service()
        if not credentials.telegram_api_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="MTProto credentials not configured"
            )
        api_hash = encryption.decrypt(credentials.telegram_api_hash)

        # CRITICAL FIX: Reuse the pending session to avoid phone_code_hash expiry
        pending_session_str = get_pending_session(user_id)
        if not pending_session_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session expired. Please click 'Resend code' to get a new verification code.",
            )
        
        logger.info(f"Reusing stored session for user {user_id} verification")
        session = StringSession(pending_session_str)
        client = TelegramClient(
            session,
            api_id=credentials.telegram_api_id,
            api_hash=api_hash,
        )

        await client.connect()

        try:
            # Sign in with verification code
            phone = credentials.telegram_phone
            if not phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="No phone number configured"
                )

            logger.info(f"Attempting to verify user {user_id} with code={request.verification_code}, phone_code_hash={request.phone_code_hash[:8]}...")
            await client.sign_in(
                phone=phone,
                code=request.verification_code,
                phone_code_hash=request.phone_code_hash,
            )
            logger.info(f"Sign in successful for user {user_id}")

        except SessionPasswordNeededError:
            # 2FA is enabled
            if not request.password:
                await safe_disconnect(client)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="2FA is enabled. Please provide password.",
                )

            # Sign in with password
            await client.sign_in(password=request.password)

        except PhoneCodeInvalidError as e:
            await safe_disconnect(client)
            logger.warning(f"PhoneCodeInvalidError for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Invalid verification code. Please check the code and try again."
            )

        except PhoneCodeExpiredError as e:
            await safe_disconnect(client)
            logger.warning(f"PhoneCodeExpiredError for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code expired. Please click 'Resend code' to get a new one.",
            )

        # Get session string
        session_string = session.save()

        await safe_disconnect(client)

        # Clear pending session (no longer needed)
        clear_pending_session(user_id)

        # Encrypt and store session in database
        encrypted_session = encryption.encrypt(session_string)
        credentials.session_string = encrypted_session
        credentials.is_verified = True
        await repository.update(credentials)

        logger.info(f"MTProto verification successful for user {user_id}")

        return MTProtoActionResponse(
            success=True,
            message="MTProto setup completed successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying MTProto for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify MTProto: {str(e)}",
        )


@router.post(
    "/disconnect",
    response_model=MTProtoActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def disconnect_mtproto(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[UserBotRepositoryFactory, Depends(get_user_bot_repository)],
):
    """
    Disconnect and remove MTProto configuration

    This will:
    1. Disconnect active client
    2. Remove session from database
    3. Keep API ID/Hash for easy reconnection
    """
    try:
        # Disconnect from service
        try:
            mtproto_service = get_user_mtproto_service()
            await mtproto_service.disconnect_user(user_id)
        except Exception as e:
            logger.warning(f"Error disconnecting MTProto service for user {user_id}: {e}")

        # Clear session from database (keep API credentials)
        credentials = await repository.get_by_user_id(user_id)
        if credentials:
            credentials.session_string = None
            credentials.is_verified = False
            await repository.update(credentials)

        logger.info(f"MTProto disconnected for user {user_id}")

        return MTProtoActionResponse(success=True, message="MTProto disconnected successfully")

    except Exception as e:
        logger.error(f"Error disconnecting MTProto for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to disconnect MTProto"
        )


@router.delete(
    "/remove",
    response_model=MTProtoActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def remove_mtproto(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[UserBotRepositoryFactory, Depends(get_user_bot_repository)],
):
    """
    Completely remove MTProto configuration

    This will remove all MTProto credentials including API ID/Hash.
    """
    try:
        # Disconnect first
        try:
            mtproto_service = get_user_mtproto_service()
            await mtproto_service.disconnect_user(user_id)
        except Exception as e:
            logger.warning(f"Error disconnecting MTProto service for user {user_id}: {e}")

        # Remove all MTProto data from database
        credentials = await repository.get_by_user_id(user_id)
        if credentials:
            credentials.telegram_api_id = None
            credentials.telegram_api_hash = None
            credentials.telegram_phone = None
            credentials.session_string = None
            credentials.is_verified = False
            await repository.update(credentials)

        logger.info(f"MTProto configuration removed for user {user_id}")

        return MTProtoActionResponse(
            success=True, message="MTProto configuration removed successfully"
        )

    except Exception as e:
        logger.error(f"Error removing MTProto for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove MTProto configuration",
        )


@router.post(
    "/toggle",
    response_model=MTProtoActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "No MTProto configuration found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def toggle_mtproto(
    payload: MTProtoToggleRequest,
    http_request: Request,
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[UserBotRepositoryFactory, Depends(get_user_bot_repository)],
):
    """
    Enable or disable MTProto functionality
    
    When disabled:
    - MTProto client will be disconnected
    - Channel history reading will be unavailable
    - Only bot-based operations will work
    
    When enabled:
    - MTProto client can reconnect
    - Full channel history access restored
    """
    try:
        # Get credentials
        credentials = await repository.get_by_user_id(user_id)
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No MTProto configuration found. Please configure MTProto first.",
            )
        
        # If disabling, disconnect client
        if not payload.enabled and credentials.mtproto_enabled:
            try:
                mtproto_service = get_user_mtproto_service()
                await mtproto_service.disconnect_user(user_id)
                logger.info(f"Disconnected MTProto client for user {user_id} (disabled)")
            except Exception as e:
                logger.warning(f"Error disconnecting MTProto service for user {user_id}: {e}")
        
        # Update flag
        previous_state = credentials.mtproto_enabled
        credentials.mtproto_enabled = payload.enabled
        await repository.update(credentials)

        # Audit log the change
        try:
            from apps.di import get_container
            from apps.api.services.mtproto_audit_service import MTProtoAuditService

            container = get_container()
            session_factory = await container.database.async_session_maker()
            async with session_factory() as audit_session:
                audit_service = MTProtoAuditService(audit_session)
                await audit_service.log_toggle_event(
                    user_id=user_id,
                    enabled=payload.enabled,
                    request=http_request,
                    channel_id=None,
                    previous_state=previous_state,
                )
        except Exception as e:
            logger.warning(f"Failed to write MTProto audit log for user {user_id}: {e}")
        
        action = "enabled" if payload.enabled else "disabled"
        logger.info(f"MTProto {action} for user {user_id}")

        return MTProtoActionResponse(
            success=True,
            message=f"MTProto {action} successfully. {'Full history access is now available.' if payload.enabled else 'Only bot-based operations are available.'}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling MTProto for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle MTProto functionality",
        )


# ============================================================================
# PER-CHANNEL MTPROTO ENDPOINTS
# ============================================================================


@router.get(
    "/channels/settings",
    response_model=ChannelMTProtoSettingsListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_all_channel_settings(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[UserBotRepositoryFactory, Depends(get_user_bot_repository)],
):
    """
    Get all per-channel MTProto settings for the user
    
    Returns the global MTProto enabled flag plus any per-channel overrides.
    If no per-channel setting exists, the channel inherits the global setting.
    """
    try:
        from apps.di import get_container
        from infra.db.repositories.channel_mtproto_repository import ChannelMTProtoRepository

        # Get global setting
        credentials = await repository.get_by_user_id(user_id)
        global_enabled = credentials.mtproto_enabled if credentials else False

        # Get per-channel settings
        container = get_container()
        session_factory = await container.database.async_session_maker()
        async with session_factory() as session:
            channel_repo = ChannelMTProtoRepository(session)
            settings = await channel_repo.get_user_settings(user_id)

        settings_list = [
            ChannelMTProtoSettingResponse(
                channel_id=s.channel_id,
                mtproto_enabled=s.mtproto_enabled,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in settings
        ]

        return ChannelMTProtoSettingsListResponse(
            global_enabled=global_enabled,
            settings=settings_list,
        )

    except Exception as e:
        logger.error(f"Error fetching channel MTProto settings for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch channel settings",
        )


@router.get(
    "/channels/{channel_id}/settings",
    response_model=ChannelMTProtoSettingResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Setting not found (uses global default)"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_channel_setting(
    channel_id: int,
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    """
    Get MTProto setting for a specific channel
    
    If no per-channel setting exists, returns 404 (channel uses global default).
    """
    try:
        from apps.di import get_container
        from infra.db.repositories.channel_mtproto_repository import ChannelMTProtoRepository

        container = get_container()
        session_factory = await container.database.async_session_maker()
        async with session_factory() as session:
            channel_repo = ChannelMTProtoRepository(session)
            setting = await channel_repo.get_setting(user_id, channel_id)

        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No per-channel setting for channel {channel_id} (uses global default)",
            )

        return ChannelMTProtoSettingResponse(
            channel_id=setting.channel_id,
            mtproto_enabled=setting.mtproto_enabled,
            created_at=setting.created_at,
            updated_at=setting.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching channel {channel_id} MTProto setting: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch channel setting",
        )


@router.post(
    "/channels/{channel_id}/toggle",
    response_model=MTProtoActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def toggle_channel_mtproto(
    channel_id: int,
    payload: MTProtoToggleRequest,
    http_request: Request,
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[UserBotRepositoryFactory, Depends(get_user_bot_repository)],
):
    """
    Enable or disable MTProto for a specific channel
    
    Creates or updates a per-channel override. Even if global MTProto is enabled,
    you can disable it for specific channels, and vice versa (though global=disabled
    will still prevent access).
    """
    try:
        from apps.di import get_container
        from infra.db.repositories.channel_mtproto_repository import ChannelMTProtoRepository
        from apps.api.services.mtproto_audit_service import MTProtoAuditService

        # Get credentials to ensure user has MTProto configured
        credentials = await repository.get_by_user_id(user_id)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No MTProto configuration found. Please configure MTProto first.",
            )

        container = get_container()
        session_factory = await container.database.async_session_maker()

        # Get previous state for audit
        async with session_factory() as session:
            channel_repo = ChannelMTProtoRepository(session)
            previous_setting = await channel_repo.get_setting(user_id, channel_id)
            previous_state = previous_setting.mtproto_enabled if previous_setting else None

        # Create or update per-channel setting
        async with session_factory() as session:
            channel_repo = ChannelMTProtoRepository(session)
            await channel_repo.create_or_update(user_id, channel_id, payload.enabled)

        # Audit log the change
        try:
            async with session_factory() as audit_session:
                audit_service = MTProtoAuditService(audit_session)
                await audit_service.log_toggle_event(
                    user_id=user_id,
                    enabled=payload.enabled,
                    request=http_request,
                    channel_id=channel_id,
                    previous_state=previous_state,
                )
        except Exception as e:
            logger.warning(f"Failed to write MTProto audit log for channel {channel_id}: {e}")

        action = "enabled" if payload.enabled else "disabled"
        logger.info(f"MTProto {action} for user {user_id}, channel {channel_id}")

        return MTProtoActionResponse(
            success=True,
            message=f"MTProto {action} for channel {channel_id}. "
            f"{'This channel can now read history (if global MTProto is also enabled).' if payload.enabled else 'This channel cannot read history.'}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling channel {channel_id} MTProto for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle channel MTProto setting",
        )


@router.delete(
    "/channels/{channel_id}/settings",
    response_model=MTProtoActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Setting not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_channel_setting(
    channel_id: int,
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    """
    Delete per-channel MTProto setting (reverts to global default)
    
    After deletion, the channel will inherit the global MTProto enabled/disabled state.
    """
    try:
        from apps.di import get_container
        from infra.db.repositories.channel_mtproto_repository import ChannelMTProtoRepository

        container = get_container()
        session_factory = await container.database.async_session_maker()
        async with session_factory() as session:
            channel_repo = ChannelMTProtoRepository(session)
            deleted = await channel_repo.delete_setting(user_id, channel_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No per-channel setting found for channel {channel_id}",
            )

        logger.info(f"Deleted per-channel MTProto setting for user {user_id}, channel {channel_id}")

        return MTProtoActionResponse(
            success=True,
            message=f"Per-channel setting deleted for channel {channel_id}. Now uses global default.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting channel {channel_id} MTProto setting: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete channel setting",
        )
