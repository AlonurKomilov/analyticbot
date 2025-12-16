"""
Marketplace Services Router
===========================

API endpoints for marketplace services (subscriptions):
- Browse service catalog
- Subscribe to services
- Manage subscriptions
- Usage tracking
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from apps.api.dependencies import CurrentUser
from apps.api.marketplace.schemas import (
    MarketplaceServiceResponse,
    ServiceCatalogResponse,
    ServiceSubscriptionRequest,
    ServiceSubscriptionResponse,
    UserSubscriptionsResponse,
    CancelSubscriptionRequest,
    ToggleAutoRenewRequest,
    SuccessResponse,
)
from apps.api.marketplace.dependencies import (
    MarketplaceServiceRepoDep,
    MarketplaceServiceDep,
    FeatureGateServiceDep,
)

router = APIRouter(tags=["marketplace-services"])


# =============================================================================
# SERVICE CATALOG
# =============================================================================

@router.get("/services", response_model=ServiceCatalogResponse)
async def get_service_catalog(
    service: MarketplaceServiceDep,
    current_user: CurrentUser,
    category: Optional[str] = Query(None, description="Filter by category (bot_service, mtproto_services, ai_services)"),
):
    """Get marketplace service catalog."""
    services = await service.get_service_catalog(
        category=category,
        user_id=current_user.id if current_user else None,
    )
    return {
        "services": services,
        "total": len(services),
    }


@router.get("/services/featured", response_model=list[MarketplaceServiceResponse])
async def get_featured_services(
    service: MarketplaceServiceDep,
    limit: int = Query(5, le=20),
):
    """Get featured services."""
    return await service.get_featured_services(limit=limit)


@router.get("/services/{service_key}", response_model=MarketplaceServiceResponse)
async def get_service_details(
    service_key: str,
    service: MarketplaceServiceDep,
    current_user: CurrentUser,
):
    """Get detailed information about a specific service."""
    details = await service.get_service_details(
        service_key=service_key,
        user_id=current_user.id if current_user else None,
    )
    
    if not details:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return details


# =============================================================================
# SUBSCRIPTIONS
# =============================================================================

@router.post("/services/subscribe", response_model=ServiceSubscriptionResponse)
async def subscribe_to_service(
    request: ServiceSubscriptionRequest,
    service: MarketplaceServiceDep,
    current_user: CurrentUser,
):
    """Subscribe to a marketplace service."""
    try:
        subscription = await service.purchase_service(
            user_id=current_user.id,
            service_key=request.service_key,
            billing_cycle=request.billing_cycle,
        )
        return subscription
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscriptions", response_model=UserSubscriptionsResponse)
async def get_user_subscriptions(
    service: MarketplaceServiceDep,
    current_user: CurrentUser,
    include_expired: bool = Query(False),
):
    """Get user's service subscriptions."""
    subscriptions = await service.get_user_subscriptions(
        user_id=current_user.id,
        include_expired=include_expired,
    )
    return {"subscriptions": subscriptions}


@router.get("/subscriptions/active")
async def get_active_subscriptions(
    service: MarketplaceServiceDep,
    current_user: CurrentUser,
):
    """Get user's active service subscriptions (convenience endpoint)."""
    subscriptions = await service.get_user_subscriptions(
        user_id=current_user.id,
        include_expired=False,
    )
    # Filter to only active
    active = [s for s in subscriptions if s.get("status") == "active"]
    return {"subscriptions": active}


@router.post("/subscriptions/cancel", response_model=SuccessResponse)
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    service: MarketplaceServiceDep,
    current_user: CurrentUser,
):
    """Cancel a subscription."""
    try:
        await service.cancel_subscription(
            user_id=current_user.id,
            subscription_id=request.subscription_id,
            reason=request.reason,
        )
        return {"success": True, "message": "Subscription cancelled"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscriptions/auto-renew", response_model=SuccessResponse)
async def toggle_auto_renew(
    request: ToggleAutoRenewRequest,
    service: MarketplaceServiceDep,
    current_user: CurrentUser,
):
    """Toggle auto-renewal for a subscription."""
    try:
        await service.toggle_auto_renew(
            user_id=current_user.id,
            subscription_id=request.subscription_id,
            auto_renew=request.auto_renew,
        )
        return {
            "success": True,
            "message": f"Auto-renewal {'enabled' if request.auto_renew else 'disabled'}",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# FEATURE ACCESS
# =============================================================================

@router.get("/access/{service_key}")
async def check_service_access(
    service_key: str,
    feature_gate: FeatureGateServiceDep,
    current_user: CurrentUser,
):
    """Check if user has access to a specific service."""
    has_access = await feature_gate.check_access(current_user.id, service_key)
    return {
        "service_key": service_key,
        "has_access": has_access,
    }


@router.get("/access/{service_key}/quota")
async def check_service_quota(
    service_key: str,
    feature_gate: FeatureGateServiceDep,
    current_user: CurrentUser,
    check_type: str = Query("daily", pattern="^(daily|monthly)$"),
):
    """Check quota status for a service."""
    quota = await feature_gate.check_quota(
        user_id=current_user.id,
        service_key=service_key,
        check_type=check_type,
    )
    return quota


@router.get("/features")
async def get_user_features(
    feature_gate: FeatureGateServiceDep,
    current_user: CurrentUser,
):
    """Get list of all services user has access to."""
    features = await feature_gate.get_user_features(current_user.id)
    return {"features": features}


# =============================================================================
# USAGE TRACKING
# =============================================================================

@router.get("/subscriptions/{subscription_id}/usage")
async def get_subscription_usage(
    subscription_id: int,
    service: MarketplaceServiceDep,
    current_user: CurrentUser,
    days: int = Query(30, le=90),
):
    """Get usage statistics for a subscription."""
    # TODO: Verify subscription belongs to user
    stats = await service.get_subscription_usage_stats(
        subscription_id=subscription_id,
        days=days,
    )
    return stats
