"""
Database connection management for PostgreSQL
"""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg
from asyncpg import Connection, Pool

logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool: Pool | None = None


async def create_connection_pool() -> Pool:
    """Create and return a connection pool"""
    global _connection_pool

    if _connection_pool is None:
        database_url = os.getenv(
            "DATABASE_URL", "postgresql://postgres:password@localhost:5432/analyticbot"
        )

        logger.info("Creating database connection pool")
        _connection_pool = await asyncpg.create_pool(
            database_url,
            min_size=1,
            max_size=10,
            command_timeout=60,
        )

    return _connection_pool


async def get_connection_pool() -> Pool:
    """Get the global connection pool, creating it if necessary"""
    global _connection_pool

    if _connection_pool is None:
        _connection_pool = await create_connection_pool()

    if _connection_pool is None:
        raise RuntimeError("Failed to create database connection pool")

    return _connection_pool


@asynccontextmanager
async def get_db_connection() -> AsyncGenerator[Connection, None]:
    """Get a database connection from the pool"""
    pool = await get_connection_pool()

    async with pool.acquire() as connection:
        yield connection


async def close_connection_pool():
    """Close the connection pool"""
    global _connection_pool

    if _connection_pool:
        logger.info("Closing database connection pool")
        await _connection_pool.close()
        _connection_pool = None


# For backwards compatibility
async def get_db() -> AsyncGenerator[Connection, None]:
    """Alias for get_db_connection"""
    async with get_db_connection() as conn:
        yield conn
