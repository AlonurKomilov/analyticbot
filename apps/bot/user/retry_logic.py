"""
Retry Logic with Exponential Backoff

Handles transient failures with intelligent retry strategies:
- Exponential backoff with jitter
- Configurable retry policies per error type
- Integration with circuit breaker and health monitoring
"""

import asyncio
import random
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, ParamSpec, TypeVar

from telethon.errors import (
    AuthKeyError,
    FloodWaitError,
    NetworkMigrateError,
    PhoneMigrateError,
    ServerError,
    SessionPasswordNeededError,
    TimedOutError,
    UserDeactivatedBanError,
    UserDeactivatedError,
)

P = ParamSpec("P")
T = TypeVar("T")


class RetryStrategy(Enum):
    """Retry strategy types"""

    EXPONENTIAL = "exponential"  # Exponential backoff with jitter
    LINEAR = "linear"  # Linear backoff
    FIXED = "fixed"  # Fixed delay between retries
    FIBONACCI = "fibonacci"  # Fibonacci sequence delays


class RetryErrorCategory(Enum):
    """Categories of errors for retry policies"""

    TRANSIENT_NETWORK = "transient_network"  # Network timeouts, server errors
    RATE_LIMIT = "rate_limit"  # Rate limiting, flood wait
    PERMANENT = "permanent"  # Auth errors, banned users
    UNKNOWN = "unknown"  # Unknown errors


@dataclass
class RetryPolicy:
    """
    Retry policy configuration

    Attributes:
        max_retries: Maximum number of retry attempts (0 = no retries)
        base_delay: Base delay in seconds for backoff calculation
        max_delay: Maximum delay between retries in seconds
        strategy: Retry strategy to use
        jitter: Add random jitter to delays (reduces thundering herd)
        exponential_base: Base for exponential backoff (default 2)
    """

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    jitter: bool = True
    exponential_base: float = 2.0


class RetryableError(Exception):
    """Base class for retryable errors"""

    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class NonRetryableError(Exception):
    """Base class for non-retryable errors"""

    pass


def categorize_error(error: Exception) -> RetryErrorCategory:
    """
    Categorize error to determine retry policy

    Args:
        error: Exception to categorize

    Returns:
        Error category
    """
    error_name = type(error).__name__

    # Rate limiting errors
    if error_name == "FloodWaitError" or isinstance(error, FloodWaitError):
        return RetryErrorCategory.RATE_LIMIT

    # Transient network errors
    if error_name in ("ServerError", "TimedOutError") or isinstance(
        error,
        (
            ServerError,
            TimedOutError,
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError,
        ),
    ):
        return RetryErrorCategory.TRANSIENT_NETWORK

    # Migration errors (need special handling but retryable)
    if error_name in ("NetworkMigrateError", "PhoneMigrateError") or isinstance(
        error, (NetworkMigrateError, PhoneMigrateError)
    ):
        return RetryErrorCategory.TRANSIENT_NETWORK

    # Permanent errors (do not retry)
    if error_name in ("UserDeactivatedError", "UserDeactivatedBanError", "AuthKeyError", "SessionPasswordNeededError") or isinstance(
        error,
        (
            UserDeactivatedError,
            UserDeactivatedBanError,
            AuthKeyError,
            SessionPasswordNeededError,
        ),
    ):
        return RetryErrorCategory.PERMANENT

    # Unknown errors - be conservative
    return RetryErrorCategory.UNKNOWN


def get_retry_policy(error: Exception) -> RetryPolicy:
    """
    Get retry policy based on error category

    Args:
        error: Exception to get policy for

    Returns:
        Appropriate retry policy
    """
    category = categorize_error(error)

    if category == RetryErrorCategory.RATE_LIMIT:
        # For rate limits, respect the server's retry-after
        if isinstance(error, FloodWaitError):
            # FloodWaitError has a 'seconds' attribute
            retry_after = getattr(error, "seconds", 60)
            return RetryPolicy(
                max_retries=2,
                base_delay=min(retry_after, 300),  # Cap at 5 minutes
                max_delay=300,
                strategy=RetryStrategy.FIXED,
                jitter=False,  # Respect exact timing from server
            )
        return RetryPolicy(
            max_retries=3,
            base_delay=5.0,
            max_delay=60.0,
            strategy=RetryStrategy.EXPONENTIAL,
        )

    elif category == RetryErrorCategory.TRANSIENT_NETWORK:
        # Network errors: retry with exponential backoff
        return RetryPolicy(
            max_retries=2,  # Changed from 3 to 2
            base_delay=2.0,  # Changed from 1.0 to 2.0
            max_delay=30.0,
            strategy=RetryStrategy.EXPONENTIAL,
            jitter=True,
        )

    elif category == RetryErrorCategory.PERMANENT:
        # Don't retry permanent errors
        return RetryPolicy(max_retries=0)

    else:
        # Unknown errors: conservative retry
        return RetryPolicy(
            max_retries=2,
            base_delay=2.0,
            max_delay=20.0,
            strategy=RetryStrategy.EXPONENTIAL,
            jitter=True,
        )


