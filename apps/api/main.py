"""
AnalyticBot API - Main Entry Point
Unified FastAPI application with layered architecture and secure configuration
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from apps.api.routers.admin_channels_router import router as admin_channels_router
from apps.api.routers.admin_system_router import router as admin_system_router
from apps.api.routers.admin_users_router import router as admin_users_router
from apps.api.routers.auth import router as auth_router

# ✅ NEW MICROROUTER ARCHITECTURE
# analytics_microrouter merged into analytics_core_router (Phase 3A consolidation)
from apps.api.routers.channels_router import router as channels_router
from apps.api.routers.content_protection_router import router as content_protection_router

# Legacy routers (keeping for compatibility during transition)
# DEPRECATED ROUTERS REMOVED - cleanup
from apps.api.routers.exports_router import router as exports_router
from apps.api.routers.health_router import router as health_router
from apps.api.routers.media_router import router as media_router
from apps.api.routers.ml_predictions_router import router as ml_predictions_router
from apps.api.routers.mobile_router import router as mobile_router
from apps.api.routers.payment_router import router as payment_router
from apps.api.routers.posts_router import router as posts_router
from apps.api.routers.sharing_router import router as sharing_router
from apps.api.routers.superadmin_router import router as superadmin_router
from apps.api.routers.system_router import router as system_router
from apps.api.routers.telegram_storage_router import router as telegram_storage_router

# ✅ MIGRATED: Use new modular DI cleanup instead of legacy deps
from apps.di import cleanup_container as cleanup_db_pool

# ✅ CLEAN ARCHITECTURE: Use DI container
from apps.di import get_container
from config import settings

# ✅ PRODUCTION READY: No more direct mock imports
# Demo services now injected via DI container based on configuration

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events - now with proper DI container management and health checks"""
    # Startup - Initialize database and DI container
    try:
        # ✅ CLEAN ARCHITECTURE: Use shared DI container for database initialization
        container = get_container()
        db_manager = await container.database.database_manager()
        await db_manager.initialize()
        logger.info("Database initialized successfully via shared DI container")

        # Pre-initialize asyncpg pool to ensure it's ready
        pool = await container.database.asyncpg_pool()
        logger.info(
            f"✅ Asyncpg pool initialized with {pool.get_min_size()}-{pool.get_max_size()} connections"
        )

        # ✅ MULTI-TENANT: Initialize bot manager with repository factory
        try:
            logger.info("🔧 Starting bot manager initialization...")
            from apps.bot.multi_tenant.bot_manager import initialize_bot_manager
            from infra.db.repositories.user_bot_repository_factory import UserBotRepositoryFactory

            # Get session factory from DI container
            logger.info("🔧 Getting session factory from DI container...")
            session_factory = await container.database.async_session_maker()
            logger.info(f"🔧 Session factory obtained: {type(session_factory)}")

            # Create repository factory that generates fresh sessions per operation
            logger.info("🔧 Creating repository factory...")
            repository_factory = UserBotRepositoryFactory(session_factory)
            logger.info(f"🔧 Repository factory created: {type(repository_factory)}")

            # Initialize bot manager with the factory
            logger.info("🔧 Calling initialize_bot_manager...")
            await initialize_bot_manager(repository_factory)
            logger.info("✅ Multi-tenant bot manager initialized")
        except Exception as bot_error:
            import traceback

            logger.error(f"❌ Bot manager initialization failed at: {bot_error.__class__.__name__}")
            logger.error(f"❌ Error: {bot_error}")
            logger.error(f"❌ Full traceback:\n{traceback.format_exc()}")
            logger.info("Application will continue without bot manager")

        # ✅ MULTI-TENANT: Initialize MTProto service for full channel history access
        try:
            logger.info("🔧 Starting MTProto service initialization...")
            from apps.mtproto.multi_tenant.user_mtproto_service import init_user_mtproto_service
            from infra.db.repositories.user_bot_repository_factory import UserBotRepositoryFactory

            # Get session factory from DI container
            session_factory = await container.database.async_session_maker()

            # Create repository factory (same pattern as bot manager)
            repository_factory = UserBotRepositoryFactory(session_factory)

            # Initialize MTProto service with factory pattern
            # The service will create fresh repository instances with their own sessions as needed
            init_user_mtproto_service(user_bot_repo_factory=repository_factory)
            logger.info("✅ MTProto service initialized - full channel history access enabled")
        except Exception as mtproto_error:
            import traceback

            logger.error(f"❌ MTProto service initialization failed: {mtproto_error}")
            logger.error(f"❌ Full traceback:\n{traceback.format_exc()}")
            logger.info("Application will continue without MTProto service")

        # ✅ PHASE 2: Initialize Redis cache for performance optimization
        try:
            from core.common.cache_decorator import init_cache_redis

            # Use Redis DB 1 for caching (DB 0 is for Celery)
            redis_url = settings.REDIS_URL.replace("/0", "/1")
            await init_cache_redis(redis_url)
            logger.info("✅ Redis cache initialized for endpoint caching")
        except Exception as cache_error:
            logger.warning(f"⚠️ Redis cache initialization failed: {cache_error}")
            logger.info("Application will continue without caching")

        # ✅ PRODUCTION READINESS: Run comprehensive startup health checks
        try:
            from apps.api.services.startup_health_check import run_startup_health_check

            # Run health checks (fail_fast=False to not block startup on non-critical failures)
            health_report = await run_startup_health_check(
                fail_fast=False,  # Don't block startup - log warnings instead
                skip_optional=True,  # Skip optional checks for faster startup
            )

            # Store report globally for health endpoint
            app.state.startup_health_report = health_report

            if not health_report.is_production_ready:
                logger.warning(
                    "⚠️ Backend started with health check warnings - not production ready"
                )
            else:
                logger.info("✅ All startup health checks passed - Backend is production ready")
        except Exception as health_error:
            logger.error(f"⚠️ Startup health check failed: {health_error}")
            logger.info("Application will continue without health validation")

    except Exception as e:
        logger.error(f"Startup initialization failed: {e}")
        # Continue without database for now to allow health checks
    yield
    # Shutdown - Cleanup database and DI container
    try:
        # ✅ MULTI-TENANT: Shutdown bot manager
        try:
            from apps.bot.multi_tenant.bot_manager import get_bot_manager

            bot_manager = await get_bot_manager()
            await bot_manager.stop()
            logger.info("✅ Bot manager shutdown completed")
        except Exception as bot_error:
            logger.warning(f"⚠️ Bot manager shutdown failed: {bot_error}")

        # ✅ MULTI-TENANT: Shutdown MTProto service
        try:
            from apps.mtproto.multi_tenant.user_mtproto_service import get_user_mtproto_service

            mtproto_service = get_user_mtproto_service()
            await mtproto_service.shutdown()
            logger.info("✅ MTProto service shutdown completed")
        except Exception as mtproto_error:
            logger.warning(f"⚠️ MTProto service shutdown failed: {mtproto_error}")

        await cleanup_db_pool()
        logger.info("✅ Application shutdown completed")
    except Exception as e:
        logger.error(f"Application shutdown failed: {e}")


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
        "email": "support@analyticbot.com",
    },
    license_info={"name": "Enterprise License", "url": "https://analyticbot.com/license"},
    openapi_tags=[
        # Core System
        {
            "name": "Core",
            "description": "Essential system endpoints: health checks, initial data, and application lifecycle",
        },
        {
            "name": "Telegram Storage",
            "description": "☁️ Telegram Storage: user-owned channel storage, zero-cost file hosting, media management",
        },
        # AI Domain (All AI services consolidated)
        {
            "name": "AI - Chat",
            "description": "💬 AI Chat: conversational analytics, natural language queries, interactive insights",
        },
        {
            "name": "AI - Insights",
            "description": "🧠 AI Insights: comprehensive insights orchestration, pattern analysis, predictions",
        },
        {
            "name": "AI - Services",
            "description": "🤖 AI Services: churn prediction, content optimization, security analysis",
        },
        {
            "name": "AI - Strategy",
            "description": "� AI Strategy: content strategy generation, quick tips, implementation roadmaps",
        },
        {
            "name": "AI - Competitive",
            "description": "🏆 AI Competitive: competitor analysis, market intelligence, benchmarking",
        },
        {
            "name": "AI - Optimization",
            "description": "⚡ AI Optimization: performance analysis, recommendations, optimization cycles",
        },
        # Analytics Domain (All analytics consolidated)
        {
            "name": "Analytics - Channels",
            "description": "📊 Analytics Channels: channel listing and validation for analytics",
        },
        {
            "name": "Analytics - Realtime",
            "description": "⚡ Real-time Analytics: live metrics, performance scoring, monitoring",
        },
        {
            "name": "Analytics - Alerts",
            "description": "🔔 Alert Management: thresholds, notifications, alert system",
        },
        {
            "name": "Analytics - Posts",
            "description": "📝 Post Analytics: post dynamics, time-series performance tracking",
        },
        {
            "name": "Analytics - Historical",
            "description": "📊 Historical Statistics: growth trends, historical metrics, data analysis",
        },
        {
            "name": "Analytics - Reports",
            "description": "📋 Statistical Reports: comprehensive analysis, comparisons, trending",
        },
        {
            "name": "Analytics - Engagement",
            "description": "💬 Engagement Intelligence: audience insights, engagement patterns, trending content",
        },
        {
            "name": "Analytics - Orchestration",
            "description": "🎼 Workflow Orchestration: comprehensive analytics pipelines, service coordination",
        },
        {
            "name": "Analytics - Predictive",
            "description": "🔮 Predictive Analytics: AI/ML forecasting, recommendations, predictions",
        },
        {
            "name": "Analytics - ML",
            "description": "🧠 ML Predictions: growth forecasting, engagement prediction (background tasks)",
        },
        {
            "name": "Analytics - Trends",
            "description": "� Trend Analytics: forecasting, anomaly detection, change points",
        },
        # Content & Exports
        {
            "name": "Content - Protection",
            "description": "�️ Content Protection: watermarking, theft detection, premium features",
        },
        {
            "name": "Exports",
            "description": "� Data Export: CSV, PNG generation with customizable formatting",
        },
        {
            "name": "Sharing",
            "description": "� Secure Sharing: token-based access, revocation, audit trails",
        },
        # Admin & Auth
        {
            "name": "Authentication",
            "description": "🔐 Auth: JWT tokens, user management, session handling",
        },
        {
            "name": "Admin - Super",
            "description": "👑 SuperAdmin: system management, user administration, configuration",
        },
        # Payments & Mobile
        {
            "name": "Payments",
            "description": "💰 Payments: Stripe integration, subscriptions, payment processing",
        },
        {
            "name": "Mobile",
            "description": "📱 Mobile API: TWA-optimized endpoints for Telegram Web Apps",
        },
        {
            "name": "User Bot Management",
            "description": "🤖 Multi-Tenant Bots: user bot setup, verification, and management",
        },
        {
            "name": "Admin Bot Management",
            "description": "👑 Admin Bots: manage all user bots, suspend/activate, rate limiting",
        },
    ],
)

