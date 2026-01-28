"""
User Bot Moderation Router Factory

Creates and configures the moderation router for user bots.
Integrates message handlers, member handlers, and admin commands.
"""

import logging
from typing import Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import ChatMemberUpdated, Message

from .admin_commands import AdminCommandHandler
from .member_handlers import MemberModerationHandler
from .message_handlers import MessageModerationHandler

logger = logging.getLogger(__name__)


def create_service_router(
    bot: Bot,
    user_id: int,
    service: Any,  # UserBotService
    bot_features_manager: Any | None = None,  # BotFeaturesManager (optional)
) -> Router:
    """
    Create a fully configured moderation router for a user's bot.

    This router handles:
    - Message moderation (spam, banned words, links, forwards)
    - Member events (join/leave, welcome messages)
    - Admin commands (warn, ban, settings, etc.)
    - Marketplace service integration (feature gates, usage logging)

    Args:
        bot: The bot instance
        user_id: Bot owner's user ID
        service: The moderation service instance
        bot_features_manager: Manager for marketplace bot services (optional)

    Returns:
        Configured Router with all moderation handlers
    """
    router = Router(name=f"moderation_{user_id}")

    # Create handlers
    message_handler = MessageModerationHandler(bot, user_id, service)
    member_handler = MemberModerationHandler(bot, user_id, service)
    admin_handler = AdminCommandHandler(bot, user_id, service)

    # Store features manager for use in handlers
    router.bot_features_manager = bot_features_manager  # type: ignore

    # ===========================================
    # Admin Commands
    # ===========================================

    @router.message(Command("settings"))
    async def cmd_settings(message: Message):
        await admin_handler.handle_settings(message)

    @router.message(Command("setup"))
    async def cmd_setup(message: Message):
        await admin_handler.handle_setup(message)

    @router.message(Command("toggle"))
    async def cmd_toggle(message: Message, command: CommandObject):
        await admin_handler.handle_toggle(message, command)

    @router.message(Command("warn"))
    async def cmd_warn(message: Message, command: CommandObject):
        await admin_handler.handle_warn(message, command)

    @router.message(Command("unwarn"))
    async def cmd_unwarn(message: Message):
        await admin_handler.handle_unwarn(message)

    @router.message(Command("warnings"))
    async def cmd_warnings(message: Message):
        await admin_handler.handle_warnings(message)

    @router.message(Command("mute"))
    async def cmd_mute(message: Message, command: CommandObject):
        await admin_handler.handle_mute(message, command)

    @router.message(Command("unmute"))
    async def cmd_unmute(message: Message):
        await admin_handler.handle_unmute(message)

    @router.message(Command("ban"))
    async def cmd_ban(message: Message, command: CommandObject):
        await admin_handler.handle_ban(message, command)

    @router.message(Command("unban"))
    async def cmd_unban(message: Message):
        await admin_handler.handle_unban(message)

    @router.message(Command("addword"))
    async def cmd_addword(message: Message, command: CommandObject):
        await admin_handler.handle_addword(message, command)

    @router.message(Command("delword"))
    async def cmd_delword(message: Message, command: CommandObject):
        await admin_handler.handle_delword(message, command)

    @router.message(Command("words"))
    async def cmd_words(message: Message):
        await admin_handler.handle_words(message)

    @router.message(Command("setwelcome"))
    async def cmd_setwelcome(message: Message, command: CommandObject):
        await admin_handler.handle_setwelcome(message, command)

    @router.message(Command("setgoodbye"))
    async def cmd_setgoodbye(message: Message, command: CommandObject):
        await admin_handler.handle_setgoodbye(message, command)

    @router.message(Command("invites"))
    async def cmd_invites(message: Message):
        await admin_handler.handle_invites(message)

    @router.message(Command("modlog"))
    async def cmd_modlog(message: Message):
        await admin_handler.handle_modlog(message)

    # ===========================================
    # Service Messages (Join/Leave) with Marketplace Integration
    # ===========================================

    @router.message(F.new_chat_members)
    async def handle_new_members(message: Message):
        """Handle new member join service messages."""
        # First, handle traditional member processing (tracking, welcome, etc.)
        await member_handler.handle_service_message(message)

        # Then, check if auto-delete is enabled via marketplace service
        if bot_features_manager:
            try:
                result = await bot_features_manager.handle_join_message(message)
                if result.get("success") and result.get("deleted"):
                    logger.info("Auto-deleted join message via marketplace service")
            except Exception as e:
                logger.error(f"Failed to handle join via marketplace: {e}")

    @router.message(F.left_chat_member)
    async def handle_left_member(message: Message):
        """Handle member left service messages."""
        # First, handle traditional member processing (tracking, etc.)
        await member_handler.handle_service_message(message)

        # Then, check if auto-delete is enabled via marketplace service
        if bot_features_manager:
            try:
                result = await bot_features_manager.handle_leave_message(message)
                if result.get("success") and result.get("deleted"):
                    logger.info("Auto-deleted leave message via marketplace service")
            except Exception as e:
                logger.error(f"Failed to handle leave via marketplace: {e}")

    # ===========================================
    # Chat Member Updates (from webhook)
    # ===========================================

    @router.chat_member()
    async def handle_chat_member_update(update: ChatMemberUpdated):
        """Handle chat member status updates."""
        await member_handler.handle_chat_member_update(update)

    # ===========================================
    # Regular Messages (Moderation Check with Marketplace Integration)
    # ===========================================

    @router.message(F.text | F.caption)
    async def handle_text_message(message: Message):
        """Check text messages for moderation."""
        # Skip commands
        if message.text and message.text.startswith("/"):
            return

        # MARKETPLACE: Check for spam using anti-spam service if available
        if bot_features_manager and message.chat and message.from_user and message.text:
            try:
                spam_check = await bot_features_manager.check_message_spam(
                    chat_id=message.chat.id,
                    sender_tg_id=message.from_user.id,
                    message_text=message.text or message.caption or "",
                    message_id=message.message_id,
                    has_links=bool(
                        message.entities
                        and any(e.type in ["url", "text_link"] for e in message.entities)
                    ),
                    is_forward=message.forward_from is not None
                    or message.forward_from_chat is not None,
                )

                # If spam detected and flagged for deletion, delete it
                if spam_check.get("success") and spam_check.get("is_spam"):
                    if spam_check.get("action_taken") == "message_deleted":
                        try:
                            await message.delete()
                            logger.info(
                                f"🛡️ Deleted spam message via marketplace service: "
                                f"confidence={spam_check.get('confidence'):.2f}"
                            )
                            return  # Don't process further
                        except Exception as e:
                            logger.error(f"Failed to delete spam message: {e}")
            except Exception as e:
                logger.error(f"Failed marketplace spam check: {e}")

        # Run traditional moderation check (banned words, etc.)
        await message_handler.handle_message(message)

    @router.message(F.forward_from | F.forward_from_chat)
    async def handle_forward(message: Message):
        """Check forwarded messages."""
        await message_handler.handle_message(message)

    logger.info(f"Created moderation router for user {user_id}")
    return router


def register_moderation_handlers(
    dp: Dispatcher,
    bot: Bot,
    user_id: int,
    service: Any,
) -> None:
    """
    Register moderation handlers on an existing dispatcher.

    Alternative to using create_service_router for cases
    where you want to add handlers to an existing dispatcher.

    Args:
        dp: The dispatcher to register handlers on
        bot: The bot instance
        user_id: Bot owner's user ID
        service: The moderation service instance
    """
    router = create_service_router(bot, user_id, service)
    dp.include_router(router)
    logger.info(f"Registered moderation handlers on dispatcher for user {user_id}")
