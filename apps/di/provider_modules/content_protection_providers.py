"""
Content Protection Service Providers

Factory functions for content protection services.
Includes image/video processing, watermarking, theft detection, and subscription management.
"""

import logging

logger = logging.getLogger(__name__)


def create_image_processor(**kwargs):
    """Create PIL image processor adapter"""
    try:
        from apps.bot.adapters.content import PILImageProcessor

        return PILImageProcessor()
    except ImportError as e:
        logger.warning(f"PIL image processor not available: {e}")
        return None


def create_video_processor(**kwargs):
    """Create FFmpeg video processor adapter"""
    try:
        from apps.bot.adapters.content import FFmpegVideoProcessor

        return FFmpegVideoProcessor()
    except ImportError as e:
        logger.warning(f"FFmpeg video processor not available: {e}")
        return None


def create_file_system_adapter(**kwargs):
    """Create local file system adapter"""
    try:
        from apps.bot.adapters.content import LocalFileSystem

        return LocalFileSystem()
    except ImportError as e:
        logger.warning(f"File system adapter not available: {e}")
        return None


def create_subscription_adapter(**kwargs):
    """
    Create subscription service adapter.

    ✅ Issue #3 Phase 1 (Oct 21, 2025): Replaced StubSubscriptionService with real
    SubscriptionAdapter that integrates with payment domain subscription service.
    """
    try:
        from apps.bot.adapters.content import SubscriptionAdapter
        from infra.services.payment import SubscriptionService

        # Get subscription service from infra layer (payment domain)
        # TODO: Inject payment_repository and payment_method_service via DI
        # For now, we'll create a basic subscription service
        # In production, this should come from payment container
        payment_repository = None  # Will be injected properly in payment container
        payment_method_service = None

        subscription_service = SubscriptionService(
            payment_repository=payment_repository,
            payment_method_service=payment_method_service,
        )

        return SubscriptionAdapter(subscription_service=subscription_service)

    except ImportError as e:
        logger.warning(
            f"SubscriptionAdapter not available, falling back to stub: {e}. "
            "This is expected if payment domain is not fully configured."
        )
        # Fallback to stub for backward compatibility
        try:
            from apps.bot.adapters.content import StubSubscriptionService

            return StubSubscriptionService()
        except ImportError:
            logger.error("Neither SubscriptionAdapter nor StubSubscriptionService available")
            return None


def create_theft_detector(**kwargs):
    """Create content theft detector service"""
    try:
        from core.services.bot.content.theft_detector import TheftDetectorService

        return TheftDetectorService()
    except ImportError as e:
        logger.warning(f"Theft detector service not available: {e}")
        return None


def create_watermark_service(image_processor=None, file_system=None, **kwargs):
    """Create watermark service for images"""
    try:
        from typing import cast

        from core.services.bot.content.protocols import FileSystemPort, ImageProcessorPort
        from core.services.bot.content.watermark_service import WatermarkService

        if not all([image_processor, file_system]):
            logger.warning("Cannot create watermark service: missing dependencies")
            return None

        return WatermarkService(
            image_processor=cast(ImageProcessorPort, image_processor),
            file_system=cast(FileSystemPort, file_system),
        )
    except ImportError as e:
        logger.warning(f"Watermark service not available: {e}")
        return None


def create_video_watermark_service(video_processor=None, file_system=None, **kwargs):
    """Create watermark service for videos"""
    try:
        from typing import cast

        from core.services.bot.content.protocols import FileSystemPort, VideoProcessorPort
        from core.services.bot.content.video_watermark_service import VideoWatermarkService

        if not all([video_processor, file_system]):
            logger.warning("Cannot create video watermark service: missing dependencies")
            return None

        return VideoWatermarkService(
            video_processor=cast(VideoProcessorPort, video_processor),
            file_system=cast(FileSystemPort, file_system),
        )
    except ImportError as e:
        logger.warning(f"Video watermark service not available: {e}")
        return None


def create_content_protection_service(
    watermark_service=None,
    video_watermark_service=None,
    theft_detector=None,
    subscription_adapter=None,
    file_system=None,
    **kwargs,
):
    """Create content protection orchestrator service"""
    try:
        from typing import cast

        from core.services.bot.content.content_protection_service import ContentProtectionService
        from core.services.bot.content.protocols import FileSystemPort, SubscriptionPort
        from core.services.bot.content.theft_detector import TheftDetectorService
        from core.services.bot.content.video_watermark_service import VideoWatermarkService
        from core.services.bot.content.watermark_service import WatermarkService

        if not all(
            [
                watermark_service,
                video_watermark_service,
                theft_detector,
                subscription_adapter,
                file_system,
            ]
        ):
            logger.warning("Cannot create content protection service: missing dependencies")
            return None

        return ContentProtectionService(
            watermark_service=cast(WatermarkService, watermark_service),
            video_watermark_service=cast(VideoWatermarkService, video_watermark_service),
            theft_detector=cast(TheftDetectorService, theft_detector),
            subscription_port=cast(SubscriptionPort, subscription_adapter),
            file_system=cast(FileSystemPort, file_system),
        )
    except ImportError as e:
        logger.warning(f"Content protection service not available: {e}")
        return None
