"""
Versioning Orchestrator
=======================

Coordinates all versioning microservices and provides
unified interface for model version management.
"""

import asyncio
import logging
from typing import Any

from core.services.adaptive_learning.versioning.models import (
    DeploymentStage,
    ModelStatus,
    ModelVersion,
    ModelVersioningConfig,
)

from ..comparison.version_comparator import VersionComparator
from ..deployment.deployment_manager import DeploymentManager
from ..management.version_manager import VersionManager
from ..storage.version_storage_service import VersionStorageService

logger = logging.getLogger(__name__)


class VersioningOrchestrator:
    """
    Orchestrates all versioning microservices.

    Provides unified interface that maintains backward compatibility
    with original ModelVersioningService.
    """

    def __init__(self, config: ModelVersioningConfig | None = None):
        self.config = config or ModelVersioningConfig()

        # Initialize microservices
        self.storage_service = VersionStorageService(
            storage_path=self.config.storage_path,
            backup_path=self.config.backup_path,
            backup_enabled=self.config.backup_enabled,
            compression_enabled=self.config.compression_enabled,
        )

        self.version_manager = VersionManager(
            storage_service=self.storage_service,
            max_versions_per_model=self.config.max_versions_per_model,
            versioning_strategy=self.config.versioning_strategy,
        )

        self.version_comparator = VersionComparator(version_manager=self.version_manager)

        self.deployment_manager = DeploymentManager(
            version_manager=self.version_manager,
            storage_service=self.storage_service,
            enable_canary=self.config.enable_canary_deployments,
            enable_rollback=self.config.enable_rollback,
        )

        # Service state
        self.is_initialized = False
        self.cleanup_tasks: list[asyncio.Task] = []

        logger.info("🗂️ Versioning Orchestrator initialized")

    # ============================================================
    # Initialization & Status
    # ============================================================

    async def initialize_versioning(self, config: dict[str, Any]) -> bool:
        """Initialize versioning infrastructure"""
        try:
            # Update configuration
            if "storage_path" in config:
                self.config.storage_path = config["storage_path"]

            if "max_versions_per_model" in config:
                self.config.max_versions_per_model = config["max_versions_per_model"]

            if "retention_days" in config:
                self.config.retention_days = config["retention_days"]

            # Load existing versions
            await self.version_manager.load_existing_versions()

            # Start background tasks
            if self.config.auto_cleanup_enabled:
                cleanup_task = asyncio.create_task(self._cleanup_loop())
                self.cleanup_tasks.append(cleanup_task)

            self.is_initialized = True
            logger.info("✅ Versioning orchestrator initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize versioning: {e}")
            return False

    async def get_versioning_status(self) -> dict[str, Any]:
        """Get comprehensive versioning status"""
        try:
            # Get status from each microservice
            storage_status = await self.storage_service.health_check()
            manager_status = await self.version_manager.health_check()
            comparator_status = await self.version_comparator.health_check()
            deployment_status = await self.deployment_manager.health_check()

            # Aggregate statistics
            manager_stats = self.version_manager.get_statistics()
            deployment_stats = self.deployment_manager.get_deployment_statistics()

            return {
                "service": "model_versioning",
                "status": "healthy" if self.is_initialized else "initializing",
                "is_initialized": self.is_initialized,
                "storage_path": self.config.storage_path,
                "total_versions": manager_stats["total_versions"],
                "total_models": manager_stats["total_models"],
                "total_deployments": deployment_stats["total_active_deployments"],
                "storage_size_mb": storage_status.get("storage_size_mb", 0),
                "status_distribution": manager_stats.get("status_distribution", {}),
                "stage_distribution": deployment_stats.get("stage_distribution", {}),
                "config": {
                    "max_versions_per_model": self.config.max_versions_per_model,
                    "retention_days": self.config.retention_days,
                    "backup_enabled": self.config.backup_enabled,
                    "versioning_strategy": self.config.versioning_strategy,
                },
                "microservices": {
                    "storage": storage_status["status"],
                    "manager": manager_status["status"],
                    "comparator": comparator_status["status"],
                    "deployment": deployment_status["status"],
                },
            }

        except Exception as e:
            logger.error(f"❌ Failed to get versioning status: {e}")
            return {"service": "model_versioning", "status": "error", "error": str(e)}

    # ============================================================
    # Version Management (delegate to VersionManager)
    # ============================================================

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
        version_id = await self.version_manager.create_version(
            model_id=model_id,
            model_data=model_data,
            metadata=metadata,
            description=description,
            tags=tags,
            parent_version=parent_version,
        )

        # Auto-cleanup if enabled
        if version_id and self.config.auto_cleanup_enabled:
            await self.version_manager.cleanup_old_versions(
                model_id=model_id, retention_days=self.config.retention_days
            )

        return version_id

    async def get_model_version(self, version_id: str) -> ModelVersion | None:
        """Get a specific version"""
        return await self.version_manager.get_version(version_id)

    async def get_model_versions(
        self,
        model_id: str | None = None,
        status: ModelStatus | None = None,
        deployment_stage: DeploymentStage | None = None,
        limit: int | None = None,
    ) -> list[ModelVersion]:
        """Get versions with filters"""
        return await self.version_manager.get_versions(
            model_id=model_id,
            status=status,
            deployment_stage=deployment_stage,
            limit=limit,
        )

    async def load_model_version(self, version_id: str) -> Any | None:
        """Load model data"""
        return await self.version_manager.load_model(version_id)

    async def delete_model_version(self, version_id: str, force: bool = False) -> bool:
        """Delete a version"""
        return await self.version_manager.delete_version(version_id, force)

    # ============================================================
    # Deployment Operations (delegate to DeploymentManager)
    # ============================================================

    async def deploy_model_version(
        self,
        version_id: str,
        deployment_stage: DeploymentStage,
        deployment_config: dict[str, Any] | None = None,
        auto_activate: bool = True,
    ) -> bool:
        """Deploy a version"""
        return await self.deployment_manager.deploy_version(
            version_id=version_id,
            deployment_stage=deployment_stage,
            deployment_config=deployment_config,
            auto_activate=auto_activate,
        )

    async def rollback_deployment(
        self,
        model_id: str,
        deployment_stage: DeploymentStage,
        target_version: str | None = None,
    ) -> bool:
        """Rollback deployment"""
        return await self.deployment_manager.rollback_deployment(
            model_id=model_id,
            deployment_stage=deployment_stage,
            target_version=target_version,
        )

    async def get_active_deployment(
        self, model_id: str, deployment_stage: DeploymentStage
    ) -> str | None:
        """Get active deployment"""
        return await self.deployment_manager.get_active_deployment(
            model_id=model_id, deployment_stage=deployment_stage
        )

    # ============================================================
    # Comparison Operations (delegate to VersionComparator)
    # ============================================================

    async def compare_versions(self, version_id1: str, version_id2: str) -> dict[str, Any]:
        """Compare two versions"""
        return await self.version_comparator.compare_versions(
            version_id1=version_id1, version_id2=version_id2
        )

    # ============================================================
    # Background Tasks
    # ============================================================

    async def _cleanup_loop(self) -> None:
        """Background cleanup task"""
        try:
            while True:
                await asyncio.sleep(3600)  # Run every hour

                try:
                    # Get all models
                    all_versions = await self.version_manager.get_versions()
                    model_ids = {v.model_id for v in all_versions}

                    # Cleanup each model
                    for model_id in model_ids:
                        await self.version_manager.cleanup_old_versions(
                            model_id=model_id, retention_days=self.config.retention_days
                        )

                    logger.info("🧹 Cleanup task completed")

                except Exception as e:
                    logger.error(f"❌ Cleanup task error: {e}")

        except asyncio.CancelledError:
            logger.info("🛑 Cleanup task cancelled")

    async def shutdown(self) -> None:
        """Shutdown versioning service"""
        try:
            # Cancel background tasks
            for task in self.cleanup_tasks:
                task.cancel()

            # Wait for tasks to complete
            if self.cleanup_tasks:
                await asyncio.gather(*self.cleanup_tasks, return_exceptions=True)

            logger.info("✅ Versioning orchestrator shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    def get_service_health(self) -> dict[str, Any]:
        """Get service health (sync version for compatibility)"""
        return {
            "service": "model_versioning",
            "status": "healthy" if self.is_initialized else "initializing",
            "is_initialized": self.is_initialized,
        }


# Backward compatibility alias
ModelVersioningService = VersioningOrchestrator
