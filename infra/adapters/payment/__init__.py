"""
Payment Adapters - Infrastructure Layer
========================================

Concrete implementations of payment gateway adapters.

Available Adapters:
- MockPaymentAdapter: Mock implementation for testing
- StripePaymentAdapter: Stripe payment gateway integration
- PaymentAdapterFactory: Factory for creating adapters

Usage:
    from infra.adapters.payment import PaymentAdapterFactory, PaymentGateway

    adapter = PaymentAdapterFactory.create_adapter(PaymentGateway.STRIPE)
"""

from .factory import PaymentAdapterFactory, PaymentGateway
from .mock_payment_adapter import MockPaymentAdapter
from .stripe_payment_adapter import StripePaymentAdapter

__all__ = [
    "PaymentAdapterFactory",
    "PaymentGateway",
    "MockPaymentAdapter",
    "StripePaymentAdapter",
]
