"""
Incremental Learning Package
=============================

Refactored incremental learning engine split into 5 microservices:

1. LearningStrategy - Core learning algorithms and strategy implementation
2. MemoryManager - Memory buffer operations and data retention
3. ContextManager - Learning context tracking and progression analysis
4. ModelOperator - Model evaluation, optimization, and performance tracking
5. DataProcessor - Data preparation, batching, and quality management
6. LearningOrchestrator - Coordination and backwards compatibility

Usage:
    # Use orchestrator for complete functionality (backwards compatible)
    from core.services.adaptive_learning.learning import IncrementalLearningEngine

    # Or use individual microservices
    from core.services.adaptive_learning.learning import (
        LearningStrategy,
        MemoryManager,
        ContextManager,
        ModelOperator,
        DataProcessor,
    )
"""

# Export data models (when ready)
# from .models import (
#     LearningConfig,
#     LearningContext,
#     DataBatch,
#     ModelEvaluation,
#     MemoryBuffer,
# )

# Export microservices
# from .strategy import LearningStrategy  # TODO: Create learning_strategy.py
from .context import ContextManager
from .data import DataProcessor
from .learning_task_manager import LearningTaskManager, LearningTaskManagerConfig

# Legacy exports for backwards compatibility (temporarily keep until refactoring complete)
from .learning_task_service import LearningTaskService
from .memory import MemoryManager
from .model import ModelOperator

# Note: IncrementalLearningEngine now refers to our new orchestrator
from .model_training_executor import (
    ExecutionPhase,
    ModelTrainingExecutor,
    ResourceUsage,
    TrainingProgress,
)
from .orchestrator import IncrementalLearningEngine, LearningOrchestrator
from .progress_tracker import ProgressConfig, ProgressTracker, TaskExecutionContext
from .task_creator import TaskCreationConfig, TaskCreator
from .task_scheduler import SchedulingConfig, TaskScheduler, WorkerInfo

__all__ = [
    # New microservices (Priority #5 refactoring)
    # "LearningStrategy",  # TODO: Uncomment when created
    "MemoryManager",
    "ContextManager",
    "ModelOperator",
    "DataProcessor",
    "LearningOrchestrator",
    "IncrementalLearningEngine",  # New orchestrator (backwards compatible)
    # Legacy services (keep for compatibility)
    "LearningTaskService",
    "LearningTaskManager",
    "LearningTaskManagerConfig",
    "TaskCreator",
    "TaskCreationConfig",
    "TaskScheduler",
    "SchedulingConfig",
    "WorkerInfo",
    "ProgressTracker",
    "ProgressConfig",
    "TaskExecutionContext",
    "ModelTrainingExecutor",
    "ExecutionPhase",
    "ResourceUsage",
    "TrainingProgress",
]
