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
from .analytics_live_router import router as analytics_live_router
from .analytics_alerts_router import router as analytics_alerts_router
from .statistics_core_router import router as statistics_core_router
from .statistics_reports_router import router as statistics_reports_router
from .insights_engagement_router import router as insights_engagement_router
from .insights_predictive_router import router as insights_predictive_router

# Other domain routers - FIXED: Updated to match renamed files
from .channels_router import router as channels_router
from .admin_channels_router import router as admin_channels_router
from .admin_users_router import router as admin_users_router
from .admin_system_router import router as admin_system_router
from .system_router import router as system_router
from .auth_router import router as auth_router
from .health_router import router as health_router
from .demo_router import router as demo_router
from .exports_router import router as exports_router
from .sharing_router import router as sharing_router
from .mobile_router import router as mobile_router
from .superadmin_router import router as superadmin_router
from .ai_services_router import router as ai_services_router

__all__ = [
    # Phase 4: Granular Analytics Architecture (No God Objects)
    "analytics_live_router",          # Real-time live analytics (4 endpoints)
    "analytics_alerts_router",        # Alert management (8 endpoints)
    "statistics_core_router",         # Historical statistics (5 endpoints)
    "statistics_reports_router",      # Statistical reports (4 endpoints)
    "insights_engagement_router",     # Engagement intelligence (4 endpoints)
    "insights_predictive_router",     # AI/ML predictions (4 endpoints)
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
    "superadmin_router",
    "ai_services_router"
]
