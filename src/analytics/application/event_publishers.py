"""
Analytics Domain Event Publishers
=================================

Services for publishing domain events from the Analytics domain.
"""

import logging

from src.shared_kernel.application.event_bus import (
    AnalyticsTrackingEnabledEvent,
    get_event_bus,
)

logger = logging.getLogger(__name__)


class AnalyticsEventPublisher:
    """Publisher for Analytics domain events"""

    def __init__(self, event_bus=None):
        self.event_bus = event_bus or get_event_bus()

    async def publish_tracking_enabled(self, user_id: str, channel_id: str = None) -> None:
        """Publish analytics tracking enabled event"""
        event = AnalyticsTrackingEnabledEvent(user_id=user_id, channel_id=channel_id)

        await self.event_bus.publish(event)
        logger.info(f"Published analytics tracking enabled event for: {user_id}")
