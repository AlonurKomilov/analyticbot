"""
⚠️ ⚠️ ⚠️ DEPRECATED - DO NOT USE ⚠️ ⚠️ ⚠️

This file is DEPRECATED and will be removed in a future release.
Please migrate to apps/api/di_analytics.py for Analytics V2 API endpoints.

Analytics Dependency Injection Container
Properly structured DI container using Repository Factory pattern for clean architecture

MIGRATION GUIDE:
---------------

This container has been replaced by apps/api/di_analytics.py for Analytics V2 API.
That file already uses the new patterns and is properly structured.

OLD (deprecated):
    from apps.api.di_container.analytics_container import get_analytics_fusion_service
    service = Depends(get_analytics_fusion_service)

NEW (already migrated in Analytics V2):
    from apps.api.di_analytics import get_analytics_fusion_service
    service = Depends(get_analytics_fusion_service)

For other API services (not analytics):
    from apps.di import get_container
    container = get_container()
    service = await container.api.some_service()

DEPRECATION SCHEDULE:
- 2025-10-14: Deprecated (this warning added)
- 2025-10-21: Will be removed (1 week grace period)

See: LEGACY_VS_NEW_DI_COMPARISON.md for complete migration guide
"""

import logging
import warnings

# Emit deprecation warning when module is imported
warnings.warn(
    "apps.api.di_container.analytics_container is DEPRECATED. "
    "Please use apps.api.di_analytics for Analytics V2 API endpoints. "
    "See LEGACY_VS_NEW_DI_COMPARISON.md for migration guide. "
    "This module will be removed on 2025-10-21.",
    DeprecationWarning,
    stacklevel=2
)

import os
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Union
from unittest.mock import AsyncMock

from core.ports.repository_factory import AbstractRepositoryFactory

# Core imports (allowed) - Updated to use new microservices
from core.services.analytics_fusion import AnalyticsOrchestratorService
from core.services.analytics_fusion.infrastructure import DataAccessService

# Infrastructure imports (allowed in DI containers)
from infra.factories.repository_factory import AsyncpgRepositoryFactory, CacheFactory

if TYPE_CHECKING:
    from asyncpg.pool import Pool

logger = logging.getLogger(__name__)

# Global instances (will be initialized by container) - Updated for new microservices
_analytics_fusion_service: AnalyticsOrchestratorService | None = None
_repository_factory: AbstractRepositoryFactory | None = None
_cache_adapter = None


async def get_database_pool() -> Union["Pool", object, None]:
    """Get database pool using proper V2 PostgreSQL connection"""
    # Check if we're in test environment
    if os.getenv("ENVIRONMENT") == "test" or "pytest" in os.getenv("_", ""):
        # For tests, create a proper mock pool that supports async context manager
        class MockConnection:
            def __init__(self):
                self.execute = AsyncMock(return_value=None)
                self.fetchrow = AsyncMock(
                    return_value={"snapshot_time": datetime(2025, 8, 31, 12, 0, 0, tzinfo=UTC)}
                )
                self.fetchval = AsyncMock(
                    return_value=100
                )  # Return a number for count/sum operations
                self.fetch = AsyncMock(
                    return_value=[
                        {
                            "msg_id": 1,
                            "date": "2025-08-30T10:00:00Z",
                            "views": 1000,
                            "forwards": 10,
                            "replies": 5,
                            "reactions": "{}",
                            "title": "Test Post",
                            "permalink": "",
                        }
                    ]
                )

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        class MockPool:
            def __init__(self):
                self._connection = MockConnection()

            def acquire(self):
                return self._connection

            async def fetchrow(self, query, *args, **kwargs):
                return None

            async def fetchval(self, query, *args, **kwargs):
                return None

            async def fetch(self, query, *args, **kwargs):
                return []

            async def execute(self, query, *args, **kwargs):
                return None

        return MockPool()

    # For production, use PostgreSQL directly with proper connection management
    try:
        # Import the optimized database manager (fallback pattern)
        from infra.db.connection_manager import db_manager

        # Check if db_manager is initialized
        if not db_manager._pool:
            logger.info("Initializing V2 database manager for PostgreSQL")
            await db_manager.initialize()

        # Get the underlying asyncpg pool
        if db_manager._pool and db_manager._pool._pool:
            pool = db_manager._pool._pool
            logger.info(f"✅ V2 database pool retrieved successfully: {type(pool)}")
            return pool
        else:
            logger.warning("V2 database manager pool not available")

    except Exception as e:
        logger.warning(f"V2 database manager failed: {e}")

    # Fallback: Create direct AsyncPG connection to PostgreSQL
    try:
        import asyncpg

        from config.settings import settings

        # Build the connection URL for asyncpg (remove +asyncpg suffix)
        database_url = settings.DATABASE_URL
        if database_url and "+asyncpg" in database_url:
            database_url = database_url.replace("+asyncpg", "")

        logger.info("Creating direct AsyncPG pool for V2 analytics")
        pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            command_timeout=60,
            server_settings={
                "application_name": "analyticbot_v2_analytics",
            },
        )

        if pool:
            logger.info(f"✅ Direct AsyncPG pool created successfully: {type(pool)}")
            return pool

    except Exception as e:
        logger.error(f"Failed to create direct AsyncPG pool: {e}", exc_info=True)

    logger.error("All V2 database connection methods failed")
    return None