# Add performance and security middleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Production performance middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*.analyticbot.com", "*"]
)

# Add CORS middleware with explicit configuration
# Support both specific origins and tunnel wildcards
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.CORS_ORIGINS if settings.api.CORS_ORIGINS != "*" else ["*"],
    allow_origin_regex=r"https://.*\.(trycloudflare\.com|devtunnels\.ms)",  # Allow Cloudflare and Microsoft Dev Tunnels
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add demo mode detection middleware
from apps.demo.middleware import DemoMiddleware

app.add_middleware(DemoMiddleware)


# Add root /health endpoint for frontend compatibility (redirects to /health/)
@app.get("/health", tags=["Core"], include_in_schema=False)
async def root_health_check():
    """Root health endpoint - redirects to /health/ for frontend compatibility"""
    from fastapi.responses import JSONResponse

    # Return same format as /health/ endpoint
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "analyticbot",
            "version": "7.5.0",
        }
    )


# ✅ NEW MICROROUTER ARCHITECTURE - Domain-Focused Routing
app.include_router(system_router)  # Core system operations (performance, scheduling)
app.include_router(health_router)  # Comprehensive health monitoring (consolidated)
# app.include_router(analytics_router)     # ❌ REMOVED - analytics_microrouter merged into analytics_core_router (Phase 3A)
app.include_router(channels_router)  # Channel management (CRUD)
app.include_router(posts_router, prefix="/api")  # Posts management (MTProto collected data)
app.include_router(media_router)  # Media upload and management
app.include_router(telegram_storage_router, prefix="/api")  # Telegram storage (user-owned channels)
app.include_router(admin_channels_router)  # Admin - Channel Management
app.include_router(admin_users_router)  # Admin - User Management
app.include_router(admin_system_router)  # Admin - System Management

