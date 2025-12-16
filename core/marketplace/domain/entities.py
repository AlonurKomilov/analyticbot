"""
Marketplace Domain Entities
===========================

Domain entities representing core marketplace concepts.
These are pure domain objects with business logic, not tied to any infrastructure.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any


# =============================================================================
# ENUMS
# =============================================================================

class ItemCategory(Enum):
    """Marketplace item categories"""
    THEMES = "themes"
    WIDGETS = "widgets"
    AI_MODELS = "ai_models"
    BUNDLES = "bundles"


class ServiceCategory(Enum):
    """Marketplace service categories"""
    BOT_SERVICE = "bot_service"
    MTPROTO_SERVICES = "mtproto_services"
    AI_SERVICES = "ai_services"


class BillingCycle(Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SubscriptionStatus(Enum):
    """Subscription status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class PurchaseStatus(Enum):
    """Purchase status"""
    COMPLETED = "completed"
    PENDING = "pending"
    REFUNDED = "refunded"
    FAILED = "failed"


# =============================================================================
# MARKETPLACE ITEMS (One-time purchases)
# =============================================================================

@dataclass
class MarketplaceItem:
    """
    Domain entity for marketplace items (themes, widgets, AI models, bundles).
    These are one-time purchases.
    """
    id: int
    unique_key: str
    name: str
    slug: str
    description: str
    short_description: str
    category: ItemCategory
    
    # Pricing
    price_credits: int
    original_price_credits: Optional[int] = None
    
    # Display
    icon: Optional[str] = None
    color: Optional[str] = None
    preview_images: List[str] = field(default_factory=list)
    demo_video_url: Optional[str] = None
    
    # Metadata
    version: str = "1.0.0"
    author: Optional[str] = None
    features: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    is_featured: bool = False
    is_popular: bool = False
    is_new: bool = False
    
    # Stats
    purchase_count: int = 0
    rating_average: float = 0.0
    rating_count: int = 0
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def has_discount(self) -> bool:
        """Check if item has a discount"""
        return (
            self.original_price_credits is not None 
            and self.original_price_credits > self.price_credits
        )
    
    @property
    def discount_percentage(self) -> int:
        """Calculate discount percentage"""
        if not self.has_discount or not self.original_price_credits:
            return 0
        return int((1 - self.price_credits / self.original_price_credits) * 100)


@dataclass
class ItemPurchase:
    """
    Domain entity for item purchases.
    """
    id: int
    user_id: int
    item_id: int
    price_paid: int
    status: PurchaseStatus
    purchased_at: datetime
    
    # Optional references
    item: Optional[MarketplaceItem] = None


@dataclass
class ItemReview:
    """
    Domain entity for item reviews.
    """
    id: int
    user_id: int
    item_id: int
    rating: int  # 1-5
    review_text: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def validate_rating(self) -> bool:
        """Ensure rating is within valid range"""
        return 1 <= self.rating <= 5


# =============================================================================
# MARKETPLACE SERVICES (Subscriptions)
# =============================================================================

@dataclass
class MarketplaceService:
    """
    Domain entity for marketplace services (bot services, MTProto services).
    These are subscription-based products.
    """
    id: int
    service_key: str
    name: str
    description: str
    short_description: str
    category: ServiceCategory
    
    # Pricing
    price_credits_monthly: int
    price_credits_yearly: Optional[int] = None
    
    # Display
    icon: Optional[str] = None
    color: Optional[str] = None
    
    # Features
    features: List[str] = field(default_factory=list)
    
    # Quotas (optional usage limits)
    quota_daily: Optional[int] = None
    quota_monthly: Optional[int] = None
    
    # Status
    is_active: bool = True
    is_featured: bool = False
    is_popular: bool = False
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def yearly_discount_percentage(self) -> int:
        """Calculate yearly discount compared to monthly * 12"""
        if not self.price_credits_yearly:
            return 0
        yearly_at_monthly = self.price_credits_monthly * 12
        return int((1 - self.price_credits_yearly / yearly_at_monthly) * 100)


@dataclass
class ServiceSubscription:
    """
    Domain entity for user service subscriptions.
    """
    id: int
    user_id: int
    service_id: int
    service_key: str
    
    # Billing
    billing_cycle: BillingCycle
    price_paid: int
    auto_renew: bool = True
    
    # Status
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    
    # Dates
    started_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Usage tracking
    usage_count_daily: int = 0
    usage_count_monthly: int = 0
    last_usage_reset: Optional[datetime] = None
    
    # Optional references
    service: Optional[MarketplaceService] = None
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        if self.status != SubscriptionStatus.ACTIVE:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
    
    @property
    def days_remaining(self) -> int:
        """Calculate days until expiration"""
        if not self.expires_at:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def is_expiring_soon(self) -> bool:
        """Check if subscription is expiring within 7 days"""
        return 0 < self.days_remaining <= 7
    
    def can_use(self, quota_daily: Optional[int] = None, quota_monthly: Optional[int] = None) -> bool:
        """Check if user can use the service (within quota limits)"""
        if not self.is_active:
            return False
        
        if quota_daily and self.usage_count_daily >= quota_daily:
            return False
        
        if quota_monthly and self.usage_count_monthly >= quota_monthly:
            return False
        
        return True


@dataclass
class ServiceUsageLog:
    """
    Domain entity for service usage tracking.
    """
    id: int
    subscription_id: int
    action: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


# =============================================================================
# BUNDLES
# =============================================================================

@dataclass
class Bundle:
    """
    Domain entity for bundles (collection of items/services at discounted price).
    """
    id: int
    unique_key: str
    name: str
    description: str
    
    # Contents
    item_ids: List[int] = field(default_factory=list)
    service_ids: List[int] = field(default_factory=list)
    
    # Pricing
    price_credits: int
    original_total_credits: int  # Sum of individual items
    
    # Display
    icon: Optional[str] = None
    color: Optional[str] = None
    
    # Status
    is_active: bool = True
    is_featured: bool = False
    
    # Timestamps
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None  # Limited-time bundles
    
    @property
    def discount_percentage(self) -> int:
        """Calculate bundle discount"""
        if self.original_total_credits == 0:
            return 0
        return int((1 - self.price_credits / self.original_total_credits) * 100)
    
    @property
    def is_limited_time(self) -> bool:
        """Check if bundle is limited-time offer"""
        return self.expires_at is not None


# =============================================================================
# GIFT SYSTEM
# =============================================================================

@dataclass 
class CreditGift:
    """
    Domain entity for credit gifts between users.
    """
    id: int
    sender_id: int
    receiver_id: int
    amount: int
    message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
