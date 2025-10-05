"""
Learning Task Microservice
==========================

Complete learning task capabilities with clean architecture.
All learning-related services and components are contained within this microservice.
"""

from .incremental_learning_engine import (
    IncrementalLearningConfig,
    IncrementalLearningEngine,
    LearningContext,
    MemoryStrategy,
)
from .learning_task_manager import LearningTaskManager, LearningTaskManagerConfig
from .learning_task_service import LearningTaskService
from .model_training_executor import (
    ExecutionPhase,
    ModelTrainingExecutor,
    ResourceUsage,
    TrainingProgress,
)
from .progress_tracker import ProgressConfig, ProgressTracker, TaskExecutionContext
from .task_creator import TaskConfig, TaskCreator
from .task_scheduler import SchedulerConfig, TaskScheduler, WorkerInfo

__all__ = [
    # Main service
    "LearningTaskService",
    # Task management (refactored into components)
    "LearningTaskManager",
    "LearningTaskManagerConfig",
    # Specialized components
    "TaskCreator",
    "TaskConfig",
    "TaskScheduler",
    "SchedulerConfig",
    "WorkerInfo",
    "ProgressTracker",
    "ProgressConfig",
    "TaskExecutionContext",
    # Learning engine
    "IncrementalLearningEngine",
    "IncrementalLearningConfig",
    "MemoryStrategy",
    "LearningContext",
    # Training execution
    "ModelTrainingExecutor",
    "ExecutionPhase",
    "ResourceUsage",
    "TrainingProgress",
]

# Microservice metadata
__microservice__ = {
    "name": "learning_tasks",
    "version": "2.0.0",
    "description": "Clean architecture learning task management with specialized components",
    "components": [
        "LearningTaskService",
        "LearningTaskManager",
        "TaskCreator",
        "TaskScheduler",
        "ProgressTracker",
        "IncrementalLearningEngine",
        "ModelTrainingExecutor",
    ],
    "refactoring_notes": "Broke down 815-line god object into focused components",
}
