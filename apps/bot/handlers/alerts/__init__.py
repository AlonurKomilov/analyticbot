"""
Alert Handlers Package
Modular alert management system for bot handlers

Main exports:
- router: Main router with all alert handlers
- Helper functions for alert formatting and validation
"""

from apps.bot.handlers.alerts.base import (
    format_alert_subscription,
    get_chat_id,
    get_user_id,
    validate_callback,
)
from apps.bot.handlers.alerts.router import router

__all__ = [
    "router",
    "get_user_id",
    "get_chat_id",
    "validate_callback",
    "format_alert_subscription",
]