# ✅ PHASE 4: ANALYTICS DOMAIN REORGANIZATION (October 22, 2025)
# Consolidated analytics domain architecture - all analytics under /analytics/*
from apps.api.routers.analytics_alerts_router import router as analytics_alerts_router
from apps.api.routers.analytics_channels_router import router as analytics_channels_router
from apps.api.routers.analytics_live_router import router as analytics_live_router
from apps.api.routers.analytics_post_dynamics_router import router as analytics_post_dynamics_router
from apps.api.routers.analytics_top_posts_router import router as analytics_top_posts_router
from apps.api.routers.insights_engagement_router import router as insights_engagement_router
from apps.api.routers.insights_orchestration_router import router as insights_orchestration_router
from apps.api.routers.insights_predictive import router as insights_predictive_router
from apps.api.routers.statistics_core_router import router as statistics_core_router
from apps.api.routers.statistics_reports_router import router as statistics_reports_router
from apps.demo.routers.main import router as demo_router

# NEW: Organized analytics domain structure
app.include_router(
    analytics_channels_router, prefix="/analytics/channels", tags=["Analytics - Channels"]
)
app.include_router(
    analytics_live_router, prefix="/analytics/realtime", tags=["Analytics - Realtime"]
)  # Renamed from /live
app.include_router(analytics_alerts_router, prefix="/analytics/alerts", tags=["Analytics - Alerts"])
app.include_router(
    analytics_post_dynamics_router, prefix="/analytics/posts/dynamics", tags=["Analytics - Posts"]
)  # Post view dynamics and time-series
app.include_router(
    analytics_top_posts_router, prefix="/analytics/posts", tags=["Analytics - Top Posts"]
)  # Top performing posts rankings
app.include_router(
    statistics_core_router, prefix="/analytics/historical", tags=["Analytics - Historical"]
)  # Renamed from /statistics/core
app.include_router(
    statistics_reports_router, prefix="/analytics/reports", tags=["Analytics - Reports"]
)  # Moved from /statistics/reports
app.include_router(
    insights_engagement_router, prefix="/analytics/engagement", tags=["Analytics - Engagement"]
)  # Moved from /insights/engagement
app.include_router(
    insights_orchestration_router,
    prefix="/analytics/orchestration",
    tags=["Analytics - Orchestration"],
)  # Moved from /insights/orchestration
app.include_router(
    insights_predictive_router, prefix="/analytics/predictive", tags=["Analytics - Predictive"]
)  # Moved from /insights/predictive
app.include_router(
    ml_predictions_router, prefix="/analytics/ml", tags=["Analytics - ML"]
)  # Moved from /ml

