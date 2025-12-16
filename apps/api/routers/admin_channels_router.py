"""
Admin Channels Router - Channel Administration

Handles administrative channel operations including listing, management, suspension, and deletion.
Clean architecture: Single responsibility for channel administration.

Domain: Admin channel management operations
Path: /admin/channels/*
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from apps.api.middleware.auth import (
    get_current_user,
    require_admin_user,
)
from apps.api.services.channel_management_service import ChannelManagementService
from apps.di.analytics_container import (
    get_channel_management_service,
    get_database_pool,
)
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
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            channels = await conn.fetch(
                """
                SELECT 
                    c.id,
                    c.title as name,
                    c.username,
                    c.user_id as owner_id,
                    u.username as owner_username,
                    c.subscriber_count,
                    c.is_active,
                    c.created_at,
                    c.updated_at as last_activity,
                    COALESCE(post_stats.total_posts, 0) as total_posts,
                    COALESCE(post_stats.total_views, 0) as total_views
                FROM channels c
                LEFT JOIN users u ON c.user_id = u.id
                LEFT JOIN (
                    SELECT 
                        channel_id,
                        COUNT(*) as total_posts,
                        COALESCE(SUM(views), 0) as total_views
                    FROM scheduled_posts
                    GROUP BY channel_id
                ) post_stats ON c.id = post_stats.channel_id
                ORDER BY c.created_at DESC
                LIMIT $1 OFFSET $2
            """,
                limit,
                offset,
            )

            return [
                AdminChannelInfo(
                    id=channel["id"],
                    name=channel["name"] or "Unnamed Channel",
                    username=channel["username"],
                    owner_id=channel["owner_id"] or 0,
                    owner_username=channel["owner_username"],
                    subscriber_count=channel["subscriber_count"] or 0,
                    is_active=(channel["is_active"] if channel["is_active"] is not None else True),
                    created_at=channel["created_at"],
                    last_activity=channel["last_activity"],
                    total_posts=channel["total_posts"],
                    total_views=channel["total_views"],
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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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
        await require_admin_user(current_user)

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
