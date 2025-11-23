"""
Channels Microservice Router

Aggregates all channel management endpoints.

Structure:
- admin_status.py: Bot/MTProto admin status verification
- validation.py: Channel validation before creation
- crud.py: CRUD operations (list, create, read, update, delete)
- lifecycle.py: Activate/deactivate channels
- status.py: Channel status and statistics
"""

from fastapi import APIRouter

from . import admin_status, crud, lifecycle, status, validation

# Create main router
router = APIRouter(
    tags=["Channel Management"],
    responses={404: {"description": "Not found"}},
)

# Include all sub-routers
router.include_router(admin_status.router)
router.include_router(validation.router)
router.include_router(crud.router, prefix="")
router.include_router(lifecycle.router)
router.include_router(status.router)
