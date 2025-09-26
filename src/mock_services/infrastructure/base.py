"""
Base Mock Service Infrastructure

Provides common functionality for all mock services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseMockService(ABC):
    """
    Base class for all mock services providing common functionality.
    
    This ensures consistent behavior across all mocks and reduces duplication.
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self._initialized = True
        logger.info(f"Initialized {self.service_name}")
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Return the service name for identification"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Standard health check for all mock services"""
        return {
            "service": self.service_name,
            "status": "healthy",
            "type": "mock",
            "initialized": self._initialized
        }
    
    def reset(self) -> None:
        """Reset mock state - override in subclasses if needed"""
        logger.info(f"Reset {self.service_name}")


class MockServiceMetrics:
    """Metrics collection for mock services during testing"""
    
    def __init__(self):
        self.call_counts: Dict[str, int] = {}
        self.method_calls: Dict[str, Dict[str, int]] = {}
    
    def record_call(self, service_name: str, method_name: str):
        """Record a method call for metrics"""
        self.call_counts[service_name] = self.call_counts.get(service_name, 0) + 1
        
        if service_name not in self.method_calls:
            self.method_calls[service_name] = {}
        
        self.method_calls[service_name][method_name] = (
            self.method_calls[service_name].get(method_name, 0) + 1
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "total_calls": sum(self.call_counts.values()),
            "service_calls": self.call_counts,
            "method_calls": self.method_calls
        }
    
    def reset(self):
        """Reset all metrics"""
        self.call_counts.clear()
        self.method_calls.clear()


# Global metrics instance for testing
mock_metrics = MockServiceMetrics()