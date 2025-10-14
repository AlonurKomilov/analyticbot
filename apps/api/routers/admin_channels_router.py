"""
Admin Channels Router - Channel Administration

Handles administrative channel operations including listing, management, suspension, and deletion.
Clean architecture: Single responsibility for channel administration.

Domain: Admin channel management operations
Path: /admin/channels/*
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from apps.api.di_analytics import get_channel_management_service
from apps.api.middleware.auth import (
    get_current_user,
    require_admin_role,
)
from apps.api.services.channel_management_service import ChannelManagementService

# ✅ CLEAN ARCHITECTURE: Use apps performance abstraction instead of direct infra import
from apps.shared.performance import performance_timer

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/admin/channels",
    tags=["Admin - Channel Management"],
    responses={404: {"description": "Not found"}},
)

# === ADMIN CHANNEL MODELS ===


class AdminChannelInfo(BaseModel):
    id: int
    name: str
    username: str | None = None
    owner_id: int
    owner_username: str | None = None
    subscriber_count: int = 0
    is_active: bool = True
    created_at: datetime
    last_activity: datetime | None = None
    total_posts: int = 0
    total_views: int = 0


# === ADMIN CHANNEL ENDPOINTS ===


@router.get("", response_model=list[AdminChannelInfo])
async def get_all_channels(
    request: Request,
    limit: int = Query(
        default=100, ge=1, le=1000, description="Maximum number of channels to return"
    ),
    offset: int = Query(default=0, ge=0, description="Number of channels to skip for pagination"),
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 👑 Get All Channels (Admin)

    Retrieve all channels in the system with administrative details.

    **Admin Only**: Requires admin role

    **Parameters:**
    - limit: Maximum number of channels to return (1-1000)
    - offset: Number of channels to skip

    **Returns:**
    - List of all channels with administrative information
    """
    try:
        await require_admin_role(current_user["id"])

        with performance_timer("admin_all_channels_fetch"):
            channels = await channel_service.get_all_channels_admin(limit=limit, skip=offset)

            return [
                AdminChannelInfo(
                    id=channel.id,
                    name=channel.name,
                    username=getattr(channel, "username", None),
                    owner_id=getattr(channel, "user_id", 0),
                    owner_username=getattr(channel, "owner_username", "Unknown"),
                    subscriber_count=channel.subscriber_count,
                    is_active=channel.is_active,
                    created_at=channel.created_at,
                    last_activity=getattr(channel, "last_activity", None),
                    total_posts=getattr(channel, "total_posts", 0),
                    total_views=getattr(channel, "total_views", 0),
                )
                for channel in channels
            ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin channels fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch channels for admin")


@router.delete("/{channel_id}")
async def delete_channel_admin(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 🗑️ Delete Channel (Admin)

    Permanently delete a channel and all associated data.

    **Admin Only**: Requires admin role
    **⚠️ WARNING**: This action is permanent and cannot be undone.

    **Parameters:**
    - channel_id: ID of the channel to delete

    **Returns:**
    - Deletion confirmation
    """
    try:
        await require_admin_role(current_user["id"])

        with performance_timer("admin_channel_deletion"):
            result = await channel_service.admin_delete_channel(channel_id)

            if not result:
                raise HTTPException(status_code=404, detail="Channel not found")

            logger.warning(
                f"ADMIN DELETION: Channel {channel_id} deleted by admin {current_user['id']}"
            )
            return {
                "message": "Channel permanently deleted by admin",
                "channel_id": channel_id,
                "deleted_by": current_user["id"],
                "deleted_at": datetime.now().isoformat(),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin channel deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete channel")


@router.post("/{channel_id}/suspend")
async def suspend_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## ⏸️ Suspend Channel (Admin)

    Temporarily suspend a channel to prevent further analytics tracking.

    **Admin Only**: Requires admin role

    **Parameters:**
    - channel_id: ID of the channel to suspend

    **Returns:**
    - Suspension confirmation
    """
    try:
        await require_admin_role(current_user["id"])

        with performance_timer("admin_channel_suspension"):
            result = await channel_service.suspend_channel(channel_id)

            if not result:
                raise HTTPException(status_code=404, detail="Channel not found")

            logger.info(f"Channel suspended by admin: {channel_id} by {current_user['id']}")
            return {
                "message": "Channel suspended successfully",
                "channel_id": channel_id,
                "suspended_by": current_user["id"],
                "suspended_at": datetime.now().isoformat(),
                "status": "suspended",
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel suspension failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to suspend channel")


@router.post("/{channel_id}/unsuspend")
async def unsuspend_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## ▶️ Unsuspend Channel (Admin)

    Reactivate a suspended channel to resume analytics tracking.

    **Admin Only**: Requires admin role

    **Parameters:**
    - channel_id: ID of the channel to unsuspend

    **Returns:**
    - Reactivation confirmation
    """
    try:
        await require_admin_role(current_user["id"])

        with performance_timer("admin_channel_unsuspension"):
            result = await channel_service.unsuspend_channel(channel_id)

            if not result:
                raise HTTPException(status_code=404, detail="Channel not found")

            logger.info(f"Channel unsuspended by admin: {channel_id} by {current_user['id']}")
            return {
                "message": "Channel unsuspended successfully",
                "channel_id": channel_id,
                "unsuspended_by": current_user["id"],
                "unsuspended_at": datetime.now().isoformat(),
                "status": "active",
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel unsuspension failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to unsuspend channel")
