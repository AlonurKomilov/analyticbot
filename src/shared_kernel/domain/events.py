"""
Shared Kernel Domain Events
===========================

Base classes and interfaces for domain events across all domains.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class DomainEvent(ABC):
    """
    Base class for all domain events.
    
    Domain events represent something important that happened
    in the domain that domain experts care about.
    """
    
    def __post_init__(self):
        if not hasattr(self, 'event_id') or self.event_id is None:
            self.event_id = str(uuid.uuid4())
        if not hasattr(self, 'occurred_on') or self.occurred_on is None:
            self.occurred_on = datetime.utcnow()
    
    @property
    @abstractmethod
    def event_name(self) -> str:
        """The name of the event (used for routing)"""
        pass
    
    def to_dict(self) -> dict:
        """Convert event to dictionary for serialization"""
        result = {
            'event_id': self.event_id,
            'event_name': self.event_name,
            'occurred_on': self.occurred_on.isoformat(),
        }
        
        # Add all dataclass fields except the base ones
        for key, value in self.__dict__.items():
            if key not in ['event_id', 'occurred_on']:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        
        return result
    
    def __str__(self) -> str:
        return f"{self.event_name}(id={self.event_id}, occurred={self.occurred_on})"