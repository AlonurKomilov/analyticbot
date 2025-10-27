"""
Alert Service Protocols

Clean Architecture: Define interfaces for alert system dependencies
These protocols allow core services to remain framework-agnostic
"""

from datetime import datetime
from typing import Any, Protocol

# Note: AlertEvent, AlertNotification, AlertRule will be type hints
# Actual imports handled by adapters to avoid circular dependencies


class AlertRepository(Protocol):
    """
    Protocol for alert persistence operations

    Defines interface for alert storage without coupling to specific implementation
    """

    async def create_alert_event(
        self,
        channel_id: str,
        alert_type: str,
        severity: str,
        message: str,
        metric_value: float | None = None,
        threshold: float | None = None,
    ) -> str:
        """
        Create and store a new alert event

        Args:
            channel_id: Channel where alert was triggered
            alert_type: Type of alert (views_drop, engagement_low, etc.)
            severity: Alert severity (low, medium, high, critical)
            message: Human-readable alert message
            metric_value: Current metric value that triggered alert
            threshold: Threshold value that was exceeded

        Returns:
            Created alert event ID
        """
        ...

    async def get_active_alerts(self, channel_id: str) -> list[dict[str, Any]]:
        """
        Get all active (unacknowledged) alerts for a channel

        Args:
            channel_id: Channel ID to fetch alerts for

        Returns:
            List of active AlertEvent objects
        """
        ...

    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """
        Mark an alert as acknowledged

        Args:
            alert_id: Alert event ID to acknowledge
            user_id: User who acknowledged the alert

        Returns:
            True if acknowledgment successful, False otherwise
        """
        ...

    async def get_alert_history(
        self,
        channel_id: str,
        limit: int = 50,
        start_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve alert history for a channel

        Args:
            channel_id: Channel ID
            limit: Maximum number of alerts to return
            start_date: Optional start date filter

        Returns:
            List of historical AlertEvent objects
        """
        ...

    async def create_alert_rule(self, rule: dict[str, Any]) -> str:
        """
        Create a new alert rule

        Args:
            rule: AlertRule object with rule configuration

        Returns:
            Created rule ID
        """
        ...

    async def get_channel_alert_rules(self, channel_id: str) -> list[dict[str, Any]]:
        """
        Get all alert rules for a channel

        Args:
            channel_id: Channel ID

        Returns:
            List of AlertRule objects
        """
        ...

    async def update_alert_rule(self, rule_id: str, updates: dict[str, Any]) -> bool:
        """
        Update an existing alert rule

        Args:
            rule_id: Rule ID to update
            updates: Dictionary of fields to update

        Returns:
            True if update successful, False otherwise
        """
        ...

    async def delete_alert_rule(self, rule_id: str, channel_id: str) -> bool:
        """
        Delete an alert rule

        Args:
            rule_id: Rule ID to delete
            channel_id: Channel ID (for authorization check)

        Returns:
            True if deletion successful, False otherwise
        """
        ...

    async def get_alert_statistics(
        self,
        channel_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Get alert statistics for a channel

        Args:
            channel_id: Channel ID
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Dictionary with alert statistics (counts, rates, etc.)
        """
        ...


class AlertNotificationPort(Protocol):
    """
    Protocol for sending alert notifications

    Abstracts notification delivery from core alert logic
    """

    async def send_alert(self, notification: dict[str, Any]) -> bool:
        """
        Send an alert notification

        Args:
            notification: AlertNotification with delivery details

        Returns:
            True if notification sent successfully, False otherwise
        """
        ...

    async def send_bulk_alerts(self, notifications: list[dict[str, Any]]) -> dict[str, bool]:
        """
        Send multiple alert notifications

        Args:
            notifications: List of AlertNotification objects

        Returns:
            Dictionary mapping notification IDs to success status
        """
        ...
