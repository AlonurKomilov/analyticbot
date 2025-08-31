"""
Dependency Injection for Analytics V2
Provides dependencies for the Analytics Fusion API
"""

import logging
from typing import Optional
from fastapi import Depends

from core.services.analytics_fusion_service import AnalyticsFusionService
from infrastructure.cache.redis_cache import create_cache_adapter
from infra.db.repositories.channel_daily_repository import AsyncpgChannelDailyRepository
from infra.db.repositories.post_repository import AsyncpgPostRepository
from infra.db.repositories.post_metrics_repository import AsyncpgPostMetricsRepository
from infra.db.repositories.edges_repository import AsyncpgEdgesRepository
from infra.db.repositories.stats_raw_repository import AsyncpgStatsRawRepository

logger = logging.getLogger(__name__)

# Global instances (will be initialized by container)
_analytics_fusion_service: Optional[AnalyticsFusionService] = None
_cache_adapter = None


async def get_database_pool():
    """Get database pool - to be implemented with existing container"""
    # This should be integrated with the existing container system
    # For now, raise an error to indicate it needs to be wired
    from apps.bot.container import container
    return await container.resolve("database_pool")


async def get_redis_client():
    """Get Redis client - to be implemented with existing container"""
    try:
        # Try to get Redis client from existing container if available
        from apps.bot.container import container
        return await container.resolve("redis_client")
    except Exception as e:
        logger.warning(f"Redis client not available: {e}")
        return None


async def init_analytics_fusion_service():
    """Initialize analytics fusion service with all dependencies"""
    global _analytics_fusion_service
    
    if _analytics_fusion_service is not None:
        return _analytics_fusion_service
    
    try:
        # Get database pool
        pool = await get_database_pool()
        
        # Initialize repositories
        channel_daily_repo = AsyncpgChannelDailyRepository(pool)
        post_repo = AsyncpgPostRepository(pool)
        metrics_repo = AsyncpgPostMetricsRepository(pool)
        edges_repo = AsyncpgEdgesRepository(pool)
        stats_raw_repo = AsyncpgStatsRawRepository(pool)
        
        # Create service
        _analytics_fusion_service = AnalyticsFusionService(
            channel_daily_repo=channel_daily_repo,
            post_repo=post_repo,
            metrics_repo=metrics_repo,
            edges_repo=edges_repo,
            stats_raw_repo=stats_raw_repo
        )
        
        logger.info("Analytics fusion service initialized successfully")
        return _analytics_fusion_service
        
    except Exception as e:
        logger.error(f"Failed to initialize analytics fusion service: {e}")
        raise


async def init_cache_adapter():
    """Initialize cache adapter"""
    global _cache_adapter
    
    if _cache_adapter is not None:
        return _cache_adapter
    
    try:
        redis_client = await get_redis_client()
        _cache_adapter = create_cache_adapter(redis_client)
        logger.info(f"Cache adapter initialized: {type(_cache_adapter).__name__}")
        return _cache_adapter
    except Exception as e:
        logger.warning(f"Cache adapter initialization failed, using no-op cache: {e}")
        _cache_adapter = create_cache_adapter(None)
        return _cache_adapter


# FastAPI dependencies

async def get_analytics_fusion_service() -> AnalyticsFusionService:
    """Dependency to provide analytics fusion service"""
    return await init_analytics_fusion_service()


async def get_cache():
    """Dependency to provide cache adapter"""
    return await init_cache_adapter()


# Repository dependencies (for direct access if needed)

async def get_channel_daily_repository():
    """Get channel daily repository"""
    pool = await get_database_pool()
    return AsyncpgChannelDailyRepository(pool)


async def get_post_repository():
    """Get post repository"""
    pool = await get_database_pool()
    return AsyncpgPostRepository(pool)


async def get_metrics_repository():
    """Get post metrics repository"""
    pool = await get_database_pool()
    return AsyncpgPostMetricsRepository(pool)


async def get_edges_repository():
    """Get edges repository"""
    pool = await get_database_pool()
    return AsyncpgEdgesRepository(pool)


async def get_stats_raw_repository():
    """Get stats raw repository"""
    pool = await get_database_pool()
    return AsyncpgStatsRawRepository(pool)


# Cleanup function

async def cleanup_analytics_v2():
    """Cleanup function for graceful shutdown"""
    global _analytics_fusion_service, _cache_adapter
    
    logger.info("Cleaning up Analytics V2 dependencies")
    
    # Reset global instances
    _analytics_fusion_service = None
    _cache_adapter = None
    
    logger.info("Analytics V2 dependencies cleaned up")
