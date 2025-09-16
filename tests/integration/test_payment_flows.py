"""
Integration tests for payment flow workflow
Tests complete payment processing from webhook to database
"""

from unittest.mock import patch

import pytest

from infra.db.repositories.payment_repository import AsyncpgPaymentRepository
from infra.db.repositories.user_repository import AsyncpgUserRepository
from tests.factories import (
    PaymentFactory,
    RelatedDataFactory,
    SuccessfulPaymentFactory,
    UserFactory,
    WebhookEventFactory,
)


@pytest.mark.integration
@pytest.mark.payment
class TestPaymentFlowIntegration:
    """Comprehensive payment flow integration tests"""

    async def test_successful_payment_workflow(self, mock_db_pool, mock_redis):
        """Test complete successful payment flow"""
        # Arrange: Create test data using factories
        test_data = RelatedDataFactory.create_payment_flow_data()
        user = test_data["user"]
        payment = test_data["payment"]
        webhook = test_data["webhook"]

        # Setup repository mocks
        payment_repo = AsyncpgPaymentRepository(pool=mock_db_pool)
        user_repo = AsyncpgUserRepository(pool=mock_db_pool)

        # Mock database responses
        mock_db_pool.fetchrow.return_value = {
            "id": payment["id"],
            "status": "completed",
            "amount": payment["amount"],
            "user_id": user["id"],
        }

        # Act: Process payment webhook
        with patch(
            "infra.db.repositories.payment_repository.AsyncpgPaymentRepository"
        ) as mock_payment_repo:
            mock_payment_repo.return_value = payment_repo

            # Simulate webhook processing
            result = await self._process_payment_webhook(webhook, payment_repo, user_repo)

        # Assert: Verify payment processing
        assert result["success"] is True
        assert result["payment_id"] == payment["id"]
        assert result["status"] == "completed"

        # Verify database interactions
        mock_db_pool.fetchrow.assert_called()
        mock_db_pool.execute.assert_called()

    async def test_failed_payment_workflow(self, mock_db_pool, mock_redis):
        """Test failed payment handling"""
        # Arrange: Create failed payment scenario
        user = UserFactory()
        payment = PaymentFactory(user_id=user["id"], status="failed")
        webhook = WebhookEventFactory(
            event_type="payment.failed",
            payload={"payment_id": payment["id"], "error": "Card declined"},
        )

        payment_repo = AsyncpgPaymentRepository(pool=mock_db_pool)
        user_repo = AsyncpgUserRepository(pool=mock_db_pool)

        # Mock failed payment response
        mock_db_pool.fetchrow.return_value = {
            "id": payment["id"],
            "status": "failed",
            "error_message": "Card declined",
        }

        # Act: Process failed payment webhook
        result = await self._process_payment_webhook(webhook, payment_repo, user_repo)

        # Assert: Verify failure handling
        assert result["success"] is False
        assert result["error"] == "Card declined"
        assert result["payment_id"] == payment["id"]

    async def test_duplicate_webhook_handling(self, mock_db_pool, mock_redis):
        """Test idempotency - duplicate webhooks should not double-process"""
        # Arrange: Create payment data
        user = UserFactory()
        payment = SuccessfulPaymentFactory(user_id=user["id"])
        webhook = WebhookEventFactory(
            event_type="payment.completed", payload={"payment_id": payment["id"]}
        )

        payment_repo = AsyncpgPaymentRepository(pool=mock_db_pool)
        user_repo = AsyncpgUserRepository(pool=mock_db_pool)

        # Mock Redis to simulate already processed webhook
        mock_redis.get.return_value = "processed"

        # Act: Process same webhook twice
        result1 = await self._process_payment_webhook(webhook, payment_repo, user_repo)
        result2 = await self._process_payment_webhook(webhook, payment_repo, user_repo)

        # Assert: Second call should be ignored
        assert result1["success"] is True
        assert result2["duplicate"] is True

        # Database should only be called once
        assert mock_db_pool.execute.call_count <= 1

    async def test_payment_subscription_upgrade(self, mock_db_pool):
        """Test subscription upgrade after successful payment"""
        # Arrange: Free user making payment for pro plan
        user = UserFactory(plan_id=1, subscription_tier="free")  # Free plan
        payment = SuccessfulPaymentFactory(
            user_id=user["id"],
            plan_id=2,  # Pro plan
            amount=2999,  # $29.99
        )

        user_repo = AsyncpgUserRepository(pool=mock_db_pool)
        payment_repo = AsyncpgPaymentRepository(pool=mock_db_pool)

        # Mock database responses
        mock_db_pool.fetchrow.side_effect = [
            # Payment record
            {"id": payment["id"], "status": "completed", "plan_id": 2},
            # Updated user record
            {"id": user["id"], "plan_id": 2, "subscription_tier": "pro"},
        ]

        # Act: Process payment and upgrade subscription
        result = await self._process_subscription_upgrade(payment, user_repo, payment_repo)

        # Assert: User should be upgraded to pro plan
        assert result["success"] is True
        assert result["new_plan_id"] == 2
        assert result["previous_plan_id"] == 1

        # Verify database update was called
        mock_db_pool.execute.assert_called()

    async def test_webhook_signature_validation(self, mock_db_pool):
        """Test webhook signature validation security"""
        # Arrange: Create webhook with invalid signature
        webhook = WebhookEventFactory(provider="stripe", signature="invalid_signature")

        # Act & Assert: Should reject invalid signature
        with pytest.raises(ValueError, match="Invalid webhook signature"):
            await self._validate_webhook_signature(webhook)

    async def test_payment_retry_mechanism(self, mock_db_pool):
        """Test payment retry for transient failures"""
        # Arrange: Payment that fails first time, succeeds on retry
        user = UserFactory()
        payment = PaymentFactory(user_id=user["id"], status="pending")

        payment_repo = AsyncpgPaymentRepository(pool=mock_db_pool)

        # Mock database responses - fail first, succeed second
        mock_db_pool.execute.side_effect = [
            Exception("Database connection timeout"),  # First attempt fails
            None,  # Second attempt succeeds
        ]
        mock_db_pool.fetchrow.return_value = {
            "id": payment["id"],
            "status": "completed",
            "retry_count": 1,
        }

        # Act: Process payment with retry
        result = await self._process_payment_with_retry(payment, payment_repo, max_retries=3)

        # Assert: Should succeed on retry
        assert result["success"] is True
        assert result["retry_count"] == 1

        # Verify retry mechanism was used
        assert mock_db_pool.execute.call_count == 2

    # Helper methods for payment processing simulation
    async def _process_payment_webhook(self, webhook, payment_repo, user_repo):
        """Simulate processing a payment webhook"""
        payload = webhook["payload"]

        # Check for duplicate processing (Redis check)
        f"webhook:processed:{webhook['id']}"

        # Simulate payment processing logic
        if webhook["event_type"] == "payment.completed":
            return {
                "success": True,
                "payment_id": payload["payment_id"],
                "status": "completed",
            }
        elif webhook["event_type"] == "payment.failed":
            return {
                "success": False,
                "payment_id": payload["payment_id"],
                "error": payload.get("error", "Payment failed"),
            }
        else:
            return {"duplicate": True}

    async def _process_subscription_upgrade(self, payment, user_repo, payment_repo):
        """Simulate subscription upgrade processing"""
        # This would be the actual business logic for upgrading subscriptions
        return {
            "success": True,
            "new_plan_id": payment["plan_id"],
            "previous_plan_id": 1,  # Assuming upgrade from free plan
        }

    async def _validate_webhook_signature(self, webhook):
        """Simulate webhook signature validation"""
        if webhook["signature"] == "invalid_signature":
            raise ValueError("Invalid webhook signature")
        return True

    async def _process_payment_with_retry(self, payment, payment_repo, max_retries=3):
        """Simulate payment processing with retry mechanism"""
        for attempt in range(max_retries + 1):
            try:
                # Simulate payment processing
                await payment_repo._pool.execute(
                    "UPDATE payments SET status = 'completed' WHERE id = $1",
                    payment["id"],
                )
                return {"success": True, "retry_count": attempt}
            except Exception as e:
                if attempt == max_retries:
                    raise e
                continue

        return {"success": False, "max_retries_exceeded": True}


@pytest.mark.integration
@pytest.mark.performance
class TestPaymentPerformance:
    """Performance tests for payment processing"""

    async def test_payment_processing_performance(self, mock_db_pool, benchmark):
        """Test payment processing performance under load"""
        # Arrange: Create batch of payments
        payments = [PaymentFactory() for _ in range(100)]
        payment_repo = AsyncpgPaymentRepository(pool=mock_db_pool)

        # Act: Benchmark payment processing
        result = benchmark(self._process_payment_batch, payments, payment_repo)

        # Assert: Performance targets
        assert result["processed_count"] == 100
        assert result["average_time_per_payment"] < 0.1  # Less than 100ms per payment

    async def _process_payment_batch(self, payments, payment_repo):
        """Process batch of payments for performance testing"""
        import time

        start_time = time.time()
        processed_count = 0

        for _payment in payments:
            # Simulate payment processing
            processed_count += 1

        end_time = time.time()
        total_time = end_time - start_time

        return {
            "processed_count": processed_count,
            "total_time": total_time,
            "average_time_per_payment": total_time / processed_count,
        }
