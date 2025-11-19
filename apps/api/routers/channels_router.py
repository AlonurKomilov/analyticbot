"""
Channels Microrouter - Pure Channel Management

This microrouter handles ONLY channel management operations (CRUD).
Domain: Channel creation, reading, updating, deletion, and basic channel operations.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from apps.api.middleware.auth import (
    get_current_user,
    require_channel_access,
)
from apps.api.services.channel_management_service import (
    ChannelCreate,
    ChannelManagementService,
    ChannelResponse,
)
from apps.api.services.telegram_validation_service import (
    ChannelValidationResult,
    TelegramValidationService,
)
from apps.di.analytics_container import get_channel_management_service
from apps.shared.performance import performance_timer

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/channels", tags=["Channel Management"], responses={404: {"description": "Not found"}}
)

# === CHANNEL MODELS ===


class ChannelListResponse(BaseModel):
    id: int
    name: str
    username: str | None = None
    subscriber_count: int = 0
    is_active: bool = True
    created_at: datetime
    last_updated: datetime
    bot_is_admin: bool | None = None  # Bot admin status
    mtproto_is_admin: bool | None = None  # MTProto admin status
    admin_status_message: str | None = None  # Helpful message for users


class ChannelUpdateRequest(BaseModel):
    name: str | None = None
    username: str | None = None
    is_active: bool | None = None
    settings: dict[str, Any] | None = None


class ValidateChannelRequest(BaseModel):
    """Request model for channel validation"""

    username: str


# === CHANNEL ENDPOINTS ===


async def get_telegram_validation_service_dep():
    """Dependency to get telegram validation service"""
    from apps.di.analytics_container import get_telegram_validation_service as di_get_service

    return await di_get_service()


@router.get("/admin-status/check-all")
async def check_all_channels_admin_status(
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 🔍 Check Admin Status for All Channels

    Verifies bot/MTProto admin status for all user's channels using their own credentials.
    This prevents starting heavy sessions if admin access is not configured.

    **Returns:**
    - Dictionary mapping channel_id to admin status
    - Saves server resources by checking before starting sessions

    **Uses multi-tenant bot/MTProto system**: Each user's own credentials are used for verification.
    """
    try:
        logger.info(f"Checking admin status for all channels of user {current_user.get('id')}")

        # Get user's channels
        channels = await channel_service.get_user_channels(user_id=current_user["id"])

        if not channels:
            return {
                "status": "success",
                "channels_checked": 0,
                "results": {},
                "note": "No channels found for this user.",
            }

        # Get user's bot and MTProto credentials
        from apps.di import get_container, get_user_mtproto_service

        container = get_container()
        user_bot_repo = await container.database.user_bot_repo()
        user_credentials = await user_bot_repo.get_by_user_id(current_user["id"])

        # Get MTProto service for this user
        mtproto_service = await get_user_mtproto_service()

        status_results = {}

        # Check each channel
        for channel in channels:
            bot_is_admin = None
            mtproto_is_admin = None
            message = "Checking admin status..."

            # Prepare channel identifiers for different APIs
            # 1. Username format (if available) - works for both Bot API and MTProto
            channel_username = None
            if channel.name and channel.name.startswith("@"):
                channel_username = channel.name
            elif channel.name and not channel.name.replace(" ", "").isdigit():
                # Name looks like a username, format it
                channel_username = f"@{channel.name.lower().replace(' ', '')}"

            # 2. Telegram ID - needs conversion for Bot API (requires -100 prefix)
            # Bot API format: -100 + channel_id (for channels/supergroups)
            bot_api_chat_id = None
            if channel.telegram_id:
                # If ID is positive, convert to Bot API format
                if channel.telegram_id > 0:
                    bot_api_chat_id = int(f"-100{channel.telegram_id}")
                else:
                    bot_api_chat_id = channel.telegram_id

            # Check bot admin status (if user has configured a bot)
            if user_credentials and user_credentials.bot_token:
                try:
                    from aiogram import Bot
                    from aiogram.enums import ChatMemberStatus

                    from core.services.encryption_service import get_encryption_service

                    # Decrypt bot token
                    encryption = get_encryption_service()
                    decrypted_token = encryption.decrypt(user_credentials.bot_token)

                    # Create temporary bot instance
                    bot = Bot(token=decrypted_token)

                    try:
                        # Get bot ID (use cached bot_id or fetch it)
                        bot_user_id = user_credentials.bot_id
                        if not bot_user_id:
                            bot_me = await bot.get_me()
                            bot_user_id = bot_me.id

                        # Try multiple methods to check bot admin status
                        chat_member = None
                        last_error = None

                        # Method 1: Try with username (most reliable if available)
                        if channel_username:
                            try:
                                chat_member = await bot.get_chat_member(
                                    chat_id=channel_username, user_id=bot_user_id
                                )
                                logger.debug(
                                    f"✓ Bot admin check via username {channel_username} succeeded"
                                )
                            except Exception as e:
                                last_error = str(e)
                                logger.debug(f"Method 1 (username {channel_username}) failed: {e}")

                        # Method 2: Try with Bot API formatted ID
                        if not chat_member and bot_api_chat_id:
                            try:
                                chat_member = await bot.get_chat_member(
                                    chat_id=bot_api_chat_id, user_id=bot_user_id
                                )
                                logger.debug(
                                    f"✓ Bot admin check via ID {bot_api_chat_id} succeeded"
                                )
                            except Exception as e:
                                last_error = str(e)
                                logger.debug(f"Method 2 (ID {bot_api_chat_id}) failed: {e}")

                        if chat_member:
                            # Check if bot is admin or creator
                            bot_is_admin = chat_member.status in [
                                ChatMemberStatus.ADMINISTRATOR,
                                ChatMemberStatus.CREATOR,
                            ]

                            if bot_is_admin:
                                logger.info(
                                    f"✅ User {current_user['id']} bot is admin of channel {channel.id}"
                                )
                            else:
                                logger.warning(
                                    f"❌ User {current_user['id']} bot is NOT admin (status: {chat_member.status})"
                                )
                        else:
                            # All methods failed
                            bot_is_admin = False
                            logger.warning(
                                f"Failed to check bot admin for channel {channel.id}: {last_error}"
                            )

                    finally:
                        # Always close bot session
                        await bot.session.close()

                except Exception as e:
                    logger.error(f"Error checking bot admin for channel {channel.id}: {e}")
                    bot_is_admin = False

            # Check MTProto admin status (if user has configured MTProto)
            if (
                user_credentials
                and user_credentials.mtproto_enabled
                and user_credentials.session_string
            ):
                try:
                    # Get user's MTProto client
                    mtproto_client = await mtproto_service.get_user_client(
                        user_id=current_user["id"], channel_id=channel.id
                    )

                    if mtproto_client:
                        # Use the client to check admin status
                        # Import MTProto dependencies only when needed (guard pattern)
                        try:
                            from telethon.tl.functions.channels import (
                                GetParticipantRequest,
                            )
                        except ImportError:
                            logger.warning(
                                "MTProto library (telethon) not available for admin check"
                            )
                            mtproto_is_admin = False
                        else:
                            # Import succeeded, proceed with MTProto admin check
                            try:
                                # MTProto get_entity() handles multiple formats:
                                # - @username
                                # - Numeric ID (positive integer)
                                # - PeerChannel object

                                entity = None
                                last_error = None

                                # Method 1: Try with username first (most reliable)
                                if channel_username:
                                    try:
                                        entity = await mtproto_client.client.get_entity(
                                            channel_username
                                        )
                                        logger.debug(
                                            f"✓ MTProto get_entity via username {channel_username} succeeded"
                                        )
                                    except Exception as e:
                                        last_error = str(e)
                                        logger.debug(f"MTProto username method failed: {e}")

                                # Method 2: Try with raw telegram_id (Telethon handles conversion)
                                if not entity and channel.telegram_id:
                                    try:
                                        entity = await mtproto_client.client.get_entity(
                                            channel.telegram_id
                                        )
                                        logger.debug(
                                            f"✓ MTProto get_entity via ID {channel.telegram_id} succeeded"
                                        )
                                    except Exception as e:
                                        last_error = str(e)
                                        logger.debug(f"MTProto ID method failed: {e}")

                                if entity:
                                    # Get current user (MTProto session user)
                                    me = await mtproto_client.client.get_me()

                                    # Check participant status
                                    participant = await mtproto_client.client(
                                        GetParticipantRequest(channel=entity, participant=me)
                                    )

                                    # Check if admin or creator
                                    participant_type = type(participant.participant).__name__
                                    mtproto_is_admin = participant_type in [
                                        "ChannelParticipantAdmin",
                                        "ChannelParticipantCreator",
                                    ]

                                    if mtproto_is_admin:
                                        logger.info(
                                            f"✅ User {current_user['id']} MTProto is admin of channel {channel.id}"
                                        )
                                    else:
                                        logger.warning(
                                            f"❌ User {current_user['id']} MTProto is NOT admin of channel {channel.id}"
                                        )
                                else:
                                    # Could not get entity
                                    mtproto_is_admin = False
                                    logger.warning(f"Failed to get channel entity: {last_error}")

                            except Exception as e:
                                logger.warning(
                                    f"Failed to check MTProto admin for channel {channel.id}: {e}"
                                )
                                mtproto_is_admin = False
                    else:
                        logger.info(f"No MTProto client available for user {current_user['id']}")
                        mtproto_is_admin = None

                except Exception as e:
                    logger.error(f"Error getting MTProto client for user {current_user['id']}: {e}")
                    mtproto_is_admin = None

            # Determine message based on status
            # null = not configured, false = configured but not admin, true = admin
            if bot_is_admin is None and mtproto_is_admin is None:
                # User hasn't configured bot OR MTProto
                message = "⚠️ Setup required: Configure your bot or MTProto session to enable data collection"
            elif bot_is_admin is True and mtproto_is_admin is True:
                # Both are configured and both have admin access
                message = "✅ Both bot and MTProto have admin access - full data collection enabled"
            elif bot_is_admin is False and mtproto_is_admin is False:
                # Both are configured but neither has admin access
                message = "🚫 Access denied: Add your bot or MTProto as admin to this channel"
            elif bot_is_admin is True or mtproto_is_admin is True:
                # One has admin, the other either doesn't or is not configured
                if bot_is_admin is True:
                    message = "✓ Bot has admin access" + (
                        " - MTProto not configured"
                        if mtproto_is_admin is None
                        else " - MTProto needs admin access"
                    )
                else:
                    message = "✓ MTProto has admin access" + (
                        " - Bot not configured"
                        if bot_is_admin is None
                        else " - Bot needs admin access"
                    )
            elif bot_is_admin is False or mtproto_is_admin is False:
                # At least one is explicitly false (configured but not admin)
                # The other is either null (not configured) or also false
                if bot_is_admin is False and mtproto_is_admin is None:
                    message = "⚠️ Bot has no admin access - Configure MTProto or add bot as admin"
                elif mtproto_is_admin is False and bot_is_admin is None:
                    message = (
                        "⚠️ MTProto has no admin access - Configure bot or add MTProto as admin"
                    )
                else:
                    message = "⚠️ Admin verification pending"
            else:
                message = "⏳ Verifying admin status..."

            status_results[channel.id] = {
                "channel_id": channel.id,
                "channel_name": channel.name,
                "bot_is_admin": bot_is_admin,
                "mtproto_is_admin": mtproto_is_admin,
                "can_collect_data": bool(bot_is_admin or mtproto_is_admin),
                "is_inactive": bot_is_admin is False
                and mtproto_is_admin is False,  # Both red = gray out card
                "message": message,
            }

        logger.info(f"Admin status checked for {len(status_results)} channels")
        return {
            "status": "success",
            "channels_checked": len(status_results),
            "results": status_results,
            "note": "Using your personal bot/MTProto credentials for verification.",
        }

    except Exception as e:
        logger.error(f"Failed to check admin status: {e}", exc_info=True)
        # Return graceful fallback instead of 500 error
        return {
            "status": "partial",
            "channels_checked": 0,
            "results": {},
            "error": str(e),
            "note": "Unable to verify admin status at this time. Your channels will work normally.",
        }


