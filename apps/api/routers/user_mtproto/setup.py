"""
MTProto Setup Endpoints

Handles POST /setup and POST /resend endpoints for initiating MTProto verification flow.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.sessions import StringSession

from apps.api.middleware.auth import get_current_user_id
from apps.api.routers.user_mtproto.deps import get_user_bot_repository, safe_disconnect
from apps.api.routers.user_mtproto.models import (
    ErrorResponse,
    MTProtoSetupRequest,
    MTProtoSetupResponse,
)
from apps.api.routers.user_mtproto.session_storage import (
    get_pending_session,
    store_pending_session,
)
from core.services.encryption_service import get_encryption_service
from infra.db.repositories.user_bot_repository_factory import UserBotRepositoryFactory

logger = logging.getLogger(__name__)

router = APIRouter()


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
        masked_phone = f"{request.telegram_phone[:4]}****{request.telegram_phone[-3:]}"
        logger.info(f"Sending initial verification code to phone: {masked_phone}")
        result = await client.send_code_request(request.telegram_phone)
        phone_code_hash = result.phone_code_hash

        # Store session string for later verification (CRITICAL FIX for phone_code_hash expiry)
        session_string = session.save()
        store_pending_session(user_id, session_string)
        logger.info(
            f"Stored pending session for user {user_id} (session will expire in 10 minutes)"
        )

        # Log delivery method
        delivery_info = f"code_type={type(result.type).__name__}"
        if hasattr(result, "next_type") and result.next_type:
            delivery_info += f", next_type={type(result.next_type).__name__}"

        hash_preview = phone_code_hash[:8]
        logger.info(
            f"Initial code sent for user {user_id}, {delivery_info}, "
            f"phone_code_hash={hash_preview}..."
        )

        # Check if email setup is required
        if type(result.type).__name__ == "SentCodeTypeSetUpEmailRequired":
            await safe_disconnect(client)
            logger.warning(
                f"User {user_id} needs to complete email verification in Telegram account"
            )

            # Check if alternative sign-in methods are available
            alt_methods = []
            if hasattr(result.type, "google_signin_allowed") and getattr(
                result.type, "google_signin_allowed", False
            ):
                alt_methods.append("Google Sign-In")
            if hasattr(result.type, "apple_signin_allowed") and getattr(
                result.type, "apple_signin_allowed", False
            ):
                alt_methods.append("Apple Sign-In")

            detail_msg = (
                "⚠️ Email Verification Required\n\n"
                "Telegram requires email verification before API access. "
                "This is a one-time security check.\n\n"
                "Steps to fix:\n"
                "1. Open Telegram app → Settings → Privacy and Security → "
                "Two-Step Verification →Email\n"
                "2. If email is already added, check for a verification email "
                "and click the link\n"
                "3. Make sure the email shows as 'Verified' (not just added)\n"
                "4. Wait a few minutes, then try again\n\n"
                f"Note: SMS code will be sent after email verification "
                f"(next_type: {type(result.next_type).__name__})"
            )

            if alt_methods:
                alt_methods_text = " or ".join(alt_methods)
                detail_msg += (
                    f"\n\nAlternative: Use {alt_methods_text} in Telegram app "
                    "for instant verification."
                )

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
            message=(
                "Verification code sent! Check your Telegram app " "for a message from 'Telegram'."
            ),
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
            if hasattr(result, "next_type") and result.next_type:
                delivery_info += f", next_type={type(result.next_type).__name__}"

            hash_preview = phone_code_hash[:8]
            logger.info(
                f"Verification code resent for user {user_id}, {delivery_info}, "
                f"phone_code_hash={hash_preview}..."
            )

            # Check if email setup is required
            if type(result.type).__name__ == "SentCodeTypeSetUpEmailRequired":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Your Telegram account requires an email address to be set up. "
                        "Please open your Telegram app, go to Settings → "
                        "Privacy and Security → Email, and add an email address. "
                        "Then try again."
                    ),
                )

            return MTProtoSetupResponse(
                success=True,
                phone_code_hash=phone_code_hash,
                message=(
                    "Verification code sent! Check your Telegram app "
                    "for a message from 'Telegram'."
                ),
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
