"""
Token bucket rate limiter using Redis for distributed rate limiting.

Conservative Telegram limits implementation:
- Per chat: 20 messages/minute
- Per bot: 30 messages/second
- Burst tolerance with token bucket algorithm

Usage:
    rate_limiter = TokenBucketRateLimiter()

    # Acquire permission to send
    success, delay = await rate_limiter.acquire("chat_123", tokens=1)
    if not success:
        await asyncio.sleep(delay)  # Wait before retry

    # Or use with automatic delay
    await rate_limiter.acquire_with_delay("chat_123", tokens=1)
"""

import asyncio
import logging
import time

import redis.asyncio as redis
from pydantic import BaseModel

from config.settings import settings

logger = logging.getLogger(__name__)


class TokenBucketConfig(BaseModel):
    """Token bucket configuration."""

    capacity: int  # Maximum tokens in bucket
    refill_rate: float  # Tokens per second
    initial_tokens: int | None = None  # Initial tokens (defaults to capacity)

    def __post_init__(self):
        if self.initial_tokens is None:
            self.initial_tokens = self.capacity


class RateLimitResult(BaseModel):
    """Rate limit check result."""

    allowed: bool
    tokens_remaining: int
    retry_after_seconds: float
    bucket_key: str


# Conservative Telegram rate limits
TELEGRAM_LIMITS = {
    # Per chat limits (conservative)
    "chat": TokenBucketConfig(
        capacity=20,  # 20 messages burst
        refill_rate=20 / 60,  # 20 messages per minute = 0.33 msg/sec
    ),
    # Per bot global limits (very conservative)
    "global": TokenBucketConfig(
        capacity=100,  # 100 messages burst
        refill_rate=20,  # 20 messages per second (well below 30/sec limit)
    ),
    # Per user limits (anti-spam)
    "user": TokenBucketConfig(
        capacity=5,  # 5 messages burst
        refill_rate=1 / 60,  # 1 message per minute for users
    ),
}


