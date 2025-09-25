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
# ✅ NEW MICROROUTER ARCHITECTURE
# analytics_microrouter merged into analytics_core_router (Phase 3A consolidation)
from apps.api.routers.channels_router import router as channels_router
from apps.api.routers.admin_channels_router import router as admin_channels_router
from apps.api.routers.admin_users_router import router as admin_users_router  
from apps.api.routers.admin_system_router import router as admin_system_router
from apps.api.routers.system_router import router as system_router
from apps.api.routers.health_router import router as health_router
# Legacy routers (keeping for compatibility during transition)
# DEPRECATED ROUTERS REMOVED - cleanup
from apps.api.routers.exports_router import router as exports_router
from apps.api.routers.sharing_router import router as sharing_router
from apps.api.routers.mobile_router import router as mobile_router
from apps.api.routers.auth_router import router as auth_router
from apps.api.routers.superadmin_router import router as superadmin_router
from apps.bot.api.content_protection_router import router as content_protection_router
from apps.bot.api.payment_router import router as payment_router
from apps.bot.models.twa import InitialDataResponse, User, Plan, Channel, ScheduledPost
from config import settings
from core import DeliveryService, ScheduleService
from infra.db.connection_manager import close_database, init_database
# ✅ PRODUCTION READY: No more direct mock imports
# Demo services now injected via DI container based on configuration

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events - now with proper DI container management"""
    # Startup - Initialize database and DI container
    try:
        await init_database()
        logger.info("Database initialized successfully")
        
        # ✅ NEW: Initialize DI container with proper asyncpg pool
        from apps.shared.di import init_container, Settings as DISettings
        di_settings = DISettings(
            database_url=settings.DATABASE_URL,
            database_pool_size=settings.DB_POOL_SIZE,
            database_max_overflow=settings.DB_MAX_OVERFLOW
        )
        di_container = init_container(di_settings)
        
        # Pre-initialize asyncpg pool to ensure it's ready
        pool = await di_container.asyncpg_pool()
        logger.info(f"✅ Asyncpg pool initialized with {pool.get_min_size()}-{pool.get_max_size()} connections")
        
    except Exception as e:
        logger.error(f"Startup initialization failed: {e}")
        # Continue without database for now to allow health checks
    yield
    # Shutdown - Cleanup database and DI container
    try:
        await close_database()
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
from core.di_container import container, configure_services
app.add_middleware(DemoModeMiddleware)

# ✅ NEW MICROROUTER ARCHITECTURE - Domain-Focused Routing
app.include_router(system_router)        # Core system operations (performance, scheduling) 
app.include_router(health_router)        # Comprehensive health monitoring (consolidated)
# app.include_router(analytics_router)     # ❌ REMOVED - analytics_microrouter merged into analytics_core_router (Phase 3A)
app.include_router(channels_router)      # Channel management (CRUD)
app.include_router(admin_channels_router)   # Admin - Channel Management
app.include_router(admin_users_router)      # Admin - User Management
app.include_router(admin_system_router)     # Admin - System Management

# ✅ PHASE 3: NEW ANALYTICS DOMAIN ARCHITECTURE
from apps.api.routers.analytics_core_router import router as analytics_core_router
from apps.api.routers.analytics_realtime_router import router as analytics_realtime_router  
from apps.api.routers.analytics_alerts_router import router as analytics_alerts_router
from apps.api.routers.analytics_insights_router import router as analytics_insights_router
from apps.api.routers.analytics_predictive_router import router as analytics_predictive_router
from apps.api.routers.demo_router import router as demo_router

app.include_router(analytics_core_router)     # Core analytics functionality (dashboard, metrics, overview, trends, refresh)
app.include_router(analytics_realtime_router) # Real-time analytics and live monitoring
app.include_router(analytics_alerts_router)   # Alert management and notifications
app.include_router(analytics_insights_router) # Advanced insights, reports, and system analysis
app.include_router(analytics_predictive_router) # AI/ML predictions, forecasting, and advanced data analysis
app.include_router(demo_router)               # Consolidated demo/mock data endpoints

# 🚨 PHASE 3B: ANALYTICS CONSOLIDATION COMPLETE ✅
# ALL legacy analytics routers successfully consolidated into clean 5-router architecture:
# - analytics_v2_router         → MIGRATED to analytics_core_router + analytics_insights_router (ARCHIVED)
# - analytics_advanced_router   → SUPERSEDED by analytics_realtime_router + analytics_alerts_router (ARCHIVED)
# - analytics_microrouter        → SPLIT into analytics_core_router + analytics_predictive_router (ARCHIVED)
# - analytics_unified_router    → MIGRATED to analytics_insights_router (ARCHIVED)
# 
# Current Clean Architecture: 5 Domain-Separated Analytics Routers
# 1. Core: Dashboard, metrics, overview, trends, top-posts, sources, refresh
# 2. Realtime: Live metrics, performance scoring, monitoring, recommendations
# 3. Alerts: Thresholds, notifications, alert management, monitoring
# 4. Insights: Advanced reports, capabilities, comparisons, channel-data, performance-metrics, trends
# 5. Predictive: AI/ML insights, forecasting, advanced analysis, predictions
# app.include_router(analytics_v2_router)      # ❌ REMOVED: Use /analytics/core/* + /analytics/insights/* instead
# app.include_router(analytics_advanced_router) # ❌ REMOVED: Use /analytics/realtime/* + /analytics/alerts/* instead
# ✅ KEEP THESE ROUTERS (No duplicates, still needed)
# ❌ REMOVED: clean_analytics_router - endpoints migrated to proper domain routers (Sept 24, 2025)
app.include_router(exports_router)            # Export functionality (unique)
app.include_router(sharing_router)            # Share functionality (unique)  
app.include_router(mobile_router)             # Mobile-optimized endpoints (unique)
app.include_router(content_protection_router) # Content protection (unique)
app.include_router(auth_router)               # Authentication (unique)
app.include_router(superadmin_router)         # Super admin operations (unique)
app.include_router(payment_router)            # Payment system (unique)

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
# 
# ✅ CLEAN ARCHITECTURE BENEFITS ACHIEVED:
# - Single Responsibility Principle: Each router has one focused domain
# - Domain Separation: Clear boundaries between business domains  
# - Maintainability: Easy to understand, modify, and test each domain
# - Scalability: New features can be added to appropriate domains


# Initialize DI Container immediately
try:
    configure_services(container, settings.demo_mode)
    logger.info("✅ DI Container initialized successfully")
    
    # Log service configuration
    services = container.get_registered_services()
    logger.info(f"📋 Registered services: {services}")
    
except Exception as e:
    logger.error(f"❌ Failed to initialize DI container: {e}")
    # Continue without DI container for now
