"""
Dependency injection setup for FastAPI
Wires database connections to repositories to services
"""
from typing import AsyncGenerator
import asyncpg
from fastapi import Depends

from config import settings
from core.repositories.postgres import PgScheduleRepository, PgDeliveryRepository
from core.services import ScheduleService, DeliveryService


# Database connection dependency
_db_pool = None


async def get_db_pool() -> asyncpg.Pool:
    """Get or create database connection pool"""
    global _db_pool
    
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=settings.DB_POOL_SIZE,
            max_size=settings.DB_MAX_OVERFLOW,
            command_timeout=settings.DB_POOL_TIMEOUT
        )
    
    return _db_pool


async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get database connection from pool"""
    pool = await get_db_pool()
    async with pool.acquire() as connection:
        yield connection


# Repository dependencies
async def get_schedule_repository(
    db: asyncpg.Connection = Depends(get_db_connection)
) -> PgScheduleRepository:
    """Get schedule repository with database dependency"""
    return PgScheduleRepository(db)


async def get_delivery_repository(
    db: asyncpg.Connection = Depends(get_db_connection)
) -> PgDeliveryRepository:
    """Get delivery repository with database dependency"""
    return PgDeliveryRepository(db)


# Service dependencies
async def get_schedule_service(
    schedule_repo: PgScheduleRepository = Depends(get_schedule_repository)
) -> ScheduleService:
    """Get schedule service with repository dependency injection"""
    return ScheduleService(schedule_repo)


async def get_delivery_service(
    delivery_repo: PgDeliveryRepository = Depends(get_delivery_repository),
    schedule_repo: PgScheduleRepository = Depends(get_schedule_repository)
) -> DeliveryService:
    """Get delivery service with repository dependency injection"""
    return DeliveryService(delivery_repo, schedule_repo)


# Cleanup function for application shutdown
async def cleanup_db_pool():
    """Clean up database pool on application shutdown"""
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None
