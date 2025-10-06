"""
Version Manager Service
=======================

Handles version lifecycle management including creation,
retrieval, listing, deletion, and version number generation.
"""

import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from core.services.adaptive_learning.versioning.models import (
    DeploymentStage,
    ModelStatus,
    ModelVersion,
)

from ..storage.version_storage_service import VersionStorageService

logger = logging.getLogger(__name__)


class VersionManager:
    """
    Manages model version lifecycle and operations.

    Responsibilities:
    - Create new versions
    - Retrieve versions
    - List versions
    - Delete versions
    - Generate version numbers
    - Track versions per model
    """

    def __init__(
        self,
        storage_service: VersionStorageService,
        max_versions_per_model: int = 10,
        versioning_strategy: str = "semantic",
    ):
        self.storage_service = storage_service
        self.max_versions_per_model = max_versions_per_model
        self.versioning_strategy = versioning_strategy

        # Version tracking
        self.versions: dict[str, ModelVersion] = {}  # version_id -> ModelVersion
        self.model_versions: dict[str, list[str]] = {}  # model_id -> [version_ids]

        # Thread safety
        self.lock = threading.Lock()

        logger.info("📋 Version Manager initialized")

    async def create_version(
        self,
        model_id: str,
        model_data: Any,
        metadata: dict[str, Any],
        description: str = "",
        tags: list[str] | None = None,
        parent_version: str | None = None,
    ) -> str | None:
        """Create a new model version"""
        try:
            # Generate version ID and number
            version_id = f"{model_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            version_number = await self.generate_version_number(model_id)

            # Save model data
            model_path, size_bytes = await self.storage_service.save_model_data(
                model_id, version_id, model_data
            )

            # Create metadata path
            model_dir = Path(model_path).parent
            metadata_path = str(model_dir / "metadata.json")

            # Calculate checksum
            checksum = await self.storage_service.calculate_checksum(model_path)

            # Create version metadata
            version = ModelVersion(
                version_id=version_id,
                model_id=model_id,
                version_number=version_number,
                status=ModelStatus.READY,
                deployment_stage=DeploymentStage.DEVELOPMENT,
                model_path=model_path,
                metadata_path=metadata_path,
                checksum=checksum,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                created_by=metadata.get("created_by", "system"),
                description=description,
                tags=tags or [],
                metrics=metadata.get("metrics", {}),
                dependencies=metadata.get("dependencies", {}),
                configuration=metadata.get("configuration", {}),
                deployment_config=metadata.get("deployment_config", {}),
                parent_version=parent_version,
                size_bytes=size_bytes,
                is_active=False,
            )

            # Save metadata
            await self.storage_service.save_version_metadata(version)

            # Register version
            with self.lock:
                self.versions[version_id] = version

                if model_id not in self.model_versions:
                    self.model_versions[model_id] = []

                self.model_versions[model_id].append(version_id)

            logger.info(f"✅ Version created: {version_id} (v{version_number})")
            return version_id

        except Exception as e:
            logger.error(f"❌ Failed to create version: {e}")
            return None

    async def get_version(self, version_id: str) -> ModelVersion | None:
        """Get a specific version by ID"""
        with self.lock:
            return self.versions.get(version_id)

    async def get_versions(
        self,
        model_id: str | None = None,
        status: ModelStatus | None = None,
        deployment_stage: DeploymentStage | None = None,
        limit: int | None = None,
    ) -> list[ModelVersion]:
        """Get versions with optional filters"""
        with self.lock:
            if model_id:
                version_ids = self.model_versions.get(model_id, [])
                versions = [self.versions[vid] for vid in version_ids if vid in self.versions]
            else:
                versions = list(self.versions.values())

            # Apply filters
            if status:
                versions = [v for v in versions if v.status == status]

            if deployment_stage:
                versions = [v for v in versions if v.deployment_stage == deployment_stage]

            # Sort by created_at (newest first)
            versions.sort(key=lambda v: v.created_at, reverse=True)

            # Apply limit
            if limit:
                versions = versions[:limit]

            return versions

    async def load_model(self, version_id: str) -> Any | None:
        """Load model data for a specific version"""
        version = await self.get_version(version_id)

        if not version:
            logger.warning(f"⚠️ Version not found: {version_id}")
            return None

        if version.status != ModelStatus.READY and version.status != ModelStatus.DEPLOYED:
            logger.warning(f"⚠️ Version not ready: {version_id} (status: {version.status})")
            return None

        model_data = await self.storage_service.load_model_data(version.model_path)

        if model_data:
            logger.info(f"✅ Model loaded: {version_id}")

        return model_data

    async def delete_version(self, version_id: str, force: bool = False) -> bool:
        """Delete a version"""
        try:
            version = await self.get_version(version_id)

            if not version:
                logger.warning(f"⚠️ Version not found: {version_id}")
                return False

            # Check if version can be deleted
            if not force:
                if version.is_active:
                    logger.error(f"❌ Cannot delete active version: {version_id}")
                    return False

                if version.status == ModelStatus.DEPLOYED:
                    logger.error(f"❌ Cannot delete deployed version: {version_id}")
                    return False

            # Backup before deletion
            await self.storage_service.backup_version(version)

            # Delete files
            deleted = await self.storage_service.delete_version_files(version)

            if deleted:
                # Remove from tracking
                with self.lock:
                    if version_id in self.versions:
                        del self.versions[version_id]

                    model_id = version.model_id
                    if model_id in self.model_versions:
                        if version_id in self.model_versions[model_id]:
                            self.model_versions[model_id].remove(version_id)

                logger.info(f"✅ Version deleted: {version_id}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"❌ Failed to delete version: {e}")
            return False

    async def update_version_status(self, version_id: str, status: ModelStatus) -> bool:
        """Update version status"""
        try:
            version = await self.get_version(version_id)

            if not version:
                return False

            with self.lock:
                version.status = status
                version.updated_at = datetime.utcnow()

            # Save updated metadata
            await self.storage_service.save_version_metadata(version)

            logger.info(f"✅ Version status updated: {version_id} -> {status.value}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update version status: {e}")
            return False

    async def generate_version_number(self, model_id: str) -> str:
        """Generate version number based on strategy"""
        with self.lock:
            version_ids = self.model_versions.get(model_id, [])
            version_count = len(version_ids)

        if self.versioning_strategy == "semantic":
            # Semantic versioning: major.minor.patch
            major = version_count // 10
            minor = version_count % 10
            return f"{major}.{minor}.0"

        elif self.versioning_strategy == "timestamp":
            # Timestamp-based
            return datetime.utcnow().strftime("%Y%m%d.%H%M%S")

        else:  # incremental
            # Simple incremental
            return f"{version_count + 1}"

    async def cleanup_old_versions(self, model_id: str, retention_days: int = 90) -> int:
        """
        Clean up old versions beyond max versions or retention period.

        Returns:
            Number of versions deleted
        """
        try:
            versions = await self.get_versions(model_id=model_id)

            if not versions:
                return 0

            # Sort by created_at (oldest first for cleanup)
            versions.sort(key=lambda v: v.created_at)

            deleted_count = 0
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

            # Keep deployed and active versions
            deletable_versions = [
                v
                for v in versions
                if not v.is_active
                and v.status != ModelStatus.DEPLOYED
                and v.created_at < cutoff_date
            ]

            # If we have more than max_versions, delete oldest
            if len(versions) > self.max_versions_per_model:
                excess_count = len(versions) - self.max_versions_per_model
                versions_to_delete = deletable_versions[:excess_count]
            else:
                versions_to_delete = deletable_versions

            # Delete versions
            for version in versions_to_delete:
                if await self.delete_version(version.version_id, force=False):
                    deleted_count += 1

            if deleted_count > 0:
                logger.info(f"🧹 Cleaned up {deleted_count} old versions for model {model_id}")

            return deleted_count

        except Exception as e:
            logger.error(f"❌ Failed to cleanup old versions: {e}")
            return 0

    async def load_existing_versions(self) -> int:
        """Load existing versions from storage"""
        try:
            versions_dict = await self.storage_service.load_all_versions_from_disk()

            with self.lock:
                self.versions = versions_dict

                # Rebuild model_versions mapping
                self.model_versions.clear()
                for version_id, version in versions_dict.items():
                    model_id = version.model_id
                    if model_id not in self.model_versions:
                        self.model_versions[model_id] = []
                    self.model_versions[model_id].append(version_id)

            logger.info(f"✅ Loaded {len(versions_dict)} existing versions")
            return len(versions_dict)

        except Exception as e:
            logger.error(f"❌ Failed to load existing versions: {e}")
            return 0

    def get_statistics(self) -> dict[str, Any]:
        """Get version management statistics"""
        with self.lock:
            total_versions = len(self.versions)
            total_models = len(self.model_versions)

            # Status distribution
            status_distribution = {}
            for version in self.versions.values():
                status = version.status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1

            # Versions per model
            versions_per_model = {
                model_id: len(version_ids) for model_id, version_ids in self.model_versions.items()
            }

            return {
                "total_versions": total_versions,
                "total_models": total_models,
                "status_distribution": status_distribution,
                "versions_per_model": versions_per_model,
                "max_versions_per_model": self.max_versions_per_model,
                "versioning_strategy": self.versioning_strategy,
            }

    async def health_check(self) -> dict[str, Any]:
        """Check version manager health"""
        try:
            stats = self.get_statistics()

            return {"service": "version_manager", "status": "healthy", **stats}

        except Exception as e:
            return {"service": "version_manager", "status": "error", "error": str(e)}
