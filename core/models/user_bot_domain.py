"""
User Bot Credentials Domain Models
Multi-tenant bot system - each user has isolated bot credentials
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class BotStatus(str, Enum):
    """Bot credential status"""

    PENDING = "pending"  # Credentials added, not verified
    ACTIVE = "active"  # Bot is active and working
    INACTIVE = "inactive"  # Bot is inactive/not setup
    SUSPENDED = "suspended"  # Admin suspended
    RATE_LIMITED = "rate_limited"  # Hit rate limits
    ERROR = "error"  # Configuration error


@dataclass
class UserBotCredentials:
    """Domain model for user's bot credentials"""

    # Identity
    id: int | None
    user_id: int

    # Telegram Bot credentials
    bot_token: str
    bot_username: str | None = None
    bot_id: int | None = None

    # MTProto credentials (optional - for reading channel history)
    mtproto_id: int | None = None  # Telegram user ID from MTProto authentication
    mtproto_username: str | None = None  # Telegram username from MTProto authentication
    mtproto_api_id: int | None = None
    telegram_api_hash: str | None = None
    mtproto_phone: str | None = None
    session_string: str | None = None
    mtproto_enabled: bool = True  # Allow user to enable/disable MTProto functionality

    # Status
    status: BotStatus = BotStatus.PENDING
    is_verified: bool = False

    # Webhook configuration
    webhook_enabled: bool = False
    webhook_secret: str | None = None
    webhook_url: str | None = None
    last_webhook_update: datetime | None = None

    # Rate limiting
    rate_limit_rps: float = 1.0
    max_concurrent_requests: int = 3

    # Usage tracking
    total_requests: int = 0

    # Suspension
    suspension_reason: str | None = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_used_at: datetime | None = None

    def is_active(self) -> bool:
        """Check if bot is active and usable"""
        return self.status == BotStatus.ACTIVE and self.is_verified

    def can_make_request(self) -> bool:
        """Check if bot can make requests"""
        return self.status in [BotStatus.ACTIVE, BotStatus.PENDING]

    def mark_used(self) -> None:
        """Update last_used_at timestamp"""
        self.last_used_at = datetime.now()
        self.updated_at = datetime.now()

    def suspend(self, reason: str | None = None) -> None:
        """Suspend bot"""
        self.status = BotStatus.SUSPENDED
        self.suspension_reason = reason
        self.updated_at = datetime.now()

    def activate(self) -> None:
        """Activate bot"""
        self.status = BotStatus.ACTIVE
        self.is_verified = True
        self.suspension_reason = None
        self.updated_at = datetime.now()


@dataclass
class AdminBotAction:
    """Domain model for admin actions on user bots"""

    id: int
    admin_user_id: int
    target_user_id: int
    action: str
    details: dict | None = None
    timestamp: datetime = field(default_factory=datetime.now)
