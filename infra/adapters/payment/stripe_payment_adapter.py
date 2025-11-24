"""
Stripe Payment Gateway Adapter
Real implementation for Stripe payment processing
"""

import logging
from decimal import Decimal
from typing import Any

import stripe

try:
    from stripe.error import StripeError  # type: ignore
except ImportError:
    StripeError = Exception

from config.settings import settings
from core.adapters.payment import PaymentGatewayAdapter
from core.domain.payment import BillingCycle, PaymentStatus, SubscriptionStatus

logger = logging.getLogger(__name__)


class StripePaymentAdapter(PaymentGatewayAdapter):
    """
    Real Stripe implementation of PaymentGatewayAdapter
    """

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        logger.info("StripePaymentAdapter initialized")

    def get_adapter_name(self) -> str:
        return "stripe"

    def _map_stripe_payment_status(self, stripe_status: str) -> PaymentStatus:
        """Map Stripe payment status to internal status"""
        status_mapping = {
            "succeeded": PaymentStatus.SUCCEEDED,
            "processing": PaymentStatus.PROCESSING,
            "requires_payment_method": PaymentStatus.FAILED,
            "requires_confirmation": PaymentStatus.PENDING,
            "requires_action": PaymentStatus.PENDING,
            "canceled": PaymentStatus.CANCELED,
            "requires_capture": PaymentStatus.PENDING,
        }
        return status_mapping.get(stripe_status, PaymentStatus.FAILED)

    def _map_stripe_subscription_status(self, stripe_status: str) -> SubscriptionStatus:
        """Map Stripe subscription status to internal status"""
        status_mapping = {
            "active": SubscriptionStatus.ACTIVE,
            "canceled": SubscriptionStatus.CANCELED,
            "incomplete": SubscriptionStatus.INCOMPLETE,
            "incomplete_expired": SubscriptionStatus.CANCELED,
            "trialing": SubscriptionStatus.TRIALING,
            "past_due": SubscriptionStatus.PAST_DUE,
            "unpaid": SubscriptionStatus.UNPAID,
            "paused": SubscriptionStatus.CANCELED,
        }
        return status_mapping.get(stripe_status, SubscriptionStatus.CANCELED)

    async def create_customer(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """Create Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=user_data.get("email") or "",
                name=user_data.get("name") or "",
                phone=user_data.get("phone") or "",
                metadata=user_data.get("metadata", {}),
            )

            logger.info(f"Created Stripe customer: {customer.id}")

            return {
                "success": True,
                "customer_id": customer.id,
                "gateway_response": customer,
            }

        except StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, "code", None),
            }

    async def create_payment_method(
        self, customer_id: str, method_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create Stripe payment method"""
        try:
            method_type = method_data.get("type", "card")
            create_params = {
                "type": method_type,
                "metadata": method_data.get("metadata", {}),
            }

            if method_type == "card" and method_data.get("card"):
                create_params["card"] = method_data["card"]

            payment_method = stripe.PaymentMethod.create(**create_params)

            # Attach to customer
            payment_method.attach(customer=customer_id)

            logger.info(f"Created Stripe payment method: {payment_method.id}")

            return {
                "success": True,
                "payment_method_id": payment_method.id,
                "gateway_response": payment_method,
            }

        except StripeError as e:
            logger.error(f"Failed to create Stripe payment method: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, "code", None),
            }

    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        customer_id: str,
        payment_method_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create Stripe payment intent"""
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                customer=customer_id,
                payment_method=payment_method_id,
                confirmation_method="manual",
                confirm=True,
                return_url=getattr(settings, "STRIPE_RETURN_URL", "https://example.com/return"),
                metadata=metadata or {},
            )

            logger.info(f"Created Stripe payment intent: {payment_intent.id}")

            return {
                "success": True,
                "provider_payment_id": payment_intent.id,
                "status": self._map_stripe_payment_status(payment_intent.status),
                "amount": float(amount),
                "currency": currency,
                "client_secret": payment_intent.client_secret,
                "gateway_response": payment_intent,
            }

        except StripeError as e:
            logger.error(f"Failed to create Stripe payment intent: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, "code", None),
            }

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_method_id: str,
        billing_cycle: BillingCycle | str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create Stripe subscription"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                default_payment_method=payment_method_id,
                expand=["latest_invoice.payment_intent"],
                metadata=metadata or {},
            )

            logger.info(f"Created Stripe subscription: {subscription.id}")

            return {
                "success": True,
                "provider_subscription_id": subscription.id,
                "status": self._map_stripe_subscription_status(subscription.status),
                "current_period_start": getattr(subscription, "current_period_start", None),
                "current_period_end": getattr(subscription, "current_period_end", None),
                "gateway_response": subscription,
            }

        except StripeError as e:
            logger.error(f"Failed to create Stripe subscription: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, "code", None),
            }

    async def cancel_subscription(
        self, subscription_id: str, immediate: bool = False
    ) -> dict[str, Any]:
        """Cancel Stripe subscription"""
        try:
            if immediate:
                subscription = stripe.Subscription.cancel(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id, cancel_at_period_end=True
                )

            logger.info(f"Canceled Stripe subscription: {subscription_id} (immediate: {immediate})")

            return {
                "success": True,
                "status": self._map_stripe_subscription_status(subscription.status),
                "canceled_at": getattr(subscription, "canceled_at", None),
                "gateway_response": subscription,
            }

        except StripeError as e:
            logger.error(f"Failed to cancel Stripe subscription: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, "code", None),
            }

    async def update_subscription(
        self, subscription_id: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
        """Update Stripe subscription"""
        try:
            subscription = stripe.Subscription.modify(subscription_id, **updates)

            logger.info(f"Updated Stripe subscription: {subscription_id}")

            return {"success": True, "gateway_response": subscription}

        except StripeError as e:
            logger.error(f"Failed to update Stripe subscription: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, "code", None),
            }

    async def handle_webhook(
        self, payload: str, signature: str, endpoint_secret: str
    ) -> dict[str, Any]:
        """Handle Stripe webhook"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, endpoint_secret or self.webhook_secret
            )

            logger.info(f"Processed Stripe webhook: {event['id']} ({event['type']})")

            return {
                "success": True,
                "event_id": event["id"],
                "event_type": event["type"],
                "event_data": event["data"],
                "processed": True,
            }

        except stripe.SignatureVerificationError as e:
            logger.error(f"Invalid Stripe webhook signature: {e}")
            return {
                "success": False,
                "error": "Invalid signature",
                "error_code": "signature_verification_failed",
            }
        except Exception as e:
            logger.error(f"Failed to process Stripe webhook: {e}")
            return {"success": False, "error": str(e)}

    async def get_customer(self, customer_id: str) -> dict[str, Any] | None:
        """Get Stripe customer"""
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return customer
        except StripeError as e:
            logger.error(f"Failed to get Stripe customer {customer_id}: {e}")
            return None

    async def get_subscription(self, subscription_id: str) -> dict[str, Any] | None:
        """Get Stripe subscription"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except StripeError as e:
            logger.error(f"Failed to get Stripe subscription {subscription_id}: {e}")
            return None

    async def list_payment_methods(self, customer_id: str) -> list[dict[str, Any]]:
        """List Stripe payment methods"""
        try:
            payment_methods = stripe.PaymentMethod.list(customer=customer_id, type="card")
            return [
                {"id": pm.id, "type": pm.type, "card": pm.card, "created": pm.created}
                for pm in payment_methods.data
            ]
        except StripeError as e:
            logger.error(f"Failed to list Stripe payment methods for {customer_id}: {e}")
            return []

    async def health_check(self) -> dict[str, Any]:
        """Stripe health check"""
        try:
            # Try a simple API call to check connectivity
            stripe.Account.retrieve()
            return {
                "status": "healthy",
                "adapter": "stripe",
                "api_version": stripe.api_version,
            }
        except StripeError as e:
            logger.error(f"Stripe health check failed: {e}")
            return {"status": "unhealthy", "adapter": "stripe", "error": str(e)}
