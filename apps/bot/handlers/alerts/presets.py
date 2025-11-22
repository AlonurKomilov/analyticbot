"""
Alert Presets Handlers
Quick setup with predefined alert configurations
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

from apps.bot.handlers.alerts.base import get_chat_id, logger, validate_callback
from apps.bot.middlewares.throttle import throttle
from core.repositories.alert_repository import (
    AlertSubscription,
    AlertSubscriptionRepository,
)

router = Router()


@router.callback_query(F.data.startswith("alerts:preset:"))
@throttle(rate=2.0)
async def setup_alert_preset(
    callback: CallbackQuery, i18n: I18nContext, alert_repo: AlertSubscriptionRepository
):
    """Set up predefined alert configurations"""
    try:
        is_valid, error_msg = validate_callback(callback)
        if not is_valid:
            await callback.answer(error_msg or "Invalid callback", show_alert=True)
            return

        assert callback.data is not None
        assert isinstance(callback.message, Message)

        parts = callback.data.split(":")
        preset_type = parts[2]  # "popular", "growth", "all"
        channel_id = int(parts[3])
        chat_id = get_chat_id(callback)

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
