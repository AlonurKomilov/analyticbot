"""
Marketplace ORM Models
======================

SQLAlchemy ORM models for the marketplace system including:
- Services (subscription-based products)
- User subscriptions
- Usage tracking
- Items (one-time purchases)
- Reviews
- Bundles
- Categories
"""

from datetime import datetime

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
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.models.base import Base

# =============================================================================
# MARKETPLACE CATEGORIES
# =============================================================================


class MarketplaceCategoryORM(Base):
    """Categories for organizing marketplace services and items."""

    __tablename__ = "marketplace_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )


# =============================================================================
# MARKETPLACE SERVICES (Subscriptions)
# =============================================================================


class MarketplaceServiceORM(Base):
    """
    Marketplace services - subscription-based products.

    Examples: anti-spam service, auto-delete, MTProto history access, AI services
    """

    __tablename__ = "marketplace_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    short_description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Pricing
    price_credits_monthly: Mapped[int] = mapped_column(Integer, nullable=False)
    price_credits_yearly: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Categorization
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    subcategory: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Features & Limits
    features: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    usage_quota_daily: Mapped[int | None] = mapped_column(Integer, nullable=True)
    usage_quota_monthly: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rate_limit_per_minute: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Requirements
    requires_bot: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    requires_mtproto: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    min_tier: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Display
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    is_popular: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    is_new: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    is_beta: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)

    # Metadata
    documentation_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    demo_video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    # Stats
    active_subscriptions: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    total_subscriptions: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    # Relationships
    subscriptions: Mapped[list["UserServiceSubscriptionORM"]] = relationship(
        "UserServiceSubscriptionORM", back_populates="service"
    )

    __table_args__ = (
        Index("ix_marketplace_services_key", "service_key", unique=True),
        Index("ix_marketplace_services_category", "category"),
        Index("ix_marketplace_services_active", "is_active"),
    )


class UserServiceSubscriptionORM(Base):
    """
    User subscriptions to marketplace services.

    Tracks which services each user has subscribed to,
    with billing cycle, quota usage, and auto-renewal settings.
    """

    __tablename__ = "user_service_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    service_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("marketplace_services.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Subscription details
    billing_cycle: Mapped[str] = mapped_column(String(20), nullable=False)  # monthly, yearly
    price_paid: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), server_default="active", nullable=False
    )  # active, paused, cancelled, expired

    # Dates
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_renewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Auto-renewal
    auto_renew: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    renewal_attempts: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    last_renewal_attempt: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Usage tracking
    usage_count_daily: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    usage_count_monthly: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    usage_reset_daily: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    usage_reset_monthly: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Metadata
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    # Relationships
    service: Mapped["MarketplaceServiceORM"] = relationship(
        "MarketplaceServiceORM", back_populates="subscriptions"
    )

    __table_args__ = (
        Index("ix_user_service_subscriptions_user", "user_id"),
        Index("ix_user_service_subscriptions_service", "service_id"),
        Index("ix_user_service_subscriptions_status", "status"),
        Index("ix_user_service_subscriptions_expires", "expires_at"),
        Index("ix_user_service_subscriptions_active", "user_id", "status"),
    )


class ServiceUsageLogORM(Base):
    """
    Service usage log for quota enforcement and billing.

    Tracks every service usage action for:
    - Quota enforcement (daily/monthly limits)
    - Usage analytics
    - Billing verification
    """

    __tablename__ = "service_usage_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    subscription_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_service_subscriptions.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    service_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("marketplace_services.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Usage details
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, server_default="1", nullable=False)

    # Result
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Performance
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Metadata
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_service_usage_log_subscription", "subscription_id"),
        Index("ix_service_usage_log_user", "user_id"),
        Index("ix_service_usage_log_service", "service_id"),
        Index("ix_service_usage_log_created", "created_at"),
        Index("ix_service_usage_log_quota_check", "user_id", "service_id", "created_at"),
    )


# =============================================================================
# MARKETPLACE ITEMS (One-time purchases)
# =============================================================================


class MarketplaceItemORM(Base):
    """
    Marketplace items - one-time purchase products.

    Examples: themes, widgets, templates, AI model packs
    """

    __tablename__ = "marketplace_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Categorization
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    subcategory: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Pricing
    price_credits: Mapped[int] = mapped_column(Integer, nullable=False)

    # Display
    is_premium: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    preview_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    icon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Metadata
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    # Stats
    download_count: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    rating: Mapped[float] = mapped_column(Numeric(3, 2), server_default="0", nullable=False)
    rating_count: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_marketplace_items_slug", "slug", unique=True),
        Index("ix_marketplace_items_category", "category"),
        Index("ix_marketplace_items_featured", "is_featured"),
    )


class UserPurchaseORM(Base):
    """User purchases of marketplace items."""

    __tablename__ = "user_purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("marketplace_items.id", ondelete="RESTRICT"), nullable=False
    )

    # Purchase details
    price_paid: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # completed, refunded

    # Gift info (if gifted)
    gifted_by_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    gift_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    purchased_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_user_purchases_user", "user_id"),
        Index("ix_user_purchases_item", "item_id"),
    )


class ItemReviewORM(Base):
    """Reviews for marketplace items."""

    __tablename__ = "item_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("marketplace_items.id", ondelete="CASCADE"), nullable=False
    )

    # Review content
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    review_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Moderation
    is_verified_purchase: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )
    is_approved: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_item_reviews_item", "item_id"),
        Index("ix_item_reviews_user_item", "user_id", "item_id", unique=True),
    )


# =============================================================================
# BUNDLES
# =============================================================================


class MarketplaceBundleORM(Base):
    """Bundles - collections of items/services at discounted price."""

    __tablename__ = "marketplace_bundles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Pricing
    price_credits: Mapped[int] = mapped_column(Integer, nullable=False)
    original_price: Mapped[int] = mapped_column(Integer, nullable=False)  # Sum before discount

    # Display
    icon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    # Limited time
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_marketplace_bundles_slug", "slug", unique=True),
        Index("ix_marketplace_bundles_active", "is_active"),
    )


class BundleItemORM(Base):
    """Items included in a bundle."""

    __tablename__ = "bundle_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bundle_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("marketplace_bundles.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Can be either an item or a service
    item_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    service_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Service subscription duration (if service)
    service_months: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (Index("ix_bundle_items_bundle", "bundle_id"),)
