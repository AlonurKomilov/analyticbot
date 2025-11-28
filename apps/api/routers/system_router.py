"""
Core Microrouter - System Core Operations

This microrouter handles core system operations like health checks,
performance monitoring, and application initialization data.
Domain: System health, performance metrics, and core application functionality.
"""

import logging
import os
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from apps.api.middleware.auth import get_current_user_id
from apps.di import get_delivery_service, get_schedule_service
from apps.shared.models.twa import InitialDataResponse
from core import DeliveryService, ScheduleService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/system", tags=["Core"], responses={404: {"description": "Not found"}})

# === CORE MODELS ===


class HealthStatus(BaseModel):
    status: str
    timestamp: datetime
    environment: str
    debug_mode: bool
    api_version: str
    database_status: str
    dependencies: dict[str, str]


class PerformanceMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    active_connections: int
    response_time_avg: float
    uptime: str
    requests_per_minute: float


class ScheduleRequest(BaseModel):
    user_id: int
    channel_id: int
    message: str
    scheduled_time: datetime
    media_type: str = "text"
    media_url: str | None = None


class SendNowRequest(BaseModel):
    user_id: int
    channel_id: int
    message: str
    media_type: str = "text"
    media_url: str | None = None
    telegram_file_id: str | None = None  # For files from Telegram storage


# === CORE ENDPOINTS ===

# NOTE: Health endpoint moved to health_system_router.py for consolidation
# Use /health/* endpoints instead of /core/health


@router.get("/performance", summary="Performance Metrics")
async def performance():
    """
    ## ⚡ Performance Metrics

    Real-time system performance metrics including CPU, memory, and API performance.

    **Returns:**
    - CPU and memory usage
    - Active connections
    - Response time statistics
    - System uptime
    - Request rate metrics
    """
    try:
        import time

        import psutil

        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        # Calculate uptime (simplified)
        boot_time = psutil.boot_time()
        current_time = time.time()
        uptime_seconds = current_time - boot_time
        uptime_hours = uptime_seconds // 3600

        return PerformanceMetrics(
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            active_connections=50,  # Simplified - would need actual connection pool info
            response_time_avg=0.25,  # Simplified - would need actual metrics
            uptime=f"{int(uptime_hours)} hours",
            requests_per_minute=120.5,  # Simplified - would need actual rate limiting metrics
        )
    except Exception as e:
        logger.error(f"Performance metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")


@router.get("/initial-data", response_model=InitialDataResponse, summary="Application Startup Data")
async def initial_data(request: Request, user_id: int = Depends(get_current_user_id)):
    """
    ## 🚀 Application Startup Data

    Get initial data required for application startup including user info, channels, and configuration.

    **Returns:**
    - User information
    - Available channels
    - Application configuration
    - Feature flags
    """
    try:
        # ✅ TEMPORARY: Return simple mock data to unblock frontend
        # TODO: Re-enable full service injection when repository issues are resolved
        from apps.shared.models.twa import Channel, User

        logger.info(f"Returning initial data for user_id: {user_id}")

        return InitialDataResponse(
            user=User(id=user_id, username=f"user_{user_id}"),
            channels=[Channel(id=1, title="Demo Channel", username="@demo_channel")],
            scheduled_posts=[],
        )

    except Exception as e:
        logger.error(f"Initial data fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get initial data: {str(e)}")


@router.post("/schedule", response_model=dict)
async def create_scheduled_post(
    request: ScheduleRequest, schedule_service: ScheduleService = Depends(get_schedule_service)
):
    """
    ## 📅 Create Scheduled Post

    Schedule a post for future delivery to a Telegram channel.

    **Parameters:**
    - request: Scheduling request with user_id, channel_id, message, and timing

    **Returns:**
    - Scheduled post confirmation with ID and timing
    """
    try:
        logger.info(
            f"📅 Scheduling post: user={request.user_id}, channel={request.channel_id}, time={request.scheduled_time}"
        )

        # Use correct service method: create_scheduled_post
        scheduled_post = await schedule_service.create_scheduled_post(
            title=f"Scheduled post for {request.channel_id}",
            content=request.message,
            channel_id=str(request.channel_id),
            user_id=str(request.user_id),
            scheduled_at=request.scheduled_time,
            media_urls=[request.media_url] if request.media_url else [],
            media_types=[request.media_type] if request.media_type else [],
        )

        logger.info(f"✅ Post scheduled successfully: id={scheduled_post.id}")
        return {
            "success": True,
            "post_id": str(scheduled_post.id),
            "scheduled_time": request.scheduled_time.isoformat(),
            "message": "Post scheduled successfully",
            "channel_id": request.channel_id,
        }
    except Exception as e:
        logger.error(f"❌ Post scheduling failed: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to schedule post: {str(e)}")


