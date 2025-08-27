"""
Base ORM Models
Common base classes for SQLAlchemy models
"""

from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base

# Create the base class for all ORM models
BaseORMModel = declarative_base()


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseTimestampedModel(BaseORMModel, TimestampMixin):
    """Base model with timestamp fields"""
    __abstract__ = True


# For backward compatibility
Base = BaseORMModel
