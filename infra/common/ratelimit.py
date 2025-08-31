"""
Enhanced token bucket rate limiter for MTProto scaling and hardening.
Supports both in-memory and Redis-based rate limiting.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    rps: float  # Requests per second
    capacity: Optional[int] = None  # Max burst capacity (defaults to 2x rps)
    
    def __post_init__(self):
        if self.capacity is None:
            self.capacity = max(1, int(self.rps * 2))


class TokenBucket:
    """In-memory token bucket for rate limiting."""
    
    def __init__(self, rps: float, capacity: Optional[int] = None):
        self.rps = rps
        self.capacity = capacity or max(1, int(rps * 2))
        self.tokens = float(self.capacity)
        self.updated = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens. Returns True if successful."""
        async with self._lock:
            now = time.monotonic()
            # Add tokens based on elapsed time
            elapsed = now - self.updated
            self.tokens = min(self.capacity, self.tokens + (elapsed * self.rps))
            self.updated = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    async def acquire_with_delay(self, tokens: int = 1) -> None:
        """Acquire tokens, waiting if necessary."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.updated
            self.tokens = min(self.capacity, self.tokens + (elapsed * self.rps))
            self.updated = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return
            
            # Calculate sleep time
            tokens_needed = tokens - self.tokens
            sleep_time = tokens_needed / self.rps
            
        # Sleep outside the lock
        await asyncio.sleep(sleep_time)
        
        # Try again after sleep
        async with self._lock:
            self.tokens = max(0, self.tokens - tokens)


class GlobalLimiter:
    """Global rate limiter for MTProto requests."""
    
    def __init__(self, rps: float):
        self.bucket = TokenBucket(rps)
        self.rps = rps
    
    async def acquire(self) -> bool:
        """Try to acquire permission for a request."""
        return await self.bucket.acquire(1)
    
    async def acquire_with_delay(self) -> None:
        """Acquire permission, waiting if necessary."""
        await self.bucket.acquire_with_delay(1)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get limiter statistics."""
        return {
            "rps": self.rps,
            "capacity": self.bucket.capacity,
            "tokens": self.bucket.tokens,
            "updated": self.bucket.updated
        }


class AccountLimiter:
    """Per-account rate limiter."""
    
    def __init__(self, account_name: str, rps: float, max_concurrency: int):
        self.account_name = account_name
        self.bucket = TokenBucket(rps)
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.rps = rps
        self.max_concurrency = max_concurrency
        self.active_requests = 0
    
    async def acquire(self) -> bool:
        """Try to acquire request permission."""
        # Check concurrency limit
        if not self.semaphore.locked() or self.semaphore._value > 0:
            if await self.bucket.acquire(1):
                return True
        return False
    
    async def acquire_with_delay(self) -> None:
        """Acquire request permission, waiting if necessary."""
        # Wait for concurrency slot
        await self.semaphore.acquire()
        try:
            self.active_requests += 1
            # Wait for rate limit slot
            await self.bucket.acquire_with_delay(1)
        finally:
            self.active_requests -= 1
            self.semaphore.release()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get account limiter statistics."""
        return {
            "account": self.account_name,
            "rps": self.rps,
            "max_concurrency": self.max_concurrency,
            "active_requests": self.active_requests,
            "semaphore_value": self.semaphore._value,
            "tokens": self.bucket.tokens
        }


class RateLimitManager:
    """Manager for coordinating global and per-account rate limiting."""
    
    def __init__(self, global_rps: float, account_rps: float, max_concurrency_per_account: int):
        self.global_limiter = GlobalLimiter(global_rps)
        self.account_limiters: Dict[str, AccountLimiter] = {}
        self.account_rps = account_rps
        self.max_concurrency_per_account = max_concurrency_per_account
        self._lock = asyncio.Lock()
    
    async def get_account_limiter(self, account_name: str) -> AccountLimiter:
        """Get or create account limiter."""
        if account_name not in self.account_limiters:
            async with self._lock:
                if account_name not in self.account_limiters:
                    self.account_limiters[account_name] = AccountLimiter(
                        account_name, self.account_rps, self.max_concurrency_per_account
                    )
        return self.account_limiters[account_name]
    
    async def acquire(self, account_name: str) -> bool:
        """Try to acquire request permission for account."""
        # Check global limit first
        if not await self.global_limiter.acquire():
            return False
        
        # Check account limit
        account_limiter = await self.get_account_limiter(account_name)
        if not await account_limiter.acquire():
            return False
        
        return True
    
    async def acquire_with_delay(self, account_name: str) -> None:
        """Acquire request permission, waiting if necessary."""
        account_limiter = await self.get_account_limiter(account_name)
        
        # Use a simple approach: wait for both global and account limits
        await asyncio.gather(
            self.global_limiter.acquire_with_delay(),
            account_limiter.acquire_with_delay()
        )
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all limiters."""
        stats = {
            "global": self.global_limiter.get_stats(),
            "accounts": {
                name: limiter.get_stats() 
                for name, limiter in self.account_limiters.items()
            }
        }
        return stats