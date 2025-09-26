import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext
from apps.bot.clients.analytics_v2_client import (
    AnalyticsV2Client,
    AnalyticsV2ClientError,
    GrowthResponse,
    OverviewResponse,
    ReachResponse,
    SourcesResponse,
    TopPostsResponse,
    TrendingResponse,
)

from apps.bot.keyboards.analytics import (
    kb_alerts_main,
    kb_channels,
    kb_export,
    kb_periods,
    kb_tabs,
)
from apps.bot.middleware.throttle import throttle
from infra.db.repositories import AsyncpgChannelRepository as ChannelRepository

"""
Analytics V2 Bot Handlers
Provides interactive analytics interface using API v2 data
"""


def _get_settings():
    """Get settings instance with proper error handling"""
    try:
        from config.settings import Settings

        # Just return the module/class without instantiation to avoid constructor issues
        return Settings
    except Exception:
        # Fallback mock settings
        class MockSettings:
            BOT_ANALYTICS_UI_ENABLED = True
            ANALYTICS_V2_BASE_URL = "http://localhost:8000"
            ANALYTICS_V2_TOKEN = None
            EXPORT_ENABLED = True
            ALERTS_ENABLED = True
            SHARE_LINKS_ENABLED = True

        return MockSettings()


def _safe_callback_data_split(
    callback_data: str | None, separator: str = ":", index: int = 1
) -> str | None:
    """Safely split callback data and return the requested part"""
    if not callback_data:
        return None
    try:
        parts = callback_data.split(separator)
        if len(parts) > index:
            return parts[index]
        return None
    except (AttributeError, IndexError):
        return None


async def _safe_edit_message(callback: CallbackQuery, text: str, reply_markup=None) -> bool:
    """Safely edit callback message with type checking"""
    try:
        from aiogram.types import Message

        if (
            callback.message
            and isinstance(callback.message, Message)
            and hasattr(callback.message, "edit_text")
        ):
            await callback.message.edit_text(text, reply_markup=reply_markup)  # type: ignore
            return True
        return False
    except Exception:
        return False


logger = logging.getLogger(__name__)

# Create router for analytics v2 handlers
router = Router()


def _get_user_id(event) -> int | None:
    """Extract user ID from message or callback"""
    if hasattr(event, "from_user") and event.from_user:
        return event.from_user.id
    return None


def _format_number(num: int) -> str:
    """Format large numbers with K/M suffixes"""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)


def _format_percentage(num: float) -> str:
    """Format percentage with sign"""
    sign = "+" if num > 0 else ""
    return f"{sign}{num:.1f}%"


def _format_overview_text(data: OverviewResponse) -> str:
    """Format overview data as user-friendly text"""
    overview = data.overview

    # Main metrics
    lines = [
        "📊 **Channel Overview**",
        (
            "🗓 Period: "
            + f"{data.period}"
            + "days ( "
            + f"{data.period_start.strftime('%m/%d')}"
            + "- "
            + f"{data.period_end.strftime('%m/%d')}"
            + " )"
        ),
        "",
        f"👥 **Subscribers:** {_format_number(overview.subscribers)}",
        (
            "📈 **Growth:** "
            + f"{_format_number(overview.subscriber_growth)}"
            + "( "
            + f"{_format_percentage(overview.subscriber_growth / max(overview.subscribers - overview.subscriber_growth, 1) * 100)}"
            + " )"
        ),
        "",
        f"📝 **Posts:** {overview.total_posts}",
        f"👁️ **Total Views:** {_format_number(overview.total_views)}",
        f"📊 **Avg Views/Post:** {_format_number(int(overview.average_views_per_post))}",
        f"💫 **Engagement Rate:** {overview.engagement_rate:.1f}%",
        "",
        f"📡 **Data Sources:** {', '.join(data.data_sources)}",
        f"🕐 **Last Updated:** {data.last_updated.strftime('%H:%M %m/%d/%Y')}",
    ]

    if data.cache_hit:
        lines.append("⚡ *Cached data*")

    return "\n".join(lines)


