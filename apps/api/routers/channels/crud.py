"""
CRUD operations for channel management.

Handles: Get user channels list, create channel, get single channel, update channel, delete channel.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

logger = logging.getLogger(__name__)

from apps.api.middleware.auth import get_current_user, require_channel_access
from apps.api.routers.analytics_channels_router import invalidate_user_channel_cache
from apps.api.routers.channels.deps import (
    get_channel_management_service,
    get_telegram_validation_service,
)
from apps.api.routers.channels.models import (
    AddChannelRequest,
    ChannelListResponse,
    ChannelLookupResponse,
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


@router.get("/lookup/{username}", response_model=ChannelLookupResponse)
async def lookup_channel(
    username: str,
    current_user: dict = Depends(get_current_user),
    telegram_service: TelegramValidationService | None = Depends(get_telegram_validation_service),
):
    """
    ## 🔍 Lookup Channel Info

    Lookup a Telegram channel by username and fetch all metadata automatically.
    Use this before adding a channel to preview what will be added.

    Uses the **user's own bot/MTProto credentials** to check admin access.

    **Parameters:**
    - username: Channel username (with or without @)

    **Returns:**
    - Channel info including name, subscribers, description, etc.
    """
    try:
        if telegram_service is None:
            logger.warning("Telegram validation unavailable for channel lookup")
            return ChannelLookupResponse(
                is_valid=False,
                username=username,
                error_message="Telegram service unavailable. Please try again later.",
            )

        # Validate and fetch channel info using system bot (for public channel info)
        validation_result = await telegram_service.validate_channel_by_username(username)

        # Check admin access using USER'S OWN BOT credentials
        is_admin = None
        admin_error = None
        if validation_result.is_valid and validation_result.telegram_id:
            user_id = current_user["id"]

            # Try to check admin using user's bot first, then MTProto
            is_admin, admin_error = await _check_user_admin_access(
                user_id=user_id,
                channel_id=validation_result.telegram_id,
                channel_username=validation_result.username or username,
            )

            if is_admin:
                admin_error = None  # Clear any previous error if admin access confirmed

        # Convert telegram_id to proper format with 100 prefix
        formatted_telegram_id = validation_result.telegram_id
        if formatted_telegram_id:
            raw_id = abs(formatted_telegram_id)
            id_str = str(raw_id)
            if not id_str.startswith("100"):
                formatted_telegram_id = int(f"100{raw_id}")

        return ChannelLookupResponse(
            is_valid=validation_result.is_valid,
            telegram_id=formatted_telegram_id,
            username=validation_result.username,
            title=validation_result.title,
            subscriber_count=validation_result.subscriber_count,
            description=validation_result.description,
            telegram_created_at=validation_result.telegram_created_at,
            is_verified=validation_result.is_verified,
            is_scam=validation_result.is_scam,
            is_admin=is_admin,
            error_message=validation_result.error_message
            or (admin_error if not is_admin else None),
        )

    except Exception as e:
        logger.error(f"Channel lookup failed for @{username}: {e}")
        return ChannelLookupResponse(
            is_valid=False,
            username=username,
            error_message=f"Lookup failed: {str(e)}",
        )


async def _check_user_admin_access(
    user_id: int,
    channel_id: int,
    channel_username: str,
) -> tuple[bool, str | None]:
    """
    Check if user's own bot or MTProto account is admin in the channel.

    This checks the user's credentials from user_bot_credentials table,
    NOT the system bot from environment.
    """
    from apps.di import get_container

    try:
        container = get_container()
        pool = await container.database.asyncpg_pool()

        # Get user's bot credentials
        async with pool.acquire() as conn:
            creds = await conn.fetchrow(
                """
                SELECT bot_token, bot_username, telegram_api_id, telegram_api_hash, 
                       session_string, mtproto_enabled, is_verified
                FROM user_bot_credentials
                WHERE user_id = $1 AND is_verified = true
                """,
                user_id,
            )

        if not creds:
            return (
                False,
                "No verified bot credentials found. Please set up your bot in Settings.",
            )

        # Try checking with user's bot first
        bot_token = creds["bot_token"]
        if bot_token:
            try:
                # Decrypt bot token if encrypted
                from core.services.encryption_service import get_encryption_service

                encryption = get_encryption_service()
                try:
                    decrypted_token = encryption.decrypt(bot_token)
                except Exception:
                    decrypted_token = bot_token  # May not be encrypted

                is_admin = await _check_bot_admin_via_api(decrypted_token, channel_id)
                if is_admin:
                    logger.info(f"User {user_id}'s bot is admin in channel {channel_id}")
                    return True, None
            except Exception as e:
                logger.warning(f"Bot admin check failed: {e}")

        # Try MTProto if enabled and session exists
        if creds["mtproto_enabled"] and creds["session_string"]:
            try:
                # Decrypt MTProto credentials
                from core.services.encryption_service import get_encryption_service

                encryption = get_encryption_service()
                try:
                    decrypted_api_hash = (
                        encryption.decrypt(creds["telegram_api_hash"])
                        if creds["telegram_api_hash"]
                        else None
                    )
                    decrypted_session = (
                        encryption.decrypt(creds["session_string"])
                        if creds["session_string"]
                        else None
                    )
                except Exception as decrypt_err:
                    logger.warning(f"Failed to decrypt MTProto credentials: {decrypt_err}")
                    decrypted_api_hash = creds["telegram_api_hash"]
                    decrypted_session = creds["session_string"]

                is_admin = await _check_mtproto_admin(
                    api_id=creds["telegram_api_id"],
                    api_hash=decrypted_api_hash,
                    session_string=decrypted_session,
                    channel_username=channel_username,
                )
                if is_admin:
                    logger.info(
                        f"User {user_id}'s MTProto account is admin in channel {channel_id}"
                    )
                    return True, None
            except Exception as e:
                logger.warning(f"MTProto admin check failed: {e}")

        bot_name = creds.get("bot_username", "your bot")
        return (
            False,
            f"Your bot (@{bot_name}) needs admin access. Add it as administrator to the channel.",
        )

    except Exception as e:
        logger.error(f"Error checking user admin access: {e}")
        return False, f"Could not verify admin access: {str(e)}"


async def _check_bot_admin_via_api(bot_token: str, channel_id: int) -> bool:
    """Check if bot is admin using Telegram Bot API"""
    import aiohttp

    # Convert channel_id to Bot API format (-100 prefix)
    # Our DB stores IDs with 100 prefix (e.g., 1002678877654)
    # Bot API expects: -1002678877654
    channel_id_str = str(abs(channel_id))
    if channel_id_str.startswith("100") and len(channel_id_str) > 10:
        # Already has 100 prefix, just make negative
        chat_id = -abs(channel_id)
    elif channel_id < 0:
        # Already negative
        chat_id = channel_id
    else:
        # Raw ID without 100 prefix - add -100 prefix
        chat_id = int(f"-100{channel_id}")

    logger.debug(f"Bot API admin check: channel_id={channel_id} -> chat_id={chat_id}")

    url = f"https://api.telegram.org/bot{bot_token}/getChatAdministrators"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, json={"chat_id": chat_id}, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("ok"):
                        # Bot successfully got admin list = bot is admin or creator
                        # Check if our bot is in the admin list
                        bot_info_url = f"https://api.telegram.org/bot{bot_token}/getMe"
                        async with session.get(bot_info_url) as bot_resp:
                            if bot_resp.status == 200:
                                bot_data = await bot_resp.json()
                                bot_id = bot_data.get("result", {}).get("id")

                                admins = data.get("result", [])
                                for admin in admins:
                                    if admin.get("user", {}).get("id") == bot_id:
                                        logger.info(
                                            f"Bot {bot_id} confirmed as admin in chat {chat_id}"
                                        )
                                        return True
                        return False
                else:
                    error_data = await resp.text()
                    logger.warning(
                        f"Bot API getChatAdministrators failed: {resp.status} - {error_data}"
                    )
                return False
    except Exception as e:
        logger.warning(f"Bot API admin check failed: {e}")
        return False


async def _check_mtproto_admin(
    api_id: int,
    api_hash: str,
    session_string: str,
    channel_username: str,
) -> bool:
    """Check if MTProto session is admin using Telethon"""
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from telethon.tl.functions.channels import GetParticipantRequest

    try:
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            await client.disconnect()
            return False

        try:
            entity = await client.get_entity(channel_username)
            me = await client.get_me()

            participant = await client(GetParticipantRequest(channel=entity, participant=me))
            participant_type = type(participant.participant).__name__

            is_admin = participant_type in [
                "ChannelParticipantAdmin",
                "ChannelParticipantCreator",
            ]

            await client.disconnect()
            return is_admin

        except Exception as e:
            logger.warning(f"MTProto participant check failed: {e}")
            await client.disconnect()
            return False

    except Exception as e:
        logger.warning(f"MTProto connection failed: {e}")
        return False


@router.post("/", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def add_channel(
    channel_data: AddChannelRequest,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
    telegram_service: TelegramValidationService | None = Depends(get_telegram_validation_service),
):
    """
    ## ➕ Add Channel

    Add an existing Telegram channel for analytics tracking.

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
        telegram_created_at = None  # Will be populated if validation succeeds

        # Check if Telegram validation service is available
        if telegram_service is None:
            logger.warning(
                f"Telegram validation unavailable - allowing channel creation without admin check for: {channel_username}"
            )
            # Proceed without validation - channel will be created but may not have full access
        else:
            # Validate channel and get metadata including creation date
            validation_result = await telegram_service.validate_channel_by_username(
                channel_username
            )

            if validation_result.is_valid:
                # Store the Telegram creation date
                telegram_created_at = validation_result.telegram_created_at
                logger.info(
                    f"Channel validated: {channel_username}, telegram_created_at: {telegram_created_at}"
                )

            # Check if USER's bot/MTProto is admin (NOT system bot)
            # First try user's own credentials, then fall back to system validation
            # Prefer telegram_id from request (from lookup), then from validation result
            channel_id = channel_data.telegram_id or (
                validation_result.telegram_id if validation_result.is_valid else None
            )
            is_admin = False
            error_msg = None

            if channel_id:
                is_admin, error_msg = await _check_user_admin_access(
                    user_id=current_user["id"],
                    channel_id=channel_id,
                    channel_username=channel_username.lstrip("@"),
                )

            # If user credentials didn't work, fall back to system check
            if not is_admin and not channel_id:
                is_admin, error_msg = await telegram_service.check_bot_admin_access(
                    channel_username
                )

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

        with performance_timer("add_channel"):
            # Set user_id on the channel data
            channel_data_dict = channel_data.dict()
            channel_data_dict["user_id"] = current_user["id"]

            # Log incoming data for debugging
            logger.info(
                f"Add channel request data: telegram_id={channel_data_dict.get('telegram_id')}, subscriber_count={channel_data_dict.get('subscriber_count')}"
            )

            # Ensure telegram_id is set (use random fallback if not provided)
            if not channel_data_dict.get("telegram_id"):
                import random

                channel_data_dict["telegram_id"] = random.randint(1000000000, 9999999999)
                logger.warning(
                    f"No telegram_id provided, using fallback: {channel_data_dict['telegram_id']}"
                )
            else:
                # Convert Telegram channel ID to proper format for storage
                # Telegram returns raw channel ID (e.g., 2678877654)
                # We store with 100 prefix as POSITIVE (e.g., 1002678877654)
                # MTProto collector uses abs() everywhere, so positive is the standard
                raw_id = abs(channel_data_dict["telegram_id"])  # Ensure positive
                id_str = str(raw_id)

                if not id_str.startswith("100"):
                    # Add 100 prefix for channels (positive format)
                    channel_data_dict["telegram_id"] = int(f"100{raw_id}")
                    logger.info(
                        f"Converted channel ID: {raw_id} -> {channel_data_dict['telegram_id']}"
                    )
                else:
                    # Already has 100 prefix, ensure positive
                    channel_data_dict["telegram_id"] = raw_id

            # Clean username - remove @ prefix if present (store without @)
            if channel_data_dict.get("username"):
                channel_data_dict["username"] = channel_data_dict["username"].lstrip("@")

            # Filter to only fields expected by ChannelCreate
            from apps.api.services.channel_management_service import ChannelCreate

            valid_fields = {"name", "telegram_id", "username", "description", "user_id"}
            filtered_data = {k: v for k, v in channel_data_dict.items() if k in valid_fields}

            channel_create = ChannelCreate(**filtered_data)
            new_channel = await channel_service.add_channel(channel_create)

            # Update additional fields that aren't part of ChannelCreate
            if new_channel:
                try:
                    from datetime import datetime as dt

                    from apps.di import get_container

                    container = get_container()
                    pool = await container.database.pool()

                    async with pool.acquire() as conn:
                        # Update telegram_created_at if we have it
                        if telegram_created_at:
                            created_dt = dt.fromisoformat(
                                telegram_created_at.replace("Z", "+00:00")
                            )
                            await conn.execute(
                                """
                                UPDATE channels 
                                SET telegram_created_at = $1, updated_at = NOW()
                                WHERE id = $2
                                """,
                                created_dt,
                                new_channel.telegram_id,
                            )
                            logger.info(
                                f"Updated telegram_created_at for channel {new_channel.id}: {created_dt}"
                            )

                        # Update subscriber_count if we have it
                        subscriber_count = channel_data_dict.get("subscriber_count", 0)
                        if subscriber_count and subscriber_count > 0:
                            await conn.execute(
                                """
                                UPDATE channels 
                                SET subscriber_count = $1, updated_at = NOW()
                                WHERE id = $2
                                """,
                                subscriber_count,
                                new_channel.telegram_id,
                            )
                            logger.info(
                                f"Updated subscriber_count for channel {new_channel.id}: {subscriber_count}"
                            )

                        # Create MTProto settings record with enabled=true by default
                        # First check if record exists
                        existing = await conn.fetchval(
                            "SELECT id FROM channel_mtproto_settings WHERE channel_id = $1",
                            new_channel.telegram_id,
                        )
                        if not existing:
                            await conn.execute(
                                """
                                INSERT INTO channel_mtproto_settings (user_id, channel_id, mtproto_enabled, created_at, updated_at)
                                VALUES ($1, $2, true, NOW(), NOW())
                                """,
                                current_user["id"],
                                new_channel.telegram_id,
                            )
                            logger.info(f"Created MTProto settings for channel {new_channel.id}")
                except Exception as e:
                    logger.warning(f"Could not update additional channel fields: {e}")

        # Invalidate analytics cache so frontend sees updated channel list
        invalidate_user_channel_cache(current_user["id"])

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

        # Invalidate analytics cache so frontend sees updated channel list
        invalidate_user_channel_cache(current_user["id"])

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
