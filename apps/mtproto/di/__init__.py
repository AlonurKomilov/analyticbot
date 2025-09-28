"""
MTProto DI Container - Main Composition Root
Focused container with clear separation of concerns
"""

from dependency_injector import containers, providers

from apps.mtproto.config import MTProtoSettings
from apps.mtproto.di.collectors import CollectorsContainer
from apps.mtproto.di.processors import ProcessorsContainer  
from apps.mtproto.di.external import ExternalContainer
from apps.mtproto.di.storage import StorageContainer


class MTProtoContainer(containers.DeclarativeContainer):
    """Main MTProto container - composes focused sub-containers"""
    
    # Core configuration
    config = providers.Configuration()
    settings = providers.Singleton(MTProtoSettings)
    
    # Sub-containers for different concerns
    collectors = providers.DependenciesContainer()
    processors = providers.DependenciesContainer() 
    external = providers.DependenciesContainer()
    storage = providers.DependenciesContainer()


def create_container() -> MTProtoContainer:
    """Create and wire the main MTProto container"""
    container = MTProtoContainer()
    
    # Wire sub-containers
    container.collectors.override(CollectorsContainer())
    container.processors.override(ProcessorsContainer())
    container.external.override(ExternalContainer()) 
    container.storage.override(StorageContainer())
    
    # Wire sub-containers together
    container.wire(modules=[__name__])
    
    return container


# Global container instance
container = create_container()