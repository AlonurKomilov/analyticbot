# apps/shared/protocols.py
"""
Application Layer Protocols for Repository Access
Clean abstraction layer that prevents direct infra imports
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol, TypeVar

# Import core protocols (this is allowed - apps can import from core)
from core.repositories.interfaces import AdminRepository, ChannelRepository, UserRepository


# Create AnalyticsRepository protocol stub if not available
class AnalyticsRepository(Protocol):
    """Analytics repository protocol"""

    async def get_analytics_data(self, **kwargs) -> Any:
        """Get analytics data"""
        ...


__all__ = [
    "DatabaseConnectionProtocol",
    "RepositoryFactoryProtocol",
    "DatabaseManagerProtocol",
    "CacheProtocol",
    "PerformanceTimerProtocol",
    "ChartRenderingProtocol",
]

T = TypeVar("T")


class DatabaseConnectionProtocol(Protocol):
    """Protocol for database connections (asyncpg.Pool abstraction)"""

    async def acquire(self):
        """Acquire a connection from the pool"""
        ...

    async def release(self, connection):
        """Release connection back to pool"""
        ...

    async def execute(self, query: str, *args):
        """Execute query and return result"""
        ...

    async def fetch(self, query: str, *args):
        """Fetch multiple rows"""
        ...

    async def fetchrow(self, query: str, *args):
        """Fetch single row"""
        ...

    async def close(self):
        """Close the pool"""
        ...


class DatabaseManagerProtocol(Protocol):
    """Protocol for database manager abstraction"""

    async def initialize(self) -> None:
        """Initialize database connections"""
        ...

    async def get_connection(self):
        """Get database connection"""
        ...

    async def execute_query(self, query: str, *args):
        """Execute database query"""
        ...

    async def health_check(self) -> bool:
        """Check database health"""
        ...

    async def close(self) -> None:
        """Close database connections"""
        ...


class RepositoryFactoryProtocol(Protocol):
    """Protocol for creating repository instances without direct infra imports"""

    async def create_user_repository(self) -> UserRepository:
        """Create user repository instance"""
        ...

    async def create_channel_repository(self) -> ChannelRepository:
        """Create channel repository instance"""
        ...

    async def create_analytics_repository(self) -> AnalyticsRepository:
        """Create analytics repository instance"""
        ...

    async def create_admin_repository(self) -> AdminRepository:
        """Create admin repository instance"""
        ...


class CacheProtocol(Protocol):
    """Protocol for caching operations"""

    async def get(self, key: str) -> str | None:
        """Get value from cache"""
        ...

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Set value in cache"""
        ...

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        ...

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        ...


class PerformanceTimerProtocol(Protocol):
    """Protocol for performance timing without infra imports"""

    async def measure(self, operation_name: str):
        """Measure operation performance (returns async context manager)"""
        ...

    def record_timing(self, operation: str, duration_ms: float) -> None:
        """Record timing measurement"""
        ...


class ChartRenderingProtocol(Protocol):
    """Protocol for chart rendering without infra imports"""

    async def create_engagement_chart(self, data: dict) -> bytes:
        """Create engagement chart"""
        ...

    async def create_growth_chart(self, data: dict) -> bytes:
        """Create growth chart"""
        ...

    async def create_analytics_report(self, data: dict) -> bytes:
        """Create analytics report"""
        ...


class ChartServiceProtocol(Protocol):
    """Protocol for chart service operations"""

    def is_available(self) -> bool:
        """Check if chart rendering is available"""
        ...

    def render_growth_chart(self, data: dict[str, Any]) -> bytes:
        """Render growth data as PNG chart"""
        ...

    def render_reach_chart(self, data: dict[str, Any]) -> bytes:
        """Render reach data as PNG chart"""
        ...

    def render_sources_chart(self, data: dict[str, Any]) -> bytes:
        """Render sources data as PNG chart"""
        ...

    def get_supported_formats(self) -> list[str]:
        """Get list of supported chart formats"""
        ...

    def get_supported_chart_types(self) -> list[str]:
        """Get list of supported chart types"""
        ...


# Application Service Abstractions
class ApplicationServiceBase(ABC):
    """Base class for application services with proper DI support"""

    def __init__(self, **dependencies):
        self._dependencies = dependencies

    def get_dependency(self, name: str, default=None):
        """Get injected dependency by name"""
        return self._dependencies.get(name, default)


class RepositoryProvider(ABC):
    """Abstract base for repository providers"""

    @abstractmethod
    async def get_user_repository(self) -> UserRepository:
        """Get user repository"""
        ...

    @abstractmethod
    async def get_channel_repository(self) -> ChannelRepository:
        """Get channel repository"""
        ...

    @abstractmethod
    async def get_analytics_repository(self) -> AnalyticsRepository:
        """Get analytics repository"""
        ...
