"""
Service Interfaces - Shared contracts for services
"""

from typing import Protocol, runtime_checkable, Optional, Dict, Any
from datetime import datetime


@runtime_checkable
class AuthenticationService(Protocol):
    """Authentication service interface"""
    
    async def authenticate_user(self, credentials: dict) -> Optional[dict]:
        """Authenticate user with credentials"""
        ...
    
    async def create_session(self, user_id: int) -> dict:
        """Create user session"""
        ...


@runtime_checkable
class PaymentService(Protocol):
    """Payment processing service interface"""
    
    async def process_payment(self, payment_data: dict) -> dict:
        """Process a payment"""
        ...
    
    async def get_payment_status(self, payment_id: int) -> str:
        """Get payment status"""
        ...


@runtime_checkable
class AnalyticsService(Protocol):
    """Analytics service interface"""
    
    async def get_channel_analytics(self, channel_id: int, date_range: tuple) -> dict:
        """Get analytics for channel"""
        ...
    
    async def generate_report(self, report_config: dict) -> dict:
        """Generate analytics report"""
        ...
