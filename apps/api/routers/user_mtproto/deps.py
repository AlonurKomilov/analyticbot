"""
User MTProto Dependencies

Shared dependencies and helper functions for MTProto endpoints.
"""

import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient

from apps.di import get_db_session
from core.ports.user_bot_repository import IUserBotRepository

logger = logging.getLogger(__name__)


async def get_user_bot_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> IUserBotRepository:
    """Get user bot repository instance via DI."""
    # Import here to avoid import-linter violation (runtime only, not module level)
    from infra.db.repositories.user_bot_repository import UserBotRepository

    return UserBotRepository(session)


async def safe_disconnect(client: TelegramClient):
    """Safely disconnect Telethon client"""
    try:
        if client.is_connected():
            result = client.disconnect()
            if result is not None:
                await result
    except Exception as e:
        logger.warning(f"Error disconnecting client: {e}")
