"""
🛒 Service Subscriptions API Router

Endpoints for browsing, purchasing, and managing marketplace service subscriptions
(bot moderation features, MTProto features, analytics features).

This is SEPARATE from marketplace_router.py which handles marketplace_items (themes/templates).
"""

import json
import logging
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator

from apps.api.middleware.auth import get_current_user_id
from apps.di import get_container
from core.services.feature_gate_service import FeatureGateService
from core.services.marketplace_service import MarketplaceService
from infra.db.repositories.credit_repository import CreditRepository
from infra.db.repositories.marketplace_service_repository import (
    MarketplaceServiceRepository,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/services", tags=["Service Subscriptions"])

# Optional bearer auth
optional_security = HTTPBearer(auto_error=False)


# ==================== Dependencies ====================


async def get_optional_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_security),
) -> int | None:
    """Get user ID from token if authenticated, otherwise return None."""
    try:
        token = None

        # Try Bearer token from Authorization header
        if credentials and credentials.credentials:
            token = credentials.credentials
            logger.debug("Found Bearer token in header")

        # Try httpOnly cookie
        if not token:
            token = request.cookies.get("access_token")
            if token:
                logger.debug("Found token in cookie")

        if not token:
            logger.debug("No token found for optional auth")
            return None

        # Decode token to get user ID
        import jwt

        from config.settings import settings

        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub") or payload.get("user_id")
        if user_id:
            logger.debug(f"Extracted user_id={user_id} from token")
            return int(user_id)
        logger.debug(f"No user_id in token payload: {list(payload.keys())}")
        return None
    except Exception as e:
        logger.warning(f"Optional auth failed: {e}")
        return None


async def get_db_pool():
    """Get database pool from DI container."""
    container = get_container()
    try:
        pool = await container.database.asyncpg_pool()
        return pool
    except Exception as e:
        logger.error(f"Failed to get database pool: {e}")
        raise HTTPException(status_code=500, detail="Database pool not available")


async def get_marketplace_repo(
    pool=Depends(get_db_pool),
) -> MarketplaceServiceRepository:
    """Get marketplace service repository instance."""
    return MarketplaceServiceRepository(pool)


async def get_credit_repo(pool=Depends(get_db_pool)) -> CreditRepository:
    """Get credit repository instance."""
    return CreditRepository(pool)


async def get_marketplace_service(
    marketplace_repo: MarketplaceServiceRepository = Depends(get_marketplace_repo),
    credit_repo: CreditRepository = Depends(get_credit_repo),
) -> MarketplaceService:
    """Get marketplace service instance."""
    return MarketplaceService(marketplace_repo, credit_repo)


async def get_feature_gate_service(
    marketplace_repo: MarketplaceServiceRepository = Depends(get_marketplace_repo),
) -> FeatureGateService:
    """Get feature gate service instance."""
    return FeatureGateService(marketplace_repo)


# ==================== Pydantic Models ====================


class ServiceResponse(BaseModel):
    """Service details response"""

    id: int
    service_key: str
    name: str
    description: str | None
    short_description: str | None
    price_credits_monthly: int
    price_credits_yearly: int | None
    category: str
    subcategory: str | None
    features: list[str] | None  # JSONB field
    usage_quota_daily: int | None
    usage_quota_monthly: int | None
    rate_limit_per_minute: int | None
    requires_bot: bool
    requires_mtproto: bool
    min_tier: str | None
    icon: str | None
    color: str | None
    is_featured: bool
    is_popular: bool
    is_new: bool
    is_beta: bool
    active_subscriptions: int
    total_subscriptions: int
    documentation_url: str | None
    demo_video_url: str | None
    # Populated if user authenticated
    user_subscribed: bool | None = None

    @field_validator("features", mode="before")
    @classmethod
    def parse_features(cls, v):
        """Parse features from JSON string if needed"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v


class ServiceListResponse(BaseModel):
    """Service catalog response"""

    services: list[ServiceResponse]
    total: int
    categories: list[str]


class PurchaseRequest(BaseModel):
    """Service purchase request"""

    billing_cycle: Literal["monthly", "yearly"] = Field(
        default="monthly", description="Billing cycle: monthly or yearly"
    )


class PurchaseResponse(BaseModel):
    """Purchase confirmation response"""

    success: bool
    subscription_id: int
    service_name: str
    service_key: str
    billing_cycle: str
    credits_spent: int
    expires_at: datetime
    auto_renew: bool
    message: str


class SubscriptionResponse(BaseModel):
    """User subscription details"""

    id: int
    service_id: int
    service_key: str
    service_name: str
    service_description: str | None
    icon: str | None
    color: str | None
    category: str
    status: str
    billing_cycle: str
    price_paid: int
    started_at: datetime
    expires_at: datetime | None
    auto_renew: bool
    usage_count_daily: int
    usage_count_monthly: int
    usage_quota_daily: int | None
    usage_quota_monthly: int | None


class MyServicesResponse(BaseModel):
    """User's subscriptions list"""

    subscriptions: list[SubscriptionResponse]
    total: int
    active_count: int


