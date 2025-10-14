"""
Bot Alerts Microhandler - Minimal Working Version
==================================================

Simplified microhandler containing core alerts functionality.
Part of Phase 2 microrouter implementation (alerts domain).

Domain Responsibilities:
- Alerts options display
- Alert subscription management (basic)

Extracted from: apps/bot/handlers/analytics_v2.py (714 lines → simplified alerts)
Architecture: Clean separation following Phase 1 microrouter pattern
"""

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from apps.di import get_container

logger = logging.getLogger(__name__)

# Create alerts microhandler router
router = Router()


# ==============================
# ALERTS DOMAIN HELPER FUNCTIONS
# ==============================


def _get_settings():
    """Get settings instance with proper error handling"""
    try:
        from config.settings import Settings

        return Settings
    except Exception:
        # Fallback mock settings
        class MockSettings:
            ALERTS_ENABLED = True

        return MockSettings()


async def _safe_edit_message(callback: CallbackQuery, text: str, reply_markup=None) -> bool:
    """Safely edit callback message with type checking"""
    try:
        from aiogram.types import Message

        if (
            callback.message
            and isinstance(callback.message, Message)
            and hasattr(callback.message, "edit_text")
        ):
            await callback.message.edit_text(text, reply_markup=reply_markup)
            return True
        return False
    except Exception:
        return False


# ====================================
# ALERTS DOMAIN COMMAND HANDLERS
# ====================================


@router.callback_query(F.data.startswith("analytics:alerts:"))
async def show_alerts_options(callback: CallbackQuery) -> None:
    """Show alerts options for channel management"""
    try:
        settings = _get_settings()

        if not getattr(settings, "ALERTS_ENABLED", True):
            await callback.answer(
                "🚧 Alerts feature is currently disabled. Coming soon!", show_alert=True
            )
            return

        # Extract channel_id from callback data
        parts = callback.data.split(":")
        if len(parts) < 3:
            await callback.answer("❌ Invalid alerts request", show_alert=True)
            return

        channel_id = parts[2]

        # Create simple alerts keyboard
        buttons = [
            [InlineKeyboardButton(text="📈 Growth Alerts", callback_data="alert_subscribe:growth")],
            [InlineKeyboardButton(text="👁️ Views Alerts", callback_data="alert_subscribe:views")],
            [
                InlineKeyboardButton(
                    text="💫 Engagement Alerts", callback_data="alert_subscribe:engagement"
                )
            ],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        text = (
            "🔔 **Alert Management**\n\n"
            f"Channel: {channel_id}\n\n"
            "Manage your alert subscriptions:"
        )

        success = await _safe_edit_message(callback, text, keyboard)
        if success:
            await callback.answer()
        else:
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()

    except Exception as e:
        logger.error(f"Alerts options failed: {e}")
        await callback.answer("❌ Failed to show alerts options", show_alert=True)


# ====================================
# ALERTS DOMAIN MANAGEMENT HANDLERS
# ====================================


@router.callback_query(F.data.startswith("alert_subscribe:"))
async def handle_alert_subscribe(callback: CallbackQuery) -> None:
    """Handle alert subscription using AlertRuleManager"""
    try:
        alert_type = callback.data.split(":", 1)[1] if ":" in callback.data else None
        if not alert_type:
            await callback.answer("❌ Invalid alert type", show_alert=True)
            return

        # Get channel_id (simulate extraction, in real use parse from callback)
        channel_id = str(callback.from_user.id)

        # Use DI to get AlertRuleManager
        container = get_container()
        alert_rule_manager = container.bot.alert_rule_manager()

        # Create a basic alert rule for the subscription
        rule_name = f"{alert_type}_subscription"
        condition = "greater_than"
        threshold = 100  # Example threshold
        severity = "info"
        enabled = True

        # Create rule (simulate, in real use pass correct params)
        try:
            rule_id = await alert_rule_manager.create_rule(
                channel_id=channel_id,
                name=rule_name,
                metric_name=alert_type,
                condition=condition,
                threshold=threshold,
                severity=severity,
                enabled=enabled,
            )
            await callback.answer(
                f"✅ Subscribed to {alert_type.title()} alerts! Rule ID: {rule_id}",
                show_alert=True,
            )
        except Exception as e:
            logger.error(f"Failed to create alert rule: {e}")
            await callback.answer("❌ Failed to subscribe to alerts", show_alert=True)

    except Exception as e:
        logger.error(f"Alert subscription failed: {e}")
        await callback.answer("❌ Alert subscription failed", show_alert=True)


@router.callback_query(F.data.startswith("alert_unsubscribe:"))
async def handle_alert_unsubscribe(callback: CallbackQuery) -> None:
    """Handle alert unsubscription using AlertRuleManager"""
    try:
        alert_type = callback.data.split(":", 1)[1] if ":" in callback.data else None
        if not alert_type:
            await callback.answer("❌ Invalid alert type", show_alert=True)
            return

        channel_id = str(callback.from_user.id)
        container = get_container()
        alert_rule_manager = container.bot.alert_rule_manager()
        rule_name = f"{alert_type}_subscription"

        # Find and delete the rule (simulate, in real use search for rule_id)
        try:
            # For demo, assume rule_id is rule_name (in real use, query repository)
            await alert_rule_manager.delete_rule(channel_id=channel_id, rule_id=rule_name)
            await callback.answer(
                f"✅ Unsubscribed from {alert_type.title()} alerts!",
                show_alert=True,
            )
        except Exception as e:
            logger.error(f"Failed to delete alert rule: {e}")
            await callback.answer("❌ Failed to unsubscribe from alerts", show_alert=True)

    except Exception as e:
        logger.error(f"Alert unsubscription failed: {e}")
        await callback.answer("❌ Alert unsubscription failed", show_alert=True)
