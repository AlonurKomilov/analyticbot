"""
Storage Channel Management Endpoints

Handles Telegram storage channel operations: list, validate, connect, disconnect.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.middleware.auth import get_current_user
from apps.api.services.telegram_storage_service import (
    ChannelNotFoundError,
    TelegramStorageError,
    TelegramStorageService,
)
from infra.db.models.telegram_storage import UserStorageChannel

from .deps import get_db_session
from .models import (
    ChannelValidationResponse,
    StorageChannelCreate,
    StorageChannelResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/channels", response_model=list[StorageChannelResponse], summary="Get user's storage channels"
)
async def get_storage_channels(
    only_active: bool = True,
    current_user: dict = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    """
    ## 📦 Get Storage Channels

    Retrieve all Telegram channels connected by the user for file storage.

    **Parameters:**
    - only_active: If true, only return active channels (default: true)

    **Returns:**
    - List of connected storage channels with status
    """
    user_id: int = current_user.get("id")  # type: ignore[assignment]
    logger.info(f"User {user_id} requested storage channels (active_only={only_active})")

    try:
        # Build query
        query = select(UserStorageChannel).where(UserStorageChannel.user_id == user_id)

        if only_active:
            query = query.where(UserStorageChannel.is_active.is_(True))

        query = query.order_by(UserStorageChannel.created_at.desc())

        # Execute query
        result = await db_session.execute(query)
        channels = result.scalars().all()

        # Convert to response models
        return [
            StorageChannelResponse(
                id=channel.id,
                user_id=channel.user_id,
                channel_id=channel.channel_id,
                channel_title=channel.channel_title,
                channel_username=channel.channel_username,
                is_active=channel.is_active,
                is_bot_admin=channel.is_bot_admin,
                created_at=channel.created_at.isoformat(),
                last_validated_at=channel.last_validated_at.isoformat()
                if channel.last_validated_at
                else None,
            )
            for channel in channels
        ]

    except Exception as e:
        logger.error(f"Failed to fetch storage channels for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch storage channels: {str(e)}",
        )


@router.post(
    "/channels/validate",
    response_model=ChannelValidationResponse,
    summary="Validate a Telegram channel for storage use",
)
async def validate_storage_channel(
    request: StorageChannelCreate,
    current_user: dict = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    """
    ## ✅ Validate Storage Channel

    Check if a Telegram channel can be used for file storage.

    **Checks performed:**
    - Channel exists and is accessible
    - Bot has admin rights in the channel
    - Bot has permission to post messages

    **Parameters:**
    - channel_id: Telegram channel ID (e.g., -1001234567890)
    - channel_username: Optional channel username

    **Returns:**
    - Validation result with channel details

    **Note:** Requires MTProto integration for full functionality.
    """
    # current_user is dict[str, Any], ensure user_id is int
    user_id_value = current_user.get("id")
    if not isinstance(user_id_value, int):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID in token"
        )
    user_id: int = user_id_value
    logger.info(f"User {user_id} validating channel: {request.channel_id}")

    try:
        # Get user's bot credentials (each user has their own bot)
        from apps.di import get_container

        container = get_container()
        user_bot_repo = await container.database.user_bot_repo()

        # Get user's bot credentials
        credentials = await user_bot_repo.get_by_user_id(user_id)

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No bot configured. Please configure your bot in Settings → Bot Configuration first.",
            )

        if not credentials.is_verified or credentials.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bot is not active (status: {credentials.status}). Please verify your bot configuration first.",
            )

        # Check if user has MTProto configured for Telethon access
        # Use TelegramStorageService factory (Clean Architecture)
        storage_service = await TelegramStorageService.create_for_user(
            user_id=user_id,
            db_session=db_session,
        )

        try:
            # Validate the channel using user's Telegram session
            channel_info = await storage_service.validate_storage_channel(
                user_id=user_id,
                channel_id=request.channel_id,
                channel_username=request.channel_username,
            )

            return ChannelValidationResponse(
                is_valid=channel_info["is_valid"],
                channel_id=channel_info["id"],
                channel_title=channel_info["title"],
                channel_username=channel_info.get("username"),
                member_count=channel_info.get("member_count", 0),
                bot_is_admin=channel_info.get("bot_is_admin", False),
                message="Channel validation successful! You can now connect this channel for storage.",
            )
        finally:
            # Clean up Telethon client
            if storage_service.client.is_connected():
                await storage_service.client.disconnect()

    except ChannelNotFoundError as e:
        logger.warning(f"Channel not found for user {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except TelegramStorageError as e:
        logger.warning(f"Channel validation failed for user {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.error(f"Error validating channel for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate channel: {str(e)}",
        )


@router.post(
    "/channels/connect",
    response_model=StorageChannelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Connect a Telegram channel for storage",
)
async def connect_storage_channel(
    request: StorageChannelCreate,
    current_user: dict = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    """
    ## 🔗 Connect Storage Channel

    Connect a Telegram channel to use for file storage.

    **Requirements:**
    1. Channel must be private (owned by user)
    2. Bot must be added as admin
    3. Bot needs "Post Messages" permission

    **Parameters:**
    - channel_id: Telegram channel ID
    - channel_username: Optional channel username

    **Returns:**
    - Connected channel information
    """
    user_id: int = current_user.get("id")  # type: ignore[assignment]
    logger.info(f"User {user_id} connecting storage channel: {request.channel_id}")

    try:
        # Use TelegramStorageService factory (Clean Architecture)
        storage_service = await TelegramStorageService.create_for_user(
            user_id=user_id,
            db_session=db_session,
        )

        # Validate the channel
        validation_result = await storage_service.validate_storage_channel(
            user_id=user_id,
            channel_id=request.channel_id,
            channel_username=request.channel_username,
        )

        if not validation_result.get("is_valid", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_result.get("error_message", "Channel validation failed"),
            )

        # Connect the channel (save to database)
        result = await storage_service.connect_storage_channel(
            user_id=user_id,
            channel_id=request.channel_id,
            channel_title=validation_result.get("title", ""),
            channel_username=request.channel_username,
            is_bot_admin=validation_result.get("bot_is_admin", False),
        )

        # Return the connected channel info
        return StorageChannelResponse(
            id=result.id,
            user_id=result.user_id,
            channel_id=result.channel_id,
            channel_title=result.channel_title,
            channel_username=result.channel_username,
            is_active=result.is_active,
            is_bot_admin=result.is_bot_admin,
            created_at=result.created_at.isoformat()
            if result.created_at
            else datetime.utcnow().isoformat(),
            last_validated_at=result.last_validated_at.isoformat()
            if result.last_validated_at
            else datetime.utcnow().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to connect storage channel: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect storage channel: {str(e)}",
        )


@router.delete(
    "/channels/{channel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disconnect a storage channel",
)
async def disconnect_storage_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🔌 Disconnect Storage Channel

    Disconnect a storage channel (marks as inactive).

    **Parameters:**
    - channel_id: Database ID of the channel to disconnect

    **Note:**
    - Files remain in the channel
    - Channel can be reconnected later
    - No files are deleted from Telegram
    """
    logger.info(f"User {current_user.get('id')} disconnecting channel: {channel_id}")

    # TODO: Mark channel as inactive in database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Channel disconnection requires database integration. Feature coming soon!",
    )
