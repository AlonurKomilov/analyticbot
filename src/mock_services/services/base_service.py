"""
Base Mock Service - Abstract base class for all mock services
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseMockService(ABC):
    """Abstract base class for all mock services"""

    def __init__(self):
        """Initialize the base mock service"""
        self._initialized = True

    @abstractmethod
    def get_service_name(self) -> str:
        """Get the service name"""

    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return getattr(self, "_initialized", False)

    def get_service_info(self) -> dict[str, Any]:
        """Get service information"""
        return {
            "name": self.get_service_name(),
            "initialized": self.is_initialized(),
            "type": "mock_service",
        }
