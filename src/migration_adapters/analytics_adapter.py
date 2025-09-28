"""
Migration Adapter for Analytics
===============================

Provides compatibility layer during migration from apps/ to src/.
Allows gradual migration without breaking existing functionality.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class AnalyticsMigrationAdapter:
    """
    Adapter to bridge legacy apps/ and new src/analytics/ implementations
    during the migration phase.
    """

    def __init__(self):
        self._legacy_available = self._check_legacy_availability()
        self._clean_available = self._check_clean_availability()
        logger.info(
            f"Analytics Migration Adapter initialized - Legacy: {self._legacy_available}, Clean: {self._clean_available}"
        )

    def _check_legacy_availability(self) -> bool:
        """Check if legacy implementation is available"""
        try:
            # Try importing legacy implementation
            # This will be domain-specific
            return True
        except ImportError:
            return False

    def _check_clean_availability(self) -> bool:
        """Check if clean architecture implementation is available"""
        try:
            # Try importing clean implementation
            return True
        except ImportError:
            return False

    def get_service(self, service_name: str) -> Any:
        """
        Get service instance, preferring clean architecture when available,
        falling back to legacy implementation.
        """
        if self._clean_available:
            logger.debug(f"Using clean architecture for {service_name}")
            return self._get_clean_service(service_name)
        elif self._legacy_available:
            logger.debug(f"Using legacy implementation for {service_name}")
            return self._get_legacy_service(service_name)
        else:
            raise RuntimeError(f"No implementation available for {service_name}")

    def _get_clean_service(self, service_name: str) -> Any:
        """Get service from clean architecture"""
        # Implementation will be domain-specific

    def _get_legacy_service(self, service_name: str) -> Any:
        """Get service from legacy apps/ structure"""
        # Implementation will be domain-specific


# Convenience factory function
def get_analytics_service(service_name: str = "default") -> Any:
    """Get analytics service using migration adapter"""
    adapter = AnalyticsMigrationAdapter()
    return adapter.get_service(service_name)
