"""
User AI ORM Models
==================

SQLAlchemy ORM models for User AI system including:
- AI Configuration per user (tier, settings)
- AI Usage tracking (daily/hourly quotas)
- AI Services subscriptions (marketplace integration)
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.models.base import Base

# =============================================================================
# USER AI CONFIGURATION
# =============================================================================


class UserAIConfigORM(Base):
    """
    Per-user AI configuration and tier.

    Stores:
    - AI tier (free, basic, pro, enterprise)
    - Enabled features
    - Model preferences
    - Settings/preferences
    """

    __tablename__ = "user_ai_config"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Tier and status
    tier: Mapped[str] = mapped_column(String(20), server_default="free", nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    # Settings (stored as JSONB for flexibility)
    settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Model preferences
    preferred_model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    temperature: Mapped[float] = mapped_column(Float, server_default="0.7", nullable=False)

    # Feature toggles (list of enabled features)
    enabled_features: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Communication preferences
    language: Mapped[str] = mapped_column(String(10), server_default="en", nullable=False)
    response_style: Mapped[str] = mapped_column(
        String(20), server_default="professional", nullable=False
    )

    # Notification preferences
    auto_insights_enabled: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    auto_insights_frequency: Mapped[str] = mapped_column(
        String(20), server_default="daily", nullable=False
    )

    # Privacy
    data_retention_days: Mapped[int] = mapped_column(Integer, server_default="30", nullable=False)
    anonymize_data: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        Index("ix_user_ai_config_tier", "tier"),
        Index("ix_user_ai_config_enabled", "enabled"),
    )


# =============================================================================
# USER AI USAGE TRACKING
# =============================================================================


class UserAIUsageORM(Base):
    """
    Daily AI usage tracking per user.

    Tracks:
    - Request counts (daily)
    - Token consumption
    - Feature usage breakdown
    """

    __tablename__ = "user_ai_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Date for this usage record
    usage_date: Mapped[datetime] = mapped_column(Date, nullable=False)

    # Request counts
    requests_count: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    # Token usage
    tokens_used: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    # Feature usage breakdown (JSONB for flexibility)
    # Example: {"analytics_insights": 5, "content_suggestions": 3}
    features_used: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Cost tracking (if applicable)
    estimated_cost: Mapped[float] = mapped_column(Float, server_default="0.0", nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "usage_date", name="uq_user_ai_usage_user_date"),
        Index("ix_user_ai_usage_user_id", "user_id"),
        Index("ix_user_ai_usage_date", "usage_date"),
        Index("ix_user_ai_usage_user_date", "user_id", "usage_date"),
    )


# =============================================================================
# USER AI HOURLY USAGE (for rate limiting)
# =============================================================================


class UserAIHourlyUsageORM(Base):
    """
    Hourly AI usage tracking for rate limiting.

    Separate table for faster queries and automatic cleanup.
    Records older than 24 hours can be deleted.
    """

    __tablename__ = "user_ai_hourly_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Hour timestamp (rounded to hour)
    hour_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Request count for this hour
    requests_count: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "hour_timestamp", name="uq_user_ai_hourly_user_hour"),
        Index("ix_user_ai_hourly_user_id", "user_id"),
        Index("ix_user_ai_hourly_timestamp", "hour_timestamp"),
    )


# =============================================================================
# USER AI SERVICES (Marketplace integration)
# =============================================================================


class UserAIServiceORM(Base):
    """
    User's active AI marketplace services.

    Links users to marketplace AI services they've purchased/activated.
    """

    __tablename__ = "user_ai_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Service key (matches marketplace_services.service_key)
    service_key: Mapped[str] = mapped_column(String(100), nullable=False)

    # Service status
    enabled: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    # Subscription details
    activated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Service-specific configuration (JSONB for flexibility)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Usage tracking for this service
    usage_count: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Link to marketplace subscription (if applicable)
    subscription_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("user_subscriptions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "service_key", name="uq_user_ai_service_user_key"),
        Index("ix_user_ai_service_user_id", "user_id"),
        Index("ix_user_ai_service_key", "service_key"),
        Index("ix_user_ai_service_enabled", "enabled"),
        Index("ix_user_ai_service_expires", "expires_at"),
    )


# =============================================================================
# AI REQUEST LOG (for debugging and analytics)
# =============================================================================


class AIRequestLogORM(Base):
    """
    Detailed log of AI requests for debugging and analytics.

    Can be used for:
    - Debugging failed requests
    - Cost analysis
    - Usage patterns
    - Quality monitoring
    """

    __tablename__ = "ai_request_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Request details
    request_type: Mapped[str] = mapped_column(String(50), nullable=False)  # analyze, suggest, etc.
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)

    # Request parameters (sanitized)
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Response details
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI Model used
    model_used: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Token usage
    prompt_tokens: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    # Timing
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    # Cost (estimated)
    estimated_cost: Mapped[float] = mapped_column(Float, server_default="0.0", nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_ai_request_log_user_id", "user_id"),
        Index("ix_ai_request_log_created_at", "created_at"),
        Index("ix_ai_request_log_type", "request_type"),
        Index("ix_ai_request_log_success", "success"),
    )
