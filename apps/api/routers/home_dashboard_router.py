"""
Home Dashboard Router
====================

API endpoint for the main dashboard after login.
Provides action alerts, today's stats, channel health, and activity feed.

Uses actual database schema:
- channels (has user_id directly)
- channel_mtproto_settings (user_id, channel_id, mtproto_enabled)
- posts (channel_id, msg_id, date, text)
- post_metrics (channel_id, msg_id, snapshot_time, views, forwards, reactions_count)
- mtproto_audit_log (channel_id, timestamp, action)
- user_bot_credentials (user_id, status)
- scheduled_posts (channel_id, status)
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
    type: str  # "critical", "error", "warning", "info"
    title: str
    description: str
    action_url: str | None = None
    action_label: str | None = None
    channel_id: int | None = None
    created_at: datetime


class TodayStats(BaseModel):
    """Today's snapshot statistics with daily changes"""

    # Subscriber stats
    total_subscribers: int = 0
    new_subscribers_today: int = 0  # Change from yesterday (estimated)
    subscriber_change_percent: float = 0.0

    # View stats
    total_views: int = 0
    views_gained_today: int = 0  # Views gained since yesterday
    views_change_percent: float = 0.0

    # Post stats
    posts_today: int = 0
    posts_this_week: int = 0

    # Best post
    best_post_title: str | None = None
    best_post_views: int = 0
    best_post_id: int | None = None
    best_post_channel_id: int | None = None


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


