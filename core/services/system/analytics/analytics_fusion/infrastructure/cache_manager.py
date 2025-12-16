"""
Cache Manager
============

Shared caching service for analytics fusion microservices.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuration for cache manager"""

    default_ttl_seconds: int = 300
    max_cache_size: int = 1000
    cleanup_interval_seconds: int = 600


@dataclass
class CacheKey:
    """Cache key structure"""

    service: str
    operation: str
    identifier: str

    def __str__(self) -> str:
        return f"{self.service}:{self.operation}:{self.identifier}"


class CacheManager:
    """Simple in-memory cache manager for analytics microservices"""

    def __init__(self, config: CacheConfig | None = None):
        self.config = config or CacheConfig()
        self.cache: dict[str, dict[str, Any]] = {}

        logger.info("🗄️ Cache Manager initialized")

    async def get(self, key: CacheKey) -> Any | None:
        """Get value from cache"""
        try:
            key_str = str(key)
            if key_str in self.cache:
                entry = self.cache[key_str]
                if self._is_valid(entry):
                    return entry["value"]
                else:
                    del self.cache[key_str]
            return None
        except Exception as e:
            logger.error(f"❌ Cache get error: {e}")
            return None

    async def set(self, key: CacheKey, value: Any, ttl_seconds: int | None = None) -> bool:
        """Set value in cache"""
        try:
            key_str = str(key)
            ttl = ttl_seconds or self.config.default_ttl_seconds

            self.cache[key_str] = {
                "value": value,
                "expires_at": datetime.utcnow() + timedelta(seconds=ttl),
                "created_at": datetime.utcnow(),
            }
            return True
        except Exception as e:
            logger.error(f"❌ Cache set error: {e}")
            return False

    def _is_valid(self, entry: dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        return datetime.utcnow() < entry["expires_at"]
