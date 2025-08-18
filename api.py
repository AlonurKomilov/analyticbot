import logging
from contextlib import asynccontextmanager
from typing import Annotated
from datetime import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

# Imports updated for the new project structure (without 'src')
from bot.config import Settings, settings
from bot.container import container
from bot.services.prometheus_service import prometheus_service, setup_prometheus_middleware
from bot.database.repositories import (
    ChannelRepository,
    PlanRepository,
    SchedulerRepository,
    UserRepository,
)
from bot.models.twa import (
    AddChannelRequest,
    Channel,
    InitialDataResponse,
    MessageResponse,
    Plan,
    ScheduledPost,
    SchedulePostRequest,
    User,
    ValidationErrorResponse,
)
from bot.services import GuardService, SubscriptionService
from bot.services.auth_service import validate_init_data

# Logging setup
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# --- FastAPI Dependencies ---


def get_settings() -> Settings:
    """Returns the application settings instance."""
    return settings


def get_user_repo() -> UserRepository:
    return container.resolve(UserRepository)


def get_channel_repo() -> ChannelRepository:
    return container.resolve(ChannelRepository)


def get_plan_repo() -> PlanRepository:
    return container.resolve(PlanRepository)


def get_scheduler_repo() -> SchedulerRepository:
    return container.resolve(SchedulerRepository)


def get_subscription_service() -> SubscriptionService:
    return container.resolve(SubscriptionService)


def get_guard_service() -> GuardService:
    return container.resolve(GuardService)


async def get_validated_user_data(
    authorization: Annotated[str, Header()],
    current_settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    """
    Validates the initData string from a TWA and returns the user data.
    """
    if not authorization or not authorization.startswith("TWA "):
        raise HTTPException(status_code=401, detail="Invalid authorization scheme.")

    init_data = authorization.split("TWA ", 1)[1]
    if not init_data:
        raise HTTPException(status_code=401, detail="initData is missing.")

    try:
        user_data = validate_init_data(
            init_data, current_settings.BOT_TOKEN.get_secret_value()
        )
        return user_data
    except Exception as e:
        log.error(f"Could not validate initData: {e}")
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid initData.")


# --- FastAPI Application ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("API is starting up...")
    yield
    log.info("API is shutting down...")


app = FastAPI(
    lifespan=lifespan,
    responses={
        422: {"description": "Validation Error", "model": ValidationErrorResponse}
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics middleware
app.add_middleware(setup_prometheus_middleware())

# Set app info for Prometheus metrics
prometheus_service.set_app_info(version="1.1.0", environment="production")


# --- API Endpoints ---


@app.get("/health", tags=["Health"])
async def health_check():
    """Enhanced health check endpoint with system status"""
    try:
        # Basic health status
        status = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }
        
        # Check database health
        try:
            from bot.database.db import is_db_healthy
            db_healthy = await is_db_healthy()
            status["database"] = "healthy" if db_healthy else "unhealthy"
        except Exception as e:
            log.warning(f"Database health check failed: {e}")
            status["database"] = "unknown"
        
        # Check Redis health (if configured)
        try:
            import redis.asyncio as redis
            redis_client = redis.from_url(str(settings.REDIS_URL))
            await redis_client.ping()
            status["redis"] = "healthy"
            await redis_client.close()
        except Exception as e:
            log.warning(f"Redis health check failed: {e}")
            status["redis"] = "unknown"
        
        # Overall status based on components
        if status.get("database") == "unhealthy":
            status["status"] = "degraded"
            return status
        
        return status
        
    except Exception as e:
        log.error(f"Health check error: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with more system information"""
    try:
        try:
            import psutil
            system_metrics_available = True
        except ImportError:
            system_metrics_available = False
            
        from bot.database.db import db_manager, is_db_healthy
        
        status = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "healthy": await is_db_healthy(),
            },
            "configuration": {
                "debug_mode": settings.DEBUG_MODE,
                "log_level": settings.LOG_LEVEL.value,
                "supported_locales": settings.SUPPORTED_LOCALES,
            }
        }
        
        # Add system metrics if psutil is available
        if system_metrics_available:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status["system"] = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": (disk.used / disk.total) * 100,
                "available_memory_mb": memory.available // 1024 // 1024,
            }
        
        # Add database pool info if available
        if db_manager.pool:
            status["database"].update({
                "pool_size": getattr(db_manager.pool, 'get_size', lambda: 0)(),
                "pool_max_size": getattr(db_manager.pool, 'get_max_size', lambda: 0)(),
            })
        
        return status
        
    except Exception as e:
        log.error(f"Detailed health check error: {e}", exc_info=True)
        return {"error": str(e)}


