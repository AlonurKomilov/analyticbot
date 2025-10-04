"""
Model Versioning for Adaptive Learning
======================================

Provides infrastructure services for model version control,
deployment management, and model lifecycle tracking.
"""

import asyncio
import hashlib
import json
import logging
import pickle
import shutil
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model status enumeration"""

    TRAINING = "training"
    READY = "ready"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"


class DeploymentStage(Enum):
    """Deployment stage enumeration"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    CANARY = "canary"
    ROLLBACK = "rollback"


@dataclass
class ModelVersion:
    """Model version metadata"""

    version_id: str
    model_id: str
    version_number: str
    status: ModelStatus
    deployment_stage: DeploymentStage
    model_path: str
    metadata_path: str
    checksum: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    description: str
    tags: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    dependencies: dict[str, str] = field(default_factory=dict)
    configuration: dict[str, Any] = field(default_factory=dict)
    deployment_config: dict[str, Any] = field(default_factory=dict)
    parent_version: str | None = None
    size_bytes: int = 0
    is_active: bool = False


@dataclass
class ModelVersioningConfig:
    """Configuration for model versioning"""

    storage_path: str = "model_versions/"
    max_versions_per_model: int = 10
    auto_cleanup_enabled: bool = True
    backup_enabled: bool = True
    backup_path: str = "model_backups/"
    compression_enabled: bool = True
    retention_days: int = 90
    versioning_strategy: str = "semantic"  # semantic, timestamp, incremental
    enable_rollback: bool = True
    enable_canary_deployments: bool = True


