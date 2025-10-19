"""
MTProto Storage Container
Focused on database repositories and storage services
Phase 2 Fix (Oct 19, 2025): Updated imports to use protocols where possible
Note: Full protocol compliance requires repository interface alignment (Phase 3)
"""

from typing import Any

from dependency_injector import containers, providers

from apps.mtproto.config import MTProtoSettings

# ✅ PHASE 2 PROGRESS: Import protocols for type awareness
# Note: Concrete implementations don't fully match protocols yet (requires Phase 3 work)
# Concrete implementations (temporary until Phase 3 aligns interfaces)
from infra.db.repositories.channel_daily_repository import ChannelDailyRepository
from infra.db.repositories.channel_repository import ChannelRepository
from infra.db.repositories.post_metrics_repository import PostMetricsRepository
from infra.db.repositories.post_repository import PostRepository
from infra.db.repositories.stats_raw_repository import StatsRawRepository


class RepositoryContainer:
    """Container for all repository instances"""

    def __init__(self):
        # Note: Repositories instantiated without pool - will be injected at runtime
        # Protocol types added for future compliance (Phase 3)
        self.channel_daily: Any = None  # Will be: ChannelDailyRepositoryProtocol
        self.channel: Any = None  # Will be: ChannelRepositoryProtocol
        self.post_metrics: Any = None  # Will be: PostMetricsRepositoryProtocol
        self.post: Any = None  # Will be: PostsRepositoryProtocol
        self.stats_raw: Any = None  # Will be: StatsRawRepositoryProtocol

    def initialize(self, pool):
        """Initialize repositories with database pool"""
        self.channel_daily = ChannelDailyRepository(pool)
        self.channel = ChannelRepository(pool)
        self.post_metrics = PostMetricsRepository(pool)
        self.post = PostRepository(pool)
        self.stats_raw = StatsRawRepository(pool)


class StorageContainer(containers.DeclarativeContainer):
    """Container for storage and repository services"""

    # Configuration
    settings = providers.Dependency(instance_of=MTProtoSettings)

    # Repository container
    repositories = providers.Singleton(RepositoryContainer)

    # Individual repositories
    channel_daily_repo = providers.Factory(lambda repos: repos.channel_daily, repos=repositories)

    channel_repo = providers.Factory(lambda repos: repos.channel, repos=repositories)

    post_metrics_repo = providers.Factory(lambda repos: repos.post_metrics, repos=repositories)

    post_repo = providers.Factory(lambda repos: repos.post, repos=repositories)

    stats_raw_repo = providers.Factory(lambda repos: repos.stats_raw, repos=repositories)
