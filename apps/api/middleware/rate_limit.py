"""
Rate limiting middleware for share links using token bucket algorithm
"""

import asyncio
import logging
import time
from dataclasses import dataclass

from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    """Token bucket for rate limiting"""

    capacity: int
    refill_rate: float  # tokens per second
    tokens: float
    last_refill: float

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket"""
        now = time.time()

        # Refill tokens based on time elapsed
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        # Check if we can consume the requested tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class ShareLinkRateLimiter:
    """Rate limiter for share link operations using token bucket algorithm"""

    def __init__(
        self,
        creation_rate: float = 5.0,  # 5 creations per minute
        creation_burst: int = 10,  # burst of 10 creations
        access_rate: float = 60.0,  # 60 accesses per minute
        access_burst: int = 120,  # burst of 120 accesses
    ):
        self.creation_rate = creation_rate / 60.0  # convert to per second
        self.creation_burst = creation_burst
        self.access_rate = access_rate / 60.0  # convert to per second
        self.access_burst = access_burst

        # Buckets per client IP
        self.creation_buckets: dict[str, TokenBucket] = {}
        self.access_buckets: dict[str, TokenBucket] = {}

        # Cleanup task
        self._cleanup_task = None

    async def start_cleanup_task(self):
        """Start background cleanup task for old buckets"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_old_buckets())

    async def stop_cleanup_task(self):
        """Stop background cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check X-Forwarded-For header first (for proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP if multiple
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"

    def get_or_create_bucket(self, client_ip: str, bucket_type: str) -> TokenBucket:
        """Get or create token bucket for client"""
        if bucket_type == "creation":
            buckets = self.creation_buckets
            capacity = self.creation_burst
            rate = self.creation_rate
        elif bucket_type == "access":
            buckets = self.access_buckets
            capacity = self.access_burst
            rate = self.access_rate
        else:
            raise ValueError(f"Invalid bucket type: {bucket_type}")

        if client_ip not in buckets:
            buckets[client_ip] = TokenBucket(
                capacity=capacity,
                refill_rate=rate,
                tokens=capacity,  # Start with full bucket
                last_refill=time.time(),
            )

        return buckets[client_ip]

    def check_creation_limit(self, request: Request) -> bool:
        """Check if share link creation is allowed"""
        client_ip = self.get_client_ip(request)
        bucket = self.get_or_create_bucket(client_ip, "creation")
        return bucket.consume(1)

    def check_access_limit(self, request: Request) -> bool:
        """Check if share link access is allowed"""
        client_ip = self.get_client_ip(request)
        bucket = self.get_or_create_bucket(client_ip, "access")
        return bucket.consume(1)

    def get_retry_after(self, bucket_type: str) -> int:
        """Get retry-after time in seconds"""
        if bucket_type == "creation":
            return int(1.0 / self.creation_rate)  # Time for 1 token (rate is per second)
        elif bucket_type == "access":
            return int(1.0 / self.access_rate)  # Time for 1 token (rate is per second)
        return 60

    async def _cleanup_old_buckets(self):
        """Cleanup old token buckets periodically"""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes

                now = time.time()
                cutoff_time = now - 3600  # Remove buckets inactive for 1 hour

                # Cleanup creation buckets
                expired_creation = [
                    ip
                    for ip, bucket in self.creation_buckets.items()
                    if bucket.last_refill < cutoff_time
                ]
                for ip in expired_creation:
                    del self.creation_buckets[ip]

                # Cleanup access buckets
                expired_access = [
                    ip
                    for ip, bucket in self.access_buckets.items()
                    if bucket.last_refill < cutoff_time
                ]
                for ip in expired_access:
                    del self.access_buckets[ip]

                if expired_creation or expired_access:
                    logger.info(
                        f"Cleaned up rate limit buckets: {len(expired_creation)} creation, {len(expired_access)} access"
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in rate limit cleanup: {e}")


# Global rate limiter instance
_rate_limiter: ShareLinkRateLimiter | None = None


def get_rate_limiter() -> ShareLinkRateLimiter:
    """Get or create global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = ShareLinkRateLimiter()
        # Start cleanup task
        asyncio.create_task(_rate_limiter.start_cleanup_task())
    return _rate_limiter


def check_creation_rate_limit(request: Request):
    """Dependency to check share link creation rate limit"""
    rate_limiter = get_rate_limiter()

    if not rate_limiter.check_creation_limit(request):
        retry_after = rate_limiter.get_retry_after("creation")

        logger.warning(
            f"Rate limit exceeded for share creation from IP {rate_limiter.get_client_ip(request)}"
        )

        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded for share link creation",
            headers={"Retry-After": str(retry_after)},
        )


def check_access_rate_limit(request: Request):
    """Dependency to check share link access rate limit"""
    rate_limiter = get_rate_limiter()

    if not rate_limiter.check_access_limit(request):
        retry_after = rate_limiter.get_retry_after("access")

        logger.warning(
            f"Rate limit exceeded for share access from IP {rate_limiter.get_client_ip(request)}"
        )

        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded for share link access",
            headers={"Retry-After": str(retry_after)},
        )