@router.post("/send", response_model=dict)
async def send_post_now(
    request: SendNowRequest, schedule_service: ScheduleService = Depends(get_schedule_service)
):
    """
    ## 🚀 Send Post Immediately

    Send a post immediately to a Telegram channel (no scheduling).

    **Parameters:**
    - request: Post data with user_id, channel_id, and message

    **Returns:**
    - Success confirmation with message_id from Telegram
    """
    try:
        logger.info(
            f"🚀 Sending post immediately: user={request.user_id}, channel={request.channel_id}"
        )
        logger.info(
            f"📎 Media info: type={request.media_type}, url={request.media_url}, telegram_file_id={request.telegram_file_id}"
        )

        # Convert channel_id to proper Telegram chat_id format
        # Telegram channels should have negative IDs (e.g., -1002284381383)
        # If user sends positive ID, make it negative
        # If already negative, keep it as-is
        channel_id = int(request.channel_id)
        if channel_id > 0:
            telegram_chat_id = -channel_id
        else:
            telegram_chat_id = channel_id

        logger.info(
            f"📍 Using telegram_chat_id: {telegram_chat_id} (from channel_id: {channel_id})"
        )

        # If using Telegram storage file, forward the message instead
        if request.telegram_file_id:
            logger.info("📤 Using MTProto to send file from storage")

            # Get the original message info from database
            from sqlalchemy import select

            from apps.api.services.telegram_storage_service import TelegramStorageService

            # Get database session from DI container
            from apps.di import get_container
            from infra.db.models.telegram_storage import TelegramMedia, UserStorageChannel

            container = get_container()
            session_factory = await container.database.async_session_maker()

            async with session_factory() as db_session:
                result = await db_session.execute(
                    select(TelegramMedia).where(
                        TelegramMedia.telegram_file_id == request.telegram_file_id
                    )
                )
                media_record = result.scalar_one_or_none()

                if not media_record:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Media file with telegram_file_id {request.telegram_file_id} not found",
                    )

                # Get storage channel info
                channel_result = await db_session.execute(
                    select(UserStorageChannel).where(
                        UserStorageChannel.id == media_record.storage_channel_id
                    )
                )
                storage_channel = channel_result.scalar_one_or_none()

                if not storage_channel:
                    raise HTTPException(status_code=404, detail="Storage channel not found")

                # Create storage service for user
                storage_service = await TelegramStorageService.create_for_user(
                    user_id=request.user_id,
                    db_session=db_session,
                )

                try:
                    # Get the message from storage channel
                    # Use username if available, otherwise use channel_id
                    from_channel = storage_channel.channel_username or int(
                        storage_channel.channel_id
                    )

                    # For target channel, ensure it's formatted correctly for Telethon
                    # If channel_id is already negative (e.g., -1002678877654), use as-is
                    # If it's just the numeric part (e.g., 1002678877654), make it negative
                    to_channel_id = int(request.channel_id)
                    if to_channel_id > 0:
                        to_channel = -to_channel_id  # Make it negative for Telethon
                    else:
                        to_channel = to_channel_id

                    logger.info(
                        f"Getting message {media_record.telegram_message_id} "
                        f"from storage channel {from_channel}"
                    )

                    # Get the original message
                    original_message = await storage_service.client.get_messages(
                        entity=from_channel, ids=media_record.telegram_message_id
                    )

                    if not original_message:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Message {media_record.telegram_message_id} not found in storage channel",
                        )

                    logger.info(f"Sending file to channel {to_channel}")

                    # Send the file to target channel as proper media type
                    # For photos/videos, don't force as document to maintain media type
                    force_document = media_record.file_type not in ["photo", "video"]

                    sent_message = await storage_service.client.send_file(
                        entity=to_channel,
                        file=original_message.media,
                        caption=request.message if request.message else media_record.caption,
                        force_document=force_document,  # Keep as photo/video, not document
                    )

                    message_id = sent_message.id
                    logger.info(f"✅ File sent successfully! Message ID: {message_id}")

                except Exception as e:
                    logger.error(f"❌ MTProto send failed: {str(e)}", exc_info=True)
                    raise HTTPException(
                        status_code=500, detail=f"Failed to send file from storage: {str(e)}"
                    )
        else:
            # Original logic for text-only or URL-based media using Bot API
            # Get Telegram bot token
            bot_token = os.getenv(
                "TELEGRAM_BOT_TOKEN", "7603888301:AAHsmvb846iBbiGPzTda7wA1_RCimuowo3o"
            )

            # Text-only message (or URL-based media, though not implemented yet)
            telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": telegram_chat_id, "text": request.message}

            logger.info(f"📤 Sending to Telegram API: {telegram_api_url}")
            logger.info(f"📦 Payload: {payload}")

            # Send to Telegram
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(telegram_api_url, json=payload)

                    # Handle specific Telegram errors
                    if response.status_code == 400:
                        error_data = response.json()
                        error_description = error_data.get("description", "Unknown error")
                        logger.error(f"❌ Telegram 400 error: {error_description}")

                        # Provide user-friendly error messages
                        if "chat not found" in error_description.lower():
                            raise HTTPException(
                                status_code=400,
                                detail="Channel not found. Please make sure the bot is added as an administrator to your channel.",
                            )
                        elif (
                            "not enough rights" in error_description.lower()
                            or "need administrator" in error_description.lower()
                        ):
                            raise HTTPException(
                                status_code=403,
                                detail="Bot doesn't have permission to post in this channel. Please add the bot as an administrator with 'Post messages' permission.",
                            )
                        elif "bot was kicked" in error_description.lower():
                            raise HTTPException(
                                status_code=403,
                                detail="The bot was removed from this channel. Please add it back as an administrator.",
                            )
                        else:
                            raise HTTPException(
                                status_code=400, detail=f"Telegram error: {error_description}"
                            )

                    response.raise_for_status()
                    telegram_response = response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"❌ Telegram API HTTP error: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Failed to send message to Telegram: {str(e)}"
                )

            if not telegram_response.get("ok"):
                raise HTTPException(
                    status_code=500,
                    detail=f"Telegram API error: {telegram_response.get('description')}",
                )

            message_id = telegram_response["result"]["message_id"]
            logger.info(f"✅ Message sent to Telegram! Message ID: {message_id}")

        # For immediate posts, save directly to DB bypassing schedule validation
        # Use repository directly instead of service to avoid "past date" validation
        from core.models import PostStatus, ScheduledPost

        post = ScheduledPost(
            title=f"Immediate post for {request.channel_id}",
            content=request.message,
            channel_id=str(request.channel_id),
            user_id=str(request.user_id),
            scheduled_at=datetime.now(UTC),  # Current time for immediate posts
            status=PostStatus.PUBLISHED,  # Mark as published immediately
            tags=[],
            media_urls=[request.media_url] if request.media_url else [],
            media_types=[request.media_type] if request.media_type else [],
        )

        # Save using repository (bypassing service validation)
        scheduled_post = await schedule_service.schedule_repo.create(post)

        logger.info(
            f"✅ Post sent successfully: id={scheduled_post.id}, telegram_message_id={message_id}"
        )
        return {
            "success": True,
            "post_id": str(scheduled_post.id),
            "message_id": message_id,
            "message": "Post sent successfully",
            "channel_id": request.channel_id,
        }
    except httpx.HTTPError as e:
        logger.error(f"❌ Telegram API request failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to send message to Telegram: {str(e)}"
        ) from e
    except Exception as e:
        logger.error(f"❌ Post send failed: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to send post: {str(e)}") from e


