# apps/shared/factory.py
"""
Repository Factory Implementation
Provides repository instances without exposing infra imports to app layer
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, cast

from apps.shared.protocols import (
    AnalyticsRepository,
    ChartServiceProtocol,
)
from core.repositories.alert_repository import (
    AlertSentRepository,
    AlertSubscriptionRepository,
)

# Import core interfaces (allowed - apps can import from core)
from core.repositories.interfaces import (
    AdminRepository,
    ChannelRepository,
    UserRepository,
)
from core.repositories.shared_reports_repository import SharedReportsRepository

logger = logging.getLogger(__name__)

__all__ = [
    "RepositoryFactory",
    "DatabaseConnectionAdapter",
    "create_repository_factory",
]


class DatabaseConnectionAdapter:
    """Adapter to provide database connection protocol without direct asyncpg import"""

    def __init__(self, connection_or_pool: Any):
        self._connection = connection_or_pool
        self._is_pool = hasattr(connection_or_pool, "acquire")

    async def acquire(self):
        """Acquire connection from pool"""
        if self._is_pool:
            return await self._connection.acquire()
        return self._connection

    async def release(self, connection):
        """Release connection back to pool"""
        if self._is_pool:
            await self._connection.release(connection)

    async def execute(self, query: str, *args):
        """Execute query"""
        if self._is_pool:
            async with self._connection.acquire() as conn:
                return await conn.execute(query, *args)
        return await self._connection.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Fetch multiple rows"""
        if self._is_pool:
            async with self._connection.acquire() as conn:
                return await conn.fetch(query, *args)
        return await self._connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Fetch single row"""
        if self._is_pool:
            async with self._connection.acquire() as conn:
                return await conn.fetchrow(query, *args)
        return await self._connection.fetchrow(query, *args)

    async def close(self):
        """Close connection/pool"""
        if hasattr(self._connection, "close"):
            await self._connection.close()


class RepositoryFactory:
    """
    Factory for creating repository instances without direct infra imports.
    Uses lazy loading to avoid circular imports.
    """

    def __init__(self, connection_provider: Callable):
        self._connection_provider = connection_provider
        self._connection_cache: Any | None = None

    async def _get_connection(self):
        """Get database connection using provider"""
        if self._connection_cache is None:
            self._connection_cache = await self._connection_provider()
        return self._connection_cache

    async def create_user_repository(self) -> UserRepository:
        """Create user repository without direct infra import"""
        try:
            # Dynamic import to avoid circular dependencies
            from infra.db.repositories.user_repository import AsyncpgUserRepository

            connection = await self._get_connection()
            if connection is None:
                logger.warning("Database connection not available, using fallback")
                return self._create_memory_user_repository()
            return AsyncpgUserRepository(connection)
        except ImportError:
            logger.warning("Failed to import AsyncpgUserRepository, using fallback")
            return self._create_memory_user_repository()

    async def create_channel_repository(self) -> ChannelRepository:
        """Create channel repository without direct infra import"""
        try:
            from infra.db.repositories.channel_repository import (
                AsyncpgChannelRepository,
            )

            connection = await self._get_connection()
            if connection is None:
                logger.warning("Database connection not available, using fallback")
                return self._create_memory_channel_repository()
            return AsyncpgChannelRepository(connection)
        except ImportError:
            logger.warning("Failed to import AsyncpgChannelRepository, using fallback")
            return self._create_memory_channel_repository()

    async def create_analytics_repository(self) -> AnalyticsRepository:
        """Create analytics repository without direct infra import"""
        try:
            from infra.db.repositories.analytics_repository import (
                AsyncpgAnalyticsRepository,
            )

            connection = await self._get_connection()
            if connection is None:
                logger.warning("Database connection not available, using fallback")
                return self._create_memory_analytics_repository()
            # Cast to AnalyticsRepository protocol for typing
            return cast(AnalyticsRepository, AsyncpgAnalyticsRepository(connection))
        except ImportError:
            logger.warning("Failed to import AsyncpgAnalyticsRepository, using fallback")
            return self._create_memory_analytics_repository()

    async def create_admin_repository(self) -> AdminRepository:
        """Create admin repository without direct infra import"""
        try:
            from infra.db.repositories.admin_repository import AsyncpgAdminRepository

            connection = await self._get_connection()
            if connection is None:
                logger.warning("Database connection not available, using fallback")
                return self._create_memory_admin_repository()
            return AsyncpgAdminRepository(connection)
        except ImportError:
            logger.warning("Failed to import AsyncpgAdminRepository, using fallback")
            return self._create_memory_admin_repository()

    async def create_alert_subscription_repository(self) -> AlertSubscriptionRepository:
        """Create alert subscription repository without direct infra import"""
        try:
            from infra.db.repositories.alert_repository import (
                AsyncpgAlertSubscriptionRepository,
            )

            connection = await self._get_connection()
            if connection is None:
                logger.warning("Database connection not available, using fallback")
                return self._create_memory_alert_subscription_repository()
            return AsyncpgAlertSubscriptionRepository(connection)
        except ImportError:
            logger.warning("Failed to import AsyncpgAlertSubscriptionRepository, using fallback")
            return self._create_memory_alert_subscription_repository()

    async def create_alert_sent_repository(self) -> AlertSentRepository:
        """Create alert sent repository without direct infra import"""
        try:
            from infra.db.repositories.alert_repository import (
                AsyncpgAlertSentRepository,
            )

            connection = await self._get_connection()
            if connection is None:
                logger.warning("Database connection not available, using fallback")
                return self._create_memory_alert_sent_repository()
            return AsyncpgAlertSentRepository(connection)
        except ImportError:
            logger.warning("Failed to import AsyncpgAlertSentRepository, using fallback")
            return self._create_memory_alert_sent_repository()

    async def create_shared_reports_repository(self) -> SharedReportsRepository:
        """Create shared reports repository without direct infra import"""
        try:
            from infra.db.repositories.shared_reports_repository import (
                AsyncPgSharedReportsRepository,
            )

            connection = await self._get_connection()
            if connection is None:
                logger.warning("Database connection not available, using fallback")
                return cast(
                    SharedReportsRepository,
                    self._create_memory_shared_reports_repository(),
                )
            # AsyncPgSharedReportsRepository doesn't take connection parameter
            return AsyncPgSharedReportsRepository()
        except ImportError:
            logger.warning("Failed to import AsyncPgSharedReportsRepository, using fallback")
            return cast(SharedReportsRepository, self._create_memory_shared_reports_repository())

    def _create_memory_user_repository(self) -> UserRepository:
        """Fallback memory-based user repository"""

        # Create a simple fallback implementation
        class FallbackUserRepository:
            async def get_user_by_id(self, user_id: int) -> dict | None:
                return None

            async def get_user_by_email(self, email: str) -> dict | None:
                return None

            async def create_user(self, user_data: dict) -> dict:
                return {}

            async def update_user(self, user_id: int, **kwargs) -> bool:
                return False

        return cast(UserRepository, FallbackUserRepository())

    def _create_memory_channel_repository(self) -> ChannelRepository:
        """Fallback memory-based channel repository"""

        class FallbackChannelRepository:
            async def get_channel_by_id(self, channel_id: int) -> dict | None:
                return None

            async def get_channels_by_user(self, user_id: int) -> list[dict]:
                return []

            async def create_channel(
                self,
                channel_id: int,
                user_id: int,
                title: str,
                username: str | None = None,
            ) -> None:
                return None

            async def update_channel(self, channel_id: int, **kwargs) -> None:
                return None

        return cast(ChannelRepository, FallbackChannelRepository())

    def _create_memory_analytics_repository(self) -> AnalyticsRepository:
        """Fallback memory-based analytics repository"""

        class FallbackAnalyticsRepository:
            async def get_analytics_data(self, **kwargs) -> Any:
                return {}

        return cast(AnalyticsRepository, FallbackAnalyticsRepository())

    def _create_memory_admin_repository(self) -> AdminRepository:
        """Fallback memory-based admin repository"""

        class FallbackAdminRepository:
            async def get_admin_by_id(self, admin_id: int) -> dict | None:
                return None

            async def get_admin_by_username(self, username: str) -> dict | None:
                return None

            async def create_admin(self, admin_data: dict) -> dict:
                return {}

            async def update_admin(self, admin_id: int, **updates) -> bool:
                return False

        return cast(AdminRepository, FallbackAdminRepository())

    def _create_memory_alert_subscription_repository(
        self,
    ) -> AlertSubscriptionRepository:
        """Fallback memory-based alert subscription repository"""

        class FallbackAlertSubscriptionRepository:
            async def create_subscription(self, subscription):
                return subscription

            async def get_subscription(self, subscription_id):
                return None

            async def get_user_subscriptions(self, chat_id):
                return []

            async def get_channel_subscriptions(self, channel_id):
                return []

            async def get_active_subscriptions(self):
                return []

            async def update_subscription(self, subscription):
                return subscription

            async def delete_subscription(self, subscription_id):
                return False

            async def toggle_subscription(self, subscription_id):
                return False

        return FallbackAlertSubscriptionRepository()

    def _create_memory_alert_sent_repository(self) -> AlertSentRepository:
        """Fallback memory-based alert sent repository"""

        class FallbackAlertSentRepository:
            async def mark_alert_sent(self, alert_sent):
                return True

            async def is_alert_sent(self, chat_id, channel_id, kind, key):
                return False

            async def cleanup_old_alerts(self, hours_old=24):
                return 0

        return FallbackAlertSentRepository()

    def _create_memory_shared_reports_repository(self):
        """Fallback memory-based shared reports repository"""

        class FallbackSharedReportsRepository:
            async def create_shared_report(self, **kwargs):
                return "fallback_token"

            async def get_shared_report(self, token):
                return None

            async def increment_access_count(self, token):
                return True

            async def delete_shared_report(self, token):
                return True

            async def cleanup_expired(self):
                return 0

        return FallbackSharedReportsRepository()


async def create_repository_factory() -> RepositoryFactory:
    """
    Create repository factory with database connection provider.
    Uses shared DI container to get connection without direct imports.
    """

    async def connection_provider():
        """Provide database connection through shared container"""
        try:
            # Use existing shared DI container
            from apps.shared.di import get_container

            container = get_container()
            return await container.asyncpg_pool()
        except Exception as e:
            logger.warning(f"Failed to get connection from shared container: {e}")
            return None

    return RepositoryFactory(connection_provider)


class LazyRepositoryFactory:
    """
    Lazy repository factory that delays creation until needed.
    Prevents circular imports and initialization order issues.
    """

    def __init__(self):
        self._factory: RepositoryFactory | None = None

    async def _ensure_factory(self) -> RepositoryFactory:
        """Ensure factory is created"""
        if self._factory is None:
            self._factory = await create_repository_factory()
        return self._factory

    async def get_user_repository(self) -> UserRepository:
        """Get user repository"""
        factory = await self._ensure_factory()
        return await factory.create_user_repository()

    async def get_channel_repository(self) -> ChannelRepository:
        """Get channel repository"""
        factory = await self._ensure_factory()
        return await factory.create_channel_repository()

    async def get_analytics_repository(self) -> AnalyticsRepository:
        """Get analytics repository"""
        factory = await self._ensure_factory()
        return await factory.create_analytics_repository()

    async def get_admin_repository(self) -> AdminRepository:
        """Get admin repository"""
        factory = await self._ensure_factory()
        return await factory.create_admin_repository()

    async def get_alert_subscription_repository(self) -> AlertSubscriptionRepository:
        """Get alert subscription repository"""
        factory = await self._ensure_factory()
        return await factory.create_alert_subscription_repository()

    async def get_alert_sent_repository(self) -> AlertSentRepository:
        """Get alert sent repository"""
        factory = await self._ensure_factory()
        return await factory.create_alert_sent_repository()

    async def get_shared_reports_repository(self) -> SharedReportsRepository:
        """Get shared reports repository"""
        factory = await self._ensure_factory()
        return await factory.create_shared_reports_repository()

    def get_chart_service(self) -> ChartServiceProtocol:
        """Get chart service instance"""
        from apps.shared.services.chart_service import create_chart_service

        return create_chart_service()

    async def create_payment_repository(self):
        """Create payment repository without direct infra import"""
        try:
            from infra.db.repositories.payment_repository import (
                AsyncpgPaymentRepository,
            )

            factory = await self._ensure_factory()
            connection = await factory._get_connection()
            if connection is None:
                logger.warning("Database connection not available")
                return None
            return AsyncpgPaymentRepository(connection)
        except ImportError:
            logger.warning("Failed to import AsyncpgPaymentRepository, using fallback")
            return None

    async def create_plan_repository(self):
        """Create plan repository without direct infra import"""
        try:
            from infra.db.repositories.plan_repository import AsyncpgPlanRepository

            factory = await self._ensure_factory()
            connection = await factory._get_connection()
            if connection is None:
                logger.warning("Database connection not available")
                return None
            return AsyncpgPlanRepository(connection)
        except ImportError:
            logger.warning("Failed to import AsyncpgPlanRepository, using fallback")
            return None


# Global lazy factory instance
_repository_factory = LazyRepositoryFactory()


def get_repository_factory() -> LazyRepositoryFactory:
    """Get global repository factory instance"""
    return _repository_factory
