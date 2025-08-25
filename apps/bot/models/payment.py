"""
Payment system data models and Pydantic schemas
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, validator


# Enums for payment system
class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"


class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class PaymentProvider(str, Enum):
    STRIPE = "stripe"
    PAYME = "payme"
    CLICK = "click"
    PAYPAL = "paypal"


class PaymentMethodType(str, Enum):
    CARD = "card"
    BANK_ACCOUNT = "bank_account"
    DIGITAL_WALLET = "digital_wallet"


# Pydantic Models for API requests/responses
class PaymentMethodCreate(BaseModel):
    provider: PaymentProvider
    provider_method_id: str
    method_type: PaymentMethodType
    last_four: str | None = None
    brand: str | None = None
    expires_at: date | None = None
    is_default: bool = False
    metadata: dict[str, Any] | None = None


class PaymentMethodResponse(BaseModel):
    id: str
    user_id: int
    provider: PaymentProvider
    method_type: PaymentMethodType
    last_four: str | None
    brand: str | None
    expires_at: date | None
    is_default: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    plan_id: int
    payment_method_id: str | None = None
    billing_cycle: BillingCycle
    trial_days: int | None = None
    metadata: dict[str, Any] | None = None


class SubscriptionResponse(BaseModel):
    id: str
    user_id: int
    plan_id: int
    status: SubscriptionStatus
    billing_cycle: BillingCycle
    amount: Decimal
    currency: str
    current_period_start: datetime
    current_period_end: datetime
    trial_ends_at: datetime | None
    canceled_at: datetime | None
    cancel_at_period_end: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    amount: Decimal
    currency: str = "USD"
    payment_method_id: str | None = None
    description: str | None = None
    metadata: dict[str, Any] | None = None

    @validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class PaymentResponse(BaseModel):
    id: str
    user_id: int
    amount: Decimal
    currency: str
    status: PaymentStatus
    provider: PaymentProvider
    description: str | None
    created_at: datetime
    processed_at: datetime | None

    class Config:
        from_attributes = True


class WebhookEvent(BaseModel):
    provider: PaymentProvider
    event_type: str
    provider_event_id: str | None
    object_id: str | None
    payload: dict[str, Any]
    signature: str | None


# Internal models for payment processing
class PaymentIntent(BaseModel):
    """Internal payment intent for processing"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: int
    amount: Decimal
    currency: str
    provider: PaymentProvider
    payment_method_id: str | None = None
    subscription_id: str | None = None
    idempotency_key: str = Field(default_factory=lambda: str(uuid4()))
    description: str | None = None
    metadata: dict[str, Any] | None = None


class PaymentResult(BaseModel):
    """Result of payment processing"""

    success: bool
    payment_id: str
    provider_payment_id: str | None
    status: PaymentStatus
    error_message: str | None = None
    error_code: str | None = None


class SubscriptionUpdateRequest(BaseModel):
    """Request to update subscription"""

    plan_id: int | None = None
    payment_method_id: str | None = None
    cancel_at_period_end: bool | None = None


class BillingInfo(BaseModel):
    """Billing information for user dashboard"""

    current_subscription: SubscriptionResponse | None
    payment_methods: list[PaymentMethodResponse]
    recent_payments: list[PaymentResponse]
    next_payment_date: datetime | None
    next_payment_amount: Decimal | None


# Enhanced plan model with pricing
class PlanWithPricing(BaseModel):
    id: int
    name: str
    max_channels: int
    max_posts_per_month: int
    price_monthly: Decimal
    price_yearly: Decimal
    currency: str
    is_active: bool

    class Config:
        from_attributes = True


# Webhook payload models for different providers
class StripeWebhookPayload(BaseModel):
    """Stripe webhook payload structure"""

    id: str
    object: str
    type: str
    data: dict[str, Any]
    created: int


class PaymeWebhookPayload(BaseModel):
    """Payme webhook payload structure"""

    id: str
    time: int
    amount: int
    state: int
    reason: int | None = None
    account: dict[str, Any]


class ClickWebhookPayload(BaseModel):
    """Click webhook payload structure"""

    click_trans_id: str
    service_id: str
    click_paydoc_id: str
    merchant_trans_id: str
    amount: float
    action: int
    error: int
    error_note: str | None = None
    sign_time: str
    sign_string: str
