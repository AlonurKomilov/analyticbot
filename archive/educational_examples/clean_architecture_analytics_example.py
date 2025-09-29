"""
🎓 EDUCATIONAL EXAMPLE: Clean Architecture Analytics Router
==========================================================

📚 PURPOSE: Educational reference for clean architecture patterns in FastAPI

🚀 MIGRATION STATUS: COMPLETED ✅
   - All endpoints migrated to proper domain routers (Sept 24, 2025)
   - File archived as educational example

🔄 ENDPOINT MIGRATION MAPPING:
   Original → New Location
   ========================================
   ❌ /channels/{channel_id}/metrics      → SKIPPED (duplicate in analytics_core_router.py)
   ✅ /channels/{channel_id}/engagement   → channels_microrouter.py
   ✅ /channels/{channel_id}/audience     → channels_microrouter.py
   ✅ /channels/{channel_id}/best-times   → analytics_predictive_router.py
   ✅ /service-info                       → core_microrouter.py

🎯 CLEAN ARCHITECTURE PATTERNS DEMONSTRATED:

   1. ✅ DEPENDENCY INJECTION
      - Service abstraction via protocols
      - Container-based service resolution
      - Mock vs. real service switching

   2. ✅ SEPARATION OF CONCERNS
      - Router handles HTTP concerns only
      - Business logic delegated to services
      - Clean error handling patterns

   3. ✅ DEPENDENCY INVERSION PRINCIPLE
      - Depends on abstractions (AnalyticsServiceProtocol)
      - Not concretions (specific service implementations)
      - Easy to extend without modification

   4. ✅ SINGLE RESPONSIBILITY PRINCIPLE
      - Each endpoint has single purpose
      - Clean, focused business logic
      - Proper error boundaries

📖 EDUCATIONAL VALUE:
   - Shows proper FastAPI + Clean Architecture integration
   - Demonstrates dependency injection in API routes
   - Examples of service abstraction patterns
   - Clean error handling and logging practices

🔗 RELATED EXAMPLES:
   - Phase 3B Analytics Architecture: apps/api/routers/analytics_*_router.py
   - Microrouter Pattern: apps/api/routers/*_microrouter.py
   - DI Container: core/di_container.py
   - Service Protocols: core/protocols.py

Domain: Clean architecture patterns, unique analytics functionality
Path: /clean/analytics/* (LEGACY - endpoints migrated)
Status: 🏛️ ARCHIVED FOR EDUCATIONAL REFERENCE
"""

import logging

from core.di_container import container
from fastapi import APIRouter, Depends, HTTPException

from config.settings import settings
from core.protocols import AnalyticsServiceProtocol

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clean/analytics", tags=["Clean Architecture Analytics"])


def get_analytics_service() -> AnalyticsServiceProtocol:
    """
    Dependency injection for analytics service
    Clean Architecture: Depend on abstractions, not concretions
    """
    try:
        return container.get_service(AnalyticsServiceProtocol)
    except ValueError as e:
        logger.error(f"Failed to get analytics service: {e}")
        raise HTTPException(status_code=500, detail="Analytics service not available")


@router.get("/channels/{channel_id}/metrics")
async def get_channel_metrics(
    channel_id: str,
    period: str = "7d",
    analytics_service: AnalyticsServiceProtocol = Depends(get_analytics_service),
):
    """
    Get channel analytics metrics
    ✅ Clean: Service injected via DI, no mock imports
    ❌ Old way: if is_demo_user(): import mock_analytics
    """
    try:
        metrics = await analytics_service.get_channel_metrics(channel_id, period)
        return {"success": True, "data": metrics}
    except Exception as e:
        logger.error(f"Failed to get channel metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/channels/{channel_id}/engagement")
async def get_engagement_data(
    channel_id: str,
    period: str = "24h",
    analytics_service: AnalyticsServiceProtocol = Depends(get_analytics_service),
):
    """
    Get channel engagement data
    ✅ Clean: Service abstraction handles mock/real switching
    """
    try:
        engagement = await analytics_service.get_engagement_data(channel_id, period)
        return {"success": True, "data": engagement}
    except Exception as e:
        logger.error(f"Failed to get engagement data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/channels/{channel_id}/best-times")
async def get_best_posting_times(
    channel_id: str,
    analytics_service: AnalyticsServiceProtocol = Depends(get_analytics_service),
):
    """
    Get optimal posting times
    ✅ Clean: Dependency inversion principle applied
    """
    try:
        best_times = await analytics_service.get_best_posting_times(channel_id)
        return {"success": True, "data": best_times}
    except Exception as e:
        logger.error(f"Failed to get best posting times: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/channels/{channel_id}/audience")
async def get_audience_insights(
    channel_id: str,
    analytics_service: AnalyticsServiceProtocol = Depends(get_analytics_service),
):
    """
    Get audience demographics and insights
    ✅ Clean: Open/closed principle - easy to extend without modification
    """
    try:
        insights = await analytics_service.get_audience_insights(channel_id)
        return {"success": True, "data": insights}
    except Exception as e:
        logger.error(f"Failed to get audience insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service-info")
async def get_service_info(
    analytics_service: AnalyticsServiceProtocol = Depends(get_analytics_service),
):
    """
    Get information about the current analytics service
    Helpful for debugging and monitoring
    """
    try:
        return {
            "service_name": analytics_service.get_service_name(),
            "demo_mode_enabled": settings.demo_mode.is_demo_enabled(),
            "using_mock_analytics": settings.demo_mode.should_use_mock_service("analytics"),
            "configuration": {
                "strategy": settings.demo_mode.DEMO_MODE_STRATEGY,
                "mock_delay_ms": settings.demo_mode.MOCK_API_DELAY_MS,
            },
        }
    except Exception as e:
        logger.error(f"Failed to get service info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
