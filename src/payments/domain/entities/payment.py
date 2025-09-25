from datetime import datetime
from typing import Dict, Any, Optional, List
from decimal import Decimal

from ..value_objects.payments_value_objects import (
    PaymentId, PaymentAmount, PaymentStatus, PaymentProvider, PaymentMethodId,
    CustomerId, PaymentStatusType, ProviderPaymentId, Money
)


class Payment:
    """
    Payment Aggregate Root
    
    Manages the complete lifecycle of a payment transaction.
    Enforces business rules around payment processing, state transitions, and validation.
    """
    
    def __init__(
        self,
        payment_id: PaymentId,
        customer_id: CustomerId,
        amount: PaymentAmount,
        provider: PaymentProvider,
        payment_method_id: Optional[PaymentMethodId] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        # Basic attributes
        self.id = payment_id.value
        self._payment_id = payment_id
        self._customer_id = customer_id
        self._amount = amount
        self._provider = provider
        self._payment_method_id = payment_method_id
        self._description = description or ""
        self._metadata = metadata or {}
        
        # Initialize state
        self._status = PaymentStatus(PaymentStatusType.PENDING)
        self._provider_payment_id: Optional[ProviderPaymentId] = None
        self._processed_at: Optional[datetime] = None
        self._failed_at: Optional[datetime] = None
        self._error_code: Optional[str] = None
        self._error_message: Optional[str] = None
        
        # Refund tracking
        self._is_refunded = False
        self._refunded_amount_value = Decimal(0)  # Track as decimal, not PaymentAmount
        self._refund_reason: Optional[str] = None
        self._refunded_at: Optional[datetime] = None
        
        # Risk assessment
        self._risk_score = 0.0
        self._is_flagged = False
        self._risk_factors: List[str] = []
        
        # Timestamps
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        
        # Domain events
        self._domain_events: List[Any] = []
        
        # Add initial domain event
        self.add_domain_event({
            'type': 'PaymentInitiated',
            'payment_id': payment_id.value,
            'customer_id': customer_id.value,
            'amount': {
                'value': str(amount.money.amount),
                'currency': amount.money.currency
            },
            'timestamp': datetime.utcnow()
        })
    
    # Properties
    @property
    def payment_id(self) -> PaymentId:
        return self._payment_id
    
    @property
    def customer_id(self) -> CustomerId:
        return self._customer_id
    
    @property
    def amount(self) -> PaymentAmount:
        return self._amount
    
    @property
    def status(self) -> PaymentStatus:
        return self._status
    
    @property
    def provider(self) -> PaymentProvider:
        return self._provider
    
    @property
    def refunded_amount(self) -> PaymentAmount:
        if self._refunded_amount_value > 0:
            return PaymentAmount(Money(self._refunded_amount_value, self._amount.money.currency))
        # Return a minimal amount to satisfy PaymentAmount requirements
        return PaymentAmount(Money(Decimal("0.01"), self._amount.money.currency))
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def add_domain_event(self, event: Any) -> None:
        """Add a domain event to the aggregate"""
        self._domain_events.append(event)
    
    def mark_as_updated(self) -> None:
        """Update the timestamp"""
        self._updated_at = datetime.utcnow()
    
    def can_be_processed(self) -> bool:
        """Check if payment can be processed"""
        return (
            self._status.value == PaymentStatusType.PENDING and
            not self._is_flagged
        )
    
    def __str__(self) -> str:
        return f"Payment(id={self._payment_id.value}, amount={self._amount}, status={self._status.value})"
