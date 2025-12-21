"""
Cached Query Wrappers for Hot Paths

Phase 3 Scaling: Provides caching layer for frequently accessed data.
Uses QueryCacheManager from DI container for 70-90% cache hit rates.

Usage:
    from infra.db.scaling.cached_queries import (
        get_cached_user,
        get_cached_channel,
        invalidate_user_cache,
    )
    
    # In your service:
    user = await get_cached_user(user_id, user_repo)
    
    # After user update:
    await invalidate_user_cache(user_id)

Design Decision: Wrapper approach instead of decorators on repositories
- Safer: No modification to existing repository code
- Flexible: Can be adopted incrementally 
- Testable: Easy to mock cache in tests
- Reversible: Can disable caching per-call
"""

import hashlib
import json
import logging
from typing import Any, Callable, TypeVar

from infra.db.scaling.cache_manager import CacheKey, CacheTier, QueryCacheManager

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Global cache manager reference (set by DI at startup)
_cache_manager: QueryCacheManager | None = None


def set_cache_manager(manager: QueryCacheManager | None) -> None:
    """Set the global cache manager (called from DI initialization)"""
    global _cache_manager
    _cache_manager = manager
    if manager:
        logger.info("✅ Cache manager configured for cached queries")


def get_cache_manager() -> QueryCacheManager | None:
    """Get the global cache manager"""
    return _cache_manager


# ============================================================================
# USER CACHING
# ============================================================================


async def get_cached_user(
    user_id: int,
    fetch_func: Callable[..., Any],
    *args,
    bypass_cache: bool = False,
    **kwargs,
) -> dict | None:
    """
    Get user with caching (STANDARD tier - 5 min TTL).
    
    Args:
        user_id: User ID to fetch
        fetch_func: Repository function to call on cache miss
        *args, **kwargs: Arguments to pass to fetch_func
        bypass_cache: If True, always fetch from DB
        
    Returns:
        User dict or None
    """
    if bypass_cache or not _cache_manager:
        return await fetch_func(*args, **kwargs)
    
    cache_key = f"user:{user_id}"
    
    # Try cache first
    cached = await _cache_manager.get(cache_key)
    if cached is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return cached
    
    # Cache miss - fetch from DB
    logger.debug(f"Cache MISS: {cache_key}")
    result = await fetch_func(*args, **kwargs)
    
    if result is not None:
        await _cache_manager.set(cache_key, result, tier=CacheTier.STANDARD, tags=["user", f"user:{user_id}"])
    
    return result


async def get_cached_user_by_telegram_id(
    telegram_id: int,
    fetch_func: Callable[..., Any],
    *args,
    bypass_cache: bool = False,
    **kwargs,
) -> dict | None:
    """Get user by Telegram ID with caching (STANDARD tier)"""
    if bypass_cache or not _cache_manager:
        return await fetch_func(*args, **kwargs)
    
    cache_key = f"user:tg:{telegram_id}"
    
    cached = await _cache_manager.get(cache_key)
    if cached is not None:
        return cached
    
    result = await fetch_func(*args, **kwargs)
    
    if result is not None:
        await _cache_manager.set(cache_key, result, tier=CacheTier.STANDARD, tags=["user", f"tg:{telegram_id}"])
    
    return result


async def invalidate_user_cache(user_id: int, telegram_id: int | None = None) -> None:
    """Invalidate user cache entries"""
    if not _cache_manager:
        return
    
    await _cache_manager.invalidate(f"user:{user_id}")
    if telegram_id:
        await _cache_manager.invalidate(f"user:tg:{telegram_id}")
    await _cache_manager.invalidate_by_tag(f"user:{user_id}")


# ============================================================================
# CHANNEL CACHING
# ============================================================================


async def get_cached_channel(
    channel_id: int,
    fetch_func: Callable[..., Any],
    *args,
    bypass_cache: bool = False,
    **kwargs,
) -> dict | None:
    """
    Get channel with caching (WARM tier - 2 min TTL).
    
    Channels change more frequently than users, so shorter TTL.
    """
    if bypass_cache or not _cache_manager:
        return await fetch_func(*args, **kwargs)
    
    cache_key = f"channel:{channel_id}"
    
    cached = await _cache_manager.get(cache_key)
    if cached is not None:
        return cached
    
    result = await fetch_func(*args, **kwargs)
    
    if result is not None:
        await _cache_manager.set(cache_key, result, tier=CacheTier.WARM, tags=["channel", f"channel:{channel_id}"])
    
    return result


