"""
Backward Compatibility Wrapper for ML Coordinator

DEPRECATED: This module is maintained for backward compatibility only.
New code should import from apps.shared.adapters instead.

Moved to apps.shared.adapters.ml_coordinator as part of Phase 2 Option B
to break API→Bot cross-dependencies and enable shared access.
"""

# Import from shared location for backward compatibility
from apps.shared.adapters.ml_coordinator import (
    MLCoordinatorProtocol,
    MLCoordinatorService,
    create_ml_coordinator,
)

__all__ = [
    "MLCoordinatorProtocol",
    "MLCoordinatorService",
    "create_ml_coordinator",
]
