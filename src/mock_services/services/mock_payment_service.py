"""
Consolidated Mock Payment Service

Migrated from:
- src/api_service/application/services/__mocks__/mock_payment_service.py
- src/api_service/infrastructure/testing/services/mock_payment_service.py
"""

import asyncio
import logging
import random
import uuid
from datetime import datetime
from typing import Any

from ..constants import PAYMENT_DELAY_MS, PAYMENT_SUCCESS_RATE, SUPPORTED_CURRENCIES
from ..infrastructure.base import BaseMockService, mock_metrics

logger = logging.getLogger(__name__)


class MockPaymentService(BaseMockService):
    """
    Consolidated Mock Payment Service

    Combines functionality from multiple scattered payment mock implementations.
    """

    def __init__(self):
        super().__init__("MockPaymentService")
        self.transactions = {}
        self.subscriptions = {}
        self.failed_transactions = []
        self.total_processed = 0

    def get_service_name(self) -> str:
        return self.service_name

    async def health_check(self) -> dict[str, Any]:
        """Enhanced health check with payment-specific metrics"""
        mock_metrics.record_call(self.service_name, "health_check")
        await asyncio.sleep(PAYMENT_DELAY_MS / 1000)

        base_health = await super().health_check()
        base_health.update(
            {
                "transactions_processed": self.total_processed,
                "failed_transactions": len(self.failed_transactions),
                "success_rate": PAYMENT_SUCCESS_RATE,
                "supported_currencies": SUPPORTED_CURRENCIES,
                "active_subscriptions": len(self.subscriptions),
            }
        )
        return base_health

    async def create_payment_intent(
        self, amount: int, currency: str = "usd", **kwargs
    ) -> dict[str, Any]:
        """Create a mock payment intent"""
        mock_metrics.record_call(self.service_name, "create_payment_intent")
        await asyncio.sleep(PAYMENT_DELAY_MS / 1000)

        if currency.lower() not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Currency {currency} not supported")

        intent_id = str(uuid.uuid4())
        client_secret = f"pi_{intent_id}_secret_{uuid.uuid4().hex[:8]}"

        # Simulate occasional failures
        will_succeed = random.random() < PAYMENT_SUCCESS_RATE

        intent_data = {
            "id": intent_id,
            "amount": amount,
            "currency": currency.lower(),
            "status": ("requires_confirmation" if will_succeed else "requires_payment_method"),
            "client_secret": client_secret,
            "created": datetime.utcnow().isoformat(),
            "metadata": kwargs.get("metadata", {}),
            "mock_simulation": {
                "will_succeed": will_succeed,
                "processing_delay": PAYMENT_DELAY_MS,
            },
        }

        self.transactions[intent_id] = intent_data
        self.total_processed += 1

        return intent_data

    async def process_payment(self, amount: int, currency: str, user_id: int) -> dict[str, Any]:
        """Process a complete payment flow"""
        mock_metrics.record_call(self.service_name, "process_payment")

        try:
            # Create payment intent
            intent = await self.create_payment_intent(
                amount=amount, currency=currency, metadata={"user_id": str(user_id)}
            )

            # Simulate confirmation
            if intent["mock_simulation"]["will_succeed"]:
                intent["status"] = "succeeded"
                intent["confirmed_at"] = datetime.utcnow().isoformat()

                return {
                    "success": True,
                    "payment_id": intent["id"],
                    "status": "succeeded",
                    "amount": amount,
                    "currency": currency,
                }
            else:
                intent["status"] = "failed"
                intent["failed_at"] = datetime.utcnow().isoformat()
                self.failed_transactions.append(intent["id"])

                return {
                    "success": False,
                    "error": "Payment failed",
                    "payment_id": intent["id"],
                }

        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            return {"success": False, "error": str(e)}

    async def create_subscription(self, user_id: int, plan_id: str) -> dict[str, Any]:
        """Create a mock subscription"""
        mock_metrics.record_call(self.service_name, "create_subscription")
        await asyncio.sleep(PAYMENT_DELAY_MS / 1000)

        subscription_id = str(uuid.uuid4())

        subscription_data = {
            "id": subscription_id,
            "user_id": user_id,
            "plan_id": plan_id,
            "status": "active",
            "created": datetime.utcnow().isoformat(),
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": datetime.utcnow().isoformat(),  # Would calculate properly
        }

        self.subscriptions[subscription_id] = subscription_data

        return {
            "success": True,
            "subscription_id": subscription_id,
            "status": "active",
            "current_period_start": subscription_data["current_period_start"],
            "current_period_end": subscription_data["current_period_end"],
        }

    def reset(self) -> None:
        """Reset service state"""
        super().reset()
        self.transactions.clear()
        self.subscriptions.clear()
        self.failed_transactions.clear()
        self.total_processed = 0

    def get_transaction_history(self) -> dict[str, Any]:
        """Get transaction history for testing"""
        return {
            "all_transactions": self.transactions.copy(),
            "failed_transactions": self.failed_transactions.copy(),
            "subscriptions": self.subscriptions.copy(),
            "total_processed": self.total_processed,
            "success_rate": (self.total_processed - len(self.failed_transactions))
            / max(1, self.total_processed),
        }
