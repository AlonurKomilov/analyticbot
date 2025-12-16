"""
Redis Caching Service for Public Channel Catalog

Provides caching layer for public catalog data to reduce database load
and improve response times for high-traffic public endpoints.

Cache TTLs:
- Categories: 1 hour (rarely change)
- Featured/Trending: 5 minutes (updated frequently)
- Channel lists: 10 minutes
- Channel details: 15 minutes
- Stats: 30 minutes
"""

import json
import logging
from datetime import datetime
from typing import Any

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    aioredis = None
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class PublicCatalogCacheService:
    """
    Redis caching service for public catalog data.
    
    Falls back to no-caching if Redis is unavailable.
    """

    # Cache key prefixes
    PREFIX = "public_catalog"
    CATEGORIES_KEY = f"{PREFIX}:categories"
    FEATURED_KEY = f"{PREFIX}:featured"
    TRENDING_KEY = f"{PREFIX}:trending"
    CHANNEL_KEY = f"{PREFIX}:channel"
    CHANNEL_LIST_KEY = f"{PREFIX}:channels"
    CATEGORY_CHANNELS_KEY = f"{PREFIX}:category_channels"
    SEARCH_KEY = f"{PREFIX}:search"
    STATS_KEY = f"{PREFIX}:stats"

    # TTLs in seconds
    TTL_CATEGORIES = 3600  # 1 hour
    TTL_FEATURED = 300  # 5 minutes
    TTL_TRENDING = 300  # 5 minutes
    TTL_CHANNEL = 900  # 15 minutes
    TTL_CHANNEL_LIST = 600  # 10 minutes
    TTL_SEARCH = 300  # 5 minutes
    TTL_STATS = 1800  # 30 minutes

    def __init__(self, redis_url: str | None = None):
        """
        Initialize the cache service.
        
        Args:
            redis_url: Redis connection URL. If None, caching is disabled.
        """
        self.redis: Any | None = None
        self.enabled = False
        self._redis_url = redis_url

    async def connect(self) -> bool:
        """
        Connect to Redis.
        
        Returns:
            True if connected successfully, False otherwise.
        """
        if not REDIS_AVAILABLE:
            logger.warning("Redis library not available, caching disabled")
            return False

        if not self._redis_url:
            logger.info("No Redis URL provided, caching disabled")
            return False

        try:
            self.redis = await aioredis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis.ping()
            self.enabled = True
            logger.info("Public catalog cache connected to Redis")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.enabled = False
            return False

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self.enabled = False
            logger.info("Public catalog cache disconnected from Redis")

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _serialize(self, data: Any) -> str:
        """Serialize data to JSON string."""
        return json.dumps(data, default=str)

    def _deserialize(self, data: str | None) -> Any | None:
        """Deserialize JSON string to data."""
        if data is None:
            return None
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

    async def _get(self, key: str) -> Any | None:
        """Get value from cache."""
        if not self.enabled or not self.redis:
            return None
        try:
            data = await self.redis.get(key)
            return self._deserialize(data)
        except Exception as e:
            logger.error(f"Cache get error for {key}: {e}")
            return None

    async def _set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache with TTL."""
        if not self.enabled or not self.redis:
            return False
        try:
            await self.redis.setex(key, ttl, self._serialize(value))
            return True
        except Exception as e:
            logger.error(f"Cache set error for {key}: {e}")
            return False

    async def _delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self.enabled or not self.redis:
            return False
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for {key}: {e}")
            return False

    async def _delete_pattern(self, pattern: str) -> int:
        """Delete keys matching a pattern."""
        if not self.enabled or not self.redis:
            return 0
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    # ========================================================================
    # Categories Cache
    # ========================================================================

    async def get_categories(self) -> list[dict] | None:
        """Get cached categories."""
        return await self._get(self.CATEGORIES_KEY)

    async def set_categories(self, categories: list[dict]) -> bool:
        """Cache categories."""
        return await self._set(self.CATEGORIES_KEY, categories, self.TTL_CATEGORIES)

    async def invalidate_categories(self) -> bool:
        """Invalidate categories cache."""
        return await self._delete(self.CATEGORIES_KEY)

    # ========================================================================
    # Featured Channels Cache
    # ========================================================================

    async def get_featured(self) -> list[dict] | None:
        """Get cached featured channels."""
        return await self._get(self.FEATURED_KEY)

    async def set_featured(self, channels: list[dict]) -> bool:
        """Cache featured channels."""
        return await self._set(self.FEATURED_KEY, channels, self.TTL_FEATURED)

    async def invalidate_featured(self) -> bool:
        """Invalidate featured cache."""
        return await self._delete(self.FEATURED_KEY)

    # ========================================================================
    # Trending Channels Cache
    # ========================================================================

    async def get_trending(self, period: str = "day") -> list[dict] | None:
        """Get cached trending channels for a period."""
        key = f"{self.TRENDING_KEY}:{period}"
        return await self._get(key)

    async def set_trending(self, channels: list[dict], period: str = "day") -> bool:
        """Cache trending channels for a period."""
        key = f"{self.TRENDING_KEY}:{period}"
        return await self._set(key, channels, self.TTL_TRENDING)

    async def invalidate_trending(self) -> int:
        """Invalidate all trending caches."""
        return await self._delete_pattern(f"{self.TRENDING_KEY}:*")

    # ========================================================================
    # Channel Details Cache
    # ========================================================================

    async def get_channel(self, username: str) -> dict | None:
        """Get cached channel details."""
        key = f"{self.CHANNEL_KEY}:{username.lower()}"
        return await self._get(key)

    async def set_channel(self, username: str, channel: dict) -> bool:
        """Cache channel details."""
        key = f"{self.CHANNEL_KEY}:{username.lower()}"
        return await self._set(key, channel, self.TTL_CHANNEL)

    async def invalidate_channel(self, username: str) -> bool:
        """Invalidate channel cache."""
        key = f"{self.CHANNEL_KEY}:{username.lower()}"
        return await self._delete(key)

    # ========================================================================
    # Channel Lists Cache
    # ========================================================================

    async def get_channels(self, page: int, per_page: int, filters: dict | None = None) -> dict | None:
        """Get cached channel list."""
        filter_hash = hash(json.dumps(filters or {}, sort_keys=True))
        key = f"{self.CHANNEL_LIST_KEY}:{page}:{per_page}:{filter_hash}"
        return await self._get(key)

    async def set_channels(self, page: int, per_page: int, data: dict, filters: dict | None = None) -> bool:
        """Cache channel list."""
        filter_hash = hash(json.dumps(filters or {}, sort_keys=True))
        key = f"{self.CHANNEL_LIST_KEY}:{page}:{per_page}:{filter_hash}"
        return await self._set(key, data, self.TTL_CHANNEL_LIST)

    async def invalidate_channels(self) -> int:
        """Invalidate all channel list caches."""
        return await self._delete_pattern(f"{self.CHANNEL_LIST_KEY}:*")

    # ========================================================================
    # Category Channels Cache
    # ========================================================================

    async def get_category_channels(self, slug: str, page: int, per_page: int) -> dict | None:
        """Get cached channels for a category."""
        key = f"{self.CATEGORY_CHANNELS_KEY}:{slug}:{page}:{per_page}"
        return await self._get(key)

    async def set_category_channels(self, slug: str, page: int, per_page: int, data: dict) -> bool:
        """Cache channels for a category."""
        key = f"{self.CATEGORY_CHANNELS_KEY}:{slug}:{page}:{per_page}"
        return await self._set(key, data, self.TTL_CHANNEL_LIST)

    async def invalidate_category_channels(self, slug: str | None = None) -> int:
        """Invalidate category channels cache. If slug is None, invalidate all."""
        pattern = f"{self.CATEGORY_CHANNELS_KEY}:{slug if slug else '*'}:*"
        return await self._delete_pattern(pattern)

    # ========================================================================
    # Search Cache
    # ========================================================================

    async def get_search(self, query: str, page: int, per_page: int) -> dict | None:
        """Get cached search results."""
        query_hash = hash(query.lower().strip())
        key = f"{self.SEARCH_KEY}:{query_hash}:{page}:{per_page}"
        return await self._get(key)

    async def set_search(self, query: str, page: int, per_page: int, data: dict) -> bool:
        """Cache search results."""
        query_hash = hash(query.lower().strip())
        key = f"{self.SEARCH_KEY}:{query_hash}:{page}:{per_page}"
        return await self._set(key, data, self.TTL_SEARCH)

    async def invalidate_search(self) -> int:
        """Invalidate all search caches."""
        return await self._delete_pattern(f"{self.SEARCH_KEY}:*")

    # ========================================================================
    # Stats Cache
    # ========================================================================

    async def get_stats(self) -> dict | None:
        """Get cached overall stats."""
        return await self._get(self.STATS_KEY)

    async def set_stats(self, stats: dict) -> bool:
        """Cache overall stats."""
        return await self._set(self.STATS_KEY, stats, self.TTL_STATS)

    async def invalidate_stats(self) -> bool:
        """Invalidate stats cache."""
        return await self._delete(self.STATS_KEY)

    # ========================================================================
    # Bulk Invalidation
    # ========================================================================

    async def invalidate_all(self) -> int:
        """Invalidate all public catalog caches."""
        return await self._delete_pattern(f"{self.PREFIX}:*")

    async def invalidate_on_channel_change(self, username: str | None = None) -> dict:
        """
        Invalidate caches that should be refreshed when a channel is added/updated/removed.
        
        Args:
            username: Channel username (if known) to invalidate specific channel cache.
            
        Returns:
            Dict with invalidation counts.
        """
        results = {
            "channel": False,
            "featured": False,
            "trending": 0,
            "channels": 0,
            "category_channels": 0,
            "search": 0,
            "stats": False,
        }

        if username:
            results["channel"] = await self.invalidate_channel(username)
        
        results["featured"] = await self.invalidate_featured()
        results["trending"] = await self.invalidate_trending()
        results["channels"] = await self.invalidate_channels()
        results["category_channels"] = await self.invalidate_category_channels()
        results["search"] = await self.invalidate_search()
        results["stats"] = await self.invalidate_stats()

        return results


# Global cache instance
_cache_instance: PublicCatalogCacheService | None = None


async def get_public_cache() -> PublicCatalogCacheService:
    """
    Get the global public catalog cache instance.
    
    Returns:
        PublicCatalogCacheService instance (may or may not be connected).
    """
    global _cache_instance
    
    if _cache_instance is None:
        from config import settings
        redis_url = getattr(settings, "REDIS_URL", None)
        _cache_instance = PublicCatalogCacheService(redis_url)
        await _cache_instance.connect()
    
    return _cache_instance
