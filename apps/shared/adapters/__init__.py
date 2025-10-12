"""
Shared Adapters - Framework-Independent Adapter Layer

Adapters in this module provide clean interfaces to core services
for both API and Bot layers. They handle service coordination and
provide user-friendly interfaces without framework dependencies.

Moved from apps.bot.services.adapters as part of Phase 2 Option B
to enable shared access and break cross-layer dependencies.
"""

from apps.shared.adapters.ml_coordinator import (
    MLCoordinatorProtocol,
    MLCoordinatorService,
    create_ml_coordinator,
)
from apps.shared.adapters.ml_facade import (
    BotMLFacadeService,
    create_bot_ml_facade,
)

__all__ = [
    "MLCoordinatorProtocol",
    "MLCoordinatorService",
    "create_ml_coordinator",
    "BotMLFacadeService",
    "create_bot_ml_facade",
]
