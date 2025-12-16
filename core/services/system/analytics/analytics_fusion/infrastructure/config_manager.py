"""
Config Manager
=============

Configuration management for analytics fusion microservices.
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Configuration for individual services"""

    service_name: str
    enabled: bool = True
    timeout_seconds: int = 300
    retry_attempts: int = 3
    cache_enabled: bool = True
    settings: dict[str, Any] | None = None


@dataclass
class InfrastructureConfig:
    """Configuration for infrastructure components"""

    data_access: dict[str, Any] | None = None
    cache: dict[str, Any] | None = None
    logging: dict[str, Any] | None = None


class ConfigManager:
    """Configuration manager for analytics microservices"""

    def __init__(self):
        self.service_configs: dict[str, ServiceConfig] = {}
        self.infrastructure_config = InfrastructureConfig()

        # Initialize default configurations
        self._initialize_default_configs()

        logger.info("⚙️ Config Manager initialized")

    def get_service_config(self, service_name: str) -> ServiceConfig:
        """Get configuration for a service"""
        return self.service_configs.get(service_name, ServiceConfig(service_name))

    def set_service_config(self, service_name: str, config: ServiceConfig):
        """Set configuration for a service"""
        self.service_configs[service_name] = config

    def _initialize_default_configs(self):
        """Initialize default configurations"""
        services = [
            "core",
            "reporting",
            "intelligence",
            "monitoring",
            "optimization",
            "orchestrator",
        ]

        for service in services:
            self.service_configs[service] = ServiceConfig(
                service_name=service,
                enabled=True,
                timeout_seconds=300,
                retry_attempts=3,
                cache_enabled=True,
                settings={},
            )