class WelcomeMessage(BaseModel):
    """Smart personalized welcome message"""

    greeting: str  # "Good morning", "Good evening", etc.
    message: str  # Additional context message
    emoji: str  # Emoji to show


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

    # Smart welcome message
    welcome: WelcomeMessage

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

    # 7-day performance sparkline
    sparkline_views: list[int] = []  # Last 7 days views per day
    sparkline_labels: list[str] = []  # Day labels (Mon, Tue, etc.)

    # Meta
    last_updated: datetime
    has_channels: bool = False
    has_bot: bool = False
    has_mtproto: bool = False


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _get_smart_welcome(
    username: str | None,
    last_login: datetime | None,
    has_channels: bool,
    posts_today: int,
    views_gained: int,
) -> WelcomeMessage:
    """Generate smart personalized welcome message"""
    now = datetime.now(UTC)
    hour = now.hour
    weekday = now.weekday()  # 0=Monday, 6=Sunday

    # Get display name
    name = username or "there"

    # Time-based greeting
    if 5 <= hour < 12:
        greeting = f"Good morning, {name}!"
        emoji = "☀️"
    elif 12 <= hour < 17:
        greeting = f"Good afternoon, {name}!"
        emoji = "👋"
    elif 17 <= hour < 21:
        greeting = f"Good evening, {name}!"
        emoji = "🌆"
    else:
        greeting = f"Hey there, {name}!"
        emoji = "🌙"

    # Context message based on various factors
    message = "Here's what's happening with your channels today."

    # Check last login (if available)
    if last_login:
        days_since_login = (now - last_login).days if last_login.tzinfo else 0
        if days_since_login >= 7:
            message = "Long time no see! Let's catch up on your channels."
            emoji = "👀"
        elif days_since_login >= 3:
            message = "Welcome back! Here's what you missed."
            emoji = "🎉"

    # Day-specific messages (override if special day)
    if weekday == 0:  # Monday
        message = "Happy Monday! Fresh week, fresh opportunities."
        emoji = "💪"
    elif weekday == 4:  # Friday
        message = "TGIF! Let's see how your week went."
        emoji = "🎉"
    elif weekday in [5, 6]:  # Weekend
        message = "Enjoy your weekend! Here's a quick overview."
        emoji = "🌴"

    # Activity-based messages (highest priority)
    if posts_today > 0:
        message = (
            f"You've been productive! {posts_today} post{'s' if posts_today > 1 else ''} today."
        )
        emoji = "🔥"
    elif views_gained > 100:
        message = f"Your content is getting attention! +{views_gained:,} views today."
        emoji = "📈"
    elif not has_channels:
        message = "Ready to get started? Add your first channel!"
        emoji = "🚀"

    return WelcomeMessage(greeting=greeting, message=message, emoji=emoji)


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
    """
    Get CRITICAL action required alerts for dashboard.
    These are blocking issues that prevent core functionality.

    Warning/Info alerts go to top bar notifications (separate endpoint).
    """
    alerts = []

    async with pool.acquire() as conn:
        # ==============================================
        # CRITICAL ALERT 1: Bot Not Configured
        # User hasn't set up their Telegram bot yet
        # This blocks: adding channels, posting, everything
        # ==============================================
        has_bot = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM user_bot_credentials WHERE user_id = $1 AND status = 'active')",
            user_id,
        )

        if not has_bot:
            alerts.append(
                ActionAlert(
                    id="no_bot_configured",
                    type="critical",
                    title="Bot Not Configured",
                    description="Set up your Telegram bot to start managing channels",
                    action_url="/bot/setup",
                    action_label="Configure Bot",
                    created_at=datetime.now(UTC),
                )
            )
            # If no bot, no point checking other alerts
            return alerts

        # ==============================================
        # CRITICAL ALERT 2: MTProto Not Configured
        # User has bot but no MTProto session
        # This blocks: data collection, analytics
        # ==============================================
        mtproto_config = await conn.fetchrow(
            """
            SELECT mtproto_enabled, session_string, telegram_api_id, telegram_api_hash
            FROM user_bot_credentials 
            WHERE user_id = $1 AND status = 'active'
        """,
            user_id,
        )

        if mtproto_config:
            has_mtproto_credentials = (
                mtproto_config["telegram_api_id"] is not None
                and mtproto_config["telegram_api_hash"] is not None
            )
            has_session = mtproto_config["session_string"] is not None
            mtproto_config["mtproto_enabled"]

            if not has_mtproto_credentials:
                alerts.append(
                    ActionAlert(
                        id="no_mtproto_credentials",
                        type="critical",
                        title="MTProto Not Configured",
                        description="Connect your Telegram account to enable data collection",
                        action_url="/settings/mtproto-setup",
                        action_label="Connect Account",
                        created_at=datetime.now(UTC),
                    )
                )
                return alerts

            if not has_session:
                alerts.append(
                    ActionAlert(
                        id="mtproto_session_missing",
                        type="critical",
                        title="MTProto Session Required",
                        description="Complete phone verification to start collecting data",
                        action_url="/settings/mtproto-setup",
                        action_label="Verify Phone",
                        created_at=datetime.now(UTC),
                    )
                )
                return alerts

        # ==============================================
        # CRITICAL ALERT 3: No Channels Added
        # User has bot + MTProto but no channels
        # ==============================================
        channel_count = await conn.fetchval(
            "SELECT COUNT(*) FROM channels WHERE user_id = $1", user_id
        )

        if channel_count == 0:
            alerts.append(
                ActionAlert(
                    id="no_channels",
                    type="critical",
                    title="No Channels Added",
                    description="Add your first Telegram channel to start tracking",
                    action_url="/channels",
                    action_label="Add Channel",
                    created_at=datetime.now(UTC),
                )
            )
            return alerts

        # ==============================================
        # CRITICAL ALERT 4: MTProto Collection Disabled for All Channels
        # User has everything but disabled data collection
        # ==============================================
        mtproto_enabled_channels = await conn.fetchval(
            """
            SELECT COUNT(*) 
            FROM channel_mtproto_settings cms
            JOIN channels c ON cms.channel_id = c.id AND cms.user_id = c.user_id
            WHERE c.user_id = $1
            AND cms.mtproto_enabled = true
        """,
            user_id,
        )

        if mtproto_enabled_channels == 0 and channel_count > 0:
            alerts.append(
                ActionAlert(
                    id="mtproto_disabled_all",
                    type="critical",
                    title="Data Collection Disabled",
                    description="Enable data collection for your channels to get analytics",
                    action_url="/settings/mtproto-monitoring",
                    action_label="Enable Collection",
                    created_at=datetime.now(UTC),
                )
            )

        # ==============================================
        # CRITICAL ALERT 5: MTProto Session Expired/Disconnected
        # Check if last successful sync was too long ago (48+ hours)
        # This indicates session issues, not just no new posts
        # ==============================================
        if mtproto_enabled_channels > 0:
            last_successful_sync = await conn.fetchval(
                """
                SELECT MAX(mal.timestamp)
                FROM mtproto_audit_log mal
                WHERE mal.user_id = $1
                AND mal.action IN ('collection_progress', 'collection_completed', 'channel_data_collected')
            """,
                user_id,
            )

            if last_successful_sync:
                hours_since_sync = (datetime.now(UTC) - last_successful_sync).total_seconds() / 3600
                if hours_since_sync > 48:
                    alerts.append(
                        ActionAlert(
                            id="mtproto_session_stale",
                            type="critical",
                            title="Data Collection Stopped",
                            description=f"No data collected in {int(hours_since_sync)} hours. Session may have expired.",
                            action_url="/settings/mtproto-monitoring",
                            action_label="Check Status",
                            created_at=datetime.now(UTC),
                        )
                    )

    return alerts


