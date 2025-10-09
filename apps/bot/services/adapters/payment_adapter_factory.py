"""
Payment Gateway Adapter Factory

DEPRECATED: This module has been moved to infra.adapters.payment
Import from there instead: from infra.adapters.payment import PaymentAdapterFactory

Kept for backward compatibility only.
"""

# Backward compatibility - import from new location
from infra.adapters.payment import (
    MockPaymentAdapter,
    PaymentAdapterFactory,
    PaymentGateway,
    StripePaymentAdapter,
)

# Re-export for backward compatibility
__all__ = ["PaymentAdapterFactory", "PaymentGateway", "MockPaymentAdapter", "StripePaymentAdapter"]
