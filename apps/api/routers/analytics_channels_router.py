"""
Analytics Channels Router - Channel list endpoint for analytics dashboard
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics - Channels"],
    responses={404: {"description": "Not found"}}
)


class ChannelInfo(BaseModel):
    """Channel information for analytics dashboard"""
    id: int
    name: str
    username: str | None = None
    subscriber_count: int = 0
    is_active: bool = True
    created_at: datetime
    last_analytics_update: datetime | None = None


@router.get("/channels", response_model=list[ChannelInfo])
async def get_analytics_channels(request: Request):
    """
    ## 📺 Get User Channels for Analytics

    Retrieve all channels belonging to the current user for analytics dashboard.
    This endpoint is used by the frontend to populate channel selection and overview.

    **Authentication Required:**
    - Valid JWT token in Authorization header

    **Returns:**
    - List of user's channels with basic information
    - Empty list if user has no channels

    **Example Response:**
    ```json
    [
        {
            "id": 1,
            "name": "My Channel",
            "username": "@mychannel",
            "subscriber_count": 1000,
            "is_active": true,
            "created_at": "2025-01-01T00:00:00",
            "last_analytics_update": "2025-01-10T12:00:00"
        }
    ]
    ```
    """
    try:
        # Extract user ID from JWT token
        from apps.api.middleware.auth import get_current_user_id_from_request

        user_id = await get_current_user_id_from_request(request)
        logger.info(f"Fetching channels for user {user_id}")

        # TODO: Implement actual database query
        # For now, return empty list to allow dashboard to load
        # Later this will query: SELECT * FROM channels WHERE user_id = {user_id}

        return []

    except Exception as e:
        logger.error(f"Failed to fetch analytics channels: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch channels: {str(e)}"
        )
