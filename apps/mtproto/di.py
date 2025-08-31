from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from typing import Protocol, runtime_checkable

from apps.mtproto.config import MTProtoSettings
from core.ports.tg_client import TGClient
from infra.tg.telethon_client import TelethonTGClient


@runtime_checkable
class MTProtoContainer(containers.DeclarativeContainer):
    """Dependency injection container for MTProto application.
    
    Provides centralized configuration and dependency management
    following Clean Architecture principles.
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Settings provider
    settings = providers.Singleton(
        MTProtoSettings
    )
    
    # TGClient implementation provider
    tg_client = providers.Factory(
        TelethonTGClient,
        settings=settings
    )


# Container instance
container = MTProtoContainer()


def configure_container(settings: MTProtoSettings) -> None:
    """Configure the DI container with application settings."""
    container.config.from_dict(settings.dict())


@inject
def get_tg_client(
    tg_client: TGClient = Provide[MTProtoContainer.tg_client]
) -> TGClient:
    """Get configured TGClient instance."""
    return tg_client


@inject 
def get_settings(
    settings: MTProtoSettings = Provide[MTProtoContainer.settings]
) -> MTProtoSettings:
    """Get application settings."""
    return settings
