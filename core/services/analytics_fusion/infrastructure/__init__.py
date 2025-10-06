"""
Infrastructure Services Package
===============================

Shared infrastructure components for analytics fusion microservices.
Provides common functionality like data access, caching, and configuration.
"""

from .cache_manager import CacheConfig, CacheKey, CacheManager
from .config_manager import ConfigManager, InfrastructureConfig, ServiceConfig
from .data_access import DataAccessConfig, DataAccessService, RepositoryManager

__all__ = [
    # Data Access
    "DataAccessService",
    "DataAccessConfig",
    "RepositoryManager",
    # Cache Management
    "CacheManager",
    "CacheConfig",
    "CacheKey",
    # Configuration
    "ConfigManager",
    "ServiceConfig",
    "InfrastructureConfig",
]

# Infrastructure metadata
__infrastructure__ = {
    "name": "analytics_fusion_infrastructure",
    "version": "1.0.0",
    "description": "Shared infrastructure for analytics microservices",
    "components": ["DataAccessService", "CacheManager", "ConfigManager"],
}
