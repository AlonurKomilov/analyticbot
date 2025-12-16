"""
MTProto Features - Pluggable marketplace services for MTProto operations

This package contains modular MTProto features that can be purchased
and activated through the marketplace services system.

Each feature integrates with:
- Feature gate service (access control)
- Usage logging (quota tracking)
- MTProto client (execution)

Services:
- BaseMTProtoService: Base class for all MTProto services
- MTProtoFeaturesManager: Manager for MTProto feature orchestration
- HistoryAccessService: Channel message history access
- MediaDownloadService: Media file download service
"""

from core.services.mtproto.features.base_mtproto_service import BaseMTProtoService
from core.services.mtproto.features.mtproto_features_manager import MTProtoFeaturesManager
from core.services.mtproto.features.history_access_service import HistoryAccessService
from core.services.mtproto.features.media_download_service import MediaDownloadService

__all__ = [
    "BaseMTProtoService",
    "MTProtoFeaturesManager",
    "HistoryAccessService",
    "MediaDownloadService",
]

