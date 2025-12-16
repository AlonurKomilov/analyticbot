"""
MTProto Services Module
=======================

All MTProto/Telegram API related services:
- features: History access, media download, bulk export
- collection: Auto-collection, real-time message capture

Usage:
    from core.services.mtproto import MTProtoService
    from core.services.mtproto.features import HistoryAccessService, MediaDownloadService
"""

# Main MTProto service
from core.services.mtproto.mtproto_service import MTProtoService

# Feature services
from core.services.mtproto.features.mtproto_features_manager import MTProtoFeaturesManager
from core.services.mtproto.features.base_mtproto_service import BaseMTProtoService
from core.services.mtproto.features.history_access_service import HistoryAccessService
from core.services.mtproto.features.media_download_service import MediaDownloadService

__all__ = [
    "MTProtoService",
    "MTProtoFeaturesManager",
    "BaseMTProtoService",
    "HistoryAccessService",
    "MediaDownloadService",
]
