"""
Base Domain Models
Pure domain models without framework dependencies
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class BaseEntity:
    """Base class for all domain entities"""

    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

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
