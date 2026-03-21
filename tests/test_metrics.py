"""Tests for metrics computation"""

from datetime import datetime, timezone

from src.analyzer.fetcher import ChannelInfo, FetchResult, FetchedPost
from src.analyzer.metrics import compute_metrics


def _make_post(
    message_id: int = 1,
    views: int = 100,
    forwards: int = 5,
    replies: int = 2,
    reactions: int = 10,
    media_type: str | None = None,
    hour: int = 12,
    weekday: int = 0,  # Monday
) -> FetchedPost:
    # Create a date with specific hour and weekday (Mon=0)
    # 2026-01-05 is a Monday
    day = 5 + weekday
    return FetchedPost(
        message_id=message_id,
        date=datetime(2026, 1, day, hour, 0, 0, tzinfo=timezone.utc),
        text=f"Post {message_id}",
        views=views,
        forwards=forwards,
        replies=replies,
        reactions_count=reactions,
        media_type=media_type,
        has_link=False,
    )


def _make_channel(member_count: int = 1000) -> ChannelInfo:
    return ChannelInfo(
        channel_id=123,
        title="Test Channel",
        username="testchannel",
        description="A test channel",
        member_count=member_count,
        channel_type="channel",
    )


class TestComputeMetrics:
    def test_empty_posts(self):
        result = FetchResult(channel=_make_channel(), posts=[])
        metrics = compute_metrics(result)
        assert metrics.total_posts == 0
        assert metrics.avg_views == 0.0

    def test_basic_metrics(self):
        posts = [
            _make_post(message_id=1, views=200, forwards=10, reactions=20),
            _make_post(message_id=2, views=100, forwards=5, reactions=10),
        ]
        result = FetchResult(channel=_make_channel(member_count=1000), posts=posts)
        metrics = compute_metrics(result)

        assert metrics.total_posts == 2
        assert metrics.total_views == 300
        assert metrics.total_forwards == 15
        assert metrics.total_reactions == 30
        assert metrics.avg_views == 150.0

    def test_engagement_rate(self):
        posts = [_make_post(views=500)]
        result = FetchResult(channel=_make_channel(member_count=1000), posts=posts)
        metrics = compute_metrics(result)
        # engagement = (500 / 1000) * 100 = 50%
        assert metrics.avg_engagement_rate == 50.0

    def test_zero_members(self):
        posts = [_make_post(views=100)]
        result = FetchResult(channel=_make_channel(member_count=0), posts=posts)
        metrics = compute_metrics(result)
        assert metrics.avg_engagement_rate == 0.0

    def test_content_mix(self):
        posts = [
            _make_post(message_id=1, media_type=None),
            _make_post(message_id=2, media_type="photo"),
            _make_post(message_id=3, media_type="photo"),
            _make_post(message_id=4, media_type="video"),
        ]
        result = FetchResult(channel=_make_channel(), posts=posts)
        metrics = compute_metrics(result)

        assert metrics.content_mix.pct_text_only == 25.0
        assert metrics.content_mix.pct_photo == 50.0
        assert metrics.content_mix.pct_video == 25.0

    def test_top_posts_limited(self):
        posts = [_make_post(message_id=i, views=i * 100) for i in range(1, 20)]
        result = FetchResult(channel=_make_channel(), posts=posts)
        metrics = compute_metrics(result, top_n=5)

        assert len(metrics.top_posts_by_views) == 5
        assert metrics.top_posts_by_views[0].views == 1900  # highest

    def test_posting_pattern(self):
        posts = [
            _make_post(message_id=1, hour=14, weekday=0),
            _make_post(message_id=2, hour=14, weekday=0),
            _make_post(message_id=3, hour=9, weekday=2),
        ]
        result = FetchResult(channel=_make_channel(), posts=posts)
        metrics = compute_metrics(result)

        assert metrics.posting_pattern.most_active_hour == 14
        assert metrics.posting_pattern.most_active_weekday == 0  # Monday

    def test_total_replies(self):
        posts = [
            _make_post(message_id=1, replies=5),
            _make_post(message_id=2, replies=3),
        ]
        result = FetchResult(channel=_make_channel(), posts=posts)
        metrics = compute_metrics(result)
        assert metrics.total_replies == 8

    def test_engagement_breakdown(self):
        posts = [
            _make_post(message_id=1, views=200, forwards=10, reactions=20, replies=4),
            _make_post(message_id=2, views=100, forwards=5, reactions=10, replies=2),
        ]
        result = FetchResult(channel=_make_channel(member_count=1000), posts=posts)
        metrics = compute_metrics(result)
        eng = metrics.engagement

        assert eng.median_views == 150.0
        # virality = (15 / 300) * 100 = 5.0%
        assert abs(eng.virality_rate - 5.0) < 0.01
        # interaction = (30 + 6) / 300 * 100 = 12.0%
        assert abs(eng.interaction_rate - 12.0) < 0.01
        assert eng.avg_replies_per_post == 3.0
        # views_per_member = 150 / 1000 = 0.15
        assert abs(eng.views_per_member - 0.15) < 0.01

    def test_views_trend(self):
        posts = [
            _make_post(message_id=1, views=200),
            _make_post(message_id=2, views=100),
        ]
        result = FetchResult(channel=_make_channel(), posts=posts)
        metrics = compute_metrics(result)
        # Both posts are on same day (2026-01-05), so 1 date entry
        assert len(metrics.views_trend.dates) == 1
        assert metrics.views_trend.daily_views[0] == 300
        assert metrics.views_trend.daily_posts[0] == 2

    def test_data_note_present(self):
        posts = [_make_post()]
        result = FetchResult(channel=_make_channel(), posts=posts)
        metrics = compute_metrics(result)
        assert isinstance(metrics.data_note, str)
        assert len(metrics.data_note) > 0

    def test_activity_status_active(self):
        """Posts from today → active status."""
        now = datetime.now(timezone.utc)
        post = FetchedPost(
            message_id=1, date=now, text="Recent",
            views=100, forwards=5, replies=2,
            reactions_count=10, media_type=None, has_link=False,
        )
        result = FetchResult(channel=_make_channel(), posts=[post])
        metrics = compute_metrics(result)
        assert metrics.activity_status == "active"
        assert metrics.days_since_last_post <= 1

    def test_activity_status_dead(self):
        """Posts from years ago → dead status."""
        old_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        post = FetchedPost(
            message_id=1, date=old_date, text="Old post",
            views=100000, forwards=5, replies=2,
            reactions_count=10, media_type=None, has_link=False,
        )
        result = FetchResult(channel=_make_channel(), posts=[post])
        metrics = compute_metrics(result)
        assert metrics.activity_status == "dead"
        assert metrics.days_since_last_post > 90

    def test_empty_posts_dead_status(self):
        result = FetchResult(channel=_make_channel(), posts=[])
        metrics = compute_metrics(result)
        assert metrics.activity_status == "dead"
        assert metrics.posting_frequency == "none"

    def test_posting_frequency_classification(self):
        """Multiple posts per day → high frequency."""
        from src.analyzer.metrics import _classify_activity
        status, freq = _classify_activity(days_since_last=0, avg_posts_per_day=5.0)
        assert freq == "high"
        assert status == "active"

        status, freq = _classify_activity(days_since_last=30, avg_posts_per_day=0.05)
        assert freq == "very_low"
        assert status == "inactive"
