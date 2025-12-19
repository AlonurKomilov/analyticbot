"""
MTProto Features - Marketplace services for MTProto capabilities

Provides premium/paid MTProto features:
- History access (read channel history)
- Media download (download media from channels)
- And more...

All services integrate with the feature gate and usage tracking system.
"""

from core.services.mtproto.features.base_mtproto_service import BaseMTProtoService
from core.services.mtproto.features.mtproto_features_manager import MTProtoFeaturesManager
from core.services.mtproto.features.history_access_service import HistoryAccessService
from core.services.mtproto.features.media_download_service import MediaDownloadService

# Aliases for backward compatibility
BaseMTProtoMarketplaceService = BaseMTProtoService
MTProtoServicesManager = MTProtoFeaturesManager

__all__ = [
    "BaseMTProtoService",
    "BaseMTProtoMarketplaceService",  # Alias
    "MTProtoFeaturesManager",
    "MTProtoServicesManager",  # Alias
    "HistoryAccessService",
    "MediaDownloadService",
]
