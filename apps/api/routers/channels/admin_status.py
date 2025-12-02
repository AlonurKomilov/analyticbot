"""
Channel Admin Status Checking

Endpoints for verifying bot and MTProto admin status across channels.
"""

import logging

from fastapi import APIRouter, Depends

from apps.api.middleware.auth import get_current_user
from apps.api.services.channel_management_service import ChannelManagementService

from .deps import get_channel_management_service

logger = logging.getLogger(__name__)

router = APIRouter()


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
    - Includes per-channel MTProto disabled status
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

        # Get per-channel MTProto settings
        from apps.di import get_container

        container = get_container()
        db_pool = await container.database.asyncpg_pool()

        channel_mtproto_settings = {}
        async with db_pool.acquire() as conn:
            for channel in channels:
                setting = await conn.fetchrow(
                    """
                    SELECT mtproto_enabled
                    FROM channel_mtproto_settings
                    WHERE channel_id = $1 AND user_id = $2
                    """,
                    channel.id,
                    current_user["id"],
                )
                # None = default enabled (backward compatibility)
                # False = explicitly disabled
                channel_mtproto_settings[channel.id] = (
                    setting["mtproto_enabled"] if setting else True
                )

        logger.info(f"Fetched MTProto settings for {len(channel_mtproto_settings)} channels")

        # Get user's bot and MTProto credentials
        user_bot_repo = await container.database.user_bot_repo()
        user_credentials = await user_bot_repo.get_by_user_id(current_user["id"])

        status_results = {}

        # Check each channel
        for channel in channels:
            bot_is_admin = None
            mtproto_is_admin = None
            message = "Checking admin status..."

            # Check if MTProto is disabled for this channel
            mtproto_disabled = not channel_mtproto_settings.get(channel.id, True)

            if mtproto_disabled:
                logger.info(
                    f"  🚫 Channel {channel.id} has MTProto disabled - skipping admin check"
                )
                # For disabled channels, set mtproto_is_admin to None and add indicator
                mtproto_is_admin = None

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
            # Our DB stores IDs with 100 prefix already (e.g., 1002678877654)
            # So we just need to make it negative for Bot API (-1002678877654)
            bot_api_chat_id = None
            if channel.telegram_id:
                channel_id_str = str(abs(channel.telegram_id))
                # If ID already has 100 prefix, just make negative
                if channel_id_str.startswith("100") and len(channel_id_str) > 10:
                    bot_api_chat_id = -abs(channel.telegram_id)
                elif channel.telegram_id > 0:
                    # Raw ID without 100 prefix - add it
                    bot_api_chat_id = int(f"-100{channel.telegram_id}")
                else:
                    # Already negative
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
                                    f"✅ User {current_user['id']} bot is admin of "
                                    f"channel {channel.id}"
                                )
                            else:
                                logger.warning(
                                    f"❌ User {current_user['id']} bot is NOT admin "
                                    f"(status: {chat_member.status})"
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

            # Check MTProto admin status (if user has configured MTProto AND channel has it enabled)
            if (
                not mtproto_disabled
                and user_credentials
                and user_credentials.mtproto_enabled
                and user_credentials.session_string
            ):
                try:
                    # Use ChannelAdminCheckService (Clean Architecture)
                    from apps.api.services.channel_admin_check_service import (
                        get_channel_admin_check_service,
                    )

                    admin_check_service = await get_channel_admin_check_service()
                    result = await admin_check_service.check_mtproto_admin_status(
                        user_id=current_user["id"],
                        channel_id=channel.id,
                        channel_username=channel_username,
                        telegram_id=channel.telegram_id,
                    )

                    mtproto_is_admin = result["is_admin"]

                    if mtproto_is_admin:
                        logger.info(
                            f"✅ User {current_user['id']} MTProto is admin of channel {channel.id} "
                            f"(method: {result['method_used']})"
                        )
                    elif result["error"]:
                        logger.warning(
                            f"❌ MTProto admin check failed for channel {channel.id}: "
                            f"{result['error']}"
                        )
                    else:
                        logger.warning(
                            f"❌ User {current_user['id']} MTProto is NOT admin of "
                            f"channel {channel.id}"
                        )

                except Exception as e:
                    logger.error(f"Error checking MTProto admin for channel {channel.id}: {e}")
                    mtproto_is_admin = None

            # Determine message based on status
            # null = not configured, false = configured but not admin, true = admin
            if mtproto_disabled:
                # Channel has MTProto explicitly disabled
                if bot_is_admin is True:
                    message = "✓ Bot has admin access - MTProto disabled for this channel"
                elif bot_is_admin is False:
                    message = "🚫 Bot has no admin access - MTProto disabled for this channel"
                elif bot_is_admin is None:
                    message = (
                        "🚫 MTProto disabled for this channel - Configure bot for data collection"
                    )
                else:
                    message = "🚫 MTProto disabled for this channel"
            elif bot_is_admin is None and mtproto_is_admin is None:
                # User hasn't configured bot OR MTProto
                message = (
                    "⚠️ Setup required: Configure your bot or MTProto session to enable "
                    "data collection"
                )
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
                "mtproto_disabled": mtproto_disabled,
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
