"""
User Bot API Router - FastAPI endpoints for user bot management.

Provides endpoints for users to create, manage, and verify their bots.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.middleware.auth import get_current_user_id  # Use existing auth system
from apps.api.services.bot_service_factory import create_user_bot_service
from apps.di import get_container
from core.ports.user_bot_repository import IUserBotRepository
from core.schemas.user_bot_schemas import (
    BotCreatedResponse,
    BotRemovedResponse,
    BotStatusResponse,
    BotVerificationResponse,
    CreateBotRequest,
    ErrorResponse,
    RateLimitUpdateResponse,
    UpdateRateLimitRequest,
    VerifyBotRequest,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/user-bot",
    tags=["User Bot Management"],
)


# ==================== Dependency Injection ====================


async def get_user_bot_repository() -> IUserBotRepository:
    """Get user bot repository from DI container."""
    container = get_container()
    return await container.database.user_bot_repo()


# ==================== User Bot Endpoints ====================


@router.post(
    "/create",
    response_model=BotCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid bot token or user already has a bot"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def create_user_bot(
    request: CreateBotRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Create a new bot for the current user.

    - **bot_token**: Bot token from @BotFather (required)
    - **bot_username**: Bot username (optional, will be fetched)
    - **api_id**: Telegram API ID for MTProto (optional)
    - **api_hash**: Telegram API Hash for MTProto (optional)
    - **max_requests_per_second**: Rate limit per second (1-100, default: 30)
    - **max_concurrent_requests**: Max concurrent requests (1-50, default: 10)
    """
    try:
        service = await create_user_bot_service(repository)

        credentials = await service.create_user_bot(
            user_id=user_id,
            bot_token=request.bot_token,
            bot_username=request.bot_username,
            api_id=request.api_id,
            api_hash=request.api_hash,
            max_requests_per_second=request.max_requests_per_second,
            max_concurrent_requests=request.max_concurrent_requests,
        )

        if credentials.id is None:
            raise ValueError("Failed to create bot: credentials ID is None")

        return BotCreatedResponse(
            id=credentials.id,
            status=credentials.status,
            bot_username=credentials.bot_username,
            requires_verification=True,
        )

    except ValueError as e:
        logger.warning(f"Failed to create bot for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        import traceback

        logger.error(f"Error creating bot for user {user_id}: {e}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create bot",
        )


@router.get(
    "/status",
    response_model=BotStatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Bot not found"},
    },
)
async def get_bot_status(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Get the status of the current user's bot.

    Returns bot configuration, status, verification state, and usage statistics.
    """
    try:
        logger.info(f"🔍 Getting bot status for user_id={user_id}")
        service = await create_user_bot_service(repository)
        logger.info("✅ Service created, calling get_user_bot_status...")
        credentials = await service.get_user_bot_status(user_id)
        logger.info(f"📊 Credentials result: {credentials}")

        if not credentials:
            logger.warning(f"❌ No bot found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No bot found for this user",
            )

        if credentials.id is None:
            logger.error(f"❌ Bot credentials ID is None for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Bot credentials ID is None",
            )

        return BotStatusResponse(
            id=credentials.id,
            user_id=credentials.user_id,
            bot_username=credentials.bot_username,
            bot_id=credentials.bot_id,
            status=credentials.status,
            is_verified=credentials.is_verified,
            max_requests_per_second=int(credentials.rate_limit_rps),
            max_concurrent_requests=credentials.max_concurrent_requests,
            total_requests=credentials.total_requests,
            last_used_at=credentials.last_used_at,
            created_at=credentials.created_at,
            updated_at=credentials.updated_at,
            suspension_reason=credentials.suspension_reason,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting bot status for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bot status: {str(e)}",
        )


@router.post(
    "/verify",
    response_model=BotVerificationResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Bot not found"},
        400: {"model": ErrorResponse, "description": "Verification failed"},
    },
)
async def verify_bot(
    request: VerifyBotRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Verify bot credentials by initializing the bot.

    - **send_test_message**: Send a test message to verify bot works (optional)
    - **test_chat_id**: Chat ID to send test message to (required if send_test_message=true)
    """
    try:
        service = await create_user_bot_service(repository)

        # Validate test message parameters
        if request.send_test_message and not request.test_chat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="test_chat_id is required when send_test_message is true",
            )

        success, message, bot_info = await service.verify_bot_credentials(
            user_id=user_id,
            send_test_message=request.send_test_message,
            test_chat_id=request.test_chat_id,
            test_message=request.test_message,
        )

        if not success and "No bot found" in message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        return BotVerificationResponse(
            success=success,
            message=message,
            bot_info=bot_info,
            is_verified=success,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying bot for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify bot",
        )


