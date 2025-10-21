"""
Unit Tests for Subscription Service
===================================

Tests subscription management, lifecycle, and billing cycles.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, Mock

from core.domain.payment import Money, SubscriptionData, SubscriptionStatus
from core.protocols.payment.payment_protocols import SubscriptionResult
from infra.services.payment import SubscriptionService


@pytest.fixture
def mock_payment_repository():
    """Mock payment repository"""
    repo = AsyncMock()
    repo.create_subscription = AsyncMock()
    repo.get_subscription = AsyncMock()
    repo.update_subscription = AsyncMock()
    repo.cancel_subscription = AsyncMock()
    repo.get_user_subscriptions = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def subscription_service(mock_payment_repository):
    """Create subscription service with mocked dependencies"""
    return SubscriptionService(payment_repository=mock_payment_repository)


@pytest.fixture
def sample_subscription_data():
    """Sample subscription data for testing"""
    return SubscriptionData(
        user_id=123,
        plan_id="premium_monthly",
        payment_method_id=1,
        start_date=datetime.now(),
        metadata={"test": True},
    )


class TestSubscriptionService:
    """Test suite for SubscriptionService"""

    @pytest.mark.asyncio
    async def test_create_subscription_success(
        self, subscription_service, mock_payment_repository, sample_subscription_data
    ):
        """Test successful subscription creation"""
        # Arrange
        subscription_record = {
            "id": 1,
            "user_id": 123,
            "plan_id": "premium_monthly",
            "status": SubscriptionStatus.ACTIVE,
            "current_period_start": datetime.now(),
            "current_period_end": datetime.now() + timedelta(days=30),
            "cancel_at_period_end": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        mock_payment_repository.create_subscription.return_value = subscription_record

        # Act
        result = await subscription_service.create_subscription(sample_subscription_data)

        # Assert
        assert isinstance(result, SubscriptionResult)
        assert result.success is True
        assert result.subscription is not None
        assert result.subscription.status == SubscriptionStatus.ACTIVE
        mock_payment_repository.create_subscription.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_subscription_prevents_duplicate_active(
        self, subscription_service, mock_payment_repository, sample_subscription_data
    ):
        """Test preventing duplicate active subscriptions"""
        # Arrange
        existing_subscription = {
            "id": 1,
            "user_id": 123,
            "plan_id": "premium_monthly",
            "status": SubscriptionStatus.ACTIVE,
            "current_period_start": datetime.now(),
            "current_period_end": datetime.now() + timedelta(days=30),
            "cancel_at_period_end": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        mock_payment_repository.get_user_subscriptions.return_value = [existing_subscription]

        # Act
        result = await subscription_service.create_subscription(sample_subscription_data)

        # Assert
        assert result.success is False
        assert "already has an active subscription" in result.error_message.lower()
        # Should not create new subscription
        mock_payment_repository.create_subscription.assert_not_called()

    @pytest.mark.asyncio
    async def test_cancel_subscription_immediate(
        self, subscription_service, mock_payment_repository
    ):
        """Test immediate subscription cancellation"""
        # Arrange
        subscription_id = 1
        subscription_record = {
            "id": subscription_id,
            "user_id": 123,
            "plan_id": "premium_monthly",
            "status": SubscriptionStatus.ACTIVE,
            "current_period_start": datetime.now(),
            "current_period_end": datetime.now() + timedelta(days=15),
            "cancel_at_period_end": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        mock_payment_repository.get_subscription.return_value = subscription_record
        mock_payment_repository.cancel_subscription.return_value = {
            **subscription_record,
            "status": SubscriptionStatus.CANCELED,
        }

        # Act
        result = await subscription_service.cancel_subscription(
            subscription_id=subscription_id, cancel_immediately=True
        )

        # Assert
        assert result["success"] is True
        assert result["subscription"]["status"] == SubscriptionStatus.CANCELED
        mock_payment_repository.cancel_subscription.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_subscription_at_period_end(
        self, subscription_service, mock_payment_repository
    ):
        """Test cancellation at end of billing period"""
        # Arrange
        subscription_id = 1
        subscription_record = {
            "id": subscription_id,
            "user_id": 123,
            "plan_id": "premium_monthly",
            "status": SubscriptionStatus.ACTIVE,
            "current_period_start": datetime.now(),
            "current_period_end": datetime.now() + timedelta(days=15),
            "cancel_at_period_end": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        mock_payment_repository.get_subscription.return_value = subscription_record
        mock_payment_repository.update_subscription.return_value = {
            **subscription_record,
            "cancel_at_period_end": True,
        }

        # Act
        result = await subscription_service.cancel_subscription(
            subscription_id=subscription_id, cancel_immediately=False
        )

        # Assert
        assert result["success"] is True
        assert result["subscription"]["cancel_at_period_end"] is True
        # Status should still be ACTIVE until period ends
        assert result["subscription"]["status"] == SubscriptionStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_renew_subscription(self, subscription_service, mock_payment_repository):
        """Test subscription renewal"""
        # Arrange
        subscription_id = 1
        old_period_end = datetime.now()
        new_period_end = old_period_end + timedelta(days=30)

        subscription_record = {
            "id": subscription_id,
            "user_id": 123,
            "plan_id": "premium_monthly",
            "status": SubscriptionStatus.ACTIVE,
            "current_period_start": old_period_end - timedelta(days=30),
            "current_period_end": old_period_end,
            "cancel_at_period_end": False,
            "created_at": datetime.now() - timedelta(days=60),
            "updated_at": datetime.now(),
        }

        mock_payment_repository.get_subscription.return_value = subscription_record
        mock_payment_repository.update_subscription.return_value = {
            **subscription_record,
            "current_period_start": old_period_end,
            "current_period_end": new_period_end,
        }

        # Act
        result = await subscription_service.renew_subscription(subscription_id)

        # Assert
        assert result["success"] is True
        assert result["subscription"]["current_period_end"] == new_period_end
        mock_payment_repository.update_subscription.assert_called_once()

    @pytest.mark.asyncio
    async def test_upgrade_subscription(self, subscription_service, mock_payment_repository):
        """Test subscription plan upgrade"""
        # Arrange
        subscription_id = 1
        new_plan_id = "premium_yearly"

        subscription_record = {
            "id": subscription_id,
            "user_id": 123,
            "plan_id": "premium_monthly",
            "status": SubscriptionStatus.ACTIVE,
            "current_period_start": datetime.now(),
            "current_period_end": datetime.now() + timedelta(days=15),
            "cancel_at_period_end": False,
            "created_at": datetime.now() - timedelta(days=15),
            "updated_at": datetime.now(),
        }

        mock_payment_repository.get_subscription.return_value = subscription_record
        mock_payment_repository.update_subscription.return_value = {
            **subscription_record,
            "plan_id": new_plan_id,
        }

        # Act
        result = await subscription_service.upgrade_subscription(
            subscription_id=subscription_id, new_plan_id=new_plan_id
        )

        # Assert
        assert result["success"] is True
        assert result["subscription"]["plan_id"] == new_plan_id
        mock_payment_repository.update_subscription.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_subscription(self, subscription_service, mock_payment_repository):
        """Test retrieving subscription details"""
        # Arrange
        subscription_id = 1
        subscription_record = {
            "id": subscription_id,
            "user_id": 123,
            "plan_id": "premium_monthly",
            "status": SubscriptionStatus.ACTIVE,
            "current_period_start": datetime.now(),
            "current_period_end": datetime.now() + timedelta(days=15),
            "cancel_at_period_end": False,
            "created_at": datetime.now() - timedelta(days=15),
            "updated_at": datetime.now(),
        }

        mock_payment_repository.get_subscription.return_value = subscription_record

        # Act
        subscription = await subscription_service.get_subscription(subscription_id)

        # Assert
        assert subscription is not None
        assert subscription.id == subscription_id
        assert subscription.status == SubscriptionStatus.ACTIVE
        mock_payment_repository.get_subscription.assert_called_once_with(subscription_id)

    @pytest.mark.asyncio
    async def test_get_user_subscriptions(
        self, subscription_service, mock_payment_repository
    ):
        """Test retrieving all subscriptions for a user"""
        # Arrange
        user_id = 123
        subscriptions = [
            {
                "id": 1,
                "user_id": user_id,
                "plan_id": "premium_monthly",
                "status": SubscriptionStatus.ACTIVE,
                "current_period_start": datetime.now(),
                "current_period_end": datetime.now() + timedelta(days=15),
                "cancel_at_period_end": False,
                "created_at": datetime.now() - timedelta(days=15),
                "updated_at": datetime.now(),
            },
            {
                "id": 2,
                "user_id": user_id,
                "plan_id": "basic_monthly",
                "status": SubscriptionStatus.CANCELED,
                "current_period_start": datetime.now() - timedelta(days=60),
                "current_period_end": datetime.now() - timedelta(days=30),
                "cancel_at_period_end": True,
                "created_at": datetime.now() - timedelta(days=90),
                "updated_at": datetime.now() - timedelta(days=30),
            },
        ]

        mock_payment_repository.get_user_subscriptions.return_value = subscriptions

        # Act
        user_subs = await subscription_service.get_user_subscriptions(user_id)

        # Assert
        assert len(user_subs) == 2
        assert user_subs[0].status == SubscriptionStatus.ACTIVE
        assert user_subs[1].status == SubscriptionStatus.CANCELED

    @pytest.mark.asyncio
    async def test_check_subscription_status(
        self, subscription_service, mock_payment_repository
    ):
        """Test checking if subscription is active"""
        # Arrange
        subscription_id = 1
        subscription_record = {
            "id": subscription_id,
            "user_id": 123,
            "plan_id": "premium_monthly",
            "status": SubscriptionStatus.ACTIVE,
            "current_period_start": datetime.now(),
            "current_period_end": datetime.now() + timedelta(days=15),
            "cancel_at_period_end": False,
            "created_at": datetime.now() - timedelta(days=15),
            "updated_at": datetime.now(),
        }

        mock_payment_repository.get_subscription.return_value = subscription_record

        # Act
        is_active = await subscription_service.is_subscription_active(subscription_id)

        # Assert
        assert is_active is True

    @pytest.mark.asyncio
    async def test_subscription_expired_status(
        self, subscription_service, mock_payment_repository
    ):
        """Test detecting expired subscriptions"""
        # Arrange
        subscription_id = 1
        subscription_record = {
            "id": subscription_id,
            "user_id": 123,
            "plan_id": "premium_monthly",
            "status": SubscriptionStatus.ACTIVE,
            "current_period_start": datetime.now() - timedelta(days=45),
            "current_period_end": datetime.now() - timedelta(days=15),  # Expired
            "cancel_at_period_end": False,
            "created_at": datetime.now() - timedelta(days=60),
            "updated_at": datetime.now() - timedelta(days=15),
        }

        mock_payment_repository.get_subscription.return_value = subscription_record

        # Act
        is_active = await subscription_service.is_subscription_active(subscription_id)

        # Assert
        # Should be False because period has ended
        assert is_active is False


class TestSubscriptionEdgeCases:
    """Test edge cases for subscription management"""

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_subscription(
        self, subscription_service, mock_payment_repository
    ):
        """Test canceling a subscription that doesn't exist"""
        # Arrange
        subscription_id = 999
        mock_payment_repository.get_subscription.return_value = None

        # Act
        result = await subscription_service.cancel_subscription(subscription_id)

        # Assert
        assert result["success"] is False
        assert "not found" in result["error_message"].lower()

    @pytest.mark.asyncio
    async def test_cancel_already_canceled_subscription(
        self, subscription_service, mock_payment_repository
    ):
        """Test canceling an already canceled subscription"""
        # Arrange
        subscription_id = 1
        subscription_record = {
            "id": subscription_id,
            "user_id": 123,
            "plan_id": "premium_monthly",
            "status": SubscriptionStatus.CANCELED,
            "current_period_start": datetime.now() - timedelta(days=30),
            "current_period_end": datetime.now(),
            "cancel_at_period_end": True,
            "created_at": datetime.now() - timedelta(days=60),
            "updated_at": datetime.now(),
        }

        mock_payment_repository.get_subscription.return_value = subscription_record

        # Act
        result = await subscription_service.cancel_subscription(subscription_id)

        # Assert
        assert result["success"] is False
        assert "already canceled" in result["error_message"].lower()

    @pytest.mark.asyncio
    async def test_renew_canceled_subscription(
        self, subscription_service, mock_payment_repository
    ):
        """Test attempting to renew a canceled subscription"""
        # Arrange
        subscription_id = 1
        subscription_record = {
            "id": subscription_id,
            "user_id": 123,
            "plan_id": "premium_monthly",
            "status": SubscriptionStatus.CANCELED,
            "current_period_start": datetime.now() - timedelta(days=30),
            "current_period_end": datetime.now(),
            "cancel_at_period_end": True,
            "created_at": datetime.now() - timedelta(days=60),
            "updated_at": datetime.now(),
        }

        mock_payment_repository.get_subscription.return_value = subscription_record

        # Act
        result = await subscription_service.renew_subscription(subscription_id)

        # Assert
        assert result["success"] is False
        assert "cannot renew" in result["error_message"].lower()
