"""
Global Rate Limiter for Multi-Tenant Bot System

PROBLEM SOLVED:
- Before: Only per-user limits (100 users × 30 RPS = 3000 total RPS to Telegram)
- After: System-wide limits prevent hitting Telegram API rate limits

TELEGRAM API LIMITS:
- sendMessage: 30 messages/second across all bots
- getUpdates: 1 request/second per bot
- Other methods: Generally 30 requests/second
- Global limit: ~3000-5000 requests/minute across all tokens

IMPLEMENTATION:
- Redis-backed sliding window rate limiting (scalable)
- In-memory fallback when Redis unavailable
- Per-method rate limits
- Global system-wide limit
- Automatic backoff on 429 errors
"""

from typing import Any

import asyncio
import logging
import os
import time
from collections import deque
from typing import ClassVar

logger = logging.getLogger(__name__)


class GlobalRateLimiter:
    """
    Global rate limiter for all bot instances

    Implements sliding window rate limiting using Redis sorted sets
    to prevent hitting Telegram API limits across all users.
    
    For 100K+ users, uses Redis for distributed coordination.
    Falls back to in-memory for single-instance deployments.

    Features:
    - Redis-backed sliding window (scalable)
    - Per-method rate limits (sendMessage, getUpdates, etc.)
    - Global system-wide limit
    - Automatic backoff on rate limit errors
    - Thread-safe with asyncio locks
    """

    _instance: ClassVar["GlobalRateLimiter | None"] = None
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    # Telegram API rate limits (conservative values)
    LIMITS = {
        "sendMessage": {"requests": 30, "window": 1.0},  # 30 messages/second
        "editMessageText": {"requests": 30, "window": 1.0},
        "deleteMessage": {"requests": 30, "window": 1.0},
        "getUpdates": {"requests": 1, "window": 1.0},  # 1 request/second
        "getChatMember": {"requests": 20, "window": 1.0},
        "getChat": {"requests": 20, "window": 1.0},
        "default": {"requests": 30, "window": 1.0},  # Default for unknown methods
        "global": {"requests": 2000, "window": 60.0},  # 2000 requests/minute globally (scaled up)
    }
    
    # Redis configuration
    REDIS_KEY_PREFIX = "bot:rate_limit:"
    REDIS_KEY_TTL = 120  # 2 minutes TTL for rate limit keys

    def __init__(self):
        """Private constructor - use get_instance() instead"""
        # Per-method request timestamps (in-memory fallback)
        self._request_history: dict[str, deque[float]] = {}
        self._locks: dict[str, asyncio.Lock] = {}

        # Backoff state for 429 errors
        self._backoff_until: float = 0.0
        self._backoff_lock = asyncio.Lock()

        # Statistics
        self._total_requests = 0
        self._rate_limited_count = 0
        self._backoff_count = 0
        
        # Redis client (lazy initialization)
        self._redis_client: Any = None
        self._redis_available: bool | None = None

    async def _get_redis(self) -> Any:
        """Get Redis client with lazy initialization"""
        if self._redis_available is False:
            return None
            
        if self._redis_client is None:
            redis_url = os.getenv("REDIS_URL")
            if not redis_url:
                self._redis_available = False
                logger.warning("⚠️ REDIS_URL not set - using in-memory rate limiting (not scalable)")
                return None
            
            try:
                import redis.asyncio as aioredis
                self._redis_client = aioredis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_timeout=2.0,
                    socket_connect_timeout=2.0,
                )
                # Test connection
                await self._redis_client.ping()
                self._redis_available = True
                logger.info("✅ Global rate limiter using Redis (production-ready)")
            except Exception as e:
                logger.warning(f"⚠️ Redis unavailable ({e}) - using in-memory rate limiting")
                self._redis_available = False
                return None
        
        return self._redis_client

    @classmethod
    async def get_instance(cls) -> "GlobalRateLimiter":
        """
        Get singleton instance (thread-safe)

        Returns:
            Shared GlobalRateLimiter instance
        """
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    logger.info("✅ Global rate limiter initialized")
        return cls._instance

    def _get_limit(self, method: str) -> dict[str, float]:
        """Get rate limit config for method"""
        return self.LIMITS.get(method, self.LIMITS["default"])

    def _get_lock(self, method: str) -> asyncio.Lock:
        """Get or create lock for method"""
        if method not in self._locks:
            self._locks[method] = asyncio.Lock()
        return self._locks[method]

    def _get_history(self, method: str) -> deque[float]:
        """Get or create request history for method (in-memory fallback)"""
        if method not in self._request_history:
            # Bounded deque to prevent memory leaks
            max_size = int(self.LIMITS.get(method, self.LIMITS["default"])["requests"] * 2)
            self._request_history[method] = deque(maxlen=max(1000, max_size))
        return self._request_history[method]

    async def _check_redis_limit(self, method: str, limit_config: dict) -> tuple[bool, float]:
        """
        Check rate limit using Redis sorted sets (sliding window).
        
        Returns:
            Tuple of (is_allowed, wait_time_if_not_allowed)
        """
        redis = await self._get_redis()
        if not redis:
            return True, 0  # Fall back to in-memory
        
        try:
            key = f"{self.REDIS_KEY_PREFIX}{method}"
            now = time.time()
            window = limit_config["window"]
            max_requests = int(limit_config["requests"])
            window_start = now - window
            
            async with redis.pipeline(transaction=True) as pipe:
                # Remove old entries
                await pipe.zremrangebyscore(key, 0, window_start)
                # Count current entries
                await pipe.zcard(key)
                # Get oldest entry score for wait time calculation
                await pipe.zrange(key, 0, 0, withscores=True)
                results = await pipe.execute()
            
            current_count = results[1]
            oldest_entries = results[2]
            
            if current_count >= max_requests:
                # Calculate wait time
                if oldest_entries:
                    oldest_time = oldest_entries[0][1]
                    wait_time = window - (now - oldest_time)
                else:
                    wait_time = window
                return False, max(0, wait_time)
            
            # Add current request
            await redis.zadd(key, {str(now): now})
            await redis.expire(key, self.REDIS_KEY_TTL)
            
            return True, 0
            
        except Exception as e:
            logger.warning(f"Redis rate limit check failed: {e}")
            return True, 0  # Allow on error, fall back to in-memory

    async def acquire(self, method: str = "default", user_id: int | None = None) -> None:
        """
        Acquire permission to make API request

        Blocks until rate limit allows the request.
        Implements both per-method and global rate limits.

        Args:
            method: Telegram API method name (e.g., "sendMessage")
            user_id: Optional user ID for logging

        Example:
            limiter = await GlobalRateLimiter.get_instance()
            await limiter.acquire("sendMessage", user_id=123)
            # Now safe to make API request
        """
        # Check for active backoff
        async with self._backoff_lock:
            if time.time() < self._backoff_until:
                wait_time = self._backoff_until - time.time()
                logger.info(f"⏸️  Rate limit backoff active, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)

        # Acquire lock for this method
        lock = self._get_lock(method)
        async with lock:
            # Try Redis first
            redis = await self._get_redis()
            
            if redis:
                # Check method-specific limit
                limit_config = self._get_limit(method)
                allowed, wait_time = await self._check_redis_limit(method, limit_config)
                
                if not allowed:
                    self._rate_limited_count += 1
                    if wait_time > 0.1:
                        logger.debug(f"⏳ Rate limit: {method}, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                
                # Check global limit
                allowed, wait_time = await self._check_redis_limit("global", self.LIMITS["global"])
                if not allowed:
                    self._rate_limited_count += 1
                    logger.debug(f"⏳ GLOBAL rate limit, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
            else:
                # Fall back to in-memory
                await self._wait_for_method_limit(method)
                await self._wait_for_global_limit()

                # Record this request in memory
                now = time.time()
                self._get_history(method).append(now)
                self._get_history("global").append(now)
            
            self._total_requests += 1

    async def _wait_for_method_limit(self, method: str) -> None:
        """Wait if method-specific rate limit is exceeded (in-memory fallback)"""
        limit_config = self._get_limit(method)
        max_requests = int(limit_config["requests"])
        window = limit_config["window"]

        history = self._get_history(method)
        now = time.time()

        # Remove old requests outside the window
        while history and history[0] < now - window:
            history.popleft()

        # If at limit, wait until oldest request expires
        if len(history) >= max_requests:
            wait_time = (history[0] + window) - now
            if wait_time > 0:
                self._rate_limited_count += 1
                if wait_time > 0.1:  # Only log significant waits
                    logger.debug(
                        f"⏳ Rate limit: {method} ({len(history)}/{max_requests}), "
                        f"waiting {wait_time:.2f}s"
                    )
                await asyncio.sleep(wait_time)

                # Clean up after waiting
                now = time.time()
                while history and history[0] < now - window:
                    history.popleft()

    async def _wait_for_global_limit(self) -> None:
        """Wait if global rate limit is exceeded (in-memory fallback)"""
        limit_config = self.LIMITS["global"]
        max_requests = int(limit_config["requests"])
        window = limit_config["window"]

        history = self._get_history("global")
        now = time.time()

        # Remove old requests outside the window
        while history and history[0] < now - window:
            history.popleft()

        # If at limit, wait until oldest request expires
        if len(history) >= max_requests:
            wait_time = (history[0] + window) - now
            if wait_time > 0:
                self._rate_limited_count += 1
                logger.debug(
                    f"⏳ GLOBAL rate limit reached ({len(history)}/{max_requests} in {window}s), "
                    f"waiting {wait_time:.2f}s"
                )
                await asyncio.sleep(wait_time)

                # Clean up after waiting
                now = time.time()
                while history and history[0] < now - window:
                    history.popleft()

    async def handle_rate_limit_error(self, retry_after: int | None = None) -> None:
        """
        Handle 429 Rate Limit error from Telegram

        Activates backoff period to prevent further requests.

        Args:
            retry_after: Seconds to wait (from Telegram's response)
        """
        async with self._backoff_lock:
            # Use Telegram's retry_after or default to 60 seconds
            backoff_duration = retry_after if retry_after else 60
            self._backoff_until = time.time() + backoff_duration
            self._backoff_count += 1

            logger.warning(
                f"🚨 Rate limit error (429) from Telegram! Backing off for {backoff_duration}s"
            )

    def get_stats(self) -> dict[str, Any]:
        """
        Get rate limiting statistics

        Returns:
            Dictionary with statistics about rate limiting
        """
        now = time.time()

        # Count active requests in windows
        active_counts = {}
        for method, history in self._request_history.items():
            limit_config = self._get_limit(method)
            window = limit_config["window"]

            # Count requests in current window
            active = sum(1 for ts in history if ts > now - window)
            if active > 0:
                active_counts[method] = {
                    "active": active,
                    "limit": limit_config["requests"],
                    "window": window,
                }

        return {
            "total_requests": self._total_requests,
            "rate_limited_count": self._rate_limited_count,
            "backoff_count": self._backoff_count,
            "backoff_active": time.time() < self._backoff_until,
            "backoff_remaining": max(0, self._backoff_until - time.time()),
            "active_methods": active_counts,
            "redis_enabled": self._redis_available is True,
        }

    @classmethod
    async def close(cls) -> None:
        """Close and reset the rate limiter"""
        if cls._instance is not None:
            if cls._instance._redis_client:
                try:
                    await cls._instance._redis_client.close()
                except Exception:
                    pass
            logger.info("✅ Global rate limiter closed")
            cls._instance = None


# Convenience function
async def acquire_rate_limit(method: str = "default", user_id: int | None = None) -> None:
    """
    Acquire permission to make API request (convenience function)

    Args:
        method: Telegram API method name
        user_id: Optional user ID for logging

    Example:
        from apps.bot.user.global_rate_limiter import acquire_rate_limit

        await acquire_rate_limit("sendMessage", user_id=123)
        await bot.send_message(chat_id, text)
    """
    limiter = await GlobalRateLimiter.get_instance()
    await limiter.acquire(method, user_id)
