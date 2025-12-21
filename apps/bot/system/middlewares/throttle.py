"""
Throttling middleware for bot commands
Rate limiting to prevent API abuse and ensure stable performance
"""

import asyncio
import logging
import time
from collections import defaultdict
from collections.abc import Callable
from functools import wraps
from typing import Any, cast

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware

logger = logging.getLogger(__name__)


# Handler timeout constants (for 100K+ user scalability)
DEFAULT_HANDLER_TIMEOUT = 25  # seconds - Telegram has 30s timeout for inline queries
HEAVY_HANDLER_TIMEOUT = 55  # seconds - for heavy operations like exports


def with_timeout(timeout: float = DEFAULT_HANDLER_TIMEOUT):
    """
    Decorator to add timeout protection to bot handlers.
    
    Prevents handlers from running indefinitely, which is critical at scale.
    Telegram has internal timeouts; handlers must complete within those limits.
    
    Args:
        timeout: Maximum execution time in seconds (default 25s)
    
    Example:
        @router.message(Command("export"))
        @with_timeout(30)
        async def handle_export(message: Message):
            # This will timeout after 30 seconds
            ...
    """
    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        async def wrapper(*args, **kwargs):
            # Extract event for error messaging
            event = None
            for arg in args:
                if isinstance(arg, (types.Message, types.CallbackQuery)):
                    event = arg
                    break
            
            try:
                async with asyncio.timeout(timeout):
                    return await handler(*args, **kwargs)
            except asyncio.TimeoutError:
                logger.warning(
                    f"⏰ Handler {handler.__name__} timed out after {timeout}s"
                )
                # Notify user gracefully
                if event:
                    error_msg = (
                        "⏰ Operation timed out. Please try again.\n"
                        "If this persists, the service may be under heavy load."
                    )
                    try:
                        if isinstance(event, types.Message):
                            await event.answer(error_msg)
                        elif isinstance(event, types.CallbackQuery):
                            await event.answer(error_msg, show_alert=True)
                    except Exception:
                        pass  # Best effort notification
                return None
            except Exception:
                raise  # Re-raise other exceptions
        
        return wrapper
    return decorator


