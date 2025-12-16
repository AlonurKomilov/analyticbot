"""
Marketplace API Dependencies
============================

Dependency injection for marketplace API endpoints.
"""

from typing import Annotated
from fastapi import Depends

from apps.di import get_container
from infra.marketplace import MarketplaceItemRepository, MarketplaceServiceRepository
from core.marketplace import MarketplaceService, FeatureGateService


async def get_marketplace_item_repo() -> MarketplaceItemRepository:
    """Get marketplace item repository from DI container"""
    container = get_container()
    pool = await container.db_pool()
    return MarketplaceItemRepository(pool)


async def get_marketplace_service_repo() -> MarketplaceServiceRepository:
    """Get marketplace service repository from DI container"""
    container = get_container()
    pool = await container.db_pool()
    return MarketplaceServiceRepository(pool)


async def get_marketplace_service() -> MarketplaceService:
    """Get marketplace business service from DI container"""
    container = get_container()
    return await container.marketplace_service()


async def get_feature_gate_service() -> FeatureGateService:
    """Get feature gate service from DI container"""
    container = get_container()
    return await container.feature_gate_service()


# Type aliases for dependency injection
MarketplaceItemRepoDep = Annotated[MarketplaceItemRepository, Depends(get_marketplace_item_repo)]
MarketplaceServiceRepoDep = Annotated[MarketplaceServiceRepository, Depends(get_marketplace_service_repo)]
MarketplaceServiceDep = Annotated[MarketplaceService, Depends(get_marketplace_service)]
FeatureGateServiceDep = Annotated[FeatureGateService, Depends(get_feature_gate_service)]
