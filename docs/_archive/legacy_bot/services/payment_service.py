"""
Payment service with universal adapter pattern for multi-gateway support
"""

import hashlib
import hmac
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import uuid4

from apps.bot.database.repositories.payment_repository import PaymentRepository
from apps.bot.models.payment import (
    BillingCycle,
    PaymentCreate,
    PaymentMethodCreate,
    PaymentMethodResponse,
    PaymentProvider,
    PaymentResponse,
    PaymentStatus,
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionStatus,
)

logger = logging.getLogger(__name__)


class PaymentGatewayAdapter(ABC):
    """Abstract base class for payment gateway adapters"""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name"""

    @abstractmethod
    async def create_payment_method(
        self, user_id: int, method_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create payment method with the gateway"""

    @abstractmethod
    async def charge_payment_method(
        self,
        method_id: str,
        amount: Decimal,
        currency: str,
        description: (str | None) = None,
        metadata: (dict[str, Any] | None) = None,
    ) -> dict[str, Any]:
        """Charge a payment method"""

    @abstractmethod
    async def create_subscription(
        self,
        customer_id: str,
        payment_method_id: str,
        plan_id: str,
        billing_cycle: BillingCycle,
        trial_days: (int | None) = None,
    ) -> dict[str, Any]:
        """Create recurring subscription"""

    @abstractmethod
    async def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        """Cancel subscription"""

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify webhook signature"""

    @abstractmethod
    async def handle_webhook_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Process webhook event"""


