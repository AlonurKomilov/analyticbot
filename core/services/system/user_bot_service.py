"""
User Bot Moderation Service

Business logic for user bot moderation features:
- Message moderation (banned words, spam detection)
- Member management (join/leave cleaning, welcome messages)
- Invite tracking
- Warning system
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Any

from core.models.user_bot_service_domain import (
    BannedWord,
    ChatSettings,
    ChatType,
    FloodDetectionResult,
    InviteRecord,
    InviteStats,
    MessageType,
    ModerationAction,
    ModerationCheckResult,
    ModerationLogEntry,
    PerformedBy,
    SpamDetectionResult,
    Warning,
    WarningType,
    WelcomeMessage,
)
from infra.db.repositories.user_bot_service_repository import (
    UserBotServiceRepository,
)

logger = logging.getLogger(__name__)


class UserBotService:
    """
    Service for user bot moderation operations.

    Handles all moderation logic including:
    - Message checking (banned words, spam, links, forwards)
    - Member events (join/leave, welcome messages)
    - Invite tracking and statistics
    - Warning management
    - Action execution (delete, warn, mute, kick, ban)
    """

    def __init__(self, repository: UserBotServiceRepository):
        self.repository = repository

        # In-memory flood detection cache (per user per chat)
        # Key: (user_id, chat_id, sender_tg_id) -> list of message timestamps
        self._flood_cache: dict[tuple[int, int, int], list[datetime]] = {}

        # Spam detection patterns
        self._spam_patterns = [
            r"(https?://[^\s]+)",  # URLs
            r"@\w+",  # @mentions
            r"t\.me/\w+",  # Telegram links
            r"(earn|money|profit|income)\s*(now|fast|easy|today)",  # Money spam
            r"(click|join|subscribe)\s*(here|now|link)",  # Action spam
            r"(free|bonus|gift|prize)\s*(coin|token|crypto|money)",  # Crypto spam
            r"\b(DM|PM)\s*(me|for)\b",  # DM solicitation
        ]
        self._compiled_spam_patterns = [re.compile(p, re.IGNORECASE) for p in self._spam_patterns]

    # ===========================================
    # Settings Management
    # ===========================================

    async def get_settings(self, user_id: int, chat_id: int) -> ChatSettings | None:
        """Get moderation settings for a chat."""
        return await self.repository.get_chat_settings(user_id, chat_id)

    async def get_or_create_settings(
        self,
        user_id: int,
        chat_id: int,
        chat_type: ChatType = ChatType.GROUP,
        chat_title: str | None = None,
    ) -> ChatSettings:
        """Get or create default settings for a chat."""
        settings = await self.repository.get_chat_settings(user_id, chat_id)
        if settings:
            return settings

        # Create with defaults
        new_settings = ChatSettings(
            user_id=user_id,
            chat_id=chat_id,
            chat_type=chat_type,
            chat_title=chat_title,
        )
        return await self.repository.create_chat_settings(new_settings)

    async def update_settings(self, settings: ChatSettings) -> ChatSettings:
        """Update chat settings."""
        return await self.repository.upsert_chat_settings(settings)

    async def get_all_user_settings(self, user_id: int) -> list[ChatSettings]:
        """Get all chat settings for a user."""
        return await self.repository.get_user_chat_settings(user_id)

    # ===========================================
    # Message Moderation
    # ===========================================

    async def check_message(
        self,
        user_id: int,
        chat_id: int,
        sender_tg_id: int,
        message_text: str | None,
        is_forward: bool = False,
        has_links: bool = False,
        message_id: int | None = None,
    ) -> ModerationCheckResult:
        """
        Check a message against all moderation rules.

        Returns:
            ModerationCheckResult with actions to take
        """
        result = ModerationCheckResult()

        # Get settings
        settings = await self.repository.get_chat_settings(user_id, chat_id)
        if not settings:
            return result  # No settings = no moderation

        # Check if user is whitelisted
        if settings.is_user_whitelisted(sender_tg_id):
            return result

        # Check forward blocking
        if settings.anti_forward_enabled and is_forward:
            result.should_delete = True
            result.action = ModerationAction.DELETE
            result.user_message = "⚠️ Forwarded messages are not allowed in this chat."
            return result

        # Check link blocking
        if settings.anti_link_enabled and has_links:
            result.should_delete = True
            result.action = ModerationAction.DELETE
            result.user_message = "⚠️ Links are not allowed in this chat."
            return result

        if message_text:
            # Check banned words
            if settings.banned_words_enabled:
                banned_words = await self.repository.get_banned_words(user_id, chat_id)
                for word in banned_words:
                    if word.matches(message_text):
                        result.banned_word_match = word
                        result.should_delete = True
                        result.action = word.action

                        if word.action in [
                            ModerationAction.WARN,
                            ModerationAction.MUTE,
                            ModerationAction.KICK,
                            ModerationAction.BAN,
                        ]:
                            result.should_warn = True
                        break

            # Check spam patterns
            if settings.anti_spam_enabled and not result.banned_word_match:
                spam_result = self._detect_spam(message_text)
                if spam_result.should_act:
                    result.spam_result = spam_result
                    result.should_delete = True
                    result.action = settings.spam_action
                    result.should_warn = settings.spam_action != ModerationAction.DELETE

        # Check flood
        flood_result = self._check_flood(
            user_id,
            chat_id,
            sender_tg_id,
            settings.flood_limit,
            settings.flood_interval_seconds,
        )
        if flood_result.is_flooding:
            result.flood_result = flood_result
            result.should_delete = True
            result.action = ModerationAction.MUTE
            result.should_warn = True
            result.user_message = "⚠️ Slow down! You're sending messages too fast."

        return result

    def _detect_spam(self, text: str) -> SpamDetectionResult:
        """Detect spam patterns in text."""
        result = SpamDetectionResult()

        for pattern in self._compiled_spam_patterns:
            matches = pattern.findall(text)
            if matches:
                result.matched_patterns.append(pattern.pattern)
                result.reasons.append(f"Matched pattern: {pattern.pattern}")

        # Count links
        url_pattern = re.compile(r"https?://[^\s]+|t\.me/\w+", re.IGNORECASE)
        result.link_count = len(url_pattern.findall(text))

        # Calculate confidence
        if result.matched_patterns:
            base_confidence = min(len(result.matched_patterns) * 0.3, 0.9)
            link_boost = min(result.link_count * 0.1, 0.3)
            result.confidence = min(base_confidence + link_boost, 1.0)
            result.is_spam = result.confidence >= 0.5

        return result

    def _check_flood(
        self,
        user_id: int,
        chat_id: int,
        sender_tg_id: int,
        limit: int,
        interval_seconds: int,
    ) -> FloodDetectionResult:
        """Check if user is flooding."""
        key = (user_id, chat_id, sender_tg_id)
        now = datetime.now()
        cutoff = now - timedelta(seconds=interval_seconds)

        # Get/initialize message timestamps
        timestamps = self._flood_cache.get(key, [])

        # Remove old timestamps
        timestamps = [ts for ts in timestamps if ts > cutoff]

        # Add current message
        timestamps.append(now)
        self._flood_cache[key] = timestamps

        # Check flood
        result = FloodDetectionResult(
            message_count=len(timestamps),
            time_window_seconds=interval_seconds,
        )

        if len(timestamps) > limit:
            result.is_flooding = True
            result.messages_per_second = len(timestamps) / interval_seconds

        return result

    # ===========================================
    # Warning System
    # ===========================================

    async def warn_user(
        self,
        user_id: int,
        chat_id: int,
        warned_tg_id: int,
        warned_username: str | None,
        warned_name: str | None,
        reason: str,
        warning_type: WarningType,
        message_id: int | None = None,
        message_text: str | None = None,
        issued_by_tg_id: int | None = None,
    ) -> tuple[Warning, int, ModerationAction | None]:
        """
        Issue a warning to a user.

        Returns:
            Tuple of (Warning, total_warnings, action_to_take if max reached)
        """
        # Get settings for max warnings
        settings = await self.repository.get_chat_settings(user_id, chat_id)
        max_warnings = settings.max_warnings if settings else 3
        warning_action = settings.warning_action if settings else ModerationAction.MUTE

        # Create warning
        warning = Warning(
            user_id=user_id,
            chat_id=chat_id,
            warned_tg_id=warned_tg_id,
            warned_username=warned_username,
            warned_name=warned_name,
            reason=reason,
            warning_type=warning_type,
            message_id=message_id,
            message_text=message_text,
            created_by_tg_id=issued_by_tg_id,
        )

        saved_warning = await self.repository.add_warning(warning)

        # Get warning count
        total_warnings = await self.repository.get_warning_count(user_id, chat_id, warned_tg_id)

        # Check if max warnings reached
        action_to_take = None
        if total_warnings >= max_warnings:
            action_to_take = warning_action
            saved_warning.action_taken = warning_action

        return saved_warning, total_warnings, action_to_take

    async def get_user_warnings(
        self, user_id: int, chat_id: int, warned_tg_id: int
    ) -> list[Warning]:
        """Get all active warnings for a user."""
        return await self.repository.get_active_warnings(user_id, chat_id, warned_tg_id)

    async def clear_user_warnings(self, user_id: int, chat_id: int, warned_tg_id: int) -> int:
        """Clear all warnings for a user. Returns count cleared."""
        return await self.repository.clear_warnings(user_id, chat_id, warned_tg_id)

    # ===========================================
    # Banned Words
    # ===========================================

    async def add_banned_word(
        self,
        user_id: int,
        word: str,
        chat_id: int | None = None,
        is_regex: bool = False,
        action: ModerationAction = ModerationAction.DELETE,
    ) -> BannedWord:
        """Add a banned word."""
        banned_word = BannedWord(
            user_id=user_id,
            chat_id=chat_id,
            word=word,
            is_regex=is_regex,
            action=action,
        )
        return await self.repository.add_banned_word(banned_word)

    async def get_banned_words(self, user_id: int, chat_id: int | None = None) -> list[BannedWord]:
        """Get all banned words for user/chat."""
        return await self.repository.get_banned_words(user_id, chat_id)

    async def remove_banned_word(self, word_id: int) -> bool:
        """Remove a banned word."""
        return await self.repository.remove_banned_word(word_id)

    # ===========================================
    # Welcome Messages
    # ===========================================

    async def set_welcome_message(
        self,
        user_id: int,
        chat_id: int,
        message_text: str,
        message_type: MessageType = MessageType.WELCOME,
        parse_mode: str = "HTML",
        buttons: list[dict] | None = None,
        media_type: str | None = None,
        media_file_id: str | None = None,
        delete_after_seconds: int | None = None,
    ) -> WelcomeMessage:
        """Set welcome/goodbye message."""
        message = WelcomeMessage(
            user_id=user_id,
            chat_id=chat_id,
            message_type=message_type,
            message_text=message_text,
            parse_mode=parse_mode,
            buttons=buttons,
            media_type=media_type,
            media_file_id=media_file_id,
            delete_after_seconds=delete_after_seconds,
        )
        return await self.repository.set_welcome_message(message)

    async def get_welcome_message(
        self,
        user_id: int,
        chat_id: int,
        message_type: MessageType = MessageType.WELCOME,
    ) -> WelcomeMessage | None:
        """Get welcome message for a chat."""
        return await self.repository.get_welcome_message(user_id, chat_id, message_type)

    async def format_welcome_message(
        self,
        user_id: int,
        chat_id: int,
        new_member_name: str,
        new_member_username: str | None,
        new_member_id: int,
        chat_title: str,
        member_count: int | None = None,
        message_type: MessageType = MessageType.WELCOME,
    ) -> str | None:
        """Get formatted welcome message for a new member."""
        welcome = await self.get_welcome_message(user_id, chat_id, message_type)
        if not welcome:
            return None

        return welcome.format_message(
            user_name=new_member_name,
            user_username=new_member_username,
            user_id=new_member_id,
            chat_title=chat_title,
            member_count=member_count,
        )

    # ===========================================
    # Invite Tracking
    # ===========================================

    async def track_invite(
        self,
        user_id: int,
        chat_id: int,
        inviter_tg_id: int,
        inviter_username: str | None,
        inviter_name: str | None,
        invited_tg_id: int,
        invited_username: str | None,
        invited_name: str | None,
        invite_link: str | None = None,
    ) -> InviteRecord:
        """Track a new invite."""
        record = InviteRecord(
            user_id=user_id,
            chat_id=chat_id,
            inviter_tg_id=inviter_tg_id,
            inviter_username=inviter_username,
            inviter_name=inviter_name,
            invited_tg_id=invited_tg_id,
            invited_username=invited_username,
            invited_name=invited_name,
            invite_link=invite_link,
        )
        return await self.repository.track_invite(record)

    async def mark_member_left(self, user_id: int, chat_id: int, member_tg_id: int) -> bool:
        """Mark a member as having left."""
        return await self.repository.mark_user_left(user_id, chat_id, member_tg_id)

    async def get_invite_stats(self, user_id: int, chat_id: int) -> list[InviteStats]:
        """Get invite statistics for a chat."""
        return await self.repository.get_invite_stats(user_id, chat_id)

    async def get_inviter_details(
        self, user_id: int, chat_id: int, inviter_tg_id: int
    ) -> list[InviteRecord]:
        """Get all invites by a specific user."""
        return await self.repository.get_invites_by_inviter(user_id, chat_id, inviter_tg_id)

    # ===========================================
    # Moderation Log
    # ===========================================

    async def log_moderation_action(
        self,
        user_id: int,
        chat_id: int,
        action: str,
        target_tg_id: int | None = None,
        target_username: str | None = None,
        performed_by: PerformedBy = PerformedBy.BOT_AUTO,
        performed_by_tg_id: int | None = None,
        reason: str | None = None,
        details: dict[str, Any] | None = None,
        message_id: int | None = None,
    ) -> ModerationLogEntry:
        """Log a moderation action."""
        entry = ModerationLogEntry(
            user_id=user_id,
            chat_id=chat_id,
            action=action,
            target_tg_id=target_tg_id,
            target_username=target_username,
            performed_by=performed_by,
            performed_by_tg_id=performed_by_tg_id,
            reason=reason,
            details=details or {},
            message_id=message_id,
        )
        return await self.repository.log_action(entry)

    async def get_moderation_log(
        self,
        user_id: int,
        chat_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ModerationLogEntry]:
        """Get moderation log for a chat."""
        return await self.repository.get_moderation_log(user_id, chat_id, limit, offset)


def get_user_bot_service(
    repository: UserBotServiceRepository, bot_manager: Any = None
) -> UserBotService:
    """
    Get a user bot service instance.

    Args:
        repository: User bot service repository
        bot_manager: Multi-tenant bot manager (optional)

    Returns:
        UserBotService instance
    """
    return UserBotService(repository)
