"""
Content Protection Services Layer

This module provides Clean Architecture-based content protection services:
- Watermarking (image and video)
- Content theft detection
- Premium content features
- Custom emoji handling

All services are framework-agnostic and depend on protocols (ports) for
external dependencies like image processing, video processing, and file system operations.
"""

from core.services.bot.content.models import (
    ContentProtectionRequest,
    ContentProtectionResponse,
    RiskLevel,
    TheftAnalysis,
    WatermarkConfig,
    WatermarkPosition,
    WatermarkResult,
)
from core.services.bot.content.content_protection_service import ContentProtectionService
from core.services.bot.content.watermark_service import WatermarkService
from core.services.bot.content.video_watermark_service import VideoWatermarkService
from core.services.bot.content.theft_detector import TheftDetectorService

__all__ = [
    # Models
    "WatermarkConfig",
    "WatermarkResult",
    "TheftAnalysis",
    "ContentProtectionRequest",
    "ContentProtectionResponse",
    "WatermarkPosition",
    "RiskLevel",
    # Services
    "ContentProtectionService",
    "WatermarkService",
    "VideoWatermarkService",
    "TheftDetectorService",
]
