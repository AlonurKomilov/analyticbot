"""
Payment Domain Models
====================

Core domain models for payment system.
These are pure domain entities without framework dependencies.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any


# Domain Enums
class PaymentStatus(str, Enum):
    """Payment status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration"""

    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    PAUSED = "paused"  # Added for completeness


class PaymentProvider(str, Enum):
    """Payment provider enumeration"""

    STRIPE = "stripe"
    PAYME = "payme"
    CLICK = "click"
    MOCK = "mock"


class BillingCycle(str, Enum):
    """Billing cycle enumeration"""

    MONTHLY = "monthly"
    YEARLY = "yearly"


class PaymentMethodType(str, Enum):
    """Payment method type enumeration"""

    CARD = "card"
    BANK_ACCOUNT = "bank_account"
    DIGITAL_WALLET = "digital_wallet"


# Domain Value Objects
@dataclass(frozen=True)
class Money:
    """Money value object"""

    amount: Decimal
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")


@dataclass
class PaymentMethodData:
    """Payment method creation data"""

    method_type: PaymentMethodType
    provider: PaymentProvider
    last_four: str | None = None
    brand: str | None = None
    expires_at: datetime | None = None
    is_default: bool = False
    metadata: dict[str, Any] | None = None
    provider_data: dict[str, Any] | None = None


@dataclass
class PaymentData:
    """Payment creation data"""

    payment_method_id: str
    amount: Money
    description: str | None = None
    subscription_id: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class SubscriptionData:
    """Subscription creation data"""

    plan_id: str
    payment_method_id: str
    billing_cycle: BillingCycle
    trial_days: int | None = None
    metadata: dict[str, Any] | None = None


# Domain Entities
@dataclass
class PaymentMethod:
    """Payment method domain entity"""

    id: str
    user_id: int
    provider: PaymentProvider
    method_type: PaymentMethodType
    last_four: str | None
    brand: str | None
    expires_at: datetime | None
    is_default: bool
    is_active: bool
    created_at: datetime
    metadata: dict[str, Any] | None = None


@dataclass
class Payment:
    """Payment domain entity"""

    id: str
    user_id: int
    payment_method_id: str
    amount: Money
    status: PaymentStatus
    provider: PaymentProvider
    provider_payment_id: str | None
    description: str | None
    subscription_id: str | None
    created_at: datetime
    updated_at: datetime | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class Subscription:
    """Subscription domain entity"""

    id: str
    user_id: int
    plan_id: str
    payment_method_id: str
    status: SubscriptionStatus
    billing_cycle: BillingCycle
    amount: Money
    current_period_start: datetime
    current_period_end: datetime
    trial_ends_at: datetime | None
    created_at: datetime
    canceled_at: datetime | None = None
    cancel_at_period_end: bool = False
    metadata: dict[str, Any] | None = None
