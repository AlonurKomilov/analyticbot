"""
Payment system data models and Pydantic schemas
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
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
    last_four: Optional[str] = None
    brand: Optional[str] = None
    expires_at: Optional[date] = None
    is_default: bool = False
    metadata: Optional[Dict[str, Any]] = None


class PaymentMethodResponse(BaseModel):
    id: str
    user_id: int
    provider: PaymentProvider
    method_type: PaymentMethodType
    last_four: Optional[str]
    brand: Optional[str]
    expires_at: Optional[date]
    is_default: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    plan_id: int
    payment_method_id: Optional[str] = None
    billing_cycle: BillingCycle
    trial_days: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


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
    trial_ends_at: Optional[datetime]
    canceled_at: Optional[datetime]
    cancel_at_period_end: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    amount: Decimal
    currency: str = "USD"
    payment_method_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v


class PaymentResponse(BaseModel):
    id: str
    user_id: int
    amount: Decimal
    currency: str
    status: PaymentStatus
    provider: PaymentProvider
    description: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WebhookEvent(BaseModel):
    provider: PaymentProvider
    event_type: str
    provider_event_id: Optional[str]
    object_id: Optional[str]
    payload: Dict[str, Any]
    signature: Optional[str]


# Internal models for payment processing
class PaymentIntent(BaseModel):
    """Internal payment intent for processing"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: int
    amount: Decimal
    currency: str
    provider: PaymentProvider
    payment_method_id: Optional[str] = None
    subscription_id: Optional[str] = None
    idempotency_key: str = Field(default_factory=lambda: str(uuid4()))
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PaymentResult(BaseModel):
    """Result of payment processing"""
    success: bool
    payment_id: str
    provider_payment_id: Optional[str]
    status: PaymentStatus
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class SubscriptionUpdateRequest(BaseModel):
    """Request to update subscription"""
    plan_id: Optional[int] = None
    payment_method_id: Optional[str] = None
    cancel_at_period_end: Optional[bool] = None


class BillingInfo(BaseModel):
    """Billing information for user dashboard"""
    current_subscription: Optional[SubscriptionResponse]
    payment_methods: list[PaymentMethodResponse]
    recent_payments: list[PaymentResponse]
    next_payment_date: Optional[datetime]
    next_payment_amount: Optional[Decimal]


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
    data: Dict[str, Any]
    created: int


class PaymeWebhookPayload(BaseModel):
    """Payme webhook payload structure"""
    id: str
    time: int
    amount: int
    state: int
    reason: Optional[int] = None
    account: Dict[str, Any]


class ClickWebhookPayload(BaseModel):
    """Click webhook payload structure"""
    click_trans_id: str
    service_id: str
    click_paydoc_id: str
    merchant_trans_id: str
    amount: float
    action: int
    error: int
    error_note: Optional[str] = None
    sign_time: str
    sign_string: str
