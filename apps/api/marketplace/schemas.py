"""
Marketplace API Schemas
=======================

Pydantic models for marketplace API requests and responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
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
    subcategory: Optional[str] = None
    price_credits: int
    is_premium: bool = False
    is_featured: bool = False
    preview_url: Optional[str] = None
    icon_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    download_count: int = 0
    rating: Optional[float] = None
    rating_count: int = 0
    created_at: datetime
    user_owned: Optional[bool] = None


class ItemPurchaseRequest(BaseModel):
    """Request to purchase a marketplace item"""
    item_id: int = Field(..., description="Item ID to purchase")


class ItemPurchaseResponse(BaseModel):
    """Response after purchasing an item"""
    success: bool
    purchase_id: Optional[int] = None
    credits_spent: Optional[int] = None
    error: Optional[str] = None


class ItemReviewRequest(BaseModel):
    """Request to add/update item review"""
    item_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    review_text: Optional[str] = Field(None, max_length=2000)


class ItemReviewResponse(BaseModel):
    """Response for item review"""
    id: int
    rating: int
    review_text: Optional[str]
    is_verified_purchase: bool
    created_at: datetime
    username: str
    full_name: Optional[str] = None


# =============================================================================
# SERVICE SCHEMAS (Subscriptions)
# =============================================================================

class MarketplaceServiceResponse(BaseModel):
    """Response schema for marketplace service"""
    id: int
    service_key: str
    name: str
    description: str
    short_description: Optional[str] = None
    price_credits_monthly: int
    price_credits_yearly: Optional[int] = None
    category: str
    subcategory: Optional[str] = None
    features: Optional[List[str]] = None
    usage_quota_daily: Optional[int] = None
    usage_quota_monthly: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_featured: bool = False
    is_popular: bool = False
    is_new: bool = False
    requires_bot: bool = False
    requires_mtproto: bool = False
    user_subscribed: Optional[bool] = None
    active_subscriptions: int = 0


class ServiceCatalogResponse(BaseModel):
    """Response for service catalog listing"""
    services: List[MarketplaceServiceResponse]
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
    usage_quota_daily: Optional[int] = None
    usage_quota_monthly: Optional[int] = None


class UserSubscriptionsResponse(BaseModel):
    """Response listing user's subscriptions"""
    subscriptions: List[ServiceSubscriptionResponse]


class CancelSubscriptionRequest(BaseModel):
    """Request to cancel a subscription"""
    subscription_id: int
    reason: Optional[str] = Field(None, max_length=500)


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
    message: Optional[str] = Field(None, max_length=200)


class GiftResponse(BaseModel):
    """Response after gifting credits"""
    success: bool
    gift_id: Optional[int] = None
    recipient: Optional[str] = None
    amount: Optional[int] = None
    error: Optional[str] = None


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
    items: Optional[List[Dict[str, Any]]] = None


class BundlePurchaseRequest(BaseModel):
    """Request to purchase a bundle"""
    bundle_id: int


class BundlePurchaseResponse(BaseModel):
    """Response after purchasing a bundle"""
    success: bool
    user_bundle_id: Optional[int] = None
    bundle_name: Optional[str] = None
    expires_at: Optional[str] = None
    credits_spent: Optional[int] = None
    error: Optional[str] = None


# =============================================================================
# GENERIC RESPONSES
# =============================================================================

class ErrorResponse(BaseModel):
    """Generic error response"""
    error: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: Optional[str] = None
