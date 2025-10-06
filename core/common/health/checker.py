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

# Note: This bridge file violates clean architecture by importing from apps layer.
# This is a TEMPORARY backward compatibility layer that should be removed.
# New code should NOT import from this module.
# Instead, inject health service dependencies from the apps layer.


class HealthCheckerStub:
    """
    Stub health checker that prevents import errors.

    DEPRECATED: This is a backward compatibility stub.
    Health checking should be performed at the apps layer,
    not in the core domain layer.

    To properly implement health checking:
    1. Define a HealthCheckProtocol in core/ports/
    2. Implement it in apps/api/services/
    3. Inject the implementation via dependency injection
    """

    def __init__(self):
        logger.warning(
            "Using deprecated HealthCheckerStub. "
            "Health checking should be injected from apps layer via DI."
        )

    async def get_system_health(self):
        return {
            "status": "unknown",
            "error": "Health checker stub - inject real implementation via DI",
            "deprecated": True,
        }


# Provide stub instance for backward compatibility
health_checker = HealthCheckerStub()

# Export for backward compatibility
__all__ = ["health_checker"]
