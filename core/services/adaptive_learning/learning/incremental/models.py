"""
Incremental Learning Data Models
================================

Shared dataclasses and configuration for incremental learning microservices.
Note: LearningContext moved to protocols/learning_protocols.py for consistency.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import torch

# Import the centralized LearningContext


class MemoryStrategy(Enum):
    """Memory strategies for continual learning"""

    RANDOM_SAMPLING = "random_sampling"
    IMPORTANCE_SAMPLING = "importance_sampling"
    GRADIENT_BASED = "gradient_based"
    CLUSTERING_BASED = "clustering_based"


@dataclass
class IncrementalLearningConfig:
    """Configuration for incremental learning"""

    memory_buffer_size: int = 1000
    rehearsal_ratio: float = 0.2
    learning_rate: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 1e-4
    temperature: float = 3.0  # For knowledge distillation
    alpha: float = 0.5  # Balance between old and new knowledge
    plasticity_factor: float = 0.1  # Control plasticity vs stability


@dataclass
class LearningResult:
    """Result of a learning operation"""

    success: bool
    final_loss: float
    metrics: dict[str, Any]
    epochs_completed: int = 0
    processed_samples: int = 0
    strategy_used: str = ""
    error: str | None = None


@dataclass
class MemoryOperation:
    """Memory buffer operation result"""

    operation_type: str  # "add", "sample", "update_importance"
    items_processed: int
    buffer_size_after: int
    success: bool
    error: str | None = None


@dataclass
class ModelEvaluation:
    """Model evaluation result"""

    model_id: str
    evaluation_type: str  # "accuracy", "loss", "performance"
    metrics: dict[str, float]
    evaluation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    sample_count: int = 0
    success: bool = True


@dataclass
class ImportanceWeights:
    """Importance weights for EWC-style regularization"""

    model_id: str
    parameter_importance: dict[str, torch.Tensor]
    calculation_method: str  # "fisher", "gradient_based", "empirical"
    sample_count: int
    calculated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class BatchData:
    """Processed batch data for training"""

    inputs: torch.Tensor
    targets: torch.Tensor
    batch_size: int
    device: str
    metadata: dict[str, Any] = field(default_factory=dict)
