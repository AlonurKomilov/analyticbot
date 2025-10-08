"""
Payment Microservices Module
============================

Clean microservices architecture for payment system.
Exports all payment microservices and the orchestrator.
"""

from .analytics.payment_analytics_service import PaymentAnalyticsService
from .gateway.payment_gateway_manager_service import PaymentGatewayManagerService
from .methods.payment_method_service import PaymentMethodService
from .orchestrator.payment_orchestrator_service import PaymentOrchestratorService
from .processing.payment_processing_service import PaymentProcessingService
from .subscriptions.subscription_service import SubscriptionService
from .webhooks.webhook_service import WebhookService

# Import protocols from core (Clean Architecture)
from core.protocols.payment.payment_protocols import (
    PaymentAnalyticsProtocol,
    PaymentEventType,
    PaymentGatewayManagerProtocol,
    PaymentMethodProtocol,
    PaymentMethodResult,
    PaymentOrchestratorProtocol,
    PaymentProcessingProtocol,
    PaymentResult,
    PaymentStats,
    SubscriptionProtocol,
    SubscriptionResult,
    SubscriptionStats,
    WebhookEvent,
    WebhookProtocol,
)

__all__ = [
    # Core Services
    "PaymentMethodService",
    "PaymentProcessingService",
    "SubscriptionService",
    "WebhookService",
    "PaymentAnalyticsService",
    "PaymentGatewayManagerService",
    "PaymentOrchestratorService",
    # Protocols
    "PaymentMethodProtocol",
    "PaymentProcessingProtocol",
    "SubscriptionProtocol",
    "WebhookProtocol",
    "PaymentAnalyticsProtocol",
    "PaymentGatewayManagerProtocol",
    "PaymentOrchestratorProtocol",
    # Data Models
    "PaymentMethodResult",
    "PaymentResult",
    "SubscriptionResult",
    "PaymentStats",
    "SubscriptionStats",
    "WebhookEvent",
    "PaymentEventType",
]
