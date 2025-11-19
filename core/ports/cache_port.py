"""Async cache port protocol for abstract caching operations.

This protocol defines the interface for asynchronous caching operations
without tying the implementation to any specific cache backend (Redis, Memcached, etc.).

Note: This is separate from the synchronous CachePort in security_ports.py
which is used for security/session management.
"""

from typing import Protocol


class AsyncCachePort(Protocol):
    """Protocol for asynchronous cache operations.

    Defines the interface for set-based async cache operations used throughout
    the application. Implementations can use Redis, Memcached, or in-memory
    storage depending on deployment requirements.

    This is the async version used for bot services and background tasks.
    For synchronous security operations, see CachePort in security_ports.py.
    """

    async def sadd(self, key: str, *values: str) -> int:
        """Add one or more values to a set.

        Args:
            key: The cache key for the set
            *values: One or more string values to add

        Returns:
            Number of elements added to the set
        """
        ...

    async def srem(self, key: str, *values: str) -> int:
        """Remove one or more values from a set.

        Args:
            key: The cache key for the set
            *values: One or more string values to remove

        Returns:
            Number of elements removed from the set
        """
        ...

    async def smembers(self, key: str) -> set[str]:
        """Get all members of a set.

        Args:
            key: The cache key for the set

        Returns:
            Set of all string values in the set
        """
        ...

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache.

        Args:
            key: The cache key to check

        Returns:
            True if key exists, False otherwise
        """
        ...

    async def delete(self, *keys: str) -> int:
        """Delete one or more keys from cache.

        Args:
            *keys: One or more cache keys to delete

        Returns:
            Number of keys deleted
        """
        ...

    async def close(self) -> None:
        """Close the cache connection.

        Should be called when shutting down to properly release resources.
        """
        ...