def _format_growth_text(data: GrowthResponse) -> str:
    """Format growth data as user-friendly text"""
    growth = data.growth

    lines = [
        "📈 **Growth Analytics**",
        f"🗓 Period: {data.period} days",
        "",
        f"📊 **Total Growth:** {_format_number(growth.subscriber_growth)}",
        f"📈 **Growth Rate:** {_format_percentage(growth.growth_rate)}",
        "",
        "📅 **Recent Daily Growth:**",
    ]

    # Show last 7 days of growth
    recent_growth = (
        growth.daily_growth[-7:] if len(growth.daily_growth) > 7 else growth.daily_growth
    )
    for day_data in recent_growth:
        date = datetime.fromisoformat(day_data["date"]).strftime("%m/%d")
        change = day_data.get("change", 0)
        subscribers = day_data.get("subscribers", 0)
        lines.append(
            "• "
            + f"{date}"
            + ": "
            + f"{_format_number(subscribers)}"
            + "( "
            + f"{_format_percentage(change) if change else '—'}"
            + " )"
        )

    lines.extend(
        [
            "",
            f"📡 **Data Sources:** {', '.join(data.data_sources)}",
            f"🕐 **Last Updated:** {data.last_updated.strftime('%H:%M %m/%d/%Y')}",
        ]
    )

    return "\n".join(lines)


def _format_reach_text(data: ReachResponse) -> str:
    """Format reach data as user-friendly text"""
    reach = data.reach

    lines = [
        "👁️ **Reach Analytics**",
        f"🗓 Period: {data.period} days",
        "",
        f"👀 **Total Views:** {_format_number(reach.total_views)}",
        f"👤 **Unique Viewers:** {_format_number(reach.unique_viewers)}",
        f"📊 **View/Reach Ratio:** {reach.view_reach_ratio:.1f}",
        f"🔥 **Peak Concurrent:** {_format_number(reach.peak_concurrent)}",
        "",
        "⏰ **Top Active Hours:**",
    ]

    # Show top 5 active hours
    hourly_sorted = sorted(reach.hourly_distribution.items(), key=lambda x: int(x[1]), reverse=True)
    for hour, views in hourly_sorted[:5]:
        lines.append(f"• {hour}:00 - {_format_number(int(views))} views")

    lines.extend(
        [
            "",
            f"📡 **Data Sources:** {', '.join(data.data_sources)}",
            f"🕐 **Last Updated:** {data.last_updated.strftime('%H:%M %m/%d/%Y')}",
        ]
    )

    return "\n".join(lines)


def _format_top_posts_text(data: TopPostsResponse) -> str:
    """Format top posts data as user-friendly text"""
    lines = ["🔥 **Top Posts**", f"🗓 Period: {data.period} days", ""]

    for i, post in enumerate(data.top_posts[:10], 1):
        # Truncate long messages
        message_preview = post.message[:80] + "..." if len(post.message) > 80 else post.message
        message_preview = message_preview.replace("\n", " ")

        lines.extend(
            [
                f"**{i}. Post #{post.post_id}**",
                f"📝 {message_preview}",
                (
                    "👁️ Views: "
                    + f"{_format_number(post.views)}"
                    + "| 🔄 Forwards: "
                    + f"{_format_number(post.forwards)}"
                    + "| 💫 Score: "
                    + f"{post.engagement_score:.1f}"
                ),
                f"📅 {post.published_at.strftime('%m/%d/%Y %H:%M')}",
                "",
            ]
        )

    lines.extend(
        [
            f"📡 **Data Sources:** {', '.join(data.data_sources)}",
            f"🕐 **Last Updated:** {data.last_updated.strftime('%H:%M %m/%d/%Y')}",
        ]
    )

    return "\n".join(lines)


