"""
Predictive insights router aggregation.

This module combines all predictive analytics and intelligence sub-routers
into a single unified router for the main application.
"""

from fastapi import APIRouter

from . import recommendations, intelligence


# Create main insights_predictive router
router = APIRouter(prefix="/insights/predictive", tags=["insights-predictive"])

# Include all sub-routers
router.include_router(recommendations.router)
router.include_router(intelligence.router)
