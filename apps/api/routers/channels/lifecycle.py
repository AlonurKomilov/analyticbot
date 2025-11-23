"""
Channel lifecycle management.

Handles: Activate channel, deactivate channel.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

logger = logging.getLogger(__name__)

from apps.api.middleware.auth import get_current_user, require_channel_access
from apps.api.routers.channels.deps import get_channel_management_service
from apps.api.services.channel_management_service import ChannelManagementService
from apps.shared.performance import performance_timer

router = APIRouter()


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
            await channel_service.update_channel(
                channel_id=channel_id, user_id=current_user["id"], update_data={"is_active": True}
            )

        logger.info(f"Channel activated successfully: {channel_id} by user {current_user['id']}")
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
            await channel_service.update_channel(
                channel_id=channel_id, user_id=current_user["id"], update_data={"is_active": False}
            )

        logger.info(f"Channel deactivated successfully: {channel_id} by user {current_user['id']}")
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
