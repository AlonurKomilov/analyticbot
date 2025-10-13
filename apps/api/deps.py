"""
Dependency injection setup for FastAPI
Wires database connections to repositories to services using proper DI container
"""

import logging
from collections.abc import AsyncGenerator
from typing import Any

import asyncpg
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

from apps.shared.di import Settings as DISettings
from apps.shared.factory import get_repository_factory
from config import settings
from core.services import DeliveryService, ScheduleService

# Use repository factory instead of direct infra imports
# from infra.db.repositories.schedule_repository import (
#     AsyncpgDeliveryRepository,
#     AsyncpgScheduleRepository,
# )
# from infra.db.repositories.user_repository import AsyncpgUserRepository
# from infra.db.repositories.channel_repository import AsyncpgChannelRepository

# Security dependencies
security = HTTPBearer()


async def get_di_container():
    """Get configured DI container"""
    # Initialize container with application settings
    di_settings = DISettings(
        database_url=settings.get_database_url(),
        database_pool_size=settings.DB_POOL_SIZE,
        database_max_overflow=settings.DB_MAX_OVERFLOW,
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


async def get_user_repository():
    """Get user repository using factory pattern"""
    factory = get_repository_factory()
    return await factory.get_user_repository()


async def get_channel_repository():
    """Get channel repository using factory pattern"""
    factory = get_repository_factory()
    return await factory.get_channel_repository()


async def get_analytics_fusion_service():
    """
    Get analytics fusion service via API container
    """
    from apps.api.di_analytics import get_analytics_fusion_service

    return await get_analytics_fusion_service()


async def get_analytics_service():
    """Get analytics service via API container"""
    from apps.api.di import container

    return container.mock_analytics_service()


async def get_ai_insights_generator():
    """Get AI insights generator via API container"""
    from apps.api.di import container

    return container.mock_ai_service()


async def get_predictive_analytics_engine():
    """Get predictive analytics engine - FIXED: replaces container.resolve()"""

    # This would be registered in the DI container in a real implementation
    # For now, create a mock implementation
    class MockPredictiveEngine:
        async def predict_growth(self, **kwargs):
            return {"predictions": [], "confidence": 0.85}

        async def forecast_metrics(self, **kwargs):
            return {"forecasts": [], "accuracy": 0.80}

    return MockPredictiveEngine()


async def get_advanced_data_processor():
    """Get advanced data processor - FIXED: replaces container.resolve()"""

    # This would be registered in the DI container in a real implementation
    # For now, create a mock implementation
    class MockDataProcessor:
        async def process_advanced_metrics(self, **kwargs):
            return {"processed_data": {}, "metadata": {}}

    return MockDataProcessor()


async def get_redis_client():
    """Get Redis client via API container"""
    from apps.api.di import container

    return container.cache_service()


# Repository dependency providers with proper pool injection


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


# Repository dependencies - using factory pattern instead of direct infra imports
async def get_schedule_repository():
    """Get schedule repository using DI container"""
    try:
        # TODO: Schedule repository not implemented yet
        logger.warning("Schedule repository not implemented")
        return None
    except Exception as e:
        logger.warning(f"Failed to get schedule repository: {e}")
        return None


async def get_delivery_repository():
    """Get delivery repository using DI container"""
    try:
        # TODO: Delivery repository not implemented yet
        logger.warning("Delivery repository not implemented")
        return None
    except Exception as e:
        logger.warning(f"Failed to get delivery repository: {e}")
        return None


# Service dependencies - using factory pattern with flexible types
async def get_schedule_service(
    schedule_repo: Any = Depends(get_schedule_repository),
) -> ScheduleService:
    """Get schedule service with repository dependency injection"""
    return ScheduleService(schedule_repo)


async def get_delivery_service(
    delivery_repo: Any = Depends(get_delivery_repository),
    schedule_repo: Any = Depends(get_schedule_repository),
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
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Get current authenticated user with proper JWT validation"""
    # Import the proper auth implementation
    from apps.api.middleware.auth import get_current_user as auth_get_current_user

    # Get user repository dependency with proper pool injection
    user_repo = await get_user_repository()

    # Call the proper authentication function
    return await auth_get_current_user(credentials, user_repo)
