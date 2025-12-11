"""
Simple API Tests for User and Admin Bot Management

Tests all user and admin bot endpoints with mocked repository.
Run with: python3 tests/test_user_bot_simple.py
"""

import asyncio
from datetime import datetime

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


def create_sample_bot(user_id: int = 123, username: str = "test_bot") -> UserBotCredentials:
    """Create sample bot credentials"""
    return UserBotCredentials(
        id=0,
        user_id=user_id,
        bot_token=f"encrypted_token_{user_id}",
        mtproto_api_id=12345,
        telegram_api_hash=f"encrypted_hash_{user_id}",
        bot_username=username,
        bot_id=987654321 + user_id,
        status=BotStatus.ACTIVE,
        is_verified=True,
        rate_limit_rps=30.0,
        max_concurrent_requests=10,
        total_requests=0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


async def test_create_and_get_bot():
    """Test: Create bot and retrieve it"""
    print("\n1️⃣ Test: Create and Get Bot")
    repo = MockUserBotRepository()

    # Create bot
    bot = create_sample_bot(user_id=123)
    created = await repo.create(bot)

    assert created.id == 1, "Bot ID should be 1"
    assert created.user_id == 123, "User ID should be 123"
    print(f"   ✅ Created bot ID={created.id} for user {created.user_id}")

    # Retrieve bot
    retrieved = await repo.get_by_user_id(123)
    assert retrieved is not None, "Bot should exist"
    assert retrieved.bot_username == "test_bot", "Username should match"
    print(f"   ✅ Retrieved bot @{retrieved.bot_username}")

    print("   ✅ Test passed!")


async def test_list_multiple_bots():
    """Test: List multiple bots with pagination"""
    print("\n2️⃣ Test: List Multiple Bots")
    repo = MockUserBotRepository()

    # Create 3 bots
    for i in range(3):
        bot = create_sample_bot(user_id=100 + i, username=f"bot_{i}")
        await repo.create(bot)

    # List all
    bots = await repo.list_all(limit=10, offset=0)
    total = await repo.count()

    assert len(bots) == 3, "Should have 3 bots"
    assert total == 3, "Total count should be 3"
    print(f"   ✅ Listed {len(bots)} bots (total: {total})")

    print("   ✅ Test passed!")


async def test_suspend_and_activate_bot():
    """Test: Suspend and activate bot"""
    print("\n3️⃣ Test: Suspend and Activate Bot")
    repo = MockUserBotRepository()

    # Create bot
    bot = create_sample_bot(user_id=123)
    created = await repo.create(bot)
    print(f"   ✅ Created bot with status: {created.status.value}")

    # Suspend bot
    bot_to_suspend = await repo.get_by_user_id(123)
    assert bot_to_suspend is not None, "Bot should exist"
    bot_to_suspend.suspend("Policy violation")
    await repo.update(bot_to_suspend)

    # Log admin action
    await repo.log_admin_action(
        AdminBotAction(
            id=0,
            admin_user_id=999,
            target_user_id=123,
            action="suspend_bot",
            details={"reason": "Policy violation"},
            timestamp=datetime.now(),
        )
    )

    # Verify suspended
    suspended_bot = await repo.get_by_user_id(123)
    assert suspended_bot is not None, "Bot should exist"
    assert suspended_bot.status == BotStatus.SUSPENDED, "Bot should be suspended"
    assert suspended_bot.suspension_reason == "Policy violation", "Reason should match"
    print(f"   ✅ Suspended bot: {suspended_bot.suspension_reason}")

    # Activate bot
    bot_to_activate = await repo.get_by_user_id(123)
    assert bot_to_activate is not None, "Bot should exist"
    bot_to_activate.activate()
    await repo.update(bot_to_activate)

    # Log admin action
    await repo.log_admin_action(
        AdminBotAction(
            id=0,
            admin_user_id=999,
            target_user_id=123,
            action="activate_bot",
            details={},
            timestamp=datetime.now(),
        )
    )

    # Verify activated
    activated_bot = await repo.get_by_user_id(123)
    assert activated_bot is not None, "Bot should exist"
    assert activated_bot.status == BotStatus.ACTIVE, "Bot should be active"
    assert activated_bot.is_verified is True, "Bot should be verified"
    assert activated_bot.suspension_reason is None, "Reason should be cleared"
    print(f"   ✅ Activated bot: status={activated_bot.status.value}")

    # Verify admin actions logged
    assert len(repo.admin_actions) == 2, "Should have 2 admin actions"
    print(f"   ✅ Logged {len(repo.admin_actions)} admin actions")

    print("   ✅ Test passed!")


async def test_update_rate_limits():
    """Test: Update bot rate limits"""
    print("\n4️⃣ Test: Update Rate Limits")
    repo = MockUserBotRepository()

    # Create bot
    bot = create_sample_bot(user_id=123)
    created = await repo.create(bot)
    print(
        f"   ✅ Initial rate limits: RPS={created.rate_limit_rps}, Concurrent={created.max_concurrent_requests}"
    )

    # Update rate limits
    bot_to_update = await repo.get_by_user_id(123)
    assert bot_to_update is not None, "Bot should exist"
    old_rps = bot_to_update.rate_limit_rps
    old_concurrent = bot_to_update.max_concurrent_requests

    bot_to_update.rate_limit_rps = 50.0
    bot_to_update.max_concurrent_requests = 20
    await repo.update(bot_to_update)

    # Log admin action
    await repo.log_admin_action(
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

    # Verify updated
    updated_bot = await repo.get_by_user_id(123)
    assert updated_bot is not None, "Bot should exist"
    assert updated_bot.rate_limit_rps == 50.0, "RPS should be 50"
    assert updated_bot.max_concurrent_requests == 20, "Concurrent should be 20"
    print(
        f"   ✅ Updated rate limits: RPS={updated_bot.rate_limit_rps}, Concurrent={updated_bot.max_concurrent_requests}"
    )

    # Verify admin action logged
    assert len(repo.admin_actions) == 1, "Should have 1 admin action"
    print(f"   ✅ Logged admin action: {repo.admin_actions[0].action}")

    print("   ✅ Test passed!")


async def test_remove_bot():
    """Test: Remove bot"""
    print("\n5️⃣ Test: Remove Bot")
    repo = MockUserBotRepository()

    # Create bot
    bot = create_sample_bot(user_id=123)
    created = await repo.create(bot)
    print(f"   ✅ Created bot ID={created.id}")

    # Verify exists
    exists = await repo.get_by_user_id(123)
    assert exists is not None, "Bot should exist"

    # Remove bot
    assert created.id is not None, "Created bot ID should not be None"
    success = await repo.delete(created.id)
    assert success is True, "Delete should succeed"
    print(f"   ✅ Deleted bot ID={created.id}")

    # Verify removed
    removed = await repo.get_by_user_id(123)
    assert removed is None, "Bot should not exist"
    print("   ✅ Verified bot removed")

    print("   ✅ Test passed!")


async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 User Bot API Tests - Simple Version")
    print("=" * 60)

    await test_create_and_get_bot()
    await test_list_multiple_bots()
    await test_suspend_and_activate_bot()
    await test_update_rate_limits()
    await test_remove_bot()

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
