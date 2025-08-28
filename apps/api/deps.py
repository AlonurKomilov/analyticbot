"""
Dependency injection setup for FastAPI
Wires database connections to repositories to services
"""

from collections.abc import AsyncGenerator

import asyncpg
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings
from infra.db.repositories.schedule_repository import AsyncpgScheduleRepository, AsyncpgDeliveryRepository
from core.services import DeliveryService, ScheduleService

# Database connection dependency
_db_pool = None

# Security dependencies
security = HTTPBearer()


async def get_db_pool() -> asyncpg.Pool:
    """Get or create database connection pool"""
    global _db_pool

    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=settings.DB_POOL_SIZE,
            max_size=settings.DB_MAX_OVERFLOW,
            command_timeout=settings.DB_POOL_TIMEOUT,
        )

    return _db_pool


async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get database connection from pool"""
    pool = await get_db_pool()
    async with pool.acquire() as connection:
        yield connection


# Repository dependencies
async def get_schedule_repository(
    db: asyncpg.Connection = Depends(get_db_connection),
) -> AsyncpgScheduleRepository:
    """Get schedule repository with database dependency"""
    return AsyncpgScheduleRepository(db)


async def get_delivery_repository(
    db: asyncpg.Connection = Depends(get_db_connection),
) -> AsyncpgDeliveryRepository:
    """Get delivery repository with database dependency"""
    return AsyncpgDeliveryRepository(db)


# Service dependencies
async def get_schedule_service(
    schedule_repo: AsyncpgScheduleRepository = Depends(get_schedule_repository),
) -> ScheduleService:
    """Get schedule service with repository dependency injection"""
    return ScheduleService(schedule_repo)


async def get_delivery_service(
    delivery_repo: AsyncpgDeliveryRepository = Depends(get_delivery_repository),
    schedule_repo: AsyncpgScheduleRepository = Depends(get_schedule_repository),
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


# Authentication dependency (placeholder for now)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated user (placeholder implementation)"""
    # TODO: Implement proper JWT validation and user lookup
    # For now, return a mock user for development
    return {
        "id": "user_123",
        "username": "dev_user",
        "tier": "pro"  # free, basic, pro, enterprise
    }
