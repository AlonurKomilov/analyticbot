"""
Alert Detection Module
Detects spike, quiet, and growth alerts based on analytics data
"""

from typing import Any

import aiohttp

from apps.jobs.alerts.runner.base import (
    ALERT_TYPE_GROWTH,
    ALERT_TYPE_QUIET,
    ALERT_TYPE_SPIKE,
    DEFAULT_BASELINE_DAYS,
    DEFAULT_PERIOD_HOURS,
    logger,
)
from apps.shared.analytics_service import SharedAnalyticsService
from core.repositories.alert_repository import AlertSubscriptionRepository


class AlertDetector:
    """Service for detecting analytics alerts"""

    def __init__(
        self,
        analytics_client: SharedAnalyticsService,
        alert_repository: AlertSubscriptionRepository,
    ):
        self.analytics_client = analytics_client
        self.alert_repository = alert_repository

    async def detect_spike_alert(self, alert_config: dict[str, Any]) -> dict[str, Any] | None:
        """Detect spike alerts (unusual high activity)"""
        channel_id = alert_config["channel_id"]
        threshold = alert_config["threshold"]
        alert_config.get("period", DEFAULT_PERIOD_HOURS)

        try:
            # Get overview data for the last period
            async with aiohttp.ClientSession() as session:
                # The analytics client expects context manager usage
                async with self.analytics_client:
                    current_data = await self.analytics_client.get_channel_overview(
                        str(channel_id), 1
                    )  # Last 24h
                    baseline_data = await self.analytics_client.get_channel_overview(
                        str(channel_id), DEFAULT_BASELINE_DAYS
                    )  # Last week

            if not current_data or not baseline_data:
                logger.warning(f"Insufficient data for spike detection on channel {channel_id}")
                return None

            # Calculate current and baseline metrics
            # Handle dict response from API
            current_views = (
                current_data.get("overview", {}).get("total_views", 0)
                if isinstance(current_data, dict)
                else getattr(getattr(current_data, "overview", None), "total_views", 0)
            )
            baseline_views_total = (
                baseline_data.get("overview", {}).get("total_views", 0)
                if isinstance(baseline_data, dict)
                else getattr(getattr(baseline_data, "overview", None), "total_views", 0)
            )
            baseline_avg_views = baseline_views_total / DEFAULT_BASELINE_DAYS  # Daily average

            # Calculate percentage increase
            if baseline_avg_views > 0:
                increase_percent = ((current_views - baseline_avg_views) / baseline_avg_views) * 100
            else:
                increase_percent = 0

            # Check if spike detected
            if increase_percent >= threshold:
                return {
                    "type": ALERT_TYPE_SPIKE,
                    "channel_id": channel_id,
                    "metric": "views",
                    "current_value": current_views,
                    "baseline_value": baseline_avg_views,
                    "increase_percent": increase_percent,
                    "threshold": threshold,
                    "message": f"🚀 **Spike Alert!**\\n\\n"
                    f"Channel: {channel_id}\\n"
                    f"Views increased by {increase_percent:.1f}% "
                    f"(from {baseline_avg_views:.0f} to {current_views:.0f})\\n"
                    f"Threshold: {threshold}%",
                }

            return None

        except Exception as e:
            logger.error(f"Error detecting spike alert for {channel_id}: {e}")
            return None

    async def detect_quiet_alert(self, alert_config: dict[str, Any]) -> dict[str, Any] | None:
        """Detect quiet alerts (unusual low activity)"""
        channel_id = alert_config["channel_id"]
        threshold = alert_config["threshold"]
        alert_config.get("period", DEFAULT_PERIOD_HOURS)

        try:
            async with aiohttp.ClientSession() as session:
                # The analytics client expects context manager usage
                async with self.analytics_client:
                    current_data = await self.analytics_client.get_channel_overview(
                        str(channel_id), 1
                    )
                    baseline_data = await self.analytics_client.get_channel_overview(
                        str(channel_id), DEFAULT_BASELINE_DAYS
                    )

            if not current_data or not baseline_data:
                logger.warning(f"Insufficient data for quiet detection on channel {channel_id}")
                return None

            current_views = (
                current_data.get("overview", {}).get("total_views", 0)
                if isinstance(current_data, dict)
                else getattr(getattr(current_data, "overview", None), "total_views", 0)
            )
            baseline_views_total = (
                baseline_data.get("overview", {}).get("total_views", 0)
                if isinstance(baseline_data, dict)
                else getattr(getattr(baseline_data, "overview", None), "total_views", 0)
            )
            baseline_avg_views = baseline_views_total / DEFAULT_BASELINE_DAYS

            # Calculate percentage decrease
            if baseline_avg_views > 0:
                decrease_percent = ((baseline_avg_views - current_views) / baseline_avg_views) * 100
            else:
                decrease_percent = 0

            # Check if quiet period detected
            if decrease_percent >= threshold:
                return {
                    "type": ALERT_TYPE_QUIET,
                    "channel_id": channel_id,
                    "metric": "views",
                    "current_value": current_views,
                    "baseline_value": baseline_avg_views,
                    "decrease_percent": decrease_percent,
                    "threshold": threshold,
                    "message": f"😴 **Quiet Alert!**\\n\\n"
                    f"Channel: {channel_id}\\n"
                    f"Views decreased by {decrease_percent:.1f}% "
                    f"(from {baseline_avg_views:.0f} to {current_views:.0f})\\n"
                    f"Threshold: {threshold}%",
                }

            return None

        except Exception as e:
            logger.error(f"Error detecting quiet alert for {channel_id}: {e}")
            return None

    async def detect_growth_alert(self, alert_config: dict[str, Any]) -> dict[str, Any] | None:
        """Detect growth alerts (subscriber growth milestones)"""
        channel_id = alert_config["channel_id"]
        threshold = alert_config["threshold"]  # subscriber count milestone

        try:
            async with aiohttp.ClientSession() as session:
                # The analytics client expects context manager usage
                async with self.analytics_client:
                    growth_data = await self.analytics_client.get_channel_growth(str(channel_id), 1)

            if not growth_data:
                logger.warning(f"No growth data for channel {channel_id}")
                return None

            # Normalize growth response to expected shape
            daily_growth = (
                growth_data.get("growth", {}).get("daily_growth")
                if isinstance(growth_data, dict)
                else getattr(getattr(growth_data, "growth", None), "daily_growth", None)
            )

            if not daily_growth:
                logger.warning(f"No growth data for channel {channel_id}")
                return None

            # Get latest subscriber count
            latest_day = daily_growth[-1]
            # daily_growth items may be dicts or objects depending on API
            current_subscribers = (
                latest_day.get("subscribers", 0)
                if isinstance(latest_day, dict)
                else getattr(latest_day, "subscribers", 0)
            )

            # Check if milestone reached
            # We need to track previous milestones to avoid duplicate alerts
            # For now, check if current count >= threshold
            if current_subscribers >= threshold:
                return {
                    "type": ALERT_TYPE_GROWTH,
                    "channel_id": channel_id,
                    "metric": "subscribers",
                    "current_value": current_subscribers,
                    "threshold": threshold,
                    "message": f"📈 **Growth Milestone!**\\n\\n"
                    f"Channel: {channel_id}\\n"
                    f"Reached {current_subscribers:,} subscribers!\\n"
                    f"Target: {threshold:,} subscribers",
                }

            return None

        except Exception as e:
            logger.error(f"Error detecting growth alert for {channel_id}: {e}")
            return None