# OLD: Backward compatibility (deprecated - will be removed in Q2 2026)
app.include_router(
    analytics_live_router,
    prefix="/analytics/live",
    tags=["analytics-live (deprecated)"],
    deprecated=True,
)
app.include_router(
    analytics_post_dynamics_router,
    prefix="/analytics/post-dynamics",
    tags=["analytics-post-dynamics (deprecated)"],
    deprecated=True,
)
app.include_router(
    statistics_core_router,
    prefix="/statistics/core",
    tags=["statistics-core (deprecated)"],
    deprecated=True,
)
app.include_router(
    statistics_reports_router,
    prefix="/statistics/reports",
    tags=["statistics-reports (deprecated)"],
    deprecated=True,
)
app.include_router(
    insights_engagement_router,
    prefix="/insights/engagement",
    tags=["insights-engagement (deprecated)"],
    deprecated=True,
)
app.include_router(
    insights_orchestration_router,
    prefix="/insights/orchestration",
    tags=["Analytics Orchestration v2 (deprecated)"],
    deprecated=True,
)
app.include_router(
    insights_predictive_router,
    prefix="/insights/predictive",
    tags=["insights-predictive (deprecated)"],
    deprecated=True,
)
app.include_router(
    ml_predictions_router, prefix="/ml", tags=["Machine Learning (deprecated)"], deprecated=True
)

