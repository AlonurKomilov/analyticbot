"""
MTProto Data Collectors Container
Focused on data collection services and clients

✅ Phase 4 Note (Oct 19, 2025): MTProto-specific infrastructure
The infra.tg imports here are acceptable because:
1. apps/mtproto is itself an infrastructure adapter for Telegram
2. These are MTProto-specific implementations (AccountPool, ProxyPool, DCRouter)
3. They don't violate Clean Architecture - MTProto layer IS infrastructure
4. Creating protocols for these would add unnecessary abstraction

This is different from apps/api or apps/bot importing infra - those are
application layers that should use protocols. apps/mtproto bridges the
application to Telegram infrastructure, so it needs direct access.
"""

from dependency_injector import containers, providers

from apps.mtproto.config import MTProtoSettings

# MTProto-specific infrastructure (acceptable - MTProto is infrastructure adapter)
from infra.tg.account_pool import AccountPool
from infra.tg.dc_router import DCRouter
from infra.tg.proxy_pool import ProxyPool
from infra.tg.telethon_client import TelethonTGClient


class CollectorsContainer(containers.DeclarativeContainer):
    """Container for data collection services"""

    # Configuration
    settings = providers.Dependency(instance_of=MTProtoSettings)

    # Core Telegram client
    tg_client = providers.Factory(TelethonTGClient, settings=settings)

    # Scaling components for data collection
    account_pool = providers.Singleton(AccountPool, settings=settings)

    proxy_pool = providers.Singleton(ProxyPool, settings=settings)

    dc_router = providers.Singleton(DCRouter)

    # Collection services would go here
    # message_collector = providers.Factory(MessageCollector, ...)
    # channel_collector = providers.Factory(ChannelCollector, ...)
    # stats_collector = providers.Factory(StatsCollector, ...)
