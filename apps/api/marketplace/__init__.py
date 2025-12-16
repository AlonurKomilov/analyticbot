"""
Marketplace API Module
======================

API endpoints for marketplace operations:
- Item browsing and purchasing (themes, widgets, AI models, bundles)
- Service subscriptions (bot services, MTProto services)
- Credit management and gifting
- Reviews and ratings

Structure
---------
apps/api/marketplace/
├── router.py           # Main router aggregating all sub-routers
├── items_router.py     # One-time purchase items
├── services_router.py  # Subscription services
├── schemas.py          # Pydantic schemas for API
└── dependencies.py     # Marketplace-specific dependencies

Mount Point
-----------
All routes are mounted at /api/v1/marketplace/

Usage
-----
    # In main router
    from apps.api.marketplace import marketplace_router
    
    app.include_router(marketplace_router, prefix="/api/v1/marketplace")
"""

from apps.api.marketplace.router import marketplace_router
from apps.api.marketplace.schemas import (
    MarketplaceItemResponse,
    ItemPurchaseRequest,
    ItemPurchaseResponse,
    MarketplaceServiceResponse,
    ServiceSubscriptionRequest,
    ServiceSubscriptionResponse,
)

__all__ = [
    "marketplace_router",
    "MarketplaceItemResponse",
    "ItemPurchaseRequest",
    "ItemPurchaseResponse",
    "MarketplaceServiceResponse",
    "ServiceSubscriptionRequest",
    "ServiceSubscriptionResponse",
]
