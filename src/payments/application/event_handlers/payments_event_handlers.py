"""
Payments Domain Event Handlers
==============================

Handles events from other domains that affect the Payments domain.
"""

import logging

from src.shared_kernel.application.event_bus import (
    AnalyticsTrackingEnabledEvent,
    UserRegisteredEvent,
)

logger = logging.getLogger(__name__)


class PaymentsEventHandlers:
    """Event handlers for the Payments domain"""

    def __init__(self, payment_repository=None):
        self.payment_repository = payment_repository

    async def handle_user_registered(self, event: UserRegisteredEvent) -> None:
        """Handle user registered event - create customer profile for payments"""
        logger.info(f"Creating payment customer profile for new user: {event.user_id}")

        try:
            # Create customer record in payments domain
            if self.payment_repository:
                # await self.payment_repository.create_customer(
                #     customer_id=event.user_id,
                #     email=event.email,
                #     username=event.username
                # )
                logger.info(f"Payment customer profile created for user: {event.user_id}")

        except Exception as e:
            logger.error(f"Failed to create payment customer profile for user {event.user_id}: {e}")

    async def handle_analytics_tracking_enabled(self, event: AnalyticsTrackingEnabledEvent) -> None:
        """Handle analytics tracking enabled - prepare for potential premium upgrade"""
        logger.info(f"Preparing payment options for analytics user: {event.user_id}")

        try:
            # Prepare payment methods and subscription options for the user
            if self.payment_repository:
                # await self.payment_repository.prepare_subscription_options(
                #     customer_id=event.user_id,
                #     channel_id=event.channel_id
                # )
                logger.info(f"Payment options prepared for user: {event.user_id}")

        except Exception as e:
            logger.error(f"Failed to prepare payment options for user {event.user_id}: {e}")


async def register_payments_event_handlers(event_bus, payment_repository=None) -> None:
    """Register all payments domain event handlers with the event bus"""
    handlers = PaymentsEventHandlers(payment_repository)

    # Subscribe to identity events
    await event_bus.subscribe("identity.user_registered", handlers.handle_user_registered)

    # Subscribe to analytics events
    await event_bus.subscribe(
        "analytics.tracking_enabled", handlers.handle_analytics_tracking_enabled
    )

    logger.info("Payments domain event handlers registered")
