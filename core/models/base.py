"""
Base Domain Models  
Pure domain models without framework dependencies
"""

from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseEntity:
    """Base class for all domain entities"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


# For backward compatibility with existing code
TimestampMixin = BaseEntity
BaseTimestampedModel = BaseEntity 
Base = BaseEntity
BaseORMModel = BaseEntity
