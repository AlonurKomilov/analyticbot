"""
Alert Services Module

Clean Architecture: Bot alert domain services
Framework-agnostic business logic for alert management and notifications
"""

from core.services.bot.alerts.protocols import (
    AlertNotificationPort,
    AlertRepository,
)

__all__ = [
    # Protocols
    "AlertRepository",
    "AlertNotificationPort",
    # Services will be added as they're implemented
]
