"""
Channels Microrouter - Pure Channel Management

This microrouter handles ONLY channel management operations (CRUD).
Domain: Channel creation, reading, updating, deletion, and basic channel operations.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from apps.migration_bridge.unified_container import get_container
from src.bot_service.services.channel_management_service import ChannelManagementService, ChannelCreate, ChannelResponse
from src.api_service.middleware.auth import (
    get_current_user, 
    require_channel_access, 
    get_current_user_id,
)
from src.bot_service.database.performance import performance_timer

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/channels", tags=["Channel Management"], responses={404: {"description": "Not found"}}
)

# === CHANNEL MODELS ===

class ChannelListResponse(BaseModel):
    id: int
    name: str
    username: str | None = None
    subscriber_count: int = 0
    is_active: bool = True
    created_at: datetime
    last_updated: datetime

class ChannelUpdateRequest(BaseModel):
    name: str | None = None
    username: str | None = None
    is_active: bool | None = None
    settings: dict[str, Any] | None = None

# === CHANNEL ENDPOINTS ===

@router.get("", response_model=list[ChannelListResponse])
async def get_user_channels(
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: get_get_container()().channel_service())
):
    """
    ## 📺 Get User Channels
    
    Retrieve all channels accessible by the current user.
    
    **Returns:**
    - List of user's channels with basic information
    """
    try:
        with performance_timer("user_channels_fetch"):
            channels = await channel_service.get_user_channels(
                user_id=current_user["id"]
            )
            
            return [
                ChannelListResponse(
                    id=channel["id"],
                    name=channel["name"],
                    username=channel.get("username"),
                    subscriber_count=channel.get("subscriber_count", 0),
                    is_active=channel.get("is_active", True),
                    created_at=channel.get("created_at", datetime.now()),
                    last_updated=channel.get("last_updated", datetime.now())
                ) for channel in channels
            ]
    except Exception as e:
        logger.error(f"User channels fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user channels")

@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: ChannelCreate,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: get_get_container()().channel_service())
):
    """
    ## ➕ Create New Channel
    
    Create a new channel for analytics tracking.
    
    **Parameters:**
    - channel_data: Channel creation data (name, username, etc.)
    
    **Returns:**
    - Created channel information
    """
    try:
        with performance_timer("channel_create"):
            # Channel creation requires authenticated user
            channel = await channel_service.create_channel(
                channel_data.name,
                channel_data.username,
                user_id=current_user["id"],
                additional_data=channel_data.additional_data or {}
            )
            
            logger.info(f"Channel created successfully: {channel['id']} by user {current_user['id']}")
            return channel
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create channel")


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: get_get_container()().channel_service())
):
    """
    ## 📺 Get Channel Details
    
    Retrieve detailed information about a specific channel.
    
    **Parameters:**
    - channel_id: Target channel ID
    
    **Returns:**
    - Detailed channel information
    """
    try:
        # Verify channel access
        await require_channel_access(channel_id, current_user["id"])
        
        with performance_timer("channel_details_fetch"):
            channel = await channel_service.get_channel(
                channel_id=channel_id,
                user_id=current_user["id"]
            )
            
            if not channel:
                raise HTTPException(status_code=404, detail="Channel not found")
                
            return ChannelResponse(**channel)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel details fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch channel details")

@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    update_data: ChannelUpdateRequest,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: get_get_container()().channel_service())
):
    """
    ## ✏️ Update Channel
    
    Update channel information and settings.
    
    **Parameters:**
    - channel_id: Target channel ID
    - update_data: Channel update data
    
    **Returns:**
    - Updated channel information
    """
    try:
        # Verify user has access to this channel
        await require_channel_access(channel_id, current_user["id"])
        
        with performance_timer("channel_update"):
            # Filter out None values
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            
            if not update_dict:
                raise HTTPException(status_code=400, detail="No update data provided")
            
            channel = await channel_service.update_channel(
                channel_id=channel_id,
                user_id=current_user["id"],
                update_data=update_dict
            )
            
            logger.info(f"Channel updated successfully: {channel_id} by user {current_user['id']}")
            return ChannelResponse(**channel)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel update failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to update channel")

@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: get_get_container()().channel_service())
):
    """
    ## 🗑️ Delete Channel
    
    Delete a channel and all associated analytics data.
    
    **Parameters:**
    - channel_id: Target channel ID
    
    **Returns:**
    - Deletion confirmation
    """
    try:
        # Verify channel access and delete permissions
        await require_channel_access(channel_id, current_user["id"])
        # Verify user has access to this channel
        await require_channel_access(channel_id, current_user["id"])
        
        with performance_timer("channel_deletion"):
            result = await channel_service.delete_channel(
                channel_id=channel_id,
                user_id=current_user["id"]
            )
            
            if not result:
                raise HTTPException(status_code=404, detail="Channel not found or already deleted")
            
            logger.info(f"Channel deleted successfully: {channel_id} by user {current_user['id']}")
            return {
                "message": "Channel deleted successfully",
                "channel_id": channel_id,
                "deleted_at": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete channel")

@router.post("/{channel_id}/activate")
async def activate_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: get_get_container()().channel_service())
):
    """
    ## ✅ Activate Channel
    
    Activate a channel for analytics tracking.
    
    **Parameters:**
    - channel_id: Target channel ID
    
    **Returns:**
    - Activation confirmation
    """
    try:
        await require_channel_access(channel_id, current_user["id"])
        
        with performance_timer("channel_activation"):
            result = await channel_service.update_channel(
                channel_id=channel_id,
                user_id=current_user["id"],
                update_data={"is_active": True}
            )
            
            logger.info(f"Channel activated: {channel_id} by user {current_user['id']}")
            return {
                "message": "Channel activated successfully",
                "channel_id": channel_id,
                "is_active": True,
                "activated_at": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel activation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to activate channel")

@router.post("/{channel_id}/deactivate")
async def deactivate_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: get_get_container()().channel_service())
):
    """
    ## ❌ Deactivate Channel
    
    Deactivate a channel to stop analytics tracking.
    
    **Parameters:**
    - channel_id: Target channel ID
    
    **Returns:**
    - Deactivation confirmation
    """
    try:
        await require_channel_access(channel_id, current_user["id"])
        
        with performance_timer("channel_deactivation"):
            result = await channel_service.update_channel(
                channel_id=channel_id,
                user_id=current_user["id"],
                update_data={"is_active": False}
            )
            
            logger.info(f"Channel deactivated: {channel_id} by user {current_user['id']}")
            return {
                "message": "Channel deactivated successfully",
                "channel_id": channel_id,
                "is_active": False,
                "deactivated_at": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel deactivation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate channel")

@router.get("/{channel_id}/status")
async def get_channel_status(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: get_get_container()().channel_service())
):
    """
    ## 📊 Get Channel Status
    
    Get the current status and basic statistics of a channel.
    
    **Parameters:**
    - channel_id: Target channel ID
    
    **Returns:**
    - Channel status information
    """
    try:
        await require_channel_access(channel_id, current_user["id"])
        
        with performance_timer("channel_status_fetch"):
            status_info = await channel_service.get_channel_status(
                channel_id=channel_id,
                user_id=current_user["id"]
            )
            
            return {
                "channel_id": channel_id,
                "is_active": status_info.get("is_active", False),
                "last_update": status_info.get("last_update"),
                "subscriber_count": status_info.get("subscriber_count", 0),
                "total_posts": status_info.get("total_posts", 0),
                "analytics_enabled": status_info.get("analytics_enabled", False),
                "connection_status": status_info.get("connection_status", "unknown"),
                "last_sync": status_info.get("last_sync"),
                "checked_at": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel status fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch channel status")


# End of channels router - analytics endpoints moved to analytics_insights_router.py