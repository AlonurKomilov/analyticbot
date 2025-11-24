"""
Video Watermark Service

Business logic for video watermarking operations.
Coordinates with VideoProcessorPort for actual video manipulation.
"""

import time

from core.services.bot.content.models import (
    WatermarkConfig,
    WatermarkPosition,
    WatermarkResult,
)
from core.services.bot.content.protocols import FileSystemPort, VideoProcessorPort


class VideoWatermarkService:
    """
    Service for adding watermarks to videos.

    Handles position calculation for video watermarks and orchestrates
    the watermarking process through the VideoProcessorPort.
    """

    def __init__(
        self,
        video_processor: VideoProcessorPort,
        file_system: FileSystemPort,
    ) -> None:
        """
        Initialize video watermark service.

        Args:
            video_processor: Port for video processing operations
            file_system: Port for file system operations
        """
        self._video_processor = video_processor
        self._file_system = file_system

    async def add_watermark(
        self,
        video_path: str,
        config: WatermarkConfig,
    ) -> WatermarkResult:
        """
        Add watermark to a video.

        Args:
            video_path: Path to input video
            config: Watermark configuration

        Returns:
            WatermarkResult with success status and output path
        """
        start_time = time.time()

        try:
            # Validate inputs
            if not await self._file_system.file_exists(video_path):
                return WatermarkResult(
                    success=False,
                    error=f"Video file not found: {video_path}",
                )

            # Check if video processor is available (e.g., FFmpeg installed)
            if not await self._video_processor.check_availability():
                return WatermarkResult(
                    success=False,
                    error="Video processor not available (FFmpeg may not be installed)",
                )

            # Convert position to FFmpeg format
            ffmpeg_position = self._convert_position_to_ffmpeg(config.position)

            # Convert color to FFmpeg format
            ffmpeg_color = self._convert_color_to_ffmpeg(config.color)

            # Apply watermark through the video processor
            output_path = await self._video_processor.add_watermark(
                video_path=video_path,
                text=config.text,
                position=ffmpeg_position,
                font_size=config.font_size,
                color=ffmpeg_color,
                opacity=config.opacity,
            )

            processing_time = (time.time() - start_time) * 1000  # Convert to ms

            return WatermarkResult(
                success=True,
                output_path=output_path,
                processing_time_ms=processing_time,
            )

        except FileNotFoundError as e:
            return WatermarkResult(
                success=False,
                error=f"File not found: {e}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )
        except ValueError as e:
            return WatermarkResult(
                success=False,
                error=f"Invalid configuration: {e}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )
        except RuntimeError as e:
            return WatermarkResult(
                success=False,
                error=f"Video watermarking failed: {e}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return WatermarkResult(
                success=False,
                error=f"Unexpected error: {type(e).__name__}: {e}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def _convert_position_to_ffmpeg(
        self,
        position: WatermarkPosition,
    ) -> str:
        """
        Convert WatermarkPosition enum to FFmpeg position string.

        FFmpeg uses position expressions like:
        - "10:10" for top-left (x:y from top-left corner)
        - "W-w-10:10" for top-right (W=video width, w=text width)
        - "10:H-h-10" for bottom-left (H=video height, h=text height)
        - "(W-w)/2:(H-h)/2" for center

        Args:
            position: Watermark position enum

        Returns:
            FFmpeg position expression string
        """
        position_map = {
            WatermarkPosition.TOP_LEFT: "10:10",
            WatermarkPosition.TOP_RIGHT: "W-w-10:10",
            WatermarkPosition.BOTTOM_LEFT: "10:H-h-10",
            WatermarkPosition.BOTTOM_RIGHT: "W-w-10:H-h-10",
            WatermarkPosition.CENTER: "(W-w)/2:(H-h)/2",
        }

        return position_map[position]

    def _convert_color_to_ffmpeg(self, color: str) -> str:
        """
        Convert color string to FFmpeg-compatible format.

        Args:
            color: Color name or hex string

        Returns:
            FFmpeg color string (hex format with 0x prefix or named color)
        """
        # FFmpeg supports named colors and hex colors
        # For hex, it expects 0xRRGGBB format

        # Named colors (FFmpeg supports these)
        named_colors = {
            "white",
            "black",
            "red",
            "green",
            "blue",
            "yellow",
            "cyan",
            "magenta",
            "gray",
            "grey",
            "orange",
            "purple",
        }

        color_lower = color.lower().strip()

        # If it's a named color, return as-is
        if color_lower in named_colors:
            return color_lower

        # If it's hex, ensure proper format
        hex_color = color_lower.lstrip("#")
        if len(hex_color) == 6:
            # Validate hex
            try:
                int(hex_color, 16)
                return f"0x{hex_color.upper()}"
            except ValueError:
                # Invalid hex, fall back to white
                return "white"

        # Default to white if unknown
        return "white"