class CancelRequest(BaseModel):
    """Subscription cancellation request"""

    reason: str | None = Field(default=None, description="Optional cancellation reason")


class ToggleRenewalRequest(BaseModel):
    """Toggle auto-renewal request"""

    auto_renew: bool = Field(description="Enable or disable auto-renewal")


class UsageStatsResponse(BaseModel):
    """Service usage statistics"""

    total_uses: int
    successful_uses: int
    success_rate: float
    days_used: int
    avg_response_time_ms: float | None


# ==================== Service Catalog Endpoints ====================


@router.get("", response_model=ServiceListResponse)
async def get_services_catalog(
    category: str | None = Query(None, description="Filter by category"),
    featured: bool | None = Query(None, description="Show only featured services"),
    search: str | None = Query(None, description="Search by name or description"),
    user_id: int | None = Depends(get_optional_user_id),
    marketplace_service: MarketplaceService = Depends(get_marketplace_service),
):
    """
    Browse the service catalog.

    Returns all available services with optional filtering.
    If user is authenticated, includes subscription status for each service.
    """
    try:
        # Get catalog (user_id optional for marking subscribed services)
        services = await marketplace_service.get_service_catalog(category=category, user_id=user_id)

        # Apply additional filters
        if featured is not None:
            services = [s for s in services if s.get("is_featured") == featured]

        if search:
            search_lower = search.lower()
            services = [
                s
                for s in services
                if search_lower in s.get("name", "").lower()
                or search_lower in s.get("description", "").lower()
            ]

        # Get unique categories
        categories = list({s.get("category") for s in services if s.get("category")})

        return ServiceListResponse(
            services=services, total=len(services), categories=sorted(categories)
        )

    except Exception as e:
        logger.error(f"Failed to get services catalog: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve services catalog",
        )


@router.get("/{service_key}", response_model=ServiceResponse)
async def get_service_details(
    service_key: str,
    user_id: int | None = Depends(get_optional_user_id),
    marketplace_service: MarketplaceService = Depends(get_marketplace_service),
):
    """
    Get detailed information about a specific service.

    If user is authenticated, includes their subscription status.
    """
    try:
        service = await marketplace_service.get_service_details(
            service_key=service_key, user_id=user_id
        )

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{service_key}' not found",
            )

        return service

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get service details for {service_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve service details",
        )


@router.get("/featured/list", response_model=ServiceListResponse)
async def get_featured_services(
    limit: int = Query(5, ge=1, le=20, description="Number of featured services"),
    marketplace_service: MarketplaceService = Depends(get_marketplace_service),
):
    """Get featured services for homepage/dashboard display."""
    try:
        services = await marketplace_service.get_featured_services(limit=limit)

        categories = list({s.get("category") for s in services if s.get("category")})

        return ServiceListResponse(
            services=services, total=len(services), categories=sorted(categories)
        )

    except Exception as e:
        logger.error(f"Failed to get featured services: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve featured services",
        )


# ==================== Purchase Endpoint ====================


@router.post("/{service_key}/purchase", response_model=PurchaseResponse)
async def purchase_service(
    service_key: str,
    request: PurchaseRequest,
    user_id: int = Depends(get_current_user_id),
    marketplace_service: MarketplaceService = Depends(get_marketplace_service),
):
    """
    Purchase a service subscription.

    Deducts credits from user's balance and activates the service.
    """
    try:
        subscription = await marketplace_service.purchase_service(
            user_id=user_id,
            service_key=service_key,
            billing_cycle=request.billing_cycle,
        )

        # Get service name for response
        service = await marketplace_service.get_service_details(service_key)

        return PurchaseResponse(
            success=True,
            subscription_id=subscription["id"],
            service_name=service["name"],
            service_key=service_key,
            billing_cycle=request.billing_cycle,
            credits_spent=subscription["price_paid"],
            expires_at=subscription["expires_at"],
            auto_renew=subscription["auto_renew"],
            message=f"Successfully purchased {service['name']}",
        )

    except ValueError as e:
        # Business logic errors (insufficient credits, already subscribed, etc.)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to purchase service {service_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process purchase",
        )


