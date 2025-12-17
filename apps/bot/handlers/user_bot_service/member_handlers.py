"""
Member Handlers for User Bot Moderation

Handles:
- Join/leave message cleaning
- Welcome messages
- Invite tracking
- Member updates
"""

import asyncio
import logging
from typing import Any

from aiogram import Bot, Router
from aiogram.types import (
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from core.models.user_bot_service_domain import (
    MessageType,
    PerformedBy,
)

logger = logging.getLogger(__name__)
router = Router()


class MemberModerationHandler:
    """Handler for member-related moderation events."""

    def __init__(
        self,
        bot: Bot,
        user_id: int,  # Bot owner
        service: Any,  # UserBotService
    ):
        self.bot = bot
        self.user_id = user_id
        self.service = moderation_service

    async def handle_new_member(
        self,
        chat_id: int,
        new_member_id: int,
        new_member_name: str,
        new_member_username: str | None,
        inviter_id: int | None = None,
        inviter_name: str | None = None,
        inviter_username: str | None = None,
        invite_link: str | None = None,
        chat_title: str | None = None,
    ) -> None:
        """Handle a new member joining the chat."""
        settings = await self.service.get_settings(self.user_id, chat_id)
        if not settings:
            return

        # Track invite if enabled
        if settings.invite_tracking_enabled and inviter_id and inviter_id != new_member_id:
            try:
                await self.service.track_invite(
                    user_id=self.user_id,
                    chat_id=chat_id,
                    inviter_tg_id=inviter_id,
                    inviter_username=inviter_username,
                    inviter_name=inviter_name,
                    invited_tg_id=new_member_id,
                    invited_username=new_member_username,
                    invited_name=new_member_name,
                    invite_link=invite_link,
                )
                logger.info(
                    f"Tracked invite: {inviter_name} invited {new_member_name} to {chat_id}"
                )
            except Exception as e:
                logger.error(f"Failed to track invite: {e}")

        # Send welcome message if enabled
        if settings.welcome_enabled:
            try:
                # Get member count
                member_count = None
                try:
                    member_count = await self.bot.get_chat_member_count(chat_id)
                except Exception:
                    pass

                formatted_message = await self.service.format_welcome_message(
                    user_id=self.user_id,
                    chat_id=chat_id,
                    new_member_name=new_member_name,
                    new_member_username=new_member_username,
                    new_member_id=new_member_id,
                    chat_title=chat_title or "this chat",
                    member_count=member_count,
                    message_type=MessageType.WELCOME,
                )

                if formatted_message:
                    welcome_config = await self.service.get_welcome_message(
                        self.user_id, chat_id, MessageType.WELCOME
                    )

                    # Build inline keyboard if buttons configured
                    reply_markup = None
                    if welcome_config and welcome_config.buttons:
                        reply_markup = self._build_keyboard(welcome_config.buttons)

                    # Send welcome message
                    sent_msg = await self.bot.send_message(
                        chat_id,
                        formatted_message,
                        parse_mode=(welcome_config.parse_mode if welcome_config else "HTML"),
                        reply_markup=reply_markup,
                    )

                    # Auto-delete if configured
                    if welcome_config and welcome_config.delete_after_seconds:
                        asyncio.create_task(
                            self._delete_after_delay(sent_msg, welcome_config.delete_after_seconds)
                        )

                    logger.info(f"Sent welcome message to {new_member_name} in {chat_id}")

            except Exception as e:
                logger.error(f"Failed to send welcome message: {e}")

    async def handle_member_left(
        self,
        chat_id: int,
        member_id: int,
        member_name: str,
        member_username: str | None,
        chat_title: str | None = None,
    ) -> None:
        """Handle a member leaving the chat."""
        settings = await self.service.get_settings(self.user_id, chat_id)
        if not settings:
            return

        # Update invite tracking
        if settings.invite_tracking_enabled:
            try:
                await self.service.mark_member_left(self.user_id, chat_id, member_id)
            except Exception as e:
                logger.error(f"Failed to update invite tracking: {e}")

        # Send goodbye message if configured
        if settings.welcome_enabled:
            try:
                formatted_message = await self.service.format_welcome_message(
                    user_id=self.user_id,
                    chat_id=chat_id,
                    new_member_name=member_name,
                    new_member_username=member_username,
                    new_member_id=member_id,
                    chat_title=chat_title or "this chat",
                    message_type=MessageType.GOODBYE,
                )

                if formatted_message:
                    goodbye_config = await self.service.get_welcome_message(
                        self.user_id, chat_id, MessageType.GOODBYE
                    )

                    sent_msg = await self.bot.send_message(
                        chat_id,
                        formatted_message,
                        parse_mode=(goodbye_config.parse_mode if goodbye_config else "HTML"),
                    )

                    if goodbye_config and goodbye_config.delete_after_seconds:
                        asyncio.create_task(
                            self._delete_after_delay(sent_msg, goodbye_config.delete_after_seconds)
                        )

            except Exception as e:
                logger.error(f"Failed to send goodbye message: {e}")

    async def handle_service_message(self, message: Message) -> bool:
        """
        Handle service messages (join/leave notifications).

        Returns:
            True if message was deleted, False otherwise
        """
        if not message.chat:
            return False

        chat_id = message.chat.id
        settings = await self.service.get_settings(self.user_id, chat_id)
        if not settings:
            return False

        should_delete = False

        # Check if it's a join message
        if message.new_chat_members and settings.clean_join_messages:
            should_delete = True

            # Process each new member
            for member in message.new_chat_members:
                if not member.is_bot:  # Don't process bot joins
                    inviter_id = None
                    inviter_name = None
                    inviter_username = None

                    if message.from_user and message.from_user.id != member.id:
                        inviter_id = message.from_user.id
                        inviter_name = message.from_user.full_name
                        inviter_username = message.from_user.username

                    await self.handle_new_member(
                        chat_id=chat_id,
                        new_member_id=member.id,
                        new_member_name=member.full_name,
                        new_member_username=member.username,
                        inviter_id=inviter_id,
                        inviter_name=inviter_name,
                        inviter_username=inviter_username,
                        chat_title=message.chat.title,
                    )

        # Check if it's a leave message
        if message.left_chat_member and settings.clean_leave_messages:
            should_delete = True

            member = message.left_chat_member
            if not member.is_bot:
                await self.handle_member_left(
                    chat_id=chat_id,
                    member_id=member.id,
                    member_name=member.full_name,
                    member_username=member.username,
                    chat_title=message.chat.title,
                )

        # Delete service message if configured
        if should_delete:
            try:
                await message.delete()

                # Log deletion
                await self.service.log_moderation_action(
                    user_id=self.user_id,
                    chat_id=chat_id,
                    action="service_message_deleted",
                    performed_by=PerformedBy.BOT_AUTO,
                    reason="Service message cleaning enabled",
                    message_id=message.message_id,
                )

                return True
            except Exception as e:
                logger.error(f"Failed to delete service message: {e}")

        return False

    async def handle_chat_member_update(self, update: ChatMemberUpdated) -> None:
        """Handle chat member status updates (from webhook)."""
        chat_id = update.chat.id

        old_status = update.old_chat_member.status if update.old_chat_member else None
        new_status = update.new_chat_member.status if update.new_chat_member else None

        member = update.new_chat_member.user if update.new_chat_member else None
        if not member or member.is_bot:
            return

        # Member joined
        if old_status in [None, "left", "kicked"] and new_status == "member":
            inviter_id = None
            inviter_name = None
            inviter_username = None
            invite_link = None

            if update.from_user and update.from_user.id != member.id:
                inviter_id = update.from_user.id
                inviter_name = update.from_user.full_name
                inviter_username = update.from_user.username

            if update.invite_link:
                invite_link = update.invite_link.invite_link

            await self.handle_new_member(
                chat_id=chat_id,
                new_member_id=member.id,
                new_member_name=member.full_name,
                new_member_username=member.username,
                inviter_id=inviter_id,
                inviter_name=inviter_name,
                inviter_username=inviter_username,
                invite_link=invite_link,
                chat_title=update.chat.title,
            )

        # Member left
        elif old_status == "member" and new_status in ["left", "kicked"]:
            await self.handle_member_left(
                chat_id=chat_id,
                member_id=member.id,
                member_name=member.full_name,
                member_username=member.username,
                chat_title=update.chat.title,
            )

    def _build_keyboard(self, buttons: list[dict]) -> InlineKeyboardMarkup | None:
        """Build inline keyboard from button configuration."""
        if not buttons:
            return None

        keyboard_rows = []
        for row in buttons:
            if isinstance(row, list):
                # Row of buttons
                button_row = []
                for btn in row:
                    button_row.append(
                        InlineKeyboardButton(
                            text=btn.get("text", "Button"),
                            url=btn.get("url"),
                            callback_data=btn.get("callback_data"),
                        )
                    )
                keyboard_rows.append(button_row)
            elif isinstance(row, dict):
                # Single button
                keyboard_rows.append(
                    [
                        InlineKeyboardButton(
                            text=row.get("text", "Button"),
                            url=row.get("url"),
                            callback_data=row.get("callback_data"),
                        )
                    ]
                )

        return InlineKeyboardMarkup(inline_keyboard=keyboard_rows) if keyboard_rows else None

    async def _delete_after_delay(self, message: Message, seconds: int) -> None:
        """Delete a message after a delay."""
        await asyncio.sleep(seconds)
        try:
            await message.delete()
        except Exception:
            pass  # Ignore if already deleted


# Factory function
def create_member_handler(bot: Bot, user_id: int, service: Any) -> MemberModerationHandler:
    """Create a member moderation handler."""
    return MemberModerationHandler(bot, user_id, service)
