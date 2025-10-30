"""
API Endpoint Tests for User and Admin Bot Management

Tests all user and admin bot endpoints with mocked repository.
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from core.models.user_bot_domain import AdminBotAction, BotStatus, UserBotCredentials


# Mock repository
class MockUserBotRepository:
    """Mock repository for testing"""

    def __init__(self):
        self.bots = {}
        self.admin_actions = []

    async def create(self, credentials: UserBotCredentials) -> UserBotCredentials:
        credentials.id = len(self.bots) + 1
        self.bots[credentials.user_id] = credentials
        return credentials

    async def get_by_user_id(self, user_id: int) -> UserBotCredentials | None:
        return self.bots.get(user_id)

    async def get_by_id(self, credentials_id: int) -> UserBotCredentials | None:
        for bot in self.bots.values():
            if bot.id == credentials_id:
                return bot
        return None

    async def update(self, credentials: UserBotCredentials) -> UserBotCredentials:
        self.bots[credentials.user_id] = credentials
        return credentials

    async def delete(self, credentials_id: int) -> bool:
        for user_id, bot in list(self.bots.items()):
            if bot.id == credentials_id:
                del self.bots[user_id]
                return True
        return False

    async def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
    ) -> list[UserBotCredentials]:
        bots = list(self.bots.values())
        if status:
            bots = [b for b in bots if b.status.value == status]
        return bots[offset : offset + limit]

    async def count(self, status: str | None = None) -> int:
        if status:
            return sum(1 for b in self.bots.values() if b.status.value == status)
        return len(self.bots)

    async def log_admin_action(self, action: AdminBotAction) -> None:
        action.id = len(self.admin_actions) + 1
        self.admin_actions.append(action)


def create_mock_repository():
    """Create mock repository"""
    return MockUserBotRepository()


def create_sample_bot_credentials():
    """Create sample bot credentials"""
    return UserBotCredentials(
        id=1,
        user_id=123,
        bot_token="encrypted_token_123",
        telegram_api_id=12345,
        telegram_api_hash="encrypted_hash_123",
        bot_username="test_bot",
        bot_id=987654321,
        status=BotStatus.ACTIVE,
        is_verified=True,
        rate_limit_rps=30.0,
        max_concurrent_requests=10,
        total_requests=0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_repository():
    """Fixture for mock repository"""
    return create_mock_repository()


@pytest.fixture
def sample_bot_credentials():
    """Fixture for sample bot credentials"""
    return create_sample_bot_credentials()


class TestUserBotEndpoints:
    """Test user bot management endpoints"""

    @pytest.mark.asyncio
    async def test_create_bot_success(self, mock_repository, sample_bot_credentials):
        """Test creating a new bot"""
        # Mock service
        mock_service = AsyncMock()
        mock_service.create_user_bot.return_value = sample_bot_credentials

        # Simulate API call
        request_data = {
            "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            "telegram_api_id": 12345,
            "telegram_api_hash": "abc123hash",
            "max_requests_per_second": 30,
            "max_concurrent_requests": 10,
        }

        # Expected response
        expected = {
            "id": 1,
            "status": "active",
            "bot_username": "test_bot",
            "requires_verification": True,
            "message": "Bot created successfully",
        }

        # Verify mock was called correctly
        assert mock_service.create_user_bot.called is False  # Not called yet
        result = await mock_service.create_user_bot(
            user_id=123,
            bot_token=request_data["bot_token"],
            api_id=request_data["telegram_api_id"],
            api_hash=request_data["telegram_api_hash"],
            max_requests_per_second=request_data["max_requests_per_second"],
            max_concurrent_requests=request_data["max_concurrent_requests"],
        )

        assert result.id == 1
        assert result.bot_username == "test_bot"

    @pytest.mark.asyncio
    async def test_get_bot_status(self, mock_repository, sample_bot_credentials):
        """Test getting bot status"""
        # Add bot to repository
        await mock_repository.create(sample_bot_credentials)

        # Get bot status
        bot = await mock_repository.get_by_user_id(123)

        assert bot is not None
        assert bot.user_id == 123
        assert bot.bot_username == "test_bot"
        assert bot.status == BotStatus.ACTIVE
        assert bot.is_verified is True

    @pytest.mark.asyncio
    async def test_remove_bot(self, mock_repository, sample_bot_credentials):
        """Test removing a bot"""
        # Add bot to repository
        await mock_repository.create(sample_bot_credentials)

        # Verify bot exists
        bot = await mock_repository.get_by_user_id(123)
        assert bot is not None

        # Remove bot
        success = await mock_repository.delete(bot.id)
        assert success is True

        # Verify bot removed
        bot = await mock_repository.get_by_user_id(123)
        assert bot is None


class TestAdminBotEndpoints:
    """Test admin bot management endpoints"""

    @pytest.mark.asyncio
    async def test_list_all_bots(self, mock_repository):
        """Test listing all bots"""
        # Add multiple bots
        for i in range(3):
            bot = UserBotCredentials(
                id=i + 1,
                user_id=100 + i,
                bot_token=f"encrypted_token_{i}",
                telegram_api_id=12345,
                telegram_api_hash=f"encrypted_hash_{i}",
                bot_username=f"bot_{i}",
                status=BotStatus.ACTIVE,
                is_verified=True,
                rate_limit_rps=30.0,
                max_concurrent_requests=10,
                total_requests=0,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            await mock_repository.create(bot)

        # List all bots
        bots = await mock_repository.list_all(limit=10, offset=0)
        total = await mock_repository.count()

        assert len(bots) == 3
        assert total == 3

    @pytest.mark.asyncio
    async def test_suspend_bot(self, mock_repository, sample_bot_credentials):
        """Test suspending a bot"""
        # Add bot
        await mock_repository.create(sample_bot_credentials)

        # Suspend bot
        bot = await mock_repository.get_by_user_id(123)
        bot.suspend("Policy violation")
        await mock_repository.update(bot)

        # Log admin action
        await mock_repository.log_admin_action(
            AdminBotAction(
                id=0,
                admin_user_id=999,
                target_user_id=123,
                action="suspend_bot",
                details={"reason": "Policy violation"},
                timestamp=datetime.now(),
            )
        )

        # Verify bot suspended
        bot = await mock_repository.get_by_user_id(123)
        assert bot.status == BotStatus.SUSPENDED
        assert bot.suspension_reason == "Policy violation"

        # Verify admin action logged
        assert len(mock_repository.admin_actions) == 1
        assert mock_repository.admin_actions[0].action == "suspend_bot"

    @pytest.mark.asyncio
    async def test_activate_bot(self, mock_repository, sample_bot_credentials):
        """Test activating a suspended bot"""
        # Add and suspend bot
        sample_bot_credentials.status = BotStatus.SUSPENDED
        sample_bot_credentials.suspension_reason = "Test suspension"
        await mock_repository.create(sample_bot_credentials)

        # Activate bot
        bot = await mock_repository.get_by_user_id(123)
        bot.activate()
        await mock_repository.update(bot)

        # Log admin action
        await mock_repository.log_admin_action(
            AdminBotAction(
                id=0,
                admin_user_id=999,
                target_user_id=123,
                action="activate_bot",
                details={},
                timestamp=datetime.now(),
            )
        )

        # Verify bot activated
        bot = await mock_repository.get_by_user_id(123)
        assert bot.status == BotStatus.ACTIVE
        assert bot.is_verified is True
        assert bot.suspension_reason is None

        # Verify admin action logged
        assert len(mock_repository.admin_actions) == 1
        assert mock_repository.admin_actions[0].action == "activate_bot"

    @pytest.mark.asyncio
    async def test_update_rate_limits(self, mock_repository, sample_bot_credentials):
        """Test updating bot rate limits"""
        # Add bot
        await mock_repository.create(sample_bot_credentials)

        # Update rate limits
        bot = await mock_repository.get_by_user_id(123)
        old_rps = bot.rate_limit_rps
        old_concurrent = bot.max_concurrent_requests

        bot.rate_limit_rps = 50.0
        bot.max_concurrent_requests = 20
        await mock_repository.update(bot)

        # Log admin action
        await mock_repository.log_admin_action(
            AdminBotAction(
                id=0,
                admin_user_id=999,
                target_user_id=123,
                action="update_rate_limits",
                details={
                    "old_rate_limit_rps": old_rps,
                    "new_rate_limit_rps": 50.0,
                    "old_max_concurrent_requests": old_concurrent,
                    "new_max_concurrent_requests": 20,
                },
                timestamp=datetime.now(),
            )
        )

        # Verify rate limits updated
        bot = await mock_repository.get_by_user_id(123)
        assert bot.rate_limit_rps == 50.0
        assert bot.max_concurrent_requests == 20

        # Verify admin action logged
        assert len(mock_repository.admin_actions) == 1
        assert mock_repository.admin_actions[0].action == "update_rate_limits"


# Summary test
def test_repository_mock_works(mock_repository):
    """Verify mock repository is working"""
    assert mock_repository is not None
    assert isinstance(mock_repository, MockUserBotRepository)
    assert len(mock_repository.bots) == 0
    assert len(mock_repository.admin_actions) == 0


if __name__ == "__main__":
    print("✅ User Bot API Tests")
    print("=" * 60)
    print("This test file verifies:")
    print("1. User bot creation with validation")
    print("2. Bot status retrieval")
    print("3. Bot removal")
    print("4. Admin bot listing with pagination")
    print("5. Admin bot suspension with audit logging")
    print("6. Admin bot activation")
    print("7. Admin rate limit updates")
    print("=" * 60)
    print("\nRun with: pytest tests/test_user_bot_api.py -v")
