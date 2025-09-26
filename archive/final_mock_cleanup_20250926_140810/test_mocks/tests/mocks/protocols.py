"""
Service Protocols for Centralized Mock Infrastructure

This module contains all service protocols that mock services implement.
This ensures type safety and consistent interfaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class AnalyticsServiceProtocol(ABC):
    """Protocol for analytics services"""
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        pass
    
    @abstractmethod
    async def get_channel_metrics(self, channel_id: str, period: str = "7d") -> Dict[str, Any]:
        """Get channel analytics metrics"""
        pass
    
    @abstractmethod
    async def get_engagement_data(self, channel_id: str, period: str = "24h") -> Dict[str, Any]:
        """Get engagement analytics"""
        pass


class PaymentServiceProtocol(ABC):
    """Protocol for payment services"""
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        pass
    
    @abstractmethod
    async def create_payment_intent(self, amount: int, currency: str = "usd") -> Dict[str, Any]:
        """Create payment intent"""
        pass


class EmailServiceProtocol(ABC):
    """Protocol for email services"""
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        pass
    
    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email"""
        pass


class TelegramAPIServiceProtocol(ABC):
    """Protocol for Telegram API services"""
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        pass
    
    @abstractmethod
    async def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Get channel information"""
        pass


class AuthServiceProtocol(ABC):
    """Protocol for authentication services"""
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        pass
    
    @abstractmethod
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate authentication token"""
        pass


class AdminServiceProtocol(ABC):
    """Protocol for admin services"""
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        pass


class AIServiceProtocol(ABC):
    """Protocol for AI services"""
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        pass
    
    @abstractmethod
    async def generate_content(self, prompt: str) -> str:
        """Generate content using AI"""
        pass


class DemoDataServiceProtocol(ABC):
    """Protocol for demo data services"""
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        pass


class DatabaseServiceProtocol(ABC):
    """Protocol for database services"""
    
    @abstractmethod
    async def get_connection(self):
        """Get database connection"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        pass