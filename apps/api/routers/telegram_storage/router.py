"""
Storage Microservice Router

Aggregates all storage-related endpoints: channels and files.
"""

from fastapi import APIRouter

from . import channels, files

router = APIRouter(
    prefix="/storage",
    tags=["Telegram Storage"],
    responses={404: {"description": "Not found"}},
)

# Include sub-routers
router.include_router(channels.router)
router.include_router(files.router)
