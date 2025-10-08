"""
MTProto Dependency Injection - Clean Architecture
Decomposed from 481-line god container into focused domain containers
"""

import logging
from typing import Any

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from apps.mtproto.config import MTProtoSettings
from apps.mtproto.di.collectors import CollectorsContainer
from apps.mtproto.di.external import ExternalContainer
from apps.mtproto.di.processors import ProcessorsContainer
from apps.mtproto.di.storage import RepositoryContainer, StorageContainer
from core.ports.tg_client import TGClient

logger = logging.getLogger(__name__)


class MTProtoContainer(containers.DeclarativeContainer):
    """Main MTProto container - clean composition root"""

    # Core configuration
    config = providers.Configuration()
    settings = providers.Singleton(MTProtoSettings)

    # Focused sub-containers
    collectors = providers.Container(CollectorsContainer, settings=settings)

    processors = providers.Container(ProcessorsContainer, settings=settings)

    external = providers.Container(ExternalContainer, settings=settings)

    storage = providers.Container(StorageContainer, settings=settings)


# Convenience functions for backward compatibility
@inject
def get_tg_client(tg_client: TGClient = Provide[MTProtoContainer.collectors.tg_client]) -> TGClient:
    """Get Telegram client instance"""
    return tg_client


@inject
def get_settings(settings: MTProtoSettings = Provide[MTProtoContainer.settings]) -> MTProtoSettings:
    """Get MTProto settings"""
    return settings


@inject
async def get_repositories() -> RepositoryContainer:
    """Get repository container"""
    container = MTProtoContainer()
    return await container.storage.repositories()


def create_tg_client(settings: MTProtoSettings) -> TGClient:
    """Create TG client instance (backward compatibility)"""
    container = MTProtoContainer()
    container.config.from_dict(settings.model_dump())
    return container.collectors.tg_client()


def create_stats_loader(settings: MTProtoSettings):
    """Create stats loader instance (backward compatibility)"""
    container = MTProtoContainer()
    container.config.from_dict(settings.model_dump())
    return container.collectors.stats_loader()


def configure_container():
    """Configure the container (backward compatibility)"""
    return MTProtoContainer()


# Application lifecycle management
async def initialize_application(settings: MTProtoSettings) -> Any:
    """Initialize MTProto application with focused containers"""
    container = MTProtoContainer()
    container.config.from_dict(settings.model_dump())

    # Initialize external services
    await container.external.health_server().start()
    await container.external.global_tracer.init()

    logger.info("🚀 MTProto application initialized with decomposed containers")
    return container


async def shutdown_application(container: Any) -> None:
    """Shutdown MTProto application"""
    if hasattr(container, "external"):
        await container.external.health_server().stop()

    logger.info("🛑 MTProto application shutdown complete")


class MTProtoApp:
    """MTProto application context manager"""

    def __init__(self, settings: MTProtoSettings):
        self.settings = settings
        self.container = None

    async def __aenter__(self) -> Any:
        self.container = await initialize_application(self.settings)
        return self.container

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.container:
            await shutdown_application(self.container)


# Global container instance
container = MTProtoContainer()
