"""
User Bot Credentials ORM Models
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.models.superadmin.superadmin_orm import Base


class UserBotCredentialsORM(Base):
    """ORM model for user bot credentials"""

    __tablename__ = "user_bot_credentials"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # User ID (foreign key constraint exists in database)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    # Telegram Bot credentials (bot_token is encrypted)
    bot_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    bot_username: Mapped[str | None] = mapped_column(String(255), unique=True)
    bot_id: Mapped[int | None] = mapped_column(BigInteger)

    # MTProto credentials (telegram_api_hash is encrypted) - Now optional
    telegram_api_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    telegram_api_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telegram_phone: Mapped[str | None] = mapped_column(String(20))
    session_string: Mapped[str | None] = mapped_column(Text)
    mtproto_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Rate limiting
    rate_limit_rps: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    max_concurrent_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Constraints
    __table_args__ = (UniqueConstraint("user_id", name="one_bot_per_user"),)


class AdminBotActionORM(Base):
    """ORM model for admin actions log"""

    __tablename__ = "admin_bot_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    admin_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    # Foreign key constraint exists in database
    target_user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[dict | None] = mapped_column(JSONB)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now, index=True
    )


class MTProtoAuditLog(Base):
    """ORM model for MTProto audit log"""

    __tablename__ = "mtproto_audit_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    # Foreign key constraint exists in database (see migration f7ffb0be449f)
    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True
    )
    channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    previous_state: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    new_state: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    event_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now, index=True
    )


class ChannelMTProtoSettings(Base):
    """ORM model for per-channel MTProto settings"""

    __tablename__ = "channel_mtproto_settings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    # Foreign key constraints exist in database (see migration 169d798b7035)
    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True
    )
    channel_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )
    mtproto_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now
    )

    __table_args__ = (
        UniqueConstraint("user_id", "channel_id", name="unique_user_channel_mtproto_setting"),
    )
