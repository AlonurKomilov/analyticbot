"""
Alert Management Handlers
Toggle, delete, and modify existing alerts
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

from apps.bot.handlers.alerts.base import logger, validate_callback
from apps.bot.keyboards.analytics import kb_confirmation
from apps.bot.middlewares.throttle import throttle
from core.repositories.alert_repository import AlertSubscriptionRepository

router = Router()


@router.callback_query(F.data.startswith("alert:toggle:"))
@throttle(rate=2.0)
async def toggle_alert(
    callback: CallbackQuery, i18n: I18nContext, alert_repo: AlertSubscriptionRepository
):
    """Toggle alert enabled/disabled status"""
    try:
        is_valid, error_msg = validate_callback(callback)
        if not is_valid:
            await callback.answer(error_msg or "Invalid callback", show_alert=True)
            return

        assert callback.data is not None

        alert_id = int(callback.data.split(":")[2])

        # Get the current subscription to check its state
        all_subs = await alert_repo.get_user_subscriptions(
            callback.from_user.id if callback.from_user else 0
        )
        current_sub = next((s for s in all_subs if s.id == alert_id), None)

        if not current_sub:
            await callback.answer("❌ Alert not found", show_alert=True)
            return

        # Toggle the alert
        toggled = await alert_repo.toggle_subscription(alert_id)

        if toggled:
            # Determine new status (opposite of current)
            new_status = "disabled" if current_sub.enabled else "enabled"
            await callback.answer(f"🔔 Alert {new_status} successfully!")
        else:
            await callback.answer("❌ Failed to toggle alert", show_alert=True)

    except Exception as e:
        logger.error(f"Alert toggle failed: {e}")
        await callback.answer("❌ Failed to toggle alert", show_alert=True)


@router.callback_query(F.data.startswith("alert:delete:"))
@throttle(rate=2.0)
async def delete_alert_confirmation(callback: CallbackQuery, i18n: I18nContext):
    """Show confirmation dialog for alert deletion"""
    try:
        is_valid, error_msg = validate_callback(callback)
        if not is_valid:
            await callback.answer(error_msg or "Invalid callback", show_alert=True)
            return

        assert callback.data is not None
        assert isinstance(callback.message, Message)

        alert_id = callback.data.split(":")[2]

        await callback.message.edit_text(
            "⚠️ **Delete Alert Subscription**\n\n"
            "Are you sure you want to delete this alert?\n\n"
            "This action cannot be undone and you will stop receiving notifications for this alert.",
            reply_markup=kb_confirmation(
                "Delete Alert",
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
    callback: CallbackQuery, i18n: I18nContext, alert_repo: AlertSubscriptionRepository
):
    """Execute alert deletion after confirmation"""
    try:
        is_valid, error_msg = validate_callback(callback)
        if not is_valid:
            await callback.answer(error_msg or "Invalid callback", show_alert=True)
            return

        assert callback.data is not None
        assert isinstance(callback.message, Message)

        alert_id = int(callback.data.split(":")[3])

        # Delete the subscription
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
    is_valid, error_msg = validate_callback(callback)
    if not is_valid:
        await callback.answer(error_msg or "Invalid callback", show_alert=True)
        return

    assert isinstance(callback.message, Message)

    await callback.message.edit_text(
        "❌ **Alert Deletion Cancelled**\n\nThe alert subscription was not deleted."
    )
    await callback.answer("Deletion cancelled")