@router.delete(
    "/remove",
    response_model=BotRemovedResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Bot not found"},
    },
)
async def remove_bot(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Remove the current user's bot.

    This will:
    - Shutdown the bot instance if active
    - Delete bot credentials from database
    - Remove all bot data
    """
    try:
        service = await create_user_bot_service(repository)
        success = await service.remove_user_bot(user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No bot found for this user",
            )

        return BotRemovedResponse(
            success=True,
            message="Bot removed successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing bot for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove bot",
        )


@router.put(
    "/rate-limits",
    response_model=RateLimitUpdateResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Bot not found"},
    },
)
async def update_rate_limits(
    request: UpdateRateLimitRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Update rate limits for the current user's bot.

    - **max_requests_per_second**: New RPS limit (1-100, optional)
    - **max_concurrent_requests**: New concurrent request limit (1-50, optional)
    """
    try:
        service = await create_user_bot_service(repository)

        credentials = await service.update_rate_limits(
            user_id=user_id,
            max_requests_per_second=request.max_requests_per_second,
            max_concurrent_requests=request.max_concurrent_requests,
        )

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No bot found for this user",
            )

        return RateLimitUpdateResponse(
            success=True,
            message="Rate limits updated successfully",
            new_limits={
                "max_requests_per_second": int(credentials.rate_limit_rps),
                "max_concurrent_requests": credentials.max_concurrent_requests,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rate limits for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update rate limits",
        )


@router.post(
    "/refresh-info",
    response_model=BotStatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Bot not found"},
        400: {"model": ErrorResponse, "description": "Failed to fetch bot info"},
    },
)
async def refresh_bot_info(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Refresh bot information (bot_id, username) from Telegram API.

    This is useful for bots created before bot_id field was added,
    or to update bot username if it changed.
    """
    try:
        from aiogram import Bot

        from core.services.encryption_service import get_encryption_service

        # Get existing credentials
        credentials = await repository.get_by_user_id(user_id)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No bot found for this user",
            )

        # Decrypt bot token
        encryption = get_encryption_service()
        decrypted_token = encryption.decrypt(credentials.bot_token)

        # Fetch fresh bot info from Telegram
        bot = Bot(token=decrypted_token)
        try:
            bot_me = await bot.get_me()

            # Update credentials with fresh data
            credentials.bot_id = bot_me.id
            credentials.bot_username = bot_me.username

            # Save updated credentials
            updated = await repository.update(credentials)

            logger.info(
                f"✅ Refreshed bot info for user {user_id}: bot_id={bot_me.id}, username={bot_me.username}"
            )

            return BotStatusResponse(
                id=updated.id,
                user_id=updated.user_id,
                bot_username=updated.bot_username,
                bot_id=updated.bot_id,
                status=updated.status,
                is_verified=updated.is_verified,
                max_requests_per_second=int(updated.rate_limit_rps),
                max_concurrent_requests=updated.max_concurrent_requests,
                total_requests=updated.total_requests,
                last_used_at=updated.last_used_at,
                created_at=updated.created_at,
                updated_at=updated.updated_at,
                suspension_reason=updated.suspension_reason,
            )

        finally:
            await bot.session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing bot info for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to refresh bot info: {str(e)}",
        )
