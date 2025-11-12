"""
Version Storage Service
======================

Handles file I/O, persistence, checksum calculation,
and physical storage operations for model versions.
"""

import hashlib
import json
import logging
import pickle
import shutil
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from core.services.adaptive_learning.versioning.models import (
    DeploymentStage,
    ModelStatus,
    ModelVersion,
)

logger = logging.getLogger(__name__)


class VersionStorageService:
    """
    Manages physical storage operations for model versions.

    Responsibilities:
    - Save/load model files
    - Save/load metadata
    - Calculate checksums
    - Calculate storage usage
    - Backup operations
    - File system operations
    """

    def __init__(
        self,
        storage_path: str = "model_versions/",
        backup_path: str = "model_backups/",
        backup_enabled: bool = True,
        compression_enabled: bool = True,
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.backup_enabled = backup_enabled
        self.compression_enabled = compression_enabled

        if self.backup_enabled:
            self.backup_path = Path(backup_path)
            self.backup_path.mkdir(parents=True, exist_ok=True)

        logger.info("💾 Version Storage Service initialized")

    async def save_model_data(
        self, model_id: str, version_id: str, model_data: Any
    ) -> tuple[str, int]:
        """
        Save model data to disk.

        Returns:
            Tuple of (model_path, size_bytes)
        """
        try:
            # Create model directory
            model_dir = self.storage_path / model_id / version_id
            model_dir.mkdir(parents=True, exist_ok=True)

            model_path = model_dir / "model.pkl"

            # Save model data
            with open(model_path, "wb") as f:
                pickle.dump(model_data, f)

            # Get file size
            size_bytes = model_path.stat().st_size

            logger.info(f"✅ Model saved: {model_path} ({size_bytes} bytes)")
            return str(model_path), size_bytes

        except Exception as e:
            logger.error(f"❌ Failed to save model data: {e}")
            raise

    async def load_model_data(self, model_path: str) -> Any | None:
        """Load model data from disk"""
        try:
            path = Path(model_path)

            if not path.exists():
                logger.warning(f"⚠️ Model file not found: {model_path}")
                return None

            with open(path, "rb") as f:
                model_data = pickle.load(f)

            logger.info(f"✅ Model loaded: {model_path}")
            return model_data

        except Exception as e:
            logger.error(f"❌ Failed to load model data: {e}")
            return None

    async def save_version_metadata(self, version: ModelVersion) -> None:
        """Save version metadata to disk"""
        try:
            metadata_path = Path(version.metadata_path)
            metadata_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dictionary
            metadata_dict = asdict(version)

            # Convert datetime and enum objects to strings
            metadata_dict["status"] = version.status.value
            metadata_dict["deployment_stage"] = version.deployment_stage.value
            metadata_dict["created_at"] = version.created_at.isoformat()
            metadata_dict["updated_at"] = version.updated_at.isoformat()

            # Save as JSON
            with open(metadata_path, "w") as f:
                json.dump(metadata_dict, f, indent=2)

            logger.debug(f"✅ Metadata saved: {metadata_path}")

        except Exception as e:
            logger.error(f"❌ Failed to save metadata: {e}")
            raise

    async def load_version_metadata(self, metadata_path: str) -> ModelVersion | None:
        """Load version metadata from disk"""
        try:
            path = Path(metadata_path)

            if not path.exists():
                logger.warning(f"⚠️ Metadata file not found: {metadata_path}")
                return None

            with open(path) as f:
                metadata_dict = json.load(f)

            # Convert strings back to datetime and enum objects
            metadata_dict["status"] = ModelStatus(metadata_dict["status"])
            metadata_dict["deployment_stage"] = DeploymentStage(metadata_dict["deployment_stage"])
            metadata_dict["created_at"] = datetime.fromisoformat(metadata_dict["created_at"])
            metadata_dict["updated_at"] = datetime.fromisoformat(metadata_dict["updated_at"])

            version = ModelVersion(**metadata_dict)
            logger.debug(f"✅ Metadata loaded: {metadata_path}")
            return version

        except Exception as e:
            logger.error(f"❌ Failed to load metadata: {e}")
            return None

    async def calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of a file"""
        try:
            path = Path(file_path)

            if not path.exists():
                return ""

            sha256_hash = hashlib.sha256()

            with open(path, "rb") as f:
                # Read in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)

            checksum = sha256_hash.hexdigest()
            logger.debug(f"✅ Checksum calculated: {checksum[:16]}...")
            return checksum

        except Exception as e:
            logger.error(f"❌ Failed to calculate checksum: {e}")
            return ""

    async def calculate_storage_usage(self) -> int:
        """Calculate total storage usage in bytes"""
        try:
            total_size = 0

            for path in self.storage_path.rglob("*"):
                if path.is_file():
                    total_size += path.stat().st_size

            logger.debug(f"📊 Total storage usage: {total_size} bytes")
            return total_size

        except Exception as e:
            logger.error(f"❌ Failed to calculate storage usage: {e}")
            return 0

    async def backup_version(self, version: ModelVersion) -> bool:
        """Create backup of a model version"""
        if not self.backup_enabled:
            return True

        try:
            model_path = Path(version.model_path)

            if not model_path.exists():
                logger.warning(f"⚠️ Model file not found for backup: {version.model_path}")
                return False

            # Create backup directory
            backup_dir = self.backup_path / version.model_id / version.version_id
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Copy model file
            backup_model_path = backup_dir / "model.pkl"
            shutil.copy2(model_path, backup_model_path)

            # Copy metadata file
            metadata_path = Path(version.metadata_path)
            if metadata_path.exists():
                backup_metadata_path = backup_dir / "metadata.json"
                shutil.copy2(metadata_path, backup_metadata_path)

            logger.info(f"✅ Version backed up: {version.version_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to backup version: {e}")
            return False

    async def delete_version_files(self, version: ModelVersion) -> bool:
        """Delete all files associated with a version"""
        try:
            model_path = Path(version.model_path)
            version_dir = model_path.parent

            if version_dir.exists():
                shutil.rmtree(version_dir)
                logger.info(f"✅ Version files deleted: {version.version_id}")
                return True
            else:
                logger.warning(f"⚠️ Version directory not found: {version_dir}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to delete version files: {e}")
            return False

    async def load_all_versions_from_disk(self) -> dict[str, ModelVersion]:
        """
        Load all existing version metadata from disk.

        Returns:
            Dictionary mapping version_id to ModelVersion
        """
        versions = {}

        try:
            if not self.storage_path.exists():
                return versions

            # Iterate through model directories
            for model_dir in self.storage_path.iterdir():
                if not model_dir.is_dir():
                    continue

                # Iterate through version directories
                for version_dir in model_dir.iterdir():
                    if not version_dir.is_dir():
                        continue

                    metadata_path = version_dir / "metadata.json"

                    if metadata_path.exists():
                        version = await self.load_version_metadata(str(metadata_path))
                        if version:
                            versions[version.version_id] = version

            logger.info(f"✅ Loaded {len(versions)} versions from disk")
            return versions

        except Exception as e:
            logger.error(f"❌ Failed to load versions from disk: {e}")
            return versions

    def get_storage_path(self) -> Path:
        """Get storage path"""
        return self.storage_path

    def get_backup_path(self) -> Path | None:
        """Get backup path"""
        return self.backup_path if self.backup_enabled else None

    async def health_check(self) -> dict[str, Any]:
        """Check storage service health"""
        try:
            storage_exists = self.storage_path.exists()
            storage_writable = self.storage_path.is_dir()

            backup_exists = None
            backup_writable = None
            if self.backup_enabled:
                backup_exists = self.backup_path.exists()
                backup_writable = self.backup_path.is_dir()

            storage_size = await self.calculate_storage_usage()

            return {
                "service": "version_storage",
                "status": ("healthy" if storage_exists and storage_writable else "unhealthy"),
                "storage_path": str(self.storage_path),
                "storage_exists": storage_exists,
                "storage_writable": storage_writable,
                "backup_enabled": self.backup_enabled,
                "backup_path": str(self.backup_path) if self.backup_enabled else None,
                "backup_exists": backup_exists,
                "backup_writable": backup_writable,
                "storage_size_bytes": storage_size,
                "storage_size_mb": round(storage_size / (1024 * 1024), 2),
            }

        except Exception as e:
            return {"service": "version_storage", "status": "error", "error": str(e)}
