"""
Base module for alert handlers
Shared imports, utilities, and helper functions
"""

import logging

from aiogram.types import CallbackQuery, Message

from core.repositories.alert_repository import AlertSubscription

logger = logging.getLogger(__name__)


def get_user_id(event) -> int | None:
    """Extract user ID from message or callback"""
    if hasattr(event, "from_user") and event.from_user:
        return event.from_user.id
    return None


def get_chat_id(event) -> int | None:
    """Extract chat ID from message or callback"""
    if hasattr(event, "chat") and event.chat:
        return event.chat.id
    elif hasattr(event, "message") and event.message and event.message.chat:
        return event.message.chat.id
    return None


def validate_callback(callback: CallbackQuery) -> tuple[bool, str | None]:
    """Validate callback has required data and message.

    Returns:
        (is_valid, error_message)
    """
    if not callback.data:
        return (False, "❌ Invalid callback data")

    if not callback.message or not isinstance(callback.message, Message):
        return (False, "❌ Unable to edit message")

    return (True, None)


def format_alert_subscription(sub: AlertSubscription) -> str:
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
