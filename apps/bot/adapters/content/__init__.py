"""Content Protection Adapters"""

from apps.bot.adapters.content.file_system import LocalFileSystem
from apps.bot.adapters.content.image_processor import PILImageProcessor
from apps.bot.adapters.content.subscription import StubSubscriptionService
from apps.bot.adapters.content.video_processor import FFmpegVideoProcessor

__all__ = [
    "PILImageProcessor",
    "FFmpegVideoProcessor",
    "LocalFileSystem",
    "StubSubscriptionService",
]
