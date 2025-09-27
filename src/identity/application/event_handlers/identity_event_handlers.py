"""
Identity Domain Event Handlers
==============================

Handles events from other domains that affect the Identity domain.
"""

import logging

from src.shared_kernel.application.event_bus import (
    PaymentCompletedEvent,
    SubscriptionCreatedEvent,
)

logger = logging.getLogger(__name__)


class IdentityEventHandlers:
    """Event handlers for the Identity domain"""

    def __init__(self, user_repository=None):
        self.user_repository = user_repository

    async def handle_payment_completed(self, event: PaymentCompletedEvent) -> None:
        """Handle payment completed event - update user's payment history"""
        logger.info(f"Processing payment completed for customer: {event.customer_id}")

        try:
            # Update user's payment status, subscription level, etc.
            # This would typically update the user's subscription status
            if self.user_repository:
                # user = await self.user_repository.get_by_id(event.customer_id)
                # user.add_payment_record(event.payment_id, event.amount, event.currency)
                # await self.user_repository.save(user)
                logger.info(f"Updated user payment history for: {event.customer_id}")

        except Exception as e:
            logger.error(f"Failed to handle payment completed event: {e}")

    async def handle_subscription_created(self, event: SubscriptionCreatedEvent) -> None:
        """Handle subscription created event - upgrade user's access level"""
        logger.info(f"Processing subscription created for customer: {event.customer_id}")

        try:
            # Update user's subscription level and permissions
            if self.user_repository:
                # user = await self.user_repository.get_by_id(event.customer_id)
                # user.upgrade_to_plan(event.plan_name)
                # await self.user_repository.save(user)
                logger.info(f"Upgraded user subscription to {event.plan_name}: {event.customer_id}")

        except Exception as e:
            logger.error(f"Failed to handle subscription created event: {e}")


async def register_identity_event_handlers(event_bus, user_repository=None) -> None:
    """Register all identity domain event handlers with the event bus"""
    handlers = IdentityEventHandlers(user_repository)

    # Subscribe to payment events
    await event_bus.subscribe("payments.payment_completed", handlers.handle_payment_completed)
    await event_bus.subscribe("payments.subscription_created", handlers.handle_subscription_created)

    logger.info("Identity domain event handlers registered")