async def _get_today_stats(pool, user_id: int) -> TodayStats:
    """Get today's snapshot statistics with daily changes"""
    stats = TodayStats()

    async with pool.acquire() as conn:
        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        week_start = today_start - timedelta(days=7)

        # Total subscribers across all channels
        total_subs = await conn.fetchval(
            """
            SELECT COALESCE(SUM(subscriber_count), 0)
            FROM channels
            WHERE user_id = $1
        """,
            user_id,
        )
        stats.total_subscribers = total_subs or 0

        # Posts today
        posts_today = await conn.fetchval(
            """
            SELECT COUNT(*)
            FROM posts p
            JOIN channels c ON p.channel_id = c.id
            WHERE c.user_id = $1
            AND p.date >= $2
        """,
            user_id,
            today_start,
        )
        stats.posts_today = posts_today or 0

        # Posts this week
        posts_week = await conn.fetchval(
            """
            SELECT COUNT(*)
            FROM posts p
            JOIN channels c ON p.channel_id = c.id
            WHERE c.user_id = $1
            AND p.date >= $2
        """,
            user_id,
            week_start,
        )
        stats.posts_this_week = posts_week or 0

        # Today's views (latest snapshot per post from today)
        today_views = await conn.fetchval(
            """
            SELECT COALESCE(SUM(latest_views), 0)
            FROM (
                SELECT DISTINCT ON (pm.channel_id, pm.msg_id) pm.views as latest_views
                FROM post_metrics pm
                JOIN channels c ON pm.channel_id = c.id
                WHERE c.user_id = $1
                AND DATE(pm.snapshot_time) = CURRENT_DATE
                ORDER BY pm.channel_id, pm.msg_id, pm.snapshot_time DESC
            ) latest
        """,
            user_id,
        )
        stats.total_views = int(today_views) if today_views else 0

        # Yesterday's views (latest snapshot per post from yesterday)
        yesterday_views = await conn.fetchval(
            """
            SELECT COALESCE(SUM(latest_views), 0)
            FROM (
                SELECT DISTINCT ON (pm.channel_id, pm.msg_id) pm.views as latest_views
                FROM post_metrics pm
                JOIN channels c ON pm.channel_id = c.id
                WHERE c.user_id = $1
                AND DATE(pm.snapshot_time) = CURRENT_DATE - 1
                ORDER BY pm.channel_id, pm.msg_id, pm.snapshot_time DESC
            ) latest
        """,
            user_id,
        )
        yesterday_views = int(yesterday_views) if yesterday_views else 0

        # Calculate views gained today
        stats.views_gained_today = max(0, stats.total_views - yesterday_views)
        if yesterday_views > 0:
            stats.views_change_percent = round(
                (stats.views_gained_today / yesterday_views) * 100, 1
            )

        # Best performing post TODAY (only posts published today)
        best_post = await conn.fetchrow(
            """
            SELECT p.msg_id, COALESCE(LEFT(p.text, 50), 'Untitled Post') as title,
                   COALESCE(pm.views, 0) as views, c.id as channel_id
            FROM posts p
            JOIN channels c ON p.channel_id = c.id
            LEFT JOIN LATERAL (
                SELECT views FROM post_metrics 
                WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                ORDER BY snapshot_time DESC LIMIT 1
            ) pm ON true
            WHERE c.user_id = $1
            AND p.date >= $2
            ORDER BY pm.views DESC NULLS LAST
            LIMIT 1
        """,
            user_id,
            today_start,
        )

        if best_post and best_post["views"] > 0:
            title = best_post["title"]
            if len(title) >= 50:
                title = title + "..."
            stats.best_post_title = title
            stats.best_post_views = best_post["views"]
            stats.best_post_id = best_post["msg_id"]
            stats.best_post_channel_id = best_post["channel_id"]

    return stats


