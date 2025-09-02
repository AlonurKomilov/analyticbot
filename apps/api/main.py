"""
AnalyticBot API - Main Entry Point
Unified FastAPI application with layered architecture and secure configuration
"""

from contextlib import asynccontextmanager
from datetime import datetime
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from apps.api.deps import cleanup_db_pool, get_delivery_service, get_schedule_service
from apps.api.routers.analytics_router import router as analytics_router
from apps.api.routers.analytics_v2 import router as analytics_v2_router
from apps.api.superadmin_routes import router as superadmin_router
from apps.bot.api.content_protection_routes import router as content_protection_router
from config import settings
from core import DeliveryService, ScheduleService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    yield
    # Shutdown
    await cleanup_db_pool()


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
app.include_router(content_protection_router)
app.include_router(superadmin_router)


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
    }


# Schedule endpoints using dependency injection
@app.post("/schedule", response_model=dict)
async def create_scheduled_post(
    title: str,
    content: str,
    channel_id: str,
    user_id: str,
    scheduled_at: datetime,
    tags: list[str] = None,
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
    channel_id: str = None,
    delivery_service: DeliveryService = Depends(get_delivery_service),
):
    """Get delivery statistics"""
    stats = await delivery_service.get_delivery_stats(channel_id=channel_id)
    return stats
