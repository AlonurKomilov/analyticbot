"""
Credit System ORM Models
========================

SQLAlchemy ORM models for the credit/economy system including:
- User credit balances
- Credit transactions
- Purchasable packages
- Per-use credit services
- Achievements and gamification
- Referral tracking
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.models.base import Base

# =============================================================================
# USER CREDITS
# =============================================================================


class UserCreditsORM(Base):
    """
    Extended user credit balance information.

    Tracks balance, lifetime stats, and daily rewards streak.
    """

    __tablename__ = "user_credits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Balances
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0", nullable=False)
    lifetime_earned: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), server_default="0", nullable=False
    )
    lifetime_spent: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), server_default="0", nullable=False
    )

    # Daily rewards
    daily_streak: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    last_daily_reward_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (Index("ix_user_credits_user_id", "user_id", unique=True),)


class CreditTransactionORM(Base):
    """
    Credit transaction history.

    Types: purchase, reward, spend, bonus, referral, adjustment
    Categories: signup, daily, referral, purchase, admin, achievement
    """

    __tablename__ = "credit_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Transaction details
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # External reference
    reference_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_credit_transactions_user_id", "user_id"),
        Index("ix_credit_transactions_type", "type"),
        Index("ix_credit_transactions_created_at", "created_at"),
        Index("ix_credit_transactions_user_created", "user_id", "created_at"),
    )


# =============================================================================
# CREDIT PACKAGES
# =============================================================================


class CreditPackageORM(Base):
    """
    Purchasable credit packages.

    Users can buy these packages with real money to get credits.
    """

    __tablename__ = "credit_packages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    # Credits
    credits: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    bonus_credits: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), server_default="0", nullable=False
    )

    # Pricing
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), server_default="USD", nullable=False)

    # Display
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_popular: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    # Payment provider
    stripe_price_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_credit_packages_slug", "slug", unique=True),
        Index("ix_credit_packages_active", "is_active"),
    )


class CreditServiceORM(Base):
    """
    Per-use credit services.

    These are one-time credit costs (not subscriptions).
    Examples: AI analysis, data export, premium report
    """

    __tablename__ = "credit_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_key: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Cost
    credit_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Display
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    # Requirements
    min_tier: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_credit_services_key", "service_key", unique=True),
        Index("ix_credit_services_active", "is_active"),
    )


# =============================================================================
# ACHIEVEMENTS
# =============================================================================


class AchievementORM(Base):
    """
    Achievement definitions.

    Gamification system with unlockable achievements.
    """

    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    achievement_key: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Reward
    credit_reward: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), server_default="0", nullable=False
    )

    # Categorization
    category: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # engagement, milestone, etc.

    # Requirements
    requirement_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # action, count, date
    requirement_value: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Display
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    is_secret: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)

    __table_args__ = (
        Index("ix_achievements_key", "achievement_key", unique=True),
        Index("ix_achievements_category", "category"),
    )


class UserAchievementORM(Base):
    """User's earned achievements."""

    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    achievement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False
    )

    # Progress (for count-based achievements)
    progress: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    # Completion
    earned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reward_claimed: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_user_achievements_user", "user_id"),
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )


# =============================================================================
# REFERRALS
# =============================================================================


class UserReferralORM(Base):
    """Referral tracking for credit rewards."""

    __tablename__ = "user_referrals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    referrer_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    referred_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Referral code used
    referral_code: Mapped[str] = mapped_column(String(20), nullable=False)

    # Reward status
    reward_paid_referrer: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    reward_paid_referred: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_user_referrals_referrer", "referrer_user_id"),
        Index("ix_user_referrals_referred", "referred_user_id", unique=True),
    )
