"""
Analytics Channels Router - Channel list endpoint for analytics dashboard
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from apps.api.middleware.auth import get_current_user  # Import auth dependency
from apps.api.services.telegram_validation_service import (
    ChannelValidationResult,
    TelegramValidationService,
)

# ✅ PHASE 2: Redis caching for performance optimization
from core.common.cache_decorator import cache_endpoint

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",  # Fixed: No prefix here since main.py adds /analytics/channels
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


@router.get(
    "", response_model=list[ChannelInfo]
)  # Fixed: Empty path since main.py adds /analytics/channels
@cache_endpoint(prefix="analytics:channels", ttl=600)  # Cache for 10 minutes
async def get_analytics_channels(
    request: Request,
    current_user: dict = Depends(get_current_user),  # Use proper dependency
):
    """
    ## 📺 Get User Channels for Analytics (CACHED)

    Retrieve all channels belonging to the current user for analytics dashboard.
    This endpoint is used by the frontend to populate channel selection and overview.

    **Performance:** Cached for 10 minutes (600 seconds) per user

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
        # Use current_user from dependency injection (proper auth)
        user_id = current_user["id"]  # Extract ID from validated user dict

        logger.info(f"🔍 Fetching analytics channels for user_id={user_id}")
        print(f"🔍 DEBUG: Fetching analytics channels for user_id={user_id}")  # Debug print

        # Get database pool from DI container
        from apps.di import get_container

        container = get_container()
        pool = await container.database.asyncpg_pool()

        # Query user's channels from database
        query = """
            SELECT 
                c.id,
                c.title as name,
                c.username,
                c.created_at,
                COUNT(sp.id) as total_posts
            FROM channels c
            LEFT JOIN scheduled_posts sp ON c.id = sp.channel_id
            WHERE c.user_id = $1
            GROUP BY c.id, c.title, c.username, c.created_at
            ORDER BY c.created_at DESC
        """

        async with pool.acquire() as conn:
            rows = await conn.fetch(query, user_id)

        # Convert to response model
        channels = [
            ChannelInfo(
                id=row["id"],
                name=row["name"] or f"Channel {row['id']}",
                username=row["username"],
                subscriber_count=0,  # TODO: Fetch from Telegram API periodically
                is_active=True,
                created_at=row["created_at"],
                last_analytics_update=None,  # TODO: Track analytics update time
            ).model_dump()  # ✅ Convert Pydantic model to dict for proper serialization
            for row in rows
        ]

        logger.info(f"Found {len(channels)} channels for user {user_id}")
        return channels

    except Exception as e:
        logger.error(f"Failed to fetch analytics channels: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch channels: {str(e)}")


class ValidateChannelRequest(BaseModel):
    """Request model for channel validation"""

    username: str


async def get_telegram_validation_service() -> TelegramValidationService:
    """Dependency to get telegram validation service"""
    from apps.api.di_analytics import get_telegram_validation_service as di_get_service

    return await di_get_service()


@router.post(
    "/validate", response_model=ChannelValidationResult
)  # Fixed: /analytics/channels/validate
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
