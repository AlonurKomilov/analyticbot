"""
Rate limiting interface for shared_kernel.
Prevents modules from directly depending on each other for rate limiting.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional

class IRateLimiter(ABC):
    @abstractmethod
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed within rate limits."""
        pass
    
    @abstractmethod
    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        """Get remaining requests in current window."""
        pass

class IHealthChecker(ABC):
    @abstractmethod
    async def check_health(self) -> Dict[str, str]:
        """Check system health status."""
        pass
    
    @abstractmethod
    async def check_database(self) -> bool:
        """Check database connectivity."""
        pass
