"""
🔒 Security Dependency Injection Container

Provides centralized access to security components with proper singleton management.
Replaces scattered SecurityManager instances across the application.
"""

import logging
from urllib.parse import urlparse

from config.settings import settings
from infra.security.adapters import RedisCache

from .auth import SecurityManager
from .rbac import RBACManager

logger = logging.getLogger(__name__)


class SecurityContainer:
    """
    Centralized security dependency container

    Ensures single instances of security components across the application
    and provides clean dependency injection for FastAPI routes.
    """

    _instance = None
    _security_manager = None
    _rbac_manager = None

    def __new__(cls):
        """Singleton pattern for the container itself"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def security_manager(self) -> SecurityManager:
        """Get the singleton SecurityManager instance with Redis cache"""
        if self._security_manager is None:
            # Parse Redis URL to get connection details
            redis_url = settings.REDIS_URL
            try:
                parsed = urlparse(redis_url)
                host = parsed.hostname or "localhost"
                port = parsed.port or 10200
                # Extract DB from path (e.g., /0 -> 0)
                db = int(parsed.path.lstrip("/")) if parsed.path and parsed.path != "/" else 0

                # Initialize Redis cache adapter
                cache = RedisCache(host=host, port=port, db=db)
                logger.info(f"🔌 Initialized SecurityManager with Redis cache: {host}:{port}/{db}")

                # Initialize SecurityManager with cache
                self._security_manager = SecurityManager(cache=cache)
            except Exception as e:
                logger.error(f"❌ Failed to initialize Redis cache for SecurityManager: {e}")
                logger.warning("⚠️ Falling back to in-memory cache (tokens will not persist!)")
                # Fallback to no cache (memory cache inside SecurityManager)
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
