from datetime import datetime
from typing import Any

from ..value_objects.payments_value_objects import (
    CardDetails,
    CustomerId,
    PaymentMethodId,
    PaymentMethodStatus,
    PaymentProvider,
)


class PaymentMethod:
    """
    PaymentMethod Aggregate Root

    Manages customer payment methods (cards, wallets, bank accounts).
    Enforces business rules around payment method registration and security.
    """

    def __init__(
        self,
        payment_method_id: PaymentMethodId,
        customer_id: CustomerId,
        provider: PaymentProvider,
        method_type: str,
        card_details: CardDetails | None = None,
        is_default: bool = False,
        metadata: dict[str, Any] | None = None,
    ):
        self.id = payment_method_id.value
        self._payment_method_id = payment_method_id
        self._customer_id = customer_id
        self._provider = provider
        self._method_type = method_type
        self._card_details = card_details
        self._is_default = is_default
        self._metadata = metadata or {}

        # Status
        self._status = PaymentMethodStatus.ACTIVE
        self._is_verified = False

        # Timestamps
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        self._last_used_at: datetime | None = None

        # Domain events
        self._domain_events: list[Any] = []

    @property
    def payment_method_id(self) -> PaymentMethodId:
        return self._payment_method_id

    @property
    def customer_id(self) -> CustomerId:
        return self._customer_id

    @property
    def is_default(self) -> bool:
        return self._is_default

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
        return f"PaymentMethod(id={self._payment_method_id.value}, type={self._method_type})"
