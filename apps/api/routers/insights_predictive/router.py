"""
Predictive insights router aggregation.

This module combines all predictive analytics and intelligence sub-routers
into a single unified router for the main application.
"""

from fastapi import APIRouter

from . import intelligence, recommendations

# Create main insights_predictive router
# ✅ FIXED: Removed prefix - now configured in main.py
router = APIRouter(tags=["insights-predictive"])

# Include all sub-routers
router.include_router(recommendations.router)
router.include_router(intelligence.router)
