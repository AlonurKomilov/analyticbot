"""
FastAPI Routers Package - Granular Analytics Architecture

This package contains all the modular routers for the analyticbot API.
Each router handles a single domain responsibility following Clean Architecture principles.

Phase 4 Complete (Sept 25, 2025) - Granular 6-Router Analytics Architecture (No God Objects):
- analytics_live_router: Real-time live analytics (4 endpoints)
- analytics_alerts_router: Alert management and notifications (8 endpoints)
- statistics_core_router: Historical statistics and core metrics (5 endpoints)
- statistics_reports_router: Statistical reports and comparisons (4 endpoints)
- insights_engagement_router: Engagement intelligence and audience insights (4 endpoints)
- insights_predictive_router: AI/ML predictions and forecasting (4 endpoints)

PERFECT CLEAN ARCHITECTURE: No god objects, clear domain boundaries, focused responsibilities.
"""

# ✅ PHASE 4: GRANULAR ANALYTICS ARCHITECTURE (NO GOD OBJECTS)
from apps.demo.routers.main import router as demo_router

from .admin_channels_router import router as admin_channels_router
from .admin_system_router import router as admin_system_router
from .admin_users_router import router as admin_users_router

# Phase 2 New Routers (Oct 22, 2025)
from .ai_chat_router import router as ai_chat_router
from .ai_insights_router import router as ai_insights_router
from .ai_services_router import router as ai_services_router
from .analytics_alerts_router import router as analytics_alerts_router
from .analytics_live_router import router as analytics_live_router
from .auth.router import router as auth_router
from .competitive_intelligence_router import router as competitive_intelligence_router

# Other domain routers - FIXED: Updated to match renamed files
from .channels_router import router as channels_router
from .exports_router import router as exports_router
from .health_router import router as health_router
from .insights_engagement_router import router as insights_engagement_router
from .mobile_router import router as mobile_router
from .optimization_router import router as optimization_router
from .sharing_router import router as sharing_router
from .statistics_core_router import router as statistics_core_router
from .statistics_reports_router import router as statistics_reports_router
from .strategy_router import router as strategy_router

# Re-enabled after fixing dependencies and imports
from .superadmin_router import router as superadmin_router
from .system_router import router as system_router
from .trend_analysis_router import router as trend_analysis_router

__all__ = [
    # Phase 4: Granular Analytics Architecture (No God Objects)
    "analytics_live_router",  # Real-time live analytics (4 endpoints)
    "analytics_alerts_router",  # Alert management (8 endpoints)
    "statistics_core_router",  # Historical statistics (5 endpoints)
    "statistics_reports_router",  # Statistical reports (4 endpoints)
    "insights_engagement_router",  # Engagement intelligence (4 endpoints)
    # Phase 2 New Routers (Oct 22, 2025)
    "ai_chat_router",  # AI chat orchestration
    "ai_insights_router",  # AI insights and predictions
    "competitive_intelligence_router",  # Competitive analysis
    "optimization_router",  # Content optimization
    "strategy_router",  # Strategy recommendations
    "trend_analysis_router",  # Trend detection and forecasting
    # Other domain routers
    "channels_router",
    "admin_channels_router",
    "admin_users_router",
    "admin_system_router",
    "system_router",
    "auth_router",
    "health_router",
    "demo_router",
    "exports_router",
    "sharing_router",
    "mobile_router",
    "superadmin_router",  # Re-enabled after dependency fixes
    "ai_services_router",  # Re-enabled after textstat dependency resolved
]
