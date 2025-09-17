"""
AnalyticBot API - Main Entry Point
Unified FastAPI application with layered architecture and secure configuration
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from apps.api.deps import cleanup_db_pool, get_delivery_service, get_schedule_service
from apps.api.routers.analytics_router import router as analytics_router
from apps.api.routers.analytics_v2 import router as analytics_v2_router
from apps.api.routers.analytics_advanced import router as analytics_advanced_router
from apps.api.routers.exports_v2 import router as exports_v2_router
from apps.api.routers.share_v2 import router as share_v2_router
from apps.api.routers.mobile_api import router as mobile_api_router
from apps.api.routers.auth_router import router as auth_router
from apps.api.superadmin_routes import router as superadmin_router
from apps.bot.api.content_protection_routes import router as content_protection_router
from apps.bot.api.payment_routes import router as payment_router
from apps.bot.models.twa import InitialDataResponse, User, Plan, Channel, ScheduledPost
from config import settings
from core import DeliveryService, ScheduleService
from infra.db.connection_manager import close_database, init_database
from apps.api.middleware.auth import get_current_user_id

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup - Initialize optimized database
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Continue without database for now to allow health checks
    yield
    # Shutdown - Cleanup database and legacy pool
    try:
        await close_database()
        await cleanup_db_pool()
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")


app = FastAPI(title="AnalyticBot API", version="v1", debug=settings.DEBUG, lifespan=lifespan)

# Add CORS middleware with explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(analytics_router)
app.include_router(analytics_v2_router)  # New Analytics Fusion API v2
app.include_router(analytics_advanced_router)  # Advanced Analytics with Alerts
app.include_router(exports_v2_router)  # Export functionality
app.include_router(share_v2_router)  # Share functionality
app.include_router(mobile_api_router)  # Mobile-optimized API endpoints
app.include_router(content_protection_router)
app.include_router(auth_router)  # Authentication endpoints
app.include_router(superadmin_router)
app.include_router(payment_router)  # Payment system

# Include AI services router
from apps.api.routers.ai_services import router as ai_services_router
app.include_router(ai_services_router)

# Include unified analytics router (best of both worlds)
from apps.api.routers.analytics_unified import router as unified_analytics_router
app.include_router(unified_analytics_router)


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "environment": settings.ENVIRONMENT, "debug": settings.DEBUG}


@app.get("/initial-data", response_model=InitialDataResponse)
async def get_initial_data(
    current_user_id: int = Depends(get_current_user_id),
):
    """Get initial application data for authenticated user
    
    Returns user info, subscription plan, channels, and scheduled posts
    for the authenticated user.
    """
    try:
        # TODO: Replace with real data from repositories
        # For now, return mock data that matches the expected structure
        
        # Mock user data
        user = User(
            id=current_user_id,
            username="demo_user"  # TODO: Get from user repository
        )
        
        # Mock plan data
        plan = Plan(
            name="Pro",
            max_channels=10,
            max_posts_per_month=1000
        )
        
        # Mock channels data
        channels = [
            Channel(id=1, title="Tech News", username="@technews"),
            Channel(id=2, title="Daily Updates", username="@dailyupdates"),
            Channel(id=3, title="Business Insights", username="@bizinsights")
        ]
        
        # Mock scheduled posts data
        scheduled_posts = [
            ScheduledPost(
                id=1,
                channel_id=1,
                scheduled_at=datetime.now(),
                text="Sample scheduled post 1"
            ),
            ScheduledPost(
                id=2,
                channel_id=2,
                scheduled_at=datetime.now(),
                text="Sample scheduled post 2"
            )
        ]
        
        return InitialDataResponse(
            user=user,
            plan=plan,
            channels=channels,
            scheduled_posts=scheduled_posts
        )
    
    except Exception as e:
        logger.error(f"Error fetching initial data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch initial data")


# Schedule endpoints using dependency injection
@app.post("/schedule", response_model=dict)
async def create_scheduled_post(
    title: str,
    content: str,
    channel_id: str,
    user_id: str,
    scheduled_at: datetime,
    tags: list[str] | None = None,
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Create a new scheduled post"""
    try:
        post = await schedule_service.create_scheduled_post(
            title=title,
            content=content,
            channel_id=channel_id,
            user_id=user_id,
            scheduled_at=scheduled_at,
            tags=tags,
        )

        return {
            "id": str(post.id),
            "title": post.title,
            "scheduled_at": post.scheduled_at.isoformat(),
            "status": post.status.value,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/schedule/{post_id}")
async def get_scheduled_post(
    post_id: UUID, schedule_service: ScheduleService = Depends(get_schedule_service)
):
    """Get a scheduled post by ID"""
    post = await schedule_service.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "id": str(post.id),
        "title": post.title,
        "content": post.content,
        "channel_id": post.channel_id,
        "user_id": post.user_id,
        "scheduled_at": post.scheduled_at.isoformat(),
        "status": post.status.value,
        "tags": post.tags,
        "created_at": post.created_at.isoformat(),
    }


@app.get("/schedule/user/{user_id}")
async def get_user_posts(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Get all scheduled posts for a user"""
    posts = await schedule_service.get_user_posts(user_id=user_id, limit=limit, offset=offset)

    return {
        "posts": [
            {
                "id": str(post.id),
                "title": post.title,
                "scheduled_at": post.scheduled_at.isoformat(),
                "status": post.status.value,
            }
            for post in posts
        ],
        "total": len(posts),
    }


@app.delete("/schedule/{post_id}")
async def cancel_scheduled_post(
    post_id: UUID, schedule_service: ScheduleService = Depends(get_schedule_service)
):
    """Cancel a scheduled post"""
    try:
        success = await schedule_service.cancel_post(post_id)
        if success:
            return {"message": "Post cancelled successfully"}
        else:
            raise HTTPException(status_code=404, detail="Post not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/delivery/stats")
async def get_delivery_stats(
    channel_id: str | None = None, delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """Get delivery statistics"""
    stats = await delivery_service.get_delivery_stats(channel_id=channel_id)
    return stats
