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


# Dependency function for channel service
def get_channel_service():
    """Get channel management service instance - using mock for now"""

    # Create a simple mock implementation to avoid complex dependencies
    class MockChannelService:
        async def get_user_channels(self, user_id: int):
            return {
                "user_id": user_id,
                "username": f"user_{user_id}",
                "channels": [
                    {"id": 1, "name": "Sample Channel", "telegram_id": 12345},
                    {"id": 2, "name": "Demo Channel", "telegram_id": 67890},
                ],
                "last_activity": "2024-01-01T12:00:00Z",
            }

    return MockChannelService()


router = APIRouter(
    prefix="/admin/users",
    tags=["Admin - User Management"],
    responses={404: {"description": "Not found"}},
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
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
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
            user_channels = await channel_service.get_user_channels(user_id=user_id)

            if not user_channels:
                raise HTTPException(status_code=404, detail="User not found or has no channels")

            # Process the channels data
            channels_list = []
            active_count = 0

            for channel in user_channels:
                channel_info = {
                    "id": channel.id,
                    "name": channel.name,
                    "username": getattr(channel, "username", None),
                    "is_active": channel.is_active,
                    "subscriber_count": channel.subscriber_count,
                    "created_at": (
                        channel.created_at.isoformat()
                        if channel.created_at
                        else datetime.now().isoformat()
                    ),
                    "total_posts": getattr(channel, "total_posts", 0),
                    "total_views": getattr(channel, "total_views", 0),
                }
                channels_list.append(channel_info)

                if channel.is_active:
                    active_count += 1

            logger.info(
                f"Admin fetched user channels: user_id={user_id}, total={len(channels_list)}"
            )

            return UserChannelInfo(
                user_id=user_id,
                username=f"User_{user_id}",  # We don't have username in channel service
                total_channels=len(channels_list),
                active_channels=active_count,
                channels=channels_list,
                last_activity=None,  # We don't have this info in channel service
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin user channels fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user channels for admin")