def _format_sources_text(data: SourcesResponse) -> str:
    """Format sources data as user-friendly text"""
    sources = data.sources

    lines = [
        "🌊 **Traffic Sources**",
        f"🗓 Period: {data.period} days",
        "",
        (
            "🎯 **Direct:** "
            + f"{_format_number(sources.direct.get('views', 0))}"
            + "( "
            + f"{sources.direct.get('percentage', 0):.1f}"
            + " %)"
        ),
        (
            "🔄 **Forwards:** "
            + f"{_format_number(sources.forwards.get('views', 0))}"
            + "( "
            + f"{sources.forwards.get('percentage', 0):.1f}"
            + " %)"
        ),
        (
            "🔗 **Links:** "
            + f"{_format_number(sources.links.get('views', 0))}"
            + "( "
            + f"{sources.links.get('percentage', 0):.1f}"
            + " %)"
        ),
        (
            "🔍 **Search:** "
            + f"{_format_number(sources.search.get('views', 0))}"
            + "( "
            + f"{sources.search.get('percentage', 0):.1f}"
            + " %)"
        ),
        "",
    ]

    if sources.referral_channels:
        lines.append("📺 **Top Referral Channels:**")
        for referrer in sources.referral_channels[:5]:
            channel = referrer.get("channel", "Unknown")
            views = referrer.get("views", 0)
            conversion = referrer.get("conversion_rate", 0)
            lines.append(f"• {channel}: {_format_number(views)} views ({conversion:.1f}% conv.)")
        lines.append("")

    lines.extend(
        [
            f"📡 **Data Sources:** {', '.join(data.data_sources)}",
            f"🕐 **Last Updated:** {data.last_updated.strftime('%H:%M %m/%d/%Y')}",
        ]
    )

    return "\n".join(lines)


def _format_trending_text(data: TrendingResponse) -> str:
    """Format trending data as user-friendly text"""
    trending = data.trending

    status_emoji = "🔥" if trending.is_trending else "😴"
    direction_emoji = {"up": "📈", "down": "📉", "stable": "➡️"}.get(trending.trend_direction, "➡️")
    confidence_emoji = {"high": "🎯", "medium": "📊", "low": "❓"}.get(trending.confidence, "📊")

    lines = [
        "📊 **Trending Analysis**",
        f"🗓 Period: {data.period} days",
        "",
        f"{status_emoji} **Status:** {'TRENDING' if trending.is_trending else 'Not Trending'}",
        f"{direction_emoji} **Direction:** {trending.trend_direction.title()}",
        f"🎯 **Trend Score:** {trending.trend_score:.2f}",
        f"{confidence_emoji} **Confidence:** {trending.confidence.title()}",
        "",
        f"📈 **Z-Score:** {trending.z_score:.2f}",
        f"📊 **EWMA Score:** {trending.ewma_score:.2f}",
        "",
        f"💡 **Analysis:** {trending.analysis}",
        "",
        f"📡 **Data Sources:** {', '.join(data.data_sources)}",
        f"🕐 **Last Updated:** {data.last_updated.strftime('%H:%M %m/%d/%Y')}",
    ]

    return "\n".join(lines)


async def _get_user_channels(
    user_id: int, channel_repo: ChannelRepository
) -> list[tuple[str, str]]:
    """Get channels for user"""
    try:
        # Mock channels since repository method doesn't exist yet
        channels = [
            {"id": "demo_channel", "name": "Demo Channel"},
            {"id": "test_channel", "name": "Test Channel"},
        ]

        # Format channels for display
        channel_list = [
            (
                ch.get("name", f"Channel {ch.get('id', 'Unknown')}"),
                str(ch.get("id", "unknown")),
            )
            for ch in channels
        ]
        return channel_list
    except Exception as e:
        logger.error(f"Failed to get user channels: {e}")
        return []


@router.message(Command("analytics"))
@throttle(rate=2.0)
async def cmd_analytics(
    message: Message,
    i18n: I18nContext,
    channel_repo: ChannelRepository,
):
    """Main analytics command - feature flagged"""
    settings = _get_settings()

    if not settings.BOT_ANALYTICS_UI_ENABLED:
        await message.answer("🚧 Analytics UI feature is currently disabled. Coming soon!")
        return

    user_id = _get_user_id(message)
    if not user_id:
        await message.answer("❌ Unable to identify user.")
        return

    try:
        # Get user channels
        channels = await _get_user_channels(user_id, channel_repo)

        if not channels:
            await message.answer(
                "📺 No channels found. Add a channel first using /add_channel @channelname",
                reply_markup=None,
            )
            return

        # Show channel selection
        await message.answer(
            "📊 **Analytics Dashboard**\n\nSelect a channel to analyze:",
            reply_markup=kb_channels(channels),
        )

    except Exception as e:
        logger.error(f"Analytics command failed: {e}")
        await message.answer("❌ Failed to load analytics. Please try again later.")


