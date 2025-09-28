"""
Channel Management Application Service
Application layer adapter that wraps core ChannelService with HTTP/Pydantic interface
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel

from core.services.channel_service import ChannelService, ChannelData

logger = logging.getLogger(__name__)


class ChannelCreate(BaseModel):
    """Pydantic model for channel creation requests"""
    name: str
    telegram_id: int
    description: str = ""
    user_id: Optional[int] = None


class ChannelResponse(BaseModel):
    """Pydantic model for channel responses"""
    id: int
    name: str
    telegram_id: int
    description: str
    created_at: datetime
    is_active: bool
    user_id: Optional[int] = None
    subscriber_count: int = 0


class ChannelManagementService:
    """Application service adapter for HTTP/REST channel operations"""
    
    def __init__(self, core_channel_service: ChannelService):
        """Initialize with core service dependency"""
        self.core_service = core_channel_service
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def get_channels_with_pagination(self, skip: int = 0, limit: int = 100) -> List[ChannelResponse]:
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
        Create a new channel (HTTP interface)
        
        Args:
            channel_data: Pydantic model with channel data
            
        Returns:
            Created channel as ChannelResponse
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            # Convert Pydantic model to domain data
            domain_data = ChannelData(
                name=channel_data.name,
                telegram_id=channel_data.telegram_id,
                description=channel_data.description,
                user_id=channel_data.user_id
            )
            
            created_channel = await self.core_service.create_channel(domain_data)
            return self._map_domain_to_response(created_channel)
            
        except ValueError as e:
            self.logger.error(f"Validation error creating channel: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            self.logger.error(f"Error creating channel: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create channel"
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
                    detail=f"Channel with ID {channel_id} not found"
                )
            
            return self._map_domain_to_response(channel)
            
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            self.logger.error(f"Error getting channel {channel_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get channel"
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
                    detail=f"Channel with ID {channel_id} not found"
                )
            
            return {"message": f"Channel {channel_id} deleted successfully"}
            
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            self.logger.error(f"Error deleting channel {channel_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete channel"
            )

    async def get_user_channels(self, user_id: int) -> List[ChannelResponse]:
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
            channels = await self.core_service.get_user_channels(user_id)
            return [self._map_domain_to_response(channel) for channel in channels]
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            self.logger.error(f"Error getting channels for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user channels"
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
            subscriber_count=channel.subscriber_count
        )