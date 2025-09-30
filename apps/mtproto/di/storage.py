"""
MTProto Storage Container
Focused on database repositories and storage services
"""

from dependency_injector import containers, providers

from apps.mtproto.config import MTProtoSettings
from infra.db.repositories.channel_daily_repository import ChannelDailyRepository
from infra.db.repositories.channel_repository import ChannelRepository
from infra.db.repositories.post_metrics_repository import PostMetricsRepository
from infra.db.repositories.post_repository import PostRepository
from infra.db.repositories.stats_raw_repository import StatsRawRepository


class RepositoryContainer:
    """Container for all repository instances"""

    def __init__(self):
        self.channel_daily = ChannelDailyRepository()
        self.channel = ChannelRepository()
        self.post_metrics = PostMetricsRepository()
        self.post = PostRepository()
        self.stats_raw = StatsRawRepository()


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
