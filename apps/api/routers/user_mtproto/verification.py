"""
MTProto Verification Endpoint

Handles POST /verify endpoint for completing MTProto verification with code.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from telethon import TelegramClient
from telethon.errors import (
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    SessionPasswordNeededError,
)
from telethon.sessions import StringSession

from apps.api.middleware.auth import get_current_user_id
from apps.api.routers.user_mtproto.deps import get_user_bot_repository, safe_disconnect
from apps.api.routers.user_mtproto.models import (
    ErrorResponse,
    MTProtoActionResponse,
    MTProtoVerifyRequest,
)
from apps.api.routers.user_mtproto.session_storage import (
    clear_pending_session,
    get_pending_session,
)
from core.ports.user_bot_repository import IUserBotRepository
from core.services.encryption_service import get_encryption_service

logger = logging.getLogger(__name__)

router = APIRouter()


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
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Verify MTProto setup with code from Telegram

    Completes the authentication flow and stores the session.
    """
    try:
        # Get pending credentials
        credentials = await repository.get_by_user_id(user_id)

        if not credentials or not credentials.mtproto_api_id:
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
                detail=(
                    "Session expired. Please click 'Resend code' to get a new " "verification code."
                ),
            )

        logger.info(f"Reusing stored session for user {user_id} verification")
        session = StringSession(pending_session_str)
        client = TelegramClient(
            session,
            api_id=credentials.mtproto_api_id,
            api_hash=api_hash,
        )

        await client.connect()

        try:
            # Sign in with verification code
            phone = credentials.mtproto_phone
            if not phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="No phone number configured"
                )

            hash_preview = request.phone_code_hash[:8]
            logger.info(
                f"Attempting to verify user {user_id} with "
                f"code={request.verification_code}, "
                f"phone_code_hash={hash_preview}..."
            )
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
                detail="Invalid verification code. Please check the code and try again.",
            )

        except PhoneCodeExpiredError as e:
            await safe_disconnect(client)
            logger.warning(f"PhoneCodeExpiredError for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code expired. Please click 'Resend code' to get a new one.",
            )

        # Get session string and MTProto user info
        session_string = session.save()

        # Get the MTProto user info (Telegram ID and username of the authenticated account)
        me = await client.get_me()
        mtproto_id = me.id if me else None
        mtproto_username = me.username if me else None
        logger.info(
            f"MTProto user ID for user {user_id}: {mtproto_id}, username: {mtproto_username}"
        )

        await safe_disconnect(client)

        # Clear pending session (no longer needed)
        clear_pending_session(user_id)

        # Encrypt and store session in database
        encrypted_session = encryption.encrypt(session_string)
        credentials.session_string = encrypted_session
        credentials.mtproto_id = mtproto_id  # Store the MTProto user ID
        credentials.mtproto_username = mtproto_username  # Store the MTProto username
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
