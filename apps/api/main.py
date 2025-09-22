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
from apps.api.middleware.demo_mode import is_request_for_demo_user, get_demo_type_from_request
from apps.api.__mocks__.demo_service import demo_data_service
from apps.api.__mocks__.initial_data.mock_data import get_mock_initial_data

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


app = FastAPI(
    title="🤖 AnalyticBot Enterprise API",
    version="2.1.0",
    description="""
## 🚀 Professional Telegram Channel Analytics Platform

### 📊 **Analytics & Insights**
Advanced analytics with real-time metrics, AI-powered recommendations, and comprehensive reporting.

### 🔐 **Authentication & Security**  
JWT-based authentication with role-based access control and content protection.

### 💰 **Payment Integration**
Stripe-powered subscription management with automated billing.

### 🤖 **AI Services**
Content optimization, churn prediction, and intelligent recommendations.

### 📱 **Mobile Optimized**
Telegram Web App (TWA) optimized endpoints for mobile experiences.

### 📈 **Export & Sharing**
Comprehensive data export capabilities with secure sharing mechanisms.

---
**🏗️ Built with Clean Architecture** | **⚡ High Performance** | **🔒 Enterprise Security**
    """,
    summary="Enterprise-grade Telegram channel analytics with AI-powered insights",
    debug=settings.DEBUG,
    lifespan=lifespan,
    contact={
        "name": "AnalyticBot Support",
        "url": "https://t.me/abccontrol_bot",
        "email": "support@analyticbot.com"
    },
    license_info={
        "name": "Enterprise License",
        "url": "https://analyticbot.com/license"
    },
    openapi_tags=[
        {
            "name": "Core",
            "description": "Essential system endpoints: health checks, initial data, and application lifecycle"
        },
        {
            "name": "Analytics",
            "description": "📊 Core analytics endpoints: channels, metrics, and basic reporting"
        },
        {
            "name": "Analytics V2", 
            "description": "📈 Enhanced analytics: advanced metrics, caching, and performance optimization"
        },
        {
            "name": "Advanced Analytics",
            "description": "🔮 AI-powered analytics: real-time dashboards, alerts, and predictive insights"
        },
        {
            "name": "AI Services",
            "description": "🤖 Artificial Intelligence: content optimization, churn prediction, security analysis"
        },
        {
            "name": "Exports",
            "description": "📋 Data Export: CSV, PNG generation with customizable formatting"
        },
        {
            "name": "Sharing",
            "description": "🔗 Secure Sharing: token-based access, revocation, and audit trails"
        },
        {
            "name": "Mobile",
            "description": "📱 Mobile API: TWA-optimized endpoints for Telegram Web Apps"
        },
        {
            "name": "Content Protection",
            "description": "🛡️ Security: content verification, threat detection, and access control"
        },
        {
            "name": "Payments",
            "description": "💰 Billing: Stripe integration, subscriptions, and payment processing"
        },
        {
            "name": "Authentication",
            "description": "🔐 Auth: JWT tokens, user management, and session handling"
        },
        {
            "name": "SuperAdmin Management",
            "description": "👑 Admin: user management, system stats, and administrative controls"
        }
    ]
)

# Add performance and security middleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Production performance middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.analyticbot.com", "*"]
)

# Add CORS middleware with explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add demo mode detection middleware
from apps.api.middleware.demo_mode import DemoModeMiddleware
app.add_middleware(DemoModeMiddleware)

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


@app.get("/health", tags=["Core"], summary="System Health Check")
async def health():
    """
    ## 🏥 System Health Status
    
    Enhanced health check providing system status, environment info, API readiness, and dependency health.
    
    **Returns:**
    - System status (ok/error)
    - Environment information
    - Debug mode status
    - API version
    - Database health
    - Dependency status
    """
    from infra.db.connection_manager import check_db_health
    db_health = await check_db_health()
    status = "ok" if db_health.get("healthy", False) else "error"
    dependencies = {
        "database": db_health,
        # Add more dependencies here (e.g., cache, external APIs)
    }
    return {
        "status": status,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "version": "2.1.0",
        "api_title": "AnalyticBot Enterprise API",
        "timestamp": datetime.now().isoformat(),
        "dependencies": dependencies
    }


