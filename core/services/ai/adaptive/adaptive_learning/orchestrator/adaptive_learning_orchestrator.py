"""
Adaptive Learning Orchestrator Service - Refactored
===================================================

Clean architecture orchestrator that coordinates adaptive learning microservices.
Uses composition with specialized components for workflow management, stage execution,
and scheduling to maintain single responsibility principle.
"""

import logging
from typing import Any

from ..deployment import ModelUpdateService
from ..drift import DriftDetectionService
from ..feedback import FeedbackCollectionService
from ..learning import LearningTaskService
from ..protocols.learning_protocols import LearningStrategy, UpdateStatus
from ..protocols.monitoring_protocols import MonitoringServiceProtocol
from .orchestration_scheduler import OrchestrationScheduler
from .stage_executor import StageExecutor
from .workflow_manager import WorkflowManager
from .workflow_models import OrchestrationConfig, OrchestrationMetrics, OrchestrationStrategy

logger = logging.getLogger(__name__)


class AdaptiveLearningOrchestrator:
    """
    Clean architecture orchestrator for adaptive learning microservices.

    Delegates responsibilities to specialized components:
    - WorkflowManager: Workflow lifecycle management
    - StageExecutor: Individual stage execution
    - OrchestrationScheduler: Background scheduling and monitoring

    This approach maintains single responsibility and makes the system
    more testable and maintainable.
    """

    def __init__(
        self,
        learning_task_service: LearningTaskService,
        model_update_service: ModelUpdateService,
        drift_detection_service: DriftDetectionService,
        feedback_collection_service: FeedbackCollectionService,
        monitoring_service: MonitoringServiceProtocol,
        config: OrchestrationConfig | None = None,
    ):
        self.config = config or OrchestrationConfig()

        # Initialize specialized components
        self.workflow_manager = WorkflowManager(
            max_concurrent_workflows=self.config.max_concurrent_workflows,
            workflow_timeout_hours=self.config.workflow_timeout_hours,
        )

        self.stage_executor = StageExecutor(
            drift_service=drift_detection_service,
            feedback_service=feedback_collection_service,
            learning_service=learning_task_service,
            deployment_service=model_update_service,
            min_confidence_threshold=self.config.min_confidence_threshold,
            performance_improvement_threshold=self.config.performance_improvement_threshold,
        )

        self.scheduler = OrchestrationScheduler(
            workflow_manager=self.workflow_manager,
            monitoring_service=monitoring_service,
            config=self.config,
        )

        # Service state
        self.is_running = False
        self.monitored_models: set[str] = set()

        # Metrics tracking
        self.orchestration_metrics = OrchestrationMetrics()

        logger.info("🎭 Adaptive Learning Orchestrator initialized with clean architecture")

    async def start_orchestration(self) -> bool:
        """Start the orchestration service"""
        try:
            if self.is_running:
                logger.warning("⚠️ Orchestration already running")
                return True

            # Validate dependencies
            if not await self._validate_dependencies():
                logger.error("❌ Service dependencies not satisfied")
                return False

            # Start components
            if not await self.scheduler.start_scheduling():
                logger.error("❌ Failed to start scheduler")
                return False

            self.is_running = True
            logger.info("✅ Adaptive learning orchestration started")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start orchestration: {e}")
            return False

    async def stop_orchestration(self) -> bool:
        """Stop the orchestration service"""
        try:
            # Stop scheduler
            await self.scheduler.stop_scheduling()

            # Complete active workflows gracefully
            active_workflows = list(self.workflow_manager.active_workflows.keys())
            for workflow_id in active_workflows:
                await self.workflow_manager.cleanup_workflow(workflow_id)

            self.is_running = False
            logger.info("⏹️ Adaptive learning orchestration stopped")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to stop orchestration: {e}")
            return False

    async def add_model_orchestration(
        self,
        model_id: str,
        learning_strategy: LearningStrategy = LearningStrategy.INCREMENTAL,
        orchestration_strategy: OrchestrationStrategy = OrchestrationStrategy.HYBRID,
        auto_learning: bool = True,
    ) -> bool:
        """Add a model to orchestrated adaptive learning"""
        try:
            if model_id in self.monitored_models:
                logger.warning(f"⚠️ Model {model_id} already under orchestration")
                return True

            # Add to scheduler
            success = await self.scheduler.add_model_scheduling(
                model_id=model_id, strategy=orchestration_strategy, auto_learning=auto_learning
            )

            if success:
                self.monitored_models.add(model_id)
                logger.info(f"🎯 Added model {model_id} to orchestrated adaptive learning")
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Failed to add model orchestration: {e}")
            return False

    async def remove_model_orchestration(self, model_id: str) -> bool:
        """Remove a model from orchestrated adaptive learning"""
        try:
            if model_id not in self.monitored_models:
                logger.warning(f"⚠️ Model {model_id} not under orchestration")
                return True

            # Cancel any active workflows for this model
            active_workflows = await self.workflow_manager.get_active_workflows_for_model(model_id)
            for workflow in active_workflows:
                await self.workflow_manager.cancel_workflow(workflow.workflow_id)

            # Remove from scheduler
            await self.scheduler.remove_model_scheduling(model_id)

            self.monitored_models.discard(model_id)
            logger.info(f"🗑️ Removed model {model_id} from orchestrated adaptive learning")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to remove model orchestration: {e}")
            return False

    async def trigger_adaptive_learning(
        self,
        model_id: str,
        trigger_reason: str = "manual",
        custom_config: dict[str, Any] | None = None,
    ) -> str | None:
        """Manually trigger adaptive learning workflow"""
        try:
            if model_id not in self.monitored_models:
                logger.error(f"❌ Model {model_id} not under orchestration")
                return None

            # Create workflow
            workflow_id = await self.workflow_manager.create_workflow(
                model_id=model_id,
                strategy=OrchestrationStrategy.REACTIVE,  # Manual triggers are reactive
                triggered_by=trigger_reason,
                custom_config=custom_config,
            )

            if workflow_id:
                # Start workflow execution in background
                await self._execute_workflow_async(workflow_id)
                self.orchestration_metrics.total_workflows += 1

                logger.info(
                    f"🚀 Triggered adaptive learning workflow {workflow_id} for model {model_id}"
                )
                return workflow_id

            return None

        except Exception as e:
            logger.error(f"❌ Failed to trigger adaptive learning: {e}")
            return None

    async def get_workflow_status(self, workflow_id: str) -> dict[str, Any] | None:
        """Get status of a specific workflow"""
        try:
            workflow = await self.workflow_manager.get_workflow(workflow_id)
            if not workflow:
                return None

            return {
                "workflow_id": workflow.workflow_id,
                "model_id": workflow.model_id,
                "strategy": workflow.strategy.value,
                "current_stage": workflow.current_stage.value,
                "status": workflow.status.value,
                "triggered_by": workflow.triggered_by,
                "created_at": workflow.created_at.isoformat(),
                "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
                "completed_at": workflow.completed_at.isoformat()
                if workflow.completed_at
                else None,
                "metadata": workflow.metadata,
                "learning_results": workflow.learning_results,
                "deployment_results": workflow.deployment_results,
                "performance_metrics": workflow.performance_metrics,
            }

        except Exception as e:
            logger.error(f"❌ Failed to get workflow status: {e}")
            return None

    async def get_model_status(self, model_id: str) -> dict[str, Any]:
        """Get orchestration status for a specific model"""
        try:
            if model_id not in self.monitored_models:
                return {"model_id": model_id, "status": "not_monitored"}

            # Get active workflows
            active_workflows = await self.workflow_manager.get_active_workflows_for_model(model_id)

            # Get workflow history
            history = await self.workflow_manager.get_workflow_history(model_id, limit=5)

            return {
                "model_id": model_id,
                "status": "monitored",
                "active_workflows": len(active_workflows),
                "active_workflow_details": [
                    {
                        "workflow_id": w.workflow_id,
                        "current_stage": w.current_stage.value,
                        "status": w.status.value,
                        "created_at": w.created_at.isoformat(),
                    }
                    for w in active_workflows
                ],
                "recent_workflows": [
                    {
                        "workflow_id": w.workflow_id,
                        "status": w.status.value,
                        "triggered_by": w.triggered_by,
                        "completed_at": w.completed_at.isoformat() if w.completed_at else None,
                    }
                    for w in history
                ],
            }

        except Exception as e:
            logger.error(f"❌ Failed to get model status: {e}")
            return {"model_id": model_id, "error": str(e)}

    async def get_orchestration_metrics(self) -> dict[str, Any]:
        """Get orchestration service metrics"""
        try:
            # Update metrics
            self.orchestration_metrics.active_workflows = len(
                self.workflow_manager.active_workflows
            )

            # Get component statuses
            workflow_status = await self.workflow_manager.get_status()
            scheduler_status = await self.scheduler.get_scheduling_status()
            stage_executor_status = await self.stage_executor.get_status()

            return {
                "service": "adaptive_learning_orchestrator",
                "is_running": self.is_running,
                "monitored_models": len(self.monitored_models),
                "metrics": {
                    "total_workflows": self.orchestration_metrics.total_workflows,
                    "successful_workflows": self.orchestration_metrics.successful_workflows,
                    "failed_workflows": self.orchestration_metrics.failed_workflows,
                    "active_workflows": self.orchestration_metrics.active_workflows,
                    "avg_workflow_duration_minutes": self.orchestration_metrics.avg_workflow_duration_minutes,
                },
                "components": {
                    "workflow_manager": workflow_status,
                    "scheduler": scheduler_status,
                    "stage_executor": stage_executor_status,
                },
                "config": {
                    "strategy": self.config.strategy.value,
                    "max_concurrent_workflows": self.config.max_concurrent_workflows,
                    "auto_learning_enabled": self.config.auto_learning_enabled,
                    "auto_deployment_enabled": self.config.auto_deployment_enabled,
                },
            }

        except Exception as e:
            logger.error(f"❌ Failed to get orchestration metrics: {e}")
            return {"error": str(e)}

    async def _execute_workflow_async(self, workflow_id: str) -> None:
        """Execute workflow asynchronously in background"""
        try:
            workflow = await self.workflow_manager.get_workflow(workflow_id)
            if not workflow:
                logger.error(f"❌ Workflow {workflow_id} not found for execution")
                return

            await self._execute_workflow(workflow)

        except Exception as e:
            logger.error(f"❌ Failed to execute workflow {workflow_id}: {e}")
            await self.workflow_manager.cancel_workflow(workflow_id)

    async def _execute_workflow(self, workflow) -> None:
        """Execute a complete workflow through all stages"""
        try:
            workflow_id = workflow.workflow_id

            # Update status to in progress
            await self.workflow_manager.update_workflow_status(
                workflow_id, UpdateStatus.IN_PROGRESS
            )

            # Execute stages based on strategy
            current_stage = workflow.current_stage

            while current_stage not in [
                workflow.current_stage.COMPLETED,
                workflow.current_stage.FAILED,
            ]:
                # Execute current stage
                stage_result = await self.stage_executor.execute_stage(workflow, current_stage)

                if not stage_result.get("success", False):
                    # Stage failed
                    error_msg = stage_result.get("error", "Unknown error")
                    logger.error(
                        f"❌ Stage {current_stage.value} failed for workflow {workflow_id}: {error_msg}"
                    )

                    # Check if rollback is needed
                    if stage_result.get("needs_rollback", False):
                        rollback_result = await self.stage_executor.execute_stage(
                            workflow, workflow.current_stage.ROLLBACK
                        )
                        if rollback_result.get("success", False):
                            logger.info(f"✅ Rollback completed for workflow {workflow_id}")

                    await self.workflow_manager.complete_workflow(workflow_id, success=False)
                    self.orchestration_metrics.failed_workflows += 1
                    return

                # Update workflow with stage results
                await self.workflow_manager.update_workflow_stage(
                    workflow_id, current_stage, stage_result
                )

                # Determine next stage
                next_stage = stage_result.get("next_stage")
                if next_stage:
                    current_stage = next_stage
                    await self.workflow_manager.update_workflow_stage(workflow_id, current_stage)
                else:
                    break

            # Complete workflow
            await self.workflow_manager.complete_workflow(workflow_id, success=True)
            self.orchestration_metrics.successful_workflows += 1

            logger.info(f"✅ Completed workflow {workflow_id}")

        except Exception as e:
            logger.error(f"❌ Failed to execute workflow: {e}")
            await self.workflow_manager.complete_workflow(workflow.workflow_id, success=False)
            self.orchestration_metrics.failed_workflows += 1

    async def _validate_dependencies(self) -> bool:
        """Validate that all required services are available"""
        try:
            # This would implement actual service health checks
            # For now, assume dependencies are valid
            return True

        except Exception as e:
            logger.error(f"❌ Failed to validate dependencies: {e}")
            return False

    async def shutdown(self) -> None:
        """Shutdown orchestrator service"""
        try:
            await self.stop_orchestration()
            logger.info("🛑 Adaptive learning orchestrator shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "service": "adaptive_learning_orchestrator",
            "status": "healthy" if self.is_running else "stopped",
            "is_running": self.is_running,
            "monitored_models": len(self.monitored_models),
            "active_workflows": len(self.workflow_manager.active_workflows),
        }