@router.callback_query(F.data.startswith("channel:"))
@throttle(rate=1.0)
async def choose_channel(callback: CallbackQuery, i18n: I18nContext):
    """Handle channel selection"""
    try:
        if not callback.data:
            await callback.answer("❌ Invalid callback data")
            return

        channel_id = callback.data.split(":")[1]

        # Show period selection
        if callback.message:
            await _safe_edit_message(
                callback,
                f"📊 **Analytics for Channel {channel_id}**\n\nSelect time period:",
                reply_markup=kb_periods(),
            )

            # Store channel ID for next step (simplified state management)
            callback.message._selected_channel = channel_id
        await callback.answer()

    except Exception as e:
        logger.error(f"Channel selection failed: {e}")
        await callback.answer("❌ Failed to select channel", show_alert=True)


@router.callback_query(F.data.startswith("period:"))
@throttle(rate=1.0)
async def choose_period(callback: CallbackQuery, i18n: I18nContext):
    """Handle period selection and show overview"""
    settings = _get_settings()

    try:
        if not callback.data:
            await callback.answer("❌ Invalid callback data")
            return
        period = int(callback.data.split(":")[1])

        # Get stored channel ID (in real implementation, use state management)
        channel_id = getattr(callback.message, "_selected_channel", "demo_channel")

        # Create analytics client
        async with AnalyticsV2Client(
            base_url=settings.ANALYTICS_V2_BASE_URL,
            token=(
                settings.ANALYTICS_V2_TOKEN.get_secret_value()
                if settings.ANALYTICS_V2_TOKEN
                else None
            ),
        ) as client:
            # Get overview data
            overview_data = await client.overview(channel_id, period)

            # Format and send overview
            text = _format_overview_text(overview_data)
            await _safe_edit_message(callback, text, reply_markup=kb_tabs(channel_id, period))

        await callback.answer()

    except AnalyticsV2ClientError as e:
        await callback.answer(f"❌ API Error: {e}", show_alert=True)
    except Exception as e:
        logger.error(f"Period selection failed: {e}")
        await callback.answer("❌ Failed to load analytics", show_alert=True)


@router.callback_query(F.data.startswith("analytics:overview:"))
@throttle(rate=1.0)
async def show_overview(callback: CallbackQuery, i18n: I18nContext):
    """Show overview analytics"""
    settings = _get_settings()

    try:
        parts = _safe_callback_data_split(callback.data, ":", 0) or []
        channel_id, period = parts[2], int(parts[3])

        async with AnalyticsV2Client(
            base_url=settings.ANALYTICS_V2_BASE_URL,
            token=(
                settings.ANALYTICS_V2_TOKEN.get_secret_value()
                if settings.ANALYTICS_V2_TOKEN
                else None
            ),
        ) as client:
            data = await client.overview(channel_id, period)
            text = _format_overview_text(data)

            await _safe_edit_message(callback, text, reply_markup=kb_tabs(channel_id, period))

        await callback.answer()

    except AnalyticsV2ClientError as e:
        await callback.answer(f"❌ API Error: {e}", show_alert=True)
    except Exception as e:
        logger.error(f"Overview failed: {e}")
        await callback.answer("❌ Failed to load overview", show_alert=True)


@router.callback_query(F.data.startswith("analytics:growth:"))
@throttle(rate=1.0)
async def show_growth(callback: CallbackQuery, i18n: I18nContext):
    """Show growth analytics"""
    settings = _get_settings()

    try:
        parts = _safe_callback_data_split(callback.data, ":", 0) or []
        channel_id, period = parts[2], int(parts[3])

        async with AnalyticsV2Client(
            base_url=settings.ANALYTICS_V2_BASE_URL,
            token=(
                settings.ANALYTICS_V2_TOKEN.get_secret_value()
                if settings.ANALYTICS_V2_TOKEN
                else None
            ),
        ) as client:
            data = await client.growth(channel_id, period)
            text = _format_growth_text(data)

            await _safe_edit_message(callback, text, reply_markup=kb_tabs(channel_id, period))

        await callback.answer()

    except AnalyticsV2ClientError as e:
        await callback.answer(f"❌ API Error: {e}", show_alert=True)
    except Exception as e:
        logger.error(f"Growth analytics failed: {e}")
        await callback.answer("❌ Failed to load growth data", show_alert=True)


