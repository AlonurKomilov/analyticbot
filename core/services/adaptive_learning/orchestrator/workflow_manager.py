"""
Workflow Manager
===============

Manages adaptive learning workflows - creation, execution, and lifecycle.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from ..protocols.learning_protocols import UpdateStatus
from .workflow_models import (
    AdaptiveLearningWorkflow,
    OrchestrationStrategy,
    WorkflowStage,
)

logger = logging.getLogger(__name__)


class WorkflowManager:
    """
    Manages the lifecycle of adaptive learning workflows.

    Handles workflow creation, tracking, and cleanup while coordinating
    with stage executors for actual workflow execution.
    """

    def __init__(self, max_concurrent_workflows: int = 5, workflow_timeout_hours: int = 12):
        self.max_concurrent_workflows = max_concurrent_workflows
        self.workflow_timeout_hours = workflow_timeout_hours

        # Workflow tracking
        self.active_workflows: dict[str, AdaptiveLearningWorkflow] = {}
        self.workflow_history: dict[str, list[AdaptiveLearningWorkflow]] = {}

        logger.info("📋 Workflow Manager initialized")

    async def create_workflow(
        self,
        model_id: str,
        strategy: OrchestrationStrategy,
        triggered_by: str,
        custom_config: dict[str, Any] | None = None,
    ) -> str | None:
        """Create a new adaptive learning workflow"""
        try:
            # Check concurrent workflow limit
            if len(self.active_workflows) >= self.max_concurrent_workflows:
                logger.warning(
                    f"⚠️ Maximum concurrent workflows reached: {self.max_concurrent_workflows}"
                )
                return None

            # Check for existing active workflow for this model
            existing_workflow = self._find_active_workflow_for_model(model_id)
            if existing_workflow:
                logger.warning(
                    f"⚠️ Active workflow already exists for model {model_id}: {existing_workflow.workflow_id}"
                )
                return existing_workflow.workflow_id

            # Create workflow
            workflow_id = str(uuid.uuid4())
            workflow = AdaptiveLearningWorkflow(
                workflow_id=workflow_id,
                model_id=model_id,
                strategy=strategy,
                current_stage=WorkflowStage.MONITORING,
                status=UpdateStatus.PENDING,
                triggered_by=triggered_by,
                created_at=datetime.utcnow(),
                metadata=custom_config or {},
            )

            # Add to tracking
            self.active_workflows[workflow_id] = workflow

            # Initialize history if needed
            if model_id not in self.workflow_history:
                self.workflow_history[model_id] = []

            logger.info(
                f"📋 Created workflow {workflow_id} for model {model_id} (strategy: {strategy.value})"
            )
            return workflow_id

        except Exception as e:
            logger.error(f"❌ Failed to create workflow: {e}")
            return None

    async def get_workflow(self, workflow_id: str) -> AdaptiveLearningWorkflow | None:
        """Get a workflow by ID"""
        return self.active_workflows.get(workflow_id)

    async def update_workflow_stage(
        self,
        workflow_id: str,
        new_stage: WorkflowStage,
        stage_metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Update workflow stage and metadata"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                logger.error(f"❌ Workflow {workflow_id} not found")
                return False

            # Update stage
            workflow.current_stage = new_stage

            # Update metadata
            if stage_metadata:
                workflow.metadata.update(stage_metadata)

            # Mark as started if first stage execution
            if workflow.started_at is None and new_stage != WorkflowStage.MONITORING:
                workflow.started_at = datetime.utcnow()

            logger.debug(f"📋 Updated workflow {workflow_id} to stage {new_stage.value}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update workflow stage: {e}")
            return False

    async def update_workflow_status(
        self,
        workflow_id: str,
        status: UpdateStatus,
        results: dict[str, Any] | None = None,
    ) -> bool:
        """Update workflow status and results"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                logger.error(f"❌ Workflow {workflow_id} not found")
                return False

            workflow.status = status

            # Update results based on stage
            if results:
                if workflow.current_stage in [
                    WorkflowStage.LEARNING_TASK_CREATION,
                    WorkflowStage.MODEL_TRAINING,
                ]:
                    workflow.learning_results = results
                elif workflow.current_stage == WorkflowStage.MODEL_DEPLOYMENT:
                    workflow.deployment_results = results
                elif "performance_metrics" in results:
                    workflow.performance_metrics = results["performance_metrics"]

            logger.debug(f"📋 Updated workflow {workflow_id} status to {status.value}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update workflow status: {e}")
            return False

    async def complete_workflow(self, workflow_id: str, success: bool = True) -> bool:
        """Complete a workflow and move to history"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                logger.error(f"❌ Workflow {workflow_id} not found")
                return False

            # Update final status
            workflow.completed_at = datetime.utcnow()
            workflow.status = UpdateStatus.COMPLETED if success else UpdateStatus.FAILED
            workflow.current_stage = WorkflowStage.COMPLETED if success else WorkflowStage.FAILED

            # Move to history
            self.workflow_history[workflow.model_id].append(workflow)

            # Remove from active workflows
            del self.active_workflows[workflow_id]

            logger.info(f"✅ Completed workflow {workflow_id} with status: {workflow.status.value}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to complete workflow: {e}")
            return False

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                logger.warning(f"⚠️ Workflow {workflow_id} not found for cancellation")
                return False

            # Update status
            workflow.status = UpdateStatus.FAILED
            workflow.current_stage = WorkflowStage.FAILED
            workflow.completed_at = datetime.utcnow()

            # Move to history
            self.workflow_history[workflow.model_id].append(workflow)

            # Remove from active workflows
            del self.active_workflows[workflow_id]

            logger.info(f"🚫 Cancelled workflow {workflow_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to cancel workflow: {e}")
            return False

    async def cleanup_workflow(self, workflow_id: str) -> None:
        """Cleanup workflow resources"""
        try:
            # Remove from active workflows if still there
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                workflow.status = UpdateStatus.FAILED
                workflow.completed_at = datetime.utcnow()

                # Move to history
                if workflow.model_id in self.workflow_history:
                    self.workflow_history[workflow.model_id].append(workflow)

                del self.active_workflows[workflow_id]

            logger.debug(f"🧹 Cleaned up workflow {workflow_id}")

        except Exception as e:
            logger.error(f"❌ Failed to cleanup workflow: {e}")

    async def get_active_workflows_for_model(self, model_id: str) -> list[AdaptiveLearningWorkflow]:
        """Get all active workflows for a model"""
        return [
            workflow for workflow in self.active_workflows.values() if workflow.model_id == model_id
        ]

    async def get_workflow_history(
        self, model_id: str, limit: int = 10
    ) -> list[AdaptiveLearningWorkflow]:
        """Get workflow history for a model"""
        if model_id not in self.workflow_history:
            return []

        # Return most recent workflows first
        history = sorted(self.workflow_history[model_id], key=lambda w: w.created_at, reverse=True)

        return history[:limit]

    async def cleanup_old_workflows(self, max_history_per_model: int = 50) -> None:
        """Cleanup old workflow history"""
        try:
            for model_id, history in self.workflow_history.items():
                if len(history) > max_history_per_model:
                    # Keep only the most recent workflows
                    sorted_history = sorted(history, key=lambda w: w.created_at, reverse=True)
                    self.workflow_history[model_id] = sorted_history[:max_history_per_model]

            logger.debug("🧹 Cleaned up old workflow history")

        except Exception as e:
            logger.error(f"❌ Failed to cleanup old workflows: {e}")

    def _find_active_workflow_for_model(self, model_id: str) -> AdaptiveLearningWorkflow | None:
        """Find active workflow for a model"""
        for workflow in self.active_workflows.values():
            if workflow.model_id == model_id:
                return workflow
        return None

    async def get_status(self) -> dict[str, Any]:
        """Get workflow manager status"""
        try:
            return {
                "service": "workflow_manager",
                "active_workflows": len(self.active_workflows),
                "max_concurrent": self.max_concurrent_workflows,
                "workflow_timeout_hours": self.workflow_timeout_hours,
                "models_with_history": len(self.workflow_history),
                "total_historical_workflows": sum(
                    len(history) for history in self.workflow_history.values()
                ),
            }

        except Exception as e:
            logger.error(f"❌ Failed to get workflow manager status: {e}")
            return {"error": str(e)}
