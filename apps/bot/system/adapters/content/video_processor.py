"""
FFmpeg Video Processor Adapter

Implements VideoProcessorPort using FFmpeg subprocess.
"""

import asyncio
import shutil
from pathlib import Path
from uuid import uuid4


class FFmpegVideoProcessor:
    """
    FFmpeg implementation of VideoProcessorPort.

    Handles video watermarking using FFmpeg command-line tool.
    """

    def __init__(self, temp_dir: str = "/tmp/analyticbot_media") -> None:
        """
        Initialize FFmpeg video processor.

        Args:
            temp_dir: Directory for temporary files
        """
        self._temp_dir = Path(temp_dir)
        self._temp_dir.mkdir(exist_ok=True, parents=True)

    async def add_watermark(
        self,
        video_path: str,
        text: str,
        position: str,
        font_size: int,
        color: str,
        opacity: float,
    ) -> str:
        """
        Add watermark to a video using FFmpeg.

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
            RuntimeError: If watermarking fails
        """
        input_path = Path(video_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Generate output filename
        output_filename = f"watermarked_{uuid4().hex[:8]}_{input_path.stem}.mp4"
        output_path = self._temp_dir / output_filename

        try:
            # Build FFmpeg drawtext filter
            # Note: Escape special characters in text
            escaped_text = text.replace("'", "\\'").replace(":", "\\:")

            # Build the filter string
            filter_str = (
                f"drawtext=text='{escaped_text}':"
                f"fontcolor={color}@{opacity}:"
                f"fontsize={font_size}:"
                f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"{position}"
            )

            # Build FFmpeg command
            cmd = [
                "ffmpeg",
                "-i", str(input_path),
                "-vf", filter_str,
                "-codec:a", "copy",  # Copy audio without re-encoding
                "-y",  # Overwrite output file
                str(output_path),
            ]

            # Execute FFmpeg
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(
                    f"FFmpeg failed with code {process.returncode}: {error_msg}"
                )

            return str(output_path)

        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg to use video watermarking."
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add watermark to video: {e}")

    async def check_availability(self) -> bool:
        """
        Check if FFmpeg is installed and available.

        Returns:
            True if FFmpeg is available, False otherwise
        """
        return shutil.which("ffmpeg") is not None
