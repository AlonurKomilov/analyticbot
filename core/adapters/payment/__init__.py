"""
Payment Adapter Protocols
=========================

Core protocols for payment gateway adapters.
Infrastructure layer implements these protocols.
"""

from .payment_adapter_protocol import PaymentGatewayAdapter

__all__ = ["PaymentGatewayAdapter"]
