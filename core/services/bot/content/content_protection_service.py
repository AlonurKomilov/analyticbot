"""
Content Protection Service

Main orchestrator for content protection operations.
Combines watermarking, theft detection, and premium features.
"""

import time
from core.services.bot.content.models import (
    ContentProtectionRequest,
    ContentProtectionResponse,
    WatermarkResult,
)
from core.services.bot.content.watermark_service import WatermarkService
from core.services.bot.content.video_watermark_service import VideoWatermarkService
from core.services.bot.content.theft_detector import TheftDetectorService
from core.services.bot.content.protocols import SubscriptionPort, FileSystemPort


class ContentProtectionService:
    """
    Main service for content protection operations.

    Orchestrates:
    - Image watermarking
    - Video watermarking
    - Content theft detection
    - Premium feature access control
    """

    def __init__(
        self,
        watermark_service: WatermarkService,
        video_watermark_service: VideoWatermarkService,
        theft_detector: TheftDetectorService,
        subscription_port: SubscriptionPort,
        file_system: FileSystemPort,
    ) -> None:
        """
        Initialize content protection service.

        Args:
            watermark_service: Service for image watermarking
            video_watermark_service: Service for video watermarking
            theft_detector: Service for content theft detection
            subscription_port: Port for checking premium status
            file_system: Port for file system operations
        """
        self._watermark_service = watermark_service
        self._video_watermark_service = video_watermark_service
        self._theft_detector = theft_detector
        self._subscription_port = subscription_port
        self._file_system = file_system

    async def protect_content(
        self,
        request: ContentProtectionRequest,
    ) -> ContentProtectionResponse:
        """
        Apply content protection based on request.

        Args:
            request: Content protection request with configuration

        Returns:
            ContentProtectionResponse with results
        """
        start_time = time.time()

        try:
            # Check premium status if user_id provided
            has_premium = False
            if request.user_id is not None:
                has_premium = await self._subscription_port.check_premium_status(
                    request.user_id
                )

            # Handle different content types
            if request.content_type == "image":
                result = await self._protect_image(request, has_premium)
            elif request.content_type == "video":
                result = await self._protect_video(request, has_premium)
            elif request.content_type == "text":
                result = await self._protect_text(request)
            else:
                result = ContentProtectionResponse(
                    success=False,
                    error=f"Unsupported content type: {request.content_type}",
                )

            # Add total processing time
            result.total_processing_time_ms = (time.time() - start_time) * 1000

            return result

        except Exception as e:
            return ContentProtectionResponse(
                success=False,
                error=f"Content protection failed: {type(e).__name__}: {e}",
                total_processing_time_ms=(time.time() - start_time) * 1000,
            )

    async def _protect_image(
        self,
        request: ContentProtectionRequest,
        has_premium: bool,
    ) -> ContentProtectionResponse:
        """
        Protect image content with watermark.

        Args:
            request: Content protection request
            has_premium: Whether user has premium status

        Returns:
            ContentProtectionResponse with watermark result
        """
        if not request.watermark_config:
            return ContentProtectionResponse(
                success=False,
                error="Watermark configuration is required for image protection",
            )

        if not has_premium:
            return ContentProtectionResponse(
                success=False,
                error="Premium subscription required for watermarking",
            )

        # Apply watermark
        watermark_result = await self._watermark_service.add_watermark(
            image_path=request.file_path or "",
            config=request.watermark_config,
        )

        return ContentProtectionResponse(
            success=watermark_result.success,
            watermark_result=watermark_result,
            error=watermark_result.error if not watermark_result.success else None,
        )

    async def _protect_video(
        self,
        request: ContentProtectionRequest,
        has_premium: bool,
    ) -> ContentProtectionResponse:
        """
        Protect video content with watermark.

        Args:
            request: Content protection request
            has_premium: Whether user has premium status

        Returns:
            ContentProtectionResponse with watermark result
        """
        if not request.watermark_config:
            return ContentProtectionResponse(
                success=False,
                error="Watermark configuration is required for video protection",
            )

        if not has_premium:
            return ContentProtectionResponse(
                success=False,
                error="Premium subscription required for video watermarking",
            )

        # Apply watermark
        watermark_result = await self._video_watermark_service.add_watermark(
            video_path=request.file_path or "",
            config=request.watermark_config,
        )

        return ContentProtectionResponse(
            success=watermark_result.success,
            watermark_result=watermark_result,
            error=watermark_result.error if not watermark_result.success else None,
        )

    async def _protect_text(
        self,
        request: ContentProtectionRequest,
    ) -> ContentProtectionResponse:
        """
        Analyze text content for theft/spam.

        Args:
            request: Content protection request

        Returns:
            ContentProtectionResponse with theft analysis
        """
        if not request.check_theft:
            return ContentProtectionResponse(
                success=True,
                error="No theft detection requested for text content",
            )

        # Analyze content
        theft_analysis = await self._theft_detector.analyze_content(
            request.text_content or ""
        )

        return ContentProtectionResponse(
            success=True,
            theft_analysis=theft_analysis,
        )

    async def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old temporary files.

        Args:
            max_age_hours: Maximum age of files to keep in hours

        Returns:
            Number of files deleted
        """
        try:
            temp_dir = await self._file_system.create_temp_dir()
            return await self._file_system.cleanup_old_files(
                directory=temp_dir,
                max_age_hours=max_age_hours,
            )
        except Exception:
            # Cleanup failures shouldn't be critical
            return 0
