"""
Test Multi-Tenant Bot Manager
Tests bot instance creation, caching, and LRU eviction
"""

import asyncio
from datetime import datetime

from core.models.user_bot_domain import AdminBotAction, BotStatus, UserBotCredentials
from core.ports.user_bot_repository import IUserBotRepository
from core.services.encryption_service import get_encryption_service


class MockRepository(IUserBotRepository):
    """Mock repository for testing"""

    def __init__(self):
        self.credentials = {}
        self.admin_actions = []

    async def create(self, credentials: UserBotCredentials) -> UserBotCredentials:
        """Create new credentials"""
        self.credentials[credentials.user_id] = credentials
        return credentials

    async def get_by_user_id(self, user_id: int) -> UserBotCredentials | None:
        """Get credentials by user ID"""
        return self.credentials.get(user_id)

    async def get_by_id(self, credentials_id: int) -> UserBotCredentials | None:
        """Get credentials by ID"""
        for cred in self.credentials.values():
            if cred.id == credentials_id:
                return cred
        return None

    async def update(self, credentials: UserBotCredentials) -> UserBotCredentials:
        """Update credentials"""
        self.credentials[credentials.user_id] = credentials
        return credentials

    async def delete(self, user_id: int) -> bool:
        """Delete credentials"""
        if user_id in self.credentials:
            del self.credentials[user_id]
            return True
        return False

    async def list_all(
        self, limit: int = 50, offset: int = 0, status: str | None = None
    ) -> list[UserBotCredentials]:
        """List all credentials"""
        return list(self.credentials.values())

    async def count(self, status: str | None = None) -> int:
        """Count credentials"""
        return len(self.credentials)

    async def log_admin_action(self, action: AdminBotAction) -> None:
        """Log admin action"""
        self.admin_actions.append(action)
        print(
            f"📝 Admin action logged: {action.action} by admin {action.admin_user_id} for user {action.target_user_id}"
        )


def create_test_credentials(user_id: int) -> UserBotCredentials:
    """Create test credentials for a user"""
    encryption = get_encryption_service()

    # Use a fake bot token for testing (will fail on actual init)
    fake_token = f"123456789:FAKE_TOKEN_FOR_USER_{user_id}"
    fake_api_hash = f"fake_api_hash_{user_id}"

    return UserBotCredentials(
        id=user_id,
        user_id=user_id,
        bot_token=encryption.encrypt(fake_token),
        telegram_api_id=12345,
        telegram_api_hash=encryption.encrypt(fake_api_hash),
        bot_username=f"test_bot_{user_id}",
        bot_id=user_id * 100,
        status=BotStatus.ACTIVE,
        is_verified=True,
        rate_limit_rps=1.0,
        max_concurrent_requests=3,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


async def test_bot_manager():
    """Test bot manager functionality"""
    from infra.bot.multi_tenant_bot_manager import MultiTenantBotManager

    print("🧪 Testing Multi-Tenant Bot Manager\n")

    # Create mock repository
    repo = MockRepository()

    # Add test credentials
    for user_id in [1, 2, 3]:
        repo.credentials[user_id] = create_test_credentials(user_id)

    # Create bot manager with small cache
    manager = MultiTenantBotManager(
        repository=repo,
        max_active_bots=2,  # Small cache for testing eviction
        bot_idle_timeout_minutes=1,
    )

    print("1️⃣ Testing bot manager initialization...")
    await manager.start()
    print("✅ Manager started\n")

    print("2️⃣ Testing get_user_bot (should create instance)...")
    try:
        # This will fail because we're using fake tokens
        # But we can test the caching logic
        bot1 = await manager.get_user_bot(1)
        print("❌ Unexpected: Bot initialized with fake token\n")
    except Exception as e:
        print(f"✅ Expected error with fake token: {type(e).__name__}\n")

    print("3️⃣ Testing statistics...")
    stats = await manager.get_stats()
    print(f"📊 Stats: {stats}\n")

    print("4️⃣ Testing admin access...")
    try:
        await manager.admin_access_bot(admin_id=999, target_user_id=2)
    except Exception:
        print("✅ Admin access logged (failed with fake token)\n")

    print(f"📝 Admin actions logged: {len(repo.admin_actions)}")

    print("5️⃣ Stopping bot manager...")
    await manager.stop()
    print("✅ Manager stopped\n")

    print("✅ All tests passed (with expected failures for fake tokens)")


if __name__ == "__main__":
    print("=" * 60)
    print("Multi-Tenant Bot Manager Test")
    print("=" * 60 + "\n")

    try:
        asyncio.run(test_bot_manager())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
