"""
Infrastructure Protocols for Clean Architecture
================================================

Protocol interfaces for infrastructure layer abstractions.
These protocols decouple the apps layer from concrete infrastructure implementations.

Phase 2 Fix (Oct 19, 2025):
- Created to eliminate Clean Architecture violations
- Allows apps/ to depend on protocols instead of concrete infra/ implementations
- Enables easy testing with mocks and infrastructure swapping
"""

from datetime import datetime
from typing import Any, Protocol

# ============================================================================
# Repository Protocols
# ============================================================================


class UserRepositoryProtocol(Protocol):
    """Protocol for user repository operations"""

    async def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        """Get user by ID"""
        ...

    async def get_user_by_telegram_id(self, telegram_id: int) -> dict[str, Any] | None:
        """Get user by Telegram ID"""
        ...

    async def create_user(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """Create new user"""
        ...

    async def update_user(self, user_id: int, **updates) -> bool:
        """Update user information"""
        ...

    async def get_user_subscription_tier(self, user_id: int) -> str:
        """Get user's subscription tier"""
        ...

    async def user_exists(self, user_id: int) -> bool:
        """Check if user exists"""
        ...

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """Get all users (paginated)"""
        ...

    async def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        ...


class AdminRepositoryProtocol(Protocol):
    """Protocol for admin operations"""

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """Get all users with pagination"""
        ...

    async def get_user_statistics(self) -> dict[str, Any]:
        """Get user statistics"""
        ...

    async def update_user_role(self, user_id: int, role: str) -> bool:
        """Update user role"""
        ...

    async def update_user_status(self, user_id: int, status: str) -> bool:
        """Update user status"""
        ...

    async def get_system_health(self) -> dict[str, Any]:
        """Get system health metrics"""
        ...


class AnalyticsRepositoryProtocol(Protocol):
    """Protocol for analytics data operations"""

    async def get_channel_analytics(
        self, channel_id: int, from_date: datetime, to_date: datetime
    ) -> dict[str, Any]:
        """Get channel analytics for date range"""
        ...

    async def get_channel_growth(self, channel_id: int, days: int = 30) -> list[dict[str, Any]]:
        """Get channel growth metrics"""
        ...

    async def get_post_performance(self, channel_id: int, post_id: int) -> dict[str, Any] | None:
        """Get individual post performance"""
        ...

    async def get_engagement_metrics(self, channel_id: int, period: str = "7d") -> dict[str, Any]:
        """Get engagement metrics"""
        ...

    async def save_analytics_snapshot(self, snapshot_data: dict[str, Any]) -> dict[str, Any]:
        """Save analytics snapshot"""
        ...


class ChannelDailyRepositoryProtocol(Protocol):
    """Protocol for daily channel metrics"""

    async def get_daily_metrics(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> list[dict[str, Any]]:
        """Get daily metrics for date range"""
        ...

    async def get_latest_metrics(self, channel_id: int) -> dict[str, Any] | None:
        """Get latest daily metrics"""
        ...

    async def save_daily_metrics(self, metrics_data: dict[str, Any]) -> dict[str, Any]:
        """Save daily metrics"""
        ...


class PostMetricsRepositoryProtocol(Protocol):
    """Protocol for post metrics"""

    async def get_post_metrics(self, post_id: int) -> dict[str, Any] | None:
        """Get metrics for a specific post"""
        ...

    async def get_channel_posts_metrics(
        self, channel_id: int, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get metrics for channel posts"""
        ...

    async def save_post_metrics(self, metrics_data: dict[str, Any]) -> dict[str, Any]:
        """Save post metrics"""
        ...


class StatsRawRepositoryProtocol(Protocol):
    """Protocol for raw statistics data"""

    async def save_raw_stats(self, stats_data: dict[str, Any]) -> dict[str, Any]:
        """Save raw statistics"""
        ...

    async def get_raw_stats(
        self, channel_id: int, from_date: datetime, to_date: datetime
    ) -> list[dict[str, Any]]:
        """Get raw statistics for date range"""
        ...


# ============================================================================
# Infrastructure Service Protocols
# ============================================================================


class CacheProtocol(Protocol):
    """Protocol for cache operations (Redis, in-memory, etc.)"""

    async def get(self, key: str) -> str | None:
        """Get value from cache"""
        ...

    async def set(self, key: str, value: str, expire: int | None = None) -> bool:
        """Set value in cache with optional expiration"""
        ...

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        ...

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        ...

    async def incr(self, key: str) -> int:
        """Increment value"""
        ...

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        ...

    async def ttl(self, key: str) -> int:
        """Get time to live"""
        ...

    async def keys(self, pattern: str) -> list[str]:
        """Get keys matching pattern"""
        ...

    async def close(self) -> None:
        """Close cache connection"""
        ...


class DatabaseManagerProtocol(Protocol):
    """
    Protocol for database connection management.

    Updated Oct 19, 2025: Aligned with actual DatabaseManager implementation.
    The DatabaseManager class uses different method names than initially designed.
    """

    @property
    def _pool(self) -> Any:
        """Get the private database connection pool"""
        ...

    async def initialize(self) -> None:
        """Initialize the database manager"""
        ...

    async def close(self) -> None:
        """Close the database manager"""
        ...

    async def health_check(self) -> dict[str, Any]:
        """Check database health"""
        ...

    async def execute_query(self, query: str, *args, **kwargs) -> Any:
        """Execute optimized query"""
        ...

    async def fetch_query(self, query: str, *args, **kwargs) -> list[dict]:
        """Fetch optimized query results"""
        ...

    async def fetch_one(self, query: str, *args, **kwargs) -> dict | None:
        """Fetch single row from optimized query"""
        ...

    def connection(self) -> Any:
        """Get optimized database connection (async context manager)"""
        ...

    def get_stats(self) -> dict[str, Any]:
        """Get database performance statistics"""
        ...


class TelegramClientProtocol(Protocol):
    """Protocol for Telegram client operations (Telethon, Pyrogram, etc.)"""

    async def start(self) -> None:
        """Start Telegram client"""
        ...

    async def stop(self) -> None:
        """Stop Telegram client"""
        ...

    async def is_connected(self) -> bool:
        """Check if client is connected"""
        ...

    async def get_entity(self, entity_id: int | str):
        """Get Telegram entity (channel, user, etc.)"""
        ...

    async def get_messages(self, entity, limit: int = 100, **kwargs) -> list[Any]:
        """Get messages from entity"""
        ...

    async def get_participants(self, entity, limit: int = 100) -> list[Any]:
        """Get participants of entity"""
        ...

    async def send_message(self, entity, message: str, **kwargs) -> Any:
        """Send message to entity"""
        ...

    async def get_stats(self, channel) -> Any:
        """Get channel statistics"""
        ...


__all__ = [
    # Repository Protocols
    "UserRepositoryProtocol",
    "AdminRepositoryProtocol",
    "AnalyticsRepositoryProtocol",
    "ChannelDailyRepositoryProtocol",
    "PostMetricsRepositoryProtocol",
    "StatsRawRepositoryProtocol",
    # Infrastructure Protocols
    "CacheProtocol",
    "DatabaseManagerProtocol",
    "TelegramClientProtocol",
]