# ==================== User Subscriptions Management ====================


@router.get("/user/active", response_model=MyServicesResponse)
async def get_my_active_services(
    include_expired: bool = Query(False, description="Include expired subscriptions"),
    user_id: int = Depends(get_current_user_id),
    marketplace_service: MarketplaceService = Depends(get_marketplace_service),
):
    """
    Get user's active service subscriptions.

    Returns all services the user has purchased and their status.
    """
    try:
        subscriptions = await marketplace_service.get_user_subscriptions(
            user_id=user_id, include_expired=include_expired
        )

        # Count active subscriptions (use timezone-aware datetime)

        now = datetime.now(UTC)
        active_count = sum(
            1
            for s in subscriptions
            if s.get("status") == "active"
            and (s.get("expires_at") is None or s.get("expires_at") > now)
        )

        return MyServicesResponse(
            subscriptions=subscriptions,
            total=len(subscriptions),
            active_count=active_count,
        )

    except Exception as e:
        logger.error(f"Failed to get user services for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve your subscriptions",
        )


@router.post("/user/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: int,
    request: CancelRequest,
    user_id: int = Depends(get_current_user_id),
    marketplace_service: MarketplaceService = Depends(get_marketplace_service),
):
    """
    Cancel a service subscription.

    The subscription will remain active until its expiration date.
    """
    try:
        result = await marketplace_service.cancel_subscription(
            user_id=user_id, subscription_id=subscription_id, reason=request.reason
        )

        return {
            "success": True,
            "message": "Subscription cancelled successfully",
            "subscription_id": result["id"],
            "expires_at": result["expires_at"],
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to cancel subscription {subscription_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription",
        )


@router.post("/user/{subscription_id}/toggle-renewal")
async def toggle_auto_renewal(
    subscription_id: int,
    request: ToggleRenewalRequest,
    user_id: int = Depends(get_current_user_id),
    marketplace_service: MarketplaceService = Depends(get_marketplace_service),
):
    """
    Toggle auto-renewal for a subscription.

    When enabled, the subscription will automatically renew before expiration
    if the user has sufficient credits.
    """
    try:
        result = await marketplace_service.toggle_auto_renew(
            user_id=user_id,
            subscription_id=subscription_id,
            auto_renew=request.auto_renew,
        )

        return {
            "success": True,
            "auto_renew": request.auto_renew,
            "message": f"Auto-renewal {'enabled' if request.auto_renew else 'disabled'}",
            "subscription_id": result["id"],
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to toggle renewal for subscription {subscription_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update auto-renewal",
        )


@router.get("/user/{subscription_id}/usage", response_model=UsageStatsResponse)
async def get_subscription_usage(
    subscription_id: int,
    days: int = Query(30, ge=1, le=365, description="Days to look back"),
    user_id: int = Depends(get_current_user_id),
    marketplace_service: MarketplaceService = Depends(get_marketplace_service),
):
    """
    Get usage statistics for a subscription.

    Shows how much the service has been used, success rate, etc.
    """
    try:
        # TODO: Add ownership verification in marketplace_service
        stats = await marketplace_service.get_subscription_usage_stats(
            subscription_id=subscription_id, days=days
        )

        total = stats.get("total_uses", 0)
        successful = stats.get("successful_uses", 0)
        success_rate = (successful / total * 100) if total > 0 else 0.0

        return UsageStatsResponse(
            total_uses=total,
            successful_uses=successful,
            success_rate=round(success_rate, 2),
            days_used=stats.get("days_used", 0),
            avg_response_time_ms=stats.get("avg_response_time_ms"),
        )

    except Exception as e:
        logger.error(f"Failed to get usage stats for subscription {subscription_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage statistics",
        )


# ==================== Feature Access Check (for internal use) ====================


@router.get("/user/features/check/{service_key}")
async def check_feature_access(
    service_key: str,
    user_id: int = Depends(get_current_user_id),
    feature_gate: FeatureGateService = Depends(get_feature_gate_service),
):
    """
    Check if user has access to a specific service.

    Used by bot/MTProto workers to verify service access before executing features.
    """
    try:
        has_access = await feature_gate.check_access(user_id=user_id, service_key=service_key)

        quota_info = None
        if has_access:
            # Check daily quota if user has access
            quota_info = await feature_gate.check_quota(
                user_id=user_id, service_key=service_key, check_type="daily"
            )

        return {
            "service_key": service_key,
            "has_access": has_access,
            "quota_info": quota_info,
        }

    except Exception as e:
        logger.error(f"Failed to check feature access for {service_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check feature access",
        )
