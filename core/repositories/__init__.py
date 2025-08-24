"""
Repository interfaces for data persistence
Framework-agnostic contracts for data access
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from core.models import ScheduledPost, Delivery, ScheduleFilter, DeliveryFilter


class ScheduleRepository(ABC):
    """
    Abstract interface for scheduled post persistence
    Defines contract for data access without implementation details
    """
    
    @abstractmethod
    async def create(self, post: ScheduledPost) -> ScheduledPost:
        """Create a new scheduled post"""
        pass
    
    @abstractmethod
    async def get_by_id(self, post_id: UUID) -> Optional[ScheduledPost]:
        """Get scheduled post by ID"""
        pass
    
    @abstractmethod
    async def update(self, post: ScheduledPost) -> ScheduledPost:
        """Update an existing scheduled post"""
        pass
    
    @abstractmethod
    async def delete(self, post_id: UUID) -> bool:
        """Delete a scheduled post"""
        pass
    
    @abstractmethod
    async def find(self, filter_criteria: ScheduleFilter) -> List[ScheduledPost]:
        """Find scheduled posts by filter criteria"""
        pass
    
    @abstractmethod
    async def get_ready_for_delivery(self) -> List[ScheduledPost]:
        """Get all posts that are ready for delivery"""
        pass
    
    @abstractmethod
    async def count(self, filter_criteria: ScheduleFilter) -> int:
        """Count scheduled posts matching filter criteria"""
        pass


class DeliveryRepository(ABC):
    """
    Abstract interface for delivery tracking persistence
    Defines contract for delivery data access
    """
    
    @abstractmethod
    async def create(self, delivery: Delivery) -> Delivery:
        """Create a new delivery record"""
        pass
    
    @abstractmethod
    async def get_by_id(self, delivery_id: UUID) -> Optional[Delivery]:
        """Get delivery by ID"""
        pass
    
    @abstractmethod
    async def get_by_post_id(self, post_id: UUID) -> List[Delivery]:
        """Get all deliveries for a specific post"""
        pass
    
    @abstractmethod
    async def update(self, delivery: Delivery) -> Delivery:
        """Update an existing delivery"""
        pass
    
    @abstractmethod
    async def find(self, filter_criteria: DeliveryFilter) -> List[Delivery]:
        """Find deliveries by filter criteria"""
        pass
    
    @abstractmethod
    async def get_failed_retryable(self) -> List[Delivery]:
        """Get failed deliveries that can be retried"""
        pass
    
    @abstractmethod
    async def count(self, filter_criteria: DeliveryFilter) -> int:
        """Count deliveries matching filter criteria"""
        pass
