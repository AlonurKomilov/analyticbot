"""
Payments Domain Events

Domain events that capture important business moments in the payments domain.
These events enable loose coupling between payment operations and other business concerns.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.shared_kernel.domain.domain_events import DomainEvent

from .value_objects import (
    BillingCycle,
    CustomerId,
    Money,
    PaymentAmount,
    PaymentId,
    PaymentMethodId,
    PaymentProvider,
    SubscriptionId,
)

# ========== PAYMENT EVENTS ==========


class PaymentInitiated(DomainEvent):
    """Event: Payment has been initiated"""

    def __init__(
        self,
        payment_id: PaymentId,
        customer_id: CustomerId,
        amount: PaymentAmount,
        provider: PaymentProvider,
        payment_method_id: PaymentMethodId | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        super().__init__()
        self.payment_id = payment_id
        self.customer_id = customer_id
        self.amount = amount
        self.provider = provider
        self.payment_method_id = payment_method_id
        self.description = description
        self.metadata = metadata


class PaymentProcessing(DomainEvent):
    """Event: Payment is being processed by provider"""

    def __init__(
        self,
        payment_id: PaymentId,
        provider: PaymentProvider,
        provider_payment_id: str | None = None,
    ):
        super().__init__()
        self.payment_id = payment_id
        self.provider = provider
        self.provider_payment_id = provider_payment_id


class PaymentSucceeded(DomainEvent):
    """Event: Payment completed successfully"""

    def __init__(
        self,
        payment_id: PaymentId,
        customer_id: CustomerId,
        amount: PaymentAmount,
        provider: PaymentProvider,
        provider_payment_id: str,
        processed_at: datetime,
    ):
        super().__init__()
        self.payment_id = payment_id
        self.customer_id = customer_id
        self.amount = amount
        self.provider = provider
        self.provider_payment_id = provider_payment_id
        self.processed_at = processed_at


class PaymentFailed(DomainEvent):
    """Event: Payment failed"""

    def __init__(
        self,
        payment_id: PaymentId,
        customer_id: CustomerId,
        amount: PaymentAmount,
        provider: PaymentProvider,
        failure_reason: str,
        failure_code: str | None = None,
        provider_payment_id: str | None = None,
    ):
        super().__init__()
        self.payment_id = payment_id
        self.customer_id = customer_id
        self.amount = amount
        self.provider = provider
        self.failure_reason = failure_reason
        self.failure_code = failure_code
        self.provider_payment_id = provider_payment_id


class PaymentRefunded(DomainEvent):
    """Event: Payment was refunded"""

    def __init__(
        self,
        payment_id: PaymentId,
        customer_id: CustomerId,
        original_amount: PaymentAmount,
        refund_amount: PaymentAmount,
        refund_reason: str | None = None,
        provider_refund_id: str | None = None,
    ):
        super().__init__()
        self.payment_id = payment_id
        self.customer_id = customer_id
        self.original_amount = original_amount
        self.refund_amount = refund_amount
        self.refund_reason = refund_reason
        self.provider_refund_id = provider_refund_id


class PaymentCanceled(DomainEvent):
    """Event: Payment was canceled before processing"""

    def __init__(
        self,
        payment_id: PaymentId,
        customer_id: CustomerId,
        amount: PaymentAmount,
        cancellation_reason: str | None = None,
    ):
        super().__init__()
        self.payment_id = payment_id
        self.customer_id = customer_id
        self.amount = amount
        self.cancellation_reason = cancellation_reason


# ========== PAYMENT METHOD EVENTS ==========


class PaymentMethodAdded(DomainEvent):
    """Event: New payment method added for customer"""

    def __init__(
        self,
        payment_method_id: PaymentMethodId,
        customer_id: CustomerId,
        provider: PaymentProvider,
        method_type: str,
        is_default: bool = False,
    ):
        super().__init__()
        self.payment_method_id = payment_method_id
        self.customer_id = customer_id
        self.provider = provider
        self.method_type = method_type
        self.is_default = is_default


class PaymentMethodUpdated(DomainEvent):
    """Event: Payment method was updated"""

    def __init__(
        self,
        payment_method_id: PaymentMethodId,
        customer_id: CustomerId,
        provider: PaymentProvider,
        changes: dict[str, Any],
    ):
        super().__init__()
        self.payment_method_id = payment_method_id
        self.customer_id = customer_id
        self.provider = provider
        self.changes = changes


class PaymentMethodRemoved(DomainEvent):
    """Event: Payment method was removed"""

    def __init__(
        self,
        payment_method_id: PaymentMethodId,
        customer_id: CustomerId,
        provider: PaymentProvider,
        removal_reason: str | None = None,
    ):
        super().__init__()
        self.payment_method_id = payment_method_id
        self.customer_id = customer_id
        self.provider = provider
        self.removal_reason = removal_reason


class PaymentMethodExpired(DomainEvent):
    """Event: Payment method has expired"""

    def __init__(
        self,
        payment_method_id: PaymentMethodId,
        customer_id: CustomerId,
        provider: PaymentProvider,
        expired_at: datetime,
    ):
        super().__init__()
        self.payment_method_id = payment_method_id
        self.customer_id = customer_id
        self.provider = provider
        self.expired_at = expired_at


class PaymentMethodSetAsDefault(DomainEvent):
    """Event: Payment method was set as default"""

    def __init__(
        self,
        payment_method_id: PaymentMethodId,
        customer_id: CustomerId,
        previous_default_id: PaymentMethodId | None = None,
    ):
        super().__init__()
        self.payment_method_id = payment_method_id
        self.customer_id = customer_id
        self.previous_default_id = previous_default_id


# ========== SUBSCRIPTION EVENTS ==========


class SubscriptionCreated(DomainEvent):
    """Event: New subscription created"""

    def __init__(
        self,
        subscription_id: SubscriptionId,
        customer_id: CustomerId,
        plan_id: str,
        billing_cycle: BillingCycle,
        amount: PaymentAmount,
        trial_ends_at: datetime | None = None,
        payment_method_id: PaymentMethodId | None = None,
    ):
        super().__init__()
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.plan_id = plan_id
        self.billing_cycle = billing_cycle
        self.amount = amount
        self.trial_ends_at = trial_ends_at
        self.payment_method_id = payment_method_id


class SubscriptionActivated(DomainEvent):
    """Event: Subscription became active"""

    def __init__(
        self,
        subscription_id: SubscriptionId,
        customer_id: CustomerId,
        activated_at: datetime,
        current_period_start: datetime,
        current_period_end: datetime,
    ):
        super().__init__()
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.activated_at = activated_at
        self.current_period_start = current_period_start
        self.current_period_end = current_period_end


class SubscriptionTrialStarted(DomainEvent):
    """Event: Subscription trial period started"""

    def __init__(
        self,
        subscription_id: SubscriptionId,
        customer_id: CustomerId,
        trial_start_date: datetime,
        trial_end_date: datetime,
        plan_id: str,
    ):
        super().__init__()
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.trial_start_date = trial_start_date
        self.trial_end_date = trial_end_date
        self.plan_id = plan_id


class SubscriptionTrialEnded(DomainEvent):
    """Event: Subscription trial period ended"""

    def __init__(
        self,
        subscription_id: SubscriptionId,
        customer_id: CustomerId,
        trial_end_date: datetime,
        converted_to_paid: bool,
    ):
        super().__init__()
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.trial_end_date = trial_end_date
        self.converted_to_paid = converted_to_paid


class SubscriptionRenewed(DomainEvent):
    """Event: Subscription was renewed for next billing cycle"""

    def __init__(
        self,
        subscription_id: SubscriptionId,
        customer_id: CustomerId,
        payment_id: PaymentId,
        new_period_start: datetime,
        new_period_end: datetime,
        amount: PaymentAmount,
    ):
        super().__init__()
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.payment_id = payment_id
        self.new_period_start = new_period_start
        self.new_period_end = new_period_end
        self.amount = amount


class SubscriptionPaymentFailed(DomainEvent):
    """Event: Subscription renewal payment failed"""

    def __init__(
        self,
        subscription_id: SubscriptionId,
        customer_id: CustomerId,
        payment_id: PaymentId,
        amount: PaymentAmount,
        failure_reason: str,
        retry_attempt: int,
        next_retry_at: datetime | None = None,
    ):
        super().__init__()
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.payment_id = payment_id
        self.amount = amount
        self.failure_reason = failure_reason
        self.retry_attempt = retry_attempt
        self.next_retry_at = next_retry_at


class SubscriptionPastDue(DomainEvent):
    """Event: Subscription is past due"""

    def __init__(
        self,
        subscription_id: SubscriptionId,
        customer_id: CustomerId,
        amount_due: PaymentAmount,
        due_date: datetime,
        days_overdue: int,
    ):
        super().__init__()
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.amount_due = amount_due
        self.due_date = due_date
        self.days_overdue = days_overdue


class SubscriptionCanceled(DomainEvent):
    """Event: Subscription was canceled"""

    def __init__(
        self,
        subscription_id: SubscriptionId,
        customer_id: CustomerId,
        canceled_at: datetime,
        effective_date: datetime,
        cancel_at_period_end: bool = True,
        cancellation_reason: str | None = None,
    ):
        super().__init__()
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.cancellation_reason = cancellation_reason
        self.canceled_at = canceled_at
        self.effective_date = effective_date
        self.cancel_at_period_end = cancel_at_period_end


class SubscriptionSuspended(DomainEvent):
    """Event: Subscription was suspended"""

    def __init__(
        self,
        subscription_id: SubscriptionId,
        customer_id: CustomerId,
        suspension_reason: str,
        suspended_at: datetime,
        auto_resume_at: datetime | None = None,
    ):
        super().__init__()
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.suspension_reason = suspension_reason
        self.suspended_at = suspended_at
        self.auto_resume_at = auto_resume_at


class SubscriptionResumed(DomainEvent):
    """Event: Suspended subscription was resumed"""

    def __init__(
        self,
        subscription_id: SubscriptionId,
        customer_id: CustomerId,
        resumed_at: datetime,
        new_period_start: datetime,
        new_period_end: datetime,
    ):
        super().__init__()
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.resumed_at = resumed_at
        self.new_period_start = new_period_start
        self.new_period_end = new_period_end


class SubscriptionPlanChanged(DomainEvent):
    """Event: Subscription plan was upgraded or downgraded"""

    def __init__(
        self,
        subscription_id: SubscriptionId,
        customer_id: CustomerId,
        old_plan_id: str,
        new_plan_id: str,
        old_amount: PaymentAmount,
        new_amount: PaymentAmount,
        change_type: str,  # upgrade, downgrade, change
        effective_date: datetime,
        proration_amount: Money | None = None,
    ):
        super().__init__()
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.old_plan_id = old_plan_id
        self.new_plan_id = new_plan_id
        self.old_amount = old_amount
        self.new_amount = new_amount
        self.change_type = change_type
        self.effective_date = effective_date
        self.proration_amount = proration_amount


# ========== FRAUD AND SECURITY EVENTS ==========


class SuspiciousPaymentDetected(DomainEvent):
    """Event: Potentially fraudulent payment detected"""

    def __init__(
        self,
        payment_id: PaymentId,
        customer_id: CustomerId,
        risk_score: int,
        risk_factors: dict[str, Any],
        requires_manual_review: bool,
    ):
        super().__init__()
        self.payment_id = payment_id
        self.customer_id = customer_id
        self.risk_score = risk_score
        self.risk_factors = risk_factors
        self.requires_manual_review = requires_manual_review


class PaymentMethodVerificationRequired(DomainEvent):
    """Event: Payment method requires verification"""

    def __init__(
        self,
        payment_method_id: PaymentMethodId,
        customer_id: CustomerId,
        verification_type: str,  # 3ds, sms, email
        verification_url: str | None = None,
    ):
        super().__init__()
        self.payment_method_id = payment_method_id
        self.customer_id = customer_id
        self.verification_type = verification_type
        self.verification_url = verification_url
