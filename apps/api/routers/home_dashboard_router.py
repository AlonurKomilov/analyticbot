"""
Home Dashboard Router
====================

API endpoint for the main dashboard after login.
Provides action alerts, today's stats, channel health, and activity feed.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from apps.api.middleware.auth import get_current_user_id
from apps.di import get_container

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class ActionAlert(BaseModel):
    """An alert requiring user action"""

    id: str
    type: str  # "error", "warning", "info"
    title: str
    description: str
    action_url: str | None = None
    action_label: str | None = None
    channel_id: int | None = None
    created_at: datetime


class TodayStats(BaseModel):
    """Today's snapshot statistics"""

    new_subscribers: int = 0
    subscriber_change_percent: float = 0.0
    total_views: int = 0
    views_change_percent: float = 0.0
    posts_today: int = 0
    best_post_title: str | None = None
    best_post_views: int = 0
    best_post_id: int | None = None


class ChannelHealth(BaseModel):
    """Health and status for a single channel"""

    id: int
    name: str
    username: str | None = None
    subscribers: int = 0
    subscriber_growth_week: int = 0
    avg_views: int = 0
    last_post_time: datetime | None = None
    last_post_ago: str | None = None  # "3 hours ago"
    engagement_rate: float = 0.0
    engagement_change: float = 0.0  # vs last week
    last_sync: datetime | None = None
    last_sync_ago: str | None = None
    sync_status: str = "unknown"  # "healthy", "stale", "error", "never"
    bot_is_admin: bool = False
    mtproto_enabled: bool = False


class ActivityItem(BaseModel):
    """Single activity feed item"""

    id: str
    type: str  # "sync", "subscriber", "post", "view", "scheduled"
    icon: str  # emoji or icon name
    message: str
    channel_name: str | None = None
    channel_id: int | None = None
    timestamp: datetime
    time_ago: str  # "2 minutes ago"


class QuickAction(BaseModel):
    """Contextual quick action"""

    id: str
    title: str
    description: str
    icon: str
    url: str
    priority: int = 0  # Higher = more important


class HomeDashboardResponse(BaseModel):
    """Complete home dashboard data"""

    user_id: int
    username: str | None = None

    # Action required alerts
    alerts: list[ActionAlert] = []

    # Today's snapshot
    today: TodayStats

    # Channel health cards
    channels: list[ChannelHealth] = []

    # Recent activity feed
    activity: list[ActivityItem] = []

    # Contextual quick actions
    quick_actions: list[QuickAction] = []

    # Meta
    last_updated: datetime
    has_channels: bool = False
    has_bot: bool = False
    has_mtproto: bool = False


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _time_ago(dt: datetime | None) -> str:
    """Convert datetime to human-readable 'time ago' string"""
    if not dt:
        return "Never"

    now = datetime.now(UTC)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        mins = int(seconds / 60)
        return f"{mins} minute{'s' if mins != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"


async def _get_user_alerts(pool, user_id: int) -> list[ActionAlert]:
    """Get action required alerts for user"""
    alerts = []

    async with pool.acquire() as conn:
        # Check for channels where bot is not admin
        bot_issues = await conn.fetch(
            """
            SELECT c.id, c.name, c.username
            FROM channels c
            JOIN user_channels uc ON c.id = uc.channel_id
            LEFT JOIN user_bot_credentials ubc ON uc.user_id = ubc.user_id
            WHERE uc.user_id = $1
            AND c.is_active = true
            AND (
                NOT EXISTS (
                    SELECT 1 FROM user_bot_credentials
                    WHERE user_id = $1 AND is_active = true
                )
            )
        """,
            user_id,
        )

        if bot_issues:
            alerts.append(
                ActionAlert(
                    id="no_bot_configured",
                    type="warning",
                    title="Bot Not Configured",
                    description="Configure your Telegram bot to enable posting and data collection",
                    action_url="/bot/dashboard",
                    action_label="Configure Bot",
                    created_at=datetime.now(UTC),
                )
            )

        # Check for stale sync (no data collection in 24 hours)
        stale_channels = await conn.fetch(
            """
            SELECT c.id, c.name
            FROM channels c
            JOIN user_channels uc ON c.id = uc.channel_id
            JOIN user_mtproto_channel_settings umcs ON c.id = umcs.channel_id AND umcs.user_id = uc.user_id
            WHERE uc.user_id = $1
            AND umcs.enabled = true
            AND (
                umcs.last_collected_at IS NULL
                OR umcs.last_collected_at < NOW() - INTERVAL '24 hours'
            )
        """,
            user_id,
        )

        for ch in stale_channels:
            alerts.append(
                ActionAlert(
                    id=f"stale_sync_{ch['id']}",
                    type="warning",
                    title="Data Collection Stale",
                    description=f"'{ch['name']}' hasn't synced in 24+ hours",
                    action_url="/mtproto-monitoring",
                    action_label="Check Status",
                    channel_id=ch["id"],
                    created_at=datetime.now(UTC),
                )
            )

        # Check for scheduled posts needing review (draft status)
        pending_posts = await conn.fetchval(
            """
            SELECT COUNT(*)
            FROM scheduled_posts sp
            JOIN user_channels uc ON sp.channel_id = uc.channel_id
            WHERE uc.user_id = $1
            AND sp.status = 'draft'
        """,
            user_id,
        )

        if pending_posts and pending_posts > 0:
            alerts.append(
                ActionAlert(
                    id="pending_posts",
                    type="info",
                    title=f"{pending_posts} Scheduled Post{'s' if pending_posts != 1 else ''} Pending",
                    description="Review and publish your scheduled posts",
                    action_url="/scheduled",
                    action_label="View Posts",
                    created_at=datetime.now(UTC),
                )
            )

    return alerts


