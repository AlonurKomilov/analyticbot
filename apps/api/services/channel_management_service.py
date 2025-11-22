"""
Channel Management Application Service
Application layer adapter that wraps core ChannelService with HTTP/Pydantic interface
"""

import logging
from datetime import datetime

from fastapi import HTTPException, status
from pydantic import BaseModel

from core.services.channel_service import ChannelData, ChannelService

logger = logging.getLogger(__name__)


class ChannelCreate(BaseModel):
    """Pydantic model for channel creation requests"""

    name: str
    telegram_id: int
    description: str = ""
    user_id: int | None = None


class ChannelResponse(BaseModel):
    """Pydantic model for channel responses"""

    id: int
    name: str
    telegram_id: int
    description: str
    created_at: datetime
    is_active: bool
    user_id: int | None = None
    subscriber_count: int = 0


class ChannelManagementService:
    """Application service adapter for HTTP/REST channel operations"""

    def __init__(self, core_channel_service: ChannelService, telegram_validation_service=None):
        """Initialize with core service dependency and optional Telegram validation

        Args:
            core_channel_service: Core domain service for channel operations
            telegram_validation_service: Optional Telegram validation service for real channel validation
        """
        self.core_service = core_channel_service
        self.telegram_service = telegram_validation_service
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_channels_with_pagination(
        self, skip: int = 0, limit: int = 100
    ) -> list[ChannelResponse]:
        """
        Get list of all channels with pagination support (HTTP interface)

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of ChannelResponse Pydantic models

        Raises:
            HTTPException: If operation fails
        """
        try:
            channels = await self.core_service.get_channels(skip=skip, limit=limit)
            return [self._map_domain_to_response(channel) for channel in channels]

        except ValueError as e:
            self.logger.error(f"Validation error fetching channels: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            self.logger.error(f"Error fetching channels: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch channels",
            )

    async def create_channel(self, channel_data: ChannelCreate) -> ChannelResponse:
        """
        Create a new channel (HTTP interface)

        If Telegram validation service is available, validates the channel first
        and enriches data with real Telegram information.

        Args:
            channel_data: Pydantic model with channel data

        Returns:
            Created channel as ChannelResponse

        Raises:
            HTTPException: If creation fails or validation fails
        """
        try:
            # If we have telegram service and telegram_id is temporary/missing, validate
            if self.telegram_service and (
                channel_data.telegram_id <= 0 or channel_data.telegram_id > 1000000000
            ):
                self.logger.info(f"Validating channel via Telegram: {channel_data.name}")

                # Try to extract username from name or description
                username = channel_data.name
                if not username.startswith("@"):
                    username = f"@{username}"

                try:
                    # Validate with Telegram API
                    validation_result = await self.telegram_service.validate_channel_by_username(
                        username
                    )

                    if validation_result.is_valid:
                        self.logger.info(
                            f"Channel validated successfully: {validation_result.title}"
                        )
                        # Use real Telegram data
                        channel_data.telegram_id = validation_result.telegram_id
                        channel_data.name = validation_result.title
                        if validation_result.description:
                            channel_data.description = validation_result.description
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Channel validation failed: {validation_result.error_message}",
                        )

                except Exception as telegram_error:
                    self.logger.warning(f"Telegram validation failed: {telegram_error}")
                    # Continue without validation in case of Telegram API issues
                    self.logger.info("Proceeding with channel creation without Telegram validation")

            # Convert Pydantic model to domain data
            domain_data = ChannelData(
                name=channel_data.name,
                telegram_id=channel_data.telegram_id,
                description=channel_data.description,
                user_id=channel_data.user_id,
            )

            created_channel = await self.core_service.create_channel(domain_data)
            return self._map_domain_to_response(created_channel)

        except HTTPException:
            raise
        except ValueError as e:
            self.logger.error(f"Validation error creating channel: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            self.logger.error(f"Error creating channel: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create channel",
            )

    async def get_channel(self, channel_id: int) -> ChannelResponse:
        """
        Get channel by ID (HTTP interface)

        Args:
            channel_id: Channel ID to retrieve

        Returns:
            Channel as ChannelResponse

        Raises:
            HTTPException: If channel not found or operation fails
        """
        try:
            channel = await self.core_service.get_channel_by_id(channel_id)
            if not channel:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Channel with ID {channel_id} not found",
                )

            return self._map_domain_to_response(channel)

        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            self.logger.error(f"Error getting channel {channel_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get channel",
            )

    async def delete_channel(self, channel_id: int) -> dict:
        """
        Delete channel (HTTP interface)

        Args:
            channel_id: Channel ID to delete

        Returns:
            Success message

        Raises:
            HTTPException: If deletion fails
        """
        try:
            success = await self.core_service.delete_channel(channel_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Channel with ID {channel_id} not found",
                )

            return {"message": f"Channel {channel_id} deleted successfully"}

        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            self.logger.error(f"Error deleting channel {channel_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete channel",
            )

    async def get_user_channels(self, user_id: int) -> list[ChannelResponse]:
        """
        Get all channels for a user (HTTP interface)

        Args:
            user_id: User ID to get channels for

        Returns:
            List of user's channels

        Raises:
            HTTPException: If operation fails
        """
        try:
            self.logger.info(f"Fetching channels for user {user_id}")
            channels = await self.core_service.get_user_channels(user_id)
            self.logger.info(f"Found {len(channels)} channels for user {user_id}")
            return [self._map_domain_to_response(channel) for channel in channels]

        except ValueError as e:
            self.logger.error(f"ValueError getting channels for user {user_id}: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            self.logger.error(f"Exception getting channels for user {user_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user channels: {str(e)}",
            )

    def _map_domain_to_response(self, channel) -> ChannelResponse:
        """Map core domain entity to HTTP response model"""
        return ChannelResponse(
            id=channel.id,
            name=channel.name,
            telegram_id=channel.telegram_id,
            description=channel.description,
            created_at=channel.created_at,
            is_active=channel.is_active,
            user_id=channel.user_id,
            subscriber_count=channel.subscriber_count,
        )

    async def get_all_channels_admin(
        self, skip: int = 0, limit: int = 100
    ) -> list[ChannelResponse]:
        """Admin method to get all channels (HTTP interface)"""
        try:
            # Use get_channels instead of non-existent get_all_channels
            channels = await self.core_service.get_channels(skip=skip, limit=limit)
            return [self._map_domain_to_response(channel) for channel in channels]
        except Exception as e:
            self.logger.error(f"Error getting all channels for admin: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get channels",
            )

    async def admin_delete_channel(self, channel_id: int) -> dict:
        """Admin method to delete a channel"""
        try:
            await self.core_service.delete_channel(channel_id)
            return {"message": "Channel deleted successfully", "channel_id": channel_id}
        except Exception as e:
            self.logger.error(f"Error deleting channel {channel_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete channel",
            )

    async def suspend_channel(self, channel_id: int) -> dict:
        """
        Suspend a channel

        ✅ Issue #3 Phase 4: Real implementation using core service
        """
        try:
            await self.core_service.update_channel_status(channel_id, is_active=False)
            self.logger.info(f"Channel {channel_id} suspended successfully")
            return {
                "message": f"Channel {channel_id} suspended successfully",
                "channel_id": channel_id,
                "status": "suspended",
            }
        except ValueError as e:
            self.logger.error(f"Validation error suspending channel {channel_id}: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            self.logger.error(f"Error suspending channel {channel_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to suspend channel",
            )

    async def unsuspend_channel(self, channel_id: int) -> dict:
        """
        Unsuspend a channel

        ✅ Issue #3 Phase 4: Real implementation using core service
        """
        try:
            await self.core_service.update_channel_status(channel_id, is_active=True)
            self.logger.info(f"Channel {channel_id} unsuspended successfully")
            return {
                "message": f"Channel {channel_id} unsuspended successfully",
                "channel_id": channel_id,
                "status": "active",
            }
        except ValueError as e:
            self.logger.error(f"Validation error unsuspending channel {channel_id}: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            self.logger.error(f"Error unsuspending channel {channel_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to unsuspend channel",
            )

    async def update_channel(self, channel_id: int, **kwargs) -> ChannelResponse:
        """
        Update a channel

        ✅ Issue #3 Phase 4: Real implementation using core service
        """
        try:
            if not kwargs:
                raise ValueError("No fields provided for update")

            # Filter allowed fields
            allowed_fields = {"name", "description", "username", "is_active"}
            update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

            if not update_fields:
                raise ValueError(f"No valid fields to update. Allowed: {allowed_fields}")

            updated_channel = await self.core_service.update_channel(channel_id, **update_fields)
            self.logger.info(
                f"Channel {channel_id} updated successfully with fields: {list(update_fields.keys())}"
            )

            return self._map_domain_to_response(updated_channel)
        except ValueError as e:
            self.logger.error(f"Validation error updating channel {channel_id}: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error updating channel {channel_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update channel",
            )

    async def get_channel_status(self, channel_id: int) -> dict:
        """Get channel status information"""
        try:
            channel = await self.core_service.get_channel_by_id(channel_id)
            if not channel:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Channel with ID {channel_id} not found",
                )
            return {
                "channel_id": channel_id,
                "is_active": channel.is_active,
                "status": "active" if channel.is_active else "suspended",
                "last_updated": getattr(channel, "updated_at", None),
            }
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error getting channel status {channel_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get channel status",
            )