@app.get("/metrics", tags=["Monitoring"])
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    try:
        # Collect latest metrics before serving
        from bot.services.prometheus_service import collect_system_metrics
        await collect_system_metrics()
        
        metrics_data = prometheus_service.get_metrics()
        
        return Response(
            content=metrics_data,
            media_type=prometheus_service.get_content_type()
        )
        
    except Exception as e:
        log.error(f"Metrics endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Metrics collection failed")


@app.post("/api/v1/media/upload", tags=["Media"])
async def upload_media_file(
    file: UploadFile = File(...),
    current_settings: Annotated[Settings, Depends(get_settings)] = None,
):
    """Upload media file to storage channel with enhanced error handling"""
    if current_settings is None:
        current_settings = get_settings()
    
    bot = Bot(token=current_settings.BOT_TOKEN.get_secret_value())

    try:
        # Validate file
        if not file.content_type:
            raise HTTPException(status_code=400, detail="File content type is required")
        
        # Check file size (if file has size attribute)
        if hasattr(file, 'size') and file.size:
            max_size = current_settings.MAX_MEDIA_SIZE_MB * 1024 * 1024
            if file.size > max_size:
                raise HTTPException(
                    status_code=413, 
                    detail=f"File too large. Maximum size: {current_settings.MAX_MEDIA_SIZE_MB}MB"
                )
        
        # Validate content type
        if file.content_type not in current_settings.ALLOWED_MEDIA_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.content_type}. "
                       f"Allowed types: {current_settings.ALLOWED_MEDIA_TYPES}"
            )

        content_type = file.content_type.lower()
        
        # Determine media type and send to storage channel
        if content_type.startswith("image/"):
            media_type = "photo"
            sent_message = await bot.send_photo(
                chat_id=current_settings.STORAGE_CHANNEL_ID, 
                photo=file.file,
                caption=f"Uploaded: {file.filename or 'unknown'}"
            )
            file_id = sent_message.photo[-1].file_id
        elif content_type.startswith("video/"):
            media_type = "video"
            sent_message = await bot.send_video(
                chat_id=current_settings.STORAGE_CHANNEL_ID, 
                video=file.file,
                caption=f"Uploaded: {file.filename or 'unknown'}"
            )
            file_id = sent_message.video.file_id
        elif content_type == "image/gif":
            # GIF files should be sent as animation
            media_type = "animation"
            sent_message = await bot.send_animation(
                chat_id=current_settings.STORAGE_CHANNEL_ID,
                animation=file.file,
                caption=f"Uploaded: {file.filename or 'unknown'}"
            )
            file_id = sent_message.animation.file_id
        else:
            # Fallback to document for other types
            media_type = "document"
            sent_message = await bot.send_document(
                chat_id=current_settings.STORAGE_CHANNEL_ID,
                document=file.file,
                caption=f"Uploaded: {file.filename or 'unknown'}"
            )
            file_id = sent_message.document.file_id

        log.info(f"Successfully uploaded {media_type} file: {file.filename}")
        return {
            "ok": True, 
            "file_id": file_id, 
            "media_type": media_type,
            "filename": file.filename
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except TelegramAPIError as e:
        log.error(f"Telegram API error while uploading file: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to upload file to Telegram: {str(e)}"
        )
    except Exception as e:
        log.error(f"Unexpected error during file upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="Internal server error during file upload"
        )
    finally:
        await bot.session.close()


@app.get("/api/v1/initial-data", response_model=InitialDataResponse)
async def get_initial_data(
    user_data: Annotated[dict, Depends(get_validated_user_data)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    channel_repo: Annotated[ChannelRepository, Depends(get_channel_repo)],
    scheduler_repo: Annotated[SchedulerRepository, Depends(get_scheduler_repo)],
    plan_repo: Annotated[PlanRepository, Depends(get_plan_repo)],
):
    user_id = user_data["id"]
    username = user_data.get("username")

    # Ensure the user exists in the database
    await user_repo.create_user(user_id, username)

    # Fetch plan information
    plan = None
    plan_name = await user_repo.get_user_plan_name(user_id)
    if plan_name:
        plan_row = await plan_repo.get_plan_by_name(plan_name)
        if plan_row:
            plan = Plan(
                name=plan_row.get("plan_name") or plan_row.get("name"),
                max_channels=plan_row["max_channels"],
                max_posts_per_month=plan_row["max_posts_per_month"],
            )

    # Fetch channels and scheduled posts
    channel_rows = await channel_repo.get_user_channels(user_id)
    channels = [
        Channel(
            id=row["id"],
            title=row.get("title") or "",
            username=row.get("username"),
        )
        for row in (channel_rows or [])
    ]
    post_rows = await scheduler_repo.get_scheduled_posts_by_user(user_id)
    scheduled_posts = [
        ScheduledPost(
            id=row["id"],
            channel_id=row["channel_id"],
            text=row.get("post_text"),
            media_id=row.get("media_id"),
            media_type=row.get("media_type"),
            scheduled_at=row.get("schedule_time"),
            buttons=row.get("inline_buttons"),
        )
        for row in (post_rows or [])
    ]

    user = User(id=user_id, username=username)
    return InitialDataResponse(
        user=user,
        plan=plan,
        channels=channels,
        scheduled_posts=scheduled_posts,
    )


@app.post("/api/v1/channels", response_model=Channel)
async def add_channel(
    request_data: AddChannelRequest,
    user_data: Annotated[dict, Depends(get_validated_user_data)],
    guard_service: Annotated[GuardService, Depends(get_guard_service)],
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
):
    user_id = user_data["id"]
    channel_username = request_data.channel_username.strip()

    if not channel_username.startswith("@"):
        channel_username = f"@{channel_username}"

    await subscription_service.check_channel_limit(user_id)
    channel_data = await guard_service.check_bot_is_admin(channel_username, user_id)

    return Channel(
        id=channel_data.get("channel_id") or channel_data["id"],
        title=channel_data.get("channel_name") or channel_data.get("title", ""),
        username=channel_data.get("username"),
    )


@app.post("/api/v1/schedule-post", response_model=ScheduledPost)
async def schedule_post(
    request: SchedulePostRequest,
    user_data: Annotated[dict, Depends(get_validated_user_data)],
    scheduler_repo: Annotated[SchedulerRepository, Depends(get_scheduler_repo)],
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
):
    user_id = user_data["id"]
    await subscription_service.check_post_limit(user_id)

    post_id = await scheduler_repo.create_scheduled_post(
        user_id=user_id,
        channel_id=request.channel_id,
        post_text=request.text or "",
        schedule_time=request.scheduled_at,
        media_id=request.media_id,
        media_type=request.media_type,
        inline_buttons=(
            [button.model_dump() for button in request.buttons]
            if request.buttons
            else None
        ),
    )

    return ScheduledPost(
        id=post_id,
        channel_id=request.channel_id,
        text=request.text,
        media_id=request.media_id,
        media_type=request.media_type,
        scheduled_at=request.scheduled_at,
        buttons=request.buttons,
    )


@app.delete("/api/v1/posts/{post_id}", response_model=MessageResponse)
async def delete_post(
    post_id: int,
    user_data: Annotated[dict, Depends(get_validated_user_data)],
    scheduler_repo: Annotated[SchedulerRepository, Depends(get_scheduler_repo)],
):
    user_id = user_data["id"]
    success = await scheduler_repo.delete_scheduled_post(post_id, user_id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Post not found or you don't have permission."
        )

    return MessageResponse(message="Post deleted successfully")


@app.delete("/api/v1/channels/{channel_id}", response_model=MessageResponse)
async def delete_channel(
    channel_id: int,
    user_data: Annotated[dict, Depends(get_validated_user_data)],
    channel_repo: Annotated[ChannelRepository, Depends(get_channel_repo)],
):
    user_id = user_data["id"]
    channel_row = await channel_repo.get_channel_by_id(channel_id)
    if not channel_row or channel_row["user_id"] != user_id:
        raise HTTPException(
            status_code=404, detail="Channel not found or you don't have permission."
        )

    success = await channel_repo.delete_channel(channel_id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Channel not found or you don't have permission."
        )

    return MessageResponse(message="Channel deleted successfully")
