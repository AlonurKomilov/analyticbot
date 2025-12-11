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
    MTProtoQR2FARequest,
    MTProtoSetupRequest,
    MTProtoSetupResponse,
)
from apps.api.routers.user_mtproto.session_storage import (
    get_pending_session,
    store_pending_session,
)
from core.ports.user_bot_repository import IUserBotRepository
from core.services.encryption_service import get_encryption_service

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
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Initiate MTProto setup by sending verification code to phone

    Steps:
    1. User provides API ID, API Hash, and Phone
    2. System sends verification code to phone
    3. User receives code and calls /verify endpoint
    """
    try:
        # Check if this phone is already assigned to another user
        existing = await repository.get_by_mtproto_phone(request.mtproto_phone)
        if existing and existing.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"This Telegram account ({request.mtproto_phone}) is already connected to another user. "
                f"Each Telegram account can only be linked to one AnalyticBot account. "
                f"Please use a different Telegram account.",
            )

        # Create temporary Telethon client with empty session
        session = StringSession()
        client = TelegramClient(
            session,
            api_id=request.mtproto_api_id,
            api_hash=request.telegram_api_hash,
        )

        await client.connect()

        # Send code request
        masked_phone = f"{request.mtproto_phone[:4]}****{request.mtproto_phone[-3:]}"
        logger.info(f"Sending initial verification code to phone: {masked_phone}")
        result = await client.send_code_request(request.mtproto_phone)
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
            credentials.mtproto_api_id = request.mtproto_api_id
            credentials.telegram_api_hash = encrypted_api_hash
            credentials.mtproto_phone = request.mtproto_phone
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
                mtproto_api_id=request.mtproto_api_id,
                telegram_api_hash=encrypted_api_hash,
                mtproto_phone=request.mtproto_phone,
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
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
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

        if not credentials or not credentials.mtproto_api_id:
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

        if not credentials.mtproto_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number not configured",
            )

        api_hash = encryption.decrypt(credentials.telegram_api_hash)
        phone = credentials.mtproto_phone

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
            api_id=credentials.mtproto_api_id,
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


@router.post(
    "/setup-simple",
    response_model=MTProtoSetupResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid phone number"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def setup_mtproto_simple(
    request: "MTProtoSimpleSetupRequest",
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Simplified MTProto setup - only requires phone number.

    Uses system-provided API credentials so users don't need to
    create their own app at my.telegram.org.

    Steps:
    1. User provides only their phone number
    2. System sends verification code to phone
    3. User calls /verify endpoint with the code
    """
    import os

    # Get system default API credentials from environment
    default_api_id = int(os.getenv("TELEGRAM_API_ID", "0"))
    default_api_hash = os.getenv("TELEGRAM_API_HASH", "")

    if not default_api_id or not default_api_hash:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System MTProto credentials not configured. Please contact support.",
        )

    # Validate phone format
    phone = request.mtproto_phone.strip()
    if not phone.startswith("+"):
        phone = "+" + phone

    # Remove spaces and dashes
    phone = "".join(c for c in phone if c.isdigit() or c == "+")

    if len(phone) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number too short. Please include country code (e.g., +1234567890)",
        )

    # Check if this phone is already assigned to another user
    existing = await repository.get_by_mtproto_phone(phone)
    if existing and existing.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This Telegram account ({phone}) is already connected to another user. "
            f"Each Telegram account can only be linked to one AnalyticBot account. "
            f"Please use a different Telegram account.",
        )

    try:
        # Create temporary Telethon client with empty session
        session = StringSession()
        client = TelegramClient(
            session,
            api_id=default_api_id,
            api_hash=default_api_hash,
        )

        await client.connect()

        # Send code request
        masked_phone = f"{phone[:4]}****{phone[-3:]}"
        logger.info(f"[Simple Setup] Sending verification code to phone: {masked_phone}")
        result = await client.send_code_request(phone)
        phone_code_hash = result.phone_code_hash

        # Store session string for later verification
        session_string = session.save()
        store_pending_session(user_id, session_string)
        logger.info(f"[Simple Setup] Stored pending session for user {user_id}")

        await safe_disconnect(client)

        # Get or create credentials record
        credentials = await repository.get_by_user_id(user_id)

        encryption = get_encryption_service()
        encrypted_api_hash = encryption.encrypt(default_api_hash)

        if credentials:
            # Update existing record
            credentials.mtproto_api_id = default_api_id
            credentials.telegram_api_hash = encrypted_api_hash
            credentials.mtproto_phone = phone
            await repository.update(credentials)
        else:
            # Create new record
            from core.models.user_bot_domain import BotStatus, UserBotCredentials

            credentials = UserBotCredentials(
                id=None,
                user_id=user_id,
                bot_token=encryption.encrypt("PENDING_BOT_TOKEN"),
                bot_username="pending",
                bot_id=0,
                mtproto_api_id=default_api_id,
                telegram_api_hash=encrypted_api_hash,
                mtproto_phone=phone,
                session_string=None,
                status=BotStatus.PENDING,
                is_verified=False,
                rate_limit_rps=1.0,
                max_concurrent_requests=3,
            )
            await repository.create(credentials)

        logger.info(f"[Simple Setup] MTProto setup initiated for user {user_id}")

        return MTProtoSetupResponse(
            success=True,
            phone_code_hash=phone_code_hash,
            message="Verification code sent! Check your Telegram app for a message.",
        )

    except FloodWaitError as e:
        logger.error(f"[Simple Setup] FloodWaitError for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Please wait {e.seconds} seconds.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Simple Setup] Error for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup MTProto: {str(e)}",
        )


