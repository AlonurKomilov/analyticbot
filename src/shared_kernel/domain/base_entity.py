"""
Base Entity - Foundation for all domain entities
"""

from abc import ABC
from datetime import datetime
from typing import Any, Generic, TypeVar

EntityId = TypeVar("EntityId")


class BaseEntity(Generic[EntityId], ABC):
    """
    Base class for all domain entities.
    
    Provides:
    - Identity management
    - Domain events handling
    - Timestamp tracking
    """
    
    def __init__(self, id: EntityId):
        self.id = id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self._domain_events = []
    
    def add_domain_event(self, event) -> None:
        """Add a domain event to be published"""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> None:
        """Clear all domain events (typically after publishing)"""
        self._domain_events.clear()
    
    def get_domain_events(self) -> list:
        """Get all pending domain events"""
        return self._domain_events.copy()
    
    def mark_as_updated(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other: Any) -> bool:
        """Entities are equal if they have the same ID and type"""
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on entity ID"""
        return hash((self.__class__, self.id))


class AggregateRoot(BaseEntity):
    """
    Base class for aggregate roots.
    
    Aggregate roots are the entry points for domain operations
    and are responsible for maintaining consistency.
    """
    
    def __init__(self, id):
        super().__init__(id)
        self.version = 1
    
    def increment_version(self) -> None:
        """Increment version for optimistic locking"""
        self.version += 1
        self.mark_as_updated()