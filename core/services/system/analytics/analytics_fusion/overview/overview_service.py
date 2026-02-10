"""
Analytics Overview Service
==========================

Service for computing comprehensive channel overview metrics.
Uses post_metrics, posts, and channels tables to build TGStat-style dashboard.
"""

import logging
from datetime import datetime, timedelta
from typing import Literal

from .overview_models import (
    ChannelInfo,
    ChannelOverviewMetrics,
    EngagementStats,
    PostsStats,
    ReachStats,
    SubscriberStats,
)

logger = logging.getLogger(__name__)

# Type for period parameter
PeriodType = Literal["today", "last_7_days", "last_30_days", "last_90_days", "all_time"]


class AnalyticsOverviewService:
    """
    Service for generating comprehensive channel overview metrics.

    Aggregates data from:
    - channels: Basic channel info, subscriber count
    - posts: Post counts and content analysis
    - post_metrics: Views, reactions, forwards, comments
    - channel_daily: Historical daily metrics (when available)
    """

    # Period to days mapping
    PERIOD_DAYS: dict[str, int | None] = {
        "today": 1,
        "last_7_days": 7,
        "last_30_days": 30,
        "last_90_days": 90,
        "all_time": None,  # None means no limit
    }

    def __init__(self, db_pool):
        """
        Initialize the service with database pool.

        Args:
            db_pool: AsyncPG connection pool
        """
        self.pool = db_pool
        logger.info("📊 AnalyticsOverviewService initialized")

    def _get_period_start_date(self, period: str) -> datetime | None:
        """
        Get the start date for the given period.

        Args:
            period: Period string (today, last_7_days, etc.)

        Returns:
            Start datetime or None for all_time
        """
        days = self.PERIOD_DAYS.get(period)
        if days is None:
            return None  # all_time - no date limit

        now = datetime.utcnow()
        if period == "today":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        return now - timedelta(days=days)

    async def get_channel_overview(
        self, channel_id: int, period: str = "last_7_days"
    ) -> ChannelOverviewMetrics:
        """
        Get complete channel overview metrics.

        Args:
            channel_id: The channel ID to get metrics for
            period: Time period for metrics (today, last_7_days, last_30_days, last_90_days, all_time)

        Returns:
            ChannelOverviewMetrics with all dashboard data
        """
        try:
            logger.info(f"📊 Generating overview for channel {channel_id}, period={period}")

            # Calculate period start date
            period_start = self._get_period_start_date(period)

            # Calculate days for charts based on period
            chart_days = (
                self.PERIOD_DAYS.get(period) or 365
            )  # all_time defaults to 1 year for charts

            # Fetch all data in parallel for performance
            async with self.pool.acquire() as conn:
                # Get channel info (not affected by period)
                channel_info = await self._get_channel_info(conn, channel_id)

                # Get subscriber stats
                subscribers = await self._get_subscriber_stats(conn, channel_id)

                # Get posts stats with period filter
                posts = await self._get_posts_stats(conn, channel_id, period_start)

                # Get engagement stats with period filter
                engagement = await self._get_engagement_stats(conn, channel_id, period_start)

                # Get reach stats with period filter
                reach = await self._get_reach_stats(conn, channel_id, period_start)

                # Get historical data for charts
                views_history = await self._get_views_history(conn, channel_id, days=chart_days)
                posts_history = await self._get_posts_history(conn, channel_id, days=chart_days)

            overview = ChannelOverviewMetrics(
                channel_info=channel_info,
                subscribers=subscribers,
                posts=posts,
                engagement=engagement,
                reach=reach,
                views_history=views_history,
                posts_history=posts_history,
                generated_at=datetime.utcnow(),
                data_freshness="real-time",
            )

            logger.info(f"✅ Generated overview for channel {channel_id}, period={period}")
            return overview

        except Exception as e:
            logger.error(f"❌ Error generating overview for channel {channel_id}: {e}")
            raise

    async def _get_channel_info(self, conn, channel_id: int) -> ChannelInfo:
        """Get basic channel information"""
        row = await conn.fetchrow(
            """
            SELECT id, title, username, description, created_at, 
                   telegram_created_at, subscriber_count, is_active
            FROM channels 
            WHERE id = $1 OR id = $2
            """,
            channel_id,
            -abs(channel_id),  # Try both positive and negative IDs
        )

        if not row:
            logger.warning(f"Channel {channel_id} not found")
            return ChannelInfo(id=channel_id)

        # Use telegram_created_at if available, otherwise fall back to created_at
        telegram_created_at = row["telegram_created_at"]
        created_at = row["created_at"]

        # Calculate age based on tracking start (created_at)
        tracking_days = (datetime.utcnow() - created_at).days if created_at else 0

        # Calculate channel age based on Telegram creation if available
        if telegram_created_at:
            channel_age_days = (datetime.utcnow() - telegram_created_at.replace(tzinfo=None)).days
        else:
            channel_age_days = None

        return ChannelInfo(
            id=row["id"],
            title=row["title"] or "",
            username=row["username"],
            description=row["description"],
            created_at=created_at,
            telegram_created_at=telegram_created_at,
            age_days=tracking_days,  # Days tracked in our system
            channel_age_days=channel_age_days,  # Actual Telegram channel age
            age_formatted=self._format_age(tracking_days),
            channel_age_formatted=(
                self._format_age(channel_age_days) if channel_age_days else None
            ),
            is_active=row["is_active"],
        )

    async def _get_subscriber_stats(self, conn, channel_id: int) -> SubscriberStats:
        """Get subscriber statistics"""
        # Get current subscriber count (take MAX to handle duplicate entries)
        row = await conn.fetchrow(
            """
            SELECT COALESCE(MAX(subscriber_count), 0) as subscriber_count
            FROM channels 
            WHERE id = $1 OR id = $2
            """,
            channel_id,
            -abs(channel_id),
        )

        total = row["subscriber_count"] if row else 0

        # Note: For now, we don't have historical subscriber data
        # This will be populated when we add the daily snapshot job
        return SubscriberStats(
            total=total,
            today_change=0,  # TODO: From channel_daily
            week_change=0,  # TODO: From channel_daily
            month_change=0,  # TODO: From channel_daily
            growth_rate=0.0,  # TODO: Calculate from history
        )

    async def _get_posts_stats(
        self, conn, channel_id: int, period_start: datetime | None = None
    ) -> PostsStats:
        """Get posts statistics filtered by period"""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Build the WHERE clause for period filter
        if period_start is not None:
            # Get stats within the specified period
            row = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE date >= $2) as today,
                    COUNT(*) FILTER (WHERE date >= $3) as week,
                    COUNT(*) FILTER (WHERE date >= $4) as month
                FROM posts 
                WHERE (channel_id = $1 OR channel_id = $5)
                AND is_deleted = false
                AND date >= $6
                """,
                channel_id,
                today_start,
                week_ago,
                month_ago,
                abs(channel_id),
                period_start,
            )
        else:
            # All time - no period filter
            row = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE date >= $2) as today,
                    COUNT(*) FILTER (WHERE date >= $3) as week,
                    COUNT(*) FILTER (WHERE date >= $4) as month
                FROM posts 
                WHERE (channel_id = $1 OR channel_id = $5)
                AND is_deleted = false
                """,
                channel_id,
                today_start,
                week_ago,
                month_ago,
                abs(channel_id),
            )

        total = row["total"] or 0

        # Calculate average posts per day based on period
        if period_start:
            days_in_period = max((now - period_start).days, 1)
            avg_per_day = total / days_in_period
        else:
            # For all_time, calculate based on month data
            avg_per_day = (row["month"] or 0) / 30 if row["month"] else 0

        return PostsStats(
            total=total,
            today=row["today"] or 0,
            week=row["week"] or 0,
            month=row["month"] or 0,
            avg_per_day=avg_per_day,
        )

    async def _get_engagement_stats(
        self, conn, channel_id: int, period_start: datetime | None = None
    ) -> EngagementStats:
        """Get engagement statistics filtered by period"""
        # Build query based on period
        # IMPORTANT: Join with posts to filter out deleted posts
        if period_start is not None:
            row = await conn.fetchrow(
                """
                WITH latest_metrics AS (
                    SELECT DISTINCT ON (pm.msg_id) 
                        pm.msg_id, pm.views, pm.forwards, pm.reactions_count, 
                        pm.comments_count, pm.replies_count, pm.snapshot_time
                    FROM post_metrics pm
                    INNER JOIN posts p ON pm.channel_id = p.channel_id AND pm.msg_id = p.msg_id
                    WHERE (pm.channel_id = $1 OR pm.channel_id = $2)
                    AND pm.snapshot_time >= $3
                    AND p.is_deleted = FALSE
                    ORDER BY pm.msg_id, pm.snapshot_time DESC
                )
                SELECT 
                    COUNT(*) as post_count,
                    COALESCE(SUM(views), 0) as total_views,
                    COALESCE(SUM(reactions_count), 0) as total_reactions,
                    COALESCE(SUM(forwards), 0) as total_forwards,
                    COALESCE(SUM(comments_count), 0) as total_comments,
                    COALESCE(AVG(views), 0) as avg_views,
                    COALESCE(AVG(reactions_count), 0) as avg_reactions
                FROM latest_metrics
                """,
                channel_id,
                abs(channel_id),
                period_start,
            )
        else:
            # All time - no period filter, but still exclude deleted posts
            row = await conn.fetchrow(
                """
                WITH latest_metrics AS (
                    SELECT DISTINCT ON (pm.msg_id) 
                        pm.msg_id, pm.views, pm.forwards, pm.reactions_count, 
                        pm.comments_count, pm.replies_count, pm.snapshot_time
                    FROM post_metrics pm
                    INNER JOIN posts p ON pm.channel_id = p.channel_id AND pm.msg_id = p.msg_id
                    WHERE (pm.channel_id = $1 OR pm.channel_id = $2)
                    AND p.is_deleted = FALSE
                    ORDER BY pm.msg_id, pm.snapshot_time DESC
                )
                SELECT 
                    COUNT(*) as post_count,
                    COALESCE(SUM(views), 0) as total_views,
                    COALESCE(SUM(reactions_count), 0) as total_reactions,
                    COALESCE(SUM(forwards), 0) as total_forwards,
                    COALESCE(SUM(comments_count), 0) as total_comments,
                    COALESCE(AVG(views), 0) as avg_views,
                    COALESCE(AVG(reactions_count), 0) as avg_reactions
                FROM latest_metrics
                """,
                channel_id,
                abs(channel_id),
            )

        total_views = int(row["total_views"] or 0)
        total_reactions = int(row["total_reactions"] or 0)
        total_forwards = int(row["total_forwards"] or 0)
        total_comments = int(row["total_comments"] or 0)

        # Calculate engagement rate
        total_engagement = total_reactions + total_forwards + total_comments
        engagement_rate = (total_engagement / total_views * 100) if total_views > 0 else 0

        # Calculate ERR (Engagement Rate Ratio)
        post_count = row["post_count"] or 1
        err = (total_engagement / post_count) if post_count > 0 else 0

        # Get 24h ERR
        err_24h = await self._get_err_24h(conn, channel_id)

        return EngagementStats(
            total_views=total_views,
            total_reactions=total_reactions,
            total_forwards=total_forwards,
            total_comments=total_comments,
            avg_views_per_post=float(row["avg_views"] or 0),
            avg_reactions_per_post=float(row["avg_reactions"] or 0),
            engagement_rate=engagement_rate,
            err=err,
            err_24h=err_24h,
        )

    async def _get_err_24h(self, conn, channel_id: int) -> float:
        """Get Engagement Rate Ratio for last 24 hours"""
        now = datetime.utcnow()
        day_ago = now - timedelta(hours=24)

        row = await conn.fetchrow(
            """
            WITH latest_24h AS (
                SELECT DISTINCT ON (msg_id) 
                    msg_id, views, forwards, reactions_count, comments_count
                FROM post_metrics
                WHERE (channel_id = $1 OR channel_id = $2)
                AND snapshot_time >= $3
                ORDER BY msg_id, snapshot_time DESC
            )
            SELECT 
                COUNT(*) as post_count,
                COALESCE(SUM(views), 0) as total_views,
                COALESCE(SUM(reactions_count + forwards + comments_count), 0) as total_engagement
            FROM latest_24h
            """,
            channel_id,
            abs(channel_id),
            day_ago,
        )

        total_views = int(row["total_views"] or 0)
        total_engagement = int(row["total_engagement"] or 0)

        return (total_engagement / total_views * 100) if total_views > 0 else 0

    async def _get_reach_stats(
        self, conn, channel_id: int, period_start: datetime | None = None
    ) -> ReachStats:
        """Get reach and advertising statistics filtered by period"""
        now = datetime.utcnow()

        # Build query based on period
        # IMPORTANT: Only include non-deleted posts
        if period_start is not None:
            row = await conn.fetchrow(
                """
                WITH latest_metrics AS (
                    SELECT DISTINCT ON (pm.msg_id) 
                        pm.msg_id, pm.views, pm.forwards, p.date as post_date
                    FROM post_metrics pm
                    INNER JOIN posts p ON pm.channel_id = p.channel_id AND pm.msg_id = p.msg_id
                    WHERE (pm.channel_id = $1 OR pm.channel_id = $2)
                    AND pm.snapshot_time >= $3
                    AND p.is_deleted = FALSE
                    ORDER BY pm.msg_id, pm.snapshot_time DESC
                )
                SELECT 
                    COALESCE(AVG(views), 0) as avg_reach,
                    COALESCE(SUM(views) FILTER (WHERE post_date >= $4), 0) as reach_12h,
                    COALESCE(SUM(views) FILTER (WHERE post_date >= $5), 0) as reach_24h,
                    COALESCE(SUM(views) FILTER (WHERE post_date >= $6), 0) as reach_48h,
                    COALESCE(SUM(forwards), 0) as total_forwards,
                    COUNT(*) as post_count
                FROM latest_metrics
                """,
                channel_id,
                abs(channel_id),
                period_start,
                now - timedelta(hours=12),
                now - timedelta(hours=24),
                now - timedelta(hours=48),
            )
        else:
            # All time - no period filter, but still exclude deleted posts
            row = await conn.fetchrow(
                """
                WITH latest_metrics AS (
                    SELECT DISTINCT ON (pm.msg_id) 
                        pm.msg_id, pm.views, pm.forwards, p.date as post_date
                    FROM post_metrics pm
                    INNER JOIN posts p ON pm.channel_id = p.channel_id AND pm.msg_id = p.msg_id
                    WHERE (pm.channel_id = $1 OR pm.channel_id = $2)
                    AND p.is_deleted = FALSE
                    ORDER BY pm.msg_id, pm.snapshot_time DESC
                )
                SELECT 
                    COALESCE(AVG(views), 0) as avg_reach,
                    COALESCE(SUM(views) FILTER (WHERE post_date >= $3), 0) as reach_12h,
                    COALESCE(SUM(views) FILTER (WHERE post_date >= $4), 0) as reach_24h,
                    COALESCE(SUM(views) FILTER (WHERE post_date >= $5), 0) as reach_48h,
                    COALESCE(SUM(forwards), 0) as total_forwards,
                    COUNT(*) as post_count
                FROM latest_metrics
                """,
                channel_id,
                abs(channel_id),
                now - timedelta(hours=12),
                now - timedelta(hours=24),
                now - timedelta(hours=48),
            )

        avg_reach = int(row["avg_reach"] or 0)
        total_forwards = int(row["total_forwards"] or 0)
        post_count = int(row["post_count"] or 1)

        # Citation index = average forwards per post * multiplier
        citation_index = (total_forwards / post_count * 10) if post_count > 0 else 0

        return ReachStats(
            avg_post_reach=avg_reach,
            avg_ad_reach=int(avg_reach * 0.7),  # Estimate: ad reach is typically 70% of organic
            reach_12h=int(row["reach_12h"] or 0),
            reach_24h=int(row["reach_24h"] or 0),
            reach_48h=int(row["reach_48h"] or 0),
            citation_index=citation_index,
        )

    async def _get_views_history(self, conn, channel_id: int, days: int = 30) -> list[dict]:
        """Get daily views history for charts"""
        start_date = datetime.utcnow() - timedelta(days=days)

        rows = await conn.fetch(
            """
            WITH daily_views AS (
                SELECT 
                    DATE(snapshot_time) as day,
                    SUM(views) as total_views
                FROM post_metrics
                WHERE (channel_id = $1 OR channel_id = $2)
                AND snapshot_time >= $3
                GROUP BY DATE(snapshot_time)
                ORDER BY day
            )
            SELECT day, total_views
            FROM daily_views
            """,
            channel_id,
            abs(channel_id),
            start_date,
        )

        return [
            {
                "date": row["day"].isoformat(),
                "value": int(row["total_views"] or 0),
            }
            for row in rows
        ]

    async def _get_posts_history(self, conn, channel_id: int, days: int = 30) -> list[dict]:
        """Get daily posts count history for charts"""
        start_date = datetime.utcnow() - timedelta(days=days)

        rows = await conn.fetch(
            """
            SELECT 
                DATE(date) as day,
                COUNT(*) as post_count
            FROM posts
            WHERE (channel_id = $1 OR channel_id = $2)
            AND date >= $3
            AND is_deleted = false
            GROUP BY DATE(date)
            ORDER BY day
            """,
            channel_id,
            abs(channel_id),
            start_date,
        )

        return [
            {
                "date": row["day"].isoformat(),
                "value": int(row["post_count"] or 0),
            }
            for row in rows
        ]

    def _format_age(self, days: int) -> str:
        """Format age in human-readable format"""
        if days < 1:
            return "Less than a day"
        elif days < 30:
            return f"{days} day{'s' if days != 1 else ''}"
        elif days < 365:
            months = days // 30
            remaining_days = days % 30
            result = f"{months} month{'s' if months != 1 else ''}"
            if remaining_days > 0:
                result += f" {remaining_days} day{'s' if remaining_days != 1 else ''}"
            return result
        else:
            years = days // 365
            remaining_months = (days % 365) // 30
            result = f"{years} year{'s' if years != 1 else ''}"
            if remaining_months > 0:
                result += f" {remaining_months} month{'s' if remaining_months != 1 else ''}"
            return result
