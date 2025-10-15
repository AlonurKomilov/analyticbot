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
    WatermarkConfig,
    WatermarkResult,
    TheftAnalysis,
    ContentProtectionRequest,
    ContentProtectionResponse,
    WatermarkPosition,
    RiskLevel,
)

__all__ = [
    "WatermarkConfig",
    "WatermarkResult",
    "TheftAnalysis",
    "ContentProtectionRequest",
    "ContentProtectionResponse",
    "WatermarkPosition",
    "RiskLevel",
]
