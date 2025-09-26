"""
Admin Users Router - User Administration

Handles administrative user operations including user management, permissions, and monitoring.
Clean architecture: Single responsibility for user administration.

Domain: Admin user management operations
Path: /admin/users/*
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from apps.migration_bridge.unified_container import get_container
from src.bot_service.services.channel_management_service import ChannelManagementService
from src.api_service.middleware.auth import (
    get_current_user, 
    require_admin_role,
    get_current_user_id,
)
from src.bot_service.database.performance import performance_timer

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/admin/users", 
    tags=["Admin - User Management"], 
    responses={404: {"description": "Not found"}}
)

# === ADMIN USER MODELS ===

class UserChannelInfo(BaseModel):
    user_id: int
    username: str | None = None
    total_channels: int = 0
    active_channels: int = 0
    channels: list[dict[str, Any]] = Field(default_factory=list)
    last_activity: datetime | None = None

# === ADMIN USER ENDPOINTS ===

@router.get("/{user_id}/channels", response_model=UserChannelInfo)
async def get_user_channels_admin(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: get_get_container()().channel_service())
):
    """
    ## 👤 Get User Channels (Admin)
    
    Retrieve all channels owned by a specific user with administrative details.
    
    **Admin Only**: Requires admin role
    
    **Parameters:**
    - user_id: ID of the user to inspect
    
    **Returns:**
    - User channel information and statistics
    """
    try:
        await require_admin_role(current_user["id"])
        
        with performance_timer("admin_user_channels_fetch"):
            user_channels = await channel_service.get_user_channels_admin(
                user_id=user_id
            )
            
            if not user_channels:
                raise HTTPException(status_code=404, detail="User not found or has no channels")
            
            # Process the channels data
            channels_list = []
            active_count = 0
            
            for channel in user_channels.get("channels", []):
                channel_info = {
                    "id": channel["id"],
                    "name": channel["name"],
                    "username": channel.get("username"),
                    "is_active": channel.get("is_active", True),
                    "subscriber_count": channel.get("subscriber_count", 0),
                    "created_at": channel.get("created_at", datetime.now()).isoformat(),
                    "total_posts": channel.get("total_posts", 0),
                    "total_views": channel.get("total_views", 0)
                }
                channels_list.append(channel_info)
                
                if channel.get("is_active", True):
                    active_count += 1
            
            logger.info(f"Admin fetched user channels: user_id={user_id}, total={len(channels_list)}")
            
            return UserChannelInfo(
                user_id=user_id,
                username=user_channels.get("username"),
                total_channels=len(channels_list),
                active_channels=active_count,
                channels=channels_list,
                last_activity=user_channels.get("last_activity")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin user channels fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user channels for admin")