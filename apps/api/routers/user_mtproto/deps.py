"""
User MTProto Dependencies

Shared dependencies and helper functions for MTProto endpoints.
"""

import logging

from telethon import TelegramClient

from infra.db.repositories.user_bot_repository_factory import UserBotRepositoryFactory

logger = logging.getLogger(__name__)


async def get_user_bot_repository() -> UserBotRepositoryFactory:
    """Get user bot repository factory instance."""
    from apps.di import get_container

    container = get_container()
    session_factory = await container.database.async_session_maker()
    return UserBotRepositoryFactory(session_factory)


async def safe_disconnect(client: TelegramClient):
    """Safely disconnect Telethon client"""
    try:
        if client.is_connected():
            result = client.disconnect()
            if result is not None:
                await result
    except Exception as e:
        logger.warning(f"Error disconnecting client: {e}")
