"""
Suspension Check Middleware for Telegram Bot

Checks if the user is suspended before processing any bot commands.
Suspended users receive a message explaining their suspension and cannot use the bot.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

logger = logging.getLogger(__name__)


class SuspensionCheckMiddleware(BaseMiddleware):
    """
    Middleware that blocks suspended users from using the bot.

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

        # Check if user is suspended
        try:
            # Import here to avoid circular import
            from apps.di import get_container

            container = get_container()
            pool = await container.database.pool()

            async with pool.acquire() as conn:
                user_data = await conn.fetchrow(
                    """
                    SELECT status, suspension_reason, suspended_at
                    FROM users
                    WHERE telegram_id = $1 OR id = $1
                """,
                    user_id,
                )

                if user_data and user_data["status"] == "suspended":
                    reason = user_data["suspension_reason"] or "Violation of terms of service"
                    suspended_at = user_data["suspended_at"]
                    suspended_at_str = (
                        suspended_at.strftime("%Y-%m-%d %H:%M UTC") if suspended_at else "Unknown"
                    )

                    logger.warning(
                        f"Suspended user {user_id} attempted to use bot. Reason: {reason}"
                    )

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
