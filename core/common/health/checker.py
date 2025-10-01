"""
Health Checker Bridge - Backward Compatibility

This module provides backward compatibility for code that still
imports health_checker from core.common.health.checker.

The actual implementation has been moved to:
apps/api/services/health_service.py

This follows clean architecture principles:
- Core layer: Domain models only (health.models)
- Apps layer: Framework-specific services (health_service)
"""

import logging
import warnings

logger = logging.getLogger(__name__)

# Issue deprecation warning
warnings.warn(
    "Importing health_checker from core.common.health.checker is deprecated. "
    "Use 'from apps.api.services.health_service import health_service' instead. "
    "The health checker has been moved to the apps layer to comply with clean architecture.",
    DeprecationWarning,
    stacklevel=2,
)

logger.warning(
    "🚨 DEPRECATED: core.common.health.checker.health_checker is deprecated. "
    "Use apps.api.services.health_service.health_service instead."
)

try:
    # Provide backward compatibility by importing from the new location
    from apps.api.services.health_service import health_service as health_checker

    logger.info(
        "✅ Health checker bridge: Successfully imported from apps.api.services.health_service"
    )

except ImportError as e:
    logger.error(f"❌ Health checker bridge failed: {e}")

    # Fallback stub to prevent import errors
    class HealthCheckerStub:
        """Stub health checker to prevent import errors"""

        def __init__(self):
            logger.error("Health checker not available - using stub")

        async def get_system_health(self):
            return {"status": "unknown", "error": "Health checker not available"}

    health_checker = HealthCheckerStub()

# Export for backward compatibility
__all__ = ["health_checker"]
