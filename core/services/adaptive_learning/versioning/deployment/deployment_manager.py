"""
Deployment Manager Service
===========================

Handles model deployment operations including deployment,
rollback, canary deployments, and active deployment tracking.
"""

import logging
import threading
from datetime import datetime
from typing import Any

from core.services.adaptive_learning.versioning.models import (
    DeploymentStage,
    ModelStatus,
)

from ..management.version_manager import VersionManager
from ..storage.version_storage_service import VersionStorageService

logger = logging.getLogger(__name__)


class DeploymentManager:
    """
    Manages model deployment operations.

    Responsibilities:
    - Deploy versions to stages
    - Rollback deployments
    - Track active deployments
    - Manage canary deployments
    - Deployment validation
    """

    def __init__(
        self,
        version_manager: VersionManager,
        storage_service: VersionStorageService,
        enable_canary: bool = True,
        enable_rollback: bool = True,
    ):
        self.version_manager = version_manager
        self.storage_service = storage_service
        self.enable_canary = enable_canary
        self.enable_rollback = enable_rollback

        # Track active deployments: model_id -> stage -> version_id
        self.active_deployments: dict[str, dict[DeploymentStage, str]] = {}

        # Deployment history for rollback
        self.deployment_history: dict[str, list[dict[str, Any]]] = {}  # model_id -> [deployments]

        # Thread safety
        self.lock = threading.Lock()

        logger.info("🚀 Deployment Manager initialized")

    async def deploy_version(
        self,
        version_id: str,
        deployment_stage: DeploymentStage,
        deployment_config: dict[str, Any] | None = None,
        auto_activate: bool = True,
    ) -> bool:
        """Deploy a version to a specific stage"""
        try:
            version = await self.version_manager.get_version(version_id)

            if not version:
                logger.error(f"❌ Version not found: {version_id}")
                return False

            # Validate version is ready
            if version.status not in [ModelStatus.READY, ModelStatus.DEPLOYED]:
                logger.error(f"❌ Version not ready for deployment: {version_id}")
                return False

            model_id = version.model_id

            # Get currently deployed version for this stage
            current_deployment = await self.get_active_deployment(model_id, deployment_stage)

            # Record deployment history
            deployment_record = {
                "version_id": version_id,
                "deployment_stage": deployment_stage,
                "deployed_at": datetime.utcnow(),
                "deployment_config": deployment_config or {},
                "previous_version": current_deployment,
            }

            with self.lock:
                if model_id not in self.deployment_history:
                    self.deployment_history[model_id] = []
                self.deployment_history[model_id].append(deployment_record)

            # Deactivate previous deployment if exists
            if current_deployment:
                previous_version = await self.version_manager.get_version(current_deployment)
                if previous_version:
                    with self.lock:
                        previous_version.is_active = False
                    await self.storage_service.save_version_metadata(previous_version)

            # Update version deployment info
            with self.lock:
                version.deployment_stage = deployment_stage
                version.status = ModelStatus.DEPLOYED
                version.is_active = auto_activate
                version.deployment_config = deployment_config or {}
                version.updated_at = datetime.utcnow()

            # Save updated metadata
            await self.storage_service.save_version_metadata(version)

            # Register active deployment
            with self.lock:
                if model_id not in self.active_deployments:
                    self.active_deployments[model_id] = {}
                self.active_deployments[model_id][deployment_stage] = version_id

            logger.info(f"✅ Version deployed: {version_id} to {deployment_stage.value}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to deploy version: {e}")
            return False

    async def rollback_deployment(
        self, model_id: str, deployment_stage: DeploymentStage, target_version: str | None = None
    ) -> bool:
        """Rollback to previous or specific version"""
        if not self.enable_rollback:
            logger.error("❌ Rollback is disabled")
            return False

        try:
            # Get deployment history
            history = self.deployment_history.get(model_id, [])

            if not history:
                logger.error(f"❌ No deployment history for model: {model_id}")
                return False

            # Find target version for rollback
            if target_version:
                # Rollback to specific version
                rollback_version_id = target_version
            else:
                # Rollback to previous version
                # Find last deployment before current
                stage_deployments = [
                    d for d in history if d["deployment_stage"] == deployment_stage
                ]

                if len(stage_deployments) < 2:
                    logger.error("❌ No previous deployment to rollback to")
                    return False

                rollback_version_id = stage_deployments[-2]["version_id"]

            # Verify rollback version exists
            rollback_version = await self.version_manager.get_version(rollback_version_id)

            if not rollback_version:
                logger.error(f"❌ Rollback version not found: {rollback_version_id}")
                return False

            # Perform deployment to rollback stage
            logger.info(f"🔄 Rolling back {model_id} to {rollback_version_id}")

            success = await self.deploy_version(
                rollback_version_id,
                DeploymentStage.ROLLBACK,
                deployment_config={"rollback": True, "original_stage": deployment_stage.value},
                auto_activate=True,
            )

            if success:
                logger.info(f"✅ Rollback completed: {model_id} -> {rollback_version_id}")

            return success

        except Exception as e:
            logger.error(f"❌ Failed to rollback deployment: {e}")
            return False

    async def get_active_deployment(
        self, model_id: str, deployment_stage: DeploymentStage
    ) -> str | None:
        """Get currently active deployment for a stage"""
        with self.lock:
            if model_id not in self.active_deployments:
                return None

            return self.active_deployments[model_id].get(deployment_stage)

    async def get_all_active_deployments(
        self, model_id: str | None = None
    ) -> dict[str, dict[str, str]]:
        """Get all active deployments, optionally filtered by model_id"""
        with self.lock:
            if model_id:
                deployments = {
                    model_id: {
                        stage.value: version_id
                        for stage, version_id in self.active_deployments.get(model_id, {}).items()
                    }
                }
            else:
                deployments = {
                    mid: {stage.value: version_id for stage, version_id in stages.items()}
                    for mid, stages in self.active_deployments.items()
                }

            return deployments

    async def deactivate_deployment(self, model_id: str, deployment_stage: DeploymentStage) -> bool:
        """Deactivate a deployment"""
        try:
            version_id = await self.get_active_deployment(model_id, deployment_stage)

            if not version_id:
                logger.warning("⚠️ No active deployment to deactivate")
                return False

            version = await self.version_manager.get_version(version_id)

            if not version:
                return False

            # Update version
            with self.lock:
                version.is_active = False
                version.updated_at = datetime.utcnow()

            await self.storage_service.save_version_metadata(version)

            # Remove from active deployments
            with self.lock:
                if model_id in self.active_deployments:
                    if deployment_stage in self.active_deployments[model_id]:
                        del self.active_deployments[model_id][deployment_stage]

            logger.info(f"✅ Deployment deactivated: {version_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to deactivate deployment: {e}")
            return False

    async def promote_version(
        self, version_id: str, from_stage: DeploymentStage, to_stage: DeploymentStage
    ) -> bool:
        """Promote a version from one stage to another"""
        try:
            # Verify version is deployed to from_stage
            version = await self.version_manager.get_version(version_id)

            if not version:
                logger.error(f"❌ Version not found: {version_id}")
                return False

            if version.deployment_stage != from_stage:
                logger.error(f"❌ Version not deployed to {from_stage.value}: {version_id}")
                return False

            # Deploy to new stage
            logger.info(f"⬆️ Promoting {version_id}: {from_stage.value} -> {to_stage.value}")

            return await self.deploy_version(
                version_id,
                to_stage,
                deployment_config={"promoted_from": from_stage.value},
                auto_activate=True,
            )

        except Exception as e:
            logger.error(f"❌ Failed to promote version: {e}")
            return False

    async def get_deployment_history(
        self, model_id: str, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Get deployment history for a model"""
        with self.lock:
            history = self.deployment_history.get(model_id, [])

            if limit:
                history = history[-limit:]

            return history

    def get_deployment_statistics(self) -> dict[str, Any]:
        """Get deployment statistics"""
        with self.lock:
            total_deployments = sum(len(stages) for stages in self.active_deployments.values())

            # Count deployments per stage
            stage_distribution = {}
            for stages in self.active_deployments.values():
                for stage in stages.keys():
                    stage_name = stage.value
                    stage_distribution[stage_name] = stage_distribution.get(stage_name, 0) + 1

            total_models_deployed = len(self.active_deployments)

            # Deployment history stats
            total_historical_deployments = sum(
                len(history) for history in self.deployment_history.values()
            )

            return {
                "total_active_deployments": total_deployments,
                "total_models_deployed": total_models_deployed,
                "stage_distribution": stage_distribution,
                "total_historical_deployments": total_historical_deployments,
                "canary_enabled": self.enable_canary,
                "rollback_enabled": self.enable_rollback,
            }

    async def health_check(self) -> dict[str, Any]:
        """Check deployment manager health"""
        try:
            stats = self.get_deployment_statistics()

            return {"service": "deployment_manager", "status": "healthy", **stats}

        except Exception as e:
            return {"service": "deployment_manager", "status": "error", "error": str(e)}
