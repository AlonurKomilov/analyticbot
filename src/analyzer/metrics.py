"""Metrics computation — takes fetched posts and produces analytics"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

from src.analyzer.fetcher import FetchResult, FetchedPost


@dataclass
class TopPost:
    message_id: int
    date: datetime
    views: int
    forwards: int
    reactions: int
    engagement_rate: float
    text_preview: str


@dataclass
class PostingPattern:
    avg_posts_per_day: float
    most_active_hour: int | None  # 0-23
    most_active_weekday: int | None  # 0=Mon, 6=Sun
    hour_distribution: dict[int, int] = field(default_factory=dict)  # hour → count
    weekday_distribution: dict[int, int] = field(default_factory=dict)  # weekday → count


@dataclass
class ContentMix:
    pct_text_only: float
    pct_photo: float
    pct_video: float
    pct_document: float
    pct_other: float


@dataclass
class AnalysisMetrics:
    """Complete analysis output."""

    # Channel info
    channel_title: str
    channel_username: str | None
    channel_type: str
    member_count: int
    description: str | None

    # Aggregate stats
    total_posts: int
    total_views: int
    total_forwards: int
    total_reactions: int
    avg_views: float
    avg_engagement_rate: float  # (views / member_count) averaged across posts
    avg_forwards_per_post: float
    avg_reactions_per_post: float

    # Patterns
    posting_pattern: PostingPattern
    content_mix: ContentMix

    # Top content
    top_posts_by_views: list[TopPost]
    top_posts_by_engagement: list[TopPost]

    # Time range covered
    date_from: datetime | None
    date_to: datetime | None
    analysis_period_days: int


def _text_preview(text: str | None, max_len: int = 80) -> str:
    if not text:
        return "(no text)"
    clean = text.replace("\n", " ").strip()
    if len(clean) > max_len:
        return clean[: max_len - 1] + "…"
    return clean


def _make_top_post(post: FetchedPost, member_count: int) -> TopPost:
    engagement = (post.views / member_count * 100) if member_count > 0 else 0.0
    return TopPost(
        message_id=post.message_id,
        date=post.date,
        views=post.views,
        forwards=post.forwards,
        reactions=post.reactions_count,
        engagement_rate=round(engagement, 2),
        text_preview=_text_preview(post.text),
    )


def compute_metrics(result: FetchResult, top_n: int = 10) -> AnalysisMetrics:
    """Compute all analytics from fetched channel data."""
    ch = result.channel
    posts = result.posts

    if not posts:
        return AnalysisMetrics(
            channel_title=ch.title,
            channel_username=ch.username,
            channel_type=ch.channel_type,
            member_count=ch.member_count,
            description=ch.description,
            total_posts=0,
            total_views=0,
            total_forwards=0,
            total_reactions=0,
            avg_views=0.0,
            avg_engagement_rate=0.0,
            avg_forwards_per_post=0.0,
            avg_reactions_per_post=0.0,
            posting_pattern=PostingPattern(0, None, None),
            content_mix=ContentMix(0, 0, 0, 0, 0),
            top_posts_by_views=[],
            top_posts_by_engagement=[],
            date_from=None,
            date_to=None,
            analysis_period_days=0,
        )

    n = len(posts)
    total_views = sum(p.views for p in posts)
    total_forwards = sum(p.forwards for p in posts)
    total_reactions = sum(p.reactions_count for p in posts)

    avg_views = total_views / n
    avg_engagement = (
        sum(p.views / ch.member_count for p in posts) / n * 100 if ch.member_count > 0 else 0.0
    )

    # ── Posting patterns ───────────────────────────────────────────────
    dates = sorted(p.date for p in posts)
    date_from, date_to = dates[0], dates[-1]
    span_days = max((date_to - date_from).days, 1)
    avg_posts_per_day = n / span_days

    hour_counts: Counter[int] = Counter()
    weekday_counts: Counter[int] = Counter()
    for p in posts:
        hour_counts[p.date.hour] += 1
        weekday_counts[p.date.weekday()] += 1

    most_active_hour = hour_counts.most_common(1)[0][0] if hour_counts else None
    most_active_weekday = weekday_counts.most_common(1)[0][0] if weekday_counts else None

    # ── Content mix ────────────────────────────────────────────────────
    media_counts: Counter[str] = Counter()
    for p in posts:
        media_counts[p.media_type or "text"] += 1

    content_mix = ContentMix(
        pct_text_only=round(media_counts.get("text", 0) / n * 100, 1),
        pct_photo=round(media_counts.get("photo", 0) / n * 100, 1),
        pct_video=round(media_counts.get("video", 0) / n * 100, 1),
        pct_document=round(media_counts.get("document", 0) / n * 100, 1),
        pct_other=round(media_counts.get("other", 0) / n * 100, 1),
    )

    # ── Top posts ──────────────────────────────────────────────────────
    by_views = sorted(posts, key=lambda p: p.views, reverse=True)[:top_n]
    by_engagement = sorted(
        posts,
        key=lambda p: (p.views / ch.member_count if ch.member_count else 0),
        reverse=True,
    )[:top_n]

    return AnalysisMetrics(
        channel_title=ch.title,
        channel_username=ch.username,
        channel_type=ch.channel_type,
        member_count=ch.member_count,
        description=ch.description,
        total_posts=n,
        total_views=total_views,
        total_forwards=total_forwards,
        total_reactions=total_reactions,
        avg_views=round(avg_views, 1),
        avg_engagement_rate=round(avg_engagement, 2),
        avg_forwards_per_post=round(total_forwards / n, 1),
        avg_reactions_per_post=round(total_reactions / n, 1),
        posting_pattern=PostingPattern(
            avg_posts_per_day=round(avg_posts_per_day, 2),
            most_active_hour=most_active_hour,
            most_active_weekday=most_active_weekday,
            hour_distribution=dict(hour_counts),
            weekday_distribution=dict(weekday_counts),
        ),
        content_mix=content_mix,
        top_posts_by_views=[_make_top_post(p, ch.member_count) for p in by_views],
        top_posts_by_engagement=[_make_top_post(p, ch.member_count) for p in by_engagement],
        date_from=date_from,
        date_to=date_to,
        analysis_period_days=span_days,
    )