async def get_cached_user_channels(
    user_id: int,
    fetch_func: Callable[..., Any],
    *args,
    bypass_cache: bool = False,
    **kwargs,
) -> list[dict]:
    """Get user's channels with caching (WARM tier)"""
    if bypass_cache or not _cache_manager:
        return await fetch_func(*args, **kwargs) or []
    
    cache_key = f"channels:user:{user_id}"
    
    cached = await _cache_manager.get(cache_key)
    if cached is not None:
        return cached
    
    result = await fetch_func(*args, **kwargs) or []
    
    await _cache_manager.set(cache_key, result, tier=CacheTier.WARM, tags=["channels", f"user:{user_id}"])
    
    return result


async def invalidate_channel_cache(channel_id: int, user_id: int | None = None) -> None:
    """Invalidate channel cache entries"""
    if not _cache_manager:
        return
    
    await _cache_manager.invalidate(f"channel:{channel_id}")
    await _cache_manager.invalidate_by_tag(f"channel:{channel_id}")
    
    if user_id:
        await _cache_manager.invalidate(f"channels:user:{user_id}")


# ============================================================================
# CHANNEL STATS CACHING (HOT PATH - 30s TTL)
# ============================================================================


async def get_cached_channel_stats(
    channel_id: int,
    fetch_func: Callable[..., Any],
    *args,
    bypass_cache: bool = False,
    **kwargs,
) -> dict | None:
    """
    Get channel stats with caching (HOT tier - 30s TTL).
    
    Stats are queried very frequently but change often.
    Short TTL ensures freshness while reducing DB load.
    """
    if bypass_cache or not _cache_manager:
        return await fetch_func(*args, **kwargs)
    
    cache_key = f"stats:channel:{channel_id}"
    
    cached = await _cache_manager.get(cache_key)
    if cached is not None:
        return cached
    
    result = await fetch_func(*args, **kwargs)
    
    if result is not None:
        await _cache_manager.set(cache_key, result, tier=CacheTier.HOT, tags=["stats", f"channel:{channel_id}"])
    
    return result


async def invalidate_channel_stats_cache(channel_id: int) -> None:
    """Invalidate channel stats cache"""
    if not _cache_manager:
        return
    
    await _cache_manager.invalidate(f"stats:channel:{channel_id}")


# ============================================================================
# SUBSCRIPTION/CREDITS CACHING
# ============================================================================


async def get_cached_user_subscription(
    user_id: int,
    fetch_func: Callable[..., Any],
    *args,
    bypass_cache: bool = False,
    **kwargs,
) -> dict | None:
    """Get user subscription with caching (WARM tier - 2 min TTL)"""
    if bypass_cache or not _cache_manager:
        return await fetch_func(*args, **kwargs)
    
    cache_key = f"subscription:{user_id}"
    
    cached = await _cache_manager.get(cache_key)
    if cached is not None:
        return cached
    
    result = await fetch_func(*args, **kwargs)
    
    if result is not None:
        await _cache_manager.set(cache_key, result, tier=CacheTier.WARM, tags=["subscription", f"user:{user_id}"])
    
    return result


async def get_cached_user_credits(
    user_id: int,
    fetch_func: Callable[..., Any],
    *args,
    bypass_cache: bool = False,
    **kwargs,
) -> int:
    """Get user credits with caching (WARM tier - 2 min TTL)"""
    if bypass_cache or not _cache_manager:
        result = await fetch_func(*args, **kwargs)
        return result if result is not None else 0
    
    cache_key = f"credits:{user_id}"
    
    cached = await _cache_manager.get(cache_key)
    if cached is not None:
        return cached
    
    result = await fetch_func(*args, **kwargs)
    result = result if result is not None else 0
    
    await _cache_manager.set(cache_key, result, tier=CacheTier.WARM, tags=["credits", f"user:{user_id}"])
    
    return result


async def invalidate_user_subscription_cache(user_id: int) -> None:
    """Invalidate user subscription and credit caches"""
    if not _cache_manager:
        return
    
    await _cache_manager.invalidate(f"subscription:{user_id}")
    await _cache_manager.invalidate(f"credits:{user_id}")


