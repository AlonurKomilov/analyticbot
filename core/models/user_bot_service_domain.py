"""
User Bot Moderation Domain Models

Framework-agnostic domain models for user bot moderation features.
These models represent the core business logic concepts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# ===========================================
# Enums
# ===========================================


class ModerationAction(str, Enum):
    """Actions that can be taken on rule violations."""

    NONE = "none"
    DELETE = "delete"
    WARN = "warn"
    MUTE = "mute"
    KICK = "kick"
    BAN = "ban"


class WarningType(str, Enum):
    """Types of warnings."""

    SPAM = "spam"
    BANNED_WORD = "banned_word"
    FLOOD = "flood"
    LINK = "link"
    FORWARD = "forward"
    MANUAL = "manual"
    CAPTCHA_FAIL = "captcha_fail"


class ChatType(str, Enum):
    """Telegram chat types."""

    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


class MessageType(str, Enum):
    """Welcome/goodbye message types."""

    WELCOME = "welcome"
    GOODBYE = "goodbye"
    RULES = "rules"


class PerformedBy(str, Enum):
    """Who performed the moderation action."""

    BOT_AUTO = "bot_auto"
    ADMIN_MANUAL = "admin_manual"
    SYSTEM = "system"


# ===========================================
# Domain Models
# ===========================================


@dataclass
class ChatSettings:
    """Settings for a specific chat/channel managed by user's bot."""

    id: int | None = None
    user_id: int = 0  # Bot owner
    chat_id: int = 0  # Telegram chat ID
    chat_type: ChatType = ChatType.GROUP
    chat_title: str | None = None

    # Feature toggles
    clean_join_messages: bool = False
    clean_leave_messages: bool = False
    banned_words_enabled: bool = False
    anti_spam_enabled: bool = False
    anti_link_enabled: bool = False
    anti_forward_enabled: bool = False
    welcome_enabled: bool = False
    invite_tracking_enabled: bool = False
    captcha_enabled: bool = False
    slow_mode_enabled: bool = False
    night_mode_enabled: bool = False

    # Anti-spam settings
    spam_action: ModerationAction = ModerationAction.WARN
    max_warnings: int = 3
    warning_action: ModerationAction = ModerationAction.MUTE
    mute_duration_minutes: int = 60

    # Anti-flood settings
    flood_limit: int = 5
    flood_interval_seconds: int = 10

    # Night mode settings
    night_mode_start_hour: int | None = None
    night_mode_end_hour: int | None = None
    night_mode_timezone: str = "UTC"

    # Permissions
    whitelisted_users: list[int] = field(default_factory=list)
    admin_users: list[int] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def is_user_whitelisted(self, tg_user_id: int) -> bool:
        """Check if user is whitelisted from moderation."""
        return tg_user_id in self.whitelisted_users

    def is_user_admin(self, tg_user_id: int) -> bool:
        """Check if user has admin permissions."""
        return tg_user_id in self.admin_users

    def should_clean_service_messages(self) -> bool:
        """Check if any service message cleaning is enabled."""
        return self.clean_join_messages or self.clean_leave_messages


@dataclass
class BannedWord:
    """A banned word/phrase configuration."""

    id: int | None = None
    user_id: int = 0
    chat_id: int | None = None  # None = applies to all chats
    word: str = ""
    is_regex: bool = False
    action: ModerationAction = ModerationAction.DELETE
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    def matches(self, text: str) -> bool:
        """Check if text contains this banned word."""
        import re

        if not self.is_active or not text:
            return False

        text_lower = text.lower()
        word_lower = self.word.lower()

        if self.is_regex:
            try:
                return bool(re.search(self.word, text, re.IGNORECASE))
            except re.error:
                return False
        else:
            # Simple word boundary match
            return word_lower in text_lower


@dataclass
class InviteRecord:
    """Record of who invited whom to a chat."""

    id: int | None = None
    user_id: int = 0  # Bot owner
    chat_id: int = 0

    # Inviter info
    inviter_tg_id: int = 0
    inviter_username: str | None = None
    inviter_name: str | None = None

    # Invited user info
    invited_tg_id: int = 0
    invited_username: str | None = None
    invited_name: str | None = None

    invite_link: str | None = None
    joined_at: datetime = field(default_factory=datetime.now)
    left_at: datetime | None = None
    is_still_member: bool = True

    def mark_left(self) -> None:
        """Mark user as having left the chat."""
        self.left_at = datetime.now()
        self.is_still_member = False


