"""
MTProto Storage Container
Focused on database repositories and storage services
✅ Phase 4 Fix (Oct 19, 2025): Migrated to DI container delegation
No more direct infra imports - uses main container via protocol-based delegation
"""


from dependency_injector import containers, providers

from apps.di import get_container
from apps.mtproto.config import MTProtoSettings


# ✅ PHASE 4 FIX: Repository delegation helpers
# These async callables delegate to main container for repository access
async def _get_channel_daily_repo():
    """Get channel daily repository from main container"""
    container = get_container()
    return await container.database.channel_daily_repo()  # type: ignore[attr-defined]


async def _get_channel_repo():
    """Get channel repository from main container"""
    container = get_container()
    return await container.database.channel_repo()  # type: ignore[attr-defined]


async def _get_post_metrics_repo():
    """Get post metrics repository from main container"""
    container = get_container()
    return await container.database.metrics_repo()  # type: ignore[attr-defined]


async def _get_post_repo():
    """Get post repository from main container"""
    container = get_container()
    return await container.database.post_repo()  # type: ignore[attr-defined]


async def _get_stats_raw_repo():
    """Get stats raw repository from main container"""
    container = get_container()
    return await container.database.stats_raw_repo()  # type: ignore[attr-defined]


class StorageContainer(containers.DeclarativeContainer):
    """
    Container for storage and repository services

    ✅ Phase 4 Fix (Oct 19, 2025): Uses DI delegation pattern
    All repositories now delegate to main container via Callable providers
    """

    # Configuration
    settings = providers.Dependency(instance_of=MTProtoSettings)

    # ✅ PHASE 4 FIX: Repository providers delegate to main container
    # Uses Callable pattern for async repository access
    channel_daily_repo = providers.Callable(_get_channel_daily_repo)
    channel_repo = providers.Callable(_get_channel_repo)
    post_metrics_repo = providers.Callable(_get_post_metrics_repo)
    post_repo = providers.Callable(_get_post_repo)
    stats_raw_repo = providers.Callable(_get_stats_raw_repo)