class StripeAdapter(PaymentGatewayAdapter):
    """Stripe payment gateway adapter"""

    def __init__(self, api_key: str, webhook_secret: str):
        self.api_key = api_key
        self.webhook_secret = webhook_secret

    @property
    def provider_name(self) -> str:
        return PaymentProvider.STRIPE

    async def create_payment_method(
        self, user_id: int, method_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create Stripe payment method"""
        return {
            "id": f"pm_{uuid4().hex[:24]}",
            "type": "card",
            "card": {
                "brand": method_data.get("brand", "visa"),
                "last4": method_data.get("last4", "4242"),
                "exp_month": method_data.get("exp_month", 12),
                "exp_year": method_data.get("exp_year", 2025),
            },
            "created": int(datetime.utcnow().timestamp()),
        }

    async def charge_payment_method(
        self,
        method_id: str,
        amount: Decimal,
        currency: str,
        description: (str | None) = None,
        metadata: (dict[str, Any] | None) = None,
    ) -> dict[str, Any]:
        """Process Stripe payment"""
        payment_intent_id = f"pi_{uuid4().hex[:24]}"
        return {
            "id": payment_intent_id,
            "amount": int(amount * 100),
            "currency": currency.lower(),
            "status": "succeeded",
            "payment_method": method_id,
            "description": description,
            "metadata": metadata or {},
            "created": int(datetime.utcnow().timestamp()),
        }

    async def create_subscription(
        self,
        customer_id: str,
        payment_method_id: str,
        plan_id: str,
        billing_cycle: BillingCycle,
        trial_days: (int | None) = None,
    ) -> dict[str, Any]:
        """Create Stripe subscription"""
        subscription_id = f"sub_{uuid4().hex[:24]}"
        now = datetime.utcnow()
        return {
            "id": subscription_id,
            "status": "active",
            "current_period_start": int(now.timestamp()),
            "current_period_end": int(
                (
                    now + timedelta(days=30 if billing_cycle == BillingCycle.MONTHLY else 365)
                ).timestamp()
            ),
            "trial_end": int((now + timedelta(days=trial_days)).timestamp())
            if trial_days
            else None,
            "customer": customer_id,
            "default_payment_method": payment_method_id,
        }

    async def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        """Cancel Stripe subscription"""
        return {
            "id": subscription_id,
            "status": "canceled",
            "canceled_at": int(datetime.utcnow().timestamp()),
        }

    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify Stripe webhook signature"""
        try:
            elements = signature.split(",")
            timestamp = None
            signatures = []
            for element in elements:
                key, value = element.split("=")
                if key == "t":
                    timestamp = value
                elif key.startswith("v"):
                    signatures.append(value)
            if not timestamp or not signatures:
                return False
            payload_str = f"{timestamp}.{payload.decode()}"
            expected_sig = hmac.new(
                secret.encode(), payload_str.encode(), hashlib.sha256
            ).hexdigest()
            return any(hmac.compare_digest(expected_sig, sig) for sig in signatures)
        except Exception as e:
            logger.error(f"Stripe webhook verification error: {e}")
            return False

    async def handle_webhook_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Handle Stripe webhook events"""
        event_type = event_data.get("type")
        if event_type == "payment_intent.succeeded":
            return {
                "action": "payment_succeeded",
                "payment_id": event_data["data"]["object"]["id"],
                "amount": event_data["data"]["object"]["amount"] / 100,
                "currency": event_data["data"]["object"]["currency"],
            }
        elif event_type == "payment_intent.payment_failed":
            return {
                "action": "payment_failed",
                "payment_id": event_data["data"]["object"]["id"],
                "failure_code": event_data["data"]["object"]
                .get("last_payment_error", {})
                .get("code"),
                "failure_message": event_data["data"]["object"]
                .get("last_payment_error", {})
                .get("message"),
            }
        elif event_type == "invoice.payment_succeeded":
            return {
                "action": "subscription_renewed",
                "subscription_id": event_data["data"]["object"]["subscription"],
                "amount": event_data["data"]["object"]["amount_paid"] / 100,
            }
        return {"action": "ignored", "event_type": event_type}


class PaymeAdapter(PaymentGatewayAdapter):
    """Payme (Uzbekistan) payment gateway adapter"""

    def __init__(self, merchant_id: str, secret_key: str):
        self.merchant_id = merchant_id
        self.secret_key = secret_key

    @property
    def provider_name(self) -> str:
        return PaymentProvider.PAYME

    async def create_payment_method(
        self, user_id: int, method_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create Payme card"""
        return {
            "id": f"card_{uuid4().hex[:16]}",
            "type": "card",
            "number": f"**** **** **** {method_data.get('last4', '1234')}",
            "expire": method_data.get("expire", "12/25"),
            "created_time": int(datetime.utcnow().timestamp() * 1000),
        }

    async def charge_payment_method(
        self,
        method_id: str,
        amount: Decimal,
        currency: str,
        description: (str | None) = None,
        metadata: (dict[str, Any] | None) = None,
    ) -> dict[str, Any]:
        """Process Payme payment"""
        transaction_id = f"txn_{uuid4().hex[:16]}"
        return {
            "id": transaction_id,
            "amount": int(amount * 100),
            "currency": "UZS",
            "state": 2,
            "create_time": int(datetime.utcnow().timestamp() * 1000),
            "perform_time": int(datetime.utcnow().timestamp() * 1000),
            "reason": None,
        }

    async def create_subscription(
        self,
        customer_id: str,
        payment_method_id: str,
        plan_id: str,
        billing_cycle: BillingCycle,
        trial_days: (int | None) = None,
    ) -> dict[str, Any]:
        """Payme doesn't support subscriptions directly - simulate with recurring payments"""
        return {
            "id": f"recurring_{uuid4().hex[:16]}",
            "status": "active",
            "card_id": payment_method_id,
            "period": "monthly" if billing_cycle == BillingCycle.MONTHLY else "yearly",
            "created_time": int(datetime.utcnow().timestamp() * 1000),
        }

    async def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        """Cancel Payme recurring payment"""
        return {
            "id": subscription_id,
            "status": "canceled",
            "canceled_time": int(datetime.utcnow().timestamp() * 1000),
        }

    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify Payme webhook signature"""
        try:
            expected_signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Payme webhook verification error: {e}")
            return False

    async def handle_webhook_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Handle Payme webhook events"""
        method = event_data.get("method")
        if method == "CheckPerformTransaction":
            return {"action": "check_transaction"}
        elif method == "CreateTransaction":
            return {
                "action": "payment_created",
                "transaction_id": event_data.get("params", {}).get("id"),
                "amount": event_data.get("params", {}).get("amount", 0) / 100,
            }
        elif method == "PerformTransaction":
            return {
                "action": "payment_succeeded",
                "transaction_id": event_data.get("params", {}).get("id"),
                "amount": event_data.get("params", {}).get("amount", 0) / 100,
            }
        return {"action": "ignored", "method": method}


class ClickAdapter(PaymentGatewayAdapter):
    """Click (Uzbekistan) payment gateway adapter"""

    def __init__(self, merchant_id: str, service_id: str, secret_key: str):
        self.merchant_id = merchant_id
        self.service_id = service_id
        self.secret_key = secret_key

    @property
    def provider_name(self) -> str:
        return PaymentProvider.CLICK

    async def create_payment_method(
        self, user_id: int, method_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Click uses phone numbers as payment methods"""
        return {
            "id": f"phone_{uuid4().hex[:12]}",
            "type": "phone",
            "phone": method_data.get("phone", "+998901234567"),
            "created_at": datetime.utcnow().isoformat(),
        }

    async def charge_payment_method(
        self,
        method_id: str,
        amount: Decimal,
        currency: str,
        description: (str | None) = None,
        metadata: (dict[str, Any] | None) = None,
    ) -> dict[str, Any]:
        """Process Click payment"""
        click_trans_id = f"click_{uuid4().hex[:12]}"
        return {
            "click_trans_id": click_trans_id,
            "amount": float(amount),
            "currency": "UZS",
            "error": 0,
            "error_note": "Success",
            "datetime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }

    async def create_subscription(
        self,
        customer_id: str,
        payment_method_id: str,
        plan_id: str,
        billing_cycle: BillingCycle,
        trial_days: (int | None) = None,
    ) -> dict[str, Any]:
        """Click subscription simulation"""
        return {
            "subscription_id": f"click_sub_{uuid4().hex[:12]}",
            "status": "active",
            "phone": payment_method_id,
            "billing_cycle": billing_cycle.value,
            "created_at": datetime.utcnow().isoformat(),
        }

    async def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        """Cancel Click subscription"""
        return {
            "subscription_id": subscription_id,
            "status": "canceled",
            "canceled_at": datetime.utcnow().isoformat(),
        }

    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify Click webhook signature"""
        try:
            expected_signature = hashlib.md5(f"{payload.decode()}{secret}".encode()).hexdigest()
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Click webhook verification error: {e}")
            return False

    async def handle_webhook_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Handle Click webhook events"""
        action = event_data.get("action")
        if action == "0":
            return {
                "action": "payment_prepared",
                "click_trans_id": event_data.get("click_trans_id"),
                "amount": event_data.get("amount"),
            }
        elif action == "1":
            return {
                "action": "payment_succeeded",
                "click_trans_id": event_data.get("click_trans_id"),
                "amount": event_data.get("amount"),
            }
        return {"action": "ignored", "click_action": action}


class PaymentService:
    """Main payment service with universal adapter pattern"""

    def __init__(self, payment_repository: PaymentRepository):
        self.repository = payment_repository
        self.adapters: dict[str, PaymentGatewayAdapter] = {}
        self.default_provider = PaymentProvider.STRIPE

    def register_adapter(self, adapter: PaymentGatewayAdapter):
        """Register a payment gateway adapter"""
        self.adapters[adapter.provider_name] = adapter
        logger.info(f"Registered payment adapter: {adapter.provider_name}")

    def get_adapter(self, provider: str) -> PaymentGatewayAdapter:
        """Get adapter for a specific provider"""
        adapter = self.adapters.get(provider)
        if not adapter:
            raise ValueError(f"Payment provider '{provider}' not supported")
        return adapter

    async def create_payment_method(
        self, user_id: int, payment_method_data: PaymentMethodCreate, provider: str = None
    ) -> PaymentMethodResponse:
        """Create payment method with specified provider"""
        provider = provider or self.default_provider
        adapter = self.get_adapter(provider)
        try:
            provider_response = await adapter.create_payment_method(
                user_id, payment_method_data.provider_data
            )
            expires_at = None
            if provider == PaymentProvider.STRIPE and "card" in provider_response:
                card = provider_response["card"]
                expires_at = datetime(
                    year=card.get("exp_year", 2025), month=card.get("exp_month", 12), day=1
                )
            method_id = await self.repository.create_payment_method(
                user_id=user_id,
                provider=provider,
                provider_method_id=provider_response["id"],
                method_type=payment_method_data.method_type,
                last_four=payment_method_data.last_four,
                brand=payment_method_data.brand,
                expires_at=expires_at,
                is_default=payment_method_data.is_default,
                metadata={"provider_response": provider_response, **payment_method_data.metadata},
            )
            return PaymentMethodResponse(
                id=method_id,
                provider=provider,
                method_type=payment_method_data.method_type,
                last_four=payment_method_data.last_four,
                brand=payment_method_data.brand,
                expires_at=expires_at,
                is_default=payment_method_data.is_default,
                is_active=True,
                created_at=datetime.utcnow(),
            )
        except Exception as e:
            logger.error(f"Failed to create payment method: {e}")
            raise

    async def get_user_payment_methods(self, user_id: int) -> list[PaymentMethodResponse]:
        """Get user's payment methods"""
        methods = await self.repository.get_user_payment_methods(user_id)
        return [
            PaymentMethodResponse(
                id=method["id"],
                provider=method["provider"],
                method_type=method["method_type"],
                last_four=method["last_four"],
                brand=method["brand"],
                expires_at=method["expires_at"],
                is_default=method["is_default"],
                is_active=method["is_active"],
                created_at=method["created_at"],
            )
            for method in methods
        ]

    async def process_payment(
        self, user_id: int, payment_data: PaymentCreate, idempotency_key: (str | None) = None
    ) -> PaymentResponse:
        """Process a one-time payment"""
        idempotency_key = idempotency_key or str(uuid4())
        existing_payment = await self.repository.get_payment_by_idempotency_key(idempotency_key)
        if existing_payment:
            return PaymentResponse(**existing_payment)
        payment_method = await self.repository.get_payment_method(payment_data.payment_method_id)
        if not payment_method:
            raise ValueError("Payment method not found")
        provider = payment_method["provider"]
        adapter = self.get_adapter(provider)
        try:
            payment_id = await self.repository.create_payment(
                user_id=user_id,
                subscription_id=payment_data.subscription_id,
                payment_method_id=payment_data.payment_method_id,
                provider=provider,
                provider_payment_id=None,
                idempotency_key=idempotency_key,
                amount=payment_data.amount,
                currency=payment_data.currency,
                status=PaymentStatus.PENDING,
                description=payment_data.description,
                metadata=payment_data.metadata,
            )
            provider_response = await adapter.charge_payment_method(
                method_id=payment_method["provider_method_id"],
                amount=payment_data.amount,
                currency=payment_data.currency,
                description=payment_data.description,
                metadata=payment_data.metadata,
            )
            status = (
                PaymentStatus.SUCCEEDED
                if provider_response.get("status") == "succeeded"
                else PaymentStatus.FAILED
            )
            await self.repository.update_payment_status(
                payment_id=payment_id,
                status=status,
                provider_payment_id=provider_response.get("id"),
            )
            payment = await self.repository.get_payment(payment_id)
            return PaymentResponse(**payment)
        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            if "payment_id" in locals():
                await self.repository.update_payment_status(
                    payment_id=payment_id, status=PaymentStatus.FAILED, failure_message=str(e)
                )
            raise

    async def create_subscription(
        self, user_id: int, subscription_data: SubscriptionCreate
    ) -> SubscriptionResponse:
        """Create a subscription"""
        plan = await self.repository.get_plan_with_pricing(subscription_data.plan_id)
        if not plan:
            raise ValueError("Plan not found")
        if subscription_data.billing_cycle == BillingCycle.MONTHLY:
            amount = plan["price_monthly"]
            period_days = 30
        else:
            amount = plan["price_yearly"]
            period_days = 365
        now = datetime.utcnow()
        current_period_start = now
        current_period_end = now + timedelta(days=period_days)
        trial_ends_at = None
        if subscription_data.trial_days and subscription_data.trial_days > 0:
            trial_ends_at = now + timedelta(days=subscription_data.trial_days)
            current_period_end = trial_ends_at + timedelta(days=period_days)
        subscription_id = await self.repository.create_subscription(
            user_id=user_id,
            plan_id=subscription_data.plan_id,
            payment_method_id=subscription_data.payment_method_id,
            provider_subscription_id=None,
            billing_cycle=subscription_data.billing_cycle.value,
            amount=amount,
            currency="USD",
            current_period_start=current_period_start,
            current_period_end=current_period_end,
            trial_ends_at=trial_ends_at,
            metadata=subscription_data.metadata,
        )
        if subscription_data.payment_method_id:
            payment_method = await self.repository.get_payment_method(
                subscription_data.payment_method_id
            )
            if payment_method:
                provider = payment_method["provider"]
                adapter = self.get_adapter(provider)
                try:
                    await adapter.create_subscription(
                        customer_id=str(user_id),
                        payment_method_id=payment_method["provider_method_id"],
                        plan_id=str(subscription_data.plan_id),
                        billing_cycle=subscription_data.billing_cycle,
                        trial_days=subscription_data.trial_days,
                    )
                    await self.repository.update_subscription_status(
                        subscription_id=subscription_id, status=SubscriptionStatus.ACTIVE
                    )
                except Exception as e:
                    logger.error(f"Provider subscription creation failed: {e}")
        subscription = await self.repository.get_user_active_subscription(user_id)
        return SubscriptionResponse(
            id=subscription["id"],
            user_id=subscription["user_id"],
            plan_id=subscription["plan_id"],
            plan_name=subscription["plan_name"],
            status=SubscriptionStatus(subscription["status"]),
            billing_cycle=BillingCycle(subscription["billing_cycle"]),
            amount=subscription["amount"],
            currency=subscription["currency"],
            current_period_start=subscription["current_period_start"],
            current_period_end=subscription["current_period_end"],
            trial_ends_at=subscription["trial_ends_at"],
            created_at=subscription["created_at"],
        )

    async def handle_webhook(
        self, provider: str, payload: bytes, signature: str, webhook_secret: str
    ) -> dict[str, Any]:
        """Handle webhook from payment provider"""
        adapter = self.get_adapter(provider)
        if not adapter.verify_webhook_signature(payload, signature, webhook_secret):
            logger.warning(f"Invalid webhook signature from {provider}")
            raise ValueError("Invalid webhook signature")
        try:
            event_data = json.loads(payload.decode())
            event_id = await self.repository.create_webhook_event(
                provider=provider,
                event_type=event_data.get("type") or event_data.get("method") or "unknown",
                provider_event_id=event_data.get("id"),
                object_id=event_data.get("data", {}).get("object", {}).get("id"),
                payload=event_data,
                signature=signature,
            )
            result = await adapter.handle_webhook_event(event_data)
            if result.get("action") != "ignored":
                await self.repository.mark_webhook_processed(event_id, True)
            return result
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            if "event_id" in locals():
                await self.repository.mark_webhook_processed(event_id, False, str(e))
            raise
