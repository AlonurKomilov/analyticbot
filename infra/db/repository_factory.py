"""
AsyncPG Repository Factory Implementation
Concrete implementation of repository factory for PostgreSQL/AsyncPG infrastructure
"""

from typing import Any, Union
from core.ports.repository_factory import AbstractRepositoryFactory

if TYPE_CHECKING:
    from asyncpg.pool import Pool


class AsyncpgRepositoryFactory(AbstractRepositoryFactory):
    """
    Concrete repository factory for AsyncPG/PostgreSQL repositories.
    This class encapsulates all direct infrastructure imports and provides
    clean abstractions to the application layer.
    """

    def __init__(self, pool: Union["Pool", Any]):
        """
        Initialize factory with database pool.
        
        Args:
            pool: AsyncPG database pool or compatible mock
        """
        self.pool = pool

    def create_channel_repository(self) -> Any:
        """Create AsyncPG channel repository"""
        from infra.db.repositories.channel_repository import AsyncpgChannelRepository
        return AsyncpgChannelRepository(self.pool)

    def create_channel_daily_repository(self) -> Any:
        """Create AsyncPG channel daily repository"""
        from infra.db.repositories.channel_daily_repository import AsyncpgChannelDailyRepository
        return AsyncpgChannelDailyRepository(self.pool)

    def create_post_repository(self) -> Any:
        """Create AsyncPG post repository"""
        from infra.db.repositories.post_repository import AsyncpgPostRepository
        return AsyncpgPostRepository(self.pool)

    def create_post_metrics_repository(self) -> Any:
        """Create AsyncPG post metrics repository"""
        from infra.db.repositories.post_metrics_repository import AsyncpgPostMetricsRepository
        return AsyncpgPostMetricsRepository(self.pool)

    def create_edges_repository(self) -> Any:
        """Create AsyncPG edges repository"""
        from infra.db.repositories.edges_repository import AsyncpgEdgesRepository
        return AsyncpgEdgesRepository(self.pool)

    def create_stats_raw_repository(self) -> Any:
        """Create AsyncPG stats raw repository"""
        from infra.db.repositories.stats_raw_repository import AsyncpgStatsRawRepository
        return AsyncpgStatsRawRepository(self.pool)


class CacheAdapterFactory:
    """
    Factory for creating cache adapters.
    Encapsulates cache infrastructure imports.
    """

    @staticmethod
    def create_cache_adapter(redis_client: Any = None) -> Any:
        """
        Create cache adapter with optional Redis client.
        
        Args:
            redis_client: Redis client instance or None for no-op cache
            
        Returns:
            Cache adapter instance
        """
        from infra.cache.redis_cache import create_cache_adapter
        return create_cache_adapter(redis_client)


# Import TYPE_CHECKING for type hints
from typing import TYPE_CHECKING