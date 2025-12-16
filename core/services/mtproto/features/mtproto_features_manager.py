"""
MTProto Features Manager - Coordinates marketplace services with MTProto operations

This manager:
1. Initializes MTProto service instances
2. Checks feature access before execution
3. Routes requests to appropriate services
4. Logs usage for billing/quotas
"""

import logging
from typing import Any

from core.services.system.feature_gate_service import FeatureGateService
from core.services.mtproto.features.history_access_service import HistoryAccessService
from core.services.mtproto.features.media_download_service import MediaDownloadService
from infra.db.repositories.marketplace_service_repository import (
    MarketplaceServiceRepository,
)


logger = logging.getLogger(__name__)


class MTProtoFeaturesManager:
    """
    Manager for marketplace MTProto services.
    
    Coordinates between MTProto operations and marketplace services:
    - Initializes service instances
    - Provides easy access to services
    - Handles feature gate integration
    """

    def __init__(
        self,
        user_id: int,
        mtproto_client: Any,
        feature_gate_service: FeatureGateService,
        marketplace_repo: MarketplaceServiceRepository,
    ):
        """
        Initialize MTProto features manager.
        
        Args:
            user_id: User's ID
            mtproto_client: MTProto client instance
            feature_gate_service: Feature gate service
            marketplace_repo: Marketplace repository
        """
        self.user_id = user_id
        self.mtproto_client = mtproto_client
        self.feature_gate = feature_gate_service
        self.marketplace_repo = marketplace_repo
        
        # Initialize service instances
        self.history_access = HistoryAccessService(
            user_id=user_id,
            feature_gate_service=feature_gate_service,
            marketplace_repo=marketplace_repo,
            mtproto_client=mtproto_client,
        )
        
        self.media_download = MediaDownloadService(
            user_id=user_id,
            feature_gate_service=feature_gate_service,
            marketplace_repo=marketplace_repo,
            mtproto_client=mtproto_client,
        )

    async def fetch_full_history(
        self,
        channel_id: int | str,
        limit: int = 1000,
        offset_id: int = 0,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Fetch full channel history using history access service.
        
        This automatically checks feature access and logs usage.
        
        Args:
            channel_id: Channel/chat ID
            limit: Maximum messages to fetch
            offset_id: Start from this message ID
            **kwargs: Additional parameters (min_date, max_date, search)
            
        Returns:
            dict with messages and metadata
        """
        return await self.history_access.run(
            channel_id=channel_id,
            limit=limit,
            offset_id=offset_id,
            **kwargs,
        )

    async def download_media(
        self,
        channel_id: int | str,
        limit: int = 100,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Download media files from channel.
        
        Args:
            channel_id: Channel/chat ID
            limit: Maximum files to download
            **kwargs: Additional parameters (message_ids, media_types, dates)
            
        Returns:
            dict with download results
        """
        return await self.media_download.run(
            channel_id=channel_id,
            limit=limit,
            **kwargs,
        )

    async def is_history_access_available(self) -> bool:
        """
        Check if history access service is available for user.
        
        Returns:
            True if service is accessible
        """
        return await self.history_access.is_available()

    async def is_media_download_available(self) -> bool:
        """
        Check if media download service is available for user.
        
        Returns:
            True if service is accessible
        """
        return await self.media_download.is_available()

    async def get_active_services(self) -> list[str]:
        """
        Get list of active MTProto service keys for this user.
        
        Returns:
            List of service keys (e.g., ['mtproto_history_access', 'mtproto_media_download'])
        """
        active_services = []
        
        # Check each service
        services_to_check = [
            "mtproto_history_access",
            "mtproto_media_download",
            "mtproto_bulk_export",
            "mtproto_auto_collection",
        ]
        
        for service_key in services_to_check:
            has_access, _ = await self.feature_gate.check_access(
                user_id=self.user_id,
                service_key=service_key,
            )
            if has_access:
                active_services.append(service_key)
        
        return active_services

    async def get_usage_summary(self, days: int = 30) -> dict:
        """
        Get usage summary for all MTProto services.
        
        Args:
            days: Number of days to look back
            
        Returns:
            dict with usage statistics per service
        """
        summary = {}
        
        # History access stats
        if await self.is_history_access_available():
            history_stats = await self.history_access.get_usage_stats(days=days)
            if history_stats:
                summary["history_access"] = history_stats
        
        # Media download stats (would add similar method to MediaDownloadService)
        # For now, just indicate it's available
        if await self.is_media_download_available():
            summary["media_download"] = {
                "service_key": "mtproto_media_download",
                "available": True,
            }
        
        return summary

    async def check_quota(self, service_key: str) -> tuple[bool, str | None]:
        """
        Check if user is within quota for a service.
        
        Args:
            service_key: Service to check quota for
            
        Returns:
            Tuple of (within_quota, message_if_exceeded)
        """
        return await self.feature_gate.check_quota(
            user_id=self.user_id,
            service_key=service_key,
        )
