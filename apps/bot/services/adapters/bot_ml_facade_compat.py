"""
Backward Compatibility Wrapper for Bot ML Facade

DEPRECATED: This module is maintained for backward compatibility only.
New code should import from apps.shared.adapters instead.

Moved to apps.shared.adapters.ml_facade as part of Phase 2 Option B
to break API→Bot cross-dependencies and enable shared access.
"""

# Import from shared location for backward compatibility
from apps.shared.adapters.ml_facade import (
    BotMLFacadeService,
    create_bot_ml_facade,
)

__all__ = [
    "BotMLFacadeService",
    "create_bot_ml_facade",
]
