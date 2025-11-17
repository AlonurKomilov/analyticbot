"""
Bot Service Factory - Helper to get bot services with proper DI injection.

This module provides factory functions that properly inject bot_manager
from the DI container into bot management services.
"""

from apps.di import get_container
from core.ports.user_bot_repository import IUserBotRepository
from core.services.admin_bot_service import AdminBotService, get_admin_bot_service
from core.services.user_bot_service import UserBotService, get_user_bot_service


async def create_user_bot_service(repository: IUserBotRepository) -> UserBotService:
    """
    Create a UserBotService with bot_manager properly injected from DI container.

    Args:
        repository: User bot repository

    Returns:
        UserBotService with bot_manager injected
    """
    container = get_container()
    bot_manager = await container.bot.bot_manager()
    return get_user_bot_service(repository, bot_manager)


async def create_admin_bot_service(repository: IUserBotRepository) -> AdminBotService:
    """
    Create an AdminBotService with bot_manager properly injected from DI container.

    Args:
        repository: User bot repository

    Returns:
        AdminBotService with bot_manager injected
    """
    container = get_container()
    bot_manager = await container.bot.bot_manager()
    return get_admin_bot_service(repository, bot_manager)
