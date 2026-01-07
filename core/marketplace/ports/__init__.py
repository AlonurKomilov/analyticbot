"""
Marketplace Ports (Interfaces)
==============================

Port interfaces for the marketplace module.
These define the contracts that adapters must implement.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.marketplace.domain import (
    BillingCycle,
    Bundle,
    ItemCategory,
    ItemPurchase,
    ItemReview,
    MarketplaceItem,
    MarketplaceService,
    ServiceCategory,
    ServiceSubscription,
    SubscriptionStatus,
)


class MarketplaceItemRepositoryPort(ABC):
    """
    Port for marketplace items repository.
    Handles CRUD operations for one-time purchase items.
    """

    @abstractmethod
    async def get_item_by_id(self, item_id: int) -> MarketplaceItem | None:
        """Get item by ID"""

    @abstractmethod
    async def get_item_by_key(self, unique_key: str) -> MarketplaceItem | None:
        """Get item by unique key"""

    @abstractmethod
    async def list_items(
        self,
        category: ItemCategory | None = None,
        is_featured: bool | None = None,
        is_active: bool = True,
        search_query: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MarketplaceItem]:
        """List items with filtering"""

    @abstractmethod
    async def get_user_purchases(self, user_id: int) -> list[ItemPurchase]:
        """Get all purchases for a user"""

    @abstractmethod
    async def has_user_purchased(self, user_id: int, item_id: int) -> bool:
        """Check if user has purchased an item"""

    @abstractmethod
    async def create_purchase(
        self,
        user_id: int,
        item_id: int,
        price_paid: int,
    ) -> ItemPurchase:
        """Create a new purchase"""

    @abstractmethod
    async def get_item_reviews(
        self,
        item_id: int,
        limit: int = 10,
        offset: int = 0,
    ) -> list[ItemReview]:
        """Get reviews for an item"""

    @abstractmethod
    async def create_review(
        self,
        user_id: int,
        item_id: int,
        rating: int,
        review_text: str | None = None,
    ) -> ItemReview:
        """Create a new review"""


class MarketplaceServiceRepositoryPort(ABC):
    """
    Port for marketplace services repository.
    Handles CRUD operations for subscription services.
    """

    @abstractmethod
    async def get_service_by_id(self, service_id: int) -> MarketplaceService | None:
        """Get service by ID"""

    @abstractmethod
    async def get_service_by_key(self, service_key: str) -> MarketplaceService | None:
        """Get service by key"""

    @abstractmethod
    async def list_services(
        self,
        category: ServiceCategory | None = None,
        is_featured: bool | None = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MarketplaceService]:
        """List services with filtering"""

    @abstractmethod
    async def get_user_subscriptions(
        self,
        user_id: int,
        status: SubscriptionStatus | None = None,
    ) -> list[ServiceSubscription]:
        """Get user's subscriptions"""

    @abstractmethod
    async def get_active_subscription(
        self,
        user_id: int,
        service_key: str,
    ) -> ServiceSubscription | None:
        """Get user's active subscription for a service"""

    @abstractmethod
    async def has_active_subscription(
        self,
        user_id: int,
        service_key: str,
    ) -> bool:
        """Check if user has active subscription"""

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

    @abstractmethod
    async def renew_subscription(
        self,
        subscription_id: int,
        new_expires_at: datetime,
        price_paid: int,
    ) -> ServiceSubscription:
        """Renew an existing subscription"""

    @abstractmethod
    async def cancel_subscription(
        self,
        subscription_id: int,
    ) -> ServiceSubscription:
        """Cancel a subscription"""

    @abstractmethod
    async def update_auto_renew(
        self,
        subscription_id: int,
        auto_renew: bool,
    ) -> ServiceSubscription:
        """Update auto-renew setting"""

    @abstractmethod
    async def log_usage(
        self,
        subscription_id: int,
        action: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log service usage"""

    @abstractmethod
    async def increment_usage(
        self,
        subscription_id: int,
    ) -> None:
        """Increment usage counters"""

    @abstractmethod
    async def reset_daily_usage(self) -> int:
        """Reset daily usage for all subscriptions. Returns count reset."""

    @abstractmethod
    async def reset_monthly_usage(self) -> int:
        """Reset monthly usage for all subscriptions. Returns count reset."""


class BundleRepositoryPort(ABC):
    """
    Port for bundle repository.
    """

    @abstractmethod
    async def get_bundle_by_id(self, bundle_id: int) -> Bundle | None:
        """Get bundle by ID"""

    @abstractmethod
    async def get_bundle_by_key(self, unique_key: str) -> Bundle | None:
        """Get bundle by unique key"""

    @abstractmethod
    async def list_bundles(
        self,
        is_active: bool = True,
        is_featured: bool | None = None,
    ) -> list[Bundle]:
        """List available bundles"""

    @abstractmethod
    async def purchase_bundle(
        self,
        user_id: int,
        bundle_id: int,
        price_paid: int,
    ) -> None:
        """Purchase a bundle (creates all item purchases and subscriptions)"""


class CreditRepositoryPort(ABC):
    """
    Port for credit operations.
    """

    @abstractmethod
    async def get_balance(self, user_id: int) -> int:
        """Get user's credit balance"""

    @abstractmethod
    async def deduct_credits(self, user_id: int, amount: int, reason: str) -> int:
        """Deduct credits from user. Returns new balance."""

    @abstractmethod
    async def add_credits(self, user_id: int, amount: int, reason: str) -> int:
        """Add credits to user. Returns new balance."""

    @abstractmethod
    async def transfer_credits(
        self,
        from_user_id: int,
        to_user_id: int,
        amount: int,
        message: str | None = None,
    ) -> None:
        """Transfer credits between users"""


class FeatureGatePort(ABC):
    """
    Port for feature gating (checking service access).
    """

    @abstractmethod
    async def has_access(self, user_id: int, service_key: str) -> bool:
        """Check if user has access to a service"""

    @abstractmethod
    async def get_user_services(self, user_id: int) -> list[str]:
        """Get list of service keys user has access to"""

    @abstractmethod
    async def check_quota(
        self,
        user_id: int,
        service_key: str,
    ) -> dict[str, Any]:
        """
        Check quota status for a service.
        Returns: {
            "can_use": bool,
            "daily_remaining": int | None,
            "monthly_remaining": int | None,
        }
        """
