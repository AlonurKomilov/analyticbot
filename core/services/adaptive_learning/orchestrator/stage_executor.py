"""
Stage Executor
=============

Executes individual stages of adaptive learning workflows.
Coordinates with microservices to perform specific workflow stages.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..deployment import ModelUpdateService
from ..drift import DriftDetectionService
from ..feedback import FeedbackCollectionService
from ..learning import LearningTaskService
from ..protocols.learning_protocols import LearningStrategy
from .workflow_models import AdaptiveLearningWorkflow, WorkflowStage

logger = logging.getLogger(__name__)


class StageExecutor:
    """
    Executes individual workflow stages by coordinating with microservices.

    Each stage execution is self-contained and returns success/failure
    along with any stage-specific results or metadata.
    """

    def __init__(
        self,
        drift_service: DriftDetectionService,
        feedback_service: FeedbackCollectionService,
        learning_service: LearningTaskService,
        deployment_service: ModelUpdateService,
        min_confidence_threshold: float = 0.8,
        performance_improvement_threshold: float = 0.05,
    ):
        self.drift_service = drift_service
        self.feedback_service = feedback_service
        self.learning_service = learning_service
        self.deployment_service = deployment_service
        self.min_confidence_threshold = min_confidence_threshold
        self.performance_improvement_threshold = performance_improvement_threshold

        logger.info("🎬 Stage Executor initialized")

    async def execute_stage(
        self, workflow: AdaptiveLearningWorkflow, stage: WorkflowStage
    ) -> dict[str, Any]:
        """Execute a specific workflow stage"""
        try:
            logger.info(f"🎬 Executing stage {stage.value} for workflow {workflow.workflow_id}")

            if stage == WorkflowStage.DRIFT_DETECTION:
                return await self._execute_drift_detection_stage(workflow)
            elif stage == WorkflowStage.FEEDBACK_COLLECTION:
                return await self._execute_feedback_collection_stage(workflow)
            elif stage == WorkflowStage.LEARNING_TASK_CREATION:
                return await self._execute_learning_task_creation_stage(workflow)
            elif stage == WorkflowStage.MODEL_TRAINING:
                return await self._execute_model_training_stage(workflow)
            elif stage == WorkflowStage.MODEL_VALIDATION:
                return await self._execute_model_validation_stage(workflow)
            elif stage == WorkflowStage.MODEL_DEPLOYMENT:
                return await self._execute_model_deployment_stage(workflow)
            elif stage == WorkflowStage.ROLLBACK:
                return await self._execute_rollback_stage(workflow)
            else:
                return {"success": False, "error": f"Unknown stage: {stage.value}"}

        except Exception as e:
            logger.error(f"❌ Failed to execute stage {stage.value}: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_drift_detection_stage(
        self, workflow: AdaptiveLearningWorkflow
    ) -> dict[str, Any]:
        """Execute drift detection stage"""
        try:
            # Trigger drift analysis
            analysis_result = await self.drift_service.analyze_drift(workflow.model_id)

            if "error" in analysis_result:
                return {
                    "success": False,
                    "error": f"Drift analysis failed: {analysis_result['error']}",
                }

            # Check if significant drift detected
            drift_detected = analysis_result.get("drift_detected", False)
            drift_severity = analysis_result.get("severity", "low")

            # Store analysis ID for later reference
            if "analysis_id" in analysis_result:
                workflow.drift_analysis_id = analysis_result["analysis_id"]

            return {
                "success": True,
                "drift_detected": drift_detected,
                "drift_severity": drift_severity,
                "analysis_result": analysis_result,
                "next_stage": WorkflowStage.FEEDBACK_COLLECTION
                if drift_detected
                else WorkflowStage.COMPLETED,
            }

        except Exception as e:
            logger.error(f"❌ Drift detection stage failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_feedback_collection_stage(
        self, workflow: AdaptiveLearningWorkflow
    ) -> dict[str, Any]:
        """Execute feedback collection stage"""
        try:
            # Get recent feedback for the model
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)  # Last week

            feedback_analysis = await self.feedback_service.get_feedback_analysis(
                content_id=workflow.model_id, time_range=(start_time, end_time)
            )

            if "error" in feedback_analysis:
                return {
                    "success": False,
                    "error": f"Feedback analysis failed: {feedback_analysis['error']}",
                }

            feedback_count = feedback_analysis.get("total_feedback", 0)

            # Store feedback batch ID if available
            if "batch_id" in feedback_analysis:
                workflow.feedback_batch_id = feedback_analysis["batch_id"]

            return {
                "success": True,
                "feedback_count": feedback_count,
                "feedback_analysis": feedback_analysis,
                "next_stage": WorkflowStage.LEARNING_TASK_CREATION
                if feedback_count > 0
                else WorkflowStage.COMPLETED,
            }

        except Exception as e:
            logger.error(f"❌ Feedback collection stage failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_learning_task_creation_stage(
        self, workflow: AdaptiveLearningWorkflow
    ) -> dict[str, Any]:
        """Execute learning task creation stage"""
        try:
            # Determine learning strategy based on workflow strategy
            if workflow.strategy.value == "continuous":
                learning_strategy = LearningStrategy.INCREMENTAL
            elif workflow.strategy.value == "reactive":
                learning_strategy = LearningStrategy.BATCH_UPDATE
            else:
                learning_strategy = LearningStrategy.INCREMENTAL

            # Create learning task
            task_config = {
                "model_id": workflow.model_id,
                "learning_strategy": learning_strategy,
                "drift_analysis_id": workflow.drift_analysis_id,
                "feedback_batch_id": workflow.feedback_batch_id,
                "workflow_id": workflow.workflow_id,
            }

            task_result = await self.learning_service.create_learning_task(
                model_id=workflow.model_id, task_config=task_config
            )

            if "error" in task_result:
                return {
                    "success": False,
                    "error": f"Learning task creation failed: {task_result['error']}",
                }

            # Store learning task ID
            if "task_id" in task_result:
                workflow.learning_task_id = task_result["task_id"]

            return {
                "success": True,
                "task_id": task_result.get("task_id"),
                "task_config": task_config,
                "next_stage": WorkflowStage.MODEL_TRAINING,
            }

        except Exception as e:
            logger.error(f"❌ Learning task creation stage failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_model_training_stage(
        self, workflow: AdaptiveLearningWorkflow
    ) -> dict[str, Any]:
        """Execute model training stage"""
        try:
            if not workflow.learning_task_id:
                return {"success": False, "error": "No learning task ID available"}

            # Execute learning task
            training_result = await self.learning_service.execute_learning_task(
                workflow.learning_task_id
            )

            if "error" in training_result:
                return {
                    "success": False,
                    "error": f"Model training failed: {training_result['error']}",
                }

            # Check training metrics
            training_metrics = training_result.get("training_metrics", {})
            model_confidence = training_metrics.get("confidence", 0.0)

            # Store training results
            workflow.learning_results = training_result

            return {
                "success": True,
                "training_result": training_result,
                "model_confidence": model_confidence,
                "next_stage": WorkflowStage.MODEL_VALIDATION
                if model_confidence >= self.min_confidence_threshold
                else WorkflowStage.FAILED,
            }

        except Exception as e:
            logger.error(f"❌ Model training stage failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_model_validation_stage(
        self, workflow: AdaptiveLearningWorkflow
    ) -> dict[str, Any]:
        """Execute model validation stage"""
        try:
            if not workflow.learning_results:
                return {"success": False, "error": "No training results available for validation"}

            # Get model validation metrics from learning service
            validation_result = await self.learning_service.validate_model(
                workflow.model_id, workflow.learning_results
            )

            if "error" in validation_result:
                return {
                    "success": False,
                    "error": f"Model validation failed: {validation_result['error']}",
                }

            # Check validation metrics
            validation_metrics = validation_result.get("validation_metrics", {})
            performance_improvement = validation_metrics.get("performance_improvement", 0.0)

            # Store performance metrics
            workflow.performance_metrics = validation_metrics

            return {
                "success": True,
                "validation_result": validation_result,
                "performance_improvement": performance_improvement,
                "next_stage": WorkflowStage.MODEL_DEPLOYMENT
                if performance_improvement >= self.performance_improvement_threshold
                else WorkflowStage.COMPLETED,
            }

        except Exception as e:
            logger.error(f"❌ Model validation stage failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_model_deployment_stage(
        self, workflow: AdaptiveLearningWorkflow
    ) -> dict[str, Any]:
        """Execute model deployment stage"""
        try:
            if not workflow.learning_results:
                return {"success": False, "error": "No model results available for deployment"}

            # Create deployment plan
            deployment_config = {
                "model_id": workflow.model_id,
                "workflow_id": workflow.workflow_id,
                "learning_results": workflow.learning_results,
                "performance_metrics": workflow.performance_metrics,
            }

            deployment_result = await self.deployment_service.create_deployment_plan(
                workflow.model_id, deployment_config
            )

            if "error" in deployment_result:
                return {
                    "success": False,
                    "error": f"Deployment planning failed: {deployment_result['error']}",
                }

            # Store deployment plan ID
            if "deployment_plan_id" in deployment_result:
                workflow.deployment_plan_id = deployment_result["deployment_plan_id"]

            # Execute deployment
            execution_result = await self.deployment_service.execute_deployment(
                deployment_result.get("deployment_plan_id")
            )

            if "error" in execution_result:
                return {
                    "success": False,
                    "error": f"Deployment execution failed: {execution_result['error']}",
                    "needs_rollback": True,
                }

            # Store deployment results
            workflow.deployment_results = execution_result

            return {
                "success": True,
                "deployment_result": execution_result,
                "next_stage": WorkflowStage.COMPLETED,
            }

        except Exception as e:
            logger.error(f"❌ Model deployment stage failed: {e}")
            return {"success": False, "error": str(e), "needs_rollback": True}

    async def _execute_rollback_stage(self, workflow: AdaptiveLearningWorkflow) -> dict[str, Any]:
        """Execute rollback stage"""
        try:
            if not workflow.deployment_plan_id:
                return {
                    "success": True,  # Nothing to rollback
                    "message": "No deployment to rollback",
                }

            # Execute rollback
            rollback_result = await self.deployment_service.rollback_deployment(
                workflow.deployment_plan_id
            )

            if "error" in rollback_result:
                return {"success": False, "error": f"Rollback failed: {rollback_result['error']}"}

            return {
                "success": True,
                "rollback_result": rollback_result,
                "next_stage": WorkflowStage.FAILED,
            }

        except Exception as e:
            logger.error(f"❌ Rollback stage failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_status(self) -> dict[str, Any]:
        """Get stage executor status"""
        return {
            "service": "stage_executor",
            "min_confidence_threshold": self.min_confidence_threshold,
            "performance_improvement_threshold": self.performance_improvement_threshold,
        }
