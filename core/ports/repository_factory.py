"""
Repository Factory Protocol
Defines the interface for creating domain repositories with infrastructure independence
"""

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RepositoryFactory(Protocol):
    """
    Protocol for creating domain repositories.
    This allows the application layer to request repositories without
    knowing the concrete infrastructure implementations.
    """

    def create_channel_repository(self) -> Any:
        """Create a channel repository instance"""
        ...

    def create_channel_daily_repository(self) -> Any:
        """Create a channel daily metrics repository instance"""
        ...

    def create_post_repository(self) -> Any:
        """Create a post repository instance"""
        ...

    def create_post_metrics_repository(self) -> Any:
        """Create a post metrics repository instance"""
        ...

    def create_edges_repository(self) -> Any:
        """Create an edges repository instance"""
        ...

    def create_stats_raw_repository(self) -> Any:
        """Create a stats raw repository instance"""
        ...


class AbstractRepositoryFactory(ABC):
    """
    Abstract base class for repository factories.
    Concrete implementations in the infrastructure layer will inherit from this.
    """

    @abstractmethod
    def create_channel_repository(self) -> Any:
        """Create a channel repository instance"""
        pass

    @abstractmethod
    def create_channel_daily_repository(self) -> Any:
        """Create a channel daily metrics repository instance"""
        pass

    @abstractmethod
    def create_post_repository(self) -> Any:
        """Create a post repository instance"""
        pass

    @abstractmethod
    def create_post_metrics_repository(self) -> Any:
        """Create a post metrics repository instance"""
        pass

    @abstractmethod
    def create_edges_repository(self) -> Any:
        """Create an edges repository instance"""
        pass

    @abstractmethod
    def create_stats_raw_repository(self) -> Any:
        """Create a stats raw repository instance"""
        pass