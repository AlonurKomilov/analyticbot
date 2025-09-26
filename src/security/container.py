"""
🔒 Security Dependency Injection Container

Provides centralized access to security components with proper singleton management.
Replaces scattered SecurityManager instances across the application.
"""

from functools import lru_cache
from typing import Any, Dict

from .auth import SecurityManager
from .rbac import RBACManager


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
        """Get the singleton SecurityManager instance"""
        if self._security_manager is None:
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
    FastAPI dependency to get SecurityManager
    
    Usage:
        @app.get("/protected")
        async def endpoint(security: SecurityManager = Depends(get_security_manager)):
            ...
    """
    return _container.security_manager


def get_rbac_manager() -> RBACManager:
    """
    FastAPI dependency to get RBACManager
    
    Usage:
        @app.get("/admin")
        async def endpoint(rbac: RBACManager = Depends(get_rbac_manager)):
            ...
    """
    return _container.rbac_manager


def get_security_container() -> SecurityContainer:
    """Get the security container instance - for advanced use cases"""
    return _container