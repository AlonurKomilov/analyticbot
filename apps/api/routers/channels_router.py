"""
Channels Microrouter - Pure Channel Management

This microrouter handles ONLY channel management operations (CRUD).
Domain: Channel creation, reading, updating, deletion, and basic channel operations.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from apps.api.di_analytics import get_channel_management_service
from apps.api.middleware.auth import (
    get_current_user,
    require_channel_access,
)
from apps.api.services.channel_management_service import (
    ChannelCreate,
    ChannelManagementService,
    ChannelResponse,
)
from apps.api.services.telegram_validation_service import (
    ChannelValidationResult,
    TelegramValidationService,
)
from apps.shared.performance import performance_timer

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


class ValidateChannelRequest(BaseModel):
    """Request model for channel validation"""

    username: str


# === CHANNEL ENDPOINTS ===


async def get_telegram_validation_service_dep():
    """Dependency to get telegram validation service"""
    from apps.api.di_analytics import get_telegram_validation_service as di_get_service

    return await di_get_service()


@router.post("/validate", response_model=ChannelValidationResult)
async def validate_telegram_channel(
    request_data: ValidateChannelRequest,
    telegram_service: TelegramValidationService = Depends(get_telegram_validation_service_dep),
):
    """
    ## ✅ Validate Telegram Channel

    Validate a Telegram channel by username and fetch metadata before creation.
    This endpoint checks if the channel exists and returns its information.

    **Authentication Required:**
    - Valid JWT token in Authorization header

    **Request Body:**
    ```json
    {
        "username": "@channelname"
    }
    ```

    **Returns:**
    - Channel validation result with metadata (telegram_id, subscriber_count, etc.)
    - Error message if validation fails

    **Example Response:**
    ```json
    {
        "is_valid": true,
        "telegram_id": 1234567890,
        "username": "channelname",
        "title": "My Channel",
        "subscriber_count": 1000,
        "description": "Channel description",
        "is_verified": false,
        "is_scam": false
    }
    ```
    """
    try:
        logger.info(f"Validating channel: {request_data.username}")
        result = await telegram_service.validate_channel_by_username(request_data.username)
        return result

    except Exception as e:
        logger.error(f"Failed to validate channel: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("", response_model=list[ChannelListResponse])
async def get_user_channels(
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 📺 Get User Channels

    Retrieve all channels accessible by the current user.

    **Returns:**
    - List of user's channels with basic information
    """
    try:
        logger.info(f"Fetching channels for user {current_user.get('id')}")
        with performance_timer("user_channels_fetch"):
            channels = await channel_service.get_user_channels(user_id=current_user["id"])
            logger.info(f"Successfully fetched {len(channels)} channels")

            return [
                ChannelListResponse(
                    id=channel.id,
                    name=channel.name,
                    username=getattr(channel, "username", None),
                    subscriber_count=channel.subscriber_count,
                    is_active=channel.is_active,
                    created_at=channel.created_at,
                    last_updated=getattr(channel, "updated_at", channel.created_at),
                )
                for channel in channels
            ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"User channels fetch failed for user {current_user.get('id')}: {e}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Failed to fetch user channels: {str(e)}")


@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: ChannelCreate,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
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
            channel_data.user_id = current_user["id"]
            channel = await channel_service.create_channel(channel_data)

            logger.info(f"Channel created successfully: {channel.id} by user {current_user['id']}")
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
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
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
            channel = await channel_service.get_channel(channel_id)

            if not channel:
                raise HTTPException(status_code=404, detail="Channel not found")

            return channel

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
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
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
                channel_id=channel_id, user_id=current_user["id"], update_data=update_dict
            )

            logger.info(f"Channel updated successfully: {channel_id} by user {current_user['id']}")
            return channel

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel update failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to update channel")


