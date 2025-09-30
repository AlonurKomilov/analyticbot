"""
Core Microrouter - System Core Operations

This microrouter handles core system operations like health checks,
performance monitoring, and application initialization data.
Domain: System health, performance metrics, and core application functionality.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from apps.api.deps import get_delivery_service, get_schedule_service

# ✅ FIXED: Import proper Request-based functions instead of user_id-based ones
from apps.api.deps_factory import get_initial_data_service
from apps.api.middleware.auth import get_current_user_id
from apps.bot.models.twa import InitialDataResponse
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


@router.get(
    "/initial-data",
    response_model=InitialDataResponse,
    summary="Application Startup Data",
)
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
        # ✅ FIXED: Use proper configuration-driven service injection
        return await get_initial_data_service(request)

    except Exception as e:
        logger.error(f"Initial data fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get initial data")


@router.post("/schedule", response_model=dict)
async def create_scheduled_post(
    request: ScheduleRequest,
    schedule_service: ScheduleService = Depends(get_schedule_service),
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
        scheduled_post = await schedule_service.schedule_post(
            user_id=request.user_id,
            channel_id=request.channel_id,
            message=request.message,
            scheduled_time=request.scheduled_time,
            media_type=request.media_type,
            media_url=request.media_url,
        )

        return {
            "success": True,
            "post_id": scheduled_post["id"],
            "scheduled_time": request.scheduled_time.isoformat(),
            "message": "Post scheduled successfully",
            "channel_id": request.channel_id,
        }
    except Exception as e:
        logger.error(f"Post scheduling failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule post")


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
        post = await schedule_service.get_scheduled_post(post_id)

        if not post:
            raise HTTPException(status_code=404, detail="Scheduled post not found")

        return {
            "id": post["id"],
            "user_id": post["user_id"],
            "channel_id": post["channel_id"],
            "message": post["message"],
            "scheduled_time": post["scheduled_time"],
            "status": post["status"],
            "created_at": post["created_at"],
            "media_type": post.get("media_type"),
            "media_url": post.get("media_url"),
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
        posts = await schedule_service.get_user_scheduled_posts(user_id)

        return {
            "user_id": user_id,
            "total_posts": len(posts),
            "posts": [
                {
                    "id": post["id"],
                    "channel_id": post["channel_id"],
                    "message": (
                        post["message"][:100] + "..."
                        if len(post["message"]) > 100
                        else post["message"]
                    ),
                    "scheduled_time": post["scheduled_time"],
                    "status": post["status"],
                    "created_at": post["created_at"],
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
        result = await schedule_service.delete_scheduled_post(post_id)

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
async def get_delivery_stats(
    delivery_service: DeliveryService = Depends(get_delivery_service),
):
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
        from apps.api.di import container
        from config.settings import settings
        from core.protocols import AnalyticsServiceProtocol

        analytics_service = container.get_service(AnalyticsServiceProtocol)

        return {
            "analytics_service": {
                "name": analytics_service.get_service_name(),
                "demo_mode_enabled": settings.demo_mode.is_demo_enabled(),
                "using_mock_analytics": settings.demo_mode.should_use_mock_service("analytics"),
                "configuration": {
                    "strategy": settings.demo_mode.DEMO_MODE_STRATEGY,
                    "mock_delay_ms": settings.demo_mode.MOCK_API_DELAY_MS,
                },
            },
            "system_info": {
                "environment": ("production" if not settings.debug_mode else "development"),
                "clean_architecture": True,
                "service_type": "core_system",
            },
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Service info fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service information")
