"""
Analytics ORM Models
====================

SQLAlchemy ORM models for analytics system including:
- Channels
- Posts
- Post metrics (time-series)
- Raw statistics
- Daily aggregates
- Stats cache
"""

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.models.base import Base

# =============================================================================
# CHANNELS
# =============================================================================


class ChannelORM(Base):
    """
    Telegram channels tracked by users.

    Each user can have multiple channels they're monitoring.
    """

    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Channel info
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Stats
    subscriber_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("ix_channels_user_id", "user_id"),
        Index("ix_channels_username", "username"),
    )


# =============================================================================
# POSTS
# =============================================================================


class PostORM(Base):
    """
    Telegram messages/posts collected via MTProto.

    Primary key is composite: (channel_id, msg_id)
    """

    __tablename__ = "posts"

    channel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    msg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # Content
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )

    __table_args__ = (
        Index("idx_posts_channel_date", "channel_id", "date"),
        Index("idx_posts_date", "date"),
    )


class PostMetricsORM(Base):
    """
    Time-series metrics for posts.

    Captures engagement metrics at different points in time
    to track growth and trends.
    """

    __tablename__ = "post_metrics"

    channel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    msg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    snapshot_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)

    # Metrics
    views: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    forwards: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    replies_count: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    reactions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reactions_count: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    __table_args__ = (
        Index("idx_post_metrics_channel_msg", "channel_id", "msg_id"),
        Index("idx_post_metrics_snapshot_time", "snapshot_time"),
    )


# =============================================================================
# RAW STATS
# =============================================================================


class StatsRawORM(Base):
    """
    Raw statistics from Telegram API.

    Stores JSON responses from stat endpoints for later processing.
    """

    __tablename__ = "stats_raw"

    channel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    key: Mapped[str] = mapped_column(Text, primary_key=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, server_default="NOW()"
    )

    # Raw JSON data
    json: Mapped[dict] = mapped_column(JSONB, nullable=False)


class ChannelDailyORM(Base):
    """
    Daily aggregated channel metrics.

    Pre-computed daily stats for fast dashboard queries.
    """

    __tablename__ = "channel_daily"

    channel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    day: Mapped[date] = mapped_column(Date, primary_key=True)
    metric: Mapped[str] = mapped_column(Text, primary_key=True)

    # Value
    value: Mapped[int] = mapped_column(BigInteger, nullable=False)


class ChannelStatsCacheORM(Base):
    """
    Cached channel statistics for fast API responses.

    Periodically refreshed to avoid expensive queries.
    """

    __tablename__ = "channel_stats_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Cached stats
    stats_json: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Cache metadata
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="NOW()", nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("ix_channel_stats_cache_channel", "channel_id", unique=True),
        Index("ix_channel_stats_cache_user", "user_id"),
        Index("ix_channel_stats_cache_expires", "expires_at"),
    )
