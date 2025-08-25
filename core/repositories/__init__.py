"""
Repository interfaces for data persistence
Framework-agnostic contracts for data access
"""

from abc import ABC, abstractmethod
from uuid import UUID

from core.models import Delivery, DeliveryFilter, ScheduledPost, ScheduleFilter


class ScheduleRepository(ABC):
    """
    Abstract interface for scheduled post persistence
    Defines contract for data access without implementation details
    """

    @abstractmethod
    async def create(self, post: ScheduledPost) -> ScheduledPost:
        """Create a new scheduled post"""

    @abstractmethod
    async def get_by_id(self, post_id: UUID) -> ScheduledPost | None:
        """Get scheduled post by ID"""

    @abstractmethod
    async def update(self, post: ScheduledPost) -> ScheduledPost:
        """Update an existing scheduled post"""

    @abstractmethod
    async def delete(self, post_id: UUID) -> bool:
        """Delete a scheduled post"""

    @abstractmethod
    async def find(self, filter_criteria: ScheduleFilter) -> list[ScheduledPost]:
        """Find scheduled posts by filter criteria"""

    @abstractmethod
    async def get_ready_for_delivery(self) -> list[ScheduledPost]:
        """Get all posts that are ready for delivery"""

    @abstractmethod
    async def count(self, filter_criteria: ScheduleFilter) -> int:
        """Count scheduled posts matching filter criteria"""


class DeliveryRepository(ABC):
    """
    Abstract interface for delivery tracking persistence
    Defines contract for delivery data access
    """

    @abstractmethod
    async def create(self, delivery: Delivery) -> Delivery:
        """Create a new delivery record"""

    @abstractmethod
    async def get_by_id(self, delivery_id: UUID) -> Delivery | None:
        """Get delivery by ID"""

    @abstractmethod
    async def get_by_post_id(self, post_id: UUID) -> list[Delivery]:
        """Get all deliveries for a specific post"""

    @abstractmethod
    async def update(self, delivery: Delivery) -> Delivery:
        """Update an existing delivery"""

    @abstractmethod
    async def find(self, filter_criteria: DeliveryFilter) -> list[Delivery]:
        """Find deliveries by filter criteria"""

    @abstractmethod
    async def get_failed_retryable(self) -> list[Delivery]:
        """Get failed deliveries that can be retried"""

    @abstractmethod
    async def count(self, filter_criteria: DeliveryFilter) -> int:
        """Count deliveries matching filter criteria"""
