"""
Marketplace API Schemas
=======================

Pydantic models for marketplace API requests and responses.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# ITEM SCHEMAS (One-time purchases)
# =============================================================================


class MarketplaceItemResponse(BaseModel):
    """Response schema for marketplace item"""

    id: int
    name: str
    slug: str
    description: str
    category: str
    subcategory: str | None = None
    price_credits: int
    is_premium: bool = False
    is_featured: bool = False
    preview_url: str | None = None
    icon_url: str | None = None
    metadata: dict[str, Any] | None = None
    download_count: int = 0
    rating: float | None = None
    rating_count: int = 0
    created_at: datetime
    user_owned: bool | None = None


class ItemPurchaseRequest(BaseModel):
    """Request to purchase a marketplace item"""

    item_id: int = Field(..., description="Item ID to purchase")


class ItemPurchaseResponse(BaseModel):
    """Response after purchasing an item"""

    success: bool
    purchase_id: int | None = None
    credits_spent: int | None = None
    error: str | None = None


class ItemReviewRequest(BaseModel):
    """Request to add/update item review"""

    item_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    review_text: str | None = Field(None, max_length=2000)


class ItemReviewResponse(BaseModel):
    """Response for item review"""

    id: int
    rating: int
    review_text: str | None
    is_verified_purchase: bool
    created_at: datetime
    username: str
    full_name: str | None = None


# =============================================================================
# SERVICE SCHEMAS (Subscriptions)
# =============================================================================


class MarketplaceServiceResponse(BaseModel):
    """Response schema for marketplace service"""

    id: int
    service_key: str
    name: str
    description: str
    short_description: str | None = None
    price_credits_monthly: int
    price_credits_yearly: int | None = None
    category: str
    subcategory: str | None = None
    features: list[str] | None = None
    usage_quota_daily: int | None = None
    usage_quota_monthly: int | None = None
    icon: str | None = None
    color: str | None = None
    is_featured: bool = False
    is_popular: bool = False
    is_new: bool = False
    requires_bot: bool = False
    requires_mtproto: bool = False
    user_subscribed: bool | None = None
    active_subscriptions: int = 0


class ServiceCatalogResponse(BaseModel):
    """Response for service catalog listing"""

    services: list[MarketplaceServiceResponse]
    total: int


class ServiceSubscriptionRequest(BaseModel):
    """Request to subscribe to a service"""

    service_key: str = Field(..., description="Service key to subscribe to")
    billing_cycle: str = Field("monthly", pattern="^(monthly|yearly)$")


class ServiceSubscriptionResponse(BaseModel):
    """Response for service subscription"""

    id: int
    service_id: int
    service_key: str
    service_name: str
    status: str
    billing_cycle: str
    price_paid: int
    started_at: datetime
    expires_at: datetime
    auto_renew: bool
    usage_count_daily: int = 0
    usage_count_monthly: int = 0
    usage_quota_daily: int | None = None
    usage_quota_monthly: int | None = None


class UserSubscriptionsResponse(BaseModel):
    """Response listing user's subscriptions"""

    subscriptions: list[ServiceSubscriptionResponse]


class CancelSubscriptionRequest(BaseModel):
    """Request to cancel a subscription"""

    subscription_id: int
    reason: str | None = Field(None, max_length=500)


class ToggleAutoRenewRequest(BaseModel):
    """Request to toggle auto-renewal"""

    subscription_id: int
    auto_renew: bool


# =============================================================================
# CREDIT / GIFT SCHEMAS
# =============================================================================


class GiftCreditsRequest(BaseModel):
    """Request to gift credits to another user"""

    recipient_username: str
    amount: int = Field(..., gt=0)
    message: str | None = Field(None, max_length=200)


class GiftResponse(BaseModel):
    """Response after gifting credits"""

    success: bool
    gift_id: int | None = None
    recipient: str | None = None
    amount: int | None = None
    error: str | None = None


class CreditBalanceResponse(BaseModel):
    """Response for credit balance"""

    balance: int
    pending: int = 0


# =============================================================================
# BUNDLE SCHEMAS
# =============================================================================


class BundleResponse(BaseModel):
    """Response for marketplace bundle"""

    id: int
    name: str
    slug: str
    description: str
    price_credits: int
    original_price: int
    discount_percent: int
    is_featured: bool = False
    valid_days: int
    items: list[dict[str, Any]] | None = None


class BundlePurchaseRequest(BaseModel):
    """Request to purchase a bundle"""

    bundle_id: int


class BundlePurchaseResponse(BaseModel):
    """Response after purchasing a bundle"""

    success: bool
    user_bundle_id: int | None = None
    bundle_name: str | None = None
    expires_at: str | None = None
    credits_spent: int | None = None
    error: str | None = None


# =============================================================================
# GENERIC RESPONSES
# =============================================================================


class ErrorResponse(BaseModel):
    """Generic error response"""

    error: str
    detail: str | None = None


class SuccessResponse(BaseModel):
    """Generic success response"""

    success: bool = True
    message: str | None = None
