"""
User MTProto API Router - FastAPI endpoints for user MTProto management.

Provides endpoints for users to configure their personal MTProto credentials
for reading channel history and analyzing posts.
"""

import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from telethon import TelegramClient
from telethon.errors import PhoneCodeExpiredError, PhoneCodeInvalidError, SessionPasswordNeededError
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


class MTProtoSetupResponse(BaseModel):
    """Response after initiating setup"""

    success: bool
    phone_code_hash: str
    message: str


class MTProtoActionResponse(BaseModel):
    """Generic success response"""

    success: bool
    message: str


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

        # Check if client is connected
        connected = False
        last_used = None

        if verified:
            try:
                mtproto_service = get_user_mtproto_service()
                client = await mtproto_service.get_user_client(user_id)
                if client:
                    connected = client._is_connected
                    last_used = client.last_used
            except Exception as e:
                logger.warning(f"Error checking MTProto connection for user {user_id}: {e}")

        # Mask phone number
        phone = credentials.telegram_phone
        if phone and len(phone) > 6:
            phone = phone[:4] + "****" + phone[-3:]

        return MTProtoStatusResponse(
            configured=configured,
            verified=verified,
            phone=phone,
            api_id=credentials.telegram_api_id if configured else None,
            connected=connected,
            last_used=last_used,
            can_read_history=verified and connected,
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
        # Create temporary Telethon client
        client = TelegramClient(
            StringSession(),
            api_id=request.telegram_api_id,
            api_hash=request.telegram_api_hash,
        )

        await client.connect()

        # Send code request
        result = await client.send_code_request(request.telegram_phone)
        phone_code_hash = result.phone_code_hash

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
            message=f"Verification code sent to {request.telegram_phone}",
        )

    except Exception as e:
        logger.error(f"Error setting up MTProto for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup MTProto: {str(e)}",
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

        # Create client with stored credentials
        session = StringSession()
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

            await client.sign_in(
                phone=phone,
                code=request.verification_code,
                phone_code_hash=request.phone_code_hash,
            )

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

        except PhoneCodeInvalidError:
            await safe_disconnect(client)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code"
            )

        except PhoneCodeExpiredError:
            await safe_disconnect(client)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code expired. Please request a new one.",
            )

        # Get session string
        session_string = session.save()

        await safe_disconnect(client)

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