async def _get_today_stats(pool, user_id: int) -> TodayStats:
    """Get today's snapshot statistics"""
    stats = TodayStats()

    async with pool.acquire() as conn:
        # Get today's posts and views
        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)

        # Posts today
        posts_today = await conn.fetchval(
            """
            SELECT COUNT(*)
            FROM posts p
            JOIN user_channels uc ON p.channel_id = uc.channel_id
            WHERE uc.user_id = $1
            AND p.posted_at >= $2
        """,
            user_id,
            today_start,
        )
        stats.posts_today = posts_today or 0

        # Views today (from post_statistics)
        views_data = await conn.fetchrow(
            """
            SELECT
                COALESCE(SUM(ps.views), 0) as total_views
            FROM post_statistics ps
            JOIN posts p ON ps.post_id = p.id
            JOIN user_channels uc ON p.channel_id = uc.channel_id
            WHERE uc.user_id = $1
            AND ps.collected_at >= $2
        """,
            user_id,
            today_start,
        )
        stats.total_views = views_data["total_views"] if views_data else 0

        # Best post today
        best_post = await conn.fetchrow(
            """
            SELECT p.id, COALESCE(p.text, 'Untitled Post') as title,
                   COALESCE(ps.views, 0) as views
            FROM posts p
            LEFT JOIN LATERAL (
                SELECT views FROM post_statistics
                WHERE post_id = p.id
                ORDER BY collected_at DESC LIMIT 1
            ) ps ON true
            JOIN user_channels uc ON p.channel_id = uc.channel_id
            WHERE uc.user_id = $1
            AND p.posted_at >= $2
            ORDER BY ps.views DESC NULLS LAST
            LIMIT 1
        """,
            user_id,
            today_start,
        )

        if best_post:
            stats.best_post_id = best_post["id"]
            title = (
                best_post["title"][:50] + "..."
                if len(best_post["title"]) > 50
                else best_post["title"]
            )
            stats.best_post_title = title
            stats.best_post_views = best_post["views"]

        # Subscriber changes (comparing latest vs yesterday)
        sub_change = await conn.fetchrow(
            """
            WITH latest_subs AS (
                SELECT c.id, c.subscriber_count as current_subs
                FROM channels c
                JOIN user_channels uc ON c.id = uc.channel_id
                WHERE uc.user_id = $1
            ),
            yesterday_subs AS (
                SELECT channel_id, subscriber_count as yesterday_subs
                FROM subscriber_history
                WHERE recorded_at >= $2 AND recorded_at < $3
                AND channel_id IN (SELECT channel_id FROM user_channels WHERE user_id = $1)
            )
            SELECT
                COALESCE(SUM(ls.current_subs), 0) as current_total,
                COALESCE(SUM(ys.yesterday_subs), 0) as yesterday_total
            FROM latest_subs ls
            LEFT JOIN yesterday_subs ys ON ls.id = ys.channel_id
        """,
            user_id,
            yesterday_start,
            today_start,
        )

        if sub_change:
            current = sub_change["current_total"] or 0
            yesterday = sub_change["yesterday_total"] or current
            stats.new_subscribers = current - yesterday
            if yesterday > 0:
                stats.subscriber_change_percent = round((current - yesterday) / yesterday * 100, 1)

    return stats