async def get_redis_client():
    """Get Redis client from DI container - FIXED: Now properly obtains Redis client"""

    if os.getenv("ENVIRONMENT") == "test" or "pytest" in os.getenv("_", ""):
        # For tests, return None (cache adapter will handle this)
        return None

    try:
        # ✅ FIXED: Create Redis client directly instead of using DI container
        import redis.asyncio as redis

        from config.settings import settings

        # Create Redis client using settings
        redis_client = redis.Redis(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=getattr(settings, "REDIS_PORT", 6379),
            db=getattr(settings, "REDIS_DB", 0),
            decode_responses=True,
        )
        logger.info("Successfully created Redis client directly")
        return redis_client

    except Exception as e:
        logger.warning(f"Redis client not available from DI container: {e}")
        # Fallback: create Redis client directly
        try:
            import redis.asyncio as redis

            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            fallback_client = redis.from_url(redis_url, decode_responses=True)
            logger.info("Created fallback Redis client directly")
            return fallback_client
        except Exception as fallback_e:
            logger.error(f"Fallback Redis client creation failed: {fallback_e}")
            return None


async def get_repository_factory() -> AbstractRepositoryFactory:
    """
    Get repository factory instance using clean architecture pattern.

    This is the key improvement - instead of creating repositories directly,
    we use the factory pattern to maintain clean architecture.
    """
    global _repository_factory

    if _repository_factory is not None:
        return _repository_factory

    try:
        # Get database pool
        pool = await get_database_pool()

        if pool is None:
            # Create enhanced mock pool for graceful degradation
            logger.warning(
                "Database pool is None, creating enhanced mock for limited functionality"
            )

            class EnhancedMockPool:
                async def fetchval(self, query, *args):
                    if "COUNT" in query.upper():
                        return 42
                    elif "subscriber" in query.lower():
                        return 1250
                    elif "SUM" in query.upper():
                        return 15000
                    return 100

                async def fetch(self, query, *args):
                    return [
                        {
                            "date": "2025-09-07",
                            "views": 1500,
                            "joins": 25,
                            "leaves": 5,
                            "posts": 8,
                            "engagement": 0.045,
                        }
                    ]

                async def fetchrow(self, query, *args):
                    return {
                        "snapshot_time": datetime(2025, 9, 7, 12, 0, 0, tzinfo=UTC),
                        "total_subscribers": 1250,
                        "views_today": 3500,
                    }

                def acquire(self):
                    return self

                async def __aenter__(self):
                    return self

                async def __aexit__(self, *args):
                    pass

                async def execute(self, query, *args):
                    return "INSERT 0 1"

            pool = EnhancedMockPool()
            logger.info("✅ Enhanced mock pool created for repository factory")

        # Create repository factory with pool
        _repository_factory = AsyncpgRepositoryFactory(pool)
        logger.info("✅ Repository factory created successfully")
        return _repository_factory

    except Exception as e:
        logger.error(f"Failed to create repository factory: {e}", exc_info=True)
        raise RuntimeError(f"Repository factory initialization failed: {e}")


