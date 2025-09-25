"""
Dependency injection setup for FastAPI
Wires database connections to repositories to services using proper DI container
"""

import logging
from collections.abc import AsyncGenerator
from typing import AsyncContextManager

import asyncpg
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

from config import settings
from core.services import DeliveryService, ScheduleService
from apps.shared.di import get_container, Settings as DISettings
from infra.db.repositories.schedule_repository import (
    AsyncpgDeliveryRepository,
    AsyncpgScheduleRepository,
)
from infra.db.repositories.user_repository import AsyncpgUserRepository
from infra.db.repositories.channel_repository import AsyncpgChannelRepository

# Security dependencies
security = HTTPBearer()


async def get_di_container():
    """Get configured DI container"""
    # Initialize container with application settings
    di_settings = DISettings(
        database_url=settings.DATABASE_URL,
        database_pool_size=settings.DB_POOL_SIZE,
        database_max_overflow=settings.DB_MAX_OVERFLOW
    )
    from apps.shared.di import init_container
    return init_container(di_settings)


async def get_asyncpg_pool() -> asyncpg.Pool:
    """
    Get asyncpg pool from DI container
    This replaces the manual pool creation with proper DI
    """
    container = await get_di_container()
    return await container.asyncpg_pool()


async def get_user_repository(pool: asyncpg.Pool = Depends(get_asyncpg_pool)) -> AsyncpgUserRepository:
    """Get user repository with proper pool injection"""
    return AsyncpgUserRepository(pool)


async def get_channel_repository(pool: asyncpg.Pool = Depends(get_asyncpg_pool)) -> AsyncpgChannelRepository:
    """Get channel repository with proper pool injection"""
    return AsyncpgChannelRepository(pool)


# Legacy database connection dependency - now uses DI container
_db_pool: asyncpg.Pool | None = None


async def get_db_pool() -> asyncpg.Pool:
    """Get or create database connection pool - uses DI container"""
    return await get_asyncpg_pool()


async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get database connection from pool"""
    pool = await get_db_pool()
    async with pool.acquire() as connection:
        yield connection


# Repository dependencies - now with proper pool injection
async def get_schedule_repository(
    pool: asyncpg.Pool = Depends(get_asyncpg_pool),
) -> AsyncpgScheduleRepository:
    """Get schedule repository with database dependency"""
    return AsyncpgScheduleRepository(pool)


async def get_delivery_repository(
    pool: asyncpg.Pool = Depends(get_asyncpg_pool),
) -> AsyncpgDeliveryRepository:
    """Get delivery repository with database dependency"""
    return AsyncpgDeliveryRepository(pool)


# Service dependencies - now using DI container
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


# Cleanup function for application shutdown - uses DI container
async def cleanup_db_pool():
    """Clean up database pool on application shutdown"""
    try:
        container = await get_di_container()
        await container.close()
        logger.info("Database pool cleanup completed")
    except Exception as e:
        logger.error(f"Database cleanup error: {e}")


# Authentication dependency - implement proper JWT validation
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated user with proper JWT validation"""
    # Import the proper auth implementation
    from apps.api.middleware.auth import get_current_user as auth_get_current_user
    
    # Get user repository dependency with proper pool injection
    user_repo = await get_user_repository()
    
    # Call the proper authentication function
    return await auth_get_current_user(credentials, user_repo)
