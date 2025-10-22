"""
Authentication router aggregation.

This module combines all authentication sub-routers into a single
unified router for the main application.
"""

from fastapi import APIRouter

from . import login, password, profile, registration

# Create main auth router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Include all sub-routers
router.include_router(login.router)
router.include_router(registration.router)
router.include_router(password.router)
router.include_router(profile.router)
