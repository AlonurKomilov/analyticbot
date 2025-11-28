"""
CRUD operations for channel management.

Handles: Get user channels list, create channel, get single channel, update channel, delete channel.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

logger = logging.getLogger(__name__)

from apps.api.middleware.auth import get_current_user, require_channel_access
from apps.api.routers.channels.deps import (
    get_channel_management_service,
    get_telegram_validation_service,
)
from apps.api.routers.channels.models import (
    ChannelCreateRequest,
    ChannelListResponse,
    ChannelResponse,
    ChannelUpdateRequest,
)
from apps.api.services.channel_management_service import ChannelManagementService
from apps.api.services.telegram_validation_service import TelegramValidationService
from apps.shared.performance import performance_timer

router = APIRouter()


@router.get("/", response_model=list[ChannelListResponse])
async def get_user_channels(
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 📋 Get User Channels

    Retrieve all channels associated with the authenticated user.

    **Returns:**
    - List of channels with basic information
    """
    try:
        with performance_timer("get_user_channels"):
            channels = await channel_service.get_user_channels(user_id=current_user["id"])

        logger.info(f"Retrieved {len(channels)} channels for user {current_user['id']}")
        return channels

    except Exception as e:
        logger.error(f"Failed to retrieve user channels: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve channels")


@router.post("/", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: ChannelCreateRequest,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
    telegram_service: TelegramValidationService | None = Depends(get_telegram_validation_service),
):
    """
    ## ➕ Create Channel

    Add a new Telegram channel for analytics tracking.

    **Security Requirements:**
    - User must have bot admin access OR MTProto admin access to the channel
    - Raises 403 Forbidden if user lacks admin privileges
    - If Telegram validation is unavailable, channel can be added without validation

    **Parameters:**
    - channel_data: Channel creation details (name, username, etc.)

    **Returns:**
    - Created channel object
    """
    try:
        # Security check: Verify bot has admin access to the channel
        channel_username = channel_data.username or channel_data.name

        # Check if Telegram validation service is available
        if telegram_service is None:
            logger.warning(
                f"Telegram validation unavailable - allowing channel creation without admin check for: {channel_username}"
            )
            # Proceed without validation - channel will be created but may not have full access
        else:
            # Check if bot is admin (or user has MTProto admin access)
            is_admin, error_msg = await telegram_service.check_bot_admin_access(channel_username)

            if not is_admin:
                logger.warning(
                    f"User {current_user['id']} attempted to add channel without admin access: {channel_username}"
                )
                # Provide clear, actionable error message
                detail_msg = error_msg or (
                    "To add this channel, please follow these steps:\n"
                    "1. Open your Telegram channel settings\n"
                    "2. Go to 'Administrators'\n"
                    "3. Add your bot (@YourBotUsername) as an administrator\n"
                    "4. Grant permissions: 'Post messages' and 'Edit messages'\n"
                    "5. Try adding the channel again"
                )
                raise HTTPException(
                    status_code=403,
                    detail=detail_msg,
                )

        with performance_timer("create_channel"):
            # Set user_id on the channel data
            channel_data_dict = channel_data.dict()
            channel_data_dict["user_id"] = current_user["id"]

            # Ensure telegram_id is set (use random fallback if not provided)
            if not channel_data_dict.get("telegram_id"):
                import random

                channel_data_dict["telegram_id"] = random.randint(1000000000, 9999999999)
                logger.warning(
                    f"No telegram_id provided, using fallback: {channel_data_dict['telegram_id']}"
                )

            # Filter to only fields expected by ChannelCreate
            from apps.api.services.channel_management_service import ChannelCreate

            valid_fields = {"name", "telegram_id", "username", "description", "user_id"}
            filtered_data = {k: v for k, v in channel_data_dict.items() if k in valid_fields}

            channel_create = ChannelCreate(**filtered_data)
            new_channel = await channel_service.create_channel(channel_create)

        logger.info(f"Channel created successfully: {new_channel.id} by user {current_user['id']}")
        return new_channel

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create channel")


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 🔍 Get Channel Details

    Retrieve detailed information about a specific channel.

    **Parameters:**
    - channel_id: Target channel ID

    **Returns:**
    - Channel object with full details
    """
    try:
        await require_channel_access(channel_id, current_user["id"])

        with performance_timer("get_channel_details"):
            channel = await channel_service.get_channel(channel_id)

        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")

        logger.info(f"Channel details retrieved: {channel_id} by user {current_user['id']}")
        return channel

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve channel")


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    update_data: ChannelUpdateRequest,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## ✏️ Update Channel

    Update channel information.

    **Parameters:**
    - channel_id: Target channel ID
    - update_data: Fields to update (only non-null fields are updated)

    **Returns:**
    - Updated channel object
    """
    try:
        await require_channel_access(channel_id, current_user["id"])

        # Filter out None values
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}

        if not update_dict:
            raise HTTPException(status_code=400, detail="No valid fields provided for update")

        with performance_timer("update_channel"):
            updated_channel = await channel_service.update_channel(
                channel_id=channel_id,
                user_id=current_user["id"],
                update_data=update_dict,
            )

        if not updated_channel:
            raise HTTPException(status_code=404, detail="Channel not found")

        logger.info(f"Channel updated successfully: {channel_id} by user {current_user['id']}")
        return updated_channel

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel update failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to update channel")


@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 🗑️ Delete Channel

    Soft delete a channel (marks as deleted, preserves data).

    **Parameters:**
    - channel_id: Target channel ID

    **Returns:**
    - Deletion confirmation
    """
    try:
        await require_channel_access(channel_id, current_user["id"])

        with performance_timer("delete_channel"):
            await channel_service.delete_channel(channel_id=channel_id)

        logger.info(f"Channel deleted successfully: {channel_id} by user {current_user['id']}")
        return {
            "message": "Channel deleted successfully",
            "channel_id": channel_id,
            "deleted_at": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete channel")
