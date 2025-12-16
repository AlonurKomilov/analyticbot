# Marketplace Module Migration Guide

## Overview

The marketplace functionality has been reorganized into a **vertical slice architecture** where all marketplace-related code is isolated in dedicated folders across each layer.

## New Structure

```
analyticbot/
├── core/marketplace/              # Business logic (domain layer)
│   ├── __init__.py
│   ├── domain/
│   │   ├── entities.py            # Domain entities (dataclasses)
│   │   └── value_objects.py       # Value objects (immutable)
│   ├── ports/
│   │   └── __init__.py            # Interface definitions
│   └── services/
│       ├── marketplace_service.py # Main marketplace business logic
│       └── feature_gate_service.py # Feature access control
│
├── infra/marketplace/             # Data access (infrastructure layer)
│   ├── __init__.py
│   └── repositories/
│       ├── items.py               # Item repository (themes, widgets)
│       └── services.py            # Service subscription repository
│
├── apps/api/marketplace/          # HTTP API (application layer)
│   ├── __init__.py
│   ├── router.py                  # Main router aggregating sub-routers
│   ├── items_router.py            # Item endpoints
│   ├── services_router.py         # Service subscription endpoints
│   ├── schemas.py                 # Pydantic request/response models
│   └── dependencies.py            # FastAPI dependency injection
│
└── apps/frontend/apps/user/src/features/marketplace/  # Frontend
    ├── index.ts                   # Main exports
    ├── types/                     # TypeScript types
    ├── api/                       # API client functions
    │   ├── items.ts
    │   ├── services.ts
    │   └── credits.ts
    ├── hooks/                     # React hooks
    │   ├── useMarketplaceItems.ts
    │   ├── useUserServices.ts
    │   ├── useCreditBalance.ts
    │   └── useServiceAccess.ts
    ├── components/                # Reusable components
    │   ├── common/                # Shared components
    │   └── cards/                 # Card components
    ├── pages/                     # Page re-exports
    ├── services/                  # Service registry
    │   └── registry.tsx
    └── utils/                     # Utilities
        ├── categoryConfig.ts
        └── priceFormatter.ts
```

## Migration Steps

### 1. Backend Imports

#### Old Import Pattern (deprecated)
```python
# DON'T use these anymore
from infra.db.repositories.marketplace_repository import MarketplaceRepository
from infra.db.repositories.marketplace_service_repository import MarketplaceServiceRepository
from core.services.marketplace_service import MarketplaceService
```

#### New Import Pattern
```python
# USE THESE
from infra.marketplace.repositories import MarketplaceItemRepository, MarketplaceServiceRepository
from core.marketplace.services import MarketplaceService, FeatureGateService
from core.marketplace.domain import MarketplaceItem, ServiceSubscription
from apps.api.marketplace import marketplace_router
```

### 2. API Routes

#### Old Route Registration
```python
# In apps/api/routers.py or similar
from apps.api.marketplace_router import router as marketplace_router
app.include_router(marketplace_router, prefix="/api/v1")
```

#### New Route Registration
```python
# In apps/api/routers.py
from apps.api.marketplace import marketplace_router
app.include_router(marketplace_router, prefix="/api/v1")
# Routes will be at /api/v1/marketplace/*
```

### 3. Frontend Imports

#### Old Import Pattern (deprecated)
```typescript
// DON'T use these anymore
import { MarketplaceCard } from '@/pages/marketplace/components/MarketplaceCard';
import { useMarketplaceData } from '@/pages/marketplace/hooks/useMarketplaceData';
import { SERVICE_REGISTRY } from '@/features/marketplace/registry';
```

#### New Import Pattern
```typescript
// USE THESE - import from feature root
import { 
  MarketplaceCard,
  useMarketplaceItems,
  useCreditBalance,
  SERVICE_REGISTRY,
  getServiceIcon,
} from '@/features/marketplace';
```

### 4. Dependency Injection

#### Backend DI Container
Update your DI container to use the new paths:

```python
# In apps/di/container.py
from core.marketplace.services import MarketplaceService, FeatureGateService
from infra.marketplace.repositories import MarketplaceItemRepository, MarketplaceServiceRepository

class Container:
    @property
    def marketplace_item_repo(self) -> MarketplaceItemRepository:
        return MarketplaceItemRepository(self.db_pool)
    
    @property  
    def marketplace_service_repo(self) -> MarketplaceServiceRepository:
        return MarketplaceServiceRepository(self.db_pool)
    
    @property
    def marketplace_service(self) -> MarketplaceService:
        return MarketplaceService(
            item_repo=self.marketplace_item_repo,
            service_repo=self.marketplace_service_repo,
        )
```

## API Endpoints

All marketplace endpoints are now under `/api/v1/marketplace/`:

### Items (One-time Purchases)
- `GET /api/v1/marketplace/items` - Browse items
- `GET /api/v1/marketplace/items/{slug}` - Get item details
- `POST /api/v1/marketplace/items/purchase` - Purchase item
- `GET /api/v1/marketplace/purchases` - User's purchases
- `POST /api/v1/marketplace/items/review` - Add review
- `GET /api/v1/marketplace/bundles` - Get bundles
- `POST /api/v1/marketplace/bundles/purchase` - Purchase bundle
- `POST /api/v1/marketplace/gift` - Send credits

### Services (Subscriptions)
- `GET /api/v1/marketplace/services` - Browse services
- `GET /api/v1/marketplace/services/{service_key}` - Get service details
- `POST /api/v1/marketplace/services/subscribe` - Subscribe
- `GET /api/v1/marketplace/subscriptions` - User's subscriptions
- `POST /api/v1/marketplace/subscriptions/cancel` - Cancel subscription
- `GET /api/v1/marketplace/access/{service_key}` - Check access
- `GET /api/v1/marketplace/features` - Get user's features

## Testing

Run marketplace tests:
```bash
pytest apps/tests/marketplace/ -v
pytest core/tests/marketplace/ -v
```

## Cleanup Tasks

After migration is complete, these old files can be removed:

### Backend (to be deprecated)
- `infra/db/repositories/marketplace_repository.py`
- `infra/db/repositories/marketplace_service_repository.py`
- Old marketplace routes in `apps/api/` (if any)

### Frontend (to be deprecated)
- `apps/frontend/apps/user/src/pages/marketplace/` (moved to features)
- Old hook files in `src/hooks/` related to marketplace

## Backward Compatibility

The feature maintains backward compatibility through re-exports:

```typescript
// Old code still works (but triggers deprecation warnings)
import { SERVICE_CONFIG_MAP } from '@/features/marketplace';
// New preferred way
import { SERVICE_REGISTRY, getServiceConfigComponent } from '@/features/marketplace';
```

## Adding New Marketplace Items

See [MARKETPLACE_DEVELOPER_GUIDE.md](./MARKETPLACE_DEVELOPER_GUIDE.md) for details on adding new items/services to the marketplace.
