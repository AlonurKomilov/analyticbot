"""
Channel Validation Endpoint

Validates Telegram channels before creation.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from apps.api.middleware.auth import get_current_user
from apps.api.services.telegram_validation_service import (
    ChannelValidationResult,
    TelegramValidationService,
)

from .deps import get_telegram_validation_service
from .models import ValidateChannelRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/validate", response_model=ChannelValidationResult)
async def validate_telegram_channel(
    request_data: ValidateChannelRequest,
    current_user: dict = Depends(get_current_user),
    telegram_service: TelegramValidationService = Depends(get_telegram_validation_service),
):
    """
    ## ✅ Validate Telegram Channel

    Validate a Telegram channel by username and fetch metadata before creation.
    This endpoint checks if the channel exists and returns its information.

    **🔒 SECURITY: Bot/MTProto Admin Verification**
    - Verifies that your bot or MTProto session is an admin of the channel
    - Prevents users from adding channels they don't own
    - Works for all login methods (email/telegram)

    **Authentication Required:**
    - Valid JWT token in Authorization header

    **Request Body:**
    ```json
    {
        "username": "@channelname"
    }
    ```

    **Returns:**
    - Channel validation result with metadata (telegram_id, subscriber_count, etc.)
    - is_admin: true/false indicating if your bot/MTProto has admin access
    - Error message if validation fails
    """
    try:
        logger.info(
            f"Validating channel: {request_data.username} for user {current_user.get('id')}"
        )

        # First, validate channel exists and get metadata
        result = await telegram_service.validate_channel_by_username(request_data.username)

        if not result.is_valid:
            return result

        # Check if the connected bot/MTProto session is an admin in this channel
        # This verifies actual ownership regardless of login method (email/telegram)
        is_admin, error_msg = await telegram_service.check_bot_admin_access(request_data.username)

        result.is_admin = is_admin

        if not is_admin:
            result.error_message = error_msg or (
                "Your bot or MTProto session must be added as an admin to this channel. "
                "Please add your bot/account as an admin in Telegram, then try again."
            )
            logger.warning(
                f"User {current_user.get('id')}'s bot/MTProto session is not admin of "
                f"@{request_data.username}"
            )
        else:
            logger.info(
                f"✅ User {current_user.get('id')}'s bot/MTProto verified as admin of "
                f"@{request_data.username}"
            )

        return result

    except Exception as e:
        logger.error(f"Failed to validate channel: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
