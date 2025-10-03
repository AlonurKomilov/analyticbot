"""
Learning Task Microservice
==========================

Complete learning task capabilities with clean architecture.
All learning-related services and components are contained within this microservice.
"""

from .learning_task_service import LearningTaskService
from .learning_task_manager import (
    LearningTaskManager,
    LearningTaskManagerConfig
)
from .task_creator import (
    TaskCreator,
    TaskConfig
)
from .task_scheduler import (
    TaskScheduler,
    SchedulerConfig,
    WorkerInfo
)
from .progress_tracker import (
    ProgressTracker,
    ProgressConfig,
    TaskExecutionContext
)
from .incremental_learning_engine import (
    IncrementalLearningEngine,
    IncrementalLearningConfig,
    MemoryStrategy,
    LearningContext
)
from .model_training_executor import (
    ModelTrainingExecutor,
    ExecutionPhase,
    ResourceUsage,
    TrainingProgress
)

__all__ = [
    # Main service
    'LearningTaskService',
    
    # Task management (refactored into components)
    'LearningTaskManager',
    'LearningTaskManagerConfig',
    
    # Specialized components
    'TaskCreator',
    'TaskConfig',
    'TaskScheduler',
    'SchedulerConfig',
    'WorkerInfo',
    'ProgressTracker',
    'ProgressConfig',
    'TaskExecutionContext',
    
    # Learning engine
    'IncrementalLearningEngine',
    'IncrementalLearningConfig',
    'MemoryStrategy',
    'LearningContext',
    
    # Training execution
    'ModelTrainingExecutor',
    'ExecutionPhase',
    'ResourceUsage',
    'TrainingProgress'
]

# Microservice metadata
__microservice__ = {
    'name': 'learning_tasks',
    'version': '2.0.0',
    'description': 'Clean architecture learning task management with specialized components',
    'components': [
        'LearningTaskService',
        'LearningTaskManager',
        'TaskCreator',
        'TaskScheduler', 
        'ProgressTracker',
        'IncrementalLearningEngine',
        'ModelTrainingExecutor'
    ],
    'refactoring_notes': 'Broke down 815-line god object into focused components'
}