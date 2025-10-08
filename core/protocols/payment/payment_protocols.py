"""
Payment System Protocols
========================

Clean interfaces for payment microservices architecture.
Defines contracts for payment methods, processing, subscriptions, webhooks, and analytics.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from core.domain.payment import (
    BillingCycle,
    Money,
    Payment,
    PaymentData,
    PaymentMethod,
    PaymentMethodData,
    PaymentProvider,
    PaymentStatus,
    Subscription,
    SubscriptionData,
    SubscriptionStatus,
)


class PaymentEventType(Enum):
    """Payment event types for webhooks"""

    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_CANCELED = "payment_canceled"
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_UPDATED = "subscription_updated"
    SUBSCRIPTION_CANCELED = "subscription_canceled"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    PAYMENT_METHOD_ATTACHED = "payment_method_attached"
    PAYMENT_METHOD_DETACHED = "payment_method_detached"


@dataclass
class PaymentMethodResult:
    """Result of payment method operations"""

    success: bool
    payment_method: PaymentMethod | None = None
    error_message: str | None = None
    provider_response: dict[str, Any] | None = None


@dataclass
class PaymentResult:
    """Result of payment processing operations"""

    success: bool
    payment: Payment | None = None
    error_message: str | None = None
    provider_response: dict[str, Any] | None = None
    transaction_id: str | None = None


@dataclass
class SubscriptionResult:
    """Result of subscription operations"""

    success: bool
    subscription: Subscription | None = None
    error_message: str | None = None
    provider_response: dict[str, Any] | None = None


@dataclass
class WebhookEvent:
    """Webhook event data structure"""

    event_id: str
    provider: str
    event_type: PaymentEventType
    object_id: str
    payload: dict[str, Any]
    signature: str
    processed_at: datetime | None = None
    processing_result: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PaymentStats:
    """Payment statistics data structure"""

    total_payments: int
    successful_payments: int
    failed_payments: int
    total_revenue: Decimal
    failed_amount: Decimal
    average_payment_amount: Decimal
    payment_count_by_provider: dict[str, int]
    revenue_by_provider: dict[str, Decimal]
    daily_stats: list[dict[str, Any]]


@dataclass
class SubscriptionStats:
    """Subscription statistics data structure"""

    total_subscriptions: int
    active_subscriptions: int
    canceled_subscriptions: int
    past_due_subscriptions: int
    trial_subscriptions: int
    average_subscription_amount: Decimal
    churn_rate: float
    monthly_recurring_revenue: Decimal
    yearly_recurring_revenue: Decimal


class PaymentMethodProtocol(ABC):
    """
    Protocol for payment method management operations.

    Handles CRUD operations for user payment methods across different providers.
    """

    @abstractmethod
    async def create_payment_method(
        self, user_id: int, payment_method_data: PaymentMethodData, provider: str | None = None
    ) -> PaymentMethodResult:
        """Create a new payment method for a user"""
        pass

    @abstractmethod
    async def get_user_payment_methods(self, user_id: int) -> list[PaymentMethod]:
        """Retrieve all payment methods for a user"""
        pass

    @abstractmethod
    async def get_payment_method(self, method_id: str) -> PaymentMethod | None:
        """Get a specific payment method by ID"""
        pass

    @abstractmethod
    async def update_payment_method(
        self, method_id: str, updates: dict[str, Any]
    ) -> PaymentMethodResult:
        """Update payment method details"""
        pass

    @abstractmethod
    async def delete_payment_method(self, method_id: str, user_id: int) -> bool:
        """Delete a payment method"""
        pass

    @abstractmethod
    async def set_default_payment_method(self, method_id: str, user_id: int) -> bool:
        """Set a payment method as default for a user"""
        pass


class PaymentProcessingProtocol(ABC):
    """
    Protocol for payment processing operations.

    Handles payment execution, validation, and transaction management.
    """

    @abstractmethod
    async def process_payment(
        self, user_id: int, payment_data: PaymentData, idempotency_key: str | None = None
    ) -> PaymentResult:
        """Process a one-time payment"""
        pass

    @abstractmethod
    async def validate_payment_data(self, payment_data: PaymentData) -> dict[str, Any]:
        """Validate payment data before processing"""
        pass

    @abstractmethod
    async def retry_failed_payment(self, payment_id: str) -> PaymentResult:
        """Retry a failed payment"""
        pass

    @abstractmethod
    async def refund_payment(
        self, payment_id: str, amount: Decimal | None = None, reason: str | None = None
    ) -> PaymentResult:
        """Refund a payment (full or partial)"""
        pass

    @abstractmethod
    async def get_payment(self, payment_id: str) -> Payment | None:
        """Get payment details by ID"""
        pass

    @abstractmethod
    async def get_payment_history(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> dict[str, Any]:
        """Get user's payment history"""
        pass


