"""
Base Repository - Infrastructure abstraction for data access
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any
from ..domain.base_entity import BaseEntity

EntityType = TypeVar("EntityType", bound=BaseEntity)
EntityId = TypeVar("EntityId")


class BaseRepository(Generic[EntityType, EntityId], ABC):
    """
    Base repository interface for data access operations.
    
    This provides a common contract for all repositories
    while allowing different implementations (PostgreSQL, MongoDB, etc.)
    """
    
    @abstractmethod
    async def get_by_id(self, entity_id: EntityId) -> Optional[EntityType]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def save(self, entity: EntityType) -> EntityType:
        """Save entity (create or update)"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: EntityId) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: EntityId) -> bool:
        """Check if entity exists"""
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[EntityType]:
        """Get all entities with pagination"""
        pass


class UnitOfWork(ABC):
    """
    Unit of Work pattern for managing database transactions
    across multiple repositories.
    """
    
    @abstractmethod
    async def __aenter__(self):
        """Enter async context manager"""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager"""
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        """Commit the transaction"""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the transaction"""
        pass