# ============================================================================
# MARKETPLACE CACHING (COLD TIER - 15 min TTL)
# ============================================================================


async def get_cached_marketplace_services(
    fetch_func: Callable[..., Any],
    *args,
    bypass_cache: bool = False,
    **kwargs,
) -> list[dict]:
    """Get marketplace services list (COLD tier - rarely changes)"""
    if bypass_cache or not _cache_manager:
        return await fetch_func(*args, **kwargs) or []
    
    cache_key = "marketplace:services"
    
    cached = await _cache_manager.get(cache_key)
    if cached is not None:
        return cached
    
    result = await fetch_func(*args, **kwargs) or []
    
    await _cache_manager.set(cache_key, result, tier=CacheTier.COLD, tags=["marketplace"])
    
    return result


async def invalidate_marketplace_cache() -> None:
    """Invalidate marketplace cache"""
    if not _cache_manager:
        return
    
    await _cache_manager.invalidate_by_tag("marketplace")


# ============================================================================
# SYSTEM/CONFIG CACHING (STATIC TIER - 1 hour TTL)
# ============================================================================


async def get_cached_feature_flags(
    fetch_func: Callable[..., Any],
    *args,
    bypass_cache: bool = False,
    **kwargs,
) -> dict:
    """Get feature flags (STATIC tier - almost never changes)"""
    if bypass_cache or not _cache_manager:
        return await fetch_func(*args, **kwargs) or {}
    
    cache_key = "system:feature_flags"
    
    cached = await _cache_manager.get(cache_key)
    if cached is not None:
        return cached
    
    result = await fetch_func(*args, **kwargs) or {}
    
    await _cache_manager.set(cache_key, result, tier=CacheTier.STATIC, tags=["system"])
    
    return result


async def invalidate_feature_flags_cache() -> None:
    """Invalidate feature flags cache (call after admin changes)"""
    if not _cache_manager:
        return
    
    await _cache_manager.invalidate("system:feature_flags")


# ============================================================================
# RATE LIMITING CACHE (HOT TIER - 30s TTL)
# ============================================================================


async def get_cached_rate_limit(
    user_id: int,
    action: str,
    fetch_func: Callable[..., Any],
    *args,
    bypass_cache: bool = False,
    **kwargs,
) -> dict:
    """Get rate limit info (HOT tier - needs fresh data)"""
    if bypass_cache or not _cache_manager:
        return await fetch_func(*args, **kwargs) or {}
    
    cache_key = f"ratelimit:{user_id}:{action}"
    
    cached = await _cache_manager.get(cache_key)
    if cached is not None:
        return cached
    
    result = await fetch_func(*args, **kwargs) or {}
    
    await _cache_manager.set(cache_key, result, tier=CacheTier.HOT, tags=["ratelimit", f"user:{user_id}"])
    
    return result


# ============================================================================
# GENERIC CACHED QUERY
# ============================================================================


async def cached_query(
    cache_key: str,
    fetch_func: Callable[..., T],
    *args,
    tier: CacheTier = CacheTier.STANDARD,
    tags: list[str] | None = None,
    bypass_cache: bool = False,
    **kwargs,
) -> T | None:
    """
    Generic cached query wrapper.
    
    Use for custom queries not covered by specific wrappers.
    
    Example:
        result = await cached_query(
            f"custom:{user_id}:{channel_id}",
            some_repo.complex_query,
            user_id, channel_id,
            tier=CacheTier.WARM,
            tags=["custom", f"user:{user_id}"]
        )
    """
    if bypass_cache or not _cache_manager:
        return await fetch_func(*args, **kwargs)
    
    cached = await _cache_manager.get(cache_key)
    if cached is not None:
        return cached
    
    result = await fetch_func(*args, **kwargs)
    
    if result is not None:
        await _cache_manager.set(cache_key, result, tier=tier, tags=tags)
    
    return result


# ============================================================================
# CACHE STATISTICS
# ============================================================================


async def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics for monitoring"""
    if not _cache_manager:
        return {"enabled": False, "reason": "Cache manager not configured"}
    
    stats = await _cache_manager.get_stats()
    stats["enabled"] = True
    return stats
