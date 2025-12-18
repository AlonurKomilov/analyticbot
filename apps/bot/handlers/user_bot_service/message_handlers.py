"""
Message Handlers for User Bot Moderation

Handles:
- Banned word detection
- Spam detection
- Link/forward blocking
- Flood protection
"""

import asyncio
import logging
from datetime import timedelta
from typing import Any

from aiogram import Bot, Router
from aiogram.types import ChatPermissions, Message

from core.models.user_bot_service_domain import (
    ModerationAction,
    PerformedBy,
    WarningType,
)

logger = logging.getLogger(__name__)
router = Router()


class MessageModerationHandler:
    """Handler for message moderation events."""

    def __init__(
        self,
        bot: Bot,
        user_id: int,  # Bot owner
        service: Any,  # UserBotService
    ):
        self.bot = bot
        self.user_id = user_id
        self.service = moderation_service

    async def handle_message(self, message: Message) -> bool:
        """
        Process a message through moderation checks.

        Returns:
            True if message should be blocked, False otherwise
        """
        if not message.chat or not message.from_user:
            return False

        chat_id = message.chat.id
        sender_id = message.from_user.id

        # Don't moderate bot owners or admins
        settings = await self.service.get_settings(self.user_id, chat_id)
        if not settings:
            return False

        if settings.is_user_whitelisted(sender_id) or settings.is_user_admin(sender_id):
            return False

        # Check if user is chat admin (don't moderate admins)
        try:
            member = await self.bot.get_chat_member(chat_id, sender_id)
            if member.status in ["administrator", "creator"]:
                return False
        except Exception:
            pass  # Continue with moderation

        # Determine message properties
        message_text = message.text or message.caption
        is_forward = message.forward_from is not None or message.forward_from_chat is not None
        has_links = bool(
            message.entities and any(e.type in ["url", "text_link"] for e in message.entities)
        )

        # Run moderation check
        result = await self.service.check_message(
            user_id=self.user_id,
            chat_id=chat_id,
            sender_tg_id=sender_id,
            message_text=message_text,
            is_forward=is_forward,
            has_links=has_links,
            message_id=message.message_id,
        )

        if not result.triggered:
            return False

        # Execute moderation action
        await self._execute_action(message, result)
        return True

    async def _execute_action(self, message: Message, result: Any) -> None:
        """Execute moderation action based on check result."""
        chat_id = message.chat.id
        sender_id = message.from_user.id
        sender_name = message.from_user.full_name
        sender_username = message.from_user.username

        # Delete message if needed
        if result.should_delete:
            try:
                await message.delete()

                # Log deletion
                await self.service.log_moderation_action(
                    user_id=self.user_id,
                    chat_id=chat_id,
                    action="message_deleted",
                    target_tg_id=sender_id,
                    target_username=sender_username,
                    performed_by=PerformedBy.BOT_AUTO,
                    reason=self._get_deletion_reason(result),
                    details={
                        "message_id": message.message_id,
                        "banned_word": (
                            result.banned_word_match.word if result.banned_word_match else None
                        ),
                        "spam_confidence": (
                            result.spam_result.confidence if result.spam_result else None
                        ),
                    },
                    message_id=message.message_id,
                )
            except Exception as e:
                logger.error(f"Failed to delete message: {e}")

        # Issue warning if needed
        if result.should_warn:
            warning_type = self._get_warning_type(result)
            reason = self._get_warning_reason(result)

            warning, total_warnings, action_to_take = await self.service.warn_user(
                user_id=self.user_id,
                chat_id=chat_id,
                warned_tg_id=sender_id,
                warned_username=sender_username,
                warned_name=sender_name,
                reason=reason,
                warning_type=warning_type,
                message_id=message.message_id,
                message_text=message.text[:200] if message.text else None,
            )

            # Get settings for max warnings
            settings = await self.service.get_settings(self.user_id, chat_id)
            max_warnings = settings.max_warnings if settings else 3

            # Notify user
            try:
                warning_msg = (
                    f"⚠️ <b>Warning</b> ({total_warnings}/{max_warnings})\n\n"
                    f"User: {sender_name}\n"
                    f"Reason: {reason}\n"
                )

                if action_to_take:
                    warning_msg += f"\n🚫 <b>Action taken:</b> {action_to_take.value}"

                sent_msg = await self.bot.send_message(chat_id, warning_msg, parse_mode="HTML")

                # Auto-delete warning message after 30 seconds
                asyncio.create_task(self._delete_after_delay(sent_msg, 30))

            except Exception as e:
                logger.error(f"Failed to send warning message: {e}")

            # Execute action if max warnings reached
            if action_to_take:
                await self._execute_punishment(
                    chat_id, sender_id, sender_name, action_to_take, settings
                )

    async def _execute_punishment(
        self,
        chat_id: int,
        user_id: int,
        user_name: str,
        action: ModerationAction,
        settings: Any,
    ) -> None:
        """Execute punishment action (mute, kick, ban)."""
        try:
            if action == ModerationAction.MUTE:
                # Mute user
                mute_duration = settings.mute_duration_minutes if settings else 60
                until_date = timedelta(minutes=mute_duration)

                await self.bot.restrict_chat_member(
                    chat_id,
                    user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=until_date,
                )

                # Log
                await self.service.log_moderation_action(
                    user_id=self.user_id,
                    chat_id=chat_id,
                    action="user_muted",
                    target_tg_id=user_id,
                    performed_by=PerformedBy.BOT_AUTO,
                    reason="Max warnings reached",
                    details={"duration_minutes": mute_duration},
                )

            elif action == ModerationAction.KICK:
                await self.bot.ban_chat_member(chat_id, user_id)
                await self.bot.unban_chat_member(chat_id, user_id)  # Unban to allow rejoin

                await self.service.log_moderation_action(
                    user_id=self.user_id,
                    chat_id=chat_id,
                    action="user_kicked",
                    target_tg_id=user_id,
                    performed_by=PerformedBy.BOT_AUTO,
                    reason="Max warnings reached",
                )

            elif action == ModerationAction.BAN:
                await self.bot.ban_chat_member(chat_id, user_id)

                await self.service.log_moderation_action(
                    user_id=self.user_id,
                    chat_id=chat_id,
                    action="user_banned",
                    target_tg_id=user_id,
                    performed_by=PerformedBy.BOT_AUTO,
                    reason="Max warnings reached",
                )

        except Exception as e:
            logger.error(f"Failed to execute punishment {action}: {e}")

    async def _delete_after_delay(self, message: Message, seconds: int) -> None:
        """Delete a message after a delay."""
        await asyncio.sleep(seconds)
        try:
            await message.delete()
        except Exception:
            pass  # Ignore if already deleted

    def _get_deletion_reason(self, result: Any) -> str:
        """Get human-readable deletion reason."""
        if result.banned_word_match:
            return f"Banned word: {result.banned_word_match.word}"
        if result.spam_result:
            return "Spam detected"
        if result.flood_result:
            return "Flood detected"
        return "Rule violation"

    def _get_warning_type(self, result: Any) -> WarningType:
        """Get warning type from result."""
        if result.banned_word_match:
            return WarningType.BANNED_WORD
        if result.spam_result:
            return WarningType.SPAM
        if result.flood_result:
            return WarningType.FLOOD
        return WarningType.MANUAL

    def _get_warning_reason(self, result: Any) -> str:
        """Get warning reason from result."""
        if result.banned_word_match:
            return "Used banned word/phrase"
        if result.spam_result:
            return "Spam content detected"
        if result.flood_result:
            return "Flooding the chat"
        return "Rule violation"


# Factory function to create message handler
def create_message_handler(bot: Bot, user_id: int, service: Any) -> MessageModerationHandler:
    """Create a message moderation handler."""
    return MessageModerationHandler(bot, user_id, service)
