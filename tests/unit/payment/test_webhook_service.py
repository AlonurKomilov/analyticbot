"""
Unit Tests for Webhook Service
==============================

Tests webhook event processing, validation, and handling for payment providers.
"""

import hashlib
import hmac
import json
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from core.protocols.payment.payment_protocols import PaymentEventType, WebhookEvent
from infra.services.payment import WebhookService


@pytest.fixture
def mock_payment_repository():
    """Mock payment repository"""
    repo = AsyncMock()
    repo.log_webhook_event = AsyncMock()
    repo.get_payment_by_provider_id = AsyncMock()
    repo.update_payment_status = AsyncMock()
    repo.get_subscription_by_provider_id = AsyncMock()
    repo.update_subscription = AsyncMock()
    return repo


@pytest.fixture
def webhook_service(mock_payment_repository):
    """Create webhook service with mocked dependencies"""
    return WebhookService(payment_repository=mock_payment_repository)


@pytest.fixture
def sample_webhook_payload():
    """Sample webhook payload"""
    return {
        "id": "evt_test123",
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_test123",
                "amount": 1999,
                "currency": "usd",
                "status": "succeeded",
                "metadata": {
                    "user_id": "123",
                },
            }
        },
        "created": int(datetime.now().timestamp()),
    }


class TestWebhookService:
    """Test suite for WebhookService"""

    @pytest.mark.asyncio
    async def test_validate_webhook_signature_success(
        self, webhook_service, sample_webhook_payload
    ):
        """Test successful webhook signature validation"""
        # Arrange
        secret = "whsec_test_secret"
        payload_str = json.dumps(sample_webhook_payload)
        timestamp = str(int(datetime.now().timestamp()))

        # Create signature
        signed_payload = f"{timestamp}.{payload_str}"
        signature = hmac.new(
            secret.encode("utf-8"),
            signed_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # Act
        is_valid = webhook_service.validate_webhook_signature(
            payload=payload_str,
            signature=f"t={timestamp},v1={signature}",
            secret=secret,
        )

        # Assert
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_webhook_signature_invalid(
        self, webhook_service, sample_webhook_payload
    ):
        """Test webhook signature validation fails with wrong signature"""
        # Arrange
        secret = "whsec_test_secret"
        payload_str = json.dumps(sample_webhook_payload)
        timestamp = str(int(datetime.now().timestamp()))
        wrong_signature = "wrong_signature"

        # Act
        is_valid = webhook_service.validate_webhook_signature(
            payload=payload_str,
            signature=f"t={timestamp},v1={wrong_signature}",
            secret=secret,
        )

        # Assert
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_process_payment_succeeded_webhook(
        self, webhook_service, mock_payment_repository, sample_webhook_payload
    ):
        """Test processing payment succeeded webhook"""
        # Arrange
        payment_record = {
            "id": 1,
            "provider_payment_id": "pi_test123",
            "status": "processing",
        }
        mock_payment_repository.get_payment_by_provider_id.return_value = payment_record

        webhook_event = WebhookEvent(
            event_id="evt_test123",
            event_type=PaymentEventType.PAYMENT_SUCCEEDED,
            provider="stripe",
            payload=sample_webhook_payload,
            timestamp=datetime.now(),
        )

        # Act
        result = await webhook_service.process_webhook(webhook_event)

        # Assert
        assert result["success"] is True
        # Verify payment status was updated
        mock_payment_repository.update_payment_status.assert_called_once()
        # Verify webhook event was logged
        mock_payment_repository.log_webhook_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_payment_failed_webhook(
        self, webhook_service, mock_payment_repository
    ):
        """Test processing payment failed webhook"""
        # Arrange
        payment_record = {
            "id": 1,
            "provider_payment_id": "pi_test123",
            "status": "processing",
        }
        mock_payment_repository.get_payment_by_provider_id.return_value = payment_record

        webhook_payload = {
            "id": "evt_test123",
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "id": "pi_test123",
                    "amount": 1999,
                    "currency": "usd",
                    "status": "failed",
                    "last_payment_error": {
                        "message": "Card declined",
                    },
                }
            },
        }

        webhook_event = WebhookEvent(
            event_id="evt_test123",
            event_type=PaymentEventType.PAYMENT_FAILED,
            provider="stripe",
            payload=webhook_payload,
            timestamp=datetime.now(),
        )

        # Act
        result = await webhook_service.process_webhook(webhook_event)

        # Assert
        assert result["success"] is True
        # Verify payment status was updated to failed
        mock_payment_repository.update_payment_status.assert_called_once()
        call_args = mock_payment_repository.update_payment_status.call_args
        assert "failed" in str(call_args).lower()

    @pytest.mark.asyncio
    async def test_process_subscription_created_webhook(
        self, webhook_service, mock_payment_repository
    ):
        """Test processing subscription created webhook"""
        # Arrange
        webhook_payload = {
            "id": "evt_test123",
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "customer": "cus_test123",
                    "status": "active",
                    "current_period_start": int(datetime.now().timestamp()),
                    "current_period_end": int(datetime.now().timestamp()) + 30*24*60*60,
                }
            },
        }

        webhook_event = WebhookEvent(
            event_id="evt_test123",
            event_type=PaymentEventType.SUBSCRIPTION_CREATED,
            provider="stripe",
            payload=webhook_payload,
            timestamp=datetime.now(),
        )

        # Act
        result = await webhook_service.process_webhook(webhook_event)

        # Assert
        assert result["success"] is True
        mock_payment_repository.log_webhook_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_subscription_canceled_webhook(
        self, webhook_service, mock_payment_repository
    ):
        """Test processing subscription canceled webhook"""
        # Arrange
        subscription_record = {
            "id": 1,
            "provider_subscription_id": "sub_test123",
            "status": "active",
        }
        mock_payment_repository.get_subscription_by_provider_id.return_value = subscription_record

        webhook_payload = {
            "id": "evt_test123",
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "customer": "cus_test123",
                    "status": "canceled",
                }
            },
        }

        webhook_event = WebhookEvent(
            event_id="evt_test123",
            event_type=PaymentEventType.SUBSCRIPTION_CANCELED,
            provider="stripe",
            payload=webhook_payload,
            timestamp=datetime.now(),
        )

        # Act
        result = await webhook_service.process_webhook(webhook_event)

        # Assert
        assert result["success"] is True
        # Verify subscription was updated to canceled
        mock_payment_repository.update_subscription.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_refund_created_webhook(
        self, webhook_service, mock_payment_repository
    ):
        """Test processing refund created webhook"""
        # Arrange
        payment_record = {
            "id": 1,
            "provider_payment_id": "pi_test123",
            "status": "succeeded",
        }
        mock_payment_repository.get_payment_by_provider_id.return_value = payment_record

        webhook_payload = {
            "id": "evt_test123",
            "type": "charge.refunded",
            "data": {
                "object": {
                    "id": "ch_test123",
                    "payment_intent": "pi_test123",
                    "amount_refunded": 1999,
                    "refunded": True,
                }
            },
        }

        webhook_event = WebhookEvent(
            event_id="evt_test123",
            event_type=PaymentEventType.REFUND_CREATED,
            provider="stripe",
            payload=webhook_payload,
            timestamp=datetime.now(),
        )

        # Act
        result = await webhook_service.process_webhook(webhook_event)

        # Assert
        assert result["success"] is True
        mock_payment_repository.update_payment_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_webhook_payment_not_found(
        self, webhook_service, mock_payment_repository, sample_webhook_payload
    ):
        """Test processing webhook when payment not found in database"""
        # Arrange
        mock_payment_repository.get_payment_by_provider_id.return_value = None

        webhook_event = WebhookEvent(
            event_id="evt_test123",
            event_type=PaymentEventType.PAYMENT_SUCCEEDED,
            provider="stripe",
            payload=sample_webhook_payload,
            timestamp=datetime.now(),
        )

        # Act
        result = await webhook_service.process_webhook(webhook_event)

        # Assert
        # Should still log webhook even if payment not found
        assert result["success"] is True
        mock_payment_repository.log_webhook_event.assert_called_once()
        # But should not try to update non-existent payment
        mock_payment_repository.update_payment_status.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_duplicate_webhook(
        self, webhook_service, mock_payment_repository, sample_webhook_payload
    ):
        """Test handling duplicate webhook events (idempotency)"""
        # Arrange
        # Simulate webhook already processed
        mock_payment_repository.log_webhook_event.side_effect = [
            Exception("Duplicate webhook event"),  # First call (duplicate)
            None,  # Should not reach second call
        ]

        webhook_event = WebhookEvent(
            event_id="evt_test123",
            event_type=PaymentEventType.PAYMENT_SUCCEEDED,
            provider="stripe",
            payload=sample_webhook_payload,
            timestamp=datetime.now(),
        )

        # Act
        result = await webhook_service.process_webhook(webhook_event)

        # Assert
        # Should handle duplicate gracefully
        assert result is not None
        mock_payment_repository.log_webhook_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_unknown_event_type(
        self, webhook_service, mock_payment_repository
    ):
        """Test processing unknown webhook event type"""
        # Arrange
        webhook_payload = {
            "id": "evt_test123",
            "type": "unknown.event.type",
            "data": {"object": {}},
        }

        webhook_event = WebhookEvent(
            event_id="evt_test123",
            event_type="unknown",  # Unknown type
            provider="stripe",
            payload=webhook_payload,
            timestamp=datetime.now(),
        )

        # Act
        result = await webhook_service.process_webhook(webhook_event)

        # Assert
        # Should log but not crash
        assert result["success"] is True
        mock_payment_repository.log_webhook_event.assert_called_once()


