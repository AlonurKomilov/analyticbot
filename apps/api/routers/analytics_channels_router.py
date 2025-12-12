"""
Analytics Channels Router - Channel list endpoint for analytics dashboard
"""

import logging
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from apps.api.middleware.auth import get_current_user  # Import auth dependency
from apps.api.services.telegram_validation_service import (
    ChannelValidationResult,
    TelegramValidationService,
)

logger = logging.getLogger(__name__)

# Simple in-memory cache with TTL per user (security fix)
_channel_cache: dict[int, tuple[list[dict], float]] = {}
_CACHE_TTL = 600  # 10 minutes


def get_cached_channels(user_id: int) -> list[dict] | None:
    """Get channels from cache if not expired"""
    if user_id in _channel_cache:
        channels, timestamp = _channel_cache[user_id]
        if time.time() - timestamp < _CACHE_TTL:
            logger.info(f"✅ Cache hit for user {user_id}")
            return channels
        else:
            del _channel_cache[user_id]  # Expired, remove from cache
    return None


def cache_channels(user_id: int, channels: list[dict]) -> None:
    """Store channels in cache with current timestamp"""
    _channel_cache[user_id] = (channels, time.time())
    logger.info(f"💾 Cached {len(channels)} channels for user {user_id}")


def invalidate_user_channel_cache(user_id: int) -> None:
    """Invalidate cache for a specific user (e.g., after channel add/delete)"""
    if user_id in _channel_cache:
        del _channel_cache[user_id]
        logger.info(f"🗑️ Cache invalidated for user {user_id}")


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
async def get_analytics_channels(
    request: Request,
    current_user: dict = Depends(get_current_user),  # Use proper dependency
):
    """
    ## 📺 Get User Channels for Analytics

    Retrieve all channels belonging to the current user for analytics dashboard.
    This endpoint is used by the frontend to populate channel selection and overview.

    **Performance:** Cached per-user for 10 minutes to prevent connection pool exhaustion

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

        # Check cache first (per-user cache for security)
        cached = get_cached_channels(user_id)
        if cached is not None:
            return cached

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

        # Cache the results (per-user for security)
        cache_channels(user_id, channels)

        return channels

    except Exception as e:
        logger.error(f"Failed to fetch analytics channels: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch channels: {str(e)}")


class ValidateChannelRequest(BaseModel):
    """Request model for channel validation"""

    username: str


async def get_telegram_validation_service() -> TelegramValidationService:
    """Dependency to get telegram validation service"""
    from apps.di.analytics_container import (
        get_telegram_validation_service as di_get_service,
    )

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
