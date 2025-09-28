"""
ChannelManagementService - Service layer for channel management operations

This service handles all business logic related to channel management, including:
- Channel creation with validation and conflict checking
- Channel retrieval with proper data mapping
- Channel listing with pagination support
- Channel data transformation and validation
- Business rules for channel operations

Follows Clean Architecture principles by separating channel business logic
from HTTP request handling in the router layer.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import HTTPException, status
from pydantic import BaseModel

from infra.db.repositories.channel_repository import AsyncpgChannelRepository

logger = logging.getLogger(__name__)


class ChannelCreate(BaseModel):
    name: str
    telegram_id: int
    description: str = ""


class ChannelResponse(BaseModel):
    id: int
    name: str
    telegram_id: int
    description: str
    created_at: datetime
    is_active: bool


class ChannelManagementService:
    """Service for managing channel operations and business logic"""
    
    def __init__(self, channel_repository: AsyncpgChannelRepository):
        """
        Initialize the ChannelManagementService
        
        Args:
            channel_repository: Repository for channel data operations
        """
        self.channel_repo = channel_repository
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def get_channels_with_pagination(self, skip: int = 0, limit: int = 100) -> List[ChannelResponse]:
        """
        Get list of all channels with pagination support
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of ChannelResponse objects
            
        Raises:
            HTTPException: If database operation fails
        """
        try:
            self.logger.info(f"Fetching channels with skip={skip}, limit={limit}")
            
            # Validate pagination parameters
            if skip < 0:
                raise ValueError("Skip parameter must be non-negative")
            if limit <= 0 or limit > 1000:
                raise ValueError("Limit must be between 1 and 1000")
            
            channels = await self.channel_repo.get_channels(skip=skip, limit=limit)
            
            return [
                self._map_channel_to_response(channel)
                for channel in channels
            ]
            
        except ValueError as e:
            self.logger.error(f"Validation error fetching channels: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            self.logger.error(f"Error fetching channels: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch channels"
            )
    
    async def create_channel(self, channel_data: ChannelCreate) -> ChannelResponse:
        """
        Create a new channel with validation and conflict checking
        
        Args:
            channel_data: Channel creation data
            
        Returns:
            ChannelResponse object for the created channel
            
        Raises:
            HTTPException: If channel already exists or creation fails
        """
        try:
            self.logger.info(f"Creating channel with telegram_id={channel_data.telegram_id}")
            
            # Validate channel data
            self._validate_channel_data(channel_data)
            
            # Check for existing channel
            existing_channel = await self.channel_repo.get_channel_by_telegram_id(channel_data.telegram_id)
            if existing_channel:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Channel with telegram_id {channel_data.telegram_id} already exists"
                )
            
            # Create the channel
            await self.channel_repo.create_channel(
                channel_id=channel_data.telegram_id,
                user_id=1,  # Default user ID for API requests - should be configurable
                title=channel_data.name,
                username=None
            )
            
            # Retrieve the created channel to return complete data
            channel = await self.channel_repo.get_channel_by_id(channel_data.telegram_id)
            if not channel:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve created channel"
                )
            
            self.logger.info(f"Successfully created channel with ID: {channel['id']}")
            return self._map_channel_to_response(channel)
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating channel: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create channel"
            )
    
    async def get_channel_by_id(self, channel_id: int) -> ChannelResponse:
        """
        Get a specific channel by ID
        
        Args:
            channel_id: ID of the channel to retrieve
            
        Returns:
            ChannelResponse object
            
        Raises:
            HTTPException: If channel not found or retrieval fails
        """
        try:
            self.logger.info(f"Fetching channel with ID: {channel_id}")
            
            # Validate channel ID
            if channel_id <= 0:
                raise ValueError("Channel ID must be positive")
            
            channel = await self.channel_repo.get_channel(channel_id)
            if not channel:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Channel with ID {channel_id} not found"
                )
            
            return self._map_channel_to_response(channel)
            
        except HTTPException:
            raise
        except ValueError as e:
            self.logger.error(f"Validation error fetching channel {channel_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            self.logger.error(f"Error fetching channel {channel_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch channel"
            )
    
    async def get_channel_by_telegram_id(self, telegram_id: int) -> Optional[ChannelResponse]:
        """
        Get a channel by its Telegram ID
        
        Args:
            telegram_id: Telegram ID of the channel
            
        Returns:
            ChannelResponse object if found, None otherwise
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            self.logger.info(f"Fetching channel with Telegram ID: {telegram_id}")
            
            channel = await self.channel_repo.get_channel_by_telegram_id(telegram_id)
            if not channel:
                return None
            
            return self._map_channel_to_response(channel)
            
        except Exception as e:
            self.logger.error(f"Error fetching channel by telegram_id {telegram_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch channel"
            )
    
    def _validate_channel_data(self, channel_data: ChannelCreate) -> None:
        """
        Validate channel creation data
        
        Args:
            channel_data: Channel data to validate
            
        Raises:
            ValueError: If validation fails
        """
        if not channel_data.name or not channel_data.name.strip():
            raise ValueError("Channel name cannot be empty")
        
        if len(channel_data.name) > 255:
            raise ValueError("Channel name cannot exceed 255 characters")
        
        if channel_data.telegram_id <= 0:
            raise ValueError("Telegram ID must be positive")
        
        if len(channel_data.description) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
    
    def _map_channel_to_response(self, channel: Dict[str, Any]) -> ChannelResponse:
        """
        Map database channel record to ChannelResponse object
        
        Args:
            channel: Raw channel data from database
            
        Returns:
            ChannelResponse object with properly mapped data
        """
        return ChannelResponse(
            id=channel["id"],
            name=channel.get("name", channel.get("title", "Unknown")),
            telegram_id=channel.get("telegram_id", channel["id"]),
            description=channel.get("description", ""),
            created_at=channel.get("created_at") or datetime.now(),
            is_active=channel.get("is_active", True),
        )
    
    async def get_channel_statistics(self, channel_id: int) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a channel
        
        This method would aggregate various metrics about the channel
        such as total posts, engagement rates, growth trends, etc.
        
        Args:
            channel_id: ID of the channel to get statistics for
            
        Returns:
            Dictionary with channel statistics
        """
        try:
            self.logger.info(f"Getting statistics for channel {channel_id}")
            
            # Ensure channel exists
            channel = await self.get_channel_by_id(channel_id)
            
            # TODO: Implement actual statistics aggregation
            # This would typically involve:
            # - Counting posts/messages
            # - Calculating engagement rates
            # - Analyzing growth trends
            # - Gathering subscriber statistics
            
            return {
                "channel_id": channel_id,
                "channel_name": channel.name,
                "total_posts": 0,  # Placeholder
                "avg_engagement_rate": 0.0,  # Placeholder
                "subscriber_count": 0,  # Placeholder
                "growth_rate": 0.0,  # Placeholder
                "last_activity": datetime.now(),  # Placeholder
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error getting statistics for channel {channel_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve channel statistics"
            )
    
    async def validate_channel_access(self, channel_id: int, user_id: int) -> bool:
        """
        Validate if a user has access to a specific channel
        
        Args:
            channel_id: ID of the channel
            user_id: ID of the user
            
        Returns:
            True if user has access, False otherwise
        """
        try:
            # Ensure channel exists
            await self.get_channel_by_id(channel_id)
            
            # TODO: Implement actual access control logic
            # This would typically check:
            # - User permissions
            # - Channel ownership
            # - Subscription status
            # - Admin/moderator roles
            
            self.logger.info(f"Validating access for user {user_id} to channel {channel_id}")
            return True  # Placeholder - allow all access for now
            
        except HTTPException:
            return False
        except Exception as e:
            self.logger.error(f"Error validating channel access: {e}")
            return False