class TestWebhookEdgeCases:
    """Test edge cases for webhook processing"""

    @pytest.mark.asyncio
    async def test_webhook_with_invalid_payload_format(
        self, webhook_service, mock_payment_repository
    ):
        """Test handling webhooks with malformed payload"""
        # Arrange
        invalid_payload = {"invalid": "structure"}  # Missing required fields

        webhook_event = WebhookEvent(
            event_id="evt_test123",
            event_type=PaymentEventType.PAYMENT_SUCCEEDED,
            provider="stripe",
            payload=invalid_payload,
            timestamp=datetime.now(),
        )

        # Act
        result = await webhook_service.process_webhook(webhook_event)

        # Assert
        # Should handle gracefully without crashing
        assert result is not None

    @pytest.mark.asyncio
    async def test_webhook_processing_with_database_error(
        self, webhook_service, mock_payment_repository, sample_webhook_payload
    ):
        """Test webhook processing when database operations fail"""
        # Arrange
        mock_payment_repository.log_webhook_event.side_effect = Exception("Database error")

        webhook_event = WebhookEvent(
            event_id="evt_test123",
            event_type=PaymentEventType.PAYMENT_SUCCEEDED,
            provider="stripe",
            payload=sample_webhook_payload,
            timestamp=datetime.now(),
        )

        # Act/Assert
        # Should raise exception to allow webhook retry
        with pytest.raises(Exception):
            await webhook_service.process_webhook(webhook_event)

    @pytest.mark.asyncio
    async def test_webhook_timestamp_validation(
        self, webhook_service, sample_webhook_payload
    ):
        """Test webhook timestamp validation for replay attack prevention"""
        # Arrange
        secret = "whsec_test_secret"
        payload_str = json.dumps(sample_webhook_payload)
        # Old timestamp (over 5 minutes ago)
        old_timestamp = str(int(datetime.now().timestamp()) - 400)

        signed_payload = f"{old_timestamp}.{payload_str}"
        signature = hmac.new(
            secret.encode("utf-8"),
            signed_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # Act
        is_valid = webhook_service.validate_webhook_signature(
            payload=payload_str,
            signature=f"t={old_timestamp},v1={signature}",
            secret=secret,
            tolerance_seconds=300,  # 5 minute tolerance
        )

        # Assert
        # Should reject due to old timestamp
        assert is_valid is False
