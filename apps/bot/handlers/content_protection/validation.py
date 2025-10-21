"""
Validation Helpers for Content Protection Handlers

Type guards and validation functions for aiogram message/callback handlers.
"""

from aiogram.types import CallbackQuery, Message


def validate_callback_state(callback: CallbackQuery) -> bool:
    """
    Validate callback has required attributes (message, bot, from_user).

    Args:
        callback: CallbackQuery to validate

    Returns:
        bool: True if callback has all required attributes, False otherwise
    """
    from aiogram.types import Message as MessageType

    return bool(
        callback.message
        and isinstance(callback.message, MessageType)
        and callback.bot
        and callback.from_user
    )


def validate_message_state(message: Message) -> bool:
    """
    Validate message has required attributes (bot, from_user).

    Args:
        message: Message to validate

    Returns:
        bool: True if message has all required attributes, False otherwise
    """
    return bool(message.bot and message.from_user)
