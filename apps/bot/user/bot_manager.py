"""
Multi-Tenant Bot Manager
Manages all user bot instances with LRU caching and background cleanup
"""

import asyncio
from collections import OrderedDict
from datetime import datetime, timedelta

from core.models.user_bot_domain import AdminBotAction
from core.ports.user_bot_repository import IUserBotRepository

from .user_bot_instance import UserBotInstance


class MultiTenantBotManager:
    """
    Manages multiple user bot instances with LRU caching

    Features:
    - LRU cache to keep most active bots in memory
    - Automatic eviction of least recently used bots
    - Background cleanup of idle bots
    - Admin access to any user's bot
    - Thread-safe operations with async locks
    """

    def __init__(
        self,
        repository: IUserBotRepository,
        max_active_bots: int = 100,
        bot_idle_timeout_minutes: int = 30,
    ):
        """
        Initialize bot manager

        Args:
            repository: User bot credentials repository
            max_active_bots: Maximum number of bots to keep in memory
            bot_idle_timeout_minutes: Timeout for idle bot cleanup
        """
        self.repository = repository
        self.max_active_bots = max_active_bots
        self.bot_idle_timeout = timedelta(minutes=bot_idle_timeout_minutes)

        # LRU cache of active bots (OrderedDict maintains insertion order)
        self.active_bots: OrderedDict[int, UserBotInstance] = OrderedDict()

        # Lock for thread-safe operations
        self.lock = asyncio.Lock()

        # Background cleanup task
        self.cleanup_task: asyncio.Task | None = None

        # Statistics
        self.stats = {
            "total_created": 0,
            "total_evicted": 0,
            "total_cleaned": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    async def start(self) -> None:
        """
        Start bot manager background tasks
        """
        self.cleanup_task = asyncio.create_task(self._cleanup_idle_bots())
        print(f"✅ Multi-Tenant Bot Manager started (max {self.max_active_bots} active)")

    async def stop(self) -> None:
        """
        Stop bot manager and shutdown all bots
        """
        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

        # Shutdown all active bots
        print(f"🛑 Shutting down {len(self.active_bots)} active bots...")
        for bot in list(self.active_bots.values()):
            await bot.shutdown()

        self.active_bots.clear()
        print("✅ Multi-Tenant Bot Manager stopped")

    async def get_user_bot(self, user_id: int) -> UserBotInstance:
        """
        Get or create bot instance for user

        Args:
            user_id: User ID

        Returns:
            UserBotInstance for the user

        Raises:
            ValueError: If no credentials found or bot is suspended
        """
        async with self.lock:
            # Check if already in cache
            if user_id in self.active_bots:
                # Move to end (most recently used)
                self.active_bots.move_to_end(user_id)
                self.stats["cache_hits"] += 1
                return self.active_bots[user_id]

            # Cache miss - load from database
            self.stats["cache_misses"] += 1
            credentials = await self.repository.get_by_user_id(user_id)

            if not credentials:
                raise ValueError(f"No bot credentials found for user {user_id}")

            if not credentials.can_make_request():
                raise ValueError(
                    f"Bot for user {user_id} is {credentials.status.value}. "
                    f"Cannot make requests."
                )

            # Create new instance
            bot_instance = UserBotInstance(credentials)
            await bot_instance.initialize()

            # Add to cache
            self.active_bots[user_id] = bot_instance
            self.stats["total_created"] += 1

            # Evict LRU if cache is full
            if len(self.active_bots) > self.max_active_bots:
                await self._evict_lru()

            return bot_instance

    async def admin_access_bot(self, admin_id: int, target_user_id: int) -> UserBotInstance:
        """
        Admin access to any user's bot

        Args:
            admin_id: Admin user ID
            target_user_id: Target user's ID

        Returns:
            UserBotInstance for the target user
        """
        # Log admin action
        await self.repository.log_admin_action(
            AdminBotAction(
                id=0,  # Will be set by DB
                admin_user_id=admin_id,
                target_user_id=target_user_id,
                action="admin_access_bot",
                details={"timestamp": datetime.now().isoformat(), "action_type": "access"},
            )
        )

        # Return user's bot (same as normal access)
        return await self.get_user_bot(target_user_id)

    async def shutdown_user_bot(self, user_id: int) -> None:
        """
        Force shutdown specific user's bot

        Args:
            user_id: User ID
        """
        async with self.lock:
            if user_id in self.active_bots:
                bot = self.active_bots.pop(user_id)
                await bot.shutdown()
                print(f"🛑 Force shutdown bot for user {user_id}")

    async def reload_user_bot(self, user_id: int) -> UserBotInstance:
        """
        Reload user's bot (shutdown and recreate)

        Useful when credentials are updated

        Args:
            user_id: User ID

        Returns:
            New UserBotInstance with updated credentials
        """
        # Shutdown existing bot
        await self.shutdown_user_bot(user_id)

        # Get fresh instance
        return await self.get_user_bot(user_id)

    async def get_active_bots_count(self) -> int:
        """
        Get count of currently active bots

        Returns:
            Number of active bots in cache
        """
        return len(self.active_bots)

    async def get_stats(self) -> dict:
        """
        Get bot manager statistics

        Returns:
            Dict with statistics
        """
        return {
            **self.stats,
            "active_bots": len(self.active_bots),
            "max_active_bots": self.max_active_bots,
            "idle_timeout_minutes": self.bot_idle_timeout.total_seconds() / 60,
        }

    async def _evict_lru(self) -> None:
        """
        Evict least recently used bot from cache
        """
        if not self.active_bots:
            return

        # Get LRU (first item in OrderedDict)
        user_id, bot = self.active_bots.popitem(last=False)
        await bot.shutdown()

        self.stats["total_evicted"] += 1
        print(f"🗑️  Evicted LRU bot for user {user_id} (cache full)")

    async def _cleanup_idle_bots(self) -> None:
        """
        Background task to cleanup idle bots

        Runs every 5 minutes and removes bots that haven't been used
        for longer than bot_idle_timeout
        """
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                async with self.lock:
                    now = datetime.now()
                    to_remove = []

                    # Find idle bots
                    for user_id, bot in self.active_bots.items():
                        idle_time = now - bot.last_activity
                        if idle_time > self.bot_idle_timeout:
                            to_remove.append(user_id)

                    # Remove idle bots
                    for user_id in to_remove:
                        bot = self.active_bots.pop(user_id)
                        await bot.shutdown()
                        self.stats["total_cleaned"] += 1
                        print(
                            f"🧹 Cleaned up idle bot for user {user_id} "
                            f"(idle for {self.bot_idle_timeout.total_seconds() / 60:.1f} minutes)"
                        )

                    if to_remove:
                        print(
                            f"📊 Cleanup stats: {len(to_remove)} bots removed, "
                            f"{len(self.active_bots)} active"
                        )

            except asyncio.CancelledError:
                print("🛑 Cleanup task cancelled")
                break
            except Exception as e:
                print(f"❌ Error in cleanup task: {e}")
                # Continue running despite errors


# Global singleton
_bot_manager: MultiTenantBotManager | None = None


async def get_bot_manager() -> MultiTenantBotManager:
    """
    Get bot manager singleton

    Returns:
        MultiTenantBotManager instance

    Raises:
        RuntimeError: If bot manager not initialized
    """
    global _bot_manager
    if _bot_manager is None:
        raise RuntimeError(
            "Bot manager not initialized. "
            "Call initialize_bot_manager() first during application startup."
        )
    return _bot_manager


async def initialize_bot_manager(
    repository: IUserBotRepository, max_active_bots: int = 100, bot_idle_timeout_minutes: int = 30
) -> MultiTenantBotManager:
    """
    Initialize and start bot manager

    Should be called once during application startup

    Args:
        repository: User bot credentials repository
        max_active_bots: Maximum number of bots to keep in memory
        bot_idle_timeout_minutes: Timeout for idle bot cleanup

    Returns:
        MultiTenantBotManager instance
    """
    global _bot_manager

    if _bot_manager is not None:
        print("⚠️  Bot manager already initialized")
        return _bot_manager

    _bot_manager = MultiTenantBotManager(
        repository=repository,
        max_active_bots=max_active_bots,
        bot_idle_timeout_minutes=bot_idle_timeout_minutes,
    )
    await _bot_manager.start()

    return _bot_manager
