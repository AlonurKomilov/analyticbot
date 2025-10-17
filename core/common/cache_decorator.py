"""
Redis Cache Decorator for FastAPI Endpoints
Provides automatic caching with TTL, error handling, and cache invalidation
"""

import json
import logging
from collections.abc import Callable
from functools import wraps

import redis.asyncio as redis
from fastapi import Request

logger = logging.getLogger(__name__)

# Redis connection (use existing Redis from config)
redis_client: redis.Redis | None = None


async def init_cache_redis(redis_url: str = "redis://localhost:10200/1"):
    """Initialize Redis connection for caching"""
    global redis_client
    try:
        redis_client = await redis.from_url(redis_url, decode_responses=True)
        # Test connection
        await redis_client.ping()
        logger.info(f"✅ Cache Redis initialized: {redis_url}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize cache Redis: {e}")
        redis_client = None


def generate_cache_key(prefix: str, request: Request) -> str:
    """
    Generate unique cache key based on endpoint and user

    Example: "cache:auth:me:user_123"
    """
    # Get user ID from request state (set by auth middleware)
    user_id = getattr(request.state, "user_id", "anonymous")

    cache_key = f"cache:{prefix}:user_{user_id}"
    return cache_key


def cache_endpoint(
    prefix: str,
    ttl: int = 300,  # 5 minutes default
    include_user: bool = True,
):
    """
    Decorator to cache endpoint responses in Redis

    Usage:
        @cache_endpoint(prefix="auth:me", ttl=300)
        async def get_current_user(request: Request):
            # ... expensive operation ...
            return user_data

    Args:
        prefix: Cache key prefix (e.g., "auth:me", "analytics:channels")
        ttl: Time-to-live in seconds (default: 300 = 5 minutes)
        include_user: Include user_id in cache key (default: True)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip caching if Redis not available
            if redis_client is None:
                logger.warning(f"⚠️ Redis not initialized, skipping cache for {prefix}")
                return await func(*args, **kwargs)

            # Find the Request object in args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            # Check kwargs if not found in args (FastAPI often passes as kwarg)
            if request is None and "request" in kwargs:
                request = kwargs["request"]

            if request is None or not isinstance(request, Request):
                logger.warning(f"⚠️ No Request object found, skipping cache for {prefix}")
                return await func(*args, **kwargs)

            # Generate cache key
            cache_key = generate_cache_key(prefix, request)

            try:
                # Try to get from cache
                cached_value = await redis_client.get(cache_key)
                if cached_value:
                    logger.info(f"✅ Cache HIT: {cache_key} (saved {ttl}s of computation)")
                    return json.loads(cached_value)

                logger.info(f"⚠️ Cache MISS: {cache_key}")

                # Execute the actual function
                result = await func(*args, **kwargs)

                # Convert result to JSON-serializable format
                # Handle Pydantic models, dataclasses, and other objects
                if hasattr(result, "model_dump"):  # Pydantic v2
                    cache_data = result.model_dump()
                elif hasattr(result, "dict"):  # Pydantic v1
                    cache_data = result.dict()
                elif isinstance(result, dict):
                    cache_data = result
                else:
                    # For other types, try to serialize directly
                    cache_data = result

                # Store in cache
                await redis_client.setex(cache_key, ttl, json.dumps(cache_data, default=str))
                logger.info(f"✅ Cached result for {cache_key} (TTL: {ttl}s)")

                return result

            except Exception as e:
                logger.error(f"❌ Cache error for {cache_key}: {e}")
                # Fall back to executing function without cache
                return await func(*args, **kwargs)

        return wrapper

    return decorator


async def invalidate_cache(prefix: str, user_id: int | None = None):
    """
    Invalidate cache entries by prefix and/or user_id

    Usage:
        await invalidate_cache("auth:me", user_id=123)  # Clear specific user cache
        await invalidate_cache("analytics:*")  # Clear all analytics cache
    """
    if redis_client is None:
        return

    try:
        pattern = f"cache:{prefix}:*"
        if user_id:
            pattern = f"cache:{prefix}:user_{user_id}:*"

        # Find all matching keys
        keys = []
        async for key in redis_client.scan_iter(match=pattern):
            keys.append(key)

        if keys:
            await redis_client.delete(*keys)
            logger.info(f"✅ Invalidated {len(keys)} cache entries: {pattern}")
    except Exception as e:
        logger.error(f"❌ Cache invalidation error: {e}")


async def get_cache_stats() -> dict:
    """Get cache statistics"""
    if redis_client is None:
        return {"status": "disconnected"}

    try:
        info = await redis_client.info("stats")

        # Count cache keys
        cache_keys = 0
        async for _ in redis_client.scan_iter(match="cache:*"):
            cache_keys += 1

        return {
            "status": "connected",
            "total_cache_keys": cache_keys,
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
        }
    except Exception as e:
        logger.error(f"❌ Failed to get cache stats: {e}")
        return {"status": "error", "error": str(e)}