async def _get_channel_health(pool, user_id: int) -> list[ChannelHealth]:
    """Get health status for all user channels"""
    channels = []

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                c.id, c.name, c.username, c.subscriber_count,
                c.is_active,
                umcs.enabled as mtproto_enabled,
                umcs.last_collected_at,
                ubc.id IS NOT NULL as has_bot
            FROM channels c
            JOIN user_channels uc ON c.id = uc.channel_id
            LEFT JOIN user_mtproto_channel_settings umcs ON c.id = umcs.channel_id AND umcs.user_id = uc.user_id
            LEFT JOIN user_bot_credentials ubc ON uc.user_id = ubc.user_id AND ubc.is_active = true
            WHERE uc.user_id = $1
            ORDER BY c.name
        """,
            user_id,
        )

        for row in rows:
            channel_id = row["id"]

            # Get additional stats
            stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(p.id) as total_posts,
                    MAX(p.posted_at) as last_post_time,
                    COALESCE(AVG(ps.views), 0) as avg_views,
                    COALESCE(AVG(
                        CASE WHEN ps.views > 0
                        THEN (COALESCE(ps.reactions, 0) + COALESCE(ps.forwards, 0))::float / ps.views * 100
                        ELSE 0 END
                    ), 0) as engagement_rate
                FROM posts p
                LEFT JOIN LATERAL (
                    SELECT views, reactions, forwards FROM post_statistics
                    WHERE post_id = p.id
                    ORDER BY collected_at DESC LIMIT 1
                ) ps ON true
                WHERE p.channel_id = $1
                AND p.posted_at >= NOW() - INTERVAL '30 days'
            """,
                channel_id,
            )

            # Subscriber growth this week
            week_growth = await conn.fetchval(
                """
                SELECT
                    COALESCE(
                        (SELECT subscriber_count FROM subscriber_history
                         WHERE channel_id = $1
                         ORDER BY recorded_at DESC LIMIT 1),
                        $2
                    ) -
                    COALESCE(
                        (SELECT subscriber_count FROM subscriber_history
                         WHERE channel_id = $1
                         AND recorded_at <= NOW() - INTERVAL '7 days'
                         ORDER BY recorded_at DESC LIMIT 1),
                        $2
                    )
            """,
                channel_id,
                row["subscriber_count"] or 0,
            )

            # Determine sync status
            last_sync = row["last_collected_at"]
            if not last_sync:
                sync_status = "never"
            elif last_sync > datetime.now(UTC) - timedelta(hours=6):
                sync_status = "healthy"
            elif last_sync > datetime.now(UTC) - timedelta(hours=24):
                sync_status = "stale"
            else:
                sync_status = "error"

            channels.append(
                ChannelHealth(
                    id=channel_id,
                    name=row["name"] or "Unknown",
                    username=row["username"],
                    subscribers=row["subscriber_count"] or 0,
                    subscriber_growth_week=week_growth or 0,
                    avg_views=int(stats["avg_views"]) if stats else 0,
                    last_post_time=stats["last_post_time"] if stats else None,
                    last_post_ago=_time_ago(stats["last_post_time"])
                    if stats and stats["last_post_time"]
                    else None,
                    engagement_rate=round(stats["engagement_rate"], 2) if stats else 0.0,
                    last_sync=last_sync,
                    last_sync_ago=_time_ago(last_sync),
                    sync_status=sync_status,
                    bot_is_admin=row["has_bot"],
                    mtproto_enabled=row["mtproto_enabled"] or False,
                )
            )

    return channels


