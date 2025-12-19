"""
Local File System Adapter

Implements FileSystemPort using local filesystem operations.
"""

import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4


class LocalFileSystem:
    """
    Local filesystem implementation of FileSystemPort.

    Handles file operations on the local filesystem.
    """

    def __init__(self, base_temp_dir: str = "/tmp/analyticbot_media") -> None:
        """
        Initialize local filesystem adapter.

        Args:
            base_temp_dir: Base directory for temporary files
        """
        self.base_temp_dir = Path(base_temp_dir)
        self.base_temp_dir.mkdir(exist_ok=True, parents=True)

    async def create_temp_dir(self) -> str:
        """
        Create a temporary directory for processing files.

        Returns:
            Absolute path to the created temporary directory
        """
        # For now, just return the base temp dir
        # Could create subdirectories per session if needed
        return str(self.base_temp_dir)

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
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        cutoff_time = time.time() - (max_age_hours * 3600)
        deleted_count = 0

        try:
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    # Check file modification time
                    if file_path.stat().st_mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            deleted_count += 1
                        except PermissionError:
                            # Skip files we can't delete
                            continue
        except PermissionError:
            raise PermissionError(f"Lacking permissions to clean directory: {directory}")

        return deleted_count

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
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid4().hex[:8]
        return f"{prefix}_{timestamp}_{unique_id}.{extension}"

    async def file_exists(self, path: str) -> bool:
        """
        Check if a file exists.

        Args:
            path: Path to file

        Returns:
            True if file exists, False otherwise
        """
        return Path(path).exists()

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
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return file_path.stat().st_size
