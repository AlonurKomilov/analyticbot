"""
Repository Interfaces (Ports) for Clean Architecture
Contains all abstract repository interfaces that define contracts
Concrete implementations are in infra/db/repositories/
"""

from typing import Protocol
from uuid import UUID

from core.models import Delivery, DeliveryFilter, ScheduledPost, ScheduleFilter


class UserRepository(Protocol):
    """User repository interface using Protocol (structural typing)"""
    
    async def get_user_by_id(self, user_id: int) -> dict | None:
        """Get user by ID"""
        ...
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> dict | None:
        """Get user by Telegram ID"""
        ...
    
    async def create_user(self, user_data: dict) -> dict:
        """Create new user"""
        ...
    
    async def update_user(self, user_id: int, **updates) -> bool:
        """Update user information"""
        ...
    
    async def get_user_subscription_tier(self, user_id: int) -> str:
        """Get user's subscription tier"""
        ...
    
    async def user_exists(self, user_id: int) -> bool:
        """Check if user exists"""
        ...


class AdminRepository(Protocol):
    """Admin repository interface using Protocol"""
    
    async def get_admin_by_username(self, username: str) -> dict | None:
        """Get admin by username"""
        ...
    
    async def create_admin(self, admin_data: dict) -> dict:
        """Create new admin"""
        ...
    
    async def update_admin(self, admin_id: int, **updates) -> bool:
        """Update admin information"""
        ...


class ScheduleRepository(Protocol):
    """
    Abstract interface for scheduled post persistence
    Defines contract for data access without implementation details
    """

    async def create(self, post: ScheduledPost) -> ScheduledPost:
        """Create a new scheduled post"""
        ...

    async def get_by_id(self, post_id: UUID) -> ScheduledPost | None:
        """Get scheduled post by ID"""
        ...

    async def update(self, post: ScheduledPost) -> ScheduledPost:
        """Update an existing scheduled post"""
        ...

    async def delete(self, post_id: UUID) -> bool:
        """Delete a scheduled post"""
        ...

    async def find(self, filter_criteria: ScheduleFilter) -> list[ScheduledPost]:
        """Find scheduled posts by filter criteria"""
        ...

    async def get_ready_for_delivery(self) -> list[ScheduledPost]:
        """Get all posts that are ready for delivery"""
        ...

    async def count(self, filter_criteria: ScheduleFilter) -> int:
        """Count scheduled posts matching filter criteria"""
        ...


class DeliveryRepository(Protocol):
    """
    Abstract interface for delivery tracking persistence
    Defines contract for delivery data access
    """

    async def create(self, delivery: Delivery) -> Delivery:
        """Create a new delivery record"""
        ...

    async def get_by_id(self, delivery_id: UUID) -> Delivery | None:
        """Get delivery by ID"""
        ...

    async def get_by_post_id(self, post_id: UUID) -> list[Delivery]:
        """Get all deliveries for a specific post"""
        ...

    async def update(self, delivery: Delivery) -> Delivery:
        """Update an existing delivery"""
        ...

    async def find(self, filter_criteria: DeliveryFilter) -> list[Delivery]:
        """Find deliveries by filter criteria"""
        ...

    async def get_failed_retryable(self) -> list[Delivery]:
        """Get failed deliveries that can be retried"""
        ...

    async def count(self, filter_criteria: DeliveryFilter) -> int:
        """Count deliveries matching filter criteria"""
        ...