@router.post("/validate", response_model=ChannelValidationResult)
async def validate_telegram_channel(
    request_data: ValidateChannelRequest,
    current_user: dict = Depends(get_current_user),
    telegram_service: TelegramValidationService = Depends(get_telegram_validation_service_dep),
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

    **Example Response:**
    ```json
    {
        "is_valid": true,
        "telegram_id": 1234567890,
        "username": "channelname",
        "title": "My Channel",
        "subscriber_count": 1000,
        "description": "Channel description",
        "is_verified": false,
        "is_scam": false,
        "is_admin": true
    }
    ```
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
                f"User {current_user.get('id')}'s bot/MTProto session is not admin of @{request_data.username}"
            )
        else:
            logger.info(
                f"✅ User {current_user.get('id')}'s bot/MTProto verified as admin of @{request_data.username}"
            )

        return result

    except Exception as e:
        logger.error(f"Failed to validate channel: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("", response_model=list[ChannelListResponse])
async def get_user_channels(
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 📺 Get User Channels

    Retrieve all channels accessible by the current user.

    **Returns:**
    - List of user's channels with basic information
    """
    try:
        logger.info(f"Fetching channels for user {current_user.get('id')}")
        with performance_timer("user_channels_fetch"):
            channels = await channel_service.get_user_channels(user_id=current_user["id"])
            logger.info(f"Successfully fetched {len(channels)} channels")

            return [
                ChannelListResponse(
                    id=channel.id,
                    name=channel.name,
                    username=getattr(channel, "username", None),
                    subscriber_count=channel.subscriber_count,
                    is_active=channel.is_active,
                    created_at=channel.created_at,
                    last_updated=getattr(channel, "updated_at", channel.created_at),
                )
                for channel in channels
            ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"User channels fetch failed for user {current_user.get('id')}: {e}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Failed to fetch user channels: {str(e)}")


@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: ChannelCreate,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
    telegram_service: TelegramValidationService = Depends(get_telegram_validation_service_dep),
):
    """
    ## ➕ Create New Channel

    Create a new channel for analytics tracking.

    **🔒 SECURITY: Bot/MTProto Admin Verification Required**
    - Your bot or MTProto session must be an admin of the Telegram channel
    - System verifies admin status before allowing channel creation
    - Prevents unauthorized access to other users' channels
    - Works for all login methods (email/telegram)

    **Steps to add a channel:**
    1. Make sure you are an admin/owner of the channel in Telegram
    2. Add your bot as an admin to the channel (if using bot), OR
    3. Connect your MTProto session (if using personal account)
    4. Try adding the channel - system will verify your bot/MTProto is admin

    **Parameters:**
    - channel_data: Channel creation data (name, username, etc.)

    **Returns:**
    - Created channel information

    **Error Cases:**
    - 403: Your bot/MTProto session is not an admin of this channel
    - 500: Channel creation failed
    """
    try:
        with performance_timer("channel_create"):
            # SECURITY CHECK: Verify user's bot/MTProto session has admin access to this channel
            # This prevents users from adding channels they don't own

            # Verify admin access using channel username or name
            channel_username = channel_data.name
            if not channel_username.startswith("@"):
                channel_username = f"@{channel_username}"

            is_admin, error_msg = await telegram_service.check_bot_admin_access(channel_username)

            if not is_admin:
                logger.warning(
                    f"🚫 User {current_user['id']} attempted to add channel {channel_username} "
                    f"without bot/MTProto admin access"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_msg
                    or (
                        "⛔ Access Denied: Your bot or MTProto session must be an admin of this channel. "
                        "Please:\n"
                        "1. Make sure you are an admin/owner of the Telegram channel\n"
                        "2. Add your bot to the channel as an admin with necessary permissions, OR\n"
                        "3. Connect your MTProto session and ensure it has admin access"
                    ),
                )

            # User's bot/MTProto is verified as admin, proceed with channel creation
            channel_data.user_id = current_user["id"]
            channel = await channel_service.create_channel(channel_data)

            logger.info(
                f"✅ Channel created successfully: {channel.id} by user {current_user['id']} "
                f"(bot/MTProto admin verified)"
            )
            return channel

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel creation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create channel")


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 📺 Get Channel Details

    Retrieve detailed information about a specific channel.

    **Parameters:**
    - channel_id: Target channel ID

    **Returns:**
    - Detailed channel information
    """
    try:
        # Verify channel access
        await require_channel_access(channel_id, current_user["id"])

        with performance_timer("channel_details_fetch"):
            channel = await channel_service.get_channel(channel_id)

            if not channel:
                raise HTTPException(status_code=404, detail="Channel not found")

            return channel

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel details fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch channel details")


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    update_data: ChannelUpdateRequest,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## ✏️ Update Channel

    Update channel information and settings.

    **Parameters:**
    - channel_id: Target channel ID
    - update_data: Channel update data

    **Returns:**
    - Updated channel information
    """
    try:
        # Verify user has access to this channel
        await require_channel_access(channel_id, current_user["id"])

        with performance_timer("channel_update"):
            # Filter out None values
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}

            if not update_dict:
                raise HTTPException(status_code=400, detail="No update data provided")

            channel = await channel_service.update_channel(
                channel_id=channel_id, user_id=current_user["id"], update_data=update_dict
            )

            logger.info(f"Channel updated successfully: {channel_id} by user {current_user['id']}")
            return channel

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

    Delete a channel and all associated analytics data.

    **Parameters:**
    - channel_id: Target channel ID

    **Returns:**
    - Deletion confirmation
    """
    try:
        # Verify user has access to this channel
        await require_channel_access(channel_id, current_user["id"])

        with performance_timer("channel_deletion"):
            result = await channel_service.delete_channel(channel_id)

            if not result:
                raise HTTPException(status_code=404, detail="Channel not found or already deleted")

            logger.info(
                f"Channel deleted successfully: {channel_id} by user {current_user['id']}, "
                f"result: {result}"
            )
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


@router.post("/{channel_id}/activate")
async def activate_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## ✅ Activate Channel

    Activate a channel for analytics tracking.

    **Parameters:**
    - channel_id: Target channel ID

    **Returns:**
    - Activation confirmation
    """
    try:
        await require_channel_access(channel_id, current_user["id"])

        with performance_timer("channel_activation"):
            await channel_service.update_channel(
                channel_id=channel_id, user_id=current_user["id"], update_data={"is_active": True}
            )

        logger.info(f"Channel activated successfully: {channel_id} by user {current_user['id']}")
        return {
            "message": "Channel activated successfully",
            "channel_id": channel_id,
            "is_active": True,
            "activated_at": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel activation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to activate channel")


@router.post("/{channel_id}/deactivate")
async def deactivate_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## ❌ Deactivate Channel

    Deactivate a channel to stop analytics tracking.

    **Parameters:**
    - channel_id: Target channel ID

    **Returns:**
    - Deactivation confirmation
    """
    try:
        await require_channel_access(channel_id, current_user["id"])

        with performance_timer("channel_deactivation"):
            await channel_service.update_channel(
                channel_id=channel_id, user_id=current_user["id"], update_data={"is_active": False}
            )

        logger.info(f"Channel deactivated successfully: {channel_id} by user {current_user['id']}")
        return {
            "message": "Channel deactivated successfully",
            "channel_id": channel_id,
            "is_active": False,
            "deactivated_at": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel deactivation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate channel")


@router.get("/{channel_id}/status")
async def get_channel_status(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 📊 Get Channel Status

    Get the current status and basic statistics of a channel.

    **Parameters:**
    - channel_id: Target channel ID

    **Returns:**
    - Channel status information
    """
    try:
        await require_channel_access(channel_id, current_user["id"])

        with performance_timer("channel_status_fetch"):
            status_info = await channel_service.get_channel_status(channel_id)

            return {
                "channel_id": channel_id,
                "is_active": status_info.get("is_active", False),
                "last_update": status_info.get("last_update"),
                "subscriber_count": status_info.get("subscriber_count", 0),
                "total_posts": status_info.get("total_posts", 0),
                "analytics_enabled": status_info.get("analytics_enabled", False),
                "connection_status": status_info.get("connection_status", "unknown"),
                "last_sync": status_info.get("last_sync"),
                "checked_at": datetime.now().isoformat(),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel status fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch channel status")


@router.get("/statistics/overview")
async def get_channels_statistics_overview(
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 📊 Get Channels Statistics Overview

    Get aggregate statistics for all user's channels plus individual channel stats.

    **Returns:**
    - Aggregate statistics (total subscribers, posts, views across all channels)
    - Per-channel statistics with detailed metrics
    """
    try:
        user_id = current_user["id"]

        with performance_timer("channels_statistics_overview"):
            # Get user's channels
            channels = await channel_service.get_user_channels(user_id=user_id)

            if not channels:
                return {
                    "aggregate": {
                        "total_channels": 0,
                        "total_subscribers": 0,
                        "total_posts": 0,
                        "total_views": 0,
                        "active_channels": 0,
                    },
                    "channels": [],
                }

            # Get database pool for stats queries
            from apps.di import get_container

            container = get_container()
            pool = await container.database.asyncpg_pool()

            channel_stats_list = []
            total_subscribers = 0
            total_posts = 0
            total_views = 0
            active_channels = 0

            async with pool.acquire() as conn:
                for channel in channels:
                    # Get post count and views for this channel
                    stats = await conn.fetchrow(
                        """
                        SELECT
                            COUNT(DISTINCT p.msg_id) as post_count,
                            COALESCE(SUM(latest_metrics.views), 0)::bigint as total_views,
                            MAX(p.date) as latest_post_date
                        FROM posts p
                        LEFT JOIN LATERAL (
                            SELECT views
                            FROM post_metrics
                            WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                            ORDER BY snapshot_time DESC
                            LIMIT 1
                        ) latest_metrics ON true
                        WHERE p.channel_id = $1 AND p.is_deleted = FALSE
                        """,
                        channel.id,
                    )

                    post_count = stats["post_count"] or 0
                    views_count = stats["total_views"] or 0
                    latest_post = stats["latest_post_date"]

                    # Count as active if has posts
                    if channel.is_active and post_count > 0:
                        active_channels += 1

                    # Aggregate totals
                    total_subscribers += channel.subscriber_count
                    total_posts += post_count
                    total_views += views_count

                    # Add to per-channel stats
                    channel_stats_list.append(
                        {
                            "id": channel.id,
                            "name": channel.name,
                            "username": getattr(channel, "username", None),
                            "subscriber_count": channel.subscriber_count,
                            "post_count": post_count,
                            "total_views": views_count,
                            "avg_views_per_post": round(views_count / post_count)
                            if post_count > 0
                            else 0,
                            "latest_post_date": latest_post.isoformat() if latest_post else None,
                            "is_active": channel.is_active,
                            "created_at": channel.created_at.isoformat(),
                        }
                    )

            return {
                "aggregate": {
                    "total_channels": len(channels),
                    "total_subscribers": total_subscribers,
                    "total_posts": total_posts,
                    "total_views": total_views,
                    "active_channels": active_channels,
                    "avg_views_per_post": round(total_views / total_posts)
                    if total_posts > 0
                    else 0,
                },
                "channels": sorted(
                    channel_stats_list, key=lambda x: x["total_views"], reverse=True
                ),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel statistics overview failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch channel statistics")


# End of channels router - analytics endpoints moved to analytics_insights_router.py
