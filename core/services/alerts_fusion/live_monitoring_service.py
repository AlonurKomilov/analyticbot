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

    def __init__(self, post_repository=None):
        self.alert_rules: dict[str, AlertRule] = {}
        self.active_alerts: dict[str, MonitoringAlert] = {}
        self.metrics_cache: dict[int, LiveMetrics] = {}
        self.monitoring_enabled = True
        self.post_repo = post_repository  # Inject repository for DB access
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
        Collect live metrics for a channel from real database data

        Args:
            channel_id: Channel ID to collect metrics for

        Returns:
            LiveMetrics object or None if collection failed
        """
        try:
            now = datetime.now()

            # If repository is available, fetch real data from database
            if self.post_repo:
                try:
                    # Calculate metrics from real database data
                    post_count_24h = await self._get_post_count_24h(channel_id)
                    avg_engagement = await self._calculate_avg_engagement(channel_id)
                    growth_rate = await self._calculate_growth_rate(channel_id)
                    quality_score = await self._calculate_content_quality(channel_id)
                    anomaly_score = await self._detect_anomalies(channel_id)

                    metrics = LiveMetrics(
                        channel_id=channel_id,
                        timestamp=now,
                        post_count_24h=post_count_24h,
                        avg_engagement_rate=avg_engagement,
                        growth_rate_7d=growth_rate,
                        content_quality_score=quality_score,
                        anomaly_score=anomaly_score,
                    )

                    self.metrics_cache[channel_id] = metrics
                    logger.info(
                        f"✅ Collected REAL metrics for channel {channel_id}: {post_count_24h} posts, {avg_engagement:.2%} engagement"
                    )
                    return metrics

                except Exception as db_error:
                    logger.warning(f"Database query failed, using fallback: {db_error}")
                    # Fall through to fallback

            # Fallback: Return minimal but valid metrics if DB not available
            logger.info(f"⚠️ Using fallback metrics for channel {channel_id} (no repository)")
            metrics = LiveMetrics(
                channel_id=channel_id,
                timestamp=now,
                post_count_24h=0,
                avg_engagement_rate=0.0,
                growth_rate_7d=0.0,
                content_quality_score=0.5,
                anomaly_score=0.0,
            )

            self.metrics_cache[channel_id] = metrics
            return metrics

        except Exception as e:
            logger.error(f"Failed to collect live metrics for channel {channel_id}: {e}")
            return None

    async def _get_post_count_24h(self, channel_id: int) -> int:
        """Get number of posts in last 24 hours"""
        if not self.post_repo or not hasattr(self.post_repo, "pool"):
            return 0

        async with self.post_repo.pool.acquire() as conn:
            count = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM posts
                WHERE channel_id = $1
                AND date >= NOW() - INTERVAL '24 hours'
                AND is_deleted = FALSE
                """,
                channel_id,
            )
            return count or 0

    async def _calculate_avg_engagement(self, channel_id: int) -> float:
        """Calculate average engagement rate from last 7 days"""
        if not self.post_repo or not hasattr(self.post_repo, "pool"):
            return 0.0

        async with self.post_repo.pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT
                    COALESCE(AVG(
                        CASE
                            WHEN pm.views > 0
                            THEN (pm.forwards + pm.reactions_count)::float / pm.views
                            ELSE 0
                        END
                    ), 0) as avg_engagement
                FROM posts p
                JOIN LATERAL (
                    SELECT views, forwards, reactions_count
                    FROM post_metrics
                    WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                    ORDER BY snapshot_time DESC
                    LIMIT 1
                ) pm ON true
                WHERE p.channel_id = $1
                AND p.date >= NOW() - INTERVAL '7 days'
                AND p.is_deleted = FALSE
                AND pm.views > 0
                """,
                channel_id,
            )
            return float(result["avg_engagement"]) if result else 0.0

    async def _calculate_growth_rate(self, channel_id: int) -> float:
        """Calculate 7-day growth rate"""
        if not self.post_repo or not hasattr(self.post_repo, "pool"):
            return 0.0

        async with self.post_repo.pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                WITH week_data AS (
                    SELECT
                        CASE
                            WHEN p.date >= NOW() - INTERVAL '3.5 days' THEN 'recent'
                            ELSE 'previous'
                        END as period,
                        COALESCE(SUM(pm.views), 0) as total_views
                    FROM posts p
                    JOIN LATERAL (
                        SELECT views
                        FROM post_metrics
                        WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                        ORDER BY snapshot_time DESC
                        LIMIT 1
                    ) pm ON true
                    WHERE p.channel_id = $1
                    AND p.date >= NOW() - INTERVAL '7 days'
                    AND p.is_deleted = FALSE
                    GROUP BY period
                )
                SELECT
                    COALESCE(
                        (MAX(CASE WHEN period = 'recent' THEN total_views END) -
                         MAX(CASE WHEN period = 'previous' THEN total_views END))::float /
                        NULLIF(MAX(CASE WHEN period = 'previous' THEN total_views END), 0),
                        0
                    ) as growth_rate
                FROM week_data
                """,
                channel_id,
            )
            return float(result["growth_rate"]) if result else 0.0

    async def _calculate_content_quality(self, channel_id: int) -> float:
        """Calculate content quality score (0-1) based on engagement metrics"""
        if not self.post_repo or not hasattr(self.post_repo, "pool"):
            return 0.5

        async with self.post_repo.pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT
                    COALESCE(
                        AVG(
                            CASE
                                WHEN pm.views > 0 THEN
                                    LEAST(1.0, (
                                        (pm.forwards::float / NULLIF(pm.views, 0) * 0.4) +
                                        (pm.reactions_count::float / NULLIF(pm.views, 0) * 0.6)
                                    ) * 20)  -- Scale to 0-1 range
                                ELSE 0
                            END
                        ),
                        0.5
                    ) as quality_score
                FROM posts p
                JOIN LATERAL (
                    SELECT views, forwards, reactions_count
                    FROM post_metrics
                    WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                    ORDER BY snapshot_time DESC
                    LIMIT 1
                ) pm ON true
                WHERE p.channel_id = $1
                AND p.date >= NOW() - INTERVAL '7 days'
                AND p.is_deleted = FALSE
                LIMIT 10
                """,
                channel_id,
            )
            return min(1.0, max(0.0, float(result["quality_score"]))) if result else 0.5

    async def _detect_anomalies(self, channel_id: int) -> float:
        """Detect anomalies by comparing recent performance to baseline (0-1 score)"""
        if not self.post_repo or not hasattr(self.post_repo, "pool"):
            return 0.0

        async with self.post_repo.pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                WITH baseline AS (
                    SELECT AVG(pm.views) as avg_views
                    FROM posts p
                    JOIN LATERAL (
                        SELECT views
                        FROM post_metrics
                        WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                        ORDER BY snapshot_time DESC
                        LIMIT 1
                    ) pm ON true
                    WHERE p.channel_id = $1
                    AND p.date >= NOW() - INTERVAL '30 days'
                    AND p.date < NOW() - INTERVAL '3 days'
                    AND p.is_deleted = FALSE
                ),
                recent AS (
                    SELECT AVG(pm.views) as avg_views
                    FROM posts p
                    JOIN LATERAL (
                        SELECT views
                        FROM post_metrics
                        WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                        ORDER BY snapshot_time DESC
                        LIMIT 1
                    ) pm ON true
                    WHERE p.channel_id = $1
                    AND p.date >= NOW() - INTERVAL '3 days'
                    AND p.is_deleted = FALSE
                )
                SELECT
                    COALESCE(
                        ABS(
                            (recent.avg_views - baseline.avg_views)::float /
                            NULLIF(baseline.avg_views, 0)
                        ),
                        0
                    ) as anomaly_score
                FROM baseline, recent
                """,
                channel_id,
            )
            # Cap anomaly score at 1.0
            return min(1.0, float(result["anomaly_score"])) if result else 0.0

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
                return {
                    "channel_id": channel_id,
                    "status": "no_data",
                    "timestamp": datetime.now(),
                }

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
