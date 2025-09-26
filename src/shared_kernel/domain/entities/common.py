"""
Common models and base classes for the core domain
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class BaseEntity:
    """Base entity for all domain models"""

    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class TimestampedEntity(BaseEntity):
    """Entity with automatic timestamp management"""
