"""
Alert Detection Job Runner
Background job for detecting analytics alerts and sending notifications
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

import aiohttp
from core.repositories.alert_repository import AlertRepository
from infra.db.repositories.alert_repository import AsyncPgAlertRepository
from src.bot_service.clients.analytics_client import AnalyticsClient

from config.settings import Settings

logger = logging.getLogger(__name__)


class AlertDetector:
    """Service for detecting analytics alerts"""

    def __init__(self, analytics_client: AnalyticsClient, alert_repository: AlertRepository):
        self.analytics_client = analytics_client
        self.alert_repository = alert_repository

    async def detect_spike_alert(self, alert_config: dict[str, Any]) -> dict[str, Any] | None:
        """Detect spike alerts (unusual high activity)"""
        channel_id = alert_config["channel_id"]
        threshold = alert_config["threshold"]
        period = alert_config.get("period", 24)  # hours

        try:
            # Get overview data for the last period
            async with aiohttp.ClientSession() as session:
                self.analytics_client.session = session
                current_data = await self.analytics_client.get_overview(channel_id, 1)  # Last 24h
                baseline_data = await self.analytics_client.get_overview(channel_id, 7)  # Last week

            if not current_data or not baseline_data:
                logger.warning(f"Insufficient data for spike detection on channel {channel_id}")
                return None

            # Calculate current and baseline metrics
            current_views = current_data.overview.views
            baseline_avg_views = baseline_data.overview.views / 7  # Daily average

            # Calculate percentage increase
            if baseline_avg_views > 0:
                increase_percent = ((current_views - baseline_avg_views) / baseline_avg_views) * 100
            else:
                increase_percent = 0

            # Check if spike detected
            if increase_percent >= threshold:
                return {
                    "type": "spike",
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
        period = alert_config.get("period", 24)  # hours

        try:
            async with aiohttp.ClientSession() as session:
                self.analytics_client.session = session
                current_data = await self.analytics_client.get_overview(channel_id, 1)
                baseline_data = await self.analytics_client.get_overview(channel_id, 7)

            if not current_data or not baseline_data:
                logger.warning(f"Insufficient data for quiet detection on channel {channel_id}")
                return None

            current_views = current_data.overview.views
            baseline_avg_views = baseline_data.overview.views / 7

            # Calculate percentage decrease
            if baseline_avg_views > 0:
                decrease_percent = ((baseline_avg_views - current_views) / baseline_avg_views) * 100
            else:
                decrease_percent = 0

            # Check if quiet period detected
            if decrease_percent >= threshold:
                return {
                    "type": "quiet",
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
                self.analytics_client.session = session
                growth_data = await self.analytics_client.get_growth(channel_id, 1)

            if not growth_data or not growth_data.growth.daily_growth:
                logger.warning(f"No growth data for channel {channel_id}")
                return None

            # Get latest subscriber count
            latest_day = growth_data.growth.daily_growth[-1]
            current_subscribers = latest_day.get("subscribers", 0)

            # Check if milestone reached
            # We need to track previous milestones to avoid duplicate alerts
            # For now, check if current count >= threshold
            if current_subscribers >= threshold:
                return {
                    "type": "growth",
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


class AlertRunner:
    """Main alert detection and notification runner"""

    def __init__(self):
        self.settings = Settings()
        self.analytics_client = AnalyticsClient(self.settings.ANALYTICS_API_URL)
        self.alert_repository = AsyncPgAlertRepository()
        self.detector = AlertDetector(self.analytics_client, self.alert_repository)
        self.running = False

    async def process_alert(self, alert_config: dict[str, Any]) -> None:
        """Process a single alert configuration"""
        alert_type = alert_config["alert_type"]
        user_id = alert_config["user_id"]
        channel_id = alert_config["channel_id"]

        logger.debug(f"Processing {alert_type} alert for {channel_id} (user {user_id})")

        try:
            # Detect alert based on type
            alert_result = None

            if alert_type == "spike":
                alert_result = await self.detector.detect_spike_alert(alert_config)
            elif alert_type == "quiet":
                alert_result = await self.detector.detect_quiet_alert(alert_config)
            elif alert_type == "growth":
                alert_result = await self.detector.detect_growth_alert(alert_config)
            else:
                logger.warning(f"Unknown alert type: {alert_type}")
                return

            if alert_result:
                # Check if we've already sent this alert recently
                recent_alert = await self.alert_repository.check_recent_alert(
                    user_id, channel_id, alert_type, hours=24
                )

                if not recent_alert:
                    # Send alert notification
                    await self.send_alert_notification(user_id, alert_result)

                    # Record alert as sent
                    await self.alert_repository.record_alert_sent(
                        user_id, channel_id, alert_type, alert_result
                    )

                    logger.info(
                        f"Sent {alert_type} alert to user {user_id} for channel {channel_id}"
                    )
                else:
                    logger.debug(f"Recent {alert_type} alert already sent for {channel_id}")

        except Exception as e:
            logger.error(f"Error processing alert {alert_config}: {e}")

    async def send_alert_notification(self, user_id: int, alert_data: dict[str, Any]) -> None:
        """Send alert notification to user"""
        # In a real implementation, this would send a message via the bot
        # For now, we'll log the alert
        message = alert_data.get("message", "Alert triggered!")

        logger.info(f"ALERT for user {user_id}: {message}")

        # TODO: Integrate with bot to actually send Telegram messages
        # This would require access to the bot instance or a message queue
        # Example implementation:
        # await bot.send_message(
        #     chat_id=user_id,
        #     text=message,
        #     parse_mode="Markdown"
        # )

    async def run_detection_cycle(self) -> None:
        """Run one cycle of alert detection"""
        if not self.settings.ALERTS_ENABLED:
            logger.debug("Alerts are disabled, skipping detection cycle")
            return

        try:
            # Get all active alert subscriptions
            active_alerts = await self.alert_repository.get_active_alerts()

            if not active_alerts:
                logger.debug("No active alerts to process")
                return

            logger.info(f"Processing {len(active_alerts)} active alerts")

            # Process alerts concurrently (with limit to avoid overwhelming)
            semaphore = asyncio.Semaphore(10)  # Max 10 concurrent alert checks

            async def process_with_semaphore(alert_config):
                async with semaphore:
                    await self.process_alert(alert_config)

            # Execute alert processing
            tasks = [process_with_semaphore(alert) for alert in active_alerts]
            await asyncio.gather(*tasks, return_exceptions=True)

            logger.info(f"Completed alert detection cycle for {len(active_alerts)} alerts")

        except Exception as e:
            logger.error(f"Error in alert detection cycle: {e}")

    async def start(self, interval_seconds: int = 300) -> None:
        """Start the alert runner with specified interval"""
        if self.running:
            logger.warning("Alert runner is already running")
            return

        self.running = True
        logger.info(f"Starting alert runner with {interval_seconds}s interval")

        try:
            while self.running:
                start_time = datetime.utcnow()

                await self.run_detection_cycle()

                # Calculate sleep time
                cycle_duration = (datetime.utcnow() - start_time).total_seconds()
                sleep_time = max(0, interval_seconds - cycle_duration)

                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    logger.warning(
                        f"Alert cycle took {cycle_duration:.1f}s, longer than interval {interval_seconds}s"
                    )

        except asyncio.CancelledError:
            logger.info("Alert runner cancelled")
        except Exception as e:
            logger.error(f"Alert runner error: {e}")
        finally:
            self.running = False
            logger.info("Alert runner stopped")

    def stop(self) -> None:
        """Stop the alert runner"""
        self.running = False


async def main():
    """Main entry point for running alerts job"""
    import argparse

    parser = argparse.ArgumentParser(description="Analytics Alert Detection Runner")
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Detection interval in seconds (default: 300)",
    )
    parser.add_argument("--once", action="store_true", help="Run detection once and exit")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    runner = AlertRunner()

    try:
        if args.once:
            logger.info("Running alert detection once")
            await runner.run_detection_cycle()
        else:
            logger.info(f"Starting continuous alert detection with {args.interval}s interval")
            await runner.start(args.interval)
    except KeyboardInterrupt:
        logger.info("Shutting down alert runner")
        runner.stop()
    except Exception as e:
        logger.error(f"Alert runner failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
