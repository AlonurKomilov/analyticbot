"""
Webhook Processing Microservice
===============================

Focused microservice for webhook handling and event processing.
Manages webhook verification, processing, and event coordination.

Single Responsibility: Webhook and event processing only.
"""

import json
import logging
from typing import Any

from apps.bot.services.adapters.payment_adapter_factory import PaymentAdapterFactory

from ..protocols.payment_protocols import (
    PaymentEventType,
    WebhookEvent,
    WebhookProtocol,
)

logger = logging.getLogger(__name__)


class WebhookService(WebhookProtocol):
    """
    Webhook processing microservice.

    Responsibilities:
    - Verify webhook signatures from payment providers
    - Parse and validate webhook payloads
    - Route events to appropriate handlers
    - Manage webhook event history and retry logic
    - Coordinate with other services for event processing
    """

    def __init__(
        self, payment_repository, payment_processing_service=None, subscription_service=None
    ):
        self.repository = payment_repository
        self.payment_processing_service = payment_processing_service
        self.subscription_service = subscription_service
        self.payment_adapter = PaymentAdapterFactory.get_current_adapter()

        # Webhook secrets by provider
        self.webhook_secrets = {
            "stripe": "whsec_test_secret",
            "payme": "payme_webhook_secret",
            "click": "click_webhook_secret",
        }

        logger.info("🔗 WebhookService initialized")

    async def process_webhook(
        self, provider: str, payload: bytes, signature: str
    ) -> dict[str, Any]:
        """
        Process incoming webhook from payment provider.

        Args:
            provider: Payment provider name
            payload: Raw webhook payload
            signature: Webhook signature for verification

        Returns:
            Processing result with action taken
        """
        try:
            logger.info(f"🔗 Processing webhook from {provider}")

            # Step 1: Verify webhook signature
            is_valid_signature = await self.verify_webhook_signature(provider, payload, signature)
            if not is_valid_signature:
                logger.warning(f"❌ Invalid webhook signature from {provider}")
                return {
                    "success": False,
                    "error": "Invalid webhook signature",
                    "provider": provider,
                }

            # Step 2: Parse webhook payload
            try:
                event_data = json.loads(payload.decode())
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON payload from {provider}: {e}")
                return {"success": False, "error": "Invalid JSON payload", "provider": provider}

            # Step 3: Create webhook event record
            event_id = await self._create_webhook_event(provider, event_data, signature)

            # Step 4: Process webhook event
            try:
                processing_result = await self._process_webhook_event(event_data, provider)

                # Mark event as processed
                await self.repository.mark_webhook_processed(event_id, True)

                logger.info(
                    f"✅ Webhook processed successfully from {provider}: {processing_result.get('action')}"
                )
                return {
                    "success": True,
                    "event_id": event_id,
                    "action": processing_result.get("action", "processed"),
                    "result": processing_result,
                    "provider": provider,
                }

            except Exception as processing_error:
                logger.error(f"❌ Webhook processing failed: {processing_error}")

                # Mark event as failed
                await self.repository.mark_webhook_processed(event_id, False, str(processing_error))

                return {
                    "success": False,
                    "event_id": event_id,
                    "error": str(processing_error),
                    "provider": provider,
                }

        except Exception as e:
            logger.error(f"❌ Webhook processing error for {provider}: {e}")
            return {"success": False, "error": str(e), "provider": provider}

    async def verify_webhook_signature(self, provider: str, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature authenticity.

        Args:
            provider: Payment provider name
            payload: Raw webhook payload
            signature: Webhook signature

        Returns:
            True if signature is valid
        """
        try:
            webhook_secret = self.webhook_secrets.get(provider.lower())
            if not webhook_secret:
                logger.error(f"❌ No webhook secret configured for provider: {provider}")
                return False

            # Use adapter's signature verification - fallback to local verification
            # since the base adapter doesn't have verify_webhook_signature method
            return await self._verify_signature_fallback(
                provider, payload, signature, webhook_secret
            )

        except Exception as e:
            logger.error(f"❌ Signature verification failed for {provider}: {e}")
            return False

    async def handle_payment_event(self, event: WebhookEvent) -> dict[str, Any]:
        """
        Handle payment-related webhook events.

        Args:
            event: Webhook event to process

        Returns:
            Processing result
        """
        try:
            logger.info(f"🔗 Handling payment event: {event.event_type}")

            if event.event_type == PaymentEventType.PAYMENT_SUCCEEDED:
                return await self._handle_payment_succeeded(event)
            elif event.event_type == PaymentEventType.PAYMENT_FAILED:
                return await self._handle_payment_failed(event)
            elif event.event_type == PaymentEventType.PAYMENT_PENDING:
                return await self._handle_payment_pending(event)
            elif event.event_type == PaymentEventType.PAYMENT_CANCELED:
                return await self._handle_payment_canceled(event)
            else:
                logger.info(f"🔗 Unhandled payment event type: {event.event_type}")
                return {"action": "ignored", "reason": f"Unhandled event type: {event.event_type}"}

        except Exception as e:
            logger.error(f"❌ Payment event handling failed: {e}")
            return {"action": "failed", "error": str(e)}

    async def handle_subscription_event(self, event: WebhookEvent) -> dict[str, Any]:
        """
        Handle subscription-related webhook events.

        Args:
            event: Webhook event to process

        Returns:
            Processing result
        """
        try:
            logger.info(f"🔗 Handling subscription event: {event.event_type}")

            if event.event_type == PaymentEventType.SUBSCRIPTION_CREATED:
                return await self._handle_subscription_created(event)
            elif event.event_type == PaymentEventType.SUBSCRIPTION_UPDATED:
                return await self._handle_subscription_updated(event)
            elif event.event_type == PaymentEventType.SUBSCRIPTION_CANCELED:
                return await self._handle_subscription_canceled(event)
            elif event.event_type == PaymentEventType.SUBSCRIPTION_RENEWED:
                return await self._handle_subscription_renewed(event)
            else:
                logger.info(f"🔗 Unhandled subscription event type: {event.event_type}")
                return {"action": "ignored", "reason": f"Unhandled event type: {event.event_type}"}

        except Exception as e:
            logger.error(f"❌ Subscription event handling failed: {e}")
            return {"action": "failed", "error": str(e)}

    async def get_webhook_events(
        self, provider: str | None = None, limit: int = 100
    ) -> list[WebhookEvent]:
        """
        Get webhook event history.

        Args:
            provider: Optional provider filter
            limit: Maximum number of events to return

        Returns:
            List of webhook events
        """
        try:
            events = await self.repository.get_webhook_events(provider, limit)
            return [
                WebhookEvent(
                    event_id=event["id"],
                    provider=event["provider"],
                    event_type=PaymentEventType(event["event_type"]),
                    object_id=event["object_id"],
                    payload=event["payload"],
                    signature=event["signature"],
                    created_at=event["created_at"],
                    processed_at=event.get("processed_at"),
                    processing_result=event.get("processing_result"),
                )
                for event in events
            ]
        except Exception as e:
            logger.error(f"❌ Failed to get webhook events: {e}")
            return []

    async def retry_webhook_processing(self, event_id: str) -> dict[str, Any]:
        """
        Retry processing of a failed webhook event.

        Args:
            event_id: Webhook event identifier

        Returns:
            Retry processing result
        """
        try:
            logger.info(f"🔗 Retrying webhook processing: {event_id}")

            # Get original webhook event
            event_data = await self.repository.get_webhook_event(event_id)
            if not event_data:
                return {"success": False, "error": "Webhook event not found"}

            # Retry processing
            processing_result = await self._process_webhook_event(
                event_data["payload"], event_data["provider"]
            )

            # Update event status
            await self.repository.mark_webhook_processed(event_id, True, processing_result)

            logger.info(f"✅ Webhook retry successful: {event_id}")
            return {"success": True, "event_id": event_id, "result": processing_result}

        except Exception as e:
            logger.error(f"❌ Webhook retry failed: {event_id}, error: {e}")
            await self.repository.mark_webhook_processed(event_id, False, str(e))
            return {"success": False, "event_id": event_id, "error": str(e)}

    async def _create_webhook_event(
        self, provider: str, event_data: dict[str, Any], signature: str
    ) -> str:
        """Create webhook event record in repository."""
        return await self.repository.create_webhook_event(
            provider=provider,
            event_type=self._extract_event_type(event_data, provider),
            provider_event_id=event_data.get("id"),
            object_id=self._extract_object_id(event_data, provider),
            payload=event_data,
            signature=signature,
        )

    async def _process_webhook_event(
        self, event_data: dict[str, Any], provider: str
    ) -> dict[str, Any]:
        """Process webhook event based on provider and event type."""
        # Use adapter's event processing if available
        if hasattr(self.payment_adapter, "handle_webhook"):
            # Convert event_data back to string for adapter
            payload_str = __import__("json").dumps(event_data)
            return await self.payment_adapter.handle_webhook(payload_str, "", "")
        else:
            # Fallback processing logic
            return await self._process_event_fallback(event_data, provider)

    async def _process_event_fallback(
        self, event_data: dict[str, Any], provider: str
    ) -> dict[str, Any]:
        """Fallback event processing when adapter doesn't support it."""
        if provider.lower() == "stripe":
            return await self._process_stripe_event(event_data)
        elif provider.lower() == "payme":
            return await self._process_payme_event(event_data)
        elif provider.lower() == "click":
            return await self._process_click_event(event_data)
        else:
            return {"action": "ignored", "reason": f"Unsupported provider: {provider}"}

    async def _process_stripe_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Process Stripe webhook events."""
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

    async def _process_payme_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Process Payme webhook events."""
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

    async def _process_click_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Process Click webhook events."""
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

    async def _verify_signature_fallback(
        self, provider: str, payload: bytes, signature: str, secret: str
    ) -> bool:
        """Fallback signature verification."""
        import hashlib
        import hmac

        try:
            if provider.lower() == "stripe":
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

            else:
                # Generic HMAC verification
                expected_signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
                return hmac.compare_digest(expected_signature, signature)

        except Exception as e:
            logger.error(f"❌ Fallback signature verification failed: {e}")
            return False

    def _extract_event_type(self, event_data: dict[str, Any], provider: str) -> str:
        """Extract event type from webhook payload."""
        if provider.lower() == "stripe":
            return event_data.get("type", "unknown")
        elif provider.lower() == "payme":
            return event_data.get("method", "unknown")
        elif provider.lower() == "click":
            return f"click_action_{event_data.get('action', 'unknown')}"
        else:
            return "unknown"

    def _extract_object_id(self, event_data: dict[str, Any], provider: str) -> str:
        """Extract object ID from webhook payload."""
        if provider.lower() == "stripe":
            return event_data.get("data", {}).get("object", {}).get("id", "")
        elif provider.lower() == "payme":
            return event_data.get("params", {}).get("id", "")
        elif provider.lower() == "click":
            return event_data.get("click_trans_id", "")
        else:
            return ""

    # Event handlers
    async def _handle_payment_succeeded(self, event: WebhookEvent) -> dict[str, Any]:
        """Handle successful payment events."""
        # Update payment status if payment processing service is available
        if self.payment_processing_service:
            payment_id = event.object_id
            # Additional processing logic here

        return {"action": "payment_succeeded", "object_id": event.object_id}

    async def _handle_payment_failed(self, event: WebhookEvent) -> dict[str, Any]:
        """Handle failed payment events."""
        return {"action": "payment_failed", "object_id": event.object_id}

    async def _handle_payment_pending(self, event: WebhookEvent) -> dict[str, Any]:
        """Handle pending payment events."""
        return {"action": "payment_pending", "object_id": event.object_id}

    async def _handle_payment_canceled(self, event: WebhookEvent) -> dict[str, Any]:
        """Handle canceled payment events."""
        return {"action": "payment_canceled", "object_id": event.object_id}

    async def _handle_subscription_created(self, event: WebhookEvent) -> dict[str, Any]:
        """Handle subscription creation events."""
        return {"action": "subscription_created", "object_id": event.object_id}

    async def _handle_subscription_updated(self, event: WebhookEvent) -> dict[str, Any]:
        """Handle subscription update events."""
        return {"action": "subscription_updated", "object_id": event.object_id}

    async def _handle_subscription_canceled(self, event: WebhookEvent) -> dict[str, Any]:
        """Handle subscription cancellation events."""
        return {"action": "subscription_canceled", "object_id": event.object_id}

    async def _handle_subscription_renewed(self, event: WebhookEvent) -> dict[str, Any]:
        """Handle subscription renewal events."""
        return {"action": "subscription_renewed", "object_id": event.object_id}

    async def health_check(self) -> dict[str, Any]:
        """Health check for webhook service."""
        try:
            # Test repository connection
            test_events = await self.repository.get_webhook_events(None, 1)

            # Check webhook secret configuration
            configured_providers = list(self.webhook_secrets.keys())

            return {
                "service": "WebhookService",
                "status": "healthy",
                "repository_connected": True,
                "configured_providers": configured_providers,
                "adapter_name": self.payment_adapter.get_adapter_name(),
            }
        except Exception as e:
            return {"service": "WebhookService", "status": "unhealthy", "error": str(e)}
