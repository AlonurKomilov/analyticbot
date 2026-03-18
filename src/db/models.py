"""Database models for Analyticbot v2"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AnalysisRequest(Base):
    """Tracks each analysis request from a user."""

    __tablename__ = "analysis_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_identifier: Mapped[str] = mapped_column(String(255), index=True)
    channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    channel_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    requested_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="bot")  # "bot" or "web"
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/running/done/failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ChannelSnapshot(Base):
    """Point-in-time snapshot of channel metadata at analysis time."""

    __tablename__ = "channel_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[int] = mapped_column(Integer, index=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, index=True)
    title: Mapped[str] = mapped_column(String(500))
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    member_count: Mapped[int] = mapped_column(Integer, default=0)
    channel_type: Mapped[str] = mapped_column(String(20))  # "channel" or "supergroup"
    fetched_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PostRecord(Base):
    """Individual post fetched during analysis."""

    __tablename__ = "post_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[int] = mapped_column(Integer, index=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, index=True)
    message_id: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime] = mapped_column(DateTime)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    forwards: Mapped[int] = mapped_column(Integer, default=0)
    replies: Mapped[int] = mapped_column(Integer, default=0)
    reactions_count: Mapped[int] = mapped_column(Integer, default=0)
    media_type: Mapped[str | None] = mapped_column(String(30), nullable=True)  # photo/video/document/none
    has_link: Mapped[bool] = mapped_column(default=False)


class AnalysisResult(Base):
    """Computed analysis results (stored as JSON-friendly columns)."""

    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)

    # Summary metrics
    total_posts: Mapped[int] = mapped_column(Integer, default=0)
    total_views: Mapped[int] = mapped_column(BigInteger, default=0)
    total_forwards: Mapped[int] = mapped_column(Integer, default=0)
    total_reactions: Mapped[int] = mapped_column(Integer, default=0)
    avg_views: Mapped[float] = mapped_column(Float, default=0.0)
    avg_engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    member_count: Mapped[int] = mapped_column(Integer, default=0)

    # Posting patterns
    avg_posts_per_day: Mapped[float] = mapped_column(Float, default=0.0)
    most_active_hour: Mapped[int | None] = mapped_column(Integer, nullable=True)
    most_active_weekday: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Content mix (percentages)
    pct_text_only: Mapped[float] = mapped_column(Float, default=0.0)
    pct_photo: Mapped[float] = mapped_column(Float, default=0.0)
    pct_video: Mapped[float] = mapped_column(Float, default=0.0)

    # Report file path
    report_pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    computed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
