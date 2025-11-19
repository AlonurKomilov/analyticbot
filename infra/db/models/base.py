"""
SQLAlchemy Declarative Base

This module provides the base class for all ORM models in the application.
It should be imported by all model files to ensure they all use the same metadata.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all database models.

    All ORM models should inherit from this class to:
    - Share the same metadata registry
    - Enable Alembic migrations to detect all tables
    - Maintain consistent table structure
    """

    pass
