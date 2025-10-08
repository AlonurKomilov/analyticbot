"""
Concrete Repository Factory Implementation
Infrastructure layer implementation of the repository factory
"""

from typing import Any

from core.ports.repository_factory import AbstractRepositoryFactory


class AsyncpgRepositoryFactory(AbstractRepositoryFactory):
    """
    Concrete implementation of repository factory using AsyncPG.

    This class is allowed to import infrastructure directly because
    it resides in the infrastructure layer and implements the abstraction
    defined in the core layer.
    """

    def __init__(self, pool: Any):
        """
        Initialize with database pool.

        Args:
            pool: AsyncPG database pool instance
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


class CacheFactory:
    """
    Factory for creating cache adapters.
    Centralizes cache creation logic in infrastructure layer.
    """

    @staticmethod
    def create_cache_adapter(redis_client=None) -> Any:
        """
        Create cache adapter instance.

        Args:
            redis_client: Optional Redis client instance

        Returns:
            Cache adapter instance
        """
        from infra.cache.redis_cache import create_cache_adapter

        return create_cache_adapter(redis_client)
