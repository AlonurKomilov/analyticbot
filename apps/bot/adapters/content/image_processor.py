"""
PIL/Pillow Image Processor Adapter

Implements ImageProcessorPort using PIL/Pillow library.
"""

from pathlib import Path
from uuid import uuid4
from PIL import Image, ImageDraw, ImageFont


class PILImageProcessor:
    """
    PIL/Pillow implementation of ImageProcessorPort.

    Handles image watermarking using the Python Imaging Library.
    """

    def __init__(self, temp_dir: str = "/tmp/analyticbot_media") -> None:
        """
        Initialize PIL image processor.

        Args:
            temp_dir: Directory for temporary files
        """
        self._temp_dir = Path(temp_dir)
        self._temp_dir.mkdir(exist_ok=True, parents=True)

    async def add_watermark(
        self,
        image_path: str,
        text: str,
        position: tuple[int, int],
        font_size: int,
        color: tuple[int, int, int, int],
        shadow: bool,
    ) -> str:
        """
        Add watermark to an image using PIL.

        Args:
            image_path: Path to input image file
            text: Watermark text to add
            position: (x, y) pixel coordinates hint (negative = from right/bottom)
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
        try:
            input_path = Path(image_path)
            if not input_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # Generate output filename
            output_filename = f"watermarked_{uuid4().hex[:8]}_{input_path.stem}.jpg"
            output_path = self._temp_dir / output_filename

            # Open and convert image to RGBA for transparency support
            image = Image.open(input_path)
            if image.mode != "RGBA":
                image = image.convert("RGBA")

            # Create transparent overlay for watermark
            overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            # Load font
            try:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    font_size,
                )
            except OSError:
                # Fallback to default font if custom font not available
                font = ImageFont.load_default()

            # Calculate text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Calculate actual position based on hints
            x, y = self._calculate_position(
                position_hint=position,
                image_width=image.width,
                image_height=image.height,
                text_width=text_width,
                text_height=text_height,
            )

            # Add shadow if enabled
            if shadow:
                shadow_color = (0, 0, 0, int(color[3] * 0.8))  # Darker shadow
                draw.text((x + 2, y + 2), text, font=font, fill=shadow_color)

            # Add main text with specified color
            draw.text((x, y), text, font=font, fill=color)

            # Composite watermark onto image
            watermarked = Image.alpha_composite(image, overlay)

            # Convert back to RGB for JPEG and save
            if watermarked.mode == "RGBA":
                watermarked = watermarked.convert("RGB")

            watermarked.save(str(output_path), "JPEG", quality=95)

            return str(output_path)

        except FileNotFoundError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to add watermark to image: {e}")

    def _calculate_position(
        self,
        position_hint: tuple[int, int],
        image_width: int,
        image_height: int,
        text_width: int,
        text_height: int,
    ) -> tuple[int, int]:
        """
        Calculate actual pixel position from hint.

        Args:
            position_hint: (x, y) hint where negative values = from right/bottom
            image_width: Width of image in pixels
            image_height: Height of image in pixels
            text_width: Width of text in pixels
            text_height: Height of text in pixels

        Returns:
            Actual (x, y) pixel coordinates
        """
        x_hint, y_hint = position_hint

        # Handle x coordinate
        if x_hint < 0:
            # Negative = from right edge
            x = image_width - text_width + x_hint
        elif x_hint == 0:
            # Zero = center
            x = (image_width - text_width) // 2
        else:
            # Positive = from left edge
            x = x_hint

        # Handle y coordinate
        if y_hint < 0:
            # Negative = from bottom edge
            y = image_height - text_height + y_hint
        elif y_hint == 0:
            # Zero = center
            y = (image_height - text_height) // 2
        else:
            # Positive = from top edge
            y = y_hint

        return (max(0, x), max(0, y))  # Ensure non-negative