class SubscriptionProtocol(ABC):
    """
    Protocol for subscription management operations.

    Handles subscription lifecycle including creation, updates, cancellation, and renewals.
    """

    @abstractmethod
    async def create_subscription(
        self, user_id: int, subscription_data: SubscriptionData
    ) -> SubscriptionResult:
        """Create a new subscription"""
        pass

    @abstractmethod
    async def get_user_subscription(self, user_id: int) -> Subscription | None:
        """Get user's active subscription"""
        pass

    @abstractmethod
    async def update_subscription(
        self, subscription_id: str, updates: dict[str, Any]
    ) -> SubscriptionResult:
        """Update subscription details"""
        pass

    @abstractmethod
    async def cancel_subscription(
        self, user_id: int, immediate: bool = False, reason: str | None = None
    ) -> dict[str, Any]:
        """Cancel a user's subscription"""
        pass

    @abstractmethod
    async def pause_subscription(
        self, subscription_id: str, duration_days: int
    ) -> SubscriptionResult:
        """Pause a subscription for a specific duration"""
        pass

    @abstractmethod
    async def resume_subscription(self, subscription_id: str) -> SubscriptionResult:
        """Resume a paused subscription"""
        pass

    @abstractmethod
    async def change_subscription_plan(
        self, subscription_id: str, new_plan_id: str
    ) -> SubscriptionResult:
        """Change subscription plan"""
        pass

    @abstractmethod
    async def get_available_plans(self) -> list[dict[str, Any]]:
        """Get all available subscription plans"""
        pass


class WebhookProtocol(ABC):
    """
    Protocol for webhook processing operations.

    Handles webhook verification, processing, and event management.
    """

    @abstractmethod
    async def process_webhook(
        self, provider: str, payload: bytes, signature: str
    ) -> dict[str, Any]:
        """Process incoming webhook from payment provider"""
        pass

    @abstractmethod
    async def verify_webhook_signature(self, provider: str, payload: bytes, signature: str) -> bool:
        """Verify webhook signature authenticity"""
        pass

    @abstractmethod
    async def handle_payment_event(self, event: WebhookEvent) -> dict[str, Any]:
        """Handle payment-related webhook events"""
        pass

    @abstractmethod
    async def handle_subscription_event(self, event: WebhookEvent) -> dict[str, Any]:
        """Handle subscription-related webhook events"""
        pass

    @abstractmethod
    async def get_webhook_events(
        self, provider: str | None = None, limit: int = 100
    ) -> list[WebhookEvent]:
        """Get webhook event history"""
        pass

    @abstractmethod
    async def retry_webhook_processing(self, event_id: str) -> dict[str, Any]:
        """Retry processing of a failed webhook event"""
        pass


class PaymentAnalyticsProtocol(ABC):
    """
    Protocol for payment analytics and reporting operations.

    Handles statistics, reports, and business intelligence for payments and subscriptions.
    """

    @abstractmethod
    async def get_payment_stats(
        self, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> PaymentStats:
        """Get comprehensive payment statistics"""
        pass

    @abstractmethod
    async def get_subscription_stats(
        self, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> SubscriptionStats:
        """Get comprehensive subscription statistics"""
        pass

    @abstractmethod
    async def get_revenue_analytics(
        self,
        period: str = "monthly",  # "daily", "weekly", "monthly", "yearly"
    ) -> dict[str, Any]:
        """Get revenue analytics for a specific period"""
        pass

    @abstractmethod
    async def get_churn_analysis(self) -> dict[str, Any]:
        """Get subscription churn analysis"""
        pass

    @abstractmethod
    async def get_payment_failure_analysis(self) -> dict[str, Any]:
        """Analyze payment failures and reasons"""
        pass

    @abstractmethod
    async def get_provider_performance(self) -> dict[str, Any]:
        """Compare performance across payment providers"""
        pass


class PaymentGatewayManagerProtocol(ABC):
    """
    Protocol for payment gateway adapter management.

    Handles switching between payment providers and managing gateway configurations.
    """

    @abstractmethod
    async def get_current_gateway(self) -> str:
        """Get currently active payment gateway"""
        pass

    @abstractmethod
    async def switch_gateway(self, gateway_name: str) -> bool:
        """Switch to a different payment gateway"""
        pass

    @abstractmethod
    async def get_supported_gateways(self) -> list[str]:
        """Get list of supported payment gateways"""
        pass

    @abstractmethod
    async def test_gateway_connection(self, gateway_name: str) -> dict[str, Any]:
        """Test connection to a payment gateway"""
        pass

    @abstractmethod
    async def get_gateway_health(self) -> dict[str, Any]:
        """Get health status of all configured gateways"""
        pass


class PaymentOrchestratorProtocol(ABC):
    """
    Protocol for payment orchestration service.

    Coordinates between all payment microservices and provides unified interface.
    """

    @abstractmethod
    async def execute_payment_workflow(
        self,
        user_id: int,
        payment_data: PaymentData,
        workflow_options: dict[str, Any] | None = None,
    ) -> PaymentResult:
        """Execute complete payment workflow"""
        pass

    @abstractmethod
    async def execute_subscription_workflow(
        self,
        user_id: int,
        subscription_data: SubscriptionData,
        workflow_options: dict[str, Any] | None = None,
    ) -> SubscriptionResult:
        """Execute complete subscription creation workflow"""
        pass

    @abstractmethod
    async def handle_payment_failure_workflow(
        self, payment_id: str, failure_reason: str
    ) -> dict[str, Any]:
        """Handle payment failure recovery workflow"""
        pass

    @abstractmethod
    async def get_payment_system_health(self) -> dict[str, Any]:
        """Get comprehensive health status of payment system"""
        pass