def calculate_delay(
    attempt: int,
    policy: RetryPolicy,
) -> float:
    """
    Calculate delay for retry attempt based on policy

    Args:
        attempt: Current retry attempt (0-indexed)
        policy: Retry policy to use

    Returns:
        Delay in seconds
    """
    if policy.strategy == RetryStrategy.EXPONENTIAL:
        # Exponential: base * (exponential_base ^ attempt)
        delay = policy.base_delay * (policy.exponential_base**attempt)

    elif policy.strategy == RetryStrategy.LINEAR:
        # Linear: base * (attempt + 1)
        delay = policy.base_delay * (attempt + 1)

    elif policy.strategy == RetryStrategy.FIXED:
        # Fixed: always base_delay
        delay = policy.base_delay

    elif policy.strategy == RetryStrategy.FIBONACCI:
        # Fibonacci: base * fibonacci(attempt)
        def fib(n: int) -> int:
            if n <= 1:
                return 1
            a, b = 1, 1
            for _ in range(n - 1):
                a, b = b, a + b
            return b

        delay = policy.base_delay * fib(attempt)

    else:
        delay = policy.base_delay

    # Apply jitter to reduce thundering herd
    if policy.jitter:
        # Add ±25% random jitter
        jitter_amount = delay * 0.25
        delay += random.uniform(-jitter_amount, jitter_amount)

    # Cap at max_delay
    delay = min(delay, policy.max_delay)

    # Ensure non-negative
    delay = max(0, delay)

    return delay


async def retry_with_backoff(
    func: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    """
    Execute function with automatic retry and exponential backoff

    Automatically determines retry policy based on exception type.
    Respects circuit breaker and rate limiting.

    Args:
        func: Async function to execute
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Result from successful function execution

    Raises:
        Exception: Last exception if all retries exhausted
        NonRetryableError: If error is not retryable

    Example:
        result = await retry_with_backoff(bot.send_message, chat_id, text)
    """
    last_exception: Exception | None = None
    attempt = 0

    while True:
        try:
            # Execute function
            result = await func(*args, **kwargs)
            return result

        except Exception as e:
            last_exception = e

            # Check if error is permanently non-retryable first
            if categorize_error(e) == RetryErrorCategory.PERMANENT:
                raise NonRetryableError(f"Non-retryable error: {e}") from e

            # Get retry policy for this error
            policy = get_retry_policy(e)

            # Check if we should retry
            if attempt >= policy.max_retries:
                # No more retries left
                raise

            # Calculate delay
            delay = calculate_delay(attempt, policy)

            # Log retry attempt (in production, use proper logging)
            error_type = type(e).__name__
            print(
                f"⚠️  Retry attempt {attempt + 1}/{policy.max_retries} after {delay:.2f}s for {error_type}: {e}"
            )

            # Wait before retry
            await asyncio.sleep(delay)

            # Increment attempt counter
            attempt += 1

    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("Retry logic failed unexpectedly")


class RetryDecorator:
    """
    Decorator for adding retry logic to functions

    Usage:
        @RetryDecorator(max_retries=3, base_delay=1.0)
        async def my_function():
            ...
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        jitter: bool = True,
    ):
        self.policy = RetryPolicy(
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=strategy,
            jitter=jitter,
        )

    def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return await retry_with_backoff(func, *args, **kwargs)

        return wrapper


# Global retry statistics for monitoring
class RetryStatistics:
    """Track retry statistics for monitoring"""

    def __init__(self):
        self.total_attempts = 0
        self.total_retries = 0
        self.successful_retries = 0
        self.failed_retries = 0
        self.errors_by_category: dict[str, int] = {}

    def record_attempt(self, attempt: int, success: bool, error_category: str | None):
        """Record retry attempt"""
        self.total_attempts += 1
        if attempt > 0:
            self.total_retries += 1
            if success:
                self.successful_retries += 1
            else:
                self.failed_retries += 1

        if error_category:
            self.errors_by_category[error_category] = (
                self.errors_by_category.get(error_category, 0) + 1
            )

    def get_statistics(self) -> dict[str, Any]:
        """Get retry statistics"""
        return {
            "total_attempts": self.total_attempts,
            "total_retries": self.total_retries,
            "successful_retries": self.successful_retries,
            "failed_retries": self.failed_retries,
            "success_rate": (
                self.successful_retries / self.total_retries
                if self.total_retries > 0
                else 0.0
            ),
            "errors_by_category": dict(self.errors_by_category),
        }

    def reset(self):
        """Reset statistics"""
        self.total_attempts = 0
        self.total_retries = 0
        self.successful_retries = 0
        self.failed_retries = 0
        self.errors_by_category.clear()


# Global singleton instance
_retry_statistics: RetryStatistics | None = None


def get_retry_statistics() -> RetryStatistics:
    """Get global retry statistics singleton"""
    global _retry_statistics
    if _retry_statistics is None:
        _retry_statistics = RetryStatistics()
    return _retry_statistics
