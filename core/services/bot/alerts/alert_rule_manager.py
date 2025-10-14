"""
Alert Rule Manager

Clean Architecture: Core business logic for managing alert rules
Framework-agnostic service for CRUD operations on alert rules
"""

import logging
from typing import Any

from core.services.bot.alerts.protocols import AlertRepository

logger = logging.getLogger(__name__)


class AlertRuleManager:
    """
    Service for managing alert rules

    Responsibilities:
    - Create new alert rules
    - Update existing rules
    - Delete rules
    - Fetch rules for channels
    - Validate rule configuration
    """

    # Valid condition types
    VALID_CONDITIONS = {
        "greater_than",
        "greater_than_or_equal",
        "less_than",
        "less_than_or_equal",
        "equals",
        "not_equals",
    }

    # Valid severity levels
    VALID_SEVERITIES = {"low", "medium", "high", "critical", "info"}

    def __init__(self, alert_repository: AlertRepository):
        """
        Initialize the alert rule manager

        Args:
            alert_repository: Repository for alert persistence
        """
        self._alert_repo = alert_repository
        self._logger = logging.getLogger(__name__)

    async def create_rule(
        self,
        channel_id: str,
        name: str,
        metric_type: str,
        condition: str,
        threshold: float,
        severity: str = "medium",
        enabled: bool = True,
    ) -> str:
        """
        Create a new alert rule

        Args:
            channel_id: Channel ID to monitor
            name: Human-readable rule name
            metric_type: Type of metric to monitor
            condition: Condition type (greater_than, less_than, etc.)
            threshold: Threshold value
            severity: Alert severity level
            enabled: Whether rule is enabled

        Returns:
            Created rule ID

        Raises:
            ValueError: If rule configuration is invalid
        """
        # Validate rule
        self._validate_rule(
            name=name,
            metric_type=metric_type,
            condition=condition,
            threshold=threshold,
            severity=severity,
        )

        # Build rule dict
        rule = {
            "channel_id": channel_id,
            "name": name,
            "metric_type": metric_type,
            "condition": condition,
            "threshold": threshold,
            "severity": severity,
            "enabled": enabled,
        }

        # Create in repository
        rule_id = await self._alert_repo.create_alert_rule(rule)

        self._logger.info(f"Created alert rule {rule_id} for channel {channel_id}: {name}")

        return rule_id

    async def get_channel_rules(self, channel_id: str) -> list[dict[str, Any]]:
        """
        Get all alert rules for a channel

        Args:
            channel_id: Channel ID

        Returns:
            List of alert rule dictionaries
        """
        try:
            rules = await self._alert_repo.get_channel_alert_rules(channel_id)
            return rules
        except Exception as e:
            self._logger.error(f"Error fetching rules for channel {channel_id}: {e}")
            return []

    async def update_rule(
        self,
        rule_id: str,
        updates: dict[str, Any],
    ) -> bool:
        """
        Update an existing alert rule

        Args:
            rule_id: Rule ID to update
            updates: Dictionary of fields to update

        Returns:
            True if update successful, False otherwise

        Raises:
            ValueError: If update contains invalid values
        """
        # Validate updates
        if "condition" in updates and updates["condition"] not in self.VALID_CONDITIONS:
            raise ValueError(f"Invalid condition: {updates['condition']}")

        if "severity" in updates and updates["severity"] not in self.VALID_SEVERITIES:
            raise ValueError(f"Invalid severity: {updates['severity']}")

        if "threshold" in updates:
            try:
                float(updates["threshold"])
            except (ValueError, TypeError):
                raise ValueError("Threshold must be a number")

        # Update in repository
        try:
            success = await self._alert_repo.update_alert_rule(rule_id, updates)

            if success:
                self._logger.info(f"Updated alert rule {rule_id}")
            else:
                self._logger.warning(f"Failed to update rule {rule_id}")

            return success

        except Exception as e:
            self._logger.error(f"Error updating rule {rule_id}: {e}")
            return False

    async def delete_rule(self, rule_id: str, channel_id: str) -> bool:
        """
        Delete an alert rule

        Args:
            rule_id: Rule ID to delete
            channel_id: Channel ID (for authorization)

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            success = await self._alert_repo.delete_alert_rule(rule_id, channel_id)

            if success:
                self._logger.info(f"Deleted alert rule {rule_id}")
            else:
                self._logger.warning(f"Failed to delete rule {rule_id}")

            return success

        except Exception as e:
            self._logger.error(f"Error deleting rule {rule_id}: {e}")
            return False

    async def toggle_rule(self, rule_id: str, enabled: bool) -> bool:
        """
        Enable or disable an alert rule

        Args:
            rule_id: Rule ID
            enabled: New enabled state

        Returns:
            True if update successful, False otherwise
        """
        return await self.update_rule(rule_id, {"enabled": enabled})

    def _validate_rule(
        self,
        name: str,
        metric_type: str,
        condition: str,
        threshold: float,
        severity: str,
    ) -> None:
        """
        Validate alert rule configuration

        Args:
            name: Rule name
            metric_type: Metric type
            condition: Condition type
            threshold: Threshold value
            severity: Severity level

        Raises:
            ValueError: If any parameter is invalid
        """
        if not name or not name.strip():
            raise ValueError("Rule name cannot be empty")

        if not metric_type or not metric_type.strip():
            raise ValueError("Metric type cannot be empty")

        if condition not in self.VALID_CONDITIONS:
            raise ValueError(
                f"Invalid condition '{condition}'. Must be one of: {', '.join(self.VALID_CONDITIONS)}"
            )

        try:
            float(threshold)
        except (ValueError, TypeError):
            raise ValueError("Threshold must be a number")

        if severity not in self.VALID_SEVERITIES:
            raise ValueError(
                f"Invalid severity '{severity}'. Must be one of: {', '.join(self.VALID_SEVERITIES)}"
            )
