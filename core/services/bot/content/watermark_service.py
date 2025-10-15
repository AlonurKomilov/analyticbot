"""
Watermark Service

Pure business logic for image watermarking operations.
Coordinates with ImageProcessorPort for actual image manipulation.
"""

import time
from core.services.bot.content.models import (
    WatermarkConfig,
    WatermarkResult,
    WatermarkPosition,
)
from core.services.bot.content.protocols import ImageProcessorPort, FileSystemPort


class WatermarkService:
    """
    Service for adding watermarks to images.

    Handles watermark position calculation, color conversion,
    and orchestrates the watermarking process through the ImageProcessorPort.
    """

    def __init__(
        self,
        image_processor: ImageProcessorPort,
        file_system: FileSystemPort,
    ) -> None:
        """
        Initialize watermark service.

        Args:
            image_processor: Port for image processing operations
            file_system: Port for file system operations
        """
        self._image_processor = image_processor
        self._file_system = file_system

    async def add_watermark(
        self,
        image_path: str,
        config: WatermarkConfig,
    ) -> WatermarkResult:
        """
        Add watermark to an image.

        Args:
            image_path: Path to input image
            config: Watermark configuration

        Returns:
            WatermarkResult with success status and output path
        """
        start_time = time.time()

        try:
            # Validate inputs
            if not await self._file_system.file_exists(image_path):
                return WatermarkResult(
                    success=False,
                    error=f"Image file not found: {image_path}",
                )

            # Get image dimensions (needed for position calculation)
            # For now, we'll delegate position calculation to the adapter
            # In a more sophisticated version, we might load image metadata here

            # Convert color from hex/name to RGBA
            rgba_color = self._convert_color_to_rgba(
                config.color,
                config.opacity,
            )

            # Calculate position
            # Note: For now, we'll use symbolic positions and let the adapter
            # handle the actual pixel calculation since it has access to PIL
            position_coords = self._get_position_hint(config.position)

            # Apply watermark through the image processor
            output_path = await self._image_processor.add_watermark(
                image_path=image_path,
                text=config.text,
                position=position_coords,
                font_size=config.font_size,
                color=rgba_color,
                shadow=config.shadow,
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
                error=f"Watermarking failed: {e}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return WatermarkResult(
                success=False,
                error=f"Unexpected error: {type(e).__name__}: {e}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def _convert_color_to_rgba(
        self,
        color: str,
        opacity: float,
    ) -> tuple[int, int, int, int]:
        """
        Convert color string to RGBA tuple.

        Args:
            color: Color name ("white", "black", etc.) or hex ("#RRGGBB" or "RRGGBB")
            opacity: Opacity value from 0.0 to 1.0

        Returns:
            RGBA tuple with values 0-255

        Raises:
            ValueError: If color format is invalid
        """
        # Named colors (basic palette)
        named_colors = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "gray": (128, 128, 128),
            "grey": (128, 128, 128),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
        }

        color_lower = color.lower().strip()

        # Check if it's a named color
        if color_lower in named_colors:
            r, g, b = named_colors[color_lower]
        else:
            # Try to parse as hex
            hex_color = color_lower.lstrip("#")

            if len(hex_color) == 6:
                try:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                except ValueError:
                    raise ValueError(
                        f"Invalid hex color format: {color}. "
                        "Expected #RRGGBB or RRGGBB"
                    )
            else:
                raise ValueError(
                    f"Unknown color: {color}. "
                    "Use named color or hex format (#RRGGBB)"
                )

        # Convert opacity to alpha channel (0-255)
        alpha = int(opacity * 255)

        return (r, g, b, alpha)

    def _get_position_hint(
        self,
        position: WatermarkPosition,
    ) -> tuple[int, int]:
        """
        Get position hint for the adapter.

        Since we don't have image dimensions at this layer,
        we return symbolic coordinates that the adapter will interpret.

        Args:
            position: Watermark position enum

        Returns:
            Tuple of (x, y) where negative values indicate
            relative positioning from right/bottom
        """
        # Position hints (adapter will translate to actual pixels)
        position_map = {
            WatermarkPosition.TOP_LEFT: (10, 10),
            WatermarkPosition.TOP_RIGHT: (-10, 10),  # Negative = from right
            WatermarkPosition.BOTTOM_LEFT: (10, -10),  # Negative = from bottom
            WatermarkPosition.BOTTOM_RIGHT: (-10, -10),
            WatermarkPosition.CENTER: (0, 0),  # Special: center
        }

        return position_map[position]
