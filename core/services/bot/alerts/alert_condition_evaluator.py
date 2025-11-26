"""
Alert Condition Evaluator

Clean Architecture: Core business logic for evaluating alert conditions
Framework-agnostic service for checking metrics against alert rules
"""

import logging
from typing import Any

from core.services.bot.alerts.protocols import AlertRepository

logger = logging.getLogger(__name__)


class AlertConditionEvaluator:
    """
    Service for evaluating metrics against alert conditions

    Responsibilities:
    - Check metrics against alert rules
    - Evaluate condition thresholds
    - Determine alert severity
    - Generate alert events when conditions are met
    """

    def __init__(self, alert_repository: AlertRepository):
        """
        Initialize the alert condition evaluator

        Args:
            alert_repository: Repository for alert persistence
        """
        self._alert_repo = alert_repository
        self._logger = logging.getLogger(__name__)

    async def check_alert_conditions(
        self, metrics: dict[str, Any], channel_id: str
    ) -> list[str]:
        """
        Check current metrics against alert conditions

        Args:
            metrics: Dictionary of metric values to check
            channel_id: Channel ID being monitored

        Returns:
            List of created alert event IDs
        """
        alert_ids = []

        try:
            # Get alert rules for this channel
            rules = await self._alert_repo.get_channel_alert_rules(channel_id)

            for rule in rules:
                # Skip disabled rules
                if not rule.get("enabled", True):
                    continue

                # Extract metric value
                metric_value = self._extract_metric_value(metrics, rule.get("metric_type", ""))

                # Evaluate condition
                evaluation = self._evaluate_condition(rule, metric_value)

                if evaluation["should_alert"]:
                    # Create alert event
                    alert_id = await self._create_alert_event(
                        channel_id=channel_id,
                        rule=rule,
                        metric_value=metric_value,
                        severity=evaluation["severity"],
                    )
                    alert_ids.append(alert_id)

            return alert_ids

        except Exception as e:
            self._logger.error(f"Error checking alert conditions for channel {channel_id}: {e}")
            return []

    def _extract_metric_value(self, metrics: dict[str, Any], metric_type: str) -> float:
        """
        Extract metric value from metrics dictionary

        Args:
            metrics: Dictionary of available metrics
            metric_type: Type of metric to extract

        Returns:
            Numeric value of the metric (0 if not found)
        """
        # Common metric mappings
        metric_mappings = {
            "views": "total_views",
            "growth": "growth_rate",
            "engagement": "engagement_rate",
            "reach": "reach_score",
            "subscribers": "subscriber_count",
            "posts": "post_count",
        }

        # Try direct lookup first
        if metric_type in metrics:
            value = metrics[metric_type]
        # Try mapped name
        elif metric_type in metric_mappings:
            mapped_name = metric_mappings[metric_type]
            value = metrics.get(mapped_name, 0)
        # Try with _rate suffix
        else:
            value = metrics.get(f"{metric_type}_rate", 0)

        # Convert to float, handle None
        try:
            return float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _evaluate_condition(
        self, rule: dict[str, Any], metric_value: float
    ) -> dict[str, Any]:
        """
        Evaluate whether alert condition is met

        Args:
            rule: Alert rule configuration
            metric_value: Current metric value

        Returns:
            Dictionary with should_alert and severity
        """
        condition_type = rule.get("condition", "greater_than")
        threshold = float(rule.get("threshold", 0))
        should_alert = False

        # Evaluate based on condition type
        if condition_type == "greater_than":
            should_alert = metric_value > threshold
        elif condition_type == "greater_than_or_equal":
            should_alert = metric_value >= threshold
        elif condition_type == "less_than":
            should_alert = metric_value < threshold
        elif condition_type == "less_than_or_equal":
            should_alert = metric_value <= threshold
        elif condition_type == "equals":
            should_alert = abs(metric_value - threshold) < 0.001  # Float comparison
        elif condition_type == "not_equals":
            should_alert = abs(metric_value - threshold) >= 0.001

        # Determine severity
        severity = self._determine_severity(rule, metric_value, threshold, should_alert)

        return {
            "should_alert": should_alert,
            "severity": severity,
            "threshold": threshold,
            "metric_value": metric_value,
        }

    def _determine_severity(
        self,
        rule: dict[str, Any],
        metric_value: float,
        threshold: float,
        alert_triggered: bool,
    ) -> str:
        """
        Determine alert severity based on rule and metric value

        Args:
            rule: Alert rule configuration
            metric_value: Current metric value
            threshold: Threshold value
            alert_triggered: Whether alert was triggered

        Returns:
            Severity level (low, medium, high, critical)
        """
        if not alert_triggered:
            return "info"

        # Use rule-defined severity if present
        if "severity" in rule:
            return rule["severity"]

        # Calculate deviation from threshold
        if threshold > 0:
            deviation_percent = abs((metric_value - threshold) / threshold) * 100
        else:
            deviation_percent = abs(metric_value - threshold) * 100

        # Determine severity based on deviation
        if deviation_percent > 100:
            return "critical"
        elif deviation_percent > 50:
            return "high"
        elif deviation_percent > 20:
            return "medium"
        else:
            return "low"

    async def _create_alert_event(
        self,
        channel_id: str,
        rule: dict[str, Any],
        metric_value: float,
        severity: str,
    ) -> str:
        """
        Create an alert event

        Args:
            channel_id: Channel ID
            rule: Alert rule that was triggered
            metric_value: Current metric value
            severity: Alert severity

        Returns:
            Created alert event ID
        """
        # Generate alert message
        message = self._generate_alert_message(rule, metric_value)

        # Create alert in repository
        alert_id = await self._alert_repo.create_alert_event(
            channel_id=channel_id,
            alert_type=rule.get("metric_type", "unknown"),
            severity=severity,
            message=message,
            metric_value=metric_value,
            threshold=rule.get("threshold"),
        )

        self._logger.info(
            f"Created alert {alert_id} for channel {channel_id}: {message}"
        )

        return alert_id

    def _generate_alert_message(
        self, rule: dict[str, Any], metric_value: float
    ) -> str:
        """
        Generate human-readable alert message

        Args:
            rule: Alert rule configuration
            metric_value: Current metric value

        Returns:
            Alert message string
        """
        rule_name = rule.get("name", "Alert")
        metric_type = rule.get("metric_type", "metric")
        threshold = rule.get("threshold", 0)
        condition = rule.get("condition", "")

        # Build message based on condition
        if "greater" in condition:
            return (
                f"{rule_name}: {metric_type} is {metric_value:.2f}, "
                f"which is above the threshold of {threshold:.2f}"
            )
        elif "less" in condition:
            return (
                f"{rule_name}: {metric_type} is {metric_value:.2f}, "
                f"which is below the threshold of {threshold:.2f}"
            )
        else:
            return (
                f"{rule_name}: {metric_type} value {metric_value:.2f} "
                f"triggered alert (threshold: {threshold:.2f})"
            )
