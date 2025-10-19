"""
Cache Services DI Container

Single Responsibility: Redis and cache adapter management
Phase 2 Fix (Oct 19, 2025): Updated to use protocols instead of concrete implementations
"""

import logging
import os

from dependency_injector import containers, providers

# ✅ PHASE 2 FIX: Import protocol instead of only concrete implementation
from core.protocols import CacheProtocol

logger = logging.getLogger(__name__)


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================


async def _create_redis_client():
    """Create Redis client (optional)"""
    if os.getenv("ENVIRONMENT") == "test" or "pytest" in os.getenv("_", ""):
        return None

    try:
        import redis.asyncio as redis

        from config.settings import settings

        return redis.Redis(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=getattr(settings, "REDIS_PORT", 6379),
            db=getattr(settings, "REDIS_DB", 0),
            decode_responses=True,
        )
    except Exception as e:
        logger.warning(f"Redis not available: {e}")
        return None


async def _create_cache_adapter(redis_client=None) -> CacheProtocol | None:
    """Create cache adapter using factory (returns protocol interface)"""
    try:
        # Still need concrete factory for instantiation
        from infra.factories.repository_factory import CacheFactory

        return CacheFactory.create_cache_adapter(redis_client)
    except Exception as e:
        logger.warning(f"Cache adapter creation failed: {e}")
        return None


# ============================================================================
# CACHE CONTAINER
# ============================================================================


class CacheContainer(containers.DeclarativeContainer):
    """
    Cache Services Container

    Single Responsibility: Manages Redis client and cache adapters
    Optional services - gracefully degrades to in-memory cache if Redis unavailable
    """

    config = providers.Configuration()

    # ============================================================================
    # REDIS & CACHE
    # ============================================================================

    redis_client = providers.Resource(_create_redis_client)

    cache_adapter = providers.Resource(_create_cache_adapter, redis_client=redis_client)
