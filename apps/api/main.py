"""
AnalyticBot API - Main Entry Point
Unified FastAPI application with layered architecture and secure configuration
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from apps.api.routers.admin_channels_router import router as admin_channels_router
from apps.api.routers.admin_system_router import router as admin_system_router
from apps.api.routers.admin_users_router import router as admin_users_router
from apps.api.routers.auth_router import router as auth_router

# ✅ NEW MICROROUTER ARCHITECTURE
# analytics_microrouter merged into analytics_core_router (Phase 3A consolidation)
from apps.api.routers.channels_router import router as channels_router

# ✅ PHASE 1 FIX: Moved routers from apps/shared/api to apps/api/routers (circular dep fix)
from apps.api.routers.content_protection_router import router as content_protection_router

from apps.api.routers.exports_router import router as exports_router
from apps.api.routers.health_router import router as health_router
from apps.api.routers.ml_predictions_router import router as ml_predictions_router
from apps.api.routers.mobile_router import router as mobile_router
from apps.api.routers.payment_router import router as payment_router
from apps.api.routers.sharing_router import router as sharing_router
from apps.api.routers.superadmin_router import router as superadmin_router
from apps.api.routers.system_router import router as system_router
from apps.di import cleanup_container as cleanup_db_pool
from apps.di import get_container
from config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events - now with proper DI container management and health checks"""
    # Startup - Initialize database and DI container
    try:
        container = get_container()
        db_manager = await container.database_manager()
        await db_manager.initialize()
        logger.info("Database initialized successfully via shared DI container")

        # Pre-initialize asyncpg pool to ensure it's ready
        pool = await container.asyncpg_pool()
        logger.info(
            f"✅ Asyncpg pool initialized with {pool.get_min_size()}-{pool.get_max_size()} connections"
        )

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
        await cleanup_db_pool()  # This calls cleanup_container internally
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
        {
            "name": "Core",
            "description": "Essential system endpoints: health checks, initial data, and application lifecycle",
        },
        {
            "name": "analytics-live",
            "description": "⚡ Real-time Analytics: live metrics, performance scoring, and monitoring",
        },
        {
            "name": "analytics-alerts",
            "description": "� Alert Management: thresholds, notifications, and alert system",
        },
        {
            "name": "statistics-core",
            "description": "📊 Core Statistics: historical metrics, growth trends, and data analysis",
        },
        {
            "name": "statistics-reports",
            "description": "📋 Statistical Reports: comprehensive analysis, comparisons, and trending",
        },
        {
            "name": "insights-engagement",
            "description": "💬 Engagement Intelligence: audience insights, engagement patterns, trending content",
        },
        {
            "name": "insights-predictive",
            "description": "🔮 Predictive Analytics: AI/ML forecasting, recommendations, and predictions",
        },
        {
            "name": "AI Services",
            "description": "🤖 Artificial Intelligence: content optimization, churn prediction, security analysis",
        },
        {
            "name": "Machine Learning",
            "description": "🧠 ML Predictions: growth forecasting, engagement prediction (background tasks)",
        },
        {
            "name": "Exports",
            "description": "📋 Data Export: CSV, PNG generation with customizable formatting",
        },
        {
            "name": "Sharing",
            "description": "🔗 Secure Sharing: token-based access, revocation, and audit trails",
        },
        {
            "name": "Mobile",
            "description": "📱 Mobile API: TWA-optimized endpoints for Telegram Web Apps",
        },
        {
            "name": "Content Protection",
            "description": "🛡️ Security: content verification, threat detection, and access control",
        },
        {
            "name": "Payments",
            "description": "💰 Billing: Stripe integration, subscriptions, and payment processing",
        },
        {
            "name": "Authentication",
            "description": "🔐 Auth: JWT tokens, user management, and session handling",
        },
        {
            "name": "SuperAdmin Management",
            "description": "👑 Admin: user management, system stats, and administrative controls",
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add demo mode detection middleware
from apps.demo.middleware import DemoMiddleware

app.add_middleware(DemoMiddleware)

# ✅ NEW MICROROUTER ARCHITECTURE - Domain-Focused Routing
app.include_router(system_router)  # Core system operations (performance, scheduling)
app.include_router(health_router)  # Comprehensive health monitoring (consolidated)
# app.include_router(analytics_router)     # ❌ REMOVED - analytics_microrouter merged into analytics_core_router (Phase 3A)
app.include_router(channels_router)  # Channel management (CRUD)
app.include_router(admin_channels_router)  # Admin - Channel Management
app.include_router(admin_users_router)  # Admin - User Management
app.include_router(admin_system_router)  # Admin - System Management

# ✅ PHASE 4: GRANULAR ANALYTICS DOMAIN ARCHITECTURE (NO GOD OBJECTS)
from apps.api.routers.analytics_alerts_router import router as analytics_alerts_router
from apps.api.routers.analytics_channels_router import router as analytics_channels_router
from apps.api.routers.analytics_live_router import router as analytics_live_router
from apps.api.routers.insights_engagement_router import router as insights_engagement_router
from apps.api.routers.insights_predictive_router import router as insights_predictive_router
from apps.api.routers.statistics_core_router import router as statistics_core_router
from apps.api.routers.statistics_reports_router import router as statistics_reports_router
from apps.demo.routers.main import router as demo_router

app.include_router(analytics_channels_router)  # Channel list for analytics - /analytics/channels
app.include_router(
    analytics_live_router
)  # Real-time live analytics (4 endpoints) - /analytics/live/*
app.include_router(analytics_alerts_router)  # Alert management (8 endpoints) - /analytics/alerts/*
app.include_router(
    statistics_core_router
)  # Historical statistics (5 endpoints) - /statistics/core/*
app.include_router(
    statistics_reports_router
)  # Statistical reports (4 endpoints) - /statistics/reports/*
app.include_router(
    insights_engagement_router
)  # Engagement intelligence (4 endpoints) - /insights/engagement/*
app.include_router(
    insights_predictive_router
)  # AI/ML predictions (4 endpoints) - /insights/predictive/*
app.include_router(ml_predictions_router)  # ML background predictions (growth forecasting) - /ml/*
app.include_router(demo_router)  # Consolidated demo/mock data endpoints

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
# ✅ KEEP THESE ROUTERS (No duplicates, still needed)
# ❌ REMOVED: clean_analytics_router - endpoints migrated to proper domain routers (Sept 24, 2025)
app.include_router(exports_router)  # Export functionality (unique)
app.include_router(sharing_router)  # Share functionality (unique)
app.include_router(mobile_router)  # Mobile-optimized endpoints (unique)
app.include_router(content_protection_router)  # Content protection (unique)
app.include_router(auth_router)  # Authentication (unique)
app.include_router(superadmin_router)  # Super admin operations (unique)
app.include_router(payment_router)  # Payment system (unique)

# Include AI services router
from apps.api.routers.ai_services_router import router as ai_services_router

app.include_router(ai_services_router)

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

# API DI Container initialized above in main.py
