"""
🔒 Security Dependency Injection Container

Provides centralized access to security components with proper singleton management.
Replaces scattered SecurityManager instances across the application.

ARCHITECTURE NOTE:
This module is in the core layer and should NOT import from infra layer.
Cache implementations (Redis, etc.) must be injected from the apps/di layer.
"""

import logging

from core.ports.security_ports import CachePort

from .auth import SecurityManager
from .rbac import RBACManager

logger = logging.getLogger(__name__)


class SecurityContainer:
    """
    Centralized security dependency container

    Ensures single instances of security components across the application
    and provides clean dependency injection for FastAPI routes.

    Cache implementation must be injected from the apps/di layer to maintain
    Clean Architecture (core doesn't depend on infra).
    """

    _instance = None
    _security_manager = None
    _rbac_manager = None
    _cache_port: CachePort | None = None

    def __new__(cls):
        """Singleton pattern for the container itself"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_cache_port(self, cache: CachePort) -> None:
        """
        Inject cache implementation from DI container (apps layer)

        This maintains Clean Architecture by allowing apps/di to provide
        the concrete Redis implementation while core only depends on the port.
        """
        self._cache_port = cache
        logger.info("✅ Cache port injected into SecurityContainer")

        # Reset managers to pick up new cache
        if self._security_manager:
            logger.info("🔄 Resetting SecurityManager to use new cache")
            self._security_manager = None
        if self._rbac_manager:
            logger.info("🔄 Resetting RBACManager to use new cache")
            self._rbac_manager = None

    @property
    def security_manager(self) -> SecurityManager:
        """Get the singleton SecurityManager instance"""
        if self._security_manager is None:
            if self._cache_port:
                logger.info("🔌 Initializing SecurityManager with injected cache port")
                self._security_manager = SecurityManager(cache=self._cache_port)
            else:
                logger.warning(
                    "⚠️ No cache port injected, SecurityManager will use in-memory fallback"
                )
                self._security_manager = SecurityManager()

        return self._security_manager

    @property
    def rbac_manager(self) -> RBACManager:
        """Get the singleton RBACManager instance"""
        if self._rbac_manager is None:
            self._rbac_manager = RBACManager()
        return self._rbac_manager

    def reset(self):
        """Reset all instances - useful for testing"""
        self._security_manager = None
        self._rbac_manager = None


# Global container instance
_container = SecurityContainer()


# FastAPI dependency functions - these replace the scattered get_security_manager functions
def get_security_manager() -> SecurityManager:
    """
    Get SecurityManager instance (for use in apps layer dependency injection)

    Note: This is a factory function for apps layer DI integration.
    No framework dependencies in core layer.
    """
    return _container.security_manager


def get_rbac_manager() -> RBACManager:
    """
    Get RBACManager instance (for use in apps layer dependency injection)

    Note: This is a factory function for apps layer DI integration.
    No framework dependencies in core layer.
    """
    return _container.rbac_manager


def get_security_container() -> SecurityContainer:
    """Get the security container instance - for advanced use cases"""
    return _container
