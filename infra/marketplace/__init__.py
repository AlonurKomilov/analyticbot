"""
Marketplace Infrastructure Module
=================================

Infrastructure components for the marketplace feature:
- Database repositories
- Redis caching (if needed)
- External service adapters

Structure
---------
infra/marketplace/
├── repositories/       # Database access
│   ├── items.py       # One-time purchase items repository
│   └── services.py    # Subscription services repository
├── adapters/          # External service adapters
└── cache/             # Redis caching utilities

Usage
-----
    from infra.marketplace import (
        MarketplaceItemRepository,
        MarketplaceServiceRepository,
    )
    
    # Or use through dependency injection
    from apps.di import get_marketplace_item_repo, get_marketplace_service_repo

Database Tables
---------------
- marketplace_items         - One-time purchase items catalog
- marketplace_services      - Subscription services catalog
- user_purchases           - Item purchase records
- user_service_subscriptions - Service subscription records
- user_reviews             - Item reviews
- service_usage_log        - Service usage tracking
"""

from infra.marketplace.repositories.items import MarketplaceItemRepository
from infra.marketplace.repositories.services import MarketplaceServiceRepository

__all__ = [
    "MarketplaceItemRepository",
    "MarketplaceServiceRepository",
]
