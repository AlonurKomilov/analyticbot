from datetime import datetime
from typing import Dict, Any, Optional, List

from ..value_objects.payments_value_objects import (
    SubscriptionId, CustomerId, PaymentMethodId, SubscriptionStatus, BillingCycle, Money
)


class Subscription:
    """
    Subscription Aggregate Root
    
    Manages recurring payment subscriptions for customers.
    Enforces business rules around billing cycles, trials, and lifecycle management.
    """
    
    def __init__(
        self,
        subscription_id: SubscriptionId,
        customer_id: CustomerId,
        payment_method_id: PaymentMethodId,
        plan_id: str,
        billing_cycle: BillingCycle,
        amount: Money,
        trial_days: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = subscription_id.value
        self._subscription_id = subscription_id
        self._customer_id = customer_id
        self._payment_method_id = payment_method_id
        self._plan_id = plan_id
        self._billing_cycle = billing_cycle
        self._amount = amount
        self._trial_days = trial_days
        self._metadata = metadata or {}
        
        # Status
        self._status = SubscriptionStatus.ACTIVE
        
        # Billing
        self._next_billing_date: Optional[datetime] = None
        self._trial_ends_at: Optional[datetime] = None
        
        # Timestamps
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        
        # Domain events
        self._domain_events: List[Any] = []
    
    @property
    def subscription_id(self) -> SubscriptionId:
        return self._subscription_id
    
    @property
    def customer_id(self) -> CustomerId:
        return self._customer_id
    
    @property
    def status(self) -> SubscriptionStatus:
        return self._status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def mark_as_updated(self) -> None:
        """Update the timestamp"""
        self._updated_at = datetime.utcnow()
    
    def __str__(self) -> str:
        return f"Subscription(id={self._subscription_id.value}, status={self._status})"