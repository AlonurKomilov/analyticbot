"""
Alert Management Bot Handlers
Provides interactive alert configuration and management
"""

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

from apps.bot.keyboards.analytics import kb_alert_types, kb_alerts_main, kb_confirmation
from apps.bot.middlewares.throttle import throttle
from config.settings import Settings
from core.repositories.alert_repository import AlertSubscription
from infra.db.repositories.alert_repository import AsyncpgAlertSubscriptionRepository

logger = logging.getLogger(__name__)

# Create router for alerts handlers
router = Router()


def _get_user_id(event) -> int | None:
    """Extract user ID from message or callback"""
    if hasattr(event, "from_user") and event.from_user:
        return event.from_user.id
    return None


def _get_chat_id(event) -> int | None:
    """Extract chat ID from message or callback"""
    if hasattr(event, "chat") and event.chat:
        return event.chat.id
    elif hasattr(event, "message") and event.message and event.message.chat:
        return event.message.chat.id
    return None


def _format_alert_subscription(sub: AlertSubscription) -> str:
    """Format alert subscription for display"""
    status = "🟢 Active" if sub.enabled else "🔴 Disabled"

    if sub.kind == "spike":
        description = f"Spike Alert (Z-score ≥ {sub.threshold or 2.0})"
    elif sub.kind == "quiet":
        description = f"Quiet Alert (No posts for {sub.window_hours}h)"
    elif sub.kind == "growth":
        description = f"Growth Alert (Growth ≥ {sub.threshold or 10.0}%)"
    else:
        description = f"Alert ({sub.kind})"

    lines = [
        f"🔔 **{description}**",
        f"📺 Channel: {sub.channel_id}",
        f"📊 Status: {status}",
        f"⏱️ Window: {sub.window_hours}h",
        f"📅 Created: {sub.created_at.strftime('%m/%d/%Y') if sub.created_at else 'Unknown'}",
    ]

    return "\n".join(lines)


