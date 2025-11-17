"""
User MTProto Router Aggregation

This module combines all user MTProto sub-routers into a single
unified router for the main application.
"""

from fastapi import APIRouter

from . import channel_settings, connection, setup, status, toggle, verification

# Create main user_mtproto router
router = APIRouter(
    prefix="/api/user-mtproto",
    tags=["User MTProto Management"],
)

# Include all sub-routers
router.include_router(status.router)
router.include_router(setup.router)
router.include_router(verification.router)
router.include_router(connection.router)
router.include_router(toggle.router)
router.include_router(channel_settings.router)
