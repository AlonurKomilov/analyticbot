"""Metrics computation — takes fetched posts and produces analytics"""

from __future__ import annotations

import statistics
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

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
class EngagementBreakdown:
    """Deeper engagement metrics beyond simple averages."""
    median_views: float
    virality_rate: float  # forwards / views (%)
    interaction_rate: float  # (reactions + replies) / views (%)
    avg_replies_per_post: float
    pct_posts_with_links: float
    views_per_member: float  # avg views / members — reach efficiency


@dataclass
class ViewsTrend:
    """Daily aggregated views for time-series chart."""
    dates: list[str] = field(default_factory=list)  # YYYY-MM-DD
    daily_views: list[int] = field(default_factory=list)
    daily_posts: list[int] = field(default_factory=list)


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
    total_replies: int
    avg_views: float
    avg_engagement_rate: float  # (views / member_count) averaged across posts
    avg_forwards_per_post: float
    avg_reactions_per_post: float

    # New: deeper engagement
    engagement: EngagementBreakdown

    # Patterns
    posting_pattern: PostingPattern
    content_mix: ContentMix

    # New: views over time
    views_trend: ViewsTrend

    # Top content
    top_posts_by_views: list[TopPost]
    top_posts_by_engagement: list[TopPost]

    # Time range covered
    date_from: datetime | None
    date_to: datetime | None
    analysis_period_days: int

    # Activity & freshness intelligence
    days_since_last_post: int  # 0 = posted today
    activity_status: str  # "active", "low", "inactive", "dead"
    posting_frequency: str  # "high", "moderate", "low", "very_low", "none"

    # Data coverage info
    data_note: str  # explains what the numbers represent


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


def _compute_views_trend(posts: list[FetchedPost]) -> ViewsTrend:
    """Aggregate views and post counts by day."""
    daily_views: dict[str, int] = {}
    daily_posts: dict[str, int] = {}

    for p in posts:
        day = p.date.strftime("%Y-%m-%d")
        daily_views[day] = daily_views.get(day, 0) + p.views
        daily_posts[day] = daily_posts.get(day, 0) + 1

    sorted_days = sorted(daily_views.keys())
    return ViewsTrend(
        dates=sorted_days,
        daily_views=[daily_views[d] for d in sorted_days],
        daily_posts=[daily_posts[d] for d in sorted_days],
    )


def _classify_activity(days_since_last: int, avg_posts_per_day: float) -> tuple[str, str]:
    """
    Classify channel activity status and posting frequency.

    Returns (activity_status, posting_frequency):
        activity_status: "active" | "low" | "inactive" | "dead"
        posting_frequency: "high" | "moderate" | "low" | "very_low" | "none"
    """
    # Posting frequency classification
    if avg_posts_per_day >= 3:
        freq = "high"
    elif avg_posts_per_day >= 1:
        freq = "moderate"
    elif avg_posts_per_day >= 0.1:  # at least ~1 post per 10 days
        freq = "low"
    elif avg_posts_per_day > 0:
        freq = "very_low"
    else:
        freq = "none"

    # Activity status based on recency
    if days_since_last <= 3:
        status = "active"
    elif days_since_last <= 14:
        status = "low"
    elif days_since_last <= 90:
        status = "inactive"
    else:
        status = "dead"

    return status, freq


