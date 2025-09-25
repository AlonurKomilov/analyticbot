"""
Payments Domain Event Publishers
================================

Services for publishing domain events from the Payments domain.
"""

import logging

from src.shared_kernel.application.event_bus import (
    get_event_bus,
    PaymentCompletedEvent,
    SubscriptionCreatedEvent
)

logger = logging.getLogger(__name__)


class PaymentsEventPublisher:
    """Publisher for Payments domain events"""
    
    def __init__(self, event_bus=None):
        self.event_bus = event_bus or get_event_bus()
    
    async def publish_payment_completed(
        self, 
        payment_id: str,
        customer_id: str,
        amount: str,
        currency: str
    ) -> None:
        """Publish payment completed event"""
        event = PaymentCompletedEvent(
            payment_id=payment_id,
            customer_id=customer_id,
            amount=amount,
            currency=currency
        )
        
        await self.event_bus.publish(event)
        logger.info(f"Published payment completed event: {payment_id}")
    
    async def publish_subscription_created(
        self,
        subscription_id: str,
        customer_id: str,
        plan_name: str
    ) -> None:
        """Publish subscription created event"""
        event = SubscriptionCreatedEvent(
            subscription_id=subscription_id,
            customer_id=customer_id,
            plan_name=plan_name
        )
        
        await self.event_bus.publish(event)
        logger.info(f"Published subscription created event: {subscription_id}")