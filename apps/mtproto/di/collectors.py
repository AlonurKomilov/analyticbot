"""
MTProto Data Collectors Container
Focused on data collection services and clients
"""

from dependency_injector import containers, providers

from apps.mtproto.config import MTProtoSettings
from core.ports.tg_client import TGClient
from infra.tg.telethon_client import TelethonTGClient
from infra.tg.account_pool import AccountPool
from infra.tg.proxy_pool import ProxyPool
from infra.tg.dc_router import DCRouter


class CollectorsContainer(containers.DeclarativeContainer):
    """Container for data collection services"""
    
    # Configuration
    settings = providers.Dependency(instance_of=MTProtoSettings)
    
    # Core Telegram client
    tg_client = providers.Factory(
        TelethonTGClient,
        settings=settings
    )
    
    # Scaling components for data collection
    account_pool = providers.Singleton(
        AccountPool,
        settings=settings
    )
    
    proxy_pool = providers.Singleton(
        ProxyPool,
        settings=settings
    )
    
    dc_router = providers.Singleton(
        DCRouter
    )
    
    # Collection services would go here
    # message_collector = providers.Factory(MessageCollector, ...)
    # channel_collector = providers.Factory(ChannelCollector, ...)
    # stats_collector = providers.Factory(StatsCollector, ...)