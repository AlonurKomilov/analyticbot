"""
Payment Service Implementation
Wraps payment adapters to implement PaymentServiceProtocol
"""

import logging
from datetime import datetime
from typing import Any

from apps.bot.models.payment import BillingCycle
from apps.bot.services.adapters.mock_payment_adapter import MockPaymentAdapter
from core.protocols import PaymentServiceProtocol

logger = logging.getLogger(__name__)


class MockPaymentService(PaymentServiceProtocol):
    """Mock payment service that wraps MockPaymentAdapter"""

    def __init__(self):
        self.service_name = "MockPaymentService"
        self.adapter = MockPaymentAdapter()
        logger.info(f"Initialized {self.service_name}")

    def get_service_name(self) -> str:
        return self.service_name

    async def health_check(self) -> dict[str, Any]:
        """Service health check"""
        adapter_health = await self.adapter.health_check()
        return {
            "status": "healthy",
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "mock": True,
            "adapter_status": adapter_health,
        }

    async def process_payment(self, amount: int, currency: str, user_id: int) -> dict[str, Any]:
        """Process a payment"""
        try:
            # Create customer if needed
            customer_result = await self.adapter.create_customer(
                {
                    "email": f"user_{user_id}@demo.com",
                    "name": f"Demo User {user_id}",
                    "metadata": {"user_id": str(user_id)},
                }
            )

            if not customer_result["success"]:
                return {"success": False, "error": "Failed to create customer"}

            customer_id = customer_result["customer_id"]

            # Create payment method
            method_result = await self.adapter.create_payment_method(customer_id, {"type": "card"})

            if not method_result["success"]:
                return {"success": False, "error": "Failed to create payment method"}

            payment_method_id = method_result["payment_method_id"]

            # Create payment intent
            payment_result = await self.adapter.create_payment_intent(
                amount=amount,
                currency=currency,
                customer_id=customer_id,
                payment_method_id=payment_method_id,
                metadata={"user_id": str(user_id)},
            )

            return {
                "success": payment_result["success"],
                "payment_id": payment_result.get("provider_payment_id"),
                "status": payment_result.get("status"),
                "amount": payment_result.get("amount"),
                "currency": payment_result.get("currency"),
                "client_secret": payment_result.get("client_secret"),
            }

        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            return {"success": False, "error": str(e)}

    async def create_subscription(self, user_id: int, plan_id: str) -> dict[str, Any]:
        """Create a subscription"""
        try:
            # Create customer if needed
            customer_result = await self.adapter.create_customer(
                {
                    "email": f"user_{user_id}@demo.com",
                    "name": f"Demo User {user_id}",
                    "metadata": {"user_id": str(user_id)},
                }
            )

            if not customer_result["success"]:
                return {"success": False, "error": "Failed to create customer"}

            customer_id = customer_result["customer_id"]

            # Create payment method
            method_result = await self.adapter.create_payment_method(customer_id, {"type": "card"})

            if not method_result["success"]:
                return {"success": False, "error": "Failed to create payment method"}

            payment_method_id = method_result["payment_method_id"]

            # Determine billing cycle from plan_id
            billing_cycle = BillingCycle.MONTHLY  # Default
            if "yearly" in plan_id.lower():
                billing_cycle = BillingCycle.YEARLY
            elif "weekly" in plan_id.lower():
                billing_cycle = BillingCycle.WEEKLY

            # Create subscription
            sub_result = await self.adapter.create_subscription(
                customer_id=customer_id,
                price_id=plan_id,
                payment_method_id=payment_method_id,
                billing_cycle=billing_cycle,
                metadata={"user_id": str(user_id)},
            )

            return {
                "success": sub_result["success"],
                "subscription_id": sub_result.get("provider_subscription_id"),
                "status": sub_result.get("status"),
                "current_period_start": sub_result.get("current_period_start"),
                "current_period_end": sub_result.get("current_period_end"),
            }

        except Exception as e:
            logger.error(f"Subscription creation failed: {e}")
            return {"success": False, "error": str(e)}

    async def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        """Cancel a subscription"""
        try:
            result = await self.adapter.cancel_subscription(subscription_id, immediate=False)

            return {
                "success": result["success"],
                "subscription_id": subscription_id,
                "status": result.get("status"),
                "canceled_at": result.get("canceled_at"),
            }

        except Exception as e:
            logger.error(f"Subscription cancellation failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_payment_methods(self, user_id: int) -> list[dict[str, Any]]:
        """Get user's payment methods"""
        try:
            # For mock service, return mock payment methods
            return [
                {
                    "id": f"pm_mock_{user_id}_1",
                    "type": "card",
                    "card": {
                        "brand": "visa",
                        "last4": "4242",
                        "exp_month": 12,
                        "exp_year": 2025,
                    },
                    "is_default": True,
                },
                {
                    "id": f"pm_mock_{user_id}_2",
                    "type": "card",
                    "card": {
                        "brand": "mastercard",
                        "last4": "5555",
                        "exp_month": 6,
                        "exp_year": 2026,
                    },
                    "is_default": False,
                },
            ]

        except Exception as e:
            logger.error(f"Failed to get payment methods: {e}")
            return []

    async def refund_payment(self, payment_id: str, amount: int | None = None) -> dict[str, Any]:
        """Process a refund"""
        try:
            # Mock refund processing
            refund_id = f"re_mock_{payment_id}_{datetime.utcnow().timestamp()}"

            logger.info(f"🔄 Mock refund processed: {refund_id}")

            return {
                "success": True,
                "refund_id": refund_id,
                "payment_id": payment_id,
                "amount": amount,
                "status": "succeeded",
                "created": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Refund processing failed: {e}")
            return {"success": False, "error": str(e)}
