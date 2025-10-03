"""
Orchestrator Microservice
========================

Coordinates and orchestrates all adaptive learning operations.
Clean architecture implementation with separated concerns:

- AdaptiveLearningOrchestrator: Main orchestrator service
- WorkflowManager: Workflow lifecycle management  
- StageExecutor: Individual stage execution
- OrchestrationScheduler: Background scheduling and monitoring
- workflow_models: Data models and configuration
"""

from .adaptive_learning_orchestrator import AdaptiveLearningOrchestrator
from .workflow_manager import WorkflowManager
from .stage_executor import StageExecutor
from .orchestration_scheduler import OrchestrationScheduler
from .workflow_models import (
    OrchestrationStrategy,
    WorkflowStage,
    OrchestrationConfig,
    AdaptiveLearningWorkflow,
    OrchestrationMetrics
)

__all__ = [
    # Main service
    'AdaptiveLearningOrchestrator',
    
    # Components
    'WorkflowManager',
    'StageExecutor',
    'OrchestrationScheduler',
    
    # Models
    'OrchestrationStrategy',
    'WorkflowStage',
    'OrchestrationConfig',
    'AdaptiveLearningWorkflow',
    'OrchestrationMetrics'
]

# Microservice metadata
__microservice__ = {
    'name': 'orchestrator',
    'version': '2.0.0',
    'description': 'Clean architecture orchestration with separated workflow management, stage execution, and scheduling',
    'components': [
        'AdaptiveLearningOrchestrator',
        'WorkflowManager',
        'StageExecutor',
        'OrchestrationScheduler'
    ]
}