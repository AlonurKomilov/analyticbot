"""
Payment Adapter Factory
======================

Manages creation and configuration of payment gateway adapters.
Provides factory pattern for switching between Stripe, Mock, and other payment providers.
"""

import logging
from enum import Enum
from typing import Any

from config.settings import settings

logger = logging.getLogger(__name__)


class PaymentGateway(Enum):
    """Supported payment gateways"""

    STRIPE = "stripe"
    MOCK = "mock"


class PaymentAdapterFactory:
    """
    Factory for creating payment adapters with configuration-based switching.
    
    Clean Architecture: Abstracts payment provider details from business logic.
    """

    _adapters: dict[str, Any] = {}
    _current_adapter: Any | None = None
    _current_gateway: PaymentGateway = PaymentGateway.MOCK

    @classmethod
    def create_adapter(cls, gateway: PaymentGateway, **kwargs) -> Any:
        """
        Create or get existing adapter for specified gateway.

        Args:
            gateway: The payment gateway to create adapter for
            **kwargs: Additional configuration options

        Returns:
            PaymentAdapter instance
        """
        gateway_name = gateway.value

        # Create cache key including configuration options
        config_key = f"{gateway_name}:{hash(str(sorted(kwargs.items())))}"

        # Return cached adapter if exists
        if config_key in cls._adapters:
            logger.debug(f"Reusing cached payment adapter: {gateway_name}")
            return cls._adapters[config_key]

        # Create new adapter
        logger.info(f"Creating new payment adapter: {gateway_name}")

        if gateway == PaymentGateway.STRIPE:
            from apps.bot.services.adapters.stripe_payment_adapter import StripePaymentAdapter

            adapter = StripePaymentAdapter(**kwargs)
        elif gateway == PaymentGateway.MOCK:
            from apps.bot.services.adapters.mock_payment_adapter import MockPaymentAdapter

            adapter = MockPaymentAdapter(**kwargs)
        else:
            raise ValueError(f"Unsupported payment gateway: {gateway_name}")

        # Cache the adapter
        cls._adapters[config_key] = adapter
        logger.info(f"✅ Payment adapter created and cached: {gateway_name}")

        return adapter

    @classmethod
    def get_current_adapter(cls) -> Any:
        """
        Get the currently active payment adapter.

        Returns:
            Active PaymentAdapter instance
        """
        if cls._current_adapter is None:
            # Auto-configure based on settings
            gateway = cls._get_gateway_from_settings()
            cls._current_adapter = cls.create_adapter(gateway)
            cls._current_gateway = gateway

        return cls._current_adapter

    @classmethod
    def set_current_adapter(cls, gateway: PaymentGateway, **kwargs) -> Any:
        """
        Set the currently active payment adapter.

        Args:
            gateway: The payment gateway to use
            **kwargs: Additional configuration options

        Returns:
            The newly set PaymentAdapter instance
        """
        cls._current_adapter = cls.create_adapter(gateway, **kwargs)
        cls._current_gateway = gateway
        logger.info(f"🔄 Switched payment adapter to: {gateway.value}")
        return cls._current_adapter

    @classmethod
    def get_current_gateway(cls) -> PaymentGateway:
        """Get the currently active payment gateway enum."""
        return cls._current_gateway

    @classmethod
    def _get_gateway_from_settings(cls) -> PaymentGateway:
        """
        Determine payment gateway from application settings.

        Returns:
            PaymentGateway enum value
        """
        # Check environment/settings for payment provider configuration
        payment_provider = getattr(settings, "PAYMENT_PROVIDER", "mock").lower()

        try:
            return PaymentGateway(payment_provider)
        except ValueError:
            logger.warning(
                f"Unknown payment provider '{payment_provider}' in settings, "
                f"defaulting to MOCK"
            )
            return PaymentGateway.MOCK

    @classmethod
    def reset(cls):
        """
        Reset factory state (useful for testing).
        Clears adapter cache and resets current adapter.
        """
        cls._adapters.clear()
        cls._current_adapter = None
        cls._current_gateway = PaymentGateway.MOCK
        logger.info("🔄 Payment adapter factory reset")

    @classmethod
    def get_available_gateways(cls) -> list[str]:
        """Get list of available payment gateway names."""
        return [gateway.value for gateway in PaymentGateway]

    @classmethod
    def is_production_gateway(cls) -> bool:
        """Check if current gateway is production-ready (not mock)."""
        return cls._current_gateway != PaymentGateway.MOCK


# Convenience functions for common operations
def get_current_payment_adapter() -> Any:
    """Get the current payment adapter instance."""
    return PaymentAdapterFactory.get_current_adapter()


def switch_to_stripe(**kwargs) -> Any:
    """Switch to Stripe payment adapter."""
    return PaymentAdapterFactory.set_current_adapter(PaymentGateway.STRIPE, **kwargs)


def switch_to_mock(**kwargs) -> Any:
    """Switch to Mock payment adapter (for testing)."""
    return PaymentAdapterFactory.set_current_adapter(PaymentGateway.MOCK, **kwargs)
