"""
Alert Runner Module
Main orchestration for alert detection and notification lifecycle
"""

import asyncio
from datetime import datetime
from typing import Any

from apps.jobs.alerts.runner.base import (
    ALERT_TYPE_GROWTH,
    ALERT_TYPE_QUIET,
    ALERT_TYPE_SPIKE,
    MAX_CONCURRENT_ALERTS,
    logger,
)
from apps.jobs.alerts.runner.detector import AlertDetector
from apps.jobs.alerts.runner.notifier import AlertNotifier
from apps.shared.analytics_service import SharedAnalyticsService
from core.repositories.alert_repository import AlertSent


class AlertRunner:
    """Main alert detection and notification runner"""

    def __init__(
        self,
        analytics_client=None,
        alert_repository=None,
        alert_sent_repository=None,
        telegram_delivery_service=None,
    ):
        self.analytics_client = analytics_client
        self.alert_repository = alert_repository
        self.alert_sent_repository = alert_sent_repository
        self.detector: AlertDetector | None = None
        self.notifier: AlertNotifier | None = None
        self.running = False

    async def _ensure_dependencies(self):
        """Ensure dependencies are available using DI container"""
        if (
            self.analytics_client is None
            or self.alert_repository is None
            or self.alert_sent_repository is None
        ):
            from apps.di import get_container

            # Get settings
            try:
                from config.settings import settings

                analytics_api_url = settings.ANALYTICS_V2_BASE_URL
            except ImportError:
                analytics_api_url = "http://localhost:8000"  # fallback

            # Create analytics client
            if self.analytics_client is None:
                self.analytics_client = SharedAnalyticsService(analytics_api_url)

            # Get repositories from DI container
            container = get_container()

            if self.alert_repository is None:
                self.alert_repository = await container.database.alert_subscription_repo()

            if self.alert_sent_repository is None:
                self.alert_sent_repository = await container.database.alert_sent_repo()

        # Create detector if not exists
        if self.detector is None:
            self.detector = AlertDetector(self.analytics_client, self.alert_repository)

        # Create notifier if not exists
        if self.notifier is None:
            self.notifier = AlertNotifier()
            telegram_delivery = await self.notifier.create_telegram_delivery_service()
            self.notifier.telegram_delivery = telegram_delivery

    async def process_alert(self, alert_config: dict[str, Any]) -> None:
        """Process a single alert configuration"""
        # Ensure dependencies are available
        await self._ensure_dependencies()

        # Type guard - after _ensure_dependencies, these should not be None
        assert self.detector is not None
        assert self.notifier is not None
        assert self.alert_repository is not None
        assert self.alert_sent_repository is not None

        alert_type = alert_config["alert_type"]
        user_id = alert_config["user_id"]
        channel_id = alert_config["channel_id"]

        logger.debug(f"Processing {alert_type} alert for {channel_id} (user {user_id})")

        try:
            # Detect alert based on type
            alert_result = None

            if alert_type == ALERT_TYPE_SPIKE:
                alert_result = await self.detector.detect_spike_alert(alert_config)
            elif alert_type == ALERT_TYPE_QUIET:
                alert_result = await self.detector.detect_quiet_alert(alert_config)
            elif alert_type == ALERT_TYPE_GROWTH:
                alert_result = await self.detector.detect_growth_alert(alert_config)
            else:
                logger.warning(f"Unknown alert type: {alert_type}")
                return

            if alert_result:
                # Generate unique key for this alert instance
                alert_key = self.notifier.generate_alert_key(alert_result)

                # Check if alert was already sent (deduplication)
                already_sent = await self.alert_sent_repository.is_alert_sent(
                    chat_id=user_id,
                    channel_id=channel_id,
                    kind=alert_type,
                    key=alert_key,
                )

                if already_sent:
                    logger.debug(
                        f"Alert already sent for {alert_type} on channel {channel_id}, skipping"
                    )
                    return

                # Send alert notification via Telegram
                delivery_result = await self.notifier.send_alert_notification(user_id, alert_result)

                # Mark alert as sent if delivery was successful
                if delivery_result.get("status") == "sent":
                    alert_sent = AlertSent(
                        chat_id=user_id,
                        channel_id=channel_id,
                        kind=alert_type,
                        key=alert_key,
                        sent_at=datetime.utcnow(),
                    )

                    await self.alert_sent_repository.mark_alert_sent(alert_sent)

                    logger.info(
                        f"Alert sent successfully for {alert_type} on channel {channel_id} "
                        f"(message_id: {delivery_result.get('message_id')})"
                    )
                else:
                    logger.error(
                        f"Failed to send alert for {alert_type} on channel {channel_id}: "
                        f"{delivery_result.get('error')}"
                    )
            else:
                logger.debug(f"No {alert_type} alert triggered for channel {channel_id}")

        except Exception as e:
            logger.error(f"Error processing alert {alert_config}: {e}")

    async def run_detection_cycle(self) -> None:
        """Run one cycle of alert detection"""
        # Ensure dependencies are available
        await self._ensure_dependencies()

        # Type guard - after _ensure_dependencies, these should not be None
        assert self.alert_repository is not None

        # Check if alerts are enabled (use a simple fallback)
        alerts_enabled = True  # Default to enabled
        try:
            from config.settings import settings

            alerts_enabled = getattr(settings, "ALERTS_ENABLED", True)
        except ImportError:
            pass

        if not alerts_enabled:
            logger.debug("Alerts are disabled, skipping detection cycle")
            return

        try:
            # Get all active alert subscriptions
            active_alerts = await self.alert_repository.get_active_subscriptions()

            if not active_alerts:
                logger.debug("No active alerts to process")
                return

            logger.info(f"Processing {len(active_alerts)} active alerts")

            # Process alerts concurrently (with limit to avoid overwhelming)
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_ALERTS)

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
