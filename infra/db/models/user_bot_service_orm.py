"""
User Bot Moderation ORM Models

Database models for user bot moderation features:
- Settings per chat
- Banned words
- Invite tracking
- Warnings
- Moderation logs
- Welcome messages
"""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.models.base import Base


class UserBotSettingsORM(Base):
    """ORM model for user bot settings per chat."""

    __tablename__ = "user_bot_settings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chat_type: Mapped[str] = mapped_column(String(20), nullable=False, default="group")
    chat_title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Feature toggles
    clean_join_messages: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    clean_leave_messages: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    banned_words_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    anti_spam_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    anti_link_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    anti_forward_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    welcome_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    invite_tracking_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    captcha_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    slow_mode_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    night_mode_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )

    # Anti-spam settings
    spam_action: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="warn"
    )
    max_warnings: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="3"
    )
    warning_action: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="mute"
    )
    mute_duration_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="60"
    )

    # Anti-flood settings
    flood_limit: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="5"
    )
    flood_interval_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="10"
    )

    # Night mode settings
    night_mode_start_hour: Mapped[int | None] = mapped_column(Integer, nullable=True)
    night_mode_end_hour: Mapped[int | None] = mapped_column(Integer, nullable=True)
    night_mode_timezone: Mapped[str | None] = mapped_column(
        String(50), nullable=True, server_default="'UTC'"
    )

    # Allowed users/admins
    whitelisted_users: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    admin_users: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now
    )

    __table_args__ = (
        UniqueConstraint("user_id", "chat_id", name="unique_user_chat_settings"),
    )


class UserBotBannedWordORM(Base):
    """ORM model for banned words."""

    __tablename__ = "user_bot_banned_words"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    word: Mapped[str] = mapped_column(String(100), nullable=False)
    is_regex: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    action: Mapped[str] = mapped_column(String(20), nullable=False, server_default="delete")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now
    )

    __table_args__ = (
        Index("idx_banned_words_user_chat", "user_id", "chat_id"),
        Index("idx_banned_words_active", "user_id", "is_active"),
    )


class UserBotInviteTrackingORM(Base):
    """ORM model for invite tracking."""

    __tablename__ = "user_bot_invite_tracking"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    inviter_tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    inviter_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    inviter_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    invited_tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    invited_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    invited_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    invite_link: Mapped[str | None] = mapped_column(String(255), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now
    )
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_still_member: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )

    __table_args__ = (
        Index("idx_invite_tracking_inviter", "user_id", "chat_id", "inviter_tg_id"),
        Index("idx_invite_tracking_invited", "user_id", "chat_id", "invited_tg_id"),
        Index("idx_invite_stats", "user_id", "chat_id", "inviter_tg_id", "is_still_member"),
    )


class UserBotWarningORM(Base):
    """ORM model for user warnings."""

    __tablename__ = "user_bot_warnings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    warned_tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    warned_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    warned_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    warning_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    message_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_taken: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now
    )
    created_by_tg_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    __table_args__ = (
        Index("idx_warnings_chat_user", "user_id", "chat_id", "warned_tg_id"),
        Index("idx_warnings_active", "user_id", "chat_id", "is_active"),
    )


class UserBotServiceLogORM(Base):
    """ORM model for moderation action logs."""

    __tablename__ = "user_bot_moderation_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    target_tg_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    target_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    performed_by: Mapped[str] = mapped_column(String(50), nullable=False)
    performed_by_tg_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now, index=True
    )

    __table_args__ = (
        Index("idx_moderation_log_date_range", "user_id", "chat_id", "created_at"),
    )


class UserBotWelcomeMessageORM(Base):
    """ORM model for welcome messages."""

    __tablename__ = "user_bot_welcome_messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_type: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="'welcome'"
    )
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    parse_mode: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="'HTML'"
    )
    buttons: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    media_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    media_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delete_after_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "chat_id", "message_type", name="unique_user_chat_message_type"
        ),
    )