class TokenBucketRateLimiter:
    """Redis-based distributed token bucket rate limiter."""

    def __init__(self, redis_url: str | None = None, key_prefix: str = "ratelimit:bucket"):
        self.redis_url = redis_url or settings.REDIS_URL
        self.key_prefix = key_prefix
        self._redis: redis.Redis | None = None

        # Lua script for atomic token bucket operation
        self._lua_script = """
        local bucket_key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local tokens_requested = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        -- Get current bucket state
        local bucket_data = redis.call('HMGET', bucket_key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket_data[1])
        local last_refill = tonumber(bucket_data[2])
        
        -- Initialize bucket if it doesn't exist
        if tokens == nil then
            tokens = capacity
            last_refill = now
        end
        
        -- Calculate tokens to add based on elapsed time
        local elapsed = now - last_refill
        local tokens_to_add = elapsed * refill_rate
        tokens = math.min(capacity, tokens + tokens_to_add)
        
        -- Check if we have enough tokens
        local success = 0
        local retry_after = 0
        
        if tokens >= tokens_requested then
            tokens = tokens - tokens_requested
            success = 1
        else
            -- Calculate how long to wait for enough tokens
            local tokens_needed = tokens_requested - tokens
            retry_after = tokens_needed / refill_rate
        end
        
        -- Update bucket state
        redis.call('HMSET', bucket_key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', bucket_key, 3600)  -- 1 hour TTL
        
        return {success, math.floor(tokens), retry_after}
        """

    async def get_redis(self) -> redis.Redis:
        """Get Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    def _make_key(self, bucket_id: str, limit_type: str = "chat") -> str:
        """Create Redis key for bucket."""
        return f"{self.key_prefix}:{limit_type}:{bucket_id}"

    async def acquire(
        self, bucket_id: str, tokens: int = 1, limit_type: str = "chat"
    ) -> tuple[bool, float]:
        """
        Try to acquire tokens from bucket.

        Args:
            bucket_id: Unique identifier (chat_id, user_id, etc.)
            tokens: Number of tokens to acquire
            limit_type: Type of limit ("chat", "global", "user")

        Returns:
            (success, retry_after_seconds)
        """
        if limit_type not in TELEGRAM_LIMITS:
            raise ValueError(f"Unknown limit type: {limit_type}")

        config = TELEGRAM_LIMITS[limit_type]
        redis_client = await self.get_redis()
        key = self._make_key(bucket_id, limit_type)

        try:
            # Execute Lua script atomically
            result = await redis_client.eval(
                self._lua_script,
                1,  # Number of keys
                key,
                config.capacity,
                config.refill_rate,
                tokens,
                time.time(),
            )

            success, tokens_remaining, retry_after = result
            success = bool(success)

            log_msg = (
                f"Rate limit check: bucket='{bucket_id}', type='{limit_type}', "
                f"tokens_requested={tokens}, success={success}, "
                f"remaining={tokens_remaining}, retry_after={retry_after:.2f}s"
            )

            if success:
                logger.debug(log_msg)
            else:
                logger.warning(log_msg)

            return success, retry_after

        except Exception as e:
            logger.error(f"Redis error in rate limiter for '{bucket_id}': {e}")
            # In case of Redis failure, allow operation (fail open)
            return True, 0.0

    async def acquire_with_delay(
        self, bucket_id: str, tokens: int = 1, limit_type: str = "chat", max_wait: float = 60.0
    ) -> bool:
        """
        Acquire tokens with automatic delay if needed.

        Args:
            bucket_id: Unique identifier
            tokens: Number of tokens to acquire
            limit_type: Type of limit
            max_wait: Maximum seconds to wait

        Returns:
            True if acquired, False if max_wait exceeded
        """
        success, delay = await self.acquire(bucket_id, tokens, limit_type)

        if success:
            return True

        if delay > max_wait:
            logger.warning(
                f"Rate limit delay ({delay:.2f}s) exceeds max_wait ({max_wait}s) "
                f"for bucket '{bucket_id}'"
            )
            return False

        logger.info(f"Rate limit hit, waiting {delay:.2f}s for bucket '{bucket_id}'")
        await asyncio.sleep(delay)

        # Try again after delay
        success, _ = await self.acquire(bucket_id, tokens, limit_type)
        return success

    async def check_remaining(self, bucket_id: str, limit_type: str = "chat") -> RateLimitResult:
        """Check remaining tokens without consuming any."""
        success, retry_after = await self.acquire(bucket_id, 0, limit_type)

        # Get current tokens (this is a bit hacky but works)
        redis_client = await self.get_redis()
        key = self._make_key(bucket_id, limit_type)

        try:
            bucket_data = await redis_client.hmget(key, "tokens")
            tokens_remaining = int(float(bucket_data[0]) if bucket_data[0] else 0)
        except Exception:
            tokens_remaining = 0

        return RateLimitResult(
            allowed=success,
            tokens_remaining=tokens_remaining,
            retry_after_seconds=retry_after,
            bucket_key=key,
        )

    async def reset_bucket(self, bucket_id: str, limit_type: str = "chat") -> None:
        """Reset bucket to full capacity."""
        redis_client = await self.get_redis()
        key = self._make_key(bucket_id, limit_type)

        try:
            await redis_client.delete(key)
            logger.info(f"Reset rate limit bucket: '{bucket_id}' ({limit_type})")
        except Exception as e:
            logger.error(f"Error resetting bucket '{bucket_id}': {e}")

    async def get_bucket_stats(self, limit_type: str = "chat") -> dict:
        """Get statistics for all buckets of a given type."""
        redis_client = await self.get_redis()
        pattern = f"{self.key_prefix}:{limit_type}:*"

        try:
            keys = await redis_client.keys(pattern)
            stats = {
                "total_buckets": len(keys),
                "limit_type": limit_type,
                "config": TELEGRAM_LIMITS[limit_type].model_dump(),
            }

            if keys:
                # Sample a few buckets for detailed stats
                sample_keys = keys[:10]  # First 10 keys
                bucket_details = []

                for key in sample_keys:
                    bucket_data = await redis_client.hmget(key, "tokens", "last_refill")
                    bucket_id = key.split(":")[-1]  # Extract bucket ID

                    bucket_details.append(
                        {
                            "bucket_id": bucket_id,
                            "tokens": float(bucket_data[0]) if bucket_data[0] else 0,
                            "last_refill": float(bucket_data[1]) if bucket_data[1] else 0,
                        }
                    )

                stats["sample_buckets"] = bucket_details

            return stats

        except Exception as e:
            logger.error(f"Error getting bucket stats: {e}")
            return {"error": str(e)}

    async def cleanup_expired(self) -> int:
        """Clean up expired buckets. Returns count of cleaned buckets."""
        redis_client = await self.get_redis()

        try:
            pattern = f"{self.key_prefix}:*"
            keys = await redis_client.keys(pattern)

            cleaned = 0
            for key in keys:
                # Check if key has TTL
                ttl = await redis_client.ttl(key)
                if ttl == -1:  # No TTL set, clean it up
                    await redis_client.delete(key)
                    cleaned += 1

            logger.info(f"Cleaned up {cleaned} expired rate limit buckets")
            return cleaned

        except Exception as e:
            logger.error(f"Error cleaning up rate limit buckets: {e}")
            return 0

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