@router.message(Command("alerts"))
@throttle(rate=3.0)
async def cmd_alerts(
    message: Message,
    i18n: I18nContext,
    alert_repo: AsyncpgAlertSubscriptionRepository,
):
    """Main alerts command - feature flagged"""
    settings = Settings()

    if not settings.ALERTS_ENABLED:
        await message.answer("🚧 Alerts feature is currently disabled. Coming soon!")
        return

    chat_id = _get_chat_id(message)
    if not chat_id:
        await message.answer("❌ Unable to identify chat.")
        return

    try:
        # Get user's alert subscriptions
        subscriptions = await alert_repo.get_user_subscriptions(chat_id)

        if not subscriptions:
            await message.answer(
                "🔔 **Alert Management**\n\n"
                "You don't have any alert subscriptions yet.\n"
                "Set up alerts to get notified about:\n"
                "• 🚀 Content spikes (viral posts)\n"
                "• 😴 Quiet periods (no activity)\n"
                "• 📈 Growth milestones\n\n"
                "Use /analytics to select a channel and configure alerts.",
                parse_mode="Markdown",
            )
            return

        # Show existing subscriptions
        lines = [
            "🔔 **Your Alert Subscriptions**",
            "",
        ]

        for i, sub in enumerate(subscriptions[:10], 1):  # Limit to 10 for readability
            lines.append(f"**{i}.** Channel {sub.channel_id}")
            lines.append(f"   • Type: {sub.kind.title()}")
            lines.append(f"   • Status: {'🟢 Active' if sub.enabled else '🔴 Disabled'}")
            if sub.threshold:
                lines.append(f"   • Threshold: {sub.threshold}")
            lines.append(f"   • Window: {sub.window_hours}h")
            lines.append("")

        if len(subscriptions) > 10:
            lines.append(f"... and {len(subscriptions) - 10} more")
            lines.append("")

        lines.extend(
            [
                "Use /analytics to manage alerts for specific channels.",
                "",
                f"📡 Total Active Alerts: {sum(1 for s in subscriptions if s.enabled)}",
            ]
        )

        await message.answer("\n".join(lines), parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Alerts command failed: {e}")
        await message.answer("❌ Failed to load alerts. Please try again later.")


@router.callback_query(F.data.startswith("alerts:list:"))
@throttle(rate=2.0)
async def show_channel_alerts(
    callback: CallbackQuery, i18n: I18nContext, alert_repo: AsyncpgAlertSubscriptionRepository
):
    """Show alerts for specific channel"""
    try:
        channel_id = int(callback.data.split(":")[2])
        chat_id = _get_chat_id(callback)

        if not chat_id:
            await callback.answer("❌ Unable to identify chat", show_alert=True)
            return

        # Get subscriptions for this channel and user
        all_subs = await alert_repo.get_user_subscriptions(chat_id)
        channel_subs = [sub for sub in all_subs if sub.channel_id == channel_id]

        if not channel_subs:
            await callback.message.edit_text(
                f"🔔 **Alerts for Channel {channel_id}**\n\n"
                "No alerts configured for this channel.\n\n"
                "Configure alerts to get notified about:\n"
                "• 🚀 Viral content spikes\n"
                "• 😴 Quiet periods\n"
                "• 📈 Growth milestones",
                reply_markup=kb_alerts_main(str(channel_id)),
            )
        else:
            lines = [f"🔔 **Alerts for Channel {channel_id}**", ""]

            for i, sub in enumerate(channel_subs, 1):
                lines.append(f"**{i}.** {_format_alert_subscription(sub)}")
                lines.append("")

            await callback.message.edit_text(
                "\n".join(lines),
                reply_markup=kb_alerts_main(str(channel_id)),
                parse_mode="Markdown",
            )

        await callback.answer()

    except Exception as e:
        logger.error(f"Channel alerts listing failed: {e}")
        await callback.answer("❌ Failed to load alerts", show_alert=True)


@router.callback_query(F.data.startswith("alerts:add:"))
@throttle(rate=2.0)
async def show_alert_types(callback: CallbackQuery, i18n: I18nContext):
    """Show alert types for adding new alert"""
    try:
        channel_id = callback.data.split(":")[2]

        await callback.message.edit_text(
            f"➕ **Add Alert for Channel {channel_id}**\n\n"
            "Choose alert type:\n\n"
            "🚀 **Spike Alert**: Get notified when content goes viral\n"
            "   • Triggers on high Z-score (unusual view spikes)\n"
            "   • Best for detecting viral content\n\n"
            "😴 **Quiet Alert**: Get notified during inactive periods\n"
            "   • Triggers when no posts for X hours\n"
            "   • Best for maintaining posting consistency\n\n"
            "📈 **Growth Alert**: Get notified on subscriber milestones\n"
            "   • Triggers on growth percentage thresholds\n"
            "   • Best for tracking channel growth",
            reply_markup=kb_alert_types(channel_id),
            parse_mode="Markdown",
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Alert types display failed: {e}")
        await callback.answer("❌ Failed to show alert types", show_alert=True)


@router.callback_query(F.data.startswith("alert:type:"))
@throttle(rate=2.0)
async def configure_alert_type(
    callback: CallbackQuery, i18n: I18nContext, alert_repo: AsyncpgAlertSubscriptionRepository
):
    """Configure specific alert type"""
    try:
        parts = callback.data.split(":")
        alert_type = parts[2]
        channel_id = int(parts[3])
        chat_id = _get_chat_id(callback)

        if not chat_id:
            await callback.answer("❌ Unable to identify chat", show_alert=True)
            return

        # Create default alert subscription
        if alert_type == "spike":
            threshold = 2.0  # Z-score threshold
            window_hours = 48
            description = "spike detection (Z-score ≥ 2.0)"
        elif alert_type == "quiet":
            threshold = None
            window_hours = 24  # Hours without posts
            description = "quiet period detection (24h without posts)"
        elif alert_type == "growth":
            threshold = 10.0  # Growth percentage
            window_hours = 168  # 7 days
            description = "growth milestone (≥10% growth in 7 days)"
        else:
            await callback.answer("❌ Unknown alert type", show_alert=True)
            return

        # Create subscription
        subscription = AlertSubscription(
            id=None,
            chat_id=chat_id,
            channel_id=channel_id,
            kind=alert_type,
            threshold=threshold,
            window_hours=window_hours,
            enabled=True,
        )

        created_sub = await alert_repo.create_subscription(subscription)

        await callback.message.edit_text(
            f"✅ **Alert Created Successfully!**\n\n"
            f"🔔 Alert Type: {alert_type.title()}\n"
            f"📺 Channel: {channel_id}\n"
            f"📊 Description: {description}\n"
            f"⏱️ Window: {window_hours} hours\n"
            f"🆔 Alert ID: {created_sub.id}\n\n"
            "You'll receive notifications when this condition is met.\n"
            "Manage your alerts with /alerts command.",
            reply_markup=kb_alerts_main(str(channel_id)),
            parse_mode="Markdown",
        )

        await callback.answer("🔔 Alert created successfully!")

    except Exception as e:
        logger.error(f"Alert configuration failed: {e}")
        await callback.answer("❌ Failed to create alert", show_alert=True)


@router.callback_query(F.data.startswith("alert:toggle:"))
@throttle(rate=2.0)
async def toggle_alert(
    callback: CallbackQuery, i18n: I18nContext, alert_repo: AsyncpgAlertSubscriptionRepository
):
    """Toggle alert enabled/disabled"""
    try:
        alert_id = int(callback.data.split(":")[2])

        new_status = await alert_repo.toggle_subscription(alert_id)
        status_text = "enabled" if new_status else "disabled"

        await callback.answer(f"🔄 Alert {status_text} successfully!")

        # Refresh the alerts list
        # In a real implementation, you'd reload the current view

    except Exception as e:
        logger.error(f"Alert toggle failed: {e}")
        await callback.answer("❌ Failed to toggle alert", show_alert=True)


@router.callback_query(F.data.startswith("alert:delete:"))
@throttle(rate=2.0)
async def delete_alert_confirmation(callback: CallbackQuery, i18n: I18nContext):
    """Show delete confirmation"""
    try:
        alert_id = callback.data.split(":")[2]

        await callback.message.edit_text(
            "🗑️ **Delete Alert**\n\n"
            "Are you sure you want to delete this alert subscription?\n"
            "This action cannot be undone.",
            reply_markup=kb_confirmation(
                "delete alert",
                f"alert:delete:confirm:{alert_id}",
                f"alert:delete:cancel:{alert_id}",
            ),
            parse_mode="Markdown",
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Delete confirmation failed: {e}")
        await callback.answer("❌ Failed to show confirmation", show_alert=True)


@router.callback_query(F.data.startswith("alert:delete:confirm:"))
@throttle(rate=2.0)
async def delete_alert_confirmed(
    callback: CallbackQuery, i18n: I18nContext, alert_repo: AsyncpgAlertSubscriptionRepository
):
    """Delete alert after confirmation"""
    try:
        alert_id = int(callback.data.split(":")[3])

        deleted = await alert_repo.delete_subscription(alert_id)

        if deleted:
            await callback.message.edit_text(
                "✅ **Alert Deleted Successfully**\n\n"
                "The alert subscription has been removed.\n"
                "You will no longer receive notifications for this alert."
            )
            await callback.answer("🗑️ Alert deleted successfully!")
        else:
            await callback.answer("❌ Alert not found or already deleted", show_alert=True)

    except Exception as e:
        logger.error(f"Alert deletion failed: {e}")
        await callback.answer("❌ Failed to delete alert", show_alert=True)


@router.callback_query(F.data.startswith("alert:delete:cancel:"))
async def delete_alert_cancelled(callback: CallbackQuery, i18n: I18nContext):
    """Cancel alert deletion"""
    await callback.message.edit_text(
        "❌ **Alert Deletion Cancelled**\n\n" "The alert subscription was not deleted."
    )
    await callback.answer("Deletion cancelled")


# Alert preset handlers for quick setup
@router.callback_query(F.data.startswith("alerts:preset:"))
@throttle(rate=2.0)
async def setup_alert_preset(
    callback: CallbackQuery, i18n: I18nContext, alert_repo: AsyncpgAlertSubscriptionRepository
):
    """Set up predefined alert configurations"""
    try:
        parts = callback.data.split(":")
        preset_type = parts[2]  # "popular", "growth", "all"
        channel_id = int(parts[3])
        chat_id = _get_chat_id(callback)

        if not chat_id:
            await callback.answer("❌ Unable to identify chat", show_alert=True)
            return

        presets = []

        if preset_type == "popular":
            # Popular content alert
            presets.append(
                AlertSubscription(
                    id=None,
                    chat_id=chat_id,
                    channel_id=channel_id,
                    kind="spike",
                    threshold=2.0,
                    window_hours=48,
                    enabled=True,
                )
            )
        elif preset_type == "growth":
            # Growth milestone alert
            presets.append(
                AlertSubscription(
                    id=None,
                    chat_id=chat_id,
                    channel_id=channel_id,
                    kind="growth",
                    threshold=15.0,
                    window_hours=168,  # 7 days
                    enabled=True,
                )
            )
        elif preset_type == "all":
            # Complete alert package
            presets.extend(
                [
                    AlertSubscription(
                        id=None,
                        chat_id=chat_id,
                        channel_id=channel_id,
                        kind="spike",
                        threshold=2.0,
                        window_hours=48,
                        enabled=True,
                    ),
                    AlertSubscription(
                        id=None,
                        chat_id=chat_id,
                        channel_id=channel_id,
                        kind="quiet",
                        threshold=None,
                        window_hours=24,
                        enabled=True,
                    ),
                    AlertSubscription(
                        id=None,
                        chat_id=chat_id,
                        channel_id=channel_id,
                        kind="growth",
                        threshold=10.0,
                        window_hours=168,
                        enabled=True,
                    ),
                ]
            )

        # Create all preset subscriptions
        created_count = 0
        for preset in presets:
            try:
                await alert_repo.create_subscription(preset)
                created_count += 1
            except Exception as e:
                logger.warning(f"Failed to create preset alert: {e}")

        if created_count > 0:
            await callback.message.edit_text(
                f"✅ **Alert Preset Configured!**\n\n"
                f"Created {created_count} alert subscription(s) for channel {channel_id}.\n\n"
                "You'll start receiving notifications based on your alert settings.\n"
                "Use /alerts to manage your subscriptions.",
                parse_mode="Markdown",
            )
            await callback.answer(f"🔔 {created_count} alerts created!")
        else:
            await callback.answer("❌ Failed to create alert presets", show_alert=True)

    except Exception as e:
        logger.error(f"Alert preset setup failed: {e}")
        await callback.answer("❌ Failed to setup alert preset", show_alert=True)
