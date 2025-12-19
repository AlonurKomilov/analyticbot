"""
Marketplace Module
==================

This module contains all marketplace-related business logic, including:
- Item management (themes, widgets, AI models, bundles)
- Service subscriptions (bot services, MTProto services)
- Feature gating and access control
- Usage tracking and quotas

Structure
---------
core/marketplace/
├── domain/           # Domain entities and value objects
├── services/         # Business logic services
│   ├── bot_services/     # Bot marketplace service implementations
│   └── mtproto_services/ # MTProto marketplace service implementations
├── ports/            # Interface definitions (ports)
└── adapters/         # External adapters

Usage
-----
    from core.marketplace import MarketplaceService, FeatureGateService
    from core.marketplace.domain import MarketplaceItem, ServiceSubscription
    from core.marketplace.services.bot_services import AntiSpamService

Related Modules
---------------
- infra/marketplace/   - Database repositories and infrastructure
- apps/api/marketplace/ - API endpoints and schemas
"""

from core.marketplace.services.feature_gate_service import FeatureGateService
from core.marketplace.services.marketplace_service import MarketplaceService

__all__ = [
    "MarketplaceService",
    "FeatureGateService",
]
