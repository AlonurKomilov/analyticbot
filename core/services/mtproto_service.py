"""
MTProto Service - Business logic for MTProto operations.

Handles MTProto channel management, audit logging, and user bot interactions
without depending on infrastructure layer.
"""

import logging
from typing import Any

from core.ports.mtproto_repository import (
    IMTProtoAuditRepository,
    IMTProtoChannelRepository,
)
from core.ports.user_bot_repository import IUserBotRepository

logger = logging.getLogger(__name__)


class MTProtoService:
    """Service for MTProto operations."""

    def __init__(
        self,
        channel_repo: IMTProtoChannelRepository,
        audit_repo: IMTProtoAuditRepository,
        user_bot_repo: IUserBotRepository,
    ):
        """
        Initialize MTProto service.

        Args:
            channel_repo: MTProto channel repository
            audit_repo: MTProto audit repository
            user_bot_repo: User bot repository
        """
        self.channel_repo = channel_repo
        self.audit_repo = audit_repo
        self.user_bot_repo = user_bot_repo

    async def get_user_channels(
        self, user_id: int, offset: int = 0, limit: int = 50
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Get user's MTProto channels with pagination.

        Args:
            user_id: User ID
            offset: Offset for pagination
            limit: Limit for pagination

        Returns:
            Tuple of (channels, total_count)
        """
        channels, total = await self.channel_repo.list_with_pagination(user_id, offset, limit)
        logger.info(f"Retrieved {len(channels)} MTProto channels for user {user_id}")
        return channels, total

    async def create_channel(self, user_id: int, channel_data: dict[str, Any]) -> dict[str, Any]:
        """
        Create new MTProto channel.

        Args:
            user_id: User ID
            channel_data: Channel data

        Returns:
            Created channel data
        """
        # Verify user has bot configured
        user_bot = await self.user_bot_repo.get_by_user_id(user_id)
        if not user_bot:
            raise ValueError("User must configure bot before creating MTProto channels")

        # Create channel
        channel = await self.channel_repo.create({**channel_data, "user_id": user_id})

        # Log action
        await self.audit_repo.log_action(
            user_id=user_id,
            action="create_channel",
            channel_id=channel.get("id"),
            details={"channel_name": channel.get("name")},
        )

        logger.info(f"Created MTProto channel {channel.get('id')} for user {user_id}")
        return channel

    async def update_channel(
        self, user_id: int, channel_id: int, updates: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Update MTProto channel.

        Args:
            user_id: User ID
            channel_id: Channel ID
            updates: Updates to apply

        Returns:
            Updated channel data or None
        """
        # Verify ownership
        channel = await self.channel_repo.get_by_id(channel_id)
        if not channel or channel.get("user_id") != user_id:
            raise ValueError("Channel not found or access denied")

        # Update channel
        updated = await self.channel_repo.update(channel_id, updates)

        # Log action
        await self.audit_repo.log_action(
            user_id=user_id,
            action="update_channel",
            channel_id=channel_id,
            details={"updates": list(updates.keys())},
        )

        logger.info(f"Updated MTProto channel {channel_id} for user {user_id}")
        return updated

    async def delete_channel(self, user_id: int, channel_id: int) -> bool:
        """
        Delete MTProto channel.

        Args:
            user_id: User ID
            channel_id: Channel ID

        Returns:
            True if deleted, False otherwise
        """
        # Verify ownership
        channel = await self.channel_repo.get_by_id(channel_id)
        if not channel or channel.get("user_id") != user_id:
            raise ValueError("Channel not found or access denied")

        # Delete channel
        deleted = await self.channel_repo.delete(channel_id)

        # Log action
        await self.audit_repo.log_action(
            user_id=user_id,
            action="delete_channel",
            channel_id=channel_id,
            details={"channel_name": channel.get("name")},
        )

        logger.info(f"Deleted MTProto channel {channel_id} for user {user_id}")
        return deleted

    async def get_audit_log(
        self, user_id: int, channel_id: int | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        Get audit log for user or specific channel.

        Args:
            user_id: User ID
            channel_id: Optional channel ID
            limit: Maximum number of records

        Returns:
            List of audit log entries
        """
        if channel_id:
            # Verify ownership
            channel = await self.channel_repo.get_by_id(channel_id)
            if not channel or channel.get("user_id") != user_id:
                raise ValueError("Channel not found or access denied")
            return await self.audit_repo.get_channel_actions(channel_id, limit=limit)
        else:
            return await self.audit_repo.get_user_actions(user_id, limit=limit)


def get_mtproto_service(
    channel_repo: IMTProtoChannelRepository,
    audit_repo: IMTProtoAuditRepository,
    user_bot_repo: IUserBotRepository,
) -> MTProtoService:
    """
    Get MTProto service instance.

    Args:
        channel_repo: MTProto channel repository
        audit_repo: MTProto audit repository
        user_bot_repo: User bot repository

    Returns:
        MTProtoService instance
    """
    return MTProtoService(channel_repo, audit_repo, user_bot_repo)
