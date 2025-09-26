"""
Repository Interfaces - Shared contracts for data access
"""

from typing import Protocol, runtime_checkable, Optional, List
from datetime import datetime


@runtime_checkable
class UserRepository(Protocol):
    """User repository interface"""
    
    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        ...
    
    async def create_user(self, user_data: dict) -> dict:
        """Create new user"""
        ...
    
    async def update_user(self, user_id: int, user_data: dict) -> dict:
        """Update user data"""
        ...


@runtime_checkable  
class PaymentRepository(Protocol):
    """Payment repository interface"""
    
    async def get_payment_by_id(self, payment_id: int) -> Optional[dict]:
        """Get payment by ID"""
        ...
    
    async def create_payment(self, payment_data: dict) -> dict:
        """Create new payment"""
        ...
    
    async def get_user_payments(self, user_id: int) -> List[dict]:
        """Get all payments for user"""
        ...


@runtime_checkable
class AnalyticsRepository(Protocol):
    """Analytics repository interface"""
    
    async def get_analytics_data(self, channel_id: int, date_from: datetime, date_to: datetime) -> List[dict]:
        """Get analytics data for channel"""
        ...
    
    async def save_analytics_data(self, data: dict) -> dict:
        """Save analytics data"""
        ...
