"""
Admin Commands for User Bot Moderation

Bot commands for managing moderation settings:
- /settings - View/edit moderation settings
- /warn - Manually warn a user
- /unwarn - Remove warnings from a user
- /ban - Ban a user
- /mute - Mute a user
- /unmute - Unmute a user
- /invites - View invite statistics
- /addword - Add banned word
- /delword - Remove banned word
- /words - List banned words
- /setwelcome - Set welcome message
- /modlog - View moderation log
"""

import logging
from datetime import timedelta
from typing import Any, cast

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ChatPermissions, User

from core.models.user_bot_service_domain import (
    ModerationAction,
    PerformedBy,
    WarningType,
    MessageType,
)

logger = logging.getLogger(__name__)
router = Router()


class AdminCommandHandler:
    """Handler for admin moderation commands."""

    def __init__(
        self,
        bot: Bot,
        user_id: int,  # Bot owner
        service: Any,  # UserBotService
    ):
        self.bot = bot
        self.user_id = user_id
        self.service = moderation_service

    async def _is_admin(self, message: Message) -> bool:
        """Check if user is admin or bot owner."""
        if not message.from_user or not message.chat:
            return False
        
        # Bot owner is always admin
        if message.from_user.id == self.user_id:
            return True
        
        # Check chat admin status
        try:
            member = await self.bot.get_chat_member(
                message.chat.id, message.from_user.id
            )
            return member.status in ["administrator", "creator"]
        except Exception:
            return False
    
    async def _get_target_user(self, message: Message) -> tuple[int, str, str | None] | None:
        """Get target user from reply or mention."""
        if message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user
            return user.id, user.full_name, user.username
        
        # Could also parse @username from command args
        return None

    # ===========================================
    # Settings Commands
    # ===========================================

    async def handle_settings(self, message: Message) -> None:
        """Show current moderation settings."""
        if not await self._is_admin(message):
            return
        
        chat_id = message.chat.id
        settings = await self.service.get_settings(self.user_id, chat_id)
        
        if not settings:
            await message.answer(
                "⚙️ No moderation settings configured for this chat.\n"
                "Use /setup to initialize settings."
            )
            return
        
        # Build settings display
        features = []
        if settings.clean_join_messages:
            features.append("✅ Clean join messages")
        if settings.clean_leave_messages:
            features.append("✅ Clean leave messages")
        if settings.banned_words_enabled:
            features.append("✅ Banned words filter")
        if settings.anti_spam_enabled:
            features.append("✅ Anti-spam protection")
        if settings.anti_link_enabled:
            features.append("✅ Link blocking")
        if settings.anti_forward_enabled:
            features.append("✅ Forward blocking")
        if settings.welcome_enabled:
            features.append("✅ Welcome messages")
        if settings.invite_tracking_enabled:
            features.append("✅ Invite tracking")
        
        if not features:
            features.append("❌ No features enabled")
        
        text = (
            f"⚙️ <b>Moderation Settings</b>\n"
            f"Chat: {message.chat.title or 'Unknown'}\n\n"
            f"<b>Features:</b>\n"
            + "\n".join(features) +
            f"\n\n<b>Warnings:</b>\n"
            f"• Max warnings: {settings.max_warnings}\n"
            f"• Action on max: {settings.warning_action.value}\n"
            f"• Mute duration: {settings.mute_duration_minutes} min\n"
            f"\n<b>Flood protection:</b>\n"
            f"• Limit: {settings.flood_limit} msgs / {settings.flood_interval_seconds}s"
        )
        
        await message.answer(text, parse_mode="HTML")

    async def handle_setup(self, message: Message) -> None:
        """Initialize moderation settings for chat."""
        if not await self._is_admin(message):
            return
        
        chat_id = message.chat.id
        chat_type_str = message.chat.type
        
        # Map chat type
        from core.models.user_bot_service_domain import ChatType
        chat_type = ChatType.GROUP
        if chat_type_str == "supergroup":
            chat_type = ChatType.SUPERGROUP
        elif chat_type_str == "channel":
            chat_type = ChatType.CHANNEL
        
        settings = await self.service.get_or_create_settings(
            user_id=self.user_id,
            chat_id=chat_id,
            chat_type=chat_type,
            chat_title=message.chat.title,
        )
        
        await message.answer(
            "✅ <b>Moderation initialized!</b>\n\n"
            "Use these commands to configure:\n"
            "• /toggle &lt;feature&gt; - Toggle a feature\n"
            "• /setwelcome - Set welcome message\n"
            "• /addword &lt;word&gt; - Add banned word\n"
            "• /settings - View current settings\n\n"
            "<b>Available features:</b>\n"
            "clean_join, clean_leave, banned_words, anti_spam, "
            "anti_link, anti_forward, welcome, invite_tracking",
            parse_mode="HTML"
        )

    async def handle_toggle(self, message: Message, command: CommandObject) -> None:
        """Toggle a moderation feature."""
        if not await self._is_admin(message):
            return
        
        if not command.args:
            await message.answer(
                "Usage: /toggle <feature>\n\n"
                "Features: clean_join, clean_leave, banned_words, "
                "anti_spam, anti_link, anti_forward, welcome, invite_tracking"
            )
            return
        
        feature = command.args.strip().lower()
        chat_id = message.chat.id
        
        settings = await self.service.get_settings(self.user_id, chat_id)
        if not settings:
            await message.answer("❌ Run /setup first to initialize moderation.")
            return
        
        # Toggle the feature
        feature_map = {
            "clean_join": "clean_join_messages",
            "clean_leave": "clean_leave_messages",
            "banned_words": "banned_words_enabled",
            "anti_spam": "anti_spam_enabled",
            "anti_link": "anti_link_enabled",
            "anti_forward": "anti_forward_enabled",
            "welcome": "welcome_enabled",
            "invite_tracking": "invite_tracking_enabled",
        }
        
        if feature not in feature_map:
            await message.answer(f"❌ Unknown feature: {feature}")
            return
        
        attr_name = feature_map[feature]
        current_value = getattr(settings, attr_name)
        new_value = not current_value
        setattr(settings, attr_name, new_value)
        
        await self.service.update_settings(settings)
        
        status = "✅ Enabled" if new_value else "❌ Disabled"
        await message.answer(f"{status}: {feature}")

    # ===========================================
    # Warning Commands
    # ===========================================

    async def handle_warn(self, message: Message, command: CommandObject) -> None:
        """Warn a user manually."""
        if not await self._is_admin(message):
            return
        
        target = await self._get_target_user(message)
        if not target:
            await message.answer("❌ Reply to a message to warn the user.")
            return
        
        target_id, target_name, target_username = target
        reason = command.args if command.args else "Manual warning by admin"
        chat_id = message.chat.id
        admin = cast(User, message.from_user)
        
        warning, total, action = await self.service.warn_user(
            user_id=self.user_id,
            chat_id=chat_id,
            warned_tg_id=target_id,
            warned_username=target_username,
            warned_name=target_name,
            reason=reason,
            warning_type=WarningType.MANUAL,
            issued_by_tg_id=admin.id,
        )
        
        settings = await self.service.get_settings(self.user_id, chat_id)
        max_warnings = settings.max_warnings if settings else 3
        
        text = (
            f"⚠️ <b>Warning Issued</b>\n\n"
            f"User: {target_name}\n"
            f"Warnings: {total}/{max_warnings}\n"
            f"Reason: {reason}\n"
            f"By: {admin.full_name}"
        )
        
        if action:
            text += f"\n\n🚫 <b>Action taken:</b> {action.value}"
            
            # Execute action
            if action == ModerationAction.MUTE:
                duration = settings.mute_duration_minutes if settings else 60
                await self.bot.restrict_chat_member(
                    chat_id, target_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=timedelta(minutes=duration),
                )
            elif action == ModerationAction.BAN:
                await self.bot.ban_chat_member(chat_id, target_id)
        
        await message.answer(text, parse_mode="HTML")

    async def handle_unwarn(self, message: Message) -> None:
        """Clear warnings for a user."""
        if not await self._is_admin(message):
            return
        
        target = await self._get_target_user(message)
        if not target:
            await message.answer("❌ Reply to a message to clear warnings.")
            return
        
        target_id, target_name, _ = target
        chat_id = message.chat.id
        
        cleared = await self.service.clear_user_warnings(
            self.user_id, chat_id, target_id
        )
        
        await message.answer(
            f"✅ Cleared {cleared} warning(s) for {target_name}"
        )

    async def handle_warnings(self, message: Message) -> None:
        """Show warnings for a user."""
        if not await self._is_admin(message):
            return
        
        target = await self._get_target_user(message)
        if not target:
            await message.answer("❌ Reply to a message to view warnings.")
            return
        
        target_id, target_name, _ = target
        chat_id = message.chat.id
        
        warnings = await self.service.get_user_warnings(
            self.user_id, chat_id, target_id
        )
        
        if not warnings:
            await message.answer(f"✅ {target_name} has no active warnings.")
            return
        
        text = f"⚠️ <b>Warnings for {target_name}</b>\n\n"
        for i, w in enumerate(warnings, 1):
            text += f"{i}. {w.reason} ({w.warning_type.value})\n"
            text += f"   📅 {w.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        
        await message.answer(text, parse_mode="HTML")

    # ===========================================
    # Moderation Actions
    # ===========================================

    async def handle_mute(self, message: Message, command: CommandObject) -> None:
        """Mute a user."""
        if not await self._is_admin(message):
            return
        
        target = await self._get_target_user(message)
        if not target:
            await message.answer("❌ Reply to a message to mute the user.")
            return
        
        target_id, target_name, target_username = target
        chat_id = message.chat.id
        admin = cast(User, message.from_user)
        
        # Parse duration (default 60 minutes)
        duration = 60
        if command.args:
            try:
                duration = int(command.args)
            except ValueError:
                pass
        
        await self.bot.restrict_chat_member(
            chat_id, target_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=timedelta(minutes=duration),
        )
        
        await self.service.log_moderation_action(
            user_id=self.user_id,
            chat_id=chat_id,
            action="user_muted",
            target_tg_id=target_id,
            target_username=target_username,
            performed_by=PerformedBy.ADMIN_MANUAL,
            performed_by_tg_id=admin.id,
            reason=f"Manual mute for {duration} minutes",
            details={"duration_minutes": duration},
        )
        
        await message.answer(
            f"🔇 {target_name} has been muted for {duration} minutes."
        )

    async def handle_unmute(self, message: Message) -> None:
        """Unmute a user."""
        if not await self._is_admin(message):
            return
        
        target = await self._get_target_user(message)
        if not target:
            await message.answer("❌ Reply to a message to unmute the user.")
            return
        
        target_id, target_name, target_username = target
        chat_id = message.chat.id
        admin = cast(User, message.from_user)
        
        await self.bot.restrict_chat_member(
            chat_id, target_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        
        await self.service.log_moderation_action(
            user_id=self.user_id,
            chat_id=chat_id,
            action="user_unmuted",
            target_tg_id=target_id,
            target_username=target_username,
            performed_by=PerformedBy.ADMIN_MANUAL,
            performed_by_tg_id=admin.id,
        )
        
        await message.answer(f"🔊 {target_name} has been unmuted.")

    async def handle_ban(self, message: Message, command: CommandObject) -> None:
        """Ban a user."""
        if not await self._is_admin(message):
            return
        
        target = await self._get_target_user(message)
        if not target:
            await message.answer("❌ Reply to a message to ban the user.")
            return
        
        target_id, target_name, target_username = target
        chat_id = message.chat.id
        admin = cast(User, message.from_user)
        reason = command.args if command.args else "Manual ban by admin"
        
        await self.bot.ban_chat_member(chat_id, target_id)
        
        await self.service.log_moderation_action(
            user_id=self.user_id,
            chat_id=chat_id,
            action="user_banned",
            target_tg_id=target_id,
            target_username=target_username,
            performed_by=PerformedBy.ADMIN_MANUAL,
            performed_by_tg_id=admin.id,
            reason=reason,
        )
        
        await message.answer(f"🚫 {target_name} has been banned.\nReason: {reason}")

    async def handle_unban(self, message: Message) -> None:
        """Unban a user (by ID in command args)."""
        if not await self._is_admin(message):
            return
        
        # For unban, we need user ID since they're not in chat
        # This would need to be passed as argument
        await message.answer(
            "To unban a user, use the chat settings or provide user ID.\n"
            "Usage: /unban <user_id>"
        )

    # ===========================================
    # Banned Words Commands
    # ===========================================

    async def handle_addword(self, message: Message, command: CommandObject) -> None:
        """Add a banned word."""
        if not await self._is_admin(message):
            return
        
        if not command.args:
            await message.answer("Usage: /addword <word or phrase>")
            return
        
        word = command.args.strip()
        chat_id = message.chat.id
        
        banned_word = await self.service.add_banned_word(
            user_id=self.user_id,
            word=word,
            chat_id=chat_id,
        )
        
        await message.answer(f"✅ Added banned word: {word}")

    async def handle_delword(self, message: Message, command: CommandObject) -> None:
        """Remove a banned word."""
        if not await self._is_admin(message):
            return
        
        if not command.args:
            await message.answer("Usage: /delword <word_id or word>")
            return
        
        # This is simplified - in practice you'd look up by word text
        await message.answer("Use /words to see word IDs, then /delword <id>")

    async def handle_words(self, message: Message) -> None:
        """List banned words."""
        if not await self._is_admin(message):
            return
        
        chat_id = message.chat.id
        words = await self.service.get_banned_words(self.user_id, chat_id)
        
        if not words:
            await message.answer("📝 No banned words configured.")
            return
        
        text = "📝 <b>Banned Words</b>\n\n"
        for w in words:
            scope = "Global" if w.chat_id is None else "This chat"
            text += f"• {w.word} ({w.action.value}) - {scope}\n"
        
        await message.answer(text, parse_mode="HTML")

    # ===========================================
    # Welcome Message Commands
    # ===========================================

    async def handle_setwelcome(self, message: Message, command: CommandObject) -> None:
        """Set welcome message."""
        if not await self._is_admin(message):
            return
        
        if not command.args:
            await message.answer(
                "Usage: /setwelcome <message>\n\n"
                "<b>Placeholders:</b>\n"
                "{name} - User's name\n"
                "{username} - User's @username\n"
                "{mention} - Clickable mention\n"
                "{chat} - Chat title\n"
                "{count} - Member count"
            , parse_mode="HTML")
            return
        
        chat_id = message.chat.id
        welcome_text = command.args
        
        await self.service.set_welcome_message(
            user_id=self.user_id,
            chat_id=chat_id,
            message_text=welcome_text,
            message_type=MessageType.WELCOME,
        )
        
        await message.answer("✅ Welcome message set!")

    async def handle_setgoodbye(self, message: Message, command: CommandObject) -> None:
        """Set goodbye message."""
        if not await self._is_admin(message):
            return
        
        if not command.args:
            await message.answer("Usage: /setgoodbye <message>")
            return
        
        chat_id = message.chat.id
        goodbye_text = command.args
        
        await self.service.set_welcome_message(
            user_id=self.user_id,
            chat_id=chat_id,
            message_text=goodbye_text,
            message_type=MessageType.GOODBYE,
        )
        
        await message.answer("✅ Goodbye message set!")

    # ===========================================
    # Invite Statistics Commands
    # ===========================================

    async def handle_invites(self, message: Message) -> None:
        """Show invite statistics."""
        if not await self._is_admin(message):
            return
        
        chat_id = message.chat.id
        stats = await self.service.get_invite_stats(self.user_id, chat_id)
        
        if not stats:
            await message.answer("📊 No invite data available yet.")
            return
        
        text = "📊 <b>Invite Statistics</b>\n\n"
        for i, s in enumerate(stats[:20], 1):  # Top 20
            name = s.inviter_username or s.inviter_name or str(s.inviter_tg_id)
            text += (
                f"{i}. {name}\n"
                f"   Invited: {s.total_invited} | "
                f"Active: {s.still_members} | "
                f"Left: {s.left_count}\n"
            )
        
        await message.answer(text, parse_mode="HTML")

    # ===========================================
    # Moderation Log Commands
    # ===========================================

    async def handle_modlog(self, message: Message) -> None:
        """Show recent moderation log."""
        if not await self._is_admin(message):
            return
        
        chat_id = message.chat.id
        logs = await self.service.get_moderation_log(
            self.user_id, chat_id, limit=20
        )
        
        if not logs:
            await message.answer("📋 No moderation actions recorded yet.")
            return
        
        text = "📋 <b>Recent Moderation Log</b>\n\n"
        for entry in logs:
            target = entry.target_username or str(entry.target_tg_id) or "N/A"
            time_str = entry.created_at.strftime("%m/%d %H:%M")
            text += f"• [{time_str}] {entry.action}\n"
            text += f"  Target: {target} | By: {entry.performed_by.value}\n"
        
        await message.answer(text, parse_mode="HTML")


# Factory function
def create_admin_handler(bot: Bot, user_id: int, service: Any) -> AdminCommandHandler:
    """Create an admin command handler."""
    return AdminCommandHandler(bot, user_id, service)
