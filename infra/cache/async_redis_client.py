"""
Async Redis Client Implementation for Analytics DI System
Implements RedisClientProtocol for proper dependency injection
"""

import logging
import os
from typing import Any

import redis.asyncio as redis

from core.protocols import RedisClientProtocol

logger = logging.getLogger(__name__)


class AsyncRedisClient(RedisClientProtocol):
    """Async Redis client implementation following the protocol"""

    def __init__(self, redis_client: redis.Redis):
        self._client = redis_client
        self._connected = False

    async def get(self, key: str) -> Any:
        """Get value from Redis"""
        try:
            return await self._client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return None

    async def set(self, key: str, value: Any, ex: int | None = None) -> bool:
        """Set value in Redis with optional expiry"""
        try:
            await self._client.set(key, value, ex=ex)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            result = await self._client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE error for key '{key}': {e}")
            return False

    async def ping(self) -> bool:
        """Check Redis connection"""
        try:
            await self._client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis PING failed: {e}")
            return False

    async def close(self) -> None:
        """Close Redis connection"""
        try:
            await self._client.close()
            self._connected = False
        except Exception as e:
            logger.error(f"Redis close error: {e}")


def create_redis_client() -> AsyncRedisClient:
    """Factory function to create configured Redis client"""
    try:
        # Get Redis configuration from environment
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        # Handle test environment
        if os.getenv("ENVIRONMENT") == "test" or "pytest" in os.getenv("_", ""):
            logger.info("Creating Redis client for test environment")
            # For tests, you might want to use a different DB or fake Redis
            redis_url = os.getenv("REDIS_TEST_URL", redis_url)

        # Create Redis client
        redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )

        logger.info(f"Created Redis client with URL: {redis_url}")
        return AsyncRedisClient(redis_client)

    except Exception as e:
        logger.error(f"Failed to create Redis client: {e}")
        raise
