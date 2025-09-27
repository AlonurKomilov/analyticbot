"""
Mock Payment Gateway Adapter
Provides realistic mock responses for development and testing
"""

import logging
import time
import uuid
from decimal import Decimal
from typing import Any

from src.bot_service.models.payment import (
    BillingCycle,
    PaymentStatus,
    SubscriptionStatus,
)
from src.bot_service.services.adapters.base_adapter import PaymentGatewayAdapter

logger = logging.getLogger(__name__)


class MockPaymentAdapter(PaymentGatewayAdapter):
    """
    Mock implementation of PaymentGatewayAdapter for development/testing
    """

    def __init__(self):
        self.customers = {}
        self.payment_methods = {}
        self.payment_intents = {}
        self.subscriptions = {}
        self.webhook_events = []

        logger.info("MockPaymentAdapter initialized")

    def get_adapter_name(self) -> str:
        return "mock_payment_gateway"

    async def create_customer(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """Create mock customer"""
        customer_id = f"cus_mock_{uuid.uuid4().hex[:12]}"

        customer = {
            "id": customer_id,
            "email": user_data.get("email", "mock@example.com"),
            "name": user_data.get("name", "Mock Customer"),
            "phone": user_data.get("phone"),
            "created": int(time.time()),
            "metadata": user_data.get("metadata", {}),
            "balance": 0,
            "currency": "usd",
            "description": f"Mock customer for {user_data.get('name', 'unknown')}",
        }

        self.customers[customer_id] = customer

        logger.info(f"Created mock customer: {customer_id}")

        return {
            "success": True,
            "customer_id": customer_id,
            "gateway_response": customer,
        }

    async def create_payment_method(
        self, customer_id: str, method_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create mock payment method"""
        method_id = f"pm_mock_{uuid.uuid4().hex[:12]}"

        payment_method = {
            "id": method_id,
            "type": method_data.get("type", "card"),
            "customer": customer_id,
            "created": int(time.time()),
            "card": (
                {
                    "brand": "visa",
                    "last4": "4242",
                    "exp_month": 12,
                    "exp_year": 2025,
                    "country": "US",
                }
                if method_data.get("type") == "card"
                else None
            ),
            "metadata": method_data.get("metadata", {}),
        }

        self.payment_methods[method_id] = payment_method

        logger.info(f"Created mock payment method: {method_id}")

        return {
            "success": True,
            "payment_method_id": method_id,
            "gateway_response": payment_method,
        }

    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        customer_id: str,
        payment_method_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create mock payment intent"""
        intent_id = f"pi_mock_{uuid.uuid4().hex[:12]}"

        # Simulate different scenarios based on amount
        if int(amount) == 999:  # Special test amount for failure
            status = "requires_action"
        elif int(amount) == 1000:  # Special test amount for processing
            status = "processing"
        else:
            status = "succeeded"

        payment_intent = {
            "id": intent_id,
            "amount": int(amount * 100),  # Convert to cents
            "currency": currency.lower(),
            "customer": customer_id,
            "payment_method": payment_method_id,
            "status": status,
            "created": int(time.time()),
            "client_secret": f"{intent_id}_secret_mock",
            "metadata": metadata or {},
            "charges": (
                {
                    "data": [
                        {
                            "id": f"ch_mock_{uuid.uuid4().hex[:8]}",
                            "amount": int(amount * 100),
                            "currency": currency.lower(),
                            "status": ("succeeded" if status == "succeeded" else "pending"),
                            "created": int(time.time()),
                        }
                    ]
                }
                if status in ["succeeded", "processing"]
                else {"data": []}
            ),
        }

        self.payment_intents[intent_id] = payment_intent

        logger.info(f"Created mock payment intent: {intent_id} (status: {status})")

        return {
            "success": True,
            "provider_payment_id": intent_id,
            "status": (PaymentStatus.SUCCEEDED if status == "succeeded" else PaymentStatus.PENDING),
            "amount": float(amount),
            "currency": currency,
            "client_secret": payment_intent["client_secret"],
            "gateway_response": payment_intent,
        }

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_method_id: str,
        billing_cycle: BillingCycle,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create mock subscription"""
        sub_id = f"sub_mock_{uuid.uuid4().hex[:12]}"

        current_time = int(time.time())
        # Calculate period end based on billing cycle
        if billing_cycle == BillingCycle.MONTHLY:
            period_end = current_time + (30 * 24 * 60 * 60)  # 30 days
        elif billing_cycle == BillingCycle.YEARLY:
            period_end = current_time + (365 * 24 * 60 * 60)  # 365 days
        else:  # Weekly
            period_end = current_time + (7 * 24 * 60 * 60)  # 7 days

        subscription = {
            "id": sub_id,
            "customer": customer_id,
            "status": "active",
            "created": current_time,
            "current_period_start": current_time,
            "current_period_end": period_end,
            "default_payment_method": payment_method_id,
            "items": {
                "data": [
                    {
                        "id": f"si_mock_{uuid.uuid4().hex[:8]}",
                        "price": {
                            "id": price_id,
                            "recurring": {
                                "interval": billing_cycle.value,
                            },
                        },
                    }
                ]
            },
            "metadata": metadata or {},
        }

        self.subscriptions[sub_id] = subscription

        logger.info(f"Created mock subscription: {sub_id}")

        return {
            "success": True,
            "provider_subscription_id": sub_id,
            "status": SubscriptionStatus.ACTIVE,
            "current_period_start": current_time,
            "current_period_end": period_end,
            "gateway_response": subscription,
        }

    async def cancel_subscription(
        self, subscription_id: str, immediate: bool = False
    ) -> dict[str, Any]:
        """Cancel mock subscription"""
        if subscription_id not in self.subscriptions:
            return {"success": False, "error": "Subscription not found"}

        subscription = self.subscriptions[subscription_id]

        if immediate:
            subscription["status"] = "canceled"
            subscription["canceled_at"] = int(time.time())
        else:
            subscription["status"] = "active"  # Will be canceled at period end
            subscription["cancel_at_period_end"] = True

        logger.info(f"Canceled mock subscription: {subscription_id} (immediate: {immediate})")

        return {
            "success": True,
            "status": (SubscriptionStatus.CANCELED if immediate else SubscriptionStatus.ACTIVE),
            "canceled_at": subscription.get("canceled_at"),
            "gateway_response": subscription,
        }

    async def update_subscription(
        self, subscription_id: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
        """Update mock subscription"""
        if subscription_id not in self.subscriptions:
            return {"success": False, "error": "Subscription not found"}

        subscription = self.subscriptions[subscription_id]
        subscription.update(updates)

        logger.info(f"Updated mock subscription: {subscription_id}")

        return {"success": True, "gateway_response": subscription}

    async def handle_webhook(
        self, payload: str, signature: str, endpoint_secret: str
    ) -> dict[str, Any]:
        """Handle mock webhook"""
        # Mock webhook validation (always succeeds)
        event_id = f"evt_mock_{uuid.uuid4().hex[:12]}"

        # Parse mock event from payload (simplified)
        event = {
            "id": event_id,
            "type": "payment_intent.succeeded",  # Mock event type
            "created": int(time.time()),
            "data": {
                "object": {
                    "id": f"pi_mock_{uuid.uuid4().hex[:8]}",
                    "status": "succeeded",
                }
            },
        }

        self.webhook_events.append(event)

        logger.info(f"Processed mock webhook: {event_id}")

        return {
            "success": True,
            "event_id": event_id,
            "event_type": event["type"],
            "processed": True,
        }

    async def get_customer(self, customer_id: str) -> dict[str, Any] | None:
        """Get mock customer"""
        return self.customers.get(customer_id)

    async def get_subscription(self, subscription_id: str) -> dict[str, Any] | None:
        """Get mock subscription"""
        return self.subscriptions.get(subscription_id)

    async def list_payment_methods(self, customer_id: str) -> list[dict[str, Any]]:
        """List mock payment methods"""
        return [pm for pm in self.payment_methods.values() if pm.get("customer") == customer_id]

    async def health_check(self) -> dict[str, Any]:
        """Mock health check"""
        return {
            "status": "healthy",
            "adapter": "mock_payment_gateway",
            "timestamp": int(time.time()),
            "mock_data": {
                "customers": len(self.customers),
                "payment_methods": len(self.payment_methods),
                "payment_intents": len(self.payment_intents),
                "subscriptions": len(self.subscriptions),
                "webhook_events": len(self.webhook_events),
            },
        }
