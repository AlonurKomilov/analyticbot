"""
Common models and base classes for the core domain
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BaseEntity:
    """Base entity for all domain models"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class TimestampedEntity(BaseEntity):
    """Entity with automatic timestamp management"""
    pass
