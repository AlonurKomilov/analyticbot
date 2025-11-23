"""
Alerts Management Service
========================

Focused microservice for alert configuration, rule management, and alert checking.

Single Responsibility:
- Alert system setup and configuration
- Alert rules creation and management
- Real-time alert checking
- Alert baselines and thresholds
- Alert notifications triggering

Extracted from AlertsIntelligenceService god object (300 lines of responsibility).
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from core.ports.repository_ports import ChannelDailyRepository, ChannelRepository, PostRepository

from ..protocols import AlertsManagementProtocol

logger = logging.getLogger(__name__)


class AlertsManagementService(AlertsManagementProtocol):
    """
    Alerts management microservice for intelligent alerting.

    Single responsibility: Alert configuration, rules, and checking only.
    No live monitoring, no competitive analysis - pure alerts focus.
    """

    def __init__(
        self,
        posts_repo: PostRepository,
        daily_repo: ChannelDailyRepository,
        channels_repo: ChannelRepository,
        live_monitoring_service=None,
        config_manager=None,
        telegram_delivery_service=None,
        alert_rule_manager=None,
    ):
        self._posts = posts_repo
        self._daily = daily_repo
        self._channels = channels_repo
        self._monitoring = live_monitoring_service
        self._telegram_delivery = telegram_delivery_service
        self._alert_rule_manager = alert_rule_manager

        # Alert configuration
        self.alert_config = {
            "baseline_days": 30,
            "anomaly_threshold": 2.0,  # Standard deviations
            "engagement_threshold": 0.8,  # 80% of baseline
            "growth_threshold": 0.1,  # 10% growth required
            "performance_threshold": 0.7,  # 70% of baseline
        }

        logger.info("🚨 Alerts Management Service initialized - intelligent alerting focus")

    async def setup_intelligent_alerts(
        self, channel_id: int, alert_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Setup intelligent alert system for a channel.

        Core method extracted from god object - handles alert system configuration.
        """
        try:
            logger.info(f"⚙️ Setting up intelligent alerts for channel {channel_id}")

            # Default alert configuration
            default_config = {
                "engagement_alerts": True,
                "growth_alerts": True,
                "performance_alerts": True,
                "anomaly_detection": True,
                "notification_frequency": "immediate",
                "alert_severity_levels": ["critical", "high", "medium", "low"],
                "custom_thresholds": {},
            }

            # Merge with custom config
            config = {**default_config, **(alert_config or {})}

            # Establish baselines for alert rules
            baseline = await self.establish_alert_baselines(channel_id)

            # Create alert rules based on configuration
            alert_rules = await self._create_alert_rules(channel_id, config, baseline)

            # Initialize alert monitoring
            monitoring_result = await self._initialize_alert_monitoring(channel_id, alert_rules)

            setup_result = {
                "channel_id": channel_id,
                "setup_timestamp": datetime.now().isoformat(),
                "alert_configuration": config,
                "baseline_metrics": baseline,
                "alert_rules": alert_rules,
                "monitoring_status": monitoring_result,
                "status": "alerts_configured",
            }

            logger.info(f"✅ Intelligent alerts configured for channel {channel_id}")
            return setup_result

        except Exception as e:
            logger.error(f"❌ Alert setup failed for channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "setup_timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "setup_failed",
            }

    async def check_real_time_alerts(self, channel_id: int) -> dict[str, Any]:
        """
        Check for real-time alerts.

        Core method extracted from god object - handles real-time alert checking.
        """
        try:
            logger.info(f"🔍 Checking real-time alerts for channel {channel_id}")

            # Get current metrics from monitoring service
            current_metrics = {}
            if self._monitoring:
                try:
                    current_metrics = await self._monitoring.get_current_metrics(channel_id)
                except Exception as e:
                    logger.warning(f"Failed to get current metrics from monitoring service: {e}")
                    # Return empty result if monitoring fails - don't use mock data
                    return {
                        "channel_id": channel_id,
                        "check_timestamp": datetime.now().isoformat(),
                        "total_alerts": 0,
                        "active_alerts": [],
                        "alert_summary": {"error": "Monitoring service unavailable"},
                    }

            # Get alert configuration
            alert_config = await self._get_alert_configuration(channel_id)

            # Check different types of alerts
            all_alerts = []

            # Engagement alerts
            engagement_alerts = await self._check_engagement_alerts(
                channel_id, current_metrics, alert_config
            )
            all_alerts.extend(engagement_alerts)

            # Growth alerts
            growth_alerts = await self._check_growth_alerts(
                channel_id, current_metrics, alert_config
            )
            all_alerts.extend(growth_alerts)

            # Performance alerts
            performance_alerts = await self._check_performance_alerts(
                channel_id, current_metrics, alert_config
            )
            all_alerts.extend(performance_alerts)

            # Statistical anomaly alerts
            anomaly_alerts = await self._check_statistical_anomalies(
                channel_id, current_metrics, alert_config
            )
            all_alerts.extend(anomaly_alerts)

            # Success alerts - celebrate wins!
            success_alerts = await self._check_success_milestones(channel_id, current_metrics)
            all_alerts.extend(success_alerts)

            # Add actionable recommendations to each alert
            for alert in all_alerts:
                alert["recommendations"] = await self.generate_actionable_recommendations(
                    channel_id, alert
                )

            # Trigger notifications for active alerts
            if all_alerts:
                await self._trigger_alert_notifications(channel_id, all_alerts)

            alert_result = {
                "channel_id": channel_id,
                "check_timestamp": datetime.now().isoformat(),
                "total_alerts": len(all_alerts),
                "active_alerts": all_alerts,
                "alert_summary": self._summarize_alerts(all_alerts),
                "status": "alerts_checked",
            }

            logger.info(
                f"✅ Real-time alerts checked for channel {channel_id}: {len(all_alerts)} alerts"
            )
            return alert_result

        except Exception as e:
            logger.error(f"❌ Alert checking failed for channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "check_timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "check_failed",
            }

    async def check_user_alerts_aggregated(self, user_id: int) -> dict[str, Any]:
        """
        Check alerts across all user's channels and aggregate similar ones.

        This reduces notification spam by combining similar alerts:
        - "3 channels have low engagement" instead of 3 separate alerts
        - Prioritizes most urgent issues
        - Groups by alert type and severity
        """
        try:
            logger.info(f"🔍 Checking aggregated alerts for user {user_id}")

            # Get all active channels for this user
            query = """
                SELECT id, username, title
                FROM channels
                WHERE user_id = $1 AND is_active = true
                ORDER BY subscriber_count DESC
            """
            channels = await self._channels.db.fetch(query, user_id)

            if not channels:
                return {
                    "user_id": user_id,
                    "check_timestamp": datetime.now().isoformat(),
                    "total_channels": 0,
                    "aggregated_alerts": [],
                    "status": "no_channels",
                }

            # Check alerts for each channel
            all_alerts = []
            channel_names = {}

            for channel in channels:
                channel_id = channel["id"]
                channel_names[channel_id] = channel["username"] or channel["title"]

                # Check alerts for this channel
                result = await self.check_real_time_alerts(channel_id)
                if result.get("active_alerts"):
                    for alert in result["active_alerts"]:
                        alert["channel_name"] = channel_names[channel_id]
                        all_alerts.append(alert)

            # Aggregate similar alerts
            aggregated = self._aggregate_alerts(all_alerts, channel_names)

            logger.info(
                f"✅ Aggregated {len(all_alerts)} alerts into {len(aggregated)} notifications "
                f"for user {user_id} ({len(channels)} channels)"
            )

            return {
                "user_id": user_id,
                "check_timestamp": datetime.now().isoformat(),
                "total_channels": len(channels),
                "raw_alerts": len(all_alerts),
                "aggregated_alerts": aggregated,
                "channels_with_alerts": len(set(a["channel_id"] for a in all_alerts)),
                "status": "alerts_aggregated",
            }

        except Exception as e:
            logger.error(f"❌ Aggregated alert check failed for user {user_id}: {e}")
            return {
                "user_id": user_id,
                "check_timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "check_failed",
            }

    def _aggregate_alerts(
        self, alerts: list[dict[str, Any]], channel_names: dict[int, str]
    ) -> list[dict[str, Any]]:
        """
        Aggregate similar alerts to reduce notification spam.

        Groups alerts by:
        1. Alert type (engagement, growth, performance)
        2. Severity level
        3. Similar thresholds

        Returns combined alerts with channel lists.
        """
        if not alerts:
            return []

        from collections import defaultdict

        # Group alerts by type and severity
        groups = defaultdict(list)

        for alert in alerts:
            alert_type = alert.get("alert_type", "unknown")
            severity = alert.get("severity", "medium")
            key = f"{alert_type}_{severity}"
            groups[key].append(alert)

        aggregated = []

        for key, group_alerts in groups.items():
            if len(group_alerts) == 1:
                # Single alert - send as-is
                aggregated.append(group_alerts[0])
            else:
                # Multiple similar alerts - aggregate
                alert_type, severity = key.split("_")
                channel_list = [a["channel_name"] for a in group_alerts]
                channel_ids = [a["channel_id"] for a in group_alerts]

                # Calculate aggregate metrics
                avg_current = sum(a.get("current_value", 0) for a in group_alerts) / len(
                    group_alerts
                )
                avg_baseline = sum(a.get("baseline", 0) for a in group_alerts) / len(group_alerts)

                # Create aggregated alert
                aggregated_alert = {
                    "alert_id": f"aggregated_{alert_type}_{severity}_{int(datetime.now().timestamp())}",
                    "alert_type": alert_type,
                    "severity": severity,
                    "is_aggregated": True,
                    "affected_channels": len(group_alerts),
                    "channel_names": channel_list[:3],  # Show first 3
                    "channel_ids": channel_ids,
                    "remaining_channels": max(0, len(group_alerts) - 3),
                    "message": self._generate_aggregated_message(
                        alert_type, severity, len(group_alerts), channel_list[:3]
                    ),
                    "triggered_at": datetime.now().isoformat(),
                    "avg_current_value": avg_current,
                    "avg_baseline": avg_baseline,
                }

                aggregated.append(aggregated_alert)

        # Sort by severity (critical > high > medium > low)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        aggregated.sort(key=lambda x: severity_order.get(x.get("severity", "medium"), 2))

        return aggregated

    def _generate_aggregated_message(
        self, alert_type: str, severity: str, count: int, channel_names: list[str]
    ) -> str:
        """Generate human-readable message for aggregated alerts"""

        # Type-specific messaging
        type_messages = {
            "QUIET": "low engagement",
            "SPIKE": "performance issues",
            "GROWTH": "growth concerns",
        }

        issue_desc = type_messages.get(alert_type, "issues")

        if count == 2:
            channels_text = f"{channel_names[0]} and {channel_names[1]}"
        elif count == 3:
            channels_text = f"{channel_names[0]}, {channel_names[1]}, and {channel_names[2]}"
        else:
            channels_text = f"{channel_names[0]}, {channel_names[1]}, and {count - 2} others"

        severity_emoji = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "⚡",
            "low": "ℹ️",
        }

        emoji = severity_emoji.get(severity, "⚡")

        return f"{emoji} {count} channels have {issue_desc}: {channels_text}"

    async def establish_alert_baselines(self, channel_id: int) -> dict[str, Any]:
        """
        Establish baseline metrics for alert thresholds.

        Extracted method for creating statistical baselines.
        """
        try:
            logger.info(f"📊 Establishing alert baselines for channel {channel_id}")

            # Get historical data for baseline calculation
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=self.alert_config["baseline_days"])

            # Get historical daily data
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date, datetime.max.time())

            daily_views = await self._daily.series_data(channel_id, "views", start_dt, end_dt)
            daily_followers = await self._daily.series_data(
                channel_id, "followers", start_dt, end_dt
            )  # Fallback for different naming conventions
            if not daily_followers:
                daily_followers = await self._daily.series_data(
                    channel_id, "subscribers", start_dt, end_dt
                )

            # Get historical posts data using available repository methods
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date, datetime.max.time())

            posts_count = await self._posts.count(channel_id, start_dt, end_dt)
            total_views = await self._posts.sum_views(channel_id, start_dt, end_dt)
            top_posts = await self._posts.top_by_views(channel_id, start_dt, end_dt, 10)

            # Create mock posts structure for compatibility
            posts = [
                {
                    "id": i,
                    "views": total_views // max(posts_count, 1),
                    "created_at": start_dt,
                    "text": f"Post {i}",
                }
                for i in range(min(posts_count, 10))
            ]

            # Calculate baseline statistics
            baseline = {
                "channel_id": channel_id,
                "baseline_period_days": self.alert_config["baseline_days"],
                "calculated_at": datetime.now().isoformat(),
                "views_stats": self._calculate_baseline_stats(
                    [d.get("value", 0.0) for d in daily_views]
                ),
                "followers_stats": self._calculate_baseline_stats(
                    [d.get("value", 0.0) for d in daily_followers]
                ),
                "post_count": len(posts),
                "engagement_baseline": self._calculate_engagement_baseline(
                    [d.get("value", 0.0) for d in daily_views],
                    [d.get("value", 0.0) for d in daily_followers],
                ),
                "status": "baseline_established",
            }

            logger.info(f"✅ Alert baselines established for channel {channel_id}")
            return baseline

        except Exception as e:
            logger.error(f"❌ Baseline establishment failed for channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "calculated_at": datetime.now().isoformat(),
                "error": str(e),
                "status": "baseline_failed",
            }

    async def _create_alert_rules(
        self, channel_id: int, config: dict[str, Any], baseline: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Create alert rules based on configuration and baselines"""
        try:
            rules = []

            # Engagement alert rules
            if config.get("engagement_alerts", True):
                rules.append(
                    {
                        "rule_id": f"engagement_{channel_id}",
                        "type": "engagement",
                        "threshold": baseline.get("engagement_baseline", {}).get("mean", 0)
                        * self.alert_config["engagement_threshold"],
                        "severity": "high",
                        "description": "Engagement rate below baseline threshold",
                    }
                )

            # Growth alert rules
            if config.get("growth_alerts", True):
                follower_mean = baseline.get("followers_stats", {}).get("mean", 0)
                rules.append(
                    {
                        "rule_id": f"growth_{channel_id}",
                        "type": "growth",
                        "threshold": follower_mean * (1 + self.alert_config["growth_threshold"]),
                        "severity": "medium",
                        "description": "Growth rate below expected threshold",
                    }
                )

            # Performance alert rules
            if config.get("performance_alerts", True):
                views_mean = baseline.get("views_stats", {}).get("mean", 0)
                rules.append(
                    {
                        "rule_id": f"performance_{channel_id}",
                        "type": "performance",
                        "threshold": views_mean * self.alert_config["performance_threshold"],
                        "severity": "medium",
                        "description": "Performance below baseline threshold",
                    }
                )

            # Anomaly detection rules
            if config.get("anomaly_detection", True):
                rules.append(
                    {
                        "rule_id": f"anomaly_{channel_id}",
                        "type": "anomaly",
                        "threshold": self.alert_config["anomaly_threshold"],
                        "severity": "critical",
                        "description": "Statistical anomaly detected",
                    }
                )

            logger.info(f"📋 Created {len(rules)} alert rules for channel {channel_id}")
            return rules

        except Exception as e:
            logger.error(f"Alert rules creation failed: {e}")
            return []

    async def _get_channel_dynamic_thresholds(self, channel_id: int) -> dict[str, Any]:
        """
        Calculate dynamic alert thresholds based on channel's historical baseline.

        ✅ UNIFIED (Nov 21, 2025): Now uses SmartRulesGenerator to ensure
        UI-displayed rules match background alert checking thresholds.
        """
        try:
            # Use SmartRulesGenerator for consistency with UI
            from core.services.alerts_fusion.alerts.smart_rules_generator import (
                SmartRulesGenerator,
            )

            generator = SmartRulesGenerator(self._channels, self._daily, self._posts)
            smart_rules = await generator.generate_smart_rules_for_channel(channel_id)

            # Convert smart rules to threshold format for backward compatibility
            thresholds = {
                "source": "smart_rules_generator",
                "personalized": any(r.get("personalized", False) for r in smart_rules),
            }

            # Extract thresholds from smart rules
            for rule in smart_rules:
                rule_id = rule.get("id", "")
                threshold = rule.get("threshold", 0)
                baseline = rule.get("baseline_value", 0)

                if "engagement" in rule_id:
                    if "low" in rule_id or "viral" not in rule_id:
                        thresholds["engagement_threshold"] = threshold
                        thresholds["engagement_critical_threshold"] = threshold * 0.5
                        thresholds["baseline_engagement"] = baseline
                    else:  # viral potential
                        thresholds["engagement_high_threshold"] = threshold

                elif "subscriber" in rule_id:
                    thresholds["growth_threshold"] = abs(threshold)  # Positive value
                    thresholds["subscriber_loss_threshold"] = threshold  # Negative value

                elif "performance" in rule_id or "views" in rule_id:
                    thresholds["views_threshold"] = threshold
                    thresholds["baseline_views"] = baseline

            # Add defaults if not set
            thresholds.setdefault("engagement_threshold", 2.0)
            thresholds.setdefault("engagement_critical_threshold", 1.0)
            thresholds.setdefault("baseline_engagement", 3.0)
            thresholds.setdefault("views_threshold", 100)
            thresholds.setdefault("baseline_views", 200)
            thresholds.setdefault("growth_threshold", 10)
            thresholds.setdefault("anomaly_std_multiplier", 2.0)

            logger.debug(
                f"✅ Dynamic thresholds from SmartRulesGenerator for channel {channel_id}: "
                f"engagement={thresholds['engagement_threshold']:.2f}%, "
                f"subscriber_loss={thresholds.get('subscriber_loss_threshold', 0)}"
            )

            return thresholds

        except Exception as e:
            logger.warning(
                f"SmartRulesGenerator failed for channel {channel_id}, using fallback: {e}"
            )
            # Fallback to old logic if SmartRulesGenerator fails
            return await self._get_channel_dynamic_thresholds_fallback(channel_id)

    async def _get_channel_dynamic_thresholds_fallback(self, channel_id: int) -> dict[str, Any]:
        """
        Fallback threshold calculation (old logic).
        Used only if SmartRulesGenerator fails.
        """
        try:
            # Get 30-day historical data for baseline calculation
            from_date = datetime.now() - timedelta(days=30)

            # Fetch historical metrics
            query = """
                SELECT
                    AVG(views) as avg_views,
                    STDDEV(views) as stddev_views,
                    AVG(subscribers) as avg_subscribers,
                    STDDEV(subscribers) as stddev_subscribers,
                    AVG(CASE
                        WHEN views > 0
                        THEN (forwards + reactions_count)::float / views * 100
                        ELSE 0
                    END) as avg_engagement_rate,
                    STDDEV(CASE
                        WHEN views > 0
                        THEN (forwards + reactions_count)::float / views * 100
                        ELSE 0
                    END) as stddev_engagement_rate
                FROM channel_daily_analytics
                WHERE channel_id = $1
                  AND date >= $2
                HAVING COUNT(*) >= 7  -- Need at least 7 days of data
            """

            result = await self._daily.db.fetchrow(query, channel_id, from_date.date())

            if not result or not result["avg_views"]:
                # Not enough data - use conservative defaults based on channel size
                channel = await self._channels.get_by_channel_id(channel_id)
                subscriber_count = channel.subscriber_count if channel else 0

                # Scale thresholds based on channel size
                if subscriber_count < 100:
                    base_views = 50
                    base_engagement = 1.0
                elif subscriber_count < 1000:
                    base_views = 200
                    base_engagement = 2.0
                elif subscriber_count < 10000:
                    base_views = 1000
                    base_engagement = 3.0
                else:
                    base_views = 5000
                    base_engagement = 4.0

                return {
                    "views_threshold": base_views * 0.5,  # 50% of expected
                    "engagement_threshold": base_engagement * 0.6,  # 60% of expected
                    "growth_threshold": subscriber_count * 0.001,  # 0.1% growth per day
                    "anomaly_std_multiplier": 2.5,  # More sensitive for new channels
                    "source": "default_fallback",
                    "channel_size": subscriber_count,
                }

            # Calculate thresholds from actual data
            avg_views = float(result["avg_views"] or 0)
            stddev_views = float(result["stddev_views"] or avg_views * 0.3)
            avg_engagement = float(result["avg_engagement_rate"] or 2.0)
            stddev_engagement = float(result["stddev_engagement_rate"] or 1.0)
            avg_subscribers = float(result["avg_subscribers"] or 0)

            # Dynamic thresholds:
            # - Views: 70% of average (allows 30% drop before alert)
            # - Engagement: 60% of average (more sensitive to engagement drops)
            # - Growth: Detect negative or stagnant growth
            # - Anomaly: 2 standard deviations from mean

            thresholds = {
                "views_threshold": avg_views * 0.7,
                "views_critical_threshold": avg_views * 0.4,  # Critical if 60% drop
                "engagement_threshold": avg_engagement * 0.6,
                "engagement_critical_threshold": avg_engagement * 0.3,
                "growth_threshold": avg_subscribers * 0.002,  # 0.2% daily growth expected
                "anomaly_std_multiplier": 2.0,  # 2 std deviations
                "baseline_views": avg_views,
                "baseline_engagement": avg_engagement,
                "baseline_subscribers": avg_subscribers,
                "stddev_views": stddev_views,
                "stddev_engagement": stddev_engagement,
                "source": "historical_fallback",
                "data_points": 30,
            }

            logger.debug(f"Fallback dynamic thresholds for channel {channel_id}: {thresholds}")
            return thresholds

        except Exception as e:
            logger.error(f"Failed to calculate fallback thresholds for channel {channel_id}: {e}")
            # Return safe defaults on error
            return {
                "views_threshold": 100,
                "engagement_threshold": 1.0,
                "growth_threshold": 1,
                "anomaly_std_multiplier": 2.5,
                "source": "error_fallback",
            }

    async def _check_engagement_alerts(
        self, channel_id: int, current_metrics: dict[str, Any], alert_config: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Check for engagement-related alerts with dynamic thresholds"""
        try:
            alerts = []

            # Get dynamic thresholds for this channel
            thresholds = await self._get_channel_dynamic_thresholds(channel_id)

            # Get current engagement rate
            current_engagement = current_metrics.get("engagement_rate", 0)

            # Critical engagement alert
            if current_engagement < thresholds["engagement_critical_threshold"]:
                alerts.append(
                    {
                        "alert_id": f"engagement_critical_{channel_id}_{int(datetime.now().timestamp())}",
                        "alert_type": "QUIET",
                        "severity": "critical",
                        "message": f"Critical: Engagement rate ({current_engagement:.2f}%) is {thresholds['baseline_engagement'] / current_engagement:.1f}x below baseline",
                        "channel_id": channel_id,
                        "triggered_at": datetime.now().isoformat(),
                        "current_value": current_engagement,
                        "baseline": thresholds["baseline_engagement"],
                        "threshold": thresholds["engagement_critical_threshold"],
                        "decrease_pct": (
                            (thresholds["baseline_engagement"] - current_engagement)
                            / thresholds["baseline_engagement"]
                            * 100
                        ),
                    }
                )
            # Warning engagement alert
            elif current_engagement < thresholds["engagement_threshold"]:
                alerts.append(
                    {
                        "alert_id": f"engagement_low_{channel_id}_{int(datetime.now().timestamp())}",
                        "alert_type": "QUIET",
                        "severity": "high",
                        "message": f"Engagement rate ({current_engagement:.2f}%) below baseline ({thresholds['baseline_engagement']:.2f}%)",
                        "channel_id": channel_id,
                        "triggered_at": datetime.now().isoformat(),
                        "current_value": current_engagement,
                        "baseline": thresholds["baseline_engagement"],
                        "threshold": thresholds["engagement_threshold"],
                        "decrease_pct": (
                            (thresholds["baseline_engagement"] - current_engagement)
                            / thresholds["baseline_engagement"]
                            * 100
                        ),
                    }
                )

            return alerts

        except Exception as e:
            logger.error(f"Engagement alerts check failed: {e}")
            return []

    async def _check_growth_alerts(
        self, channel_id: int, current_metrics: dict[str, Any], alert_config: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Check for growth-related alerts with dynamic thresholds"""
        try:
            alerts = []

            # Get dynamic thresholds
            thresholds = await self._get_channel_dynamic_thresholds(channel_id)

            # Get growth rate from metrics
            growth_rate = current_metrics.get("growth_rate", 0)
            current_subscribers = current_metrics.get("current_followers", 0)

            # Check for negative or stagnant growth
            if growth_rate < 0:
                alerts.append(
                    {
                        "alert_id": f"growth_negative_{channel_id}_{int(datetime.now().timestamp())}",
                        "alert_type": "GROWTH",
                        "severity": "high",
                        "message": f"Subscriber count declining: {abs(growth_rate):.1f}% decrease",
                        "channel_id": channel_id,
                        "triggered_at": datetime.now().isoformat(),
                        "current_value": growth_rate,
                        "baseline": thresholds["baseline_subscribers"],
                        "threshold": 0,
                    }
                )
            elif growth_rate < thresholds["growth_threshold"]:
                alerts.append(
                    {
                        "alert_id": f"growth_stagnant_{channel_id}_{int(datetime.now().timestamp())}",
                        "alert_type": "GROWTH",
                        "severity": "medium",
                        "message": f"Growth rate ({growth_rate:.2f}%) below expected threshold",
                        "channel_id": channel_id,
                        "triggered_at": datetime.now().isoformat(),
                        "current_value": growth_rate,
                        "baseline": thresholds["baseline_subscribers"],
                        "threshold": thresholds["growth_threshold"],
                    }
                )

            return alerts

        except Exception as e:
            logger.error(f"Growth alerts check failed: {e}")
            return []

    async def _check_performance_alerts(
        self, channel_id: int, current_metrics: dict[str, Any], alert_config: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Check for performance-related alerts with dynamic thresholds"""
        try:
            alerts = []

            # Get dynamic thresholds
            thresholds = await self._get_channel_dynamic_thresholds(channel_id)

            # Get current metrics
            post_count_24h = current_metrics.get("post_count_24h", 0)
            avg_views = current_metrics.get("avg_views", 0)
            content_quality = current_metrics.get("content_quality", 0)

            # Critical views alert
            if avg_views > 0 and avg_views < thresholds["views_critical_threshold"]:
                alerts.append(
                    {
                        "alert_id": f"views_critical_{channel_id}_{int(datetime.now().timestamp())}",
                        "alert_type": "SPIKE",
                        "severity": "critical",
                        "message": f"Critical: Average views ({avg_views:.0f}) is {(thresholds['baseline_views'] / avg_views):.1f}x below baseline",
                        "channel_id": channel_id,
                        "triggered_at": datetime.now().isoformat(),
                        "current_value": avg_views,
                        "baseline": thresholds["baseline_views"],
                        "threshold": thresholds["views_critical_threshold"],
                        "decrease_pct": (
                            (thresholds["baseline_views"] - avg_views)
                            / thresholds["baseline_views"]
                            * 100
                        ),
                    }
                )
            # Warning views alert
            elif avg_views > 0 and avg_views < thresholds["views_threshold"]:
                alerts.append(
                    {
                        "alert_id": f"views_low_{channel_id}_{int(datetime.now().timestamp())}",
                        "alert_type": "SPIKE",
                        "severity": "high",
                        "message": f"Average views ({avg_views:.0f}) below baseline ({thresholds['baseline_views']:.0f})",
                        "channel_id": channel_id,
                        "triggered_at": datetime.now().isoformat(),
                        "current_value": avg_views,
                        "baseline": thresholds["baseline_views"],
                        "threshold": thresholds["views_threshold"],
                        "decrease_pct": (
                            (thresholds["baseline_views"] - avg_views)
                            / thresholds["baseline_views"]
                            * 100
                        ),
                    }
                )

            # Content quality alert
            if content_quality < 0.5:  # Below 50% quality score
                alerts.append(
                    {
                        "alert_id": f"quality_low_{channel_id}_{int(datetime.now().timestamp())}",
                        "alert_type": "QUIET",
                        "severity": "medium",
                        "message": f"Content quality score ({content_quality:.1%}) is low",
                        "channel_id": channel_id,
                        "triggered_at": datetime.now().isoformat(),
                        "current_value": content_quality,
                        "threshold": 0.5,
                    }
                )

            return alerts

        except Exception as e:
            logger.error(f"Performance alerts check failed: {e}")
            return []

    async def _check_statistical_anomalies(
        self, channel_id: int, current_metrics: dict[str, Any], alert_config: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Check for statistical anomalies"""
        try:
            alerts = []

            # Example anomaly detection logic
            recent_posts_24h = current_metrics.get("recent_posts_24h", 0)

            # Simplified anomaly check
            if recent_posts_24h > 10:  # Unusually high posting frequency
                alerts.append(
                    {
                        "alert_id": f"anomaly_high_posting_{channel_id}_{int(datetime.now().timestamp())}",
                        "type": "anomaly",
                        "severity": "critical",
                        "message": f"Unusual posting frequency detected: {recent_posts_24h} posts in 24h",
                        "channel_id": channel_id,
                        "triggered_at": datetime.now().isoformat(),
                        "metric_value": recent_posts_24h,
                        "anomaly_type": "high_posting_frequency",
                    }
                )

            return alerts

        except Exception as e:
            logger.error(f"Statistical anomaly check failed: {e}")
            return []

    async def _check_success_milestones(
        self, channel_id: int, current_metrics: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Check for success milestones and positive achievements.

        Celebrates:
        - Subscriber milestones (1K, 5K, 10K, 50K, 100K, etc.)
        - Engagement improvements (>25% increase)
        - View count achievements
        - Growth rate increases
        """
        try:
            alerts = []

            # Get current channel stats
            channel = await self._channels.get_by_channel_id(channel_id)
            if not channel:
                return []

            current_subscribers = channel.subscriber_count

            # Check subscriber milestones
            milestones = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]

            for milestone in milestones:
                # Check if just crossed milestone (within last 7 days)
                if current_subscribers >= milestone:
                    # Check if this is recent achievement
                    recent = await self._is_recent_milestone(channel_id, milestone)
                    if recent:
                        alerts.append(
                            {
                                "alert_id": f"success_milestone_{channel_id}_{milestone}_{int(datetime.now().timestamp())}",
                                "alert_type": "SUCCESS",
                                "severity": "success",
                                "message": f"🎉 Congratulations! You reached {milestone:,} subscribers!",
                                "channel_id": channel_id,
                                "triggered_at": datetime.now().isoformat(),
                                "milestone_type": "subscribers",
                                "milestone_value": milestone,
                                "current_value": current_subscribers,
                            }
                        )
                        break  # Only celebrate one milestone at a time

            # Check engagement improvements
            engagement_rate = current_metrics.get("engagement_rate", 0)
            avg_engagement = current_metrics.get("avg_engagement_rate", 0)

            if avg_engagement > 0 and engagement_rate > avg_engagement * 1.5:  # 50% improvement
                alerts.append(
                    {
                        "alert_id": f"success_engagement_{channel_id}_{int(datetime.now().timestamp())}",
                        "alert_type": "SUCCESS",
                        "severity": "success",
                        "message": f"🚀 Amazing! Your engagement is up {((engagement_rate / avg_engagement - 1) * 100):.0f}%!",
                        "channel_id": channel_id,
                        "triggered_at": datetime.now().isoformat(),
                        "success_type": "engagement_boost",
                        "current_value": engagement_rate,
                        "baseline": avg_engagement,
                        "improvement_pct": ((engagement_rate / avg_engagement - 1) * 100),
                    }
                )

            # Check view count achievements (viral post)
            avg_views = current_metrics.get("avg_views", 0)

            if avg_views > 10000:  # High view count
                # Check if this is unusually high
                query = """
                    SELECT AVG(views) as historical_avg
                    FROM channel_daily_analytics
                    WHERE channel_id = $1
                      AND date > NOW() - INTERVAL '30 days'
                """
                result = await self._daily.db.fetchrow(query, channel_id)
                historical_avg = (
                    float(result["historical_avg"]) if result and result["historical_avg"] else 0
                )

                if historical_avg > 0 and avg_views > historical_avg * 3:  # 3x normal
                    alerts.append(
                        {
                            "alert_id": f"success_viral_{channel_id}_{int(datetime.now().timestamp())}",
                            "alert_type": "SUCCESS",
                            "severity": "success",
                            "message": f"🔥 Viral alert! Your content is getting {(avg_views / historical_avg):.1f}x more views than usual!",
                            "channel_id": channel_id,
                            "triggered_at": datetime.now().isoformat(),
                            "success_type": "viral_content",
                            "current_value": avg_views,
                            "baseline": historical_avg,
                            "multiplier": (avg_views / historical_avg),
                        }
                    )

            # Check growth rate improvements
            growth_rate = current_metrics.get("growth_rate", 0)

            if growth_rate > 5:  # >5% growth rate
                alerts.append(
                    {
                        "alert_id": f"success_growth_{channel_id}_{int(datetime.now().timestamp())}",
                        "alert_type": "SUCCESS",
                        "severity": "success",
                        "message": f"📈 Excellent growth! Your channel is growing at {growth_rate:.1f}% per day!",
                        "channel_id": channel_id,
                        "triggered_at": datetime.now().isoformat(),
                        "success_type": "high_growth",
                        "growth_rate": growth_rate,
                    }
                )

            return alerts

        except Exception as e:
            logger.error(f"Success milestone check failed: {e}")
            return []

    async def _is_recent_milestone(self, channel_id: int, milestone: int) -> bool:
        """Check if milestone was recently crossed (within last 7 days)"""
        try:
            # Check if we recently crossed this threshold
            query = """
                SELECT COUNT(*) as count
                FROM channel_daily_analytics
                WHERE channel_id = $1
                  AND date >= NOW() - INTERVAL '7 days'
                  AND subscribers >= $2
                ORDER BY date DESC
                LIMIT 1
            """

            result = await self._daily.db.fetchrow(query, channel_id, milestone)

            if not result or result["count"] == 0:
                return False

            # Check if we already sent alert for this milestone
            alert_query = """
                SELECT COUNT(*) as count
                FROM alert_sent
                WHERE channel_id = $1
                  AND alert_type = 'SUCCESS'
                  AND sent_at > NOW() - INTERVAL '30 days'
            """

            alert_result = await self._posts.db.fetchrow(alert_query, channel_id)

            # Don't send if already sent success alert recently
            return alert_result["count"] == 0 if alert_result else True

        except Exception as e:
            logger.warning(f"Error checking recent milestone: {e}")
            return False

    async def _get_alert_configuration(self, channel_id: int) -> dict[str, Any]:
        """Get alert configuration for a channel"""
        # For now, return default configuration
        # In a real implementation, this would fetch from database
        return {
            "engagement_alerts": True,
            "growth_alerts": True,
            "performance_alerts": True,
            "anomaly_detection": True,
            "notification_frequency": "immediate",
        }

    async def _initialize_alert_monitoring(
        self, channel_id: int, alert_rules: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Initialize alert monitoring for a channel"""
        return {
            "monitoring_active": True,
            "rules_count": len(alert_rules),
            "monitoring_started": datetime.now().isoformat(),
            "next_check": (datetime.now() + timedelta(minutes=5)).isoformat(),
        }

    async def _trigger_alert_notifications(
        self, channel_id: int, alerts: list[dict[str, Any]]
    ) -> bool:
        """Trigger alert notifications via Telegram with preferences and deduplication"""
        try:
            if not self._telegram_delivery:
                logger.warning("Telegram delivery service not available, skipping notifications")
                return False

            if not alerts:
                logger.debug(f"No alerts to send for channel {channel_id}")
                return True

            # Fetch channel info and owner
            channel = await self._channels.get_by_channel_id(channel_id)
            if not channel:
                logger.error(f"Channel {channel_id} not found, cannot send alerts")
                return False

            channel_name = channel.username if channel else f"Channel {channel_id}"
            user_id = channel.user_id

            if not user_id:
                logger.error(f"No user_id for channel {channel_id}, cannot send alerts")
                return False

            # Check if channel is muted
            if await self._is_channel_muted(user_id, channel_id):
                logger.info(f"⏸️ Channel {channel_id} is muted for user {user_id}, skipping alerts")
                return True

            # Get user preferences
            preferences = await self._get_user_alert_preferences(user_id)

            # Check if alerts are globally disabled
            if not preferences.get("enabled", True):
                logger.info(f"⏸️ Alerts disabled for user {user_id}")
                return True

            # Check if Telegram notifications are enabled
            if not preferences.get("telegram_enabled", True):
                logger.info(f"⏸️ Telegram notifications disabled for user {user_id}")
                return True

            # Check quiet hours
            if await self._is_in_quiet_hours(preferences):
                logger.info(f"🌙 In quiet hours for user {user_id}, alerts will be batched")
                # TODO: Store for daily digest instead
                return True

            # Filter alerts by minimum severity
            min_severity = preferences.get("min_severity", "medium")
            filtered_alerts = self._filter_alerts_by_severity(alerts, min_severity)

            if not filtered_alerts:
                logger.info(f"⏭️ All alerts filtered out by severity preference for user {user_id}")
                return True

            # Check alert frequency preference
            alert_frequency = preferences.get("alert_frequency", "immediate")
            if alert_frequency != "immediate":
                logger.info(f"📬 Alert frequency is '{alert_frequency}', storing for digest")
                # TODO: Store for batch delivery
                return True

            # Check for recent duplicate alerts to avoid spam
            sent_count = 0
            failed_count = 0
            skipped_count = 0

            for alert in filtered_alerts:
                alert_type = alert.get("alert_type", "unknown")
                severity = alert.get("severity", "medium")

                # Check if same alert sent recently (within last hour)
                if await self._is_duplicate_alert(user_id, channel_id, alert_type, hours=1):
                    logger.info(
                        f"⏭️ Skipping duplicate alert: {alert_type} for channel {channel_id} "
                        f"(already sent within last hour)"
                    )
                    skipped_count += 1
                    continue

                # Enrich alert data with channel info
                alert_data = {
                    **alert,
                    "channel_name": channel_name,
                    "channel_id": channel_id,
                }

                # Send alert via Telegram
                result = await self._telegram_delivery.send_alert(
                    chat_id=user_id, alert_data=alert_data
                )

                # Record alert in database
                if result.get("status") == "sent":
                    sent_count += 1
                    await self._record_alert_sent(
                        user_id=user_id,
                        channel_id=channel_id,
                        alert_type=alert_type,
                        severity=severity,
                        status="sent",
                        message_id=result.get("message_id"),
                    )
                    logger.info(f"✅ Alert sent: {alert_type} to user {user_id}")
                else:
                    failed_count += 1
                    await self._record_alert_sent(
                        user_id=user_id,
                        channel_id=channel_id,
                        alert_type=alert_type,
                        severity=severity,
                        status="failed",
                        error_message=result.get("error"),
                    )
                    logger.error(f"❌ Alert failed: {alert_type} - {result.get('error')}")

            logger.info(
                f"📧 Alert delivery completed for channel {channel_id}: "
                f"{sent_count} sent, {failed_count} failed, {skipped_count} skipped"
            )

            return failed_count == 0

        except Exception as e:
            logger.error(f"Alert notification failed: {e}", exc_info=True)
            return False

    def _calculate_baseline_stats(self, data: list[float]) -> dict[str, float]:
        """Calculate baseline statistics from historical data"""
        if not data:
            return {"mean": 0, "std": 0, "min": 0, "max": 0, "count": 0}

        np_data = np.array(data)
        return {
            "mean": float(np.mean(np_data)),
            "std": float(np.std(np_data)),
            "min": float(np.min(np_data)),
            "max": float(np.max(np_data)),
            "count": len(data),
        }

    def _calculate_posts_baseline_stats(self, posts: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate baseline statistics for posts"""
        if not posts:
            return {"daily_avg": 0, "views_avg": 0, "engagement_avg": 0}

        views = [post.get("views", 0) for post in posts]
        return {
            "daily_avg": len(posts) / max(30, 1),  # Average posts per day
            "views_avg": np.mean(views) if views else 0,
            "engagement_avg": 0,  # Would calculate from actual engagement data
        }

    def _calculate_engagement_baseline(
        self, views_data: list[float], followers_data: list[float]
    ) -> dict[str, float]:
        """Calculate engagement baseline metrics"""
        if not views_data or not followers_data:
            return {"mean": 0, "std": 0}

        # Simplified engagement calculation
        avg_views = np.mean(views_data) if views_data else 0
        avg_followers = np.mean(followers_data) if followers_data else 1

        engagement_rate = (avg_views / avg_followers * 100) if avg_followers > 0 else 0

        return {
            "mean": float(engagement_rate),
            "std": 0.5,  # Simplified standard deviation
        }

    async def _is_duplicate_alert(
        self, user_id: int, channel_id: int, alert_type: str, hours: int = 1
    ) -> bool:
        """Check if same alert was sent recently to avoid spam"""
        try:
            query = (
                """
                SELECT COUNT(*) as count
                FROM alert_sent
                WHERE user_id = $1
                  AND channel_id = $2
                  AND alert_type = $3
                  AND sent_at > NOW() - INTERVAL '%s hours'
                  AND status = 'sent'
            """
                % hours
            )

            result = await self._posts.db.fetchrow(query, user_id, channel_id, alert_type)
            return result["count"] > 0 if result else False
        except Exception as e:
            logger.warning(f"Error checking duplicate alert: {e}")
            return False  # If check fails, allow sending

    async def _get_user_alert_preferences(self, user_id: int) -> dict[str, Any]:
        """Get user alert preferences or return defaults"""
        try:
            query = """
                SELECT alert_frequency, min_severity, quiet_hours_start,
                       quiet_hours_end, timezone, enabled, telegram_enabled,
                       email_enabled, web_push_enabled
                FROM user_alert_preferences
                WHERE user_id = $1
            """

            result = await self._posts.db.fetchrow(query, user_id)

            if result:
                return dict(result)

            # Return defaults if no preferences found
            return {
                "alert_frequency": "immediate",
                "min_severity": "medium",
                "quiet_hours_start": None,
                "quiet_hours_end": None,
                "timezone": "UTC",
                "enabled": True,
                "telegram_enabled": True,
                "email_enabled": False,
                "web_push_enabled": False,
            }
        except Exception as e:
            logger.warning(f"Error fetching user preferences: {e}")
            # Return safe defaults on error
            return {
                "alert_frequency": "immediate",
                "min_severity": "medium",
                "enabled": True,
                "telegram_enabled": True,
            }

    async def _is_channel_muted(self, user_id: int, channel_id: int) -> bool:
        """Check if channel is muted for this user"""
        try:
            query = """
                SELECT COUNT(*) as count
                FROM muted_channels
                WHERE user_id = $1
                  AND channel_id = $2
                  AND (muted_until IS NULL OR muted_until > NOW())
            """

            result = await self._posts.db.fetchrow(query, user_id, channel_id)
            return result["count"] > 0 if result else False
        except Exception as e:
            logger.warning(f"Error checking muted channel: {e}")
            return False  # If check fails, allow sending

    async def _is_in_quiet_hours(self, preferences: dict[str, Any]) -> bool:
        """Check if current time is in user's quiet hours"""
        try:
            quiet_start = preferences.get("quiet_hours_start")
            quiet_end = preferences.get("quiet_hours_end")

            if quiet_start is None or quiet_end is None:
                return False  # No quiet hours configured

            # Get current hour in user's timezone
            from datetime import datetime

            import pytz

            user_tz = pytz.timezone(preferences.get("timezone", "UTC"))
            current_hour = datetime.now(user_tz).hour

            # Handle quiet hours that span midnight
            if quiet_start <= quiet_end:
                return quiet_start <= current_hour < quiet_end
            else:
                return current_hour >= quiet_start or current_hour < quiet_end

        except Exception as e:
            logger.warning(f"Error checking quiet hours: {e}")
            return False  # If check fails, allow sending

    def _filter_alerts_by_severity(
        self, alerts: list[dict[str, Any]], min_severity: str
    ) -> list[dict[str, Any]]:
        """Filter alerts by minimum severity level (always allows success alerts)"""
        severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3, "success": 999}
        min_level = severity_order.get(min_severity, 1)

        filtered = [
            alert
            for alert in alerts
            if (
                alert.get("severity") == "success"  # Always allow success alerts
                or severity_order.get(alert.get("severity", "medium"), 1) >= min_level
            )
        ]

        return filtered

    async def _record_alert_sent(
        self,
        user_id: int,
        channel_id: int,
        alert_type: str,
        severity: str,
        status: str,
        message_id: int | None = None,
        error_message: str | None = None,
        rule_name: str | None = None,
    ) -> None:
        """Record alert delivery in database for tracking and deduplication"""
        try:
            query = """
                INSERT INTO alert_sent (
                    user_id, channel_id, alert_type, rule_name,
                    severity, status, message_id, error_message
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """

            await self._posts.db.execute(
                query,
                user_id,
                channel_id,
                alert_type,
                rule_name,
                severity,
                status,
                message_id,
                error_message,
            )
        except Exception as e:
            logger.error(f"Failed to record alert: {e}", exc_info=True)
            # Don't raise - recording failure shouldn't break alert delivery

    async def generate_actionable_recommendations(
        self, channel_id: int, alert: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Generate specific, actionable recommendations based on alert type.

        Instead of just saying "engagement is low", suggests:
        - Best times to post (from historical data)
        - Top-performing content types
        - Engagement tactics that worked before
        """
        try:
            alert_type = alert.get("alert_type", "unknown")
            recommendations = []

            # Get channel performance insights
            insights = await self._get_channel_insights(channel_id)

            if alert_type == "QUIET":  # Low engagement
                recommendations.extend(
                    [
                        {
                            "action": "optimize_posting_time",
                            "title": "📅 Post at optimal times",
                            "description": f"Your best engagement is at {insights.get('best_hour', '10:00')}. Try posting then.",
                            "priority": "high",
                            "estimated_impact": "+25% engagement",
                        },
                        {
                            "action": "use_interactive_content",
                            "title": "💬 Add interactive elements",
                            "description": "Posts with polls or questions get 40% more engagement",
                            "priority": "medium",
                            "estimated_impact": "+40% interactions",
                        },
                        {
                            "action": "analyze_top_posts",
                            "title": "🔍 Learn from your best posts",
                            "description": f"Your top post got {insights.get('top_post_views', 'high')} views. Review what made it successful.",
                            "priority": "medium",
                            "link": f"/analytics/posts?channel_id={channel_id}&sort=engagement",
                        },
                    ]
                )

            elif alert_type == "SPIKE":  # Performance issues (low views)
                recommendations.extend(
                    [
                        {
                            "action": "check_content_quality",
                            "title": "✨ Improve content quality",
                            "description": "Add more visual content (images/videos) - they get 2x more views",
                            "priority": "high",
                            "estimated_impact": "+100% views",
                        },
                        {
                            "action": "increase_posting_frequency",
                            "title": "📈 Post more frequently",
                            "description": f"You're posting {insights.get('posts_per_day', 1):.1f} times/day. Try 3-5 posts for better visibility.",
                            "priority": "medium",
                            "estimated_impact": "+50% reach",
                        },
                        {
                            "action": "promote_channel",
                            "title": "📢 Cross-promote your channel",
                            "description": "Share your channel in related communities or with influencers",
                            "priority": "low",
                            "estimated_impact": "+new subscribers",
                        },
                    ]
                )

            elif alert_type == "GROWTH":  # Subscriber growth issues
                recommendations.extend(
                    [
                        {
                            "action": "run_promotion",
                            "title": "🎁 Run a giveaway or contest",
                            "description": "Contests can bring 500-1000 new subscribers in a week",
                            "priority": "high",
                            "estimated_impact": "+500 subscribers",
                        },
                        {
                            "action": "collaborate",
                            "title": "🤝 Collaborate with similar channels",
                            "description": "Partner with channels in your niche for cross-promotion",
                            "priority": "medium",
                            "estimated_impact": "+20% growth rate",
                        },
                        {
                            "action": "optimize_bio",
                            "title": "📝 Update channel description",
                            "description": "Clear, compelling bio increases conversion by 30%",
                            "priority": "low",
                            "estimated_impact": "+30% conversions",
                        },
                    ]
                )

            # Add generic helpful tips
            recommendations.append(
                {
                    "action": "view_analytics",
                    "title": "📊 View detailed analytics",
                    "description": "Get deeper insights into your channel performance",
                    "priority": "low",
                    "link": f"/analytics/advanced?channel_id={channel_id}",
                }
            )

            return recommendations

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []

    async def _get_channel_insights(self, channel_id: int) -> dict[str, Any]:
        """Get quick performance insights for recommendations"""
        try:
            # Get best posting hour
            hour_query = """
                SELECT
                    EXTRACT(HOUR FROM p.date) as hour,
                    AVG(pm.views) as avg_views
                FROM posts p
                JOIN LATERAL (
                    SELECT views
                    FROM post_metrics
                    WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                    ORDER BY snapshot_time DESC
                    LIMIT 1
                ) pm ON true
                WHERE p.channel_id = $1
                  AND p.date > NOW() - INTERVAL '30 days'
                GROUP BY EXTRACT(HOUR FROM p.date)
                ORDER BY avg_views DESC
                LIMIT 1
            """

            hour_result = await self._posts.db.fetchrow(hour_query, channel_id)
            best_hour = int(hour_result["hour"]) if hour_result else 10

            # Get top post views
            top_post_query = """
                SELECT MAX(pm.views) as max_views
                FROM posts p
                JOIN post_metrics pm ON p.channel_id = pm.channel_id AND p.msg_id = pm.msg_id
                WHERE p.channel_id = $1
                  AND p.date > NOW() - INTERVAL '30 days'
            """

            top_post_result = await self._posts.db.fetchrow(top_post_query, channel_id)
            top_post_views = (
                int(top_post_result["max_views"])
                if top_post_result and top_post_result["max_views"]
                else 0
            )

            # Get posting frequency
            freq_query = """
                SELECT COUNT(*)::float / 30 as posts_per_day
                FROM posts
                WHERE channel_id = $1
                  AND date > NOW() - INTERVAL '30 days'
            """

            freq_result = await self._posts.db.fetchrow(freq_query, channel_id)
            posts_per_day = float(freq_result["posts_per_day"]) if freq_result else 1.0

            return {
                "best_hour": f"{best_hour:02d}:00",
                "top_post_views": top_post_views,
                "posts_per_day": posts_per_day,
            }

        except Exception as e:
            logger.warning(f"Failed to get channel insights: {e}")
            return {
                "best_hour": "10:00",
                "top_post_views": 0,
                "posts_per_day": 1.0,
            }

    async def analyze_channel_trends(self, channel_id: int, days: int = 7) -> dict[str, Any]:
        """
        Analyze multi-day trends to detect patterns.

        Detects:
        - Consecutive days of decline
        - Week-over-week changes
        - Predictive warnings (will drop below threshold in X days)
        """
        try:
            logger.info(f"📈 Analyzing {days}-day trends for channel {channel_id}")

            # Get daily metrics for trend analysis
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)

            query = """
                SELECT
                    date,
                    views,
                    subscribers,
                    CASE
                        WHEN views > 0
                        THEN (forwards + reactions)::float / views * 100
                        ELSE 0
                    END as engagement_rate
                FROM channel_daily_analytics
                WHERE channel_id = $1
                  AND date >= $2
                  AND date <= $3
                ORDER BY date ASC
            """

            results = await self._daily.db.fetch(query, channel_id, start_date, end_date)

            if not results or len(results) < 3:
                return {
                    "channel_id": channel_id,
                    "days_analyzed": days,
                    "status": "insufficient_data",
                    "message": "Need at least 3 days of data for trend analysis",
                }

            # Extract time series
            dates = [r["date"] for r in results]
            views_series = [float(r["views"] or 0) for r in results]
            engagement_series = [float(r["engagement_rate"] or 0) for r in results]
            subscriber_series = [float(r["subscribers"] or 0) for r in results]

            # Detect trends
            trends = {
                "views_trend": self._calculate_trend(views_series),
                "engagement_trend": self._calculate_trend(engagement_series),
                "subscriber_trend": self._calculate_trend(subscriber_series),
            }

            # Detect consecutive declines
            consecutive_declines = self._detect_consecutive_declines(views_series)

            # Predict future performance
            predictions = await self._predict_future_performance(
                channel_id, views_series, engagement_series
            )

            # Generate trend alerts
            trend_alerts = []

            if consecutive_declines >= 3:
                trend_alerts.append(
                    {
                        "type": "consecutive_decline",
                        "severity": "high",
                        "message": f"⚠️ Views declining for {consecutive_declines} consecutive days",
                        "days": consecutive_declines,
                    }
                )

            if (
                trends["engagement_trend"]["direction"] == "declining"
                and abs(trends["engagement_trend"]["change_pct"]) > 20
            ):
                trend_alerts.append(
                    {
                        "type": "engagement_decline",
                        "severity": "medium",
                        "message": f"📉 Engagement down {abs(trends['engagement_trend']['change_pct']):.1f}% over {days} days",
                        "change_pct": trends["engagement_trend"]["change_pct"],
                    }
                )

            if (
                trends["views_trend"]["direction"] == "improving"
                and trends["views_trend"]["change_pct"] > 25
            ):
                trend_alerts.append(
                    {
                        "type": "views_growth",
                        "severity": "success",
                        "message": f"🚀 Views up {trends['views_trend']['change_pct']:.1f}% this week!",
                        "change_pct": trends["views_trend"]["change_pct"],
                    }
                )

            return {
                "channel_id": channel_id,
                "days_analyzed": days,
                "date_range": {
                    "start": str(start_date),
                    "end": str(end_date),
                },
                "trends": trends,
                "consecutive_declines": consecutive_declines,
                "predictions": predictions,
                "trend_alerts": trend_alerts,
                "status": "analyzed",
            }

        except Exception as e:
            logger.error(f"Trend analysis failed for channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "days_analyzed": days,
                "status": "failed",
                "error": str(e),
            }

    def _calculate_trend(self, series: list[float]) -> dict[str, Any]:
        """Calculate trend direction and change percentage"""
        if len(series) < 2:
            return {"direction": "unknown", "change_pct": 0, "slope": 0}

        # Simple linear regression slope
        n = len(series)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(series) / n

        numerator = sum((x[i] - x_mean) * (series[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        slope = numerator / denominator if denominator != 0 else 0

        # Calculate percentage change from first to last
        first_val = series[0] if series[0] != 0 else 0.01
        last_val = series[-1]
        change_pct = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0

        # Determine direction
        if slope > 0.1:
            direction = "improving"
        elif slope < -0.1:
            direction = "declining"
        else:
            direction = "stable"

        return {
            "direction": direction,
            "slope": slope,
            "change_pct": change_pct,
            "first_value": series[0],
            "last_value": series[-1],
        }

    def _detect_consecutive_declines(self, series: list[float]) -> int:
        """Count consecutive days of decline"""
        if len(series) < 2:
            return 0

        consecutive = 0
        for i in range(len(series) - 1, 0, -1):
            if series[i] < series[i - 1]:
                consecutive += 1
            else:
                break

        return consecutive

    async def _predict_future_performance(
        self, channel_id: int, views_series: list[float], engagement_series: list[float]
    ) -> dict[str, Any]:
        """Predict if metrics will drop below threshold in next 7 days"""
        try:
            if len(views_series) < 3:
                return {"prediction_available": False}

            # Get dynamic thresholds
            thresholds = await self._get_channel_dynamic_thresholds(channel_id)

            # Calculate trend slope
            views_trend = self._calculate_trend(views_series)
            engagement_trend = self._calculate_trend(engagement_series)

            # Project 7 days forward
            days_to_predict = 7
            predicted_views = views_trend["last_value"] + (views_trend["slope"] * days_to_predict)
            predicted_engagement = engagement_trend["last_value"] + (
                engagement_trend["slope"] * days_to_predict
            )

            predictions = {
                "prediction_available": True,
                "days_predicted": days_to_predict,
                "predicted_views": max(0, predicted_views),
                "predicted_engagement": max(0, predicted_engagement),
                "views_threshold": thresholds.get("views_threshold", 100),
                "engagement_threshold": thresholds.get("engagement_threshold", 1.0),
            }

            # Check if will drop below threshold
            warnings = []

            if predicted_views < thresholds.get("views_threshold", 100):
                days_until = self._calculate_days_until_threshold(
                    views_trend["last_value"],
                    views_trend["slope"],
                    thresholds.get("views_threshold", 100),
                )
                warnings.append(
                    {
                        "type": "views_warning",
                        "message": f"⚠️ Views predicted to drop below threshold in ~{days_until} days",
                        "days_until": days_until,
                        "confidence": 0.75,
                    }
                )

            if predicted_engagement < thresholds.get("engagement_threshold", 1.0):
                days_until = self._calculate_days_until_threshold(
                    engagement_trend["last_value"],
                    engagement_trend["slope"],
                    thresholds.get("engagement_threshold", 1.0),
                )
                warnings.append(
                    {
                        "type": "engagement_warning",
                        "message": f"⚠️ Engagement predicted to drop below threshold in ~{days_until} days",
                        "days_until": days_until,
                        "confidence": 0.75,
                    }
                )

            predictions["warnings"] = warnings
            return predictions

        except Exception as e:
            logger.warning(f"Prediction failed: {e}")
            return {"prediction_available": False, "error": str(e)}

    def _calculate_days_until_threshold(
        self, current_value: float, slope: float, threshold: float
    ) -> int:
        """Calculate how many days until value crosses threshold"""
        if slope >= 0:
            return 999  # Not declining

        days = (threshold - current_value) / slope
        return max(1, int(abs(days)))

    def _summarize_alerts(self, alerts: list[dict[str, Any]]) -> dict[str, Any]:
        """Summarize alerts by type and severity"""
        summary = {"total": len(alerts), "by_severity": {}, "by_type": {}}

        for alert in alerts:
            severity = alert.get("severity", "unknown")
            alert_type = alert.get("type", "unknown")

            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            summary["by_type"][alert_type] = summary["by_type"].get(alert_type, 0) + 1

        return summary

    # === ALERT RULE MANAGEMENT METHODS ===
    # Added for frontend alert rule management integration

    async def get_channel_rules(self, channel_id: str) -> list[dict[str, Any]]:
        """
        Get all alert rules for a channel.

        Returns list of rule dictionaries with:
        - id: Rule ID
        - name: Rule name
        - metric_type: Type of metric monitored
        - condition: Comparison condition
        - threshold: Threshold value
        - severity: Alert severity
        - enabled: Whether rule is active
        """
        try:
            if not self._alert_rule_manager:
                logger.warning(f"Alert rule manager not available for channel {channel_id}")
                return []

            rules = await self._alert_rule_manager.get_channel_rules(channel_id)

            # Transform to frontend-friendly format
            formatted_rules = []
            for rule in rules:
                formatted_rules.append(
                    {
                        "id": rule.get("id"),
                        "name": rule.get("name"),
                        "description": f"{rule.get('metric_type')} {rule.get('condition')} {rule.get('threshold')}",
                        "metric_type": rule.get("metric_type"),
                        "condition": rule.get("condition"),
                        "threshold": rule.get("threshold"),
                        "severity": rule.get("severity", "medium"),
                        "enabled": rule.get("enabled", True),
                    }
                )

            return formatted_rules

        except Exception as e:
            logger.error(f"Failed to get rules for channel {channel_id}: {e}")
            return []

    async def create_alert_rule(
        self,
        channel_id: str,
        rule_name: str,
        metric_type: str,
        threshold_value: float,
        comparison: str,
        enabled: bool = True,
        notification_channels: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new alert rule for a channel.

        Args:
            channel_id: Channel ID
            rule_name: Human-readable rule name
            metric_type: Type of metric (engagement, growth, views, etc.)
            threshold_value: Threshold value for alert
            comparison: Comparison type (above, below, equals)
            enabled: Whether rule is enabled
            notification_channels: List of notification channels

        Returns:
            Created rule dictionary
        """
        try:
            if not self._alert_rule_manager:
                raise Exception("Alert rule manager not available")

            # Map comparison to condition
            condition_map = {
                "above": "greater_than",
                "below": "less_than",
                "equals": "equals",
                "greater_than": "greater_than",
                "less_than": "less_than",
            }
            condition = condition_map.get(comparison, "greater_than")

            # Create rule
            rule_id = await self._alert_rule_manager.create_rule(
                channel_id=channel_id,
                name=rule_name,
                metric_type=metric_type,
                condition=condition,
                threshold=threshold_value,
                severity="medium",
                enabled=enabled,
            )

            logger.info(f"Created alert rule {rule_id} for channel {channel_id}: {rule_name}")

            return {
                "id": rule_id,
                "name": rule_name,
                "description": f"{metric_type} {comparison} {threshold_value}",
                "metric_type": metric_type,
                "condition": condition,
                "threshold": threshold_value,
                "enabled": enabled,
                "created_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to create rule for channel {channel_id}: {e}")
            raise

    async def update_alert_rule(
        self,
        channel_id: str,
        rule_id: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """
        Update an alert rule (toggle enabled/disabled).

        Args:
            channel_id: Channel ID
            rule_id: Rule ID to update
            enabled: New enabled state

        Returns:
            Updated rule dictionary
        """
        try:
            if not self._alert_rule_manager:
                raise Exception("Alert rule manager not available")

            # Update rule
            success = await self._alert_rule_manager.toggle_rule(rule_id, enabled)

            if not success:
                raise Exception(f"Failed to update rule {rule_id}")

            logger.info(f"Updated alert rule {rule_id} for channel {channel_id}: enabled={enabled}")

            return {
                "id": rule_id,
                "enabled": enabled,
                "updated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to update rule {rule_id} for channel {channel_id}: {e}")
            raise

    async def health_check(self) -> dict[str, Any]:
        """Health check for alerts management service"""
        return {
            "service_name": "AlertsManagementService",
            "status": "operational",
            "version": "1.0.0",
            "type": "microservice",
            "responsibility": "alert_management",
            "dependencies": {
                "posts_repository": "connected",
                "daily_repository": "connected",
                "channels_repository": "connected",
                "live_monitoring_service": "connected",
            },
            "capabilities": [
                "intelligent_alert_setup",
                "real_time_alert_checking",
                "baseline_establishment",
                "alert_rule_management",
                "notification_triggering",
            ],
            "configuration": self.alert_config,
        }
