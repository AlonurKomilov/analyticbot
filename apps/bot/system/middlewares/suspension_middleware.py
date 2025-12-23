"""
Suspension Check Middleware for Telegram Bot

Checks if the user is suspended before processing any bot commands.
Suspended users receive a message explaining their suspension and cannot use the bot.

Performance: Uses Redis caching to avoid DB query per request (5 min TTL).
"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

logger = logging.getLogger(__name__)

# Cache TTL for suspension status (5 minutes)
SUSPENSION_CACHE_TTL = 300


class SuspensionCheckMiddleware(BaseMiddleware):
    """
    Middleware that blocks suspended users from using the bot.

    Performance optimized with Redis caching:
    - Suspension status cached for 5 minutes
    - Cache invalidated when user is suspended/unsuspended
    - Falls back to DB if Redis unavailable

    When a suspended user tries to use the bot:
    1. Their request is blocked
    2. They receive a message explaining:
       - That their account is suspended
       - The reason for suspension
       - How to contact support
    """

    SUSPENSION_MESSAGE_TEMPLATE = """
🚫 <b>Account Suspended</b>

Your account has been suspended and you cannot use this bot.

<b>Reason:</b> {reason}
<b>Suspended at:</b> {suspended_at}

If you believe this is a mistake, please contact support:
📧 support@analyticbot.org

Your data collection and scheduled posts have been paused until your account is restored.
"""

    @staticmethod
    def _cache_key(user_id: int) -> str:
        """Generate cache key for suspension status"""
        return f"suspension:status:{user_id}"

    @staticmethod
    async def invalidate_cache(user_id: int) -> None:
        """
        Invalidate suspension cache for a user.
        Call this when suspending or unsuspending a user.
        """
        try:
            from apps.di import get_container

            container = get_container()
            redis = await container.cache.redis_client()
            if redis:
                await redis.delete(SuspensionCheckMiddleware._cache_key(user_id))
                logger.debug(f"Invalidated suspension cache for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to invalidate suspension cache: {e}")

    async def _get_suspension_status(self, user_id: int) -> dict | None:
        """
        Get suspension status with Redis caching.
        Returns dict with status info or None if user not found.
        """
        import json

        from apps.di import get_container

        container = get_container()
        cache_key = self._cache_key(user_id)

        # Try Redis cache first
        try:
            redis = await container.cache.redis_client()
            if redis:
                cached = await redis.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    logger.debug(f"Suspension cache HIT for user {user_id}")
                    return data
        except Exception as e:
            logger.warning(f"Redis cache error: {e}")

        # Cache miss - query database
        logger.debug(f"Suspension cache MISS for user {user_id}")
        try:
            pool = await container.database.asyncpg_pool()
            async with pool.acquire() as conn:
                user_data = await conn.fetchrow(
                    """
                    SELECT status, suspension_reason, suspended_at
                    FROM users
                    WHERE telegram_id = $1 OR id = $1
                    """,
                    user_id,
                )

                if user_data:
                    result = {
                        "status": user_data["status"],
                        "suspension_reason": user_data["suspension_reason"],
                        "suspended_at": (
                            user_data["suspended_at"].isoformat()
                            if user_data["suspended_at"]
                            else None
                        ),
                    }

                    # Cache the result
                    try:
                        redis = await container.cache.redis_client()
                        if redis:
                            await redis.setex(cache_key, SUSPENSION_CACHE_TTL, json.dumps(result))
                    except Exception as e:
                        logger.warning(f"Failed to cache suspension status: {e}")

                    return result
                return None

        except Exception as e:
            logger.error(f"Database error checking suspension: {e}")
            return None

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Extract user ID from the event
        user_id = None

        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id is None:
            # No user to check, continue normally
            return await handler(event, data)

        # Check if user is suspended (with caching)
        try:
            user_data = await self._get_suspension_status(user_id)

            if user_data and user_data["status"] == "suspended":
                reason = user_data["suspension_reason"] or "Violation of terms of service"
                suspended_at = user_data["suspended_at"]
                suspended_at_str = (
                    suspended_at[:16].replace("T", " ") + " UTC" if suspended_at else "Unknown"
                )

                logger.warning(f"Suspended user {user_id} attempted to use bot. Reason: {reason}")

                # Send suspension message
                message = self.SUSPENSION_MESSAGE_TEMPLATE.format(
                    reason=reason,
                    suspended_at=suspended_at_str,
                )

                if isinstance(event, Message):
                    await event.answer(message, parse_mode="HTML")
                elif isinstance(event, CallbackQuery):
                    await event.answer("Your account is suspended", show_alert=True)
                    if event.message:
                        await event.message.answer(message, parse_mode="HTML")

                # Block further processing
                return None

        except Exception as e:
            # If we can't check suspension status, log but allow the request
            # This prevents blocking users if there's a database issue
            logger.error(f"Failed to check suspension status for user {user_id}: {e}")

        # User is not suspended, continue with handler
        return await handler(event, data)
