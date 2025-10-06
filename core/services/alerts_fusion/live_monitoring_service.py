"""
Advanced Live Monitoring Service

Provides real-time monitoring capabilities for the analytics bot system.
Handles live data streams, alert generation, and performance tracking.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MonitoringMetric(Enum):
    """Available monitoring metrics"""

    POST_FREQUENCY = "post_frequency"
    ENGAGEMENT_RATE = "engagement_rate"
    GROWTH_RATE = "growth_rate"
    CONTENT_QUALITY = "content_quality"
    ANOMALY_DETECTION = "anomaly_detection"


@dataclass
class AlertRule:
    """Configuration for an alert rule"""

    id: str
    name: str
    metric: MonitoringMetric
    threshold: float
    severity: AlertSeverity
    channel_ids: list[int] | None = None
    enabled: bool = True


@dataclass
class MonitoringAlert:
    """A generated monitoring alert"""

    id: str
    rule_id: str
    channel_id: int
    channel_name: str
    metric: MonitoringMetric
    severity: AlertSeverity
    message: str
    value: float
    threshold: float
    timestamp: datetime
    acknowledged: bool = False


@dataclass
class LiveMetrics:
    """Real-time metrics data"""

    channel_id: int
    timestamp: datetime
    post_count_24h: int
    avg_engagement_rate: float
    growth_rate_7d: float
    content_quality_score: float
    anomaly_score: float


class LiveMonitoringService:
    """
    Advanced Live Monitoring Service

    Provides comprehensive real-time monitoring capabilities including:
    - Continuous metric collection
    - Alert rule management
    - Real-time alert generation
    - Performance tracking
    """

    def __init__(self):
        self.alert_rules: dict[str, AlertRule] = {}
        self.active_alerts: dict[str, MonitoringAlert] = {}
        self.metrics_cache: dict[int, LiveMetrics] = {}
        self.monitoring_enabled = True
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default monitoring rules"""
        default_rules = [
            AlertRule(
                id="low_engagement",
                name="Low Engagement Rate",
                metric=MonitoringMetric.ENGAGEMENT_RATE,
                threshold=0.02,  # 2%
                severity=AlertSeverity.MEDIUM,
            ),
            AlertRule(
                id="high_anomaly",
                name="High Anomaly Score",
                metric=MonitoringMetric.ANOMALY_DETECTION,
                threshold=0.8,
                severity=AlertSeverity.HIGH,
            ),
            AlertRule(
                id="negative_growth",
                name="Negative Growth Rate",
                metric=MonitoringMetric.GROWTH_RATE,
                threshold=-0.05,  # -5%
                severity=AlertSeverity.MEDIUM,
            ),
            AlertRule(
                id="low_posting_frequency",
                name="Low Posting Frequency",
                metric=MonitoringMetric.POST_FREQUENCY,
                threshold=1.0,  # Less than 1 post per day
                severity=AlertSeverity.LOW,
            ),
        ]

        for rule in default_rules:
            self.alert_rules[rule.id] = rule

    async def collect_live_metrics(self, channel_id: int) -> LiveMetrics | None:
        """
        Collect live metrics for a channel

        Args:
            channel_id: Channel ID to collect metrics for

        Returns:
            LiveMetrics object or None if collection failed
        """
        try:
            now = datetime.now()

            # Mock data implementation
            metrics = LiveMetrics(
                channel_id=channel_id,
                timestamp=now,
                post_count_24h=5,  # Mock: 5 posts in last 24h
                avg_engagement_rate=0.035,  # Mock: 3.5% engagement
                growth_rate_7d=0.02,  # Mock: 2% growth
                content_quality_score=0.75,  # Mock: 75% quality score
                anomaly_score=0.1,  # Mock: 10% anomaly score
            )

            self.metrics_cache[channel_id] = metrics
            return metrics

        except Exception as e:
            logger.error(f"Failed to collect live metrics for channel {channel_id}: {e}")
            return None

    async def evaluate_alerts(self, channel_id: int) -> list[MonitoringAlert]:
        """
        Evaluate alert rules for a channel

        Args:
            channel_id: Channel ID to evaluate

        Returns:
            List of generated alerts
        """
        try:
            metrics = await self.collect_live_metrics(channel_id)
            if not metrics:
                return []

            alerts = []

            for rule in self.alert_rules.values():
                if not rule.enabled:
                    continue

                if rule.channel_ids and channel_id not in rule.channel_ids:
                    continue

                # Check if alert should be triggered
                should_alert = False
                metric_value = 0.0

                if rule.metric == MonitoringMetric.ENGAGEMENT_RATE:
                    metric_value = metrics.avg_engagement_rate
                    should_alert = metric_value < rule.threshold
                elif rule.metric == MonitoringMetric.GROWTH_RATE:
                    metric_value = metrics.growth_rate_7d
                    should_alert = metric_value < rule.threshold
                elif rule.metric == MonitoringMetric.POST_FREQUENCY:
                    metric_value = metrics.post_count_24h
                    should_alert = metric_value < rule.threshold
                elif rule.metric == MonitoringMetric.ANOMALY_DETECTION:
                    metric_value = metrics.anomaly_score
                    should_alert = metric_value > rule.threshold

                if should_alert:
                    alert = MonitoringAlert(
                        id=f"{rule.id}_{channel_id}_{int(metrics.timestamp.timestamp())}",
                        rule_id=rule.id,
                        channel_id=channel_id,
                        channel_name=f"Channel {channel_id}",  # Mock name
                        metric=rule.metric,
                        severity=rule.severity,
                        message=f"{rule.name} triggered: {metric_value:.3f} (threshold: {rule.threshold})",
                        value=metric_value,
                        threshold=rule.threshold,
                        timestamp=metrics.timestamp,
                    )

                    alerts.append(alert)
                    self.active_alerts[alert.id] = alert

            return alerts

        except Exception as e:
            logger.error(f"Failed to evaluate alerts for channel {channel_id}: {e}")
            return []

    async def monitor_channels(self, channel_ids: list[int]) -> dict[int, list[MonitoringAlert]]:
        """
        Monitor multiple channels simultaneously

        Args:
            channel_ids: List of channel IDs to monitor

        Returns:
            Dict mapping channel IDs to their alerts
        """
        if not self.monitoring_enabled:
            return {}

        try:
            # Collect metrics and evaluate alerts for all channels
            tasks = [self.evaluate_alerts(channel_id) for channel_id in channel_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            channel_alerts = {}
            for i, result in enumerate(results):
                channel_id = channel_ids[i]
                if isinstance(result, Exception):
                    logger.error(f"Error monitoring channel {channel_id}: {result}")
                    channel_alerts[channel_id] = []
                else:
                    channel_alerts[channel_id] = result

            return channel_alerts

        except Exception as e:
            logger.error(f"Failed to monitor channels: {e}")
            return {}

    def add_alert_rule(self, rule: AlertRule) -> bool:
        """
        Add a new alert rule

        Args:
            rule: AlertRule to add

        Returns:
            True if added successfully
        """
        try:
            self.alert_rules[rule.id] = rule
            logger.info(f"Added alert rule: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add alert rule: {e}")
            return False

    def remove_alert_rule(self, rule_id: str) -> bool:
        """
        Remove an alert rule

        Args:
            rule_id: ID of rule to remove

        Returns:
            True if removed successfully
        """
        try:
            if rule_id in self.alert_rules:
                del self.alert_rules[rule_id]
                logger.info(f"Removed alert rule: {rule_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove alert rule: {e}")
            return False

    def update_alert_rule(self, rule_id: str, updates: dict[str, Any]) -> bool:
        """
        Update an existing alert rule

        Args:
            rule_id: ID of rule to update
            updates: Dict of field updates

        Returns:
            True if updated successfully
        """
        try:
            if rule_id not in self.alert_rules:
                return False

            rule = self.alert_rules[rule_id]
            for field, value in updates.items():
                if hasattr(rule, field):
                    setattr(rule, field, value)

            logger.info(f"Updated alert rule: {rule_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update alert rule: {e}")
            return False

    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an active alert

        Args:
            alert_id: ID of alert to acknowledge

        Returns:
            True if acknowledged successfully
        """
        try:
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].acknowledged = True
                logger.info(f"Acknowledged alert: {alert_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False

    def get_active_alerts(
        self, channel_id: int | None = None, severity: AlertSeverity | None = None
    ) -> list[MonitoringAlert]:
        """
        Get active alerts with optional filtering

        Args:
            channel_id: Filter by channel ID
            severity: Filter by severity level

        Returns:
            List of matching alerts
        """
        try:
            alerts = list(self.active_alerts.values())

            if channel_id is not None:
                alerts = [a for a in alerts if a.channel_id == channel_id]

            if severity is not None:
                alerts = [a for a in alerts if a.severity == severity]

            return alerts
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []

    def get_metrics_summary(self, channel_ids: list[int]) -> dict[str, Any]:
        """
        Get summary of metrics for multiple channels

        Args:
            channel_ids: List of channel IDs

        Returns:
            Summary statistics
        """
        try:
            summary = {
                "total_channels": len(channel_ids),
                "channels_with_data": 0,
                "avg_engagement": 0.0,
                "avg_growth": 0.0,
                "total_alerts": len(self.active_alerts),
                "critical_alerts": 0,
                "timestamp": datetime.now(),
            }

            valid_metrics = []
            for channel_id in channel_ids:
                if channel_id in self.metrics_cache:
                    valid_metrics.append(self.metrics_cache[channel_id])

            if valid_metrics:
                summary["channels_with_data"] = len(valid_metrics)
                summary["avg_engagement"] = sum(m.avg_engagement_rate for m in valid_metrics) / len(
                    valid_metrics
                )
                summary["avg_growth"] = sum(m.growth_rate_7d for m in valid_metrics) / len(
                    valid_metrics
                )

            # Count critical alerts
            critical_alerts = [
                a for a in self.active_alerts.values() if a.severity == AlertSeverity.CRITICAL
            ]
            summary["critical_alerts"] = len(critical_alerts)

            return summary

        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}

    def enable_monitoring(self):
        """Enable live monitoring"""
        self.monitoring_enabled = True
        logger.info("Live monitoring enabled")

    def disable_monitoring(self):
        """Disable live monitoring"""
        self.monitoring_enabled = False
        logger.info("Live monitoring disabled")

    def clear_old_alerts(self, hours: int = 24):
        """
        Clear alerts older than specified hours

        Args:
            hours: Number of hours to keep alerts
        """
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            old_alert_ids = [
                alert_id
                for alert_id, alert in self.active_alerts.items()
                if alert.timestamp < cutoff
            ]

            for alert_id in old_alert_ids:
                del self.active_alerts[alert_id]

            logger.info(f"Cleared {len(old_alert_ids)} old alerts")

        except Exception as e:
            logger.error(f"Failed to clear old alerts: {e}")

    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check of the monitoring service

        Returns:
            Health status information
        """
        try:
            health = {
                "status": "healthy",
                "monitoring_enabled": self.monitoring_enabled,
                "alert_rules_count": len(self.alert_rules),
                "active_alerts_count": len(self.active_alerts),
                "cached_metrics_count": len(self.metrics_cache),
                "timestamp": datetime.now(),
            }

            # Check if we have recent metrics
            if self.metrics_cache:
                latest_metric = max(self.metrics_cache.values(), key=lambda m: m.timestamp)
                age = datetime.now() - latest_metric.timestamp
                health["latest_metric_age_minutes"] = age.total_seconds() / 60

                if age.total_seconds() > 3600:  # 1 hour
                    health["status"] = "degraded"
                    health["warning"] = "No recent metrics collected"

            return health

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now()}

    async def get_live_metrics(self, channel_id: int, hours: int = 6) -> dict[str, Any]:
        """
        Protocol method - Get real-time metrics for specified hours.
        Delegates to collect_live_metrics implementation.
        """
        try:
            metrics = await self.collect_live_metrics(channel_id)
            if metrics is None:
                return {
                    "channel_id": channel_id,
                    "hours": hours,
                    "status": "no_data",
                    "timestamp": datetime.now(),
                }

            # Convert LiveMetrics dataclass to dict
            return {
                "channel_id": metrics.channel_id,
                "timestamp": metrics.timestamp,
                "post_count_24h": metrics.post_count_24h,
                "avg_engagement_rate": metrics.avg_engagement_rate,
                "growth_rate_7d": metrics.growth_rate_7d,
                "content_quality_score": metrics.content_quality_score,
                "anomaly_score": metrics.anomaly_score,
                "hours": hours,
                "status": "active",
            }
        except Exception as e:
            logger.error(f"Failed to get live metrics for channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "hours": hours,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(),
            }

    async def get_current_metrics(self, channel_id: int) -> dict[str, Any]:
        """
        Protocol method - Get current metrics snapshot.
        Delegates to collect_live_metrics implementation.
        """
        try:
            metrics = await self.collect_live_metrics(channel_id)
            if metrics is None:
                return {"channel_id": channel_id, "status": "no_data", "timestamp": datetime.now()}

            # Convert LiveMetrics dataclass to dict for current snapshot
            return {
                "channel_id": metrics.channel_id,
                "timestamp": metrics.timestamp,
                "post_count_24h": metrics.post_count_24h,
                "avg_engagement_rate": metrics.avg_engagement_rate,
                "growth_rate_7d": metrics.growth_rate_7d,
                "content_quality_score": metrics.content_quality_score,
                "anomaly_score": metrics.anomaly_score,
                "status": "current",
            }
        except Exception as e:
            logger.error(f"Failed to get current metrics for channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(),
            }
