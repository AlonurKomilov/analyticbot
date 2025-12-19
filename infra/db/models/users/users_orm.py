"""
Users ORM Models
================

SQLAlchemy ORM models for user management including:
- Users
- Plans
- Subscriptions
- Alert preferences
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.models.base import Base


# =============================================================================
# USERS
# =============================================================================

class UserORM(Base):
    """
    Application users (Telegram users who use the bot).
    
    Primary key is Telegram user ID.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Plan/tier
    plan_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("plans.id", ondelete="SET NULL"), nullable=True, server_default="1"
    )
    
    # Credits (denormalized from user_credits for quick access)
    credit_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0", nullable=False)
    
    # Referral
    referral_code: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    referred_by_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    
    # Role (5-tier: viewer < user < moderator < admin < owner)
    role: Mapped[str] = mapped_column(String(20), server_default="user", nullable=False)
    
    # Suspension
    is_suspended: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suspension_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_users_username", "username"),
        Index("ix_users_referral_code", "referral_code", unique=True),
        Index("ix_users_role", "role"),
    )


class PlanORM(Base):
    """
    Subscription plans (free, pro, enterprise, etc.).
    """

    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    
    # Limits
    max_channels: Mapped[int] = mapped_column(Integer, server_default="1", nullable=False)
    max_posts_per_month: Mapped[int] = mapped_column(Integer, server_default="30", nullable=False)


class SubscriptionORM(Base):
    """
    User subscriptions to plans (for paid plans).
    """

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("plans.id", ondelete="RESTRICT"), nullable=False
    )
    
    # Status
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # active, cancelled, expired
    
    # Dates
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Payment
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    __table_args__ = (
        Index("ix_subscriptions_user", "user_id"),
        Index("ix_subscriptions_status", "status"),
    )


# =============================================================================
# ALERTS
# =============================================================================

class UserAlertPreferenceORM(Base):
    """
    User's alert notification preferences.
    """

    __tablename__ = "user_alert_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    
    # Notification channels
    telegram_enabled: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    email_enabled: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    email_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Alert types
    performance_alerts: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    system_alerts: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    marketplace_alerts: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    
    # Quiet hours
    quiet_hours_enabled: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    quiet_start_hour: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quiet_end_hour: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), server_default="UTC", nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_user_alert_preferences_user", "user_id", unique=True),
    )


class AlertSentORM(Base):
    """
    Log of sent alerts (for deduplication and history).
    """

    __tablename__ = "alert_sent"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    
    # Alert details
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    alert_key: Mapped[str] = mapped_column(String(255), nullable=False)  # For deduplication
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Delivery
    channel: Mapped[str] = mapped_column(String(20), nullable=False)  # telegram, email
    delivered: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    
    # Metadata
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    
    # Timestamp
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_alert_sent_user", "user_id"),
        Index("ix_alert_sent_key", "user_id", "alert_key"),
        Index("ix_alert_sent_type", "alert_type"),
        Index("ix_alert_sent_time", "sent_at"),
    )
