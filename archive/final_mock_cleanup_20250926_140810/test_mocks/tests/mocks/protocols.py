"""
Service Protocols for Centralized Mock Infrastructure

This module contains all service protocols that mock services implement.
This ensures type safety and consistent interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any


class AnalyticsServiceProtocol(ABC):
    """Protocol for analytics services"""

    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Health check endpoint"""

    @abstractmethod
    async def get_channel_metrics(self, channel_id: str, period: str = "7d") -> dict[str, Any]:
        """Get channel analytics metrics"""

    @abstractmethod
    async def get_engagement_data(self, channel_id: str, period: str = "24h") -> dict[str, Any]:
        """Get engagement analytics"""


class PaymentServiceProtocol(ABC):
    """Protocol for payment services"""

    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Health check endpoint"""

    @abstractmethod
    async def create_payment_intent(self, amount: int, currency: str = "usd") -> dict[str, Any]:
        """Create payment intent"""


class EmailServiceProtocol(ABC):
    """Protocol for email services"""

    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Health check endpoint"""

    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email"""


class TelegramAPIServiceProtocol(ABC):
    """Protocol for Telegram API services"""

    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Health check endpoint"""

    @abstractmethod
    async def get_channel_info(self, channel_id: str) -> dict[str, Any]:
        """Get channel information"""


class AuthServiceProtocol(ABC):
    """Protocol for authentication services"""

    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Health check endpoint"""

    @abstractmethod
    async def validate_token(self, token: str) -> dict[str, Any]:
        """Validate authentication token"""


class AdminServiceProtocol(ABC):
    """Protocol for admin services"""

    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Health check endpoint"""


class AIServiceProtocol(ABC):
    """Protocol for AI services"""

    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Health check endpoint"""

    @abstractmethod
    async def generate_content(self, prompt: str) -> str:
        """Generate content using AI"""


class DemoDataServiceProtocol(ABC):
    """Protocol for demo data services"""

    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name"""

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Health check endpoint"""


class DatabaseServiceProtocol(ABC):
    """Protocol for database services"""

    @abstractmethod
    async def get_connection(self):
        """Get database connection"""

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Health check endpoint"""