class ThrottleMiddleware(BaseMiddleware):
    """
    Aiogram middleware for request throttling
    Prevents users from sending too many requests
    """

    def __init__(self, rate: float = 1.0, key_strategy: str = "user"):
        """
        Initialize throttle middleware

        Args:
            rate: Minimum time between requests (seconds)
            key_strategy: Throttling key strategy ("user", "chat", "global")
        """
        self.rate = rate
        self.key_strategy = key_strategy
        self.requests: dict[str, float] = {}

    def _get_key(self, event: types.TelegramObject) -> str:
        """Get throttling key based on strategy"""
        if self.key_strategy == "user":
            # Check for from_user attribute with proper type narrowing
            from_user = getattr(event, "from_user", None)
            if from_user is not None:
                user_id = getattr(from_user, "id", None)
                if user_id is not None:
                    return f"user:{user_id}"
        elif self.key_strategy == "chat":
            # Check for chat attribute with proper type narrowing
            chat = getattr(event, "chat", None)
            if chat is not None:
                chat_id = getattr(chat, "id", None)
                if chat_id is not None:
                    return f"chat:{chat_id}"
        elif self.key_strategy == "global":
            return "global"

        # Fallback to global if no specific key found
        return "global"

    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, dict[str, Any]], Any],
        event: types.TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Check throttling and call handler"""
        key = self._get_key(event)
        now = time.time()

        # Check if request is throttled
        if key in self.requests:
            time_passed = now - self.requests[key]
            if time_passed < self.rate:
                # Request is throttled
                remaining = self.rate - time_passed

                # For messages, send throttle notification
                if isinstance(event, types.Message):
                    await event.answer(
                        f"⏰ Too fast! Please wait {remaining:.1f} seconds.",
                        show_alert=True if isinstance(event, types.CallbackQuery) else False,
                    )
                elif isinstance(event, types.CallbackQuery):
                    await event.answer(
                        f"⏰ Too fast! Please wait {remaining:.1f} seconds.", show_alert=True
                    )

                return  # Don't process the request

        # Update request time
        self.requests[key] = now

        # Call the handler
        return await handler(event, data)


def throttle(rate: float = 2.0, key: str | None = None):
    """
    Decorator for throttling specific handlers

    Args:
        rate: Minimum time between calls (seconds)
        key: Custom throttling key, defaults to user ID
    """

    def decorator(func: Callable) -> Callable:
        # Storage for request times
        if not hasattr(throttle, "_requests"):
            cast(Any, throttle)._requests = defaultdict(float)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract event from arguments
            event = None
            for arg in args:
                if isinstance(arg, (types.Message, types.CallbackQuery)):
                    event = arg
                    break

            if not event:
                # No event found, proceed without throttling
                return await func(*args, **kwargs)

            # Generate throttling key
            throttle_key = key
            if not throttle_key:
                if hasattr(event, "from_user") and event.from_user:
                    throttle_key = f"user:{event.from_user.id}:{func.__name__}"
                else:
                    throttle_key = f"global:{func.__name__}"

            now = time.time()
            # Access dynamic attribute with cast for type safety
            throttle_requests = cast(Any, throttle)._requests
            last_request = throttle_requests[throttle_key]

            # Check throttling
            if now - last_request < rate:
                remaining = rate - (now - last_request)

                if isinstance(event, types.Message):
                    await event.answer(
                        f"⏰ Please wait {remaining:.1f}s before using this command again."
                    )
                elif isinstance(event, types.CallbackQuery):
                    await event.answer(
                        f"⏰ Please wait {remaining:.1f}s before using this feature again.",
                        show_alert=True,
                    )

                return  # Don't execute the handler

            # Update last request time
            throttle_requests[throttle_key] = now

            # Execute the handler
            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Cleanup old throttle entries periodically
async def cleanup_throttle_entries():
    """Clean up old throttle entries to prevent memory leaks"""
    while True:
        try:
            await asyncio.sleep(300)  # Clean up every 5 minutes

            now = time.time()
            cutoff = now - 3600  # Remove entries older than 1 hour

            # Clean middleware requests
            middleware_class = cast(Any, ThrottleMiddleware)
            if hasattr(middleware_class, "_instances"):
                for instance in middleware_class._instances:
                    if hasattr(instance, "requests"):
                        keys_to_remove = [
                            key
                            for key, timestamp in instance.requests.items()
                            if timestamp < cutoff
                        ]
                        for key in keys_to_remove:
                            del instance.requests[key]

            # Clean decorator requests
            throttle_any = cast(Any, throttle)
            if hasattr(throttle_any, "_requests"):
                keys_to_remove = [
                    key for key, timestamp in throttle_any._requests.items() if timestamp < cutoff
                ]
                for key in keys_to_remove:
                    throttle_any._requests.pop(key, None)

        except Exception:
            # Continue cleanup even if there are errors
            pass


def rate_limit(key: str = "default", per_minute: int = 60, rate: float | None = None):
    """
    Decorator for rate limiting bot handlers.
    
    Uses sliding window algorithm for accurate rate limiting.
    Falls back to in-memory tracking if Redis unavailable.

    Args:
        key: Custom key for throttling category
        per_minute: Maximum requests per minute
        rate: Minimum time between requests (seconds) - legacy parameter

    Returns:
        Decorator function
    """
    # Storage for in-memory rate limiting (fallback when Redis unavailable)
    if not hasattr(rate_limit, "_window_storage"):
        cast(Any, rate_limit)._window_storage = {}

    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        async def wrapper(*args, **kwargs):
            import logging
            import os
            from datetime import datetime
            
            logger = logging.getLogger(__name__)
            
            # Extract event from arguments
            event = None
            for arg in args:
                if isinstance(arg, (types.Message, types.CallbackQuery)):
                    event = arg
                    break

            if not event:
                return await handler(*args, **kwargs)

            # Generate unique throttling key
            user_id = None
            if hasattr(event, "from_user") and event.from_user:
                user_id = event.from_user.id
            
            throttle_key = f"rate_limit:{key}:{user_id or 'anon'}:{handler.__name__}"
            
            now = time.time()
            window_size = 60.0  # 1 minute window
            max_requests = per_minute
            
            # Try Redis first for distributed rate limiting
            redis_url = os.getenv("REDIS_URL")
            rate_limited = False
            remaining = 0
            
            if redis_url:
                try:
                    import redis.asyncio as aioredis
                    
                    redis_client = aioredis.from_url(
                        redis_url,
                        decode_responses=True,
                        socket_timeout=2.0,
                    )
                    
                    async with redis_client.pipeline(transaction=True) as pipe:
                        # Remove old entries (sliding window)
                        window_start = now - window_size
                        await pipe.zremrangebyscore(throttle_key, 0, window_start)
                        # Count current requests in window
                        await pipe.zcard(throttle_key)
                        # Add current request
                        await pipe.zadd(throttle_key, {str(now): now})
                        # Set TTL on key
                        await pipe.expire(throttle_key, int(window_size) + 10)
                        results = await pipe.execute()
                    
                    await redis_client.close()
                    
                    current_count = results[1]  # zcard result
                    
                    if current_count >= max_requests:
                        rate_limited = True
                        # Calculate when oldest request will expire
                        remaining = window_size - (now - window_start)
                        logger.debug(f"Rate limited (Redis): {throttle_key} - {current_count}/{max_requests}")
                        
                except Exception as e:
                    logger.warning(f"Redis rate limit failed, using in-memory: {e}")
                    redis_url = None  # Fall back to in-memory
            
            # In-memory fallback
            if not redis_url:
                storage = cast(Any, rate_limit)._window_storage
                
                if throttle_key not in storage:
                    storage[throttle_key] = []
                
                # Clean old entries
                window_start = now - window_size
                storage[throttle_key] = [ts for ts in storage[throttle_key] if ts > window_start]
                
                if len(storage[throttle_key]) >= max_requests:
                    rate_limited = True
                    oldest = storage[throttle_key][0] if storage[throttle_key] else now
                    remaining = window_size - (now - oldest)
                else:
                    storage[throttle_key].append(now)
            
            if rate_limited:
                remaining = max(0, remaining)
                
                if isinstance(event, types.Message):
                    await event.answer(
                        f"⏰ Rate limit exceeded ({per_minute}/min). "
                        f"Please wait {remaining:.0f}s."
                    )
                elif isinstance(event, types.CallbackQuery):
                    await event.answer(
                        f"⏰ Rate limit exceeded. Wait {remaining:.0f}s.",
                        show_alert=True,
                    )
                return None
            
            return await handler(*args, **kwargs)

        cast(Any, wrapper).__throttle_key__ = key
        cast(Any, wrapper).__throttle_per_minute__ = per_minute
        if rate is not None:
            cast(Any, wrapper).__throttle_rate__ = rate
        return wrapper

    return decorator
