"""
MTProto Service Factory - Helper to get MTProto service with proper DI injection.

This module provides factory functions that properly inject dependencies
from the DI container into MTProto service.
"""

from apps.di import get_container
from core.services.mtproto_service import MTProtoService, get_mtproto_service


async def create_mtproto_service() -> MTProtoService:
    """
    Create MTProto service with all dependencies injected from DI container.

    Returns:
        MTProtoService with dependencies injected
    """
    container = get_container()

    # Get repositories from DI container
    channel_repo = await container.database.channel_mtproto_repo()
    user_bot_repo = await container.database.user_bot_repo()

    # Create audit repo (assuming it exists or will be added to DI container)
    # For now, we'll use the channel_mtproto_repo as it likely has audit capabilities
    audit_repo = channel_repo  # TODO: Add proper audit repository to DI container

    return get_mtproto_service(channel_repo, audit_repo, user_bot_repo)