@router.callback_query(F.data.startswith("analytics:reach:"))
@throttle(rate=1.0)
async def show_reach(callback: CallbackQuery, i18n: I18nContext):
    """Show reach analytics"""
    settings = _get_settings()

    try:
        parts = _safe_callback_data_split(callback.data, ":", 0) or []
        channel_id, period = parts[2], int(parts[3])

        async with AnalyticsV2Client(
            base_url=settings.ANALYTICS_V2_BASE_URL,
            token=(
                settings.ANALYTICS_V2_TOKEN.get_secret_value()
                if settings.ANALYTICS_V2_TOKEN
                else None
            ),
        ) as client:
            data = await client.reach(channel_id, period)
            text = _format_reach_text(data)

            await _safe_edit_message(callback, text, reply_markup=kb_tabs(channel_id, period))

        await callback.answer()

    except AnalyticsV2ClientError as e:
        await callback.answer(f"❌ API Error: {e}", show_alert=True)
    except Exception as e:
        logger.error(f"Reach analytics failed: {e}")
        await callback.answer("❌ Failed to load reach data", show_alert=True)


@router.callback_query(F.data.startswith("analytics:top_posts:"))
@throttle(rate=1.0)
async def show_top_posts(callback: CallbackQuery, i18n: I18nContext):
    """Show top posts analytics"""
    settings = _get_settings()

    try:
        parts = _safe_callback_data_split(callback.data, ":", 0) or []
        channel_id, period = parts[2], int(parts[3])

        async with AnalyticsV2Client(
            base_url=settings.ANALYTICS_V2_BASE_URL,
            token=(
                settings.ANALYTICS_V2_TOKEN.get_secret_value()
                if settings.ANALYTICS_V2_TOKEN
                else None
            ),
        ) as client:
            data = await client.top_posts(channel_id, period, limit=10)
            text = _format_top_posts_text(data)

            await _safe_edit_message(callback, text, reply_markup=kb_tabs(channel_id, period))

        await callback.answer()

    except AnalyticsV2ClientError as e:
        await callback.answer(f"❌ API Error: {e}", show_alert=True)
    except Exception as e:
        logger.error(f"Top posts analytics failed: {e}")
        await callback.answer("❌ Failed to load top posts", show_alert=True)


@router.callback_query(F.data.startswith("analytics:sources:"))
@throttle(rate=1.0)
async def show_sources(callback: CallbackQuery, i18n: I18nContext):
    """Show sources analytics"""
    settings = _get_settings()

    try:
        parts = _safe_callback_data_split(callback.data, ":", 0) or []
        channel_id, period = parts[2], int(parts[3])

        async with AnalyticsV2Client(
            base_url=settings.ANALYTICS_V2_BASE_URL,
            token=(
                settings.ANALYTICS_V2_TOKEN.get_secret_value()
                if settings.ANALYTICS_V2_TOKEN
                else None
            ),
        ) as client:
            data = await client.sources(channel_id, period)
            text = _format_sources_text(data)

            await _safe_edit_message(callback, text, reply_markup=kb_tabs(channel_id, period))

        await callback.answer()

    except AnalyticsV2ClientError as e:
        await callback.answer(f"❌ API Error: {e}", show_alert=True)
    except Exception as e:
        logger.error(f"Sources analytics failed: {e}")
        await callback.answer("❌ Failed to load sources data", show_alert=True)


