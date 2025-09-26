"""
Mock Factory for Dynamic Service Creation

Provides factory methods for creating and managing mock services.
"""

from typing import Dict, Any, Optional, TypeVar, Type
import logging
from .registry import mock_registry, MockRegistry
from .base import BaseMockService

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseMockService)


class MockFactory:
    """
    Factory for creating and managing mock services.
    
    Provides a clean interface for production code to create mock services
    without knowing implementation details.
    """
    
    def __init__(self, registry: Optional[MockRegistry] = None):
        self.registry = registry or mock_registry
    
    def create_service(self, service_name: str, **kwargs) -> Optional[BaseMockService]:
        """Create a mock service by name with optional parameters"""
        service = self.registry.get_service(service_name)
        if service and kwargs:
            # Apply additional configuration if provided
            for key, value in kwargs.items():
                if hasattr(service, key):
                    setattr(service, key, value)
        return service
    
    def create_analytics_service(self, **config) -> Optional[BaseMockService]:
        """Create mock analytics service with configuration"""
        return self.create_service("analytics", **config)
    
    def create_payment_service(self, **config) -> Optional[BaseMockService]:
        """Create mock payment service with configuration"""
        return self.create_service("payment", **config)
    
    def create_email_service(self, **config) -> Optional[BaseMockService]:
        """Create mock email service with configuration"""
        return self.create_service("email", **config)
    
    def create_telegram_service(self, **config) -> Optional[BaseMockService]:
        """Create mock telegram service with configuration"""
        return self.create_service("telegram", **config)
    
    def create_auth_service(self, **config) -> Optional[BaseMockService]:
        """Create mock auth service with configuration"""
        return self.create_service("auth", **config)
    
    def create_admin_service(self, **config) -> Optional[BaseMockService]:
        """Create mock admin service with configuration"""
        return self.create_service("admin", **config)
    
    def create_ai_service(self, **config) -> Optional[BaseMockService]:
        """Create mock AI service with configuration"""
        return self.create_service("ai", **config)
    
    def create_demo_data_service(self, **config) -> Optional[BaseMockService]:
        """Create mock demo data service with configuration"""
        return self.create_service("demo_data", **config)
    
    def create_database_service(self, **config) -> Optional[BaseMockService]:
        """Create mock database service with configuration"""
        return self.create_service("database", **config)
    
    def create_testing_suite(self, services: Optional[list] = None) -> Dict[str, BaseMockService]:
        """
        Create a complete testing suite with specified services.
        
        Args:
            services: List of service names to create. If None, creates all available.
            
        Returns:
            Dictionary of service_name -> service_instance
        """
        if services is None:
            services = self.registry.list_services()
        
        suite = {}
        for service_name in services:
            service = self.create_service(service_name)
            if service:
                suite[service_name] = service
            else:
                logger.warning(f"Failed to create service for testing suite: {service_name}")
        
        logger.info(f"Created testing suite with {len(suite)} services")
        return suite
    
    def reset_all_services(self) -> None:
        """Reset all services in the registry"""
        self.registry.reset_all()
    
    def get_factory_info(self) -> Dict[str, Any]:
        """Get factory information for debugging"""
        return {
            "registry_info": self.registry.get_registry_info(),
            "available_methods": [
                method for method in dir(self) 
                if method.startswith('create_') and not method.startswith('_')
            ]
        }


# Global factory instance
mock_factory = MockFactory()