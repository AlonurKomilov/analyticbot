"""
Learning Protocols for Adaptive Learning
========================================

Defines interfaces for online learning, incremental updates, and model adaptation.
These protocols ensure clean separation of concerns and dependency injection.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class LearningStrategy(Enum):
    """Types of learning strategies"""

    INCREMENTAL = "incremental"  # Gradual learning from new data
    BATCH_UPDATE = "batch_update"  # Periodic batch updates
    ONLINE_SGD = "online_sgd"  # Online stochastic gradient descent
    TRANSFER_LEARNING = "transfer_learning"  # Transfer from related models
    CONTINUAL_LEARNING = "continual_learning"  # Continual learning with memory
    REINFORCEMENT = "reinforcement"  # Reinforcement learning from feedback


class UpdateStatus(Enum):
    """Status of model updates"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ModelVersion(Enum):
    """Model version types"""

    MAJOR = "major"  # Breaking changes
    MINOR = "minor"  # New features
    PATCH = "patch"  # Bug fixes
    HOTFIX = "hotfix"  # Critical fixes


class DeploymentStage(Enum):
    """Deployment stages for model updates"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    CANARY = "canary"
    PRODUCTION = "production"


@dataclass
class LearningTask:
    """Learning task data structure"""

    task_id: str
    model_id: str
    strategy: LearningStrategy
    data_source: str
    parameters: dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: UpdateStatus = UpdateStatus.PENDING
    progress: float = 0.0
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass
class ModelUpdate:
    """Model update data structure"""

    update_id: str
    model_id: str
    version: str
    version_type: ModelVersion
    changes: dict[str, Any]
    performance_before: dict[str, float]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    performance_after: dict[str, float] | None = None
    rollback_available: bool = True
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass
class LearningProgress:
    """Learning progress tracking"""

    task_id: str
    model_id: str
    current_epoch: int
    total_epochs: int
    training_loss: float
    validation_metrics: dict[str, float]
    timestamp: datetime
    metadata: dict[str, Any] | None = field(default_factory=dict)


class LearningProtocol(ABC):
    """
    Protocol for online and incremental learning services.

    This interface defines the contract for adapting models
    based on new data and feedback.
    """

    @abstractmethod
    async def create_learning_task(self, task: LearningTask) -> bool:
        """
        Create a new learning task

        Args:
            task: Learning task to create

        Returns:
            True if task was successfully created
        """

    @abstractmethod
    async def execute_learning_task(self, task_id: str) -> bool:
        """
        Execute a learning task

        Args:
            task_id: ID of the task to execute

        Returns:
            True if task execution started successfully
        """

    @abstractmethod
    async def get_learning_progress(self, task_id: str) -> LearningProgress | None:
        """
        Get progress of a learning task

        Args:
            task_id: ID of the task

        Returns:
            Learning progress or None if task not found
        """

    @abstractmethod
    async def cancel_learning_task(self, task_id: str) -> bool:
        """
        Cancel a running learning task

        Args:
            task_id: ID of the task to cancel

        Returns:
            True if task was successfully cancelled
        """

    @abstractmethod
    async def get_active_tasks(self, model_id: str | None = None) -> list[LearningTask]:
        """
        Get list of active learning tasks

        Args:
            model_id: Optional filter for specific model

        Returns:
            List of active learning tasks
        """


class OnlineLearnerProtocol(ABC):
    """
    Protocol for online learning implementations.

    This interface defines methods for real-time model updates
    based on streaming data and feedback.
    """

    @abstractmethod
    async def update_model_online(
        self, model_id: str, training_data: dict[str, Any], learning_rate: float = 0.001
    ) -> ModelUpdate:
        """
        Update model with online learning

        Args:
            model_id: ID of the model to update
            training_data: New training data
            learning_rate: Learning rate for update

        Returns:
            Model update information
        """

    @abstractmethod
    async def incremental_fit(
        self,
        model_id: str,
        batch_data: list[dict[str, Any]],
        validation_data: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Perform incremental fitting on new data batch

        Args:
            model_id: ID of the model
            batch_data: Batch of new training data
            validation_data: Optional validation data

        Returns:
            Dictionary containing fitting results
        """

    @abstractmethod
    async def adapt_to_feedback(
        self, model_id: str, feedback_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Adapt model based on user feedback

        Args:
            model_id: ID of the model
            feedback_data: List of feedback data

        Returns:
            Dictionary containing adaptation results
        """

    @abstractmethod
    async def validate_model_performance(
        self, model_id: str, test_data: list[dict[str, Any]]
    ) -> dict[str, float]:
        """
        Validate model performance after updates

        Args:
            model_id: ID of the model
            test_data: Test data for validation

        Returns:
            Dictionary containing performance metrics
        """


class ModelVersioningProtocol(ABC):
    """
    Protocol for model versioning and rollback capabilities.

    This interface defines methods for managing model versions
    and providing rollback functionality.
    """

    @abstractmethod
    async def create_model_checkpoint(
        self, model_id: str, version: str, model_state: dict[str, Any]
    ) -> bool:
        """
        Create a model checkpoint

        Args:
            model_id: ID of the model
            version: Version identifier
            model_state: Model state to checkpoint

        Returns:
            True if checkpoint was successfully created
        """

    @abstractmethod
    async def rollback_model(self, model_id: str, target_version: str) -> bool:
        """
        Rollback model to a previous version

        Args:
            model_id: ID of the model
            target_version: Version to rollback to

        Returns:
            True if rollback was successful
        """

    @abstractmethod
    async def get_model_versions(self, model_id: str) -> list[ModelUpdate]:
        """
        Get list of model versions

        Args:
            model_id: ID of the model

        Returns:
            List of model versions
        """

    @abstractmethod
    async def compare_model_versions(
        self, model_id: str, version1: str, version2: str
    ) -> dict[str, Any]:
        """
        Compare two model versions

        Args:
            model_id: ID of the model
            version1: First version to compare
            version2: Second version to compare

        Returns:
            Dictionary containing comparison results
        """


class IncrementalUpdaterProtocol(ABC):
    """
    Protocol for incremental model updates.

    This interface defines methods for gradually updating models
    without full retraining.
    """

    @abstractmethod
    async def schedule_incremental_update(
        self,
        model_id: str,
        update_frequency: str,  # "hourly", "daily", "weekly"
        update_parameters: dict[str, Any],
    ) -> str:
        """
        Schedule incremental updates

        Args:
            model_id: ID of the model
            update_frequency: Frequency of updates
            update_parameters: Parameters for updates

        Returns:
            Schedule ID
        """

    @abstractmethod
    async def perform_incremental_update(
        self, model_id: str, new_data: list[dict[str, Any]]
    ) -> ModelUpdate:
        """
        Perform incremental update with new data

        Args:
            model_id: ID of the model
            new_data: New data for update

        Returns:
            Model update information
        """

    @abstractmethod
    async def get_update_schedule(self, model_id: str) -> dict[str, Any]:
        """
        Get update schedule for a model

        Args:
            model_id: ID of the model

        Returns:
            Dictionary containing schedule information
        """


# Additional deployment-related classes and protocols


class DeploymentStrategy(Enum):
    """Deployment strategies"""

    DIRECT = "direct"
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"


class DeploymentStatus(Enum):
    """Deployment status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class ModelMetadata:
    """Model metadata for deployment"""

    model_id: str
    version: str
    architecture: str
    model_size: int
    requires_gpu: bool = False
    performance_metrics: dict[str, float] = field(default_factory=dict)
    creation_date: datetime = field(default_factory=datetime.utcnow)
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Validation result"""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    validation_details: dict[str, Any] = field(default_factory=dict)


class ModelDeploymentProtocol(ABC):
    """Protocol for model deployment operations"""

    @abstractmethod
    async def deploy_model(
        self,
        model_id: str,
        version: str,
        strategy: DeploymentStrategy,
        metadata: ModelMetadata,
    ) -> str:
        """Deploy model with specified strategy"""

    @abstractmethod
    async def get_deployment_status(self, deployment_id: str) -> DeploymentStatus:
        """Get deployment status"""

    @abstractmethod
    async def rollback_deployment(self, deployment_id: str, reason: str) -> bool:
        """Rollback deployment"""


class ModelUpdateProtocol(ABC):
    """Protocol for model update operations"""

    @abstractmethod
    async def plan_deployment(
        self,
        model_id: str,
        source_version: str,
        target_version: str,
        target_metadata: ModelMetadata,
    ) -> str | None:
        """Plan model deployment"""

    @abstractmethod
    async def execute_deployment(self, plan_id: str) -> str | None:
        """Execute deployment plan"""

    @abstractmethod
    async def get_deployment_status(self, execution_id: str) -> dict[str, Any] | None:
        """Get deployment status"""

    @abstractmethod
    async def trigger_rollback(self, model_id: str, target_version: str, reason: str) -> str | None:
        """Trigger rollback"""
