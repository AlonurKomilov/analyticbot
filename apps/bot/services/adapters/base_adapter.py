"""
Base Payment Gateway Adapter Interface
Defines the contract that all payment adapters must implement
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from apps.bot.models.payment import BillingCycle


class PaymentGatewayAdapter(ABC):
    """
    Abstract base class for payment gateway adapters
    """

    @abstractmethod
    async def create_customer(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new customer in the payment gateway

        Args:
            user_data: Dictionary containing customer information

        Returns:
            Dictionary with customer data including gateway customer ID
        """
        pass

    @abstractmethod
    async def create_payment_method(
        self, customer_id: str, method_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create a payment method for a customer

        Args:
            customer_id: Gateway customer ID
            method_data: Payment method information

        Returns:
            Dictionary with payment method data
        """
        pass

    @abstractmethod
    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        customer_id: str,
        payment_method_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a payment intent for one-time payment

        Args:
            amount: Payment amount
            currency: Payment currency
            customer_id: Gateway customer ID
            payment_method_id: Payment method ID
            metadata: Additional metadata

        Returns:
            Dictionary with payment intent data
        """
        pass

    @abstractmethod
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_method_id: str,
        billing_cycle: BillingCycle,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a subscription for recurring payments

        Args:
            customer_id: Gateway customer ID
            price_id: Price/plan ID in the gateway
            payment_method_id: Payment method ID
            billing_cycle: Billing frequency
            metadata: Additional metadata

        Returns:
            Dictionary with subscription data
        """
        pass

    @abstractmethod
    async def cancel_subscription(
        self, subscription_id: str, immediate: bool = False
    ) -> dict[str, Any]:
        """
        Cancel a subscription

        Args:
            subscription_id: Gateway subscription ID
            immediate: Whether to cancel immediately or at period end

        Returns:
            Dictionary with cancellation result
        """
        pass

    @abstractmethod
    async def update_subscription(
        self, subscription_id: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update subscription details

        Args:
            subscription_id: Gateway subscription ID
            updates: Dictionary of updates to apply

        Returns:
            Dictionary with updated subscription data
        """
        pass

    @abstractmethod
    async def handle_webhook(
        self, payload: str, signature: str, endpoint_secret: str
    ) -> dict[str, Any]:
        """
        Handle webhook events from the payment gateway

        Args:
            payload: Raw webhook payload
            signature: Webhook signature for verification
            endpoint_secret: Webhook endpoint secret

        Returns:
            Dictionary with processed webhook data
        """
        pass

    @abstractmethod
    async def get_customer(self, customer_id: str) -> dict[str, Any] | None:
        """
        Retrieve customer information

        Args:
            customer_id: Gateway customer ID

        Returns:
            Dictionary with customer data or None if not found
        """
        pass

    @abstractmethod
    async def get_subscription(self, subscription_id: str) -> dict[str, Any] | None:
        """
        Retrieve subscription information

        Args:
            subscription_id: Gateway subscription ID

        Returns:
            Dictionary with subscription data or None if not found
        """
        pass

    @abstractmethod
    async def list_payment_methods(self, customer_id: str) -> list[dict[str, Any]]:
        """
        List all payment methods for a customer

        Args:
            customer_id: Gateway customer ID

        Returns:
            List of payment method dictionaries
        """
        pass

    @abstractmethod
    def get_adapter_name(self) -> str:
        """
        Get the name/type of this adapter

        Returns:
            String identifier for the adapter
        """
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """
        Check if the payment gateway is accessible

        Returns:
            Dictionary with health status
        """
        pass
