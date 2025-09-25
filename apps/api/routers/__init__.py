"""
FastAPI Routers Package - Clean Analytics Architecture

This package contains all the modular routers for the analyticbot API.
Each router handles a single domain responsibility following Clean Architecture principles.

Phase 3B Complete (Sept 24, 2025) - Clean 5-Router Analytics Architecture:
- analytics_core_router: Core analytics (dashboard, metrics, overview, trends)
- analytics_realtime_router: Real-time analytics and live monitoring
- analytics_alerts_router: Alert management and notifications
- analytics_insights_router: Advanced insights, reports, and system analysis
- analytics_predictive_router: AI/ML predictions, forecasting, and advanced analysis
"""

# ✅ PHASE 3B: CLEAN ANALYTICS ARCHITECTURE
from .analytics_core_router import router as analytics_core_router
from .analytics_realtime_router import router as analytics_realtime_router
from .analytics_alerts_router import router as analytics_alerts_router
from .analytics_insights_router import router as analytics_insights_router
from .analytics_predictive_router import router as analytics_predictive_router

# Other domain routers - FIXED: Updated to match renamed files
from .channels_router import router as channels_router
from .admin_router import router as admin_router
from .system_router import router as system_router
from .auth_router import router as auth_router
from .health_system_router import router as health_system_router
from .demo_router import router as demo_router
from .exports_router import router as exports_router
from .sharing_router import router as sharing_router
from .mobile_router import router as mobile_router
from .superadmin_router import router as superadmin_router
from .ai_services import router as ai_services_router

__all__ = [
    # Phase 3B: Clean Analytics Architecture
    "analytics_core_router",
    "analytics_realtime_router",
    "analytics_alerts_router", 
    "analytics_insights_router",
    "analytics_predictive_router",
    # Other domain routers - FIXED: Updated names
    "channels_router", 
    "admin_router",
    "system_router",
    "auth_router",
    "health_system_router",
    "demo_router",
    "exports_router", 
    "sharing_router",
    "mobile_router",
    "superadmin_router",
    "ai_services_router"
]
