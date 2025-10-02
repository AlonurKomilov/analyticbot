# infra/notifications/simple_notification_service.py
"""
Simple notification service implementation.
"""

import logging
from datetime import datetime

from core.ports import NotificationService

logger = logging.getLogger(__name__)


class SimpleNotificationService(NotificationService):
    """Simple logging-based notification service."""

    def __init__(self, log_level: str = "INFO"):
        self.log_level = getattr(logging, log_level.upper())
        self.notification_log = logging.getLogger(f"{__name__}.notifications")
        self.notification_log.setLevel(self.log_level)

    async def send_notification(self, user_id: str, message: str, type: str = "info") -> bool:
        """Send notification to user via logging."""
        try:
            timestamp = datetime.utcnow().isoformat()
            log_message = f"NOTIFICATION [{type.upper()}] User:{user_id} @ {timestamp}: {message}"

            if type.lower() == "error":
                self.notification_log.error(log_message)
            elif type.lower() == "warning":
                self.notification_log.warning(log_message)
            else:
                self.notification_log.info(log_message)

            return True
        except Exception as e:
            logger.error(f"Failed to send notification to user {user_id}: {e}")
            return False

    async def send_system_alert(self, message: str, severity: str = "info") -> bool:
        """Send system-wide alert via logging."""
        try:
            timestamp = datetime.utcnow().isoformat()
            log_message = f"SYSTEM ALERT [{severity.upper()}] @ {timestamp}: {message}"

            if severity.lower() == "critical":
                self.notification_log.critical(log_message)
            elif severity.lower() == "error":
                self.notification_log.error(log_message)
            elif severity.lower() == "warning":
                self.notification_log.warning(log_message)
            else:
                self.notification_log.info(log_message)

            return True
        except Exception as e:
            logger.error(f"Failed to send system alert: {e}")
            return False


class EmailNotificationService(NotificationService):
    """Email-based notification service (placeholder implementation)."""

    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self._client = None

    async def send_notification(self, user_id: str, message: str, type: str = "info") -> bool:
        """Send email notification (placeholder - would use real SMTP)."""
        logger.info(f"EMAIL NOTIFICATION would be sent to user {user_id}: {message}")
        # TODO: Implement actual email sending
        return True

    async def send_system_alert(self, message: str, severity: str = "info") -> bool:
        """Send system alert via email (placeholder)."""
        logger.info(f"EMAIL SYSTEM ALERT [{severity}]: {message}")
        # TODO: Implement actual email sending
        return True
