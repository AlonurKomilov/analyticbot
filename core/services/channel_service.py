"""
Channel Service - Core Business Logic
Pure domain service without framework dependencies
"""

import logging
from dataclasses import dataclass
from datetime import datetime

from core.ports.repository_ports import ChannelRepository

logger = logging.getLogger(__name__)


@dataclass
class ChannelData:
    """Channel data transfer object"""

    name: str
    telegram_id: int
    description: str = ""
    user_id: int | None = None


@dataclass
class Channel:
    """Channel domain entity"""

    id: int
    name: str
    telegram_id: int
    description: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    user_id: int | None = None
    subscriber_count: int = 0


class ChannelService:
    """Core service for channel business logic - framework agnostic"""

    def __init__(self, channel_repository: ChannelRepository):
        """Initialize with repository dependency injection"""
        self.channel_repo = channel_repository
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_channels(self, skip: int = 0, limit: int = 100) -> list[Channel]:
        """
        Get list of channels with pagination

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Channel domain entities

        Raises:
            ValueError: If pagination parameters are invalid
        """
        # Validate business rules
        if skip < 0:
            raise ValueError("Skip parameter must be non-negative")
        if limit <= 0 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")

        self.logger.info(f"Fetching channels with skip={skip}, limit={limit}")

        try:
            channel_records = await self.channel_repo.get_channels(skip=skip, limit=limit)
            return [self._map_record_to_entity(record) for record in channel_records]
        except Exception as e:
            self.logger.error(f"Error fetching channels: {e}")
            raise

    async def create_channel(self, channel_data: ChannelData) -> Channel:
        """
        Create a new channel with business validation

        Args:
            channel_data: Channel data to create

        Returns:
            Created Channel entity

        Raises:
            ValueError: If validation fails
        """
        # Business validation
        if not channel_data.name or len(channel_data.name.strip()) == 0:
            raise ValueError("Channel name cannot be empty")

        if len(channel_data.name) > 100:
            raise ValueError("Channel name cannot exceed 100 characters")

        if channel_data.telegram_id <= 0:
            raise ValueError("Invalid Telegram ID")

        # Check for duplicate telegram_id
        existing_channel = await self.channel_repo.get_channel_by_telegram_id(
            channel_data.telegram_id
        )
        if existing_channel:
            raise ValueError(f"Channel with Telegram ID {channel_data.telegram_id} already exists")

        self.logger.info(f"Creating channel: {channel_data.name}")

        try:
            # Use the protocol's create_channel method signature
            await self.channel_repo.create_channel(
                channel_id=channel_data.telegram_id,
                user_id=channel_data.user_id or 0,
                title=channel_data.name.strip(),
                username=channel_data.name.lower().replace(" ", "_"),
            )

            # Get the created channel back
            created_record = await self.channel_repo.get_channel_by_telegram_id(
                channel_data.telegram_id
            )
            if not created_record:
                raise RuntimeError("Failed to retrieve created channel")

            return self._map_record_to_entity(created_record)
        except Exception as e:
            self.logger.error(f"Error creating channel: {e}")
            raise

    async def get_channel_by_id(self, channel_id: int) -> Channel | None:
        """
        Get channel by ID

        Args:
            channel_id: Channel ID to search for

        Returns:
            Channel entity if found, None otherwise
        """
        if channel_id <= 0:
            raise ValueError("Channel ID must be positive")

        try:
            record = await self.channel_repo.get_channel_by_id(channel_id)
            return self._map_record_to_entity(record) if record else None
        except Exception as e:
            self.logger.error(f"Error fetching channel {channel_id}: {e}")
            raise

    async def get_channel_by_telegram_id(self, telegram_id: int) -> Channel | None:
        """
        Get channel by Telegram ID

        Args:
            telegram_id: Telegram ID to search for

        Returns:
            Channel entity if found, None otherwise
        """
        if telegram_id <= 0:
            raise ValueError("Telegram ID must be positive")

        try:
            record = await self.channel_repo.get_channel_by_telegram_id(telegram_id)
            return self._map_record_to_entity(record) if record else None
        except Exception as e:
            self.logger.error(f"Error fetching channel with telegram_id {telegram_id}: {e}")
            raise

    async def update_channel_status(self, channel_id: int, is_active: bool) -> None:
        """
        Update channel active status (suspend/unsuspend)

        ✅ Issue #3 Phase 4: Added for channel suspension functionality

        Args:
            channel_id: Channel ID to update
            is_active: New active status (True=active, False=suspended)

        Raises:
            ValueError: If channel_id is invalid
        """
        if channel_id <= 0:
            raise ValueError("Channel ID must be positive")

        self.logger.info(
            f"Updating channel {channel_id} status to {'active' if is_active else 'suspended'}"
        )

        try:
            await self.channel_repo.update_channel_status(channel_id, is_active)
        except Exception as e:
            self.logger.error(f"Error updating channel {channel_id} status: {e}")
            raise

    async def update_channel(self, channel_id: int, **kwargs) -> Channel:
        """
        Update channel with provided fields

        ✅ Issue #3 Phase 4: Added for channel update functionality

        Args:
            channel_id: Channel ID to update
            **kwargs: Fields to update (name, description, username, is_active, etc.)

        Returns:
            Updated channel entity

        Raises:
            ValueError: If channel_id is invalid or channel not found
        """
        if channel_id <= 0:
            raise ValueError("Channel ID must be positive")

        if not kwargs:
            raise ValueError("No fields provided for update")

        self.logger.info(f"Updating channel {channel_id} with fields: {list(kwargs.keys())}")

        try:
            updated_record = await self.channel_repo.update_channel(channel_id, **kwargs)
            if not updated_record:
                raise ValueError(f"Channel with ID {channel_id} not found")
            return self._map_record_to_entity(updated_record)
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating channel {channel_id}: {e}")
            raise

    async def delete_channel(self, channel_id: int) -> bool:
        """
        Soft delete a channel

        Args:
            channel_id: Channel ID to delete

        Returns:
            True if deleted successfully
        """
        if channel_id <= 0:
            raise ValueError("Channel ID must be positive")

        self.logger.info(f"Deleting channel {channel_id}")

        try:
            return await self.channel_repo.delete_channel(channel_id)
        except Exception as e:
            self.logger.error(f"Error deleting channel {channel_id}: {e}")
            raise

    async def get_user_channels(self, user_id: int) -> list[Channel]:
        """
        Get all channels for a specific user

        Args:
            user_id: User ID to get channels for

        Returns:
            List of Channel entities
        """
        if user_id <= 0:
            raise ValueError("User ID must be positive")

        try:
            channel_records = await self.channel_repo.get_user_channels(user_id)
            return [self._map_record_to_entity(record) for record in channel_records]
        except Exception as e:
            self.logger.error(f"Error fetching channels for user {user_id}: {e}")
            raise

    def _map_record_to_entity(self, record: dict) -> Channel:
        """Map database record to Channel domain entity"""
        return Channel(
            id=record["id"],
            name=record["name"],
            telegram_id=record["telegram_id"],
            description=record.get("description", ""),
            created_at=record["created_at"],
            updated_at=record.get("updated_at", record["created_at"]),
            is_active=record.get("is_active", True),
            user_id=record.get("user_id"),
            subscriber_count=record.get("subscriber_count", 0),
        )
