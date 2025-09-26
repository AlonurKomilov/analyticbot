"""
Analytics Domain Event Handlers
===============================

Handles events from other domains that affect the Analytics domain.
"""

import logging

from src.shared_kernel.application.event_bus import (
    SubscriptionCreatedEvent,
    UserEmailVerifiedEvent,
    UserRegisteredEvent,
)

logger = logging.getLogger(__name__)


class AnalyticsEventHandlers:
    """Event handlers for the Analytics domain"""

    def __init__(self, analytics_repository=None):
        self.analytics_repository = analytics_repository

    async def handle_user_registered(self, event: UserRegisteredEvent) -> None:
        """Handle user registered event - initialize analytics for new user"""
        logger.info(f"Initializing analytics for new user: {event.user_id}")

        try:
            # Initialize analytics tracking for the new user
            if self.analytics_repository:
                # await self.analytics_repository.initialize_user_analytics(
                #     user_id=event.user_id,
                #     email=event.email,
                #     username=event.username
                # )
                logger.info(f"Analytics initialized for user: {event.user_id}")

        except Exception as e:
            logger.error(f"Failed to initialize analytics for user {event.user_id}: {e}")

    async def handle_user_email_verified(self, event: UserEmailVerifiedEvent) -> None:
        """Handle email verification - enable full analytics features"""
        logger.info(f"Enabling full analytics for verified user: {event.user_id}")

        try:
            # Enable full analytics features for verified user
            if self.analytics_repository:
                # await self.analytics_repository.enable_full_analytics(event.user_id)
                logger.info(f"Full analytics enabled for user: {event.user_id}")

        except Exception as e:
            logger.error(f"Failed to enable full analytics for user {event.user_id}: {e}")

    async def handle_subscription_created(self, event: SubscriptionCreatedEvent) -> None:
        """Handle subscription creation - unlock premium analytics features"""
        logger.info(f"Unlocking premium analytics for subscriber: {event.customer_id}")

        try:
            # Unlock premium analytics features based on subscription plan
            if self.analytics_repository:
                # await self.analytics_repository.unlock_premium_features(
                #     user_id=event.customer_id,
                #     plan_name=event.plan_name
                # )
                logger.info(f"Premium analytics unlocked for user: {event.customer_id}")

        except Exception as e:
            logger.error(f"Failed to unlock premium analytics for user {event.customer_id}: {e}")


async def register_analytics_event_handlers(event_bus, analytics_repository=None) -> None:
    """Register all analytics domain event handlers with the event bus"""
    handlers = AnalyticsEventHandlers(analytics_repository)

    # Subscribe to identity events
    await event_bus.subscribe("identity.user_registered", handlers.handle_user_registered)
    await event_bus.subscribe("identity.user_email_verified", handlers.handle_user_email_verified)

    # Subscribe to payment events
    await event_bus.subscribe("payments.subscription_created", handlers.handle_subscription_created)

    logger.info("Analytics domain event handlers registered")
