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
from typing import Any, Optional


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
    last_four: Optional[str] = None
    brand: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_default: bool = False
    metadata: Optional[dict[str, Any]] = None
    provider_data: Optional[dict[str, Any]] = None


@dataclass
class PaymentData:
    """Payment creation data"""
    payment_method_id: str
    amount: Money
    description: Optional[str] = None
    subscription_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


@dataclass
class SubscriptionData:
    """Subscription creation data"""
    plan_id: str
    payment_method_id: str
    billing_cycle: BillingCycle
    trial_days: Optional[int] = None
    metadata: Optional[dict[str, Any]] = None


# Domain Entities
@dataclass
class PaymentMethod:
    """Payment method domain entity"""
    id: str
    user_id: int
    provider: PaymentProvider
    method_type: PaymentMethodType
    last_four: Optional[str]
    brand: Optional[str]
    expires_at: Optional[datetime]
    is_default: bool
    is_active: bool
    created_at: datetime
    metadata: Optional[dict[str, Any]] = None


@dataclass
class Payment:
    """Payment domain entity"""
    id: str
    user_id: int
    payment_method_id: str
    amount: Money
    status: PaymentStatus
    provider: PaymentProvider
    provider_payment_id: Optional[str]
    description: Optional[str]
    subscription_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    metadata: Optional[dict[str, Any]] = None


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
    trial_ends_at: Optional[datetime]
    created_at: datetime
    canceled_at: Optional[datetime] = None
    cancel_at_period_end: bool = False
    metadata: Optional[dict[str, Any]] = None
