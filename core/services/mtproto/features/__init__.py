"""
MTProto Features - DEPRECATED - Use core.marketplace.services.mtproto

This package has been moved to core/marketplace/services/mtproto/
for proper separation of marketplace (paid) services.

For backward compatibility, imports are re-exported from the new location.

New location:
    from core.marketplace.services.mtproto import (
        BaseMTProtoMarketplaceService,
        MTProtoServicesManager,
        HistoryAccessService,
        MediaDownloadService,
    )

DEPRECATED imports (still work for backward compatibility):
    from core.services.mtproto.features import (
        BaseMTProtoService,        # -> BaseMTProtoMarketplaceService
        MTProtoFeaturesManager,    # -> MTProtoServicesManager
        HistoryAccessService,
        MediaDownloadService,
    )
"""

import warnings

# Re-export from new location for backward compatibility
from core.marketplace.services.mtproto.base_mtproto_marketplace_service import (
    BaseMTProtoMarketplaceService as BaseMTProtoService,
)
from core.marketplace.services.mtproto.mtproto_services_manager import (
    MTProtoServicesManager as MTProtoFeaturesManager,
)
from core.marketplace.services.mtproto.history_access_service import HistoryAccessService
from core.marketplace.services.mtproto.media_download_service import MediaDownloadService

# Emit deprecation warning on import
warnings.warn(
    "core.services.mtproto.features is deprecated. "
    "Use core.marketplace.services.mtproto instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "BaseMTProtoService",  # Alias for BaseMTProtoMarketplaceService
    "MTProtoFeaturesManager",  # Alias for MTProtoServicesManager
    "HistoryAccessService",
    "MediaDownloadService",
]