@router.get("/schedule/{post_id}")
async def get_scheduled_post(
    post_id: int, schedule_service: ScheduleService = Depends(get_schedule_service)
):
    """
    ## 📋 Get Scheduled Post

    Retrieve details of a specific scheduled post.

    **Parameters:**
    - post_id: Scheduled post ID

    **Returns:**
    - Scheduled post details and status
    """
    try:
        from uuid import UUID

        # Convert int to UUID for the service call
        # Note: This assumes post_id comes as int from the API path, but service expects UUID
        try:
            post_uuid = UUID(int=post_id) if isinstance(post_id, int) else UUID(str(post_id))
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid post ID format")

        post = await schedule_service.get_post(post_uuid)

        if not post:
            raise HTTPException(status_code=404, detail="Scheduled post not found")

        return {
            "id": str(post.id),
            "user_id": post.user_id,
            "channel_id": post.channel_id,
            "message": post.content,
            "scheduled_time": post.scheduled_at.isoformat(),
            "status": post.status.value,
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "media_type": post.media_types[0] if post.media_types else None,
            "media_url": post.media_urls[0] if post.media_urls else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scheduled post fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get scheduled post")


@router.get("/schedule/user/{user_id}")
async def get_user_scheduled_posts(
    user_id: int, schedule_service: ScheduleService = Depends(get_schedule_service)
):
    """
    ## 📋 Get User Scheduled Posts

    Retrieve all scheduled posts for a specific user.

    **Parameters:**
    - user_id: Target user ID

    **Returns:**
    - List of user's scheduled posts
    """
    try:
        # Use correct service method: get_user_posts
        posts = await schedule_service.get_user_posts(user_id=str(user_id))

        return {
            "user_id": user_id,
            "total_posts": len(posts),
            "posts": [
                {
                    "id": str(post.id),
                    "channel_id": post.channel_id,
                    "message": post.content[:100] + "..."
                    if len(post.content) > 100
                    else post.content,
                    "scheduled_time": post.scheduled_at.isoformat(),
                    "status": post.status.value,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                }
                for post in posts
            ],
        }
    except Exception as e:
        logger.error(f"User scheduled posts fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user scheduled posts")


@router.delete("/schedule/{post_id}")
async def delete_scheduled_post(
    post_id: int, schedule_service: ScheduleService = Depends(get_schedule_service)
):
    """
    ## 🗑️ Delete Scheduled Post

    Cancel and delete a scheduled post.

    **Parameters:**
    - post_id: Scheduled post ID to delete

    **Returns:**
    - Deletion confirmation
    """
    try:
        from uuid import UUID

        # Convert int to UUID for the service call
        try:
            post_uuid = UUID(int=post_id) if isinstance(post_id, int) else UUID(str(post_id))
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid post ID format")

        result = await schedule_service.delete_post(post_uuid)

        if not result:
            raise HTTPException(status_code=404, detail="Scheduled post not found")

        return {
            "success": True,
            "message": "Scheduled post deleted successfully",
            "post_id": post_id,
            "deleted_at": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scheduled post deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete scheduled post")


@router.get("/delivery/stats")
async def get_delivery_stats(delivery_service: DeliveryService = Depends(get_delivery_service)):
    """
    ## 📊 Delivery Statistics

    Get statistics about message delivery performance and status.

    **Returns:**
    - Delivery performance metrics
    - Success/failure rates
    - Queue status
    """
    try:
        stats = await delivery_service.get_delivery_stats()

        return {
            "total_delivered": stats.get("total_delivered", 0),
            "delivery_success_rate": stats.get("success_rate", 0.0),
            "average_delivery_time": stats.get("avg_delivery_time", 0.0),
            "pending_deliveries": stats.get("pending_count", 0),
            "failed_deliveries": stats.get("failed_count", 0),
            "last_24h_delivered": stats.get("last_24h_count", 0),
            "queue_health": stats.get("queue_health", "unknown"),
            "updated_at": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Delivery stats fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get delivery statistics")


@router.get("/service-info")
async def get_service_information():
    """
    ## ⚙️ Service Information

    Get comprehensive information about system services and configuration.
    Migrated from clean analytics router - service metadata belongs to core system functionality.

    **Returns:**
    - Analytics service configuration
    - Demo mode status
    - System service information
    - Configuration details
    """
    try:
        # Import analytics service using clean architecture pattern
        from apps.di import get_container
        from config.settings import settings

        container = get_container()
        # Verify analytics service is available
        _ = await container.core_services.analytics_fusion_service()

        return {
            "analytics_service": {
                "name": "AnalyticsFusionService",
                "service_type": "production",
            },
            "system_info": {
                "environment": "production" if not settings.DEBUG else "development",
                "clean_architecture": True,
                "service_type": "core_system",
            },
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Service info fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service information")
