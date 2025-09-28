"""
Payment Gateway Adapter Factory
Manages creation and configuration of payment gateway adapters
"""

import logging
from enum import Enum
from typing import Any

from apps.bot.services.adapters.base_adapter import PaymentGatewayAdapter
from apps.bot.services.adapters.mock_payment_adapter import MockPaymentAdapter
from apps.bot.services.adapters.stripe_payment_adapter import StripePaymentAdapter

from config.settings import settings

logger = logging.getLogger(__name__)


class PaymentGateway(Enum):
    """Supported payment gateways"""

    STRIPE = "stripe"
    MOCK = "mock"


class PaymentAdapterFactory:
    """
    Factory for creating payment gateway adapters
    """

    _adapters: dict[str, PaymentGatewayAdapter] = {}
    _current_adapter: PaymentGatewayAdapter | None = None

    @classmethod
    def create_adapter(cls, gateway: PaymentGateway) -> PaymentGatewayAdapter:
        """
        Create or get existing adapter for specified gateway

        Args:
            gateway: The payment gateway to create adapter for

        Returns:
            PaymentGatewayAdapter instance
        """
        gateway_name = gateway.value

        # Return existing adapter if already created
        if gateway_name in cls._adapters:
            logger.debug(f"Returning existing {gateway_name} adapter")
            return cls._adapters[gateway_name]

        # Create new adapter based on gateway type
        if gateway == PaymentGateway.STRIPE:
            adapter = StripePaymentAdapter()
        elif gateway == PaymentGateway.MOCK:
            adapter = MockPaymentAdapter()
        else:
            raise ValueError(f"Unsupported payment gateway: {gateway_name}")

        # Cache the adapter
        cls._adapters[gateway_name] = adapter
        logger.info(f"Created new {gateway_name} adapter")

        return adapter

    @classmethod
    def get_current_adapter(cls) -> PaymentGatewayAdapter:
        """
        Get the currently configured payment adapter based on settings

        Returns:
            PaymentGatewayAdapter instance
        """
        if cls._current_adapter is not None:
            return cls._current_adapter

        # Determine gateway from settings
        use_mock = getattr(settings, "USE_MOCK_PAYMENT", False)
        gateway = PaymentGateway.MOCK if use_mock else PaymentGateway.STRIPE

        cls._current_adapter = cls.create_adapter(gateway)
        logger.info(f"Set current adapter to: {gateway.value}")

        return cls._current_adapter

    @classmethod
    def set_current_adapter(cls, gateway: PaymentGateway) -> PaymentGatewayAdapter:
        """
        Explicitly set the current payment adapter

        Args:
            gateway: The payment gateway to use

        Returns:
            PaymentGatewayAdapter instance
        """
        cls._current_adapter = cls.create_adapter(gateway)
        logger.info(f"Manually set current adapter to: {gateway.value}")

        return cls._current_adapter

    @classmethod
    def clear_cache(cls):
        """Clear all cached adapters"""
        cls._adapters.clear()
        cls._current_adapter = None
        logger.info("Cleared payment adapter cache")

    @classmethod
    def get_available_gateways(cls) -> list[str]:
        """Get list of available payment gateways"""
        return [gateway.value for gateway in PaymentGateway]

    @classmethod
    async def health_check_all(cls) -> dict[str, Any]:
        """
        Run health check on all available payment gateways

        Returns:
            Dict with health status for each gateway
        """
        results = {}

        for gateway in PaymentGateway:
            try:
                adapter = cls.create_adapter(gateway)
                health = await adapter.health_check()
                results[gateway.value] = health
            except Exception as e:
                logger.error(f"Health check failed for {gateway.value}: {e}")
                results[gateway.value] = {"status": "error", "error": str(e)}

        return results

    @classmethod
    def get_adapter_info(cls, gateway: PaymentGateway) -> dict[str, Any]:
        """
        Get information about a specific adapter

        Args:
            gateway: The payment gateway

        Returns:
            Dict with adapter information
        """
        try:
            adapter = cls.create_adapter(gateway)
            return {
                "name": adapter.get_adapter_name(),
                "gateway": gateway.value,
                "class": adapter.__class__.__name__,
                "is_current": cls._current_adapter == adapter,
                "cached": gateway.value in cls._adapters,
            }
        except Exception as e:
            return {"gateway": gateway.value, "error": str(e), "available": False}
