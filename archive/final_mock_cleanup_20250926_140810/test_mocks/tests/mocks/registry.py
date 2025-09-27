"""
Mock Registry for Centralized Service Management

Maintains a registry of all available mock services and their configurations.
"""

import logging
from typing import Any

from .base import BaseMockService

logger = logging.getLogger(__name__)


class MockRegistry:
    """
    Central registry for all mock services.

    Provides service discovery, registration, and lifecycle management.
    """

    def __init__(self):
        self._services: dict[str, type[BaseMockService]] = {}
        self._instances: dict[str, BaseMockService] = {}
        self._configurations: dict[str, dict[str, Any]] = {}

    def register_service(
        self,
        service_name: str,
        service_class: type[BaseMockService],
        config: dict[str, Any] | None = None,
    ) -> None:
        """Register a mock service with optional configuration"""
        self._services[service_name] = service_class
        if config:
            self._configurations[service_name] = config
        logger.info(f"Registered mock service: {service_name}")

    def get_service(self, service_name: str) -> BaseMockService | None:
        """Get an instance of a registered mock service"""
        if service_name in self._instances:
            return self._instances[service_name]

        if service_name not in self._services:
            logger.warning(f"Mock service not registered: {service_name}")
            return None

        try:
            service_class = self._services[service_name]
            config = self._configurations.get(service_name, {})

            # Create instance with configuration
            if config:
                instance = service_class(**config)
            else:
                instance = service_class()

            self._instances[service_name] = instance
            logger.info(f"Created mock service instance: {service_name}")
            return instance

        except Exception as e:
            logger.error(f"Failed to create mock service {service_name}: {e}")
            return None

    def list_services(self) -> list[str]:
        """List all registered mock services"""
        return list(self._services.keys())

    def reset_all(self) -> None:
        """Reset all mock service instances"""
        for instance in self._instances.values():
            instance.reset()
        logger.info("Reset all mock services")

    def clear_instances(self) -> None:
        """Clear all service instances (force recreation)"""
        self._instances.clear()
        logger.info("Cleared all mock service instances")

    def get_registry_info(self) -> dict[str, Any]:
        """Get registry information for debugging"""
        return {
            "registered_services": list(self._services.keys()),
            "active_instances": list(self._instances.keys()),
            "configurations": list(self._configurations.keys()),
        }


# Global registry instance
mock_registry = MockRegistry()
