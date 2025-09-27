"""
AlertingService - Service layer for alert processing and condition checking

This service handles all business logic related to alerts, including:
- Checking metrics against alert conditions
- Managing alert rules and thresholds
- Generating alert notifications
- Processing alert severity levels

Follows Clean Architecture principles by separating alert business logic
from HTTP request handling in the router layer.
"""

import logging
from datetime import datetime
from typing import Any

from src.shared_kernel.models.alerts import AlertEvent

logger = logging.getLogger(__name__)


class AlertingService:
    """Service for processing alerts and checking alert conditions"""

    def __init__(self):
        """Initialize the AlertingService"""
        self.logger = logging.getLogger(self.__class__.__name__)

    def check_alert_conditions(self, metrics: dict[str, Any], channel_id: str) -> list[AlertEvent]:
        """
        Check current metrics against alert conditions and generate alerts

        Args:
            metrics: Dictionary of metric values to check
            channel_id: ID of the channel being monitored

        Returns:
            List of AlertEvent objects for triggered conditions
        """
        alerts = []

        try:
            current_time = datetime.utcnow()

            # Get alert conditions (in a real app, these would be user-configurable)
            alert_conditions = self._get_default_alert_conditions()

            for condition in alert_conditions:
                if not condition["enabled"]:
                    continue

                metric_value = self._extract_metric_value(metrics, condition["type"])
                alert_result = self._evaluate_alert_condition(condition, metric_value)

                if alert_result["should_alert"]:
                    alert = self._create_alert_event(
                        condition=condition,
                        metric_value=metric_value,
                        severity=alert_result["severity"],
                        channel_id=channel_id,
                        timestamp=current_time,
                    )
                    alerts.append(alert)

            return alerts

        except Exception as e:
            self.logger.error(f"Error checking alert conditions: {e}")
            return []

    def _get_default_alert_conditions(self) -> list[dict[str, Any]]:
        """
        Get default alert conditions configuration

        In a production system, this would come from user settings or database
        """
        return [
            {
                "rule_id": "growth-spike",
                "name": "Growth Spike Alert",
                "type": "growth",
                "condition": "greater_than",
                "threshold": 15.0,
                "enabled": True,
            },
            {
                "rule_id": "low-engagement",
                "name": "Low Engagement Warning",
                "type": "engagement",
                "condition": "less_than",
                "threshold": 3.0,
                "enabled": True,
            },
            {
                "rule_id": "high-reach",
                "name": "Excellent Reach Achievement",
                "type": "reach",
                "condition": "greater_than",
                "threshold": 80.0,
                "enabled": True,
            },
        ]

    def _extract_metric_value(self, metrics: dict[str, Any], metric_type: str) -> float:
        """
        Extract the appropriate metric value based on the alert type

        Args:
            metrics: Dictionary of available metrics
            metric_type: Type of metric to extract (growth, engagement, reach)

        Returns:
            Numeric value of the requested metric
        """
        if metric_type == "reach":
            return metrics.get("reach_score", 0)
        else:
            return metrics.get(f"{metric_type}_rate", 0)

    def _evaluate_alert_condition(
        self, condition: dict[str, Any], metric_value: float
    ) -> dict[str, Any]:
        """
        Evaluate whether an alert condition is met and determine severity

        Args:
            condition: Alert condition configuration
            metric_value: Current value of the metric

        Returns:
            Dictionary with should_alert boolean and severity level
        """
        should_alert = False
        severity = "info"

        if condition["condition"] == "greater_than" and metric_value > condition["threshold"]:
            should_alert = True
            severity = "success" if condition["type"] == "growth" else "info"
        elif condition["condition"] == "less_than" and metric_value < condition["threshold"]:
            should_alert = True
            severity = "warning"

        return {"should_alert": should_alert, "severity": severity}

    def _create_alert_event(
        self,
        condition: dict[str, Any],
        metric_value: float,
        severity: str,
        channel_id: str,
        timestamp: datetime,
    ) -> AlertEvent:
        """
        Create an AlertEvent object from condition and metric data

        Args:
            condition: Alert condition that was triggered
            metric_value: Value that triggered the alert
            severity: Severity level of the alert
            channel_id: ID of the channel
            timestamp: When the alert was triggered

        Returns:
            AlertEvent object ready for use
        """
        return AlertEvent(
            id=f"{condition['rule_id']}-{int(timestamp.timestamp())}",
            rule_id=condition["rule_id"],
            title=condition["name"],
            message=f"{condition['type'].title()} is {metric_value:.1f} (threshold: {condition['threshold']})",
            severity=severity,
            timestamp=timestamp,
            channel_id=channel_id,
            triggered_value=metric_value,
            threshold=condition["threshold"],
        )

    def get_active_alerts_for_channel(self, channel_id: str) -> list[AlertEvent]:
        """
        Get all currently active alerts for a specific channel

        This is a placeholder for future implementation that would
        retrieve persisted alerts from a database or cache

        Args:
            channel_id: ID of the channel to get alerts for

        Returns:
            List of active AlertEvent objects
        """
        # TODO: Implement persistent alert storage and retrieval
        self.logger.info(f"Getting active alerts for channel {channel_id}")
        return []

    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """
        Mark an alert as acknowledged by a user

        Args:
            alert_id: ID of the alert to acknowledge
            user_id: ID of the user acknowledging the alert

        Returns:
            True if successfully acknowledged, False otherwise
        """
        # TODO: Implement alert acknowledgment logic
        self.logger.info(f"Alert {alert_id} acknowledged by user {user_id}")
        return True
