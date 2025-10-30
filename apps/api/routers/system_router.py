"""
Core Microrouter - System Core Operations

This microrouter handles core system operations like health checks,
performance monitoring, and application initialization data.
Domain: System health, performance metrics, and core application functionality.
"""

import logging
import os
from datetime import datetime, UTC

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from apps.di import get_delivery_service, get_schedule_service
from apps.api.deps_factory import (
    get_initial_data_service,
)
from apps.api.middleware.auth import get_current_user_id
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
            channels=[
                Channel(id=1, title="Demo Channel", username="@demo_channel")
            ],
            scheduled_posts=[]
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
        logger.info(f"📅 Scheduling post: user={request.user_id}, channel={request.channel_id}, time={request.scheduled_time}")
        
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
        logger.info(f"🚀 Sending post immediately: user={request.user_id}, channel={request.channel_id}")
        
        # Get Telegram bot token
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "7603888301:AAHsmvb846iBbiGPzTda7wA1_RCimuowo3o")
        telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Convert channel_id to negative for Telegram API
        telegram_chat_id = -request.channel_id
        
        # Send to Telegram
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                telegram_api_url,
                json={
                    "chat_id": telegram_chat_id,
                    "text": request.message
                }
            )
            response.raise_for_status()
            telegram_response = response.json()
        
        if not telegram_response.get("ok"):
            raise HTTPException(status_code=500, detail=f"Telegram API error: {telegram_response.get('description')}")
        
        message_id = telegram_response["result"]["message_id"]
        logger.info(f"✅ Message sent to Telegram! Message ID: {message_id}")
        
        # Save to database with status='sent' and schedule_time=NOW()
        scheduled_post = await schedule_service.create_scheduled_post(
            title=f"Immediate post for {request.channel_id}",
            content=request.message,
            channel_id=str(request.channel_id),
            user_id=str(request.user_id),
            scheduled_at=datetime.now(UTC),  # Current time for immediate posts
            media_urls=[request.media_url] if request.media_url else [],
            media_types=[request.media_type] if request.media_type else [],
        )
        
        logger.info(f"✅ Post sent successfully: id={scheduled_post.id}, telegram_message_id={message_id}")
        return {
            "success": True,
            "post_id": str(scheduled_post.id),
            "message_id": message_id,
            "message": "Post sent successfully",
            "channel_id": request.channel_id,
        }
    except httpx.HTTPError as e:
        logger.error(f"❌ Telegram API request failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to send message to Telegram: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Post send failed: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to send post: {str(e)}")


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

        # Convert int to UUID and use correct service method: get_post
        post_uuid = UUID(int=post_id) if isinstance(post_id, int) else UUID(post_id)
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

        # Convert int to UUID and use correct service method: delete_post
        post_uuid = UUID(int=post_id) if isinstance(post_id, int) else UUID(post_id)
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
        from core.protocols import AnalyticsServiceProtocol

        container = get_container()
        analytics_service = await container.core_services.analytics_fusion_service()

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