app.include_router(demo_router)  # Demo endpoints

# 🎯 PHASE 4: GRANULAR ANALYTICS ARCHITECTURE COMPLETE ✅
# SUCCESSFULLY ELIMINATED GOD OBJECTS with 6 focused domain-separated routers:
#
# OLD (Phase 3): 4 routers with potential god objects
# - analytics_core_router        → SPLIT into statistics_core_router (5 endpoints)
# - analytics_realtime_router    → SPLIT into analytics_live_router (4 endpoints)
# - analytics_insights_router    → SPLIT into statistics_reports_router (4) + insights_engagement_router (4)
# - analytics_predictive_router  → SPLIT into insights_predictive_router (4 endpoints)
# - analytics_alerts_router      → KEPT as-is (8 endpoints, already focused)
#
# NEW (Phase 4): 6 focused routers with NO god objects (4-8 endpoints each):
# 1. Live Analytics:     /analytics/live/*        → analytics_live_router (4 endpoints)
# 2. Alert Management:   /analytics/alerts/*      → analytics_alerts_router (8 endpoints)
# 3. Core Statistics:    /statistics/core/*       → statistics_core_router (5 endpoints)
# 4. Statistical Reports:/statistics/reports/*    → statistics_reports_router (4 endpoints)
# 5. Engagement Insights:/insights/engagement/*   → insights_engagement_router (4 endpoints)
# 6. Predictive AI/ML:   /insights/predictive/*   → insights_predictive_router (4 endpoints)
#
# ✅ PERFECT CLEAN ARCHITECTURE: Single Responsibility, Clear Domain Boundaries, No God Objects
# Original files archived with _ORIGINAL_BEFORE_GRANULAR_SPLIT suffix for reference
# app.include_router(analytics_v2_router)      # ❌ REMOVED: Use /analytics/core/* + /analytics/insights/* instead
# app.include_router(analytics_advanced_router) # ❌ REMOVED: Use /analytics/realtime/* + /analytics/alerts/* instead
# ✅ PHASE 8: REMAINING DOMAINS REORGANIZATION (October 22, 2025)
# Standardizing naming conventions across all remaining domains

# Content Protection: /content-protection → /content/protection
app.include_router(
    content_protection_router, prefix="/content/protection", tags=["Content - Protection"]
)  # NEW
app.include_router(
    content_protection_router,
    prefix="/content-protection",
    tags=["Content Protection (deprecated)"],
    deprecated=True,
)  # OLD

# Payments: /payment → /payments (plural for consistency)
app.include_router(payment_router, prefix="/payments", tags=["Payments"])  # NEW
app.include_router(
    payment_router, prefix="/payment", tags=["Payments (deprecated)"], deprecated=True
)  # OLD

# Admin: /superadmin → /admin/super (better hierarchy)
app.include_router(superadmin_router, prefix="/admin/super", tags=["Admin - Super"])  # NEW
app.include_router(
    superadmin_router,
    prefix="/superadmin",
    tags=["SuperAdmin Management (deprecated)"],
    deprecated=True,
)  # OLD

# Auth, Channels, System, Health, Mobile, Exports, Sharing - Already well-organized
app.include_router(auth_router)  # /auth/* - Already good
app.include_router(exports_router)  # /exports/* - Already good
app.include_router(sharing_router)  # /sharing/* - Already good
app.include_router(mobile_router)  # /mobile/* - Already good

# ✅ PHASE 4 MULTI-TENANT: User and Admin Bot Management (October 27, 2025)
from apps.api.routers.admin_bot_router import router as admin_bot_router
from apps.api.routers.user_bot_router import router as user_bot_router
from apps.api.routers.user_mtproto_monitoring_router import router as user_mtproto_monitoring_router
from apps.api.routers.user_mtproto_router import router as user_mtproto_router

