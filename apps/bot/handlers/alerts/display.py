"""
Alert Display Handlers
Main /alerts command and channel alert listing
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

from apps.bot.handlers.alerts.base import (
    format_alert_subscription,
    get_chat_id,
    logger,
    validate_callback,
)
from apps.bot.keyboards.analytics import kb_alerts_main
from apps.bot.middlewares.throttle import throttle
from config.settings import Settings
from core.repositories.alert_repository import AlertSubscriptionRepository

router = Router()


@router.message(Command("alerts"))
@throttle(rate=3.0)
async def cmd_alerts(
    message: Message,
    i18n: I18nContext,
    alert_repo: AlertSubscriptionRepository,
):
    """Main alerts command - feature flagged"""
    settings = Settings()

    if not settings.ALERTS_ENABLED:
        await message.answer("🚧 Alerts feature is currently disabled. Coming soon!")
        return

    chat_id = get_chat_id(message)
    if not chat_id:
        await message.answer("❌ Unable to identify chat.")
        return

    try:
        # Get user's alert subscriptions
        subscriptions = await alert_repo.get_user_subscriptions(chat_id)

        if not subscriptions:
            await message.answer(
                "🔔 **Alert Management**\n\n"
                "You don't have any alert subscriptions yet.\n\n"
                "Alerts notify you about:\n"
                "• 🚀 Viral spikes (unusual high engagement)\n"
                "• 😴 Quiet periods (inactive content)\n"
                "• 📈 Growth milestones (subscriber growth)\n\n"
                "Configure alerts for specific channels to get real-time notifications!",
                parse_mode="Markdown",
                reply_markup=kb_alerts_main(),
            )
            return

        # Group subscriptions by channel
        channel_alerts: dict[int, list] = {}
        for sub in subscriptions:
            if sub.channel_id not in channel_alerts:
                channel_alerts[sub.channel_id] = []
            channel_alerts[sub.channel_id].append(sub)

        # Build response message
        response_parts = ["🔔 **Your Alert Subscriptions**\n"]

        for channel_id, alerts in channel_alerts.items():
            response_parts.append(f"\n📺 **Channel {channel_id}**")

            for alert in alerts:
                status_icon = "🟢" if alert.enabled else "🔴"
                alert_type = alert.kind.title()

                if alert.kind == "spike":
                    detail = f"Z-score ≥ {alert.threshold or 2.0}"
                elif alert.kind == "quiet":
                    detail = f"Inactive {alert.window_hours}h"
                elif alert.kind == "growth":
                    detail = f"Growth ≥ {alert.threshold or 10.0}%"
                else:
                    detail = "Custom"

                response_parts.append(f"  {status_icon} {alert_type}: {detail}")

        response_parts.append(
            "\n💡 Use the buttons below to manage your alert subscriptions."
        )

        await message.answer(
            "\n".join(response_parts),
            parse_mode="Markdown",
            reply_markup=kb_alerts_main(),
        )

    except Exception as e:
        logger.error(f"Failed to fetch alert subscriptions: {e}")
        await message.answer(
            "❌ Failed to load alert subscriptions. Please try again later."
        )


@router.callback_query(F.data.startswith("alerts:list:"))
@throttle(rate=2.0)
async def show_channel_alerts(
    callback: CallbackQuery, i18n: I18nContext, alert_repo: AlertSubscriptionRepository
):
    """Show all alerts for a specific channel"""
    try:
        is_valid, error_msg = validate_callback(callback)
        if not is_valid:
            await callback.answer(error_msg or "Invalid callback", show_alert=True)
            return

        # Type narrowing: validation ensures callback.data and callback.message are not None
        assert callback.data is not None
        assert isinstance(callback.message, Message)

        channel_id = int(callback.data.split(":")[2])
        chat_id = get_chat_id(callback)

        if not chat_id:
            await callback.answer("❌ Unable to identify chat", show_alert=True)
            return

        # Get alerts for this channel
        all_subscriptions = await alert_repo.get_user_subscriptions(chat_id)
        channel_alerts = [
            sub for sub in all_subscriptions if sub.channel_id == channel_id
        ]

        if not channel_alerts:
            await callback.message.edit_text(
                f"📺 **Channel {channel_id} Alerts**\n\n"
                "No alert subscriptions configured for this channel.\n\n"
                "Use the buttons below to add alerts.",
                reply_markup=kb_alerts_main(),
            )
            await callback.answer()
            return

        # Build alert list
        alert_list = [f"📺 **Channel {channel_id} - Alert Subscriptions**\n"]

        for i, sub in enumerate(channel_alerts, 1):
            alert_list.append(f"\n**Alert #{i}**")
            alert_list.append(format_alert_subscription(sub))

        alert_list.append(
            "\n\n💡 Toggle or delete alerts using the management options."
        )

        await callback.message.edit_text(
            "\n".join(alert_list),
            parse_mode="Markdown",
            reply_markup=kb_alerts_main(),
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Channel alerts listing failed: {e}")
        await callback.answer("❌ Failed to load alerts", show_alert=True)
