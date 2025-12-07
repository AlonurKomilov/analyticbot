"""Unit tests for AsyncCachePort implementations."""

import pytest

from core.ports.cache_port import AsyncCachePort
from infra.cache.redis_cache_adapter import (
    InMemoryCacheAdapter,
    create_redis_cache_adapter,
)


class TestInMemoryCacheAdapter:
    """Test in-memory cache adapter implementation."""

    @pytest.fixture
    def cache(self) -> AsyncCachePort:
        """Create in-memory cache instance."""
        return InMemoryCacheAdapter()

    @pytest.mark.asyncio
    async def test_sadd_and_smembers(self, cache: AsyncCachePort):
        """Test adding and retrieving set members."""
        # Add items to set
        count = await cache.sadd("test_set", "value1", "value2")
        assert count == 2

        # Retrieve members
        members = await cache.smembers("test_set")
        assert members == {"value1", "value2"}

    @pytest.mark.asyncio
    async def test_srem(self, cache: AsyncCachePort):
        """Test removing items from set."""
        # Setup
        await cache.sadd("test_set", "value1", "value2", "value3")

        # Remove one item
        count = await cache.srem("test_set", "value2")
        assert count == 1

        # Verify remaining items
        members = await cache.smembers("test_set")
        assert members == {"value1", "value3"}

    @pytest.mark.asyncio
    async def test_exists(self, cache: AsyncCachePort):
        """Test checking key existence."""
        # Key doesn't exist initially
        assert not await cache.exists("test_key")

        # Add item
        await cache.sadd("test_key", "value")

        # Key should exist now
        assert await cache.exists("test_key")

    @pytest.mark.asyncio
    async def test_delete(self, cache: AsyncCachePort):
        """Test deleting keys."""
        # Setup
        await cache.sadd("key1", "value1")
        await cache.sadd("key2", "value2")

        # Delete keys
        count = await cache.delete("key1", "key2")
        assert count == 2

        # Verify they're gone
        assert not await cache.exists("key1")
        assert not await cache.exists("key2")

    @pytest.mark.asyncio
    async def test_empty_set_operations(self, cache: AsyncCachePort):
        """Test operations on empty sets."""
        # Empty set returns empty set
        members = await cache.smembers("nonexistent")
        assert members == set()

        # Removing from nonexistent set
        count = await cache.srem("nonexistent", "value")
        assert count == 0


class TestCacheFactory:
    """Test cache adapter factory."""

    def test_create_without_redis_returns_memory_adapter(self):
        """Test that factory returns in-memory adapter when redis_client is None."""
        cache = create_redis_cache_adapter(None)
        assert isinstance(cache, InMemoryCacheAdapter)

    @pytest.mark.asyncio
    async def test_memory_adapter_from_factory_works(self):
        """Test that in-memory adapter from factory is functional."""
        cache = create_redis_cache_adapter(None)

        await cache.sadd("test", "value1", "value2")
        members = await cache.smembers("test")
        assert members == {"value1", "value2"}
