"""
Scheduling Service Providers

Factory functions for scheduling services.
Includes schedule manager, post delivery, and delivery status tracking.
"""

import logging

logger = logging.getLogger(__name__)


def create_schedule_manager(schedule_repository=None, analytics_repository=None, **kwargs):
    """Create schedule manager (core scheduling logic)"""
    try:
        from core.services.bot.scheduling import ScheduleManager

        if schedule_repository is None:
            logger.warning("Cannot create schedule manager: missing schedule repository")
            return None

        return ScheduleManager(schedule_repository=schedule_repository)
    except ImportError as e:
        logger.warning(f"Schedule manager not available: {e}")
        return None


def create_post_delivery_service(
    message_sender=None,
    markup_builder=None,
    schedule_repository=None,
    analytics_repository=None,
    **kwargs,
):
    """Create post delivery service (orchestrates message delivery)"""
    try:
        from typing import cast

        from core.services.bot.scheduling import PostDeliveryService
        from core.services.bot.scheduling.protocols import (
            AnalyticsRepository,
            MarkupBuilderPort,
            MessageSenderPort,
            ScheduleRepository,
        )

        if not all([message_sender, markup_builder, schedule_repository, analytics_repository]):
            logger.warning("Cannot create post delivery service: missing dependencies")
            return None

        # Type cast to satisfy type checker (DI ensures correct types at runtime)
        return PostDeliveryService(
            message_sender=cast(MessageSenderPort, message_sender),
            markup_builder=cast(MarkupBuilderPort, markup_builder),
            schedule_repo=cast(ScheduleRepository, schedule_repository),
            analytics_repo=cast(AnalyticsRepository, analytics_repository),
        )
    except ImportError as e:
        logger.warning(f"Post delivery service not available: {e}")
        return None


def create_delivery_status_tracker(schedule_repository=None, analytics_repository=None, **kwargs):
    """Create delivery status tracker (manages post lifecycle)"""
    try:
        from core.services.bot.scheduling import DeliveryStatusTracker

        if schedule_repository is None or analytics_repository is None:
            logger.warning("Cannot create delivery status tracker: missing repositories")
            return None

        return DeliveryStatusTracker(
            schedule_repo=schedule_repository,
            analytics_repo=analytics_repository,
        )
    except ImportError as e:
        logger.warning(f"Delivery status tracker not available: {e}")
        return None
