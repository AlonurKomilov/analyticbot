"""
Payment Protocols Module
========================

Clean Architecture payment protocols and interfaces.
These abstractions belong in the core layer.
"""

from .payment_protocols import (
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