app.include_router(user_bot_router, tags=["User Bot Management"])  # /api/user-bot/*
app.include_router(admin_bot_router, tags=["Admin Bot Management"])  # /api/admin/bots/*
app.include_router(user_mtproto_router, tags=["User Bot Management"])  # /api/user-mtproto/*
app.include_router(
    user_mtproto_monitoring_router, tags=["MTProto Monitoring"]
)  # /api/user-mtproto/monitoring/*

# ✅ PHASE 7: AI DOMAIN REORGANIZATION (October 22, 2025)
# Consolidating all AI services under /ai/* for better organization
from apps.api.routers.ai_chat_router import router as ai_chat_router
from apps.api.routers.ai_insights_router import router as ai_insights_router
from apps.api.routers.ai_services_router import router as ai_services_router
from apps.api.routers.competitive_intelligence_router import router as competitive_router
from apps.api.routers.optimization_router import router as optimization_router
from apps.api.routers.strategy_router import router as strategy_router
from apps.api.routers.trend_analysis_router import router as trends_router

# NEW: Organized AI domain structure
app.include_router(ai_chat_router, prefix="/ai/chat", tags=["AI - Chat"])  # Conversational AI
app.include_router(ai_insights_router, prefix="/ai/insights", tags=["AI - Insights"])  # AI analysis
app.include_router(
    ai_services_router, prefix="/ai/services", tags=["AI - Services"]
)  # Churn, content, security
app.include_router(
    strategy_router, prefix="/ai/strategy", tags=["AI - Strategy"]
)  # Strategy generation
app.include_router(
    competitive_router, prefix="/ai/competitive", tags=["AI - Competitive"]
)  # Market intelligence
app.include_router(
    optimization_router, prefix="/ai/optimization", tags=["AI - Optimization"]
)  # Performance optimization

# OLD: Backward compatibility (deprecated - will be removed in Q2 2026)
app.include_router(
    ai_chat_router, prefix="/ai-chat", tags=["AI Chat (deprecated)"], deprecated=True
)
app.include_router(
    ai_insights_router, prefix="/ai-insights", tags=["AI Insights (deprecated)"], deprecated=True
)
app.include_router(
    ai_services_router, prefix="/ai-services", tags=["AI Services (deprecated)"], deprecated=True
)
app.include_router(
    strategy_router, prefix="/strategy", tags=["Strategy (deprecated)"], deprecated=True
)
app.include_router(
    competitive_router,
    prefix="/competitive",
    tags=["Competitive Intelligence (deprecated)"],
    deprecated=True,
)
app.include_router(
    optimization_router, prefix="/optimization", tags=["Optimization (deprecated)"], deprecated=True
)

# Analytics Trends moved to analytics domain
app.include_router(
    trends_router, prefix="/analytics/trends", tags=["Analytics - Trends"]
)  # NEW location
app.include_router(
    trends_router, prefix="/trends", tags=["Trend Analysis (deprecated)"], deprecated=True
)  # OLD location

# CLEAN ARCHITECTURE REORGANIZATION COMPLETE ✅
# ===============================================
# Phase 1: Router file renames and import updates
# Phase 2: Domain boundary corrections (analytics separated)
# Phase 3: Admin god router split into focused routers
#
# CURRENT ROUTER ARCHITECTURE:
# - /channels → channels_router.py (Pure channel CRUD)
# - /admin/channels → admin_channels_router.py (Channel administration)
# - /admin/users → admin_users_router.py (User administration)
# - /admin/system → admin_system_router.py (System administration)
# - /analytics/insights → analytics_insights_router.py (Analytics domain)
# - /system → system_router.py (System health, performance)
# - /health, /performance, /initial-data → system_router.py
# - /schedule → system_router.py
# - /delivery/stats → system_router.py
#
# ✅ CLEAN ARCHITECTURE BENEFITS ACHIEVED:
# - Single Responsibility Principle: Each router has one focused domain
# - Domain Separation: Clear boundaries between business domains
# - Maintainability: Easy to understand, modify, and test each domain
# - Scalability: New features can be added to appropriate domains

# API DI Container initialized above in main.py