class ModelVersioningService:
    """
    Infrastructure service for model versioning capabilities.

    Provides version control, deployment management,
    and model lifecycle tracking.
    """

    def __init__(self, config: ModelVersioningConfig | None = None):
        self.config = config or ModelVersioningConfig()
        self.storage_path = Path(self.config.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Backup path
        if self.config.backup_enabled:
            self.backup_path = Path(self.config.backup_path)
            self.backup_path.mkdir(parents=True, exist_ok=True)

        # Version tracking
        self.versions: dict[str, ModelVersion] = {}  # version_id -> ModelVersion
        self.model_versions: dict[str, list[str]] = {}  # model_id -> [version_ids]
        self.active_deployments: dict[
            str, dict[DeploymentStage, str]
        ] = {}  # model_id -> stage -> version_id

        # Locks for thread safety
        self.version_lock = threading.Lock()
        self.deployment_lock = threading.Lock()

        # Service state
        self.is_initialized = False
        self.cleanup_tasks: list[asyncio.Task] = []

        logger.info("🗂️ Model Versioning Service initialized")

    async def initialize_versioning(self, config: dict[str, Any]) -> bool:
        """Initialize model versioning infrastructure"""
        try:
            # Update configuration
            if "storage_path" in config:
                self.config.storage_path = config["storage_path"]
                self.storage_path = Path(self.config.storage_path)
                self.storage_path.mkdir(parents=True, exist_ok=True)

            if "max_versions_per_model" in config:
                self.config.max_versions_per_model = config["max_versions_per_model"]

            if "retention_days" in config:
                self.config.retention_days = config["retention_days"]

            # Load existing versions
            await self._load_existing_versions()

            # Start background tasks
            if self.config.auto_cleanup_enabled:
                cleanup_task = asyncio.create_task(self._cleanup_loop())
                self.cleanup_tasks.append(cleanup_task)

            self.is_initialized = True
            logger.info("✅ Model versioning initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize model versioning: {e}")
            return False

    async def get_versioning_status(self) -> dict[str, Any]:
        """Get status of model versioning"""
        try:
            total_versions = len(self.versions)
            total_models = len(self.model_versions)
            total_deployments = sum(len(stages) for stages in self.active_deployments.values())

            # Storage usage
            storage_size = await self._calculate_storage_usage()

            # Version status distribution
            status_distribution = {}
            for version in self.versions.values():
                status = version.status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1

            # Deployment stage distribution
            stage_distribution = {}
            for stages in self.active_deployments.values():
                for stage in stages.keys():
                    stage_name = stage.value
                    stage_distribution[stage_name] = stage_distribution.get(stage_name, 0) + 1

            return {
                "service": "model_versioning",
                "status": "healthy" if self.is_initialized else "initializing",
                "is_initialized": self.is_initialized,
                "storage_path": str(self.storage_path),
                "total_versions": total_versions,
                "total_models": total_models,
                "total_deployments": total_deployments,
                "storage_size_mb": round(storage_size / (1024 * 1024), 2),
                "status_distribution": status_distribution,
                "stage_distribution": stage_distribution,
                "config": asdict(self.config),
            }

        except Exception as e:
            logger.error(f"❌ Failed to get versioning status: {e}")
            return {"service": "model_versioning", "status": "error", "error": str(e)}

    async def create_model_version(
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
            version_number = await self._generate_version_number(model_id)

            # Create model and metadata paths
            model_dir = self.storage_path / model_id / version_id
            model_dir.mkdir(parents=True, exist_ok=True)

            model_path = model_dir / "model.pkl"
            metadata_path = model_dir / "metadata.json"

            # Save model data
            with open(model_path, "wb") as f:
                pickle.dump(model_data, f)

            # Calculate checksum
            checksum = await self._calculate_checksum(model_path)

            # Get file size
            size_bytes = model_path.stat().st_size

            # Create version metadata
            version = ModelVersion(
                version_id=version_id,
                model_id=model_id,
                version_number=version_number,
                status=ModelStatus.READY,
                deployment_stage=DeploymentStage.DEVELOPMENT,
                model_path=str(model_path),
                metadata_path=str(metadata_path),
                checksum=checksum,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                created_by=metadata.get("created_by", "system"),
                description=description,
                tags=tags or [],
                metrics=metadata.get("metrics", {}),
                dependencies=metadata.get("dependencies", {}),
                configuration=metadata.get("configuration", {}),
                parent_version=parent_version,
                size_bytes=size_bytes,
            )

            # Save metadata
            with open(metadata_path, "w") as f:
                json.dump(asdict(version), f, indent=2, default=str)

            # Register version
            with self.version_lock:
                self.versions[version_id] = version
                if model_id not in self.model_versions:
                    self.model_versions[model_id] = []
                self.model_versions[model_id].append(version_id)

            # Cleanup old versions if needed
            await self._cleanup_old_versions(model_id)

            logger.info(f"📦 Created model version {version_id} for {model_id}")
            return version_id

        except Exception as e:
            logger.error(f"❌ Failed to create model version: {e}")
            return None

    async def get_model_version(self, version_id: str) -> ModelVersion | None:
        """Get a specific model version"""
        try:
            return self.versions.get(version_id)

        except Exception as e:
            logger.error(f"❌ Failed to get model version: {e}")
            return None

    async def get_model_versions(
        self,
        model_id: str,
        status: ModelStatus | None = None,
        deployment_stage: DeploymentStage | None = None,
        limit: int | None = None,
    ) -> list[ModelVersion]:
        """Get versions for a specific model"""
        try:
            if model_id not in self.model_versions:
                return []

            version_ids = self.model_versions[model_id]
            versions = [self.versions[vid] for vid in version_ids if vid in self.versions]

            # Apply filters
            if status:
                versions = [v for v in versions if v.status == status]

            if deployment_stage:
                versions = [v for v in versions if v.deployment_stage == deployment_stage]

            # Sort by creation time (newest first)
            versions.sort(key=lambda v: v.created_at, reverse=True)

            # Apply limit
            if limit:
                versions = versions[:limit]

            return versions

        except Exception as e:
            logger.error(f"❌ Failed to get model versions: {e}")
            return []

    async def load_model_version(self, version_id: str) -> Any | None:
        """Load model data from a specific version"""
        try:
            version = await self.get_model_version(version_id)
            if not version:
                logger.warning(f"⚠️ Version {version_id} not found")
                return None

            # Verify checksum
            current_checksum = await self._calculate_checksum(Path(version.model_path))
            if current_checksum != version.checksum:
                logger.error(f"❌ Checksum mismatch for version {version_id}")
                return None

            # Load model data
            with open(version.model_path, "rb") as f:
                model_data = pickle.load(f)

            logger.debug(f"📂 Loaded model version {version_id}")
            return model_data

        except Exception as e:
            logger.error(f"❌ Failed to load model version: {e}")
            return None

    async def deploy_model_version(
        self,
        version_id: str,
        deployment_stage: DeploymentStage,
        deployment_config: dict[str, Any] | None = None,
    ) -> bool:
        """Deploy a model version to a specific stage"""
        try:
            version = await self.get_model_version(version_id)
            if not version:
                logger.error(f"❌ Version {version_id} not found")
                return False

            if version.status != ModelStatus.READY:
                logger.error(f"❌ Version {version_id} is not ready for deployment")
                return False

            with self.deployment_lock:
                # Update version metadata
                version.deployment_stage = deployment_stage
                version.status = ModelStatus.DEPLOYED
                version.deployment_config = deployment_config or {}
                version.updated_at = datetime.utcnow()

                # Track active deployment
                if version.model_id not in self.active_deployments:
                    self.active_deployments[version.model_id] = {}

                # Handle previous deployment in same stage
                if deployment_stage in self.active_deployments[version.model_id]:
                    old_version_id = self.active_deployments[version.model_id][deployment_stage]
                    if old_version_id in self.versions:
                        old_version = self.versions[old_version_id]
                        if old_version.deployment_stage == deployment_stage:
                            old_version.status = ModelStatus.DEPRECATED

                self.active_deployments[version.model_id][deployment_stage] = version_id

                # Mark as active if deploying to production
                if deployment_stage == DeploymentStage.PRODUCTION:
                    version.is_active = True
                    # Deactivate other production versions
                    for other_version in self.versions.values():
                        if (
                            other_version.model_id == version.model_id
                            and other_version.version_id != version_id
                            and other_version.deployment_stage == DeploymentStage.PRODUCTION
                        ):
                            other_version.is_active = False

            # Save updated metadata
            await self._save_version_metadata(version)

            logger.info(f"🚀 Deployed version {version_id} to {deployment_stage.value}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to deploy model version: {e}")
            return False

    async def rollback_deployment(
        self,
        model_id: str,
        deployment_stage: DeploymentStage,
        target_version: str | None = None,
    ) -> bool:
        """Rollback deployment to a previous version"""
        try:
            if not self.config.enable_rollback:
                logger.error("❌ Rollback is disabled")
                return False

            if model_id not in self.active_deployments:
                logger.error(f"❌ No deployments found for model {model_id}")
                return False

            if deployment_stage not in self.active_deployments[model_id]:
                logger.error(f"❌ No deployment found for stage {deployment_stage.value}")
                return False

            current_version_id = self.active_deployments[model_id][deployment_stage]

            # Find target version
            if target_version:
                if target_version not in self.versions:
                    logger.error(f"❌ Target version {target_version} not found")
                    return False
                rollback_version_id = target_version
            else:
                # Find previous version
                versions = await self.get_model_versions(model_id)
                suitable_versions = [
                    v
                    for v in versions
                    if v.version_id != current_version_id
                    and v.status in [ModelStatus.READY, ModelStatus.DEPRECATED]
                ]

                if not suitable_versions:
                    logger.error("❌ No suitable version found for rollback")
                    return False

                rollback_version_id = suitable_versions[0].version_id

            # Perform rollback
            rollback_success = await self.deploy_model_version(
                rollback_version_id,
                deployment_stage,
                {
                    "rollback_from": current_version_id,
                    "rollback_timestamp": datetime.utcnow().isoformat(),
                },
            )

            if rollback_success:
                # Mark current version as rolled back
                if current_version_id in self.versions:
                    current_version = self.versions[current_version_id]
                    current_version.status = ModelStatus.DEPRECATED
                    current_version.deployment_stage = DeploymentStage.ROLLBACK
                    await self._save_version_metadata(current_version)

                logger.info(
                    f"⏪ Rolled back {model_id} from {current_version_id} to {rollback_version_id}"
                )

            return rollback_success

        except Exception as e:
            logger.error(f"❌ Failed to rollback deployment: {e}")
            return False

    async def delete_model_version(self, version_id: str, force: bool = False) -> bool:
        """Delete a model version"""
        try:
            version = await self.get_model_version(version_id)
            if not version:
                logger.warning(f"⚠️ Version {version_id} not found")
                return True

            # Check if version is deployed
            if version.status == ModelStatus.DEPLOYED and not force:
                logger.error(f"❌ Cannot delete deployed version {version_id} without force flag")
                return False

            # Create backup if enabled
            if self.config.backup_enabled:
                await self._backup_version(version)

            # Remove from tracking
            with self.version_lock:
                if version_id in self.versions:
                    del self.versions[version_id]

                if version.model_id in self.model_versions:
                    if version_id in self.model_versions[version.model_id]:
                        self.model_versions[version.model_id].remove(version_id)

                    # Clean up empty model entries
                    if not self.model_versions[version.model_id]:
                        del self.model_versions[version.model_id]

            # Remove from deployments
            with self.deployment_lock:
                if version.model_id in self.active_deployments:
                    for stage, deployed_version_id in list(
                        self.active_deployments[version.model_id].items()
                    ):
                        if deployed_version_id == version_id:
                            del self.active_deployments[version.model_id][stage]

                    # Clean up empty deployment entries
                    if not self.active_deployments[version.model_id]:
                        del self.active_deployments[version.model_id]

            # Remove files
            version_dir = Path(version.model_path).parent
            if version_dir.exists():
                shutil.rmtree(version_dir)

            logger.info(f"🗑️ Deleted model version {version_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete model version: {e}")
            return False

    async def get_active_deployment(
        self, model_id: str, deployment_stage: DeploymentStage
    ) -> str | None:
        """Get the currently deployed version for a stage"""
        try:
            if model_id not in self.active_deployments:
                return None

            return self.active_deployments[model_id].get(deployment_stage)

        except Exception as e:
            logger.error(f"❌ Failed to get active deployment: {e}")
            return None

    async def compare_versions(self, version_id1: str, version_id2: str) -> dict[str, Any]:
        """Compare two model versions"""
        try:
            version1 = await self.get_model_version(version_id1)
            version2 = await self.get_model_version(version_id2)

            if not version1 or not version2:
                return {"error": "One or both versions not found"}

            comparison = {
                "version1": {
                    "version_id": version1.version_id,
                    "version_number": version1.version_number,
                    "created_at": version1.created_at.isoformat(),
                    "status": version1.status.value,
                    "deployment_stage": version1.deployment_stage.value,
                    "size_bytes": version1.size_bytes,
                    "metrics": version1.metrics,
                    "tags": version1.tags,
                },
                "version2": {
                    "version_id": version2.version_id,
                    "version_number": version2.version_number,
                    "created_at": version2.created_at.isoformat(),
                    "status": version2.status.value,
                    "deployment_stage": version2.deployment_stage.value,
                    "size_bytes": version2.size_bytes,
                    "metrics": version2.metrics,
                    "tags": version2.tags,
                },
                "differences": {
                    "age_difference_hours": (
                        version2.created_at - version1.created_at
                    ).total_seconds()
                    / 3600,
                    "size_difference_bytes": version2.size_bytes - version1.size_bytes,
                    "metric_differences": {},
                },
            }

            # Compare metrics
            all_metrics = set(version1.metrics.keys()) | set(version2.metrics.keys())
            for metric in all_metrics:
                val1 = version1.metrics.get(metric, 0)
                val2 = version2.metrics.get(metric, 0)
                comparison["differences"]["metric_differences"][metric] = {
                    "version1": val1,
                    "version2": val2,
                    "difference": val2 - val1,
                    "percent_change": (((val2 - val1) / val1 * 100) if val1 != 0 else float("inf")),
                }

            return comparison

        except Exception as e:
            logger.error(f"❌ Failed to compare versions: {e}")
            return {"error": str(e)}

    async def _generate_version_number(self, model_id: str) -> str:
        """Generate version number based on strategy"""
        try:
            if self.config.versioning_strategy == "timestamp":
                return datetime.utcnow().strftime("%Y.%m.%d.%H%M%S")

            elif self.config.versioning_strategy == "incremental":
                existing_versions = await self.get_model_versions(model_id)
                if not existing_versions:
                    return "1.0.0"

                # Find highest version number
                max_version = max(
                    existing_versions,
                    key=lambda v: [int(x) for x in v.version_number.split(".")],
                    default=None,
                )

                if max_version:
                    parts = max_version.version_number.split(".")
                    parts[-1] = str(int(parts[-1]) + 1)
                    return ".".join(parts)
                else:
                    return "1.0.0"

            else:  # semantic versioning
                existing_versions = await self.get_model_versions(model_id)
                if not existing_versions:
                    return "1.0.0"

                # For now, just increment patch version
                max_version = max(
                    existing_versions,
                    key=lambda v: [int(x) for x in v.version_number.split(".")],
                    default=None,
                )

                if max_version:
                    major, minor, patch = map(int, max_version.version_number.split("."))
                    return f"{major}.{minor}.{patch + 1}"
                else:
                    return "1.0.0"

        except Exception as e:
            logger.error(f"❌ Failed to generate version number: {e}")
            return "1.0.0"

    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()

        except Exception as e:
            logger.error(f"❌ Failed to calculate checksum: {e}")
            return ""

    async def _calculate_storage_usage(self) -> int:
        """Calculate total storage usage in bytes"""
        try:
            total_size = 0
            for version in self.versions.values():
                total_size += version.size_bytes
            return total_size

        except Exception as e:
            logger.error(f"❌ Failed to calculate storage usage: {e}")
            return 0

    async def _load_existing_versions(self) -> None:
        """Load existing versions from storage"""
        try:
            if not self.storage_path.exists():
                return

            for model_dir in self.storage_path.iterdir():
                if model_dir.is_dir():
                    model_id = model_dir.name

                    for version_dir in model_dir.iterdir():
                        if version_dir.is_dir():
                            metadata_path = version_dir / "metadata.json"
                            if metadata_path.exists():
                                try:
                                    with open(metadata_path) as f:
                                        version_data = json.load(f)

                                    # Convert to ModelVersion object
                                    version = ModelVersion(
                                        version_id=version_data["version_id"],
                                        model_id=version_data["model_id"],
                                        version_number=version_data["version_number"],
                                        status=ModelStatus(version_data["status"]),
                                        deployment_stage=DeploymentStage(
                                            version_data["deployment_stage"]
                                        ),
                                        model_path=version_data["model_path"],
                                        metadata_path=version_data["metadata_path"],
                                        checksum=version_data["checksum"],
                                        created_at=datetime.fromisoformat(
                                            version_data["created_at"]
                                        ),
                                        updated_at=datetime.fromisoformat(
                                            version_data["updated_at"]
                                        ),
                                        created_by=version_data["created_by"],
                                        description=version_data["description"],
                                        tags=version_data.get("tags", []),
                                        metrics=version_data.get("metrics", {}),
                                        dependencies=version_data.get("dependencies", {}),
                                        configuration=version_data.get("configuration", {}),
                                        deployment_config=version_data.get("deployment_config", {}),
                                        parent_version=version_data.get("parent_version"),
                                        size_bytes=version_data.get("size_bytes", 0),
                                        is_active=version_data.get("is_active", False),
                                    )

                                    # Register version
                                    self.versions[version.version_id] = version

                                    if model_id not in self.model_versions:
                                        self.model_versions[model_id] = []
                                    self.model_versions[model_id].append(version.version_id)

                                    # Track active deployments
                                    if version.status == ModelStatus.DEPLOYED:
                                        if model_id not in self.active_deployments:
                                            self.active_deployments[model_id] = {}
                                        self.active_deployments[model_id][
                                            version.deployment_stage
                                        ] = version.version_id

                                except Exception as e:
                                    logger.warning(
                                        f"⚠️ Failed to load version from {metadata_path}: {e}"
                                    )

            logger.info(f"📂 Loaded {len(self.versions)} existing versions")

        except Exception as e:
            logger.warning(f"⚠️ Failed to load existing versions: {e}")

    async def _save_version_metadata(self, version: ModelVersion) -> None:
        """Save version metadata to file"""
        try:
            with open(version.metadata_path, "w") as f:
                json.dump(asdict(version), f, indent=2, default=str)

        except Exception as e:
            logger.error(f"❌ Failed to save version metadata: {e}")

    async def _cleanup_old_versions(self, model_id: str) -> None:
        """Clean up old versions if limit exceeded"""
        try:
            if model_id not in self.model_versions:
                return

            versions = await self.get_model_versions(model_id)
            if len(versions) <= self.config.max_versions_per_model:
                return

            # Keep the most recent versions and deployed versions
            versions_to_keep = set()

            # Keep recent versions
            recent_versions = sorted(versions, key=lambda v: v.created_at, reverse=True)
            for version in recent_versions[: self.config.max_versions_per_model]:
                versions_to_keep.add(version.version_id)

            # Keep deployed versions
            for version in versions:
                if version.status == ModelStatus.DEPLOYED:
                    versions_to_keep.add(version.version_id)

            # Delete old versions
            for version in versions:
                if version.version_id not in versions_to_keep:
                    await self.delete_model_version(version.version_id, force=False)

        except Exception as e:
            logger.error(f"❌ Failed to cleanup old versions: {e}")

    async def _backup_version(self, version: ModelVersion) -> None:
        """Create backup of a version before deletion"""
        try:
            if not self.config.backup_enabled:
                return

            backup_dir = self.backup_path / version.model_id / version.version_id
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Copy model file
            source_dir = Path(version.model_path).parent
            for file_path in source_dir.iterdir():
                shutil.copy2(file_path, backup_dir / file_path.name)

            logger.debug(f"💾 Created backup for version {version.version_id}")

        except Exception as e:
            logger.error(f"❌ Failed to create backup: {e}")

    async def _cleanup_loop(self) -> None:
        """Background task for periodic cleanup"""
        while True:
            try:
                await asyncio.sleep(24 * 3600)  # Run daily

                # Clean up old versions
                cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_days)

                for model_id in list(self.model_versions.keys()):
                    versions = await self.get_model_versions(model_id)
                    old_versions = [
                        v
                        for v in versions
                        if v.created_at < cutoff_date and v.status != ModelStatus.DEPLOYED
                    ]

                    for version in old_versions:
                        await self.delete_model_version(version.version_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in cleanup loop: {e}")

    async def shutdown(self) -> None:
        """Shutdown model versioning service"""
        try:
            # Cancel cleanup tasks
            for task in self.cleanup_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            self.cleanup_tasks.clear()
            self.is_initialized = False

            logger.info("🛑 Model versioning shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "service": "model_versioning",
            "status": "healthy" if self.is_initialized else "initializing",
            "is_initialized": self.is_initialized,
            "storage_path": str(self.storage_path),
            "total_versions": len(self.versions),
            "total_models": len(self.model_versions),
            "total_deployments": sum(len(stages) for stages in self.active_deployments.values()),
        }
