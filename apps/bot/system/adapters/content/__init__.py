"""Content Protection Adapters"""

from apps.bot.system.adapters.content.file_system import LocalFileSystem
from apps.bot.system.adapters.content.image_processor import PILImageProcessor
from apps.bot.system.adapters.content.subscription import (
    StubSubscriptionService,  # Deprecated, for backward compatibility
    SubscriptionAdapter,
)
from apps.bot.system.adapters.content.video_processor import FFmpegVideoProcessor

__all__ = [
    "PILImageProcessor",
    "FFmpegVideoProcessor",
    "LocalFileSystem",
    "SubscriptionAdapter",
    "StubSubscriptionService",  # Deprecated
]
