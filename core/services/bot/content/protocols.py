"""
Protocol Interfaces (Ports) for Content Protection

These protocols define the interfaces for external dependencies, allowing
the core business logic to remain framework-agnostic.

Adapters (implementations) will be in the apps/bot/adapters/ layer.
"""

from typing import Protocol


class ImageProcessorPort(Protocol):
    """
    Port for image processing operations.

    Implementations might use PIL/Pillow, ImageMagick, or cloud services.
    """

    async def add_watermark(
        self,
        image_path: str,
        text: str,
        position: tuple[int, int],
        font_size: int,
        color: tuple[int, int, int, int],  # RGBA
        shadow: bool,
    ) -> str:
        """
        Add watermark to an image.

        Args:
            image_path: Path to input image file
            text: Watermark text to add
            position: (x, y) pixel coordinates for watermark
            font_size: Font size in points
            color: RGBA color tuple (0-255 each)
            shadow: Whether to add shadow effect

        Returns:
            Path to the watermarked output image

        Raises:
            FileNotFoundError: If image_path doesn't exist
            ValueError: If image format is unsupported
            RuntimeError: If watermarking fails
        """
        ...


class VideoProcessorPort(Protocol):
    """
    Port for video processing operations.

    Implementations might use FFmpeg, cloud video services, etc.
    """

    async def add_watermark(
        self,
        video_path: str,
        text: str,
        position: str,  # FFmpeg position format (e.g., "10:10", "W-w-10:10")
        font_size: int,
        color: str,  # Hex color or color name
        opacity: float,  # 0.0 to 1.0
    ) -> str:
        """
        Add watermark to a video.

        Args:
            video_path: Path to input video file
            text: Watermark text to add
            position: Position string in FFmpeg format
            font_size: Font size in points
            color: Color in hex format (e.g., "0xFFFFFF") or name
            opacity: Transparency level (0.0 = transparent, 1.0 = opaque)

        Returns:
            Path to the watermarked output video

        Raises:
            FileNotFoundError: If video_path doesn't exist
            ValueError: If video format is unsupported
            RuntimeError: If watermarking fails (e.g., FFmpeg not installed)
        """
        ...

    async def check_availability(self) -> bool:
        """
        Check if video processor is available.

        For FFmpeg, checks if the binary is installed and accessible.

        Returns:
            True if video processing is available, False otherwise
        """
        ...


class FileSystemPort(Protocol):
    """
    Port for file system operations.

    Abstracts file system access to allow different storage backends
    (local, cloud, network storage, etc.).
    """

    async def create_temp_dir(self) -> str:
        """
        Create a temporary directory for processing files.

        Returns:
            Absolute path to the created temporary directory

        Raises:
            RuntimeError: If directory creation fails
        """
        ...

    async def cleanup_old_files(
        self,
        directory: str,
        max_age_hours: int,
    ) -> int:
        """
        Remove files older than specified age from directory.

        Args:
            directory: Path to directory to clean
            max_age_hours: Maximum age of files to keep in hours

        Returns:
            Number of files deleted

        Raises:
            FileNotFoundError: If directory doesn't exist
            PermissionError: If lacking permissions to delete files
        """
        ...

    def generate_unique_filename(
        self,
        prefix: str,
        extension: str,
    ) -> str:
        """
        Generate a unique filename.

        Args:
            prefix: Filename prefix
            extension: File extension (without dot)

        Returns:
            Unique filename (not full path)

        Examples:
            >>> fs.generate_unique_filename("watermark", "jpg")
            "watermark_20251015_143022_a3f9b2.jpg"
        """
        ...

    async def file_exists(self, path: str) -> bool:
        """
        Check if a file exists.

        Args:
            path: Path to file

        Returns:
            True if file exists, False otherwise
        """
        ...

    async def get_file_size(self, path: str) -> int:
        """
        Get file size in bytes.

        Args:
            path: Path to file

        Returns:
            File size in bytes

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        ...


class SubscriptionPort(Protocol):
    """
    Port for subscription/premium status checking.

    This should integrate with the payment domain services.
    """

    async def check_premium_status(self, user_id: int) -> bool:
        """
        Check if a user has active premium subscription.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user has active premium subscription, False otherwise
        """
        ...

    async def get_user_tier(
        self,
        user_id: int,
    ) -> str:
        """
        Get user's subscription tier.

        Args:
            user_id: Telegram user ID

        Returns:
            Tier name: "free", "starter", "pro", or "enterprise"
        """
        ...
