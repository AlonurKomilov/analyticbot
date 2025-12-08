"""
Alert Event Manager

Clean Architecture: Core business logic for managing alert events
Framework-agnostic service for alert event lifecycle and history
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from core.services.bot.alerts.protocols import AlertRepository

logger = logging.getLogger(__name__)


class AlertEventManager:
    """
    Service for managing alert events and history

    Responsibilities:
    - Get active alerts
    - Acknowledge alerts
    - Retrieve alert history
    - Calculate alert statistics
    - Manage alert lifecycle
    """

    def __init__(self, alert_repository: AlertRepository):
        """
        Initialize the alert event manager

        Args:
            alert_repository: Repository for alert persistence
        """
        self._alert_repo = alert_repository
        self._logger = logging.getLogger(__name__)

    async def get_active_alerts(self, channel_id: str) -> list[dict[str, Any]]:
        """
        Get all active (unacknowledged) alerts for a channel

        Args:
            channel_id: Channel ID

        Returns:
            List of active alert event dictionaries
        """
        try:
            alerts = await self._alert_repo.get_active_alerts(channel_id)
            self._logger.debug(f"Found {len(alerts)} active alerts for channel {channel_id}")
            return alerts

        except Exception as e:
            self._logger.error(f"Error fetching active alerts for channel {channel_id}: {e}")
            return []

    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """
        Mark an alert as acknowledged

        Args:
            alert_id: Alert event ID
            user_id: User acknowledging the alert

        Returns:
            True if acknowledgment successful, False otherwise
        """
        try:
            success = await self._alert_repo.acknowledge_alert(alert_id, user_id)

            if success:
                self._logger.info(f"Alert {alert_id} acknowledged by user {user_id}")
            else:
                self._logger.warning(f"Failed to acknowledge alert {alert_id}")

            return success

        except Exception as e:
            self._logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return False

    async def get_alert_history(
        self,
        channel_id: str,
        limit: int = 50,
        days_back: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve alert history for a channel

        Args:
            channel_id: Channel ID
            limit: Maximum number of alerts to return
            days_back: Optional number of days to look back

        Returns:
            List of historical alert event dictionaries
        """
        try:
            # Calculate start date if days_back specified
            start_date = None
            if days_back is not None:
                start_date = datetime.utcnow() - timedelta(days=days_back)

            alerts = await self._alert_repo.get_alert_history(
                channel_id=channel_id,
                limit=limit,
                start_date=start_date,
            )

            self._logger.debug(
                f"Retrieved {len(alerts)} historical alerts for channel {channel_id}"
            )

            return alerts

        except Exception as e:
            self._logger.error(f"Error fetching alert history for channel {channel_id}: {e}")
            return []

    async def get_alert_statistics(
        self,
        channel_id: str,
        days_back: int = 30,
    ) -> dict[str, Any]:
        """
        Get alert statistics for a channel

        Args:
            channel_id: Channel ID
            days_back: Number of days to analyze

        Returns:
            Dictionary with alert statistics
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)

            # Get stats from repository
            stats = await self._alert_repo.get_alert_statistics(
                channel_id=channel_id,
                start_date=start_date,
                end_date=end_date,
            )

            # Add calculated metrics
            total_alerts = stats.get("total_count", 0)
            acknowledged_count = stats.get("acknowledged_count", 0)

            if total_alerts > 0:
                stats["acknowledgment_rate"] = (acknowledged_count / total_alerts) * 100
                stats["alerts_per_day"] = total_alerts / days_back
            else:
                stats["acknowledgment_rate"] = 0.0
                stats["alerts_per_day"] = 0.0

            self._logger.debug(
                f"Alert statistics for channel {channel_id}: {total_alerts} total alerts"
            )

            return stats

        except Exception as e:
            self._logger.error(f"Error calculating alert statistics for channel {channel_id}: {e}")
            return {
                "total_count": 0,
                "acknowledged_count": 0,
                "acknowledgment_rate": 0.0,
                "alerts_per_day": 0.0,
            }

    async def get_recent_alerts_by_severity(
        self,
        channel_id: str,
        severity: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get recent alerts filtered by severity

        Args:
            channel_id: Channel ID
            severity: Severity level to filter by
            limit: Maximum number of alerts

        Returns:
            List of alert event dictionaries
        """
        try:
            # Get alert history
            all_alerts = await self.get_alert_history(channel_id, limit=limit * 2)

            # Filter by severity
            filtered_alerts = [alert for alert in all_alerts if alert.get("severity") == severity][
                :limit
            ]

            return filtered_alerts

        except Exception as e:
            self._logger.error(f"Error fetching alerts by severity for channel {channel_id}: {e}")
            return []

    async def bulk_acknowledge_alerts(
        self,
        alert_ids: list[str],
        user_id: str,
    ) -> dict[str, bool]:
        """
        Acknowledge multiple alerts at once

        Args:
            alert_ids: List of alert IDs to acknowledge
            user_id: User acknowledging the alerts

        Returns:
            Dictionary mapping alert IDs to success status
        """
        results = {}

        for alert_id in alert_ids:
            success = await self.acknowledge_alert(alert_id, user_id)
            results[alert_id] = success

        successful_count = sum(1 for success in results.values() if success)
        self._logger.info(
            f"Bulk acknowledged {successful_count}/{len(alert_ids)} alerts for user {user_id}"
        )

        return results
