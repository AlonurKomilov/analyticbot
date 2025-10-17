"""
Analytics Channels Router - Channel list endpoint for analytics dashboard
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from apps.api.services.telegram_validation_service import (
    ChannelValidationResult,
    TelegramValidationService,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics - Channels"],
    responses={404: {"description": "Not found"}},
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
async def get_analytics_channels():
    """
    ## 📺 Get User Channels for Analytics

    Retrieve all channels belonging to the current user for analytics dashboard.
    This endpoint is used by the frontend to populate channel selection and overview.

    **Authentication Required:**
    - Valid JWT token in Authorization header (handled by middleware)

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
        # Authentication is handled by middleware
        # Return empty list for now - user can add channels through the UI
        logger.info("Fetching analytics channels")

        # TODO: Implement actual database query
        # For now, return empty list to allow dashboard to load
        # Later this will query: SELECT * FROM channels WHERE user_id = current_user.id

        return []

    except Exception as e:
        logger.error(f"Failed to fetch analytics channels: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch channels: {str(e)}")


class ValidateChannelRequest(BaseModel):
    """Request model for channel validation"""

    username: str


async def get_telegram_validation_service():
    """Dependency to get telegram validation service"""
    from apps.api.di_analytics import get_telegram_validation_service as di_get_service

    return await di_get_service()


@router.post("/channels/validate", response_model=ChannelValidationResult)
async def validate_telegram_channel(
    request_data: ValidateChannelRequest,
    telegram_service: TelegramValidationService = Depends(get_telegram_validation_service),
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
