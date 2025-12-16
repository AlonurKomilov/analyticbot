"""
Marketplace API Router
======================

Main router that aggregates all marketplace sub-routers:
- /items - One-time purchase items (themes, widgets)
- /services - Subscription services

Mount this at /api/v1/marketplace/
"""

from fastapi import APIRouter

from apps.api.marketplace.items_router import router as items_router
from apps.api.marketplace.services_router import router as services_router

# Main marketplace router
marketplace_router = APIRouter(prefix="/marketplace")

# Include sub-routers
marketplace_router.include_router(items_router)
marketplace_router.include_router(services_router)

# Re-export for convenience
__all__ = ["marketplace_router"]
