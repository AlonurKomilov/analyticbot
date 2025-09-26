"""
Identity Domain Event Publishers
================================

Services for publishing domain events from the Identity domain.
"""

import logging

from src.shared_kernel.application.event_bus import (
    UserEmailVerifiedEvent,
    UserRegisteredEvent,
    get_event_bus,
)

logger = logging.getLogger(__name__)


class IdentityEventPublisher:
    """Publisher for Identity domain events"""

    def __init__(self, event_bus=None):
        self.event_bus = event_bus or get_event_bus()

    async def publish_user_registered(self, user_id: str, email: str, username: str = None) -> None:
        """Publish user registered event"""
        event = UserRegisteredEvent(user_id=user_id, email=email, username=username)

        await self.event_bus.publish(event)
        logger.info(f"Published user registered event for: {user_id}")

    async def publish_user_email_verified(self, user_id: str, email: str) -> None:
        """Publish user email verified event"""
        event = UserEmailVerifiedEvent(user_id=user_id, email=email)

        await self.event_bus.publish(event)
        logger.info(f"Published user email verified event for: {user_id}")