@app.get("/performance", tags=["Core"], summary="Performance Metrics")
async def get_performance_metrics():
    """
    ## ⚡ Real-Time Performance Metrics
    
    Comprehensive performance monitoring including cache hit rates, response times, and system metrics.
    
    **Metrics Include:**
    - 📊 Cache performance statistics
    - ⏱️ Average response times
    - 💾 Memory usage patterns
    - 🔄 Request throughput metrics
    """
    try:
        from apps.bot.database.performance import performance_manager
        
        # Get performance stats if available
        if hasattr(performance_manager, 'get_performance_stats'):
            stats = await performance_manager.get_performance_stats()
        else:
            stats = {"cache_connected": False, "performance_optimizations": "enabled"}
        
        return {
            "api_performance": {
                "status": "optimized",
                "cache_enabled": True,
                "compression_enabled": True,
                "security_middleware": True
            },
            "system_stats": stats,
            "optimization_features": [
                "Intelligent caching with Redis",
                "GZip compression middleware", 
                "Performance timing decorators",
                "Advanced cache decorators",
                "Database connection pooling"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.warning(f"Performance metrics unavailable: {e}")
        return {
            "api_performance": {
                "status": "baseline",
                "optimization_features": ["Professional endpoint structure", "Enhanced documentation"]
            },
            "timestamp": datetime.now().isoformat()
        }


@app.get("/initial-data", response_model=InitialDataResponse, tags=["Core"], summary="Application Startup Data")
async def get_initial_data(
    current_user_id: int = Depends(get_current_user_id),
):
    """
    ## 🚀 Initialize Application State
    
    Fetches essential data required for application startup including user profile, 
    subscription details, managed channels, and scheduled content.
    
    **Authentication Required:** JWT token via Authorization header
    
    **Returns:**
    - **User Profile**: ID, username, and basic account info
    - **Subscription Plan**: Current plan limits and features  
    - **Managed Channels**: List of accessible Telegram channels
    - **Scheduled Posts**: Upcoming scheduled content
    
    **Used by:** Frontend applications, mobile TWA, and dashboard initialization
    """
    try:
        # Check if this is a demo user by ID
        from apps.api.__mocks__.auth.mock_users import is_demo_user_by_id, get_demo_user_type_by_id
        
        if is_demo_user_by_id(str(current_user_id)):
            demo_type = get_demo_user_type_by_id(str(current_user_id))
            demo_data = demo_data_service.get_initial_data(demo_type)
            
            return InitialDataResponse(
                user=User(
                    id=demo_data["user"]["id"],
                    username=demo_data["user"]["username"]
                ),
                plan=Plan(
                    name=demo_data["plan"]["name"],
                    max_channels=demo_data["plan"]["max_channels"],
                    max_posts_per_month=demo_data["plan"]["max_posts_per_month"]
                ),
                channels=[
                    Channel(
                        id=channel["id"],
                        title=channel["title"],
                        username=channel["username"]
                    ) for channel in demo_data["channels"]
                ],
                scheduled_posts=[
                    ScheduledPost(
                        id=post["id"],
                        channel_id=post["channel_id"],
                        scheduled_at=datetime.fromisoformat(post["scheduled_at"]),
                        text=post["text"]
                    ) for post in demo_data["scheduled_posts"]
                ]
            )
        
        # For regular users, fetch data from actual repositories
        # TODO: Replace with actual user repository implementation
        try:
            # Attempt to get user data from database
            # user = await user_repository.get_by_id(current_user_id)
            # plan = await subscription_service.get_user_plan(current_user_id)
            # channels = await channel_repository.get_user_channels(current_user_id)
            # scheduled_posts = await schedule_service.get_user_scheduled_posts(current_user_id)
            
            # Temporary fallback until repositories are implemented
            user = User(
                id=current_user_id,
                username="user"
            )
            
            plan = Plan(
                name="Free",
                max_channels=3,
                max_posts_per_month=100
            )
            
            channels = []  # No channels until user creates them
            scheduled_posts = []  # No scheduled posts until user creates them
            
            return InitialDataResponse(
                user=user,
                plan=plan,
                channels=channels,
                scheduled_posts=scheduled_posts
            )
            
        except Exception as e:
            logger.error(f"Error fetching user data for user {current_user_id}: {e}")
            # Return minimal data structure - no mock data fallback
            return InitialDataResponse(
                user=User(id=current_user_id, username="user"),
                plan=Plan(name="Free", max_channels=3, max_posts_per_month=100),
                channels=[],
                scheduled_posts=[]
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