@router.callback_query(F.data.startswith("analytics:trending:"))
@throttle(rate=1.0)
async def show_trending(callback: CallbackQuery, i18n: I18nContext):
    """Show trending analytics"""
    settings = _get_settings()

    try:
        parts = _safe_callback_data_split(callback.data, ":", 0) or []
        channel_id, period = parts[2], int(parts[3])

        async with AnalyticsV2Client(
            base_url=settings.ANALYTICS_V2_BASE_URL,
            token=(
                settings.ANALYTICS_V2_TOKEN.get_secret_value()
                if settings.ANALYTICS_V2_TOKEN
                else None
            ),
        ) as client:
            data = await client.trending(channel_id, period)
            text = _format_trending_text(data)

            await _safe_edit_message(callback, text, reply_markup=kb_tabs(channel_id, period))

        await callback.answer()

    except AnalyticsV2ClientError as e:
        await callback.answer(f"❌ API Error: {e}", show_alert=True)
    except Exception as e:
        logger.error(f"Trending analytics failed: {e}")
        await callback.answer("❌ Failed to load trending data", show_alert=True)


@router.callback_query(F.data.startswith("analytics:export:"))
@throttle(rate=3.0)  # Slower rate for exports
async def show_export_options(callback: CallbackQuery, i18n: I18nContext):
    """Show export options"""
    settings = _get_settings()

    if not settings.EXPORT_ENABLED:
        await callback.answer(
            "🚧 Export feature is currently disabled. Coming soon!", show_alert=True
        )
        return

    try:
        parts = _safe_callback_data_split(callback.data, ":", 0) or []
        channel_id, period = parts[2], int(parts[3])

        await _safe_edit_message(
            callback,
            (
                "📤 **Export Options**\n\nChannel: "
                + f"{channel_id}"
                + "\nPeriod: "
                + f"{period}"
                + " days\n\nChoose export format:"
            ),
            reply_markup=kb_export(channel_id, period),
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Export options failed: {e}")
        await callback.answer("❌ Failed to show export options", show_alert=True)


@router.callback_query(F.data.startswith("analytics:alerts:"))
@throttle(rate=2.0)
async def show_alerts_options(callback: CallbackQuery, i18n: I18nContext):
    """Show alerts options"""
    settings = _get_settings()

    if not settings.ALERTS_ENABLED:
        await callback.answer(
            "🚧 Alerts feature is currently disabled. Coming soon!", show_alert=True
        )
        return

    try:
        parts = _safe_callback_data_split(callback.data, ":", 0) or []
        channel_id = parts[2]

        await _safe_edit_message(
            callback,
            f"🔔 **Alert Management**\n\nChannel: {channel_id}\n\nManage your alert subscriptions:",
            reply_markup=kb_alerts_main(channel_id),
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Alerts options failed: {e}")
        await callback.answer("❌ Failed to show alerts options", show_alert=True)


@router.callback_query(F.data.startswith("analytics:share:"))
@throttle(rate=2.0)
async def show_share_options(callback: CallbackQuery, i18n: I18nContext):
    """Show share options"""
    settings = _get_settings()

    if not settings.SHARE_LINKS_ENABLED:
        await callback.answer(
            "🚧 Share links feature is currently disabled. Coming soon!",
            show_alert=True,
        )
        return

    try:
        parts = _safe_callback_data_split(callback.data, ":", 0) or []
        channel_id, period = parts[2], int(parts[3])

        await callback.answer("🔗 Share links feature coming soon!", show_alert=True)

    except Exception as e:
        logger.error(f"Share options failed: {e}")
        await callback.answer("❌ Failed to show share options", show_alert=True)


# Navigation handlers
@router.callback_query(F.data == "analytics:back")
async def handle_back(callback: CallbackQuery):
    """Handle back navigation"""
    await _safe_edit_message(callback, "📊 Select time period:", reply_markup=kb_periods())
    await callback.answer()


@router.callback_query(F.data == "analytics:channels")
async def show_channels_again(callback: CallbackQuery, channel_repo: ChannelRepository):
    """Show channels selection again"""
    user_id = _get_user_id(callback)
    if user_id:
        channels = await _get_user_channels(user_id, channel_repo)
        await _safe_edit_message(
            callback,
            "📊 **Analytics Dashboard**\n\nSelect a channel to analyze:",
            reply_markup=kb_channels(channels),
        )
    await callback.answer()
