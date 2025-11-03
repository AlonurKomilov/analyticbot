"""
Alert Creation Handlers
Handle alert type selection and configuration
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

from apps.bot.handlers.alerts.base import get_chat_id, logger, validate_callback
from apps.bot.keyboards.analytics import kb_alert_types
from apps.bot.middlewares.throttle import throttle
from core.repositories.alert_repository import (
    AlertSubscription,
    AlertSubscriptionRepository,
)

router = Router()


@router.callback_query(F.data.startswith("alerts:add:"))
@throttle(rate=2.0)
async def show_alert_types(callback: CallbackQuery, i18n: I18nContext):
    """Show alert types for adding new alert"""
    try:
        is_valid, error_msg = validate_callback(callback)
        if not is_valid:
            await callback.answer(error_msg or "Invalid callback", show_alert=True)
            return

        # Type narrowing: validation ensures callback.data and callback.message are not None
        assert callback.data is not None
        assert isinstance(callback.message, Message)

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
    callback: CallbackQuery, i18n: I18nContext, alert_repo: AlertSubscriptionRepository
):
    """Configure specific alert type"""
    try:
        is_valid, error_msg = validate_callback(callback)
        if not is_valid:
            await callback.answer(error_msg or "Invalid callback", show_alert=True)
            return

        # Type narrowing: validation ensures callback.data and callback.message are not None
        assert callback.data is not None
        assert isinstance(callback.message, Message)

        parts = callback.data.split(":")
        alert_type = parts[2]
        channel_id = int(parts[3])
        chat_id = get_chat_id(callback)

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

        await alert_repo.create_subscription(subscription)

        await callback.message.edit_text(
            f"✅ **Alert Created Successfully!**\n\n"
            f"📺 Channel: {channel_id}\n"
            f"🔔 Type: {alert_type.title()}\n"
            f"📊 Settings: {description}\n\n"
            "The alert is now active and you'll receive notifications when conditions are met.\n\n"
            "💡 Use /alerts to manage your alert subscriptions.",
            parse_mode="Markdown",
        )

        await callback.answer("🔔 Alert created successfully!")

    except Exception as e:
        logger.error(f"Alert creation failed: {e}")
        await callback.answer("❌ Failed to create alert", show_alert=True)
