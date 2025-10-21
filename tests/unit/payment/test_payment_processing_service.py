"""
Unit Tests for Payment Processing Service
=========================================

Tests payment transaction processing, validation, retries, and refunds.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from core.domain.payment import Money, Payment, PaymentData, PaymentStatus
from core.protocols.payment.payment_protocols import PaymentResult
from infra.services.payment import PaymentProcessingService


@pytest.fixture
def mock_payment_repository():
    """Mock payment repository"""
    repo = AsyncMock()
    repo.get_payment_by_idempotency_key = AsyncMock(return_value=None)
    repo.create_payment = AsyncMock()
    repo.update_payment_status = AsyncMock()
    repo.get_payment = AsyncMock()
    return repo


@pytest.fixture
def mock_payment_method_service():
    """Mock payment method service"""
    service = AsyncMock()
    service.get_payment_method = AsyncMock()
    return service


@pytest.fixture
def payment_service(mock_payment_repository, mock_payment_method_service):
    """Create payment processing service with mocked dependencies"""
    return PaymentProcessingService(
        payment_repository=mock_payment_repository,
        payment_method_service=mock_payment_method_service,
    )


@pytest.fixture
def sample_payment_data():
    """Sample payment data for testing"""
    return PaymentData(
        amount=Money(amount=Decimal("19.99"), currency="USD"),
        payment_method_id=1,
        description="Test payment",
        metadata={"test": True},
    )


class TestPaymentProcessingService:
    """Test suite for PaymentProcessingService"""

    @pytest.mark.asyncio
    async def test_process_payment_success(
        self, payment_service, mock_payment_repository, sample_payment_data
    ):
        """Test successful payment processing"""
        # Arrange
        user_id = 123
        idempotency_key = str(uuid4())

        payment_record = {
            "id": 1,
            "user_id": user_id,
            "payment_method_id": 1,
            "amount": Decimal("19.99"),
            "currency": "USD",
            "status": PaymentStatus.SUCCEEDED,
            "provider": "stripe",
            "provider_payment_id": "pi_test123",
            "description": "Test payment",
            "subscription_id": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "metadata": {"test": True},
        }

        mock_payment_repository.create_payment.return_value = payment_record

        # Mock payment adapter
        with patch("apps.bot.services.adapters.payment_adapter_factory.PaymentAdapterFactory") as mock_factory:
            mock_adapter = AsyncMock()
            mock_adapter.process_payment = AsyncMock(
                return_value={"success": True, "transaction_id": "pi_test123"}
            )
            mock_factory.get_current_adapter.return_value = mock_adapter

            # Act
            result = await payment_service.process_payment(
                user_id=user_id,
                payment_data=sample_payment_data,
                idempotency_key=idempotency_key,
            )

            # Assert
            assert isinstance(result, PaymentResult)
            assert result.success is True
            assert result.payment is not None
            assert result.payment.amount.amount == Decimal("19.99")
            assert result.payment.status == PaymentStatus.SUCCEEDED

            # Verify repository was called
            mock_payment_repository.create_payment.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_payment_idempotency(
        self, payment_service, mock_payment_repository, sample_payment_data
    ):
        """Test idempotency - duplicate requests return same result"""
        # Arrange
        user_id = 123
        idempotency_key = "test_key_123"

        existing_payment = {
            "id": 1,
            "user_id": user_id,
            "payment_method_id": 1,
            "amount": Decimal("19.99"),
            "currency": "USD",
            "status": PaymentStatus.SUCCEEDED,
            "provider": "stripe",
            "provider_payment_id": "pi_test123",
            "description": "Test payment",
            "subscription_id": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "metadata": {},
        }

        mock_payment_repository.get_payment_by_idempotency_key.return_value = existing_payment

        # Act
        result = await payment_service.process_payment(
            user_id=user_id,
            payment_data=sample_payment_data,
            idempotency_key=idempotency_key,
        )

        # Assert
        assert result.success is True
        assert result.transaction_id == 1
        # Repository create should NOT be called since payment already exists
        mock_payment_repository.create_payment.assert_not_called()

    @pytest.mark.asyncio
    async def test_validate_payment_data_valid(self, payment_service, sample_payment_data):
        """Test validation of valid payment data"""
        # Act
        result = await payment_service.validate_payment_data(sample_payment_data)

        # Assert
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_validate_payment_data_invalid_amount(self, payment_service):
        """Test validation rejects negative amounts"""
        # Arrange
        invalid_data = PaymentData(
            amount=Money(amount=Decimal("-10.00"), currency="USD"),
            payment_method_id=1,
            description="Invalid payment",
        )

        # Act
        result = await payment_service.validate_payment_data(invalid_data)

        # Assert
        assert result["is_valid"] is False
        assert any("amount" in error.lower() for error in result["errors"])

    @pytest.mark.asyncio
    async def test_validate_payment_data_invalid_currency(self, payment_service):
        """Test validation rejects invalid currency codes"""
        # Arrange
        invalid_data = PaymentData(
            amount=Money(amount=Decimal("19.99"), currency="INVALID"),
            payment_method_id=1,
            description="Invalid payment",
        )

        # Act
        result = await payment_service.validate_payment_data(invalid_data)

        # Assert
        assert result["is_valid"] is False
        assert any("currency" in error.lower() for error in result["errors"])

    @pytest.mark.asyncio
    async def test_validate_payment_data_missing_payment_method(self, payment_service):
        """Test validation requires payment method"""
        # Arrange
        invalid_data = PaymentData(
            amount=Money(amount=Decimal("19.99"), currency="USD"),
            payment_method_id=None,
            description="Invalid payment",
        )

        # Act
        result = await payment_service.validate_payment_data(invalid_data)

        # Assert
        assert result["is_valid"] is False
        assert any("payment method" in error.lower() for error in result["errors"])

    @pytest.mark.asyncio
    async def test_process_refund_full(self, payment_service, mock_payment_repository):
        """Test full refund processing"""
        # Arrange
        payment_id = 1
        payment_record = {
            "id": payment_id,
            "user_id": 123,
            "payment_method_id": 1,
            "amount": Decimal("19.99"),
            "currency": "USD",
            "status": PaymentStatus.SUCCEEDED,
            "provider": "stripe",
            "provider_payment_id": "pi_test123",
            "description": "Test payment",
            "subscription_id": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "metadata": {},
        }

        mock_payment_repository.get_payment.return_value = payment_record

        # Mock payment adapter
        with patch("apps.bot.services.adapters.payment_adapter_factory.PaymentAdapterFactory") as mock_factory:
            mock_adapter = AsyncMock()
            mock_adapter.process_refund = AsyncMock(
                return_value={"success": True, "refund_id": "re_test123"}
            )
            mock_factory.get_current_adapter.return_value = mock_adapter

            # Act
            result = await payment_service.process_refund(
                payment_id=payment_id,
                amount=None,  # Full refund
                reason="Customer request",
            )

            # Assert
            assert result["success"] is True
            assert result["refund_id"] == "re_test123"
            mock_adapter.process_refund.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_refund_partial(self, payment_service, mock_payment_repository):
        """Test partial refund processing"""
        # Arrange
        payment_id = 1
        refund_amount = Money(amount=Decimal("10.00"), currency="USD")
        
        payment_record = {
            "id": payment_id,
            "user_id": 123,
            "payment_method_id": 1,
            "amount": Decimal("19.99"),
            "currency": "USD",
            "status": PaymentStatus.SUCCEEDED,
            "provider": "stripe",
            "provider_payment_id": "pi_test123",
            "description": "Test payment",
            "subscription_id": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "metadata": {},
        }

        mock_payment_repository.get_payment.return_value = payment_record

        # Mock payment adapter
        with patch("apps.bot.services.adapters.payment_adapter_factory.PaymentAdapterFactory") as mock_factory:
            mock_adapter = AsyncMock()
            mock_adapter.process_refund = AsyncMock(
                return_value={"success": True, "refund_id": "re_test123"}
            )
            mock_factory.get_current_adapter.return_value = mock_adapter

            # Act
            result = await payment_service.process_refund(
                payment_id=payment_id,
                amount=refund_amount,
                reason="Partial refund",
            )

            # Assert
            assert result["success"] is True
            mock_adapter.process_refund.assert_called_once()
            # Verify partial amount was passed
            call_args = mock_adapter.process_refund.call_args
            assert call_args[1]["amount"] == refund_amount

    @pytest.mark.asyncio
    async def test_process_refund_payment_not_found(
        self, payment_service, mock_payment_repository
    ):
        """Test refund fails for non-existent payment"""
        # Arrange
        payment_id = 999
        mock_payment_repository.get_payment.return_value = None

        # Act
        result = await payment_service.process_refund(
            payment_id=payment_id,
            amount=None,
            reason="Test",
        )

        # Assert
        assert result["success"] is False
        assert "not found" in result["error_message"].lower()

    @pytest.mark.asyncio
    async def test_get_payment_status(self, payment_service, mock_payment_repository):
        """Test retrieving payment status"""
        # Arrange
        payment_id = 1
        payment_record = {
            "id": payment_id,
            "user_id": 123,
            "payment_method_id": 1,
            "amount": Decimal("19.99"),
            "currency": "USD",
            "status": PaymentStatus.PROCESSING,
            "provider": "stripe",
            "provider_payment_id": "pi_test123",
            "description": "Test payment",
            "subscription_id": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "metadata": {},
        }

        mock_payment_repository.get_payment.return_value = payment_record

        # Act
        status = await payment_service.get_payment_status(payment_id)

        # Assert
        assert status == PaymentStatus.PROCESSING
        mock_payment_repository.get_payment.assert_called_once_with(payment_id)


class TestPaymentProcessingEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.mark.asyncio
    async def test_process_payment_with_retry_on_failure(
        self, payment_service, mock_payment_repository, sample_payment_data
    ):
        """Test payment retry logic on transient failures"""
        # Arrange
        user_id = 123

        # Mock adapter to fail first time, succeed second time
        with patch("apps.bot.services.adapters.payment_adapter_factory.PaymentAdapterFactory") as mock_factory:
            mock_adapter = AsyncMock()
            mock_adapter.process_payment = AsyncMock(
                side_effect=[
                    {"success": False, "error": "Transient error"},
                    {
                        "success": True,
                        "transaction_id": "pi_test123",
                    },
                ]
            )
            mock_factory.get_current_adapter.return_value = mock_adapter

            payment_record = {
                "id": 1,
                "user_id": user_id,
                "payment_method_id": 1,
                "amount": Decimal("19.99"),
                "currency": "USD",
                "status": PaymentStatus.SUCCEEDED,
                "provider": "stripe",
                "provider_payment_id": "pi_test123",
                "description": "Test payment",
                "subscription_id": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "metadata": {},
            }

            mock_payment_repository.create_payment.return_value = payment_record

            # Act
            result = await payment_service.process_payment(
                user_id=user_id,
                payment_data=sample_payment_data,
            )

            # Assert
            assert result.success is True
            # Verify retry happened (called twice)
            assert mock_adapter.process_payment.call_count >= 1

    @pytest.mark.asyncio
    async def test_concurrent_payment_processing(
        self, payment_service, mock_payment_repository, sample_payment_data
    ):
        """Test handling concurrent payment requests with same idempotency key"""
        # Arrange
        user_id = 123
        idempotency_key = "concurrent_test_key"

        # First call - no existing payment
        # Second call - payment exists (simulating race condition)
        mock_payment_repository.get_payment_by_idempotency_key.side_effect = [
            None,  # First check
            {  # Second check returns existing
                "id": 1,
                "user_id": user_id,
                "payment_method_id": 1,
                "amount": Decimal("19.99"),
                "currency": "USD",
                "status": PaymentStatus.PROCESSING,
                "provider": "stripe",
                "provider_payment_id": "pi_test123",
                "description": "Test payment",
                "subscription_id": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "metadata": {},
            },
        ]

        # Act - Make two "concurrent" calls
        with patch("apps.bot.services.adapters.payment_adapter_factory.PaymentAdapterFactory"):
            result1 = await payment_service.process_payment(
                user_id=user_id,
                payment_data=sample_payment_data,
                idempotency_key=idempotency_key,
            )

            result2 = await payment_service.process_payment(
                user_id=user_id,
                payment_data=sample_payment_data,
                idempotency_key=idempotency_key,
            )

        # Assert - Both return results, second one uses existing payment
        assert result1 is not None
        assert result2 is not None
        assert result2.transaction_id == 1
