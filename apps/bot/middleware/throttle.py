"""
Throttling middleware for bot commands
Rate limiting to prevent API abuse and ensure stable performance
"""

import asyncio
import time
from collections import defaultdict
from functools import wraps
from typing import Any, Callable, Dict, Optional

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware


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
        self.requests: Dict[str, float] = {}
    
    def _get_key(self, event: types.TelegramObject) -> str:
        """Get throttling key based on strategy"""
        if self.key_strategy == "user":
            if hasattr(event, 'from_user') and event.from_user:
                return f"user:{event.from_user.id}"
        elif self.key_strategy == "chat":
            if hasattr(event, 'chat') and event.chat:
                return f"chat:{event.chat.id}"
        elif self.key_strategy == "global":
            return "global"
        
        # Fallback to global if no specific key found
        return "global"
    
    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Any],
        event: types.TelegramObject,
        data: Dict[str, Any]
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
                        show_alert=True if isinstance(event, types.CallbackQuery) else False
                    )
                elif isinstance(event, types.CallbackQuery):
                    await event.answer(
                        f"⏰ Too fast! Please wait {remaining:.1f} seconds.",
                        show_alert=True
                    )
                
                return  # Don't process the request
        
        # Update request time
        self.requests[key] = now
        
        # Call the handler
        return await handler(event, data)


def throttle(rate: float = 2.0, key: Optional[str] = None):
    """
    Decorator for throttling specific handlers
    
    Args:
        rate: Minimum time between calls (seconds)
        key: Custom throttling key, defaults to user ID
    """
    def decorator(func: Callable) -> Callable:
        # Storage for request times
        if not hasattr(throttle, '_requests'):
            throttle._requests = defaultdict(float)
        
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
                if hasattr(event, 'from_user') and event.from_user:
                    throttle_key = f"user:{event.from_user.id}:{func.__name__}"
                else:
                    throttle_key = f"global:{func.__name__}"
            
            now = time.time()
            last_request = throttle._requests[throttle_key]
            
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
                        show_alert=True
                    )
                
                return  # Don't execute the handler
            
            # Update last request time
            throttle._requests[throttle_key] = now
            
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
            if hasattr(ThrottleMiddleware, '_instances'):
                for instance in ThrottleMiddleware._instances:
                    if hasattr(instance, 'requests'):
                        keys_to_remove = [
                            key for key, timestamp in instance.requests.items()
                            if timestamp < cutoff
                        ]
                        for key in keys_to_remove:
                            del instance.requests[key]
            
            # Clean decorator requests
            if hasattr(throttle, '_requests'):
                keys_to_remove = [
                    key for key, timestamp in throttle._requests.items()
                    if timestamp < cutoff
                ]
                for key in keys_to_remove:
                    del throttle._requests[key]
                    
        except Exception:
            # Continue cleanup even if there are errors
            pass
