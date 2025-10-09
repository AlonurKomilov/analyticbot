"""
Base Payment Gateway Adapter Interface

DEPRECATED: This module has been moved to core.adapters.payment
Import from there instead: from core.adapters.payment import PaymentGatewayAdapter

Kept for backward compatibility only.
"""

# Backward compatibility - import from new location
from core.adapters.payment import PaymentGatewayAdapter

# Re-export for backward compatibility
__all__ = ["PaymentGatewayAdapter"]