@dataclass
class InviteStats:
    """Statistics for an inviter."""

    inviter_tg_id: int
    inviter_username: str | None
    inviter_name: str | None
    total_invited: int = 0
    still_members: int = 0
    left_count: int = 0

    @property
    def retention_rate(self) -> float:
        """Calculate retention rate as percentage."""
        if self.total_invited == 0:
            return 0.0
        return (self.still_members / self.total_invited) * 100


@dataclass
class Warning:
    """A warning issued to a user."""

    id: int | None = None
    user_id: int = 0  # Bot owner
    chat_id: int = 0

    # Warned user info
    warned_tg_id: int = 0
    warned_username: str | None = None
    warned_name: str | None = None

    reason: str = ""
    warning_type: WarningType = WarningType.MANUAL
    message_id: int | None = None
    message_text: str | None = None
    action_taken: ModerationAction | None = None

    is_active: bool = True
    expires_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)
    created_by_tg_id: int | None = None  # Admin who issued

    def is_expired(self) -> bool:
        """Check if warning has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def deactivate(self) -> None:
        """Deactivate/remove this warning."""
        self.is_active = False


@dataclass
class ModerationLogEntry:
    """Log entry for a moderation action."""

    id: int | None = None
    user_id: int = 0  # Bot owner
    chat_id: int = 0
    action: str = ""  # message_deleted, user_warned, etc.

    target_tg_id: int | None = None
    target_username: str | None = None

    performed_by: PerformedBy = PerformedBy.BOT_AUTO
    performed_by_tg_id: int | None = None

    reason: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    message_id: int | None = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WelcomeMessage:
    """Custom welcome/goodbye message template."""

    id: int | None = None
    user_id: int = 0
    chat_id: int = 0
    message_type: MessageType = MessageType.WELCOME
    message_text: str = ""
    parse_mode: str = "HTML"
    buttons: list[dict] | None = None  # Inline keyboard buttons
    media_type: str | None = None  # photo, video, animation, sticker
    media_file_id: str | None = None
    delete_after_seconds: int | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def format_message(
        self,
        user_name: str,
        user_username: str | None,
        user_id: int,
        chat_title: str,
        member_count: int | None = None,
    ) -> str:
        """
        Format message with placeholders replaced.

        Supported placeholders:
        - {name} - User's first name
        - {username} - User's @username (or name if no username)
        - {user_id} - User's Telegram ID
        - {chat} - Chat title
        - {count} - Member count
        - {mention} - User mention link
        """
        text = self.message_text

        username_display = f"@{user_username}" if user_username else user_name
        mention = f'<a href="tg://user?id={user_id}">{user_name}</a>'

        replacements = {
            "{name}": user_name,
            "{username}": username_display,
            "{user_id}": str(user_id),
            "{chat}": chat_title,
            "{count}": str(member_count) if member_count else "N/A",
            "{mention}": mention,
        }

        for placeholder, value in replacements.items():
            text = text.replace(placeholder, value)

        return text


# ===========================================
# Detection Results
# ===========================================


@dataclass
class SpamDetectionResult:
    """Result of spam detection analysis."""

    is_spam: bool = False
    confidence: float = 0.0
    reasons: list[str] = field(default_factory=list)
    matched_patterns: list[str] = field(default_factory=list)
    link_count: int = 0
    forward_detected: bool = False

    @property
    def should_act(self) -> bool:
        """Whether action should be taken based on confidence."""
        return self.is_spam and self.confidence >= 0.7


@dataclass
class FloodDetectionResult:
    """Result of flood detection."""

    is_flooding: bool = False
    message_count: int = 0
    time_window_seconds: int = 0
    messages_per_second: float = 0.0


@dataclass
class ModerationCheckResult:
    """Combined result of all moderation checks."""

    should_delete: bool = False
    should_warn: bool = False
    action: ModerationAction = ModerationAction.NONE

    # What triggered the action
    banned_word_match: BannedWord | None = None
    spam_result: SpamDetectionResult | None = None
    flood_result: FloodDetectionResult | None = None

    # Generated warning if applicable
    warning: Warning | None = None

    # Message to send to user (if any)
    user_message: str | None = None

    @property
    def triggered(self) -> bool:
        """Whether any moderation rule was triggered."""
        return self.should_delete or self.should_warn or self.action != ModerationAction.NONE
