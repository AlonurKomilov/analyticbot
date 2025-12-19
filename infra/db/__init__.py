"""
Database Infrastructure Layer
=============================

Complete database infrastructure for the AnalyticBot system.

Structure:
    connection.py        - Basic asyncpg pool (legacy)
    connection_manager.py - Advanced pool with health monitoring ⭐
    performance.py       - Redis caching, query optimization
    health_utils.py      - Database health checks
    metadata.py          - SQLAlchemy metadata for Alembic
    sqlite_engine.py     - SQLite for development/testing

    adapters/           - Hexagonal architecture bridges
    models/             - ORM models (organized by domain)
    repositories/       - Data access layer
    alembic/            - Database migrations

Usage:
    from infra.db.connection_manager import db_manager
    
    # Initialize
    await db_manager.initialize()
    
    # Use connection
    async with db_manager.connection() as conn:
        result = await conn.fetch("SELECT * FROM users")
    
    # Health check
    health = await db_manager.health_check()
"""

from .connection_manager import db_manager, init_database, close_database
from .metadata import metadata

__all__ = [
    "db_manager",
    "init_database", 
    "close_database",
    "metadata",
]