async def _get_activity_feed(pool, user_id: int, limit: int = 10) -> list[ActivityItem]:
    """Get recent activity feed"""
    activities = []

    async with pool.acquire() as conn:
        # Get recent syncs
        syncs = await conn.fetch(
            """
            SELECT
                mal.id, mal.channel_id, c.name as channel_name,
                mal.posts_collected, mal.started_at as timestamp,
                mal.status
            FROM mtproto_audit_log mal
            JOIN channels c ON mal.channel_id = c.id
            JOIN user_channels uc ON c.id = uc.channel_id
            WHERE uc.user_id = $1
            AND mal.started_at >= NOW() - INTERVAL '24 hours'
            ORDER BY mal.started_at DESC
            LIMIT 5
        """,
            user_id,
        )

        for sync in syncs:
            posts = sync["posts_collected"] or 0
            status = sync["status"]

            if status == "completed":
                message = f"Collected {posts} new post{'s' if posts != 1 else ''}"
                icon = "📊"
            elif status == "failed":
                message = "Sync failed"
                icon = "❌"
            else:
                message = "Sync in progress..."
                icon = "🔄"

            activities.append(
                ActivityItem(
                    id=f"sync_{sync['id']}",
                    type="sync",
                    icon=icon,
                    message=message,
                    channel_name=sync["channel_name"],
                    channel_id=sync["channel_id"],
                    timestamp=sync["timestamp"],
                    time_ago=_time_ago(sync["timestamp"]),
                )
            )

        # Get recent posts
        posts = await conn.fetch(
            """
            SELECT
                p.id, p.channel_id, c.name as channel_name,
                COALESCE(LEFT(p.text, 50), 'New post') as title,
                p.posted_at as timestamp,
                ps.views
            FROM posts p
            JOIN channels c ON p.channel_id = c.id
            JOIN user_channels uc ON c.id = uc.channel_id
            LEFT JOIN LATERAL (
                SELECT views FROM post_statistics
                WHERE post_id = p.id
                ORDER BY collected_at DESC LIMIT 1
            ) ps ON true
            WHERE uc.user_id = $1
            AND p.posted_at >= NOW() - INTERVAL '24 hours'
            ORDER BY p.posted_at DESC
            LIMIT 5
        """,
            user_id,
        )

        for post in posts:
            views = post["views"] or 0
            activities.append(
                ActivityItem(
                    id=f"post_{post['id']}",
                    type="post",
                    icon="📝",
                    message=f"\"{post['title']}{'...' if len(post['title']) >= 50 else ''}\" - {views:,} views",
                    channel_name=post["channel_name"],
                    channel_id=post["channel_id"],
                    timestamp=post["timestamp"],
                    time_ago=_time_ago(post["timestamp"]),
                )
            )

    # Sort by timestamp and limit
    activities.sort(key=lambda x: x.timestamp, reverse=True)
    return activities[:limit]


async def _get_quick_actions(
    pool, user_id: int, has_channels: bool, has_bot: bool, has_mtproto: bool
) -> list[QuickAction]:
    """Get contextual quick actions based on user state"""
    actions = []

    if not has_channels:
        actions.append(
            QuickAction(
                id="add_channel",
                title="Add Your First Channel",
                description="Connect a Telegram channel to start tracking analytics",
                icon="add_circle",
                url="/channels",
                priority=100,
            )
        )

    if has_channels and not has_bot:
        actions.append(
            QuickAction(
                id="setup_bot",
                title="Configure Your Bot",
                description="Add your Telegram bot to enable posting and management",
                icon="smart_toy",
                url="/bot/dashboard",
                priority=90,
            )
        )

    if has_channels and not has_mtproto:
        actions.append(
            QuickAction(
                id="setup_mtproto",
                title="Enable Advanced Analytics",
                description="Connect MTProto for real-time data collection",
                icon="analytics",
                url="/settings",
                priority=80,
            )
        )

    if has_channels:
        actions.append(
            QuickAction(
                id="create_post",
                title="Create Post",
                description="Write and publish a new post to your channel",
                icon="edit",
                url="/posts/create",
                priority=70,
            )
        )

        actions.append(
            QuickAction(
                id="view_analytics",
                title="View Analytics",
                description="See detailed performance metrics",
                icon="bar_chart",
                url="/analytics",
                priority=60,
            )
        )

    # Sort by priority
    actions.sort(key=lambda x: x.priority, reverse=True)
    return actions[:4]  # Max 4 quick actions


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get("", response_model=HomeDashboardResponse)
async def get_home_dashboard(
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> HomeDashboardResponse:
    """
    Get complete home dashboard data.

    Returns:
        - Action required alerts
        - Today's stats snapshot
        - Channel health cards
        - Recent activity feed
        - Contextual quick actions
    """
    container = get_container()
    pool = await container.database.asyncpg_pool()

    if not pool:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        # Get user info
        async with pool.acquire() as conn:
            user = await conn.fetchrow("SELECT id, username FROM users WHERE id = $1", user_id)

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Check what user has configured
            has_channels = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM user_channels WHERE user_id = $1)", user_id
            )

            has_bot = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM user_bot_credentials WHERE user_id = $1 AND is_active = true)",
                user_id,
            )

            has_mtproto = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM user_mtproto_sessions WHERE user_id = $1 AND is_active = true)",
                user_id,
            )

        # Fetch all dashboard data
        alerts = await _get_user_alerts(pool, user_id)
        today = await _get_today_stats(pool, user_id)
        channels = await _get_channel_health(pool, user_id)
        activity = await _get_activity_feed(pool, user_id)
        quick_actions = await _get_quick_actions(pool, user_id, has_channels, has_bot, has_mtproto)

        return HomeDashboardResponse(
            user_id=user_id,
            username=user["username"],
            alerts=alerts,
            today=today,
            channels=channels,
            activity=activity,
            quick_actions=quick_actions,
            last_updated=datetime.now(UTC),
            has_channels=has_channels,
            has_bot=has_bot,
            has_mtproto=has_mtproto,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching dashboard for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard")