def compute_metrics(result: FetchResult, top_n: int = 10) -> AnalysisMetrics:
    """Compute all analytics from fetched channel data."""
    ch = result.channel
    posts = result.posts
    empty_engagement = EngagementBreakdown(0, 0, 0, 0, 0, 0)

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
            total_replies=0,
            avg_views=0.0,
            avg_engagement_rate=0.0,
            avg_forwards_per_post=0.0,
            avg_reactions_per_post=0.0,
            engagement=empty_engagement,
            posting_pattern=PostingPattern(0, None, None),
            content_mix=ContentMix(0, 0, 0, 0, 0),
            views_trend=ViewsTrend(),
            top_posts_by_views=[],
            top_posts_by_engagement=[],
            date_from=None,
            date_to=None,
            analysis_period_days=0,
            days_since_last_post=999,
            activity_status="dead",
            posting_frequency="none",
            data_note="No posts found.",
        )

    n = len(posts)
    total_views = sum(p.views for p in posts)
    total_forwards = sum(p.forwards for p in posts)
    total_reactions = sum(p.reactions_count for p in posts)
    total_replies = sum(p.replies for p in posts)

    avg_views = total_views / n
    avg_engagement = (
        sum(p.views / ch.member_count for p in posts) / n * 100 if ch.member_count > 0 else 0.0
    )

    # ── Deeper engagement ──────────────────────────────────────────────
    views_list = [p.views for p in posts]
    median_views = statistics.median(views_list)
    virality_rate = (total_forwards / total_views * 100) if total_views > 0 else 0.0
    interaction_rate = (
        (total_reactions + total_replies) / total_views * 100 if total_views > 0 else 0.0
    )
    pct_with_links = sum(1 for p in posts if p.has_link) / n * 100
    views_per_member = avg_views / ch.member_count if ch.member_count > 0 else 0.0

    engagement_breakdown = EngagementBreakdown(
        median_views=round(median_views, 1),
        virality_rate=round(virality_rate, 3),
        interaction_rate=round(interaction_rate, 3),
        avg_replies_per_post=round(total_replies / n, 1),
        pct_posts_with_links=round(pct_with_links, 1),
        views_per_member=round(views_per_member, 3),
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

    # ── Views over time ───────────────────────────────────────────────
    views_trend = _compute_views_trend(posts)

    # ── Top posts ──────────────────────────────────────────────────────
    by_views = sorted(posts, key=lambda p: p.views, reverse=True)[:top_n]
    by_engagement = sorted(
        posts,
        key=lambda p: (p.views / ch.member_count if ch.member_count else 0),
        reverse=True,
    )[:top_n]

    # ── Data coverage note ─────────────────────────────────────────────
    data_note = (
        f"Based on the most recent {n} posts "
        f"({date_from.strftime('%b %d')} – {date_to.strftime('%b %d, %Y')}, "
        f"{span_days} days). "
    )
    if n >= 500:
        data_note += (
            "This covers active posting history. For channels with high "
            "volume (17+ posts/day), older posts beyond this window are not included."
        )
    else:
        data_note += "This represents the channel's complete recent history."

    # ── Activity classification ────────────────────────────────────────
    now = datetime.now(UTC)
    # date_to may be tz-naive from Telethon, normalize
    last_post_dt = date_to.replace(tzinfo=UTC) if date_to.tzinfo is None else date_to
    days_since_last_post = max((now - last_post_dt).days, 0)
    activity_status, posting_frequency = _classify_activity(days_since_last_post, avg_posts_per_day)

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
        total_replies=total_replies,
        avg_views=round(avg_views, 1),
        avg_engagement_rate=round(avg_engagement, 2),
        avg_forwards_per_post=round(total_forwards / n, 1),
        avg_reactions_per_post=round(total_reactions / n, 1),
        engagement=engagement_breakdown,
        posting_pattern=PostingPattern(
            avg_posts_per_day=round(avg_posts_per_day, 2),
            most_active_hour=most_active_hour,
            most_active_weekday=most_active_weekday,
            hour_distribution=dict(hour_counts),
            weekday_distribution=dict(weekday_counts),
        ),
        content_mix=content_mix,
        views_trend=views_trend,
        top_posts_by_views=[_make_top_post(p, ch.member_count) for p in by_views],
        top_posts_by_engagement=[_make_top_post(p, ch.member_count) for p in by_engagement],
        date_from=date_from,
        date_to=date_to,
        analysis_period_days=span_days,
        days_since_last_post=days_since_last_post,
        activity_status=activity_status,
        posting_frequency=posting_frequency,
        data_note=data_note,
    )