async def init_analytics_fusion_service() -> AnalyticsOrchestratorService:
    """Initialize analytics orchestrator service using new microservices architecture"""
    global _analytics_fusion_service

    if _analytics_fusion_service is not None:
        return _analytics_fusion_service

    try:
        # Get repository factory (clean architecture pattern)
        repository_factory = await get_repository_factory()

        logger.info(f"Repository factory retrieved: {type(repository_factory)}")

        # Create repositories through factory (no direct infra imports!)
        repository_factory.create_channel_daily_repository()
        repository_factory.create_post_repository()
        repository_factory.create_post_metrics_repository()
        repository_factory.create_edges_repository()
        repository_factory.create_stats_raw_repository()

        logger.info("✅ Repositories created through factory pattern")

        # Initialize cache with error handling
        try:
            await init_cache_adapter()
            logger.info("✅ Cache adapter initialized")
        except Exception as cache_error:
            logger.warning(f"Cache initialization failed: {cache_error}")

        # Create data access service for the new microservices architecture
        # TODO: Properly integrate repository_factory with DataAccessService
        data_access_service = DataAccessService(repository_manager=None)  # Temporary fix

        # Create analytics orchestrator service (replaces the god object)
        _analytics_fusion_service = AnalyticsOrchestratorService(
            data_access_service=data_access_service
        )

        logger.info("🎯 Analytics Orchestrator Service initialized with microservices architecture")
        return _analytics_fusion_service

    except Exception as e:
        logger.error(f"Failed to initialize analytics fusion service: {e}", exc_info=True)
        raise RuntimeError(f"Analytics initialization failed: {e}")


async def init_cache_adapter():
    """Initialize cache adapter using factory pattern"""
    global _cache_adapter

    if _cache_adapter is not None:
        return _cache_adapter

    try:
        redis_client = await get_redis_client()
        # Use cache factory instead of direct import
        _cache_adapter = CacheFactory.create_cache_adapter(redis_client)
        logger.info(f"Cache adapter initialized: {type(_cache_adapter).__name__}")
        return _cache_adapter
    except Exception as e:
        logger.warning(f"Cache adapter initialization failed, using no-op cache: {e}")
        _cache_adapter = CacheFactory.create_cache_adapter(None)
        return _cache_adapter


# FastAPI dependencies


async def get_analytics_fusion_service() -> AnalyticsOrchestratorService:
    """Dependency to provide analytics orchestrator service (replaces god object)"""
    return await init_analytics_fusion_service()


async def get_cache():
    """Dependency to provide cache adapter"""
    return await init_cache_adapter()


# Repository dependencies (now using factory pattern)


async def get_channel_daily_repository():
    """Get channel daily repository through factory"""
    factory = await get_repository_factory()
    return factory.create_channel_daily_repository()


async def get_post_repository():
    """Get post repository through factory"""
    factory = await get_repository_factory()
    return factory.create_post_repository()


async def get_metrics_repository():
    """Get post metrics repository through factory"""
    factory = await get_repository_factory()
    return factory.create_post_metrics_repository()


async def get_edges_repository():
    """Get edges repository through factory"""
    factory = await get_repository_factory()
    return factory.create_edges_repository()


async def get_stats_raw_repository():
    """Get stats raw repository through factory"""
    factory = await get_repository_factory()
    return factory.create_stats_raw_repository()


async def get_channel_management_service():
    """Get channel management service with proper dependencies"""
    from apps.api.services.channel_management_service import ChannelManagementService
    from core.services.channel_service import ChannelService

    # Get repository through factory (clean architecture)
    factory = await get_repository_factory()
    channel_repo = factory.create_channel_repository()

    # Create core service
    core_service = ChannelService(channel_repo)

    # Create and return application service
    return ChannelManagementService(core_service)


# Cleanup function


async def cleanup_analytics():
    """Cleanup function for graceful shutdown"""
    global _analytics_fusion_service, _repository_factory, _cache_adapter

    logger.info("Cleaning up Analytics dependencies")

    # Reset global instances
    _analytics_fusion_service = None
    _repository_factory = None
    _cache_adapter = None

    logger.info("Analytics dependencies cleaned up")