@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
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
        # Verify user has access to this channel
        await require_channel_access(channel_id, current_user["id"])

        with performance_timer("channel_deletion"):
            result = await channel_service.delete_channel(channel_id)

            if not result:
                raise HTTPException(status_code=404, detail="Channel not found or already deleted")

            logger.info(f"Channel deleted successfully: {channel_id} by user {current_user['id']}")
            return {
                "message": "Channel deleted successfully",
                "channel_id": channel_id,
                "deleted_at": datetime.now().isoformat(),
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
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
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
                channel_id=channel_id, user_id=current_user["id"], update_data={"is_active": True}
            )

            logger.info(f"Channel activated: {channel_id} by user {current_user['id']}")
            return {
                "message": "Channel activated successfully",
                "channel_id": channel_id,
                "is_active": True,
                "activated_at": datetime.now().isoformat(),
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
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
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
                channel_id=channel_id, user_id=current_user["id"], update_data={"is_active": False}
            )

            logger.info(f"Channel deactivated: {channel_id} by user {current_user['id']}")
            return {
                "message": "Channel deactivated successfully",
                "channel_id": channel_id,
                "is_active": False,
                "deactivated_at": datetime.now().isoformat(),
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
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
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
            status_info = await channel_service.get_channel_status(channel_id)

            return {
                "channel_id": channel_id,
                "is_active": status_info.get("is_active", False),
                "last_update": status_info.get("last_update"),
                "subscriber_count": status_info.get("subscriber_count", 0),
                "total_posts": status_info.get("total_posts", 0),
                "analytics_enabled": status_info.get("analytics_enabled", False),
                "connection_status": status_info.get("connection_status", "unknown"),
                "last_sync": status_info.get("last_sync"),
                "checked_at": datetime.now().isoformat(),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel status fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch channel status")


@router.get("/statistics/overview")
async def get_channels_statistics_overview(
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 📊 Get Channels Statistics Overview

    Get aggregate statistics for all user's channels plus individual channel stats.

    **Returns:**
    - Aggregate statistics (total subscribers, posts, views across all channels)
    - Per-channel statistics with detailed metrics
    """
    try:
        user_id = current_user["id"]

        with performance_timer("channels_statistics_overview"):
            # Get user's channels
            channels = await channel_service.get_user_channels(user_id=user_id)

            if not channels:
                return {
                    "aggregate": {
                        "total_channels": 0,
                        "total_subscribers": 0,
                        "total_posts": 0,
                        "total_views": 0,
                        "active_channels": 0,
                    },
                    "channels": [],
                }

            # Get database pool for stats queries
            from apps.di import get_container

            container = get_container()
            pool = await container.database.asyncpg_pool()

            channel_stats_list = []
            total_subscribers = 0
            total_posts = 0
            total_views = 0
            active_channels = 0

            async with pool.acquire() as conn:
                for channel in channels:
                    # Get post count and views for this channel
                    stats = await conn.fetchrow(
                        """
                        SELECT
                            COUNT(DISTINCT p.msg_id) as post_count,
                            COALESCE(SUM(latest_metrics.views), 0)::bigint as total_views,
                            MAX(p.date) as latest_post_date
                        FROM posts p
                        LEFT JOIN LATERAL (
                            SELECT views
                            FROM post_metrics
                            WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                            ORDER BY snapshot_time DESC
                            LIMIT 1
                        ) latest_metrics ON true
                        WHERE p.channel_id = $1 AND p.is_deleted = FALSE
                        """,
                        channel.id,
                    )

                    post_count = stats["post_count"] or 0
                    views_count = stats["total_views"] or 0
                    latest_post = stats["latest_post_date"]

                    # Count as active if has posts
                    if channel.is_active and post_count > 0:
                        active_channels += 1

                    # Aggregate totals
                    total_subscribers += channel.subscriber_count
                    total_posts += post_count
                    total_views += views_count

                    # Add to per-channel stats
                    channel_stats_list.append(
                        {
                            "id": channel.id,
                            "name": channel.name,
                            "username": getattr(channel, "username", None),
                            "subscriber_count": channel.subscriber_count,
                            "post_count": post_count,
                            "total_views": views_count,
                            "avg_views_per_post": round(views_count / post_count)
                            if post_count > 0
                            else 0,
                            "latest_post_date": latest_post.isoformat() if latest_post else None,
                            "is_active": channel.is_active,
                            "created_at": channel.created_at.isoformat(),
                        }
                    )

            return {
                "aggregate": {
                    "total_channels": len(channels),
                    "total_subscribers": total_subscribers,
                    "total_posts": total_posts,
                    "total_views": total_views,
                    "active_channels": active_channels,
                    "avg_views_per_post": round(total_views / total_posts)
                    if total_posts > 0
                    else 0,
                },
                "channels": sorted(
                    channel_stats_list, key=lambda x: x["total_views"], reverse=True
                ),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel statistics overview failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch channel statistics")


# End of channels router - analytics endpoints moved to analytics_insights_router.py
