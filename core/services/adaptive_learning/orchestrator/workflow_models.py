"""
Workflow Models
==============

Data models for adaptive learning workflows and orchestration.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from ..protocols.learning_protocols import UpdateStatus


class OrchestrationStrategy(Enum):
    """Orchestration strategies for adaptive learning"""
    REACTIVE = "reactive"  # Respond to drift detection
    PROACTIVE = "proactive"  # Scheduled updates
    CONTINUOUS = "continuous"  # Continuous learning
    HYBRID = "hybrid"  # Combined approach


class WorkflowStage(Enum):
    """Stages in adaptive learning workflow"""
    MONITORING = "monitoring"
    DRIFT_DETECTION = "drift_detection"
    FEEDBACK_COLLECTION = "feedback_collection" 
    LEARNING_TASK_CREATION = "learning_task_creation"
    MODEL_TRAINING = "model_training"
    MODEL_VALIDATION = "model_validation"
    MODEL_DEPLOYMENT = "model_deployment"
    ROLLBACK = "rollback"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class OrchestrationConfig:
    """Configuration for orchestration service"""
    strategy: OrchestrationStrategy = OrchestrationStrategy.HYBRID
    monitoring_interval_minutes: int = 30
    drift_check_frequency_hours: int = 6
    feedback_collection_threshold: int = 100
    auto_learning_enabled: bool = True
    auto_deployment_enabled: bool = False
    max_concurrent_workflows: int = 5
    workflow_timeout_hours: int = 12
    min_confidence_threshold: float = 0.8
    performance_improvement_threshold: float = 0.05


@dataclass
class AdaptiveLearningWorkflow:
    """Represents an adaptive learning workflow"""
    workflow_id: str
    model_id: str
    strategy: OrchestrationStrategy
    current_stage: WorkflowStage
    status: UpdateStatus
    triggered_by: str  # "drift_detection", "scheduled", "manual", "feedback"
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Workflow context
    drift_analysis_id: Optional[str] = None
    learning_task_id: Optional[str] = None
    deployment_plan_id: Optional[str] = None
    feedback_batch_id: Optional[str] = None
    
    # Results
    learning_results: Optional[Dict[str, Any]] = None
    deployment_results: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class OrchestrationMetrics:
    """Orchestration service metrics"""
    total_workflows: int = 0
    successful_workflows: int = 0
    failed_workflows: int = 0
    avg_workflow_duration_minutes: float = 0.0
    active_workflows: int = 0
    drift_triggered_workflows: int = 0
    scheduled_workflows: int = 0
    feedback_triggered_workflows: int = 0