async def _get_channel_health(pool, user_id: int) -> list[ChannelHealth]:
    """Get health status for all user channels"""
    channels = []

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT 
                c.id, c.title as name, c.username, c.subscriber_count,
                cms.mtproto_enabled,
                (SELECT MAX(p.date) FROM posts p WHERE p.channel_id = c.id) as last_collected_at,
                EXISTS(SELECT 1 FROM user_bot_credentials WHERE user_id = $1 AND status = 'active') as has_bot
            FROM channels c
            LEFT JOIN channel_mtproto_settings cms ON c.id = cms.channel_id AND cms.user_id = c.user_id
            WHERE c.user_id = $1
            ORDER BY c.title
        """,
            user_id,
        )

        for row in rows:
            channel_id = row["id"]

            # Get post stats for this channel
            stats = await conn.fetchrow(
                """
                SELECT 
                    COUNT(p.msg_id) as total_posts,
                    MAX(p.date) as last_post_time,
                    COALESCE(AVG(pm.views), 0) as avg_views,
                    COALESCE(AVG(
                        CASE WHEN pm.views > 0 
                        THEN (COALESCE(pm.reactions_count, 0) + COALESCE(pm.forwards, 0))::float / pm.views * 100 
                        ELSE 0 END
                    ), 0) as engagement_rate
                FROM posts p
                LEFT JOIN LATERAL (
                    SELECT views, reactions_count, forwards FROM post_metrics
                    WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                    ORDER BY snapshot_time DESC LIMIT 1
                ) pm ON true
                WHERE p.channel_id = $1
                AND p.date >= NOW() - INTERVAL '30 days'
            """,
                channel_id,
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
                    subscriber_growth_week=0,  # No historical data
                    avg_views=int(stats["avg_views"]) if stats else 0,
                    last_post_time=stats["last_post_time"] if stats else None,
                    last_post_ago=(
                        _time_ago(stats["last_post_time"])
                        if stats and stats["last_post_time"]
                        else None
                    ),
                    engagement_rate=(round(stats["engagement_rate"], 2) if stats else 0.0),
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
        # Get recent MTProto setting changes (enable/disable actions)
        settings_changes = await conn.fetch(
            """
            SELECT 
                mal.id, mal.channel_id, c.title as channel_name,
                mal.action, mal.timestamp
            FROM mtproto_audit_log mal
            JOIN channels c ON mal.channel_id = c.id
            WHERE c.user_id = $1
            AND mal.timestamp >= NOW() - INTERVAL '7 days'
            ORDER BY mal.timestamp DESC
            LIMIT 3
        """,
            user_id,
        )

        for change in settings_changes:
            action = change["action"]
            if action == "enabled":
                message = "MTProto data collection enabled"
                icon = "✅"
            elif action == "disabled":
                message = "MTProto data collection disabled"
                icon = "⏸️"
            else:
                message = f"Settings updated: {action}"
                icon = "⚙️"

            activities.append(
                ActivityItem(
                    id=f"setting_{change['id']}",
                    type="settings",
                    icon=icon,
                    message=message,
                    channel_name=change["channel_name"],
                    channel_id=change["channel_id"],
                    timestamp=change["timestamp"],
                    time_ago=_time_ago(change["timestamp"]),
                )
            )

        # Get recent posts
        posts = await conn.fetch(
            """
            SELECT 
                p.msg_id, p.channel_id, c.title as channel_name,
                COALESCE(LEFT(p.text, 50), 'New post') as title,
                p.date as timestamp,
                pm.views
            FROM posts p
            JOIN channels c ON p.channel_id = c.id
            LEFT JOIN LATERAL (
                SELECT views FROM post_metrics 
                WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                ORDER BY snapshot_time DESC LIMIT 1
            ) pm ON true
            WHERE c.user_id = $1
            AND p.date >= NOW() - INTERVAL '24 hours'
            ORDER BY p.date DESC
            LIMIT 5
        """,
            user_id,
        )

        for post in posts:
            views = post["views"] or 0
            title = post["title"]
            if len(title) >= 50:
                title = title + "..."
            activities.append(
                ActivityItem(
                    id=f"post_{post['channel_id']}_{post['msg_id']}",
                    type="post",
                    icon="📝",
                    message=f'"{title}" - {views:,} views',
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
    has_channels: bool, has_bot: bool, has_mtproto: bool
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


async def _get_sparkline_data(pool, user_id: int) -> tuple[list[int], list[str]]:
    """Get 7-day performance sparkline data (posts per day)"""
    views_data = []
    labels = []

    async with pool.acquire() as conn:
        # Get posts count per day for last 7 days
        for i in range(6, -1, -1):  # 6 days ago to today
            day = datetime.now(UTC) - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            # Count posts on this day
            count = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM posts p
                JOIN channels c ON p.channel_id = c.id
                WHERE c.user_id = $1
                AND p.date >= $2 AND p.date < $3
            """,
                user_id,
                day_start,
                day_end,
            )

            views_data.append(count or 0)
            labels.append(day.strftime("%a"))  # Mon, Tue, Wed, etc.

    return views_data, labels


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
            user = await conn.fetchrow(
                "SELECT id, username, last_login FROM users WHERE id = $1", user_id
            )

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Check what user has configured
            has_channels = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM channels WHERE user_id = $1)", user_id
            )

            has_bot = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM user_bot_credentials WHERE user_id = $1 AND status = 'active')",
                user_id,
            )

            has_mtproto = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM channel_mtproto_settings WHERE user_id = $1 AND mtproto_enabled = true)",
                user_id,
            )

        # Fetch all dashboard data
        alerts = await _get_user_alerts(pool, user_id)
        today = await _get_today_stats(pool, user_id)
        channels = await _get_channel_health(pool, user_id)
        activity = await _get_activity_feed(pool, user_id)
        quick_actions = await _get_quick_actions(has_channels, has_bot, has_mtproto)
        sparkline_views, sparkline_labels = await _get_sparkline_data(pool, user_id)

        # Generate smart welcome message
        welcome = _get_smart_welcome(
            username=user["username"],
            last_login=user.get("last_login"),
            has_channels=has_channels,
            posts_today=today.posts_today,
            views_gained=today.views_gained_today,
        )

        return HomeDashboardResponse(
            user_id=user_id,
            username=user["username"],
            welcome=welcome,
            alerts=alerts,
            today=today,
            channels=channels,
            activity=activity,
            quick_actions=quick_actions,
            sparkline_views=sparkline_views,
            sparkline_labels=sparkline_labels,
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
