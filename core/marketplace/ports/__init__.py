"""
Marketplace Ports (Interfaces)
==============================

Port interfaces for the marketplace module.
These define the contracts that adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.marketplace.domain import (
    MarketplaceItem,
    MarketplaceService,
    ServiceSubscription,
    ItemPurchase,
    ItemReview,
    Bundle,
    ItemCategory,
    ServiceCategory,
    BillingCycle,
    SubscriptionStatus,
)


class MarketplaceItemRepositoryPort(ABC):
    """
    Port for marketplace items repository.
    Handles CRUD operations for one-time purchase items.
    """
    
    @abstractmethod
    async def get_item_by_id(self, item_id: int) -> Optional[MarketplaceItem]:
        """Get item by ID"""
        pass
    
    @abstractmethod
    async def get_item_by_key(self, unique_key: str) -> Optional[MarketplaceItem]:
        """Get item by unique key"""
        pass
    
    @abstractmethod
    async def list_items(
        self,
        category: Optional[ItemCategory] = None,
        is_featured: Optional[bool] = None,
        is_active: bool = True,
        search_query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[MarketplaceItem]:
        """List items with filtering"""
        pass
    
    @abstractmethod
    async def get_user_purchases(self, user_id: int) -> List[ItemPurchase]:
        """Get all purchases for a user"""
        pass
    
    @abstractmethod
    async def has_user_purchased(self, user_id: int, item_id: int) -> bool:
        """Check if user has purchased an item"""
        pass
    
    @abstractmethod
    async def create_purchase(
        self,
        user_id: int,
        item_id: int,
        price_paid: int,
    ) -> ItemPurchase:
        """Create a new purchase"""
        pass
    
    @abstractmethod
    async def get_item_reviews(
        self,
        item_id: int,
        limit: int = 10,
        offset: int = 0,
    ) -> List[ItemReview]:
        """Get reviews for an item"""
        pass
    
    @abstractmethod
    async def create_review(
        self,
        user_id: int,
        item_id: int,
        rating: int,
        review_text: Optional[str] = None,
    ) -> ItemReview:
        """Create a new review"""
        pass


class MarketplaceServiceRepositoryPort(ABC):
    """
    Port for marketplace services repository.
    Handles CRUD operations for subscription services.
    """
    
    @abstractmethod
    async def get_service_by_id(self, service_id: int) -> Optional[MarketplaceService]:
        """Get service by ID"""
        pass
    
    @abstractmethod
    async def get_service_by_key(self, service_key: str) -> Optional[MarketplaceService]:
        """Get service by key"""
        pass
    
    @abstractmethod
    async def list_services(
        self,
        category: Optional[ServiceCategory] = None,
        is_featured: Optional[bool] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> List[MarketplaceService]:
        """List services with filtering"""
        pass
    
    @abstractmethod
    async def get_user_subscriptions(
        self,
        user_id: int,
        status: Optional[SubscriptionStatus] = None,
    ) -> List[ServiceSubscription]:
        """Get user's subscriptions"""
        pass
    
    @abstractmethod
    async def get_active_subscription(
        self,
        user_id: int,
        service_key: str,
    ) -> Optional[ServiceSubscription]:
        """Get user's active subscription for a service"""
        pass
    
    @abstractmethod
    async def has_active_subscription(
        self,
        user_id: int,
        service_key: str,
    ) -> bool:
        """Check if user has active subscription"""
        pass
    
    @abstractmethod
    async def create_subscription(
        self,
        user_id: int,
        service_id: int,
        service_key: str,
        billing_cycle: BillingCycle,
        price_paid: int,
        expires_at: datetime,
    ) -> ServiceSubscription:
        """Create a new subscription"""
        pass
    
    @abstractmethod
    async def renew_subscription(
        self,
        subscription_id: int,
        new_expires_at: datetime,
        price_paid: int,
    ) -> ServiceSubscription:
        """Renew an existing subscription"""
        pass
    
    @abstractmethod
    async def cancel_subscription(
        self,
        subscription_id: int,
    ) -> ServiceSubscription:
        """Cancel a subscription"""
        pass
    
    @abstractmethod
    async def update_auto_renew(
        self,
        subscription_id: int,
        auto_renew: bool,
    ) -> ServiceSubscription:
        """Update auto-renew setting"""
        pass
    
    @abstractmethod
    async def log_usage(
        self,
        subscription_id: int,
        action: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log service usage"""
        pass
    
    @abstractmethod
    async def increment_usage(
        self,
        subscription_id: int,
    ) -> None:
        """Increment usage counters"""
        pass
    
    @abstractmethod
    async def reset_daily_usage(self) -> int:
        """Reset daily usage for all subscriptions. Returns count reset."""
        pass
    
    @abstractmethod
    async def reset_monthly_usage(self) -> int:
        """Reset monthly usage for all subscriptions. Returns count reset."""
        pass


class BundleRepositoryPort(ABC):
    """
    Port for bundle repository.
    """
    
    @abstractmethod
    async def get_bundle_by_id(self, bundle_id: int) -> Optional[Bundle]:
        """Get bundle by ID"""
        pass
    
    @abstractmethod
    async def get_bundle_by_key(self, unique_key: str) -> Optional[Bundle]:
        """Get bundle by unique key"""
        pass
    
    @abstractmethod
    async def list_bundles(
        self,
        is_active: bool = True,
        is_featured: Optional[bool] = None,
    ) -> List[Bundle]:
        """List available bundles"""
        pass
    
    @abstractmethod
    async def purchase_bundle(
        self,
        user_id: int,
        bundle_id: int,
        price_paid: int,
    ) -> None:
        """Purchase a bundle (creates all item purchases and subscriptions)"""
        pass


class CreditRepositoryPort(ABC):
    """
    Port for credit operations.
    """
    
    @abstractmethod
    async def get_balance(self, user_id: int) -> int:
        """Get user's credit balance"""
        pass
    
    @abstractmethod
    async def deduct_credits(self, user_id: int, amount: int, reason: str) -> int:
        """Deduct credits from user. Returns new balance."""
        pass
    
    @abstractmethod
    async def add_credits(self, user_id: int, amount: int, reason: str) -> int:
        """Add credits to user. Returns new balance."""
        pass
    
    @abstractmethod
    async def transfer_credits(
        self,
        from_user_id: int,
        to_user_id: int,
        amount: int,
        message: Optional[str] = None,
    ) -> None:
        """Transfer credits between users"""
        pass


class FeatureGatePort(ABC):
    """
    Port for feature gating (checking service access).
    """
    
    @abstractmethod
    async def has_access(self, user_id: int, service_key: str) -> bool:
        """Check if user has access to a service"""
        pass
    
    @abstractmethod
    async def get_user_services(self, user_id: int) -> List[str]:
        """Get list of service keys user has access to"""
        pass
    
    @abstractmethod
    async def check_quota(
        self,
        user_id: int,
        service_key: str,
    ) -> Dict[str, Any]:
        """
        Check quota status for a service.
        Returns: {
            "can_use": bool,
            "daily_remaining": int | None,
            "monthly_remaining": int | None,
        }
        """
        pass