# Import for type hint
from datetime import UTC

from apps.api.routers.user_mtproto.models import (
    MTProtoQRLoginResponse,
    MTProtoQRStatusResponse,
    MTProtoSimpleSetupRequest,
)

# QR Code Login - In-memory storage for pending QR sessions
_qr_pending_sessions: dict[int, dict] = {}


@router.post(
    "/qr-login/request",
    response_model=MTProtoQRLoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def request_qr_login(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Request QR code for login.

    The user scans this QR code with their Telegram app to authenticate.
    QR code is valid for ~30 seconds and must be refreshed.

    Returns:
    - qr_code_url: URL to encode in QR code (tg://login?token=...)
    - qr_code_base64: Pre-generated QR code image (if qrcode library available)
    - expires_in: Seconds until expiration
    """
    import base64
    import os
    from io import BytesIO

    # Get system default API credentials from environment
    default_api_id = int(os.getenv("TELEGRAM_API_ID", "0"))
    default_api_hash = os.getenv("TELEGRAM_API_HASH", "")

    if not default_api_id or not default_api_hash:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System MTProto credentials not configured. Please contact support.",
        )

    try:
        # Create temporary Telethon client with empty session
        session = StringSession()
        client = TelegramClient(
            session,
            api_id=default_api_id,
            api_hash=default_api_hash,
        )

        await client.connect()

        # Request QR code token
        logger.info(f"[QR Login] Requesting QR code for user {user_id}")

        from telethon.tl.functions.auth import ExportLoginTokenRequest

        result = await client(
            ExportLoginTokenRequest(api_id=default_api_id, api_hash=default_api_hash, except_ids=[])
        )

        # Build the login URL
        token_bytes = result.token
        token_base64 = base64.urlsafe_b64encode(token_bytes).decode("utf-8").rstrip("=")
        qr_url = f"tg://login?token={token_base64}"

        # Calculate expiration - result.expires is a datetime object
        from datetime import datetime

        now_ts = datetime.now(UTC).timestamp()
        # Handle both datetime and int/float types for expires
        if hasattr(result.expires, "timestamp"):
            expires_ts = result.expires.timestamp()
        else:
            expires_ts = float(result.expires)
        expires_in = max(1, int(expires_ts - now_ts))

        # Store session for later polling
        session_string = session.save()
        _qr_pending_sessions[user_id] = {
            "session_string": session_string,
            "api_id": default_api_id,
            "api_hash": default_api_hash,
            "token": token_bytes,
            "expires": expires_ts,  # Store as timestamp
        }

        # Try to generate QR code image
        qr_base64 = None
        try:
            import qrcode

            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        except ImportError:
            logger.warning("qrcode library not installed, returning URL only")
        except Exception as e:
            logger.warning(f"Failed to generate QR image: {e}")

        # Don't disconnect yet - keep for polling
        await safe_disconnect(client)

        logger.info(f"[QR Login] QR code generated for user {user_id}, expires in {expires_in}s")

        return MTProtoQRLoginResponse(
            success=True,
            qr_code_url=qr_url,
            qr_code_base64=qr_base64,
            expires_in=expires_in,
            message="Scan this QR code with your Telegram app to login",
        )

    except Exception as e:
        logger.error(f"[QR Login] Error for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate QR code: {str(e)}",
        )


@router.get(
    "/qr-login/status",
    response_model=MTProtoQRStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def check_qr_login_status(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Check if QR code has been scanned and login completed.

    Frontend should poll this endpoint every 2-3 seconds after
    displaying the QR code.

    Returns:
    - status: "pending" (waiting for scan), "success" (logged in), "expired" (need new QR)
    """
    from datetime import datetime

    pending = _qr_pending_sessions.get(user_id)

    if not pending:
        return MTProtoQRStatusResponse(
            status="expired",
            success=False,
            message="No pending QR login. Please request a new QR code.",
        )

    # Check if expired
    if datetime.now(UTC).timestamp() > pending["expires"]:
        del _qr_pending_sessions[user_id]
        return MTProtoQRStatusResponse(
            status="expired",
            success=False,
            message="QR code expired. Please request a new one.",
        )

    try:
        # Recreate client from stored session
        session = StringSession(pending["session_string"])
        client = TelegramClient(
            session,
            api_id=pending["api_id"],
            api_hash=pending["api_hash"],
        )

        await client.connect()

        from telethon.tl.functions.auth import ExportLoginTokenRequest

        # Try to export token again - if successful with auth, we're logged in
        try:
            result = await client(
                ExportLoginTokenRequest(
                    api_id=pending["api_id"], api_hash=pending["api_hash"], except_ids=[]
                )
            )

            # Check result type
            result_type = type(result).__name__

            if result_type == "LoginTokenSuccess":
                # Login successful!
                logger.info(f"[QR Login] Success for user {user_id}")

                # Get authorization details
                auth = result.authorization
                tg_user_id = auth.user.id if hasattr(auth, "user") else None
                tg_username = (
                    auth.user.username
                    if hasattr(auth, "user") and hasattr(auth.user, "username")
                    else None
                )

                # Save session
                session_string = session.save()

                # Store credentials
                encryption = get_encryption_service()
                encrypted_api_hash = encryption.encrypt(pending["api_hash"])
                encrypted_session = encryption.encrypt(session_string)

                credentials = await repository.get_by_user_id(user_id)

                if credentials:
                    credentials.mtproto_id = tg_user_id  # Store MTProto user ID
                    credentials.mtproto_username = tg_username  # Store MTProto username
                    credentials.mtproto_api_id = pending["api_id"]
                    credentials.telegram_api_hash = encrypted_api_hash
                    credentials.session_string = encrypted_session
                    credentials.is_verified = True
                    await repository.update(credentials)
                else:
                    from core.models.user_bot_domain import BotStatus, UserBotCredentials

                    credentials = UserBotCredentials(
                        id=None,
                        user_id=user_id,
                        bot_token=encryption.encrypt("PENDING_BOT_TOKEN"),
                        bot_username="pending",
                        bot_id=0,
                        mtproto_id=tg_user_id,  # Store MTProto user ID
                        mtproto_username=tg_username,  # Store MTProto username
                        mtproto_api_id=pending["api_id"],
                        telegram_api_hash=encrypted_api_hash,
                        mtproto_phone=None,  # QR login doesn't need phone
                        session_string=encrypted_session,
                        status=BotStatus.ACTIVE,
                        is_verified=True,
                        rate_limit_rps=1.0,
                        max_concurrent_requests=3,
                    )
                    await repository.create(credentials)

                # Cleanup
                del _qr_pending_sessions[user_id]
                await safe_disconnect(client)

                return MTProtoQRStatusResponse(
                    status="success",
                    success=True,
                    message="Login successful! You can now use MTProto features.",
                    user_id=tg_user_id,
                )

            elif result_type == "LoginTokenMigrateTo":
                # Need to migrate to another DC
                logger.info(f"[QR Login] Migration needed for user {user_id}")
                await safe_disconnect(client)
                return MTProtoQRStatusResponse(
                    status="pending",
                    success=False,
                    message="Processing login... please wait.",
                )

            else:
                # Still waiting for scan
                # Update stored session
                _qr_pending_sessions[user_id]["session_string"] = session.save()
                await safe_disconnect(client)
                return MTProtoQRStatusResponse(
                    status="pending",
                    success=False,
                    message="Waiting for QR code scan...",
                )

        except Exception as inner_e:
            error_name = type(inner_e).__name__

            if "SessionPasswordNeeded" in error_name:
                # 2FA required - user needs to enter password
                logger.info(f"[QR Login] 2FA required for user {user_id}")
                # Keep the session for 2FA verification
                _qr_pending_sessions[user_id]["session_string"] = session.save()
                _qr_pending_sessions[user_id]["needs_2fa"] = True
                await safe_disconnect(client)
                return MTProtoQRStatusResponse(
                    status="2fa_required",
                    success=False,
                    message="Two-factor authentication required. Please enter your password.",
                    needs_2fa=True,
                )

            raise inner_e

    except Exception as e:
        logger.error(f"[QR Login] Error checking status for user {user_id}: {e}")
        return MTProtoQRStatusResponse(
            status="error",
            success=False,
            message=f"Error checking login status: {str(e)}",
        )


@router.post(
    "/qr-login/2fa",
    response_model=MTProtoQRStatusResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid password"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def verify_qr_login_2fa(
    request: MTProtoQR2FARequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Complete QR login with 2FA password.

    Called when QR status returns '2fa_required'. User must provide their
    Telegram two-factor authentication password.
    """
    pending = _qr_pending_sessions.get(user_id)

    if not pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending QR login session. Please request a new QR code.",
        )

    if not pending.get("needs_2fa"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA not required for this session.",
        )

    try:
        # Recreate client from stored session
        session = StringSession(pending["session_string"])
        client = TelegramClient(
            session,
            api_id=pending["api_id"],
            api_hash=pending["api_hash"],
        )

        await client.connect()

        # Sign in with password
        from telethon.errors import PasswordHashInvalidError

        try:
            await client.sign_in(password=request.password)
        except PasswordHashInvalidError:
            await safe_disconnect(client)
            return MTProtoQRStatusResponse(
                status="2fa_required",
                success=False,
                message="Invalid password. Please try again.",
                needs_2fa=True,
            )

        # Check if we're now authorized
        if await client.is_user_authorized():
            logger.info(f"[QR Login 2FA] Success for user {user_id}")

            # Get user info
            me = await client.get_me()
            tg_user_id = me.id if me else None
            tg_username = me.username if me else None

            # Save session
            session_string = session.save()

            # Store credentials
            encryption = get_encryption_service()
            encrypted_api_hash = encryption.encrypt(pending["api_hash"])
            encrypted_session = encryption.encrypt(session_string)

            credentials = await repository.get_by_user_id(user_id)

            if credentials:
                credentials.mtproto_id = tg_user_id  # Store MTProto user ID
                credentials.mtproto_username = tg_username  # Store MTProto username
                credentials.mtproto_api_id = pending["api_id"]
                credentials.telegram_api_hash = encrypted_api_hash
                credentials.session_string = encrypted_session
                credentials.is_verified = True
                await repository.update(credentials)
            else:
                from core.models.user_bot_domain import BotStatus, UserBotCredentials

                credentials = UserBotCredentials(
                    id=None,
                    user_id=user_id,
                    bot_token=encryption.encrypt("PENDING_BOT_TOKEN"),
                    bot_username="pending",
                    bot_id=0,
                    mtproto_id=tg_user_id,  # Store MTProto user ID
                    mtproto_username=tg_username,  # Store MTProto username
                    mtproto_api_id=pending["api_id"],
                    telegram_api_hash=encrypted_api_hash,
                    mtproto_phone=None,
                    session_string=encrypted_session,
                    status=BotStatus.ACTIVE,
                    is_verified=True,
                    rate_limit_rps=1.0,
                    max_concurrent_requests=3,
                )
                await repository.create(credentials)

            # Cleanup
            del _qr_pending_sessions[user_id]
            await safe_disconnect(client)

            return MTProtoQRStatusResponse(
                status="success",
                success=True,
                message="Login successful! You can now use MTProto features.",
                user_id=tg_user_id,
            )
        else:
            await safe_disconnect(client)
            return MTProtoQRStatusResponse(
                status="error",
                success=False,
                message="Authentication failed. Please try again.",
            )

    except Exception as e:
        logger.error(f"[QR Login 2FA] Error for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify 2FA: {str(e)}",
        )
