"""
Incremental Learning Data Models
=================================

Shared dataclasses and configuration for incremental learning microservices.
"""

from dataclasses import dataclass, field
from typing import Any

# Import the centralized LearningContext from protocols


@dataclass
class LearningConfig:
    """Configuration for incremental learning services."""

    # Learning parameters
    learning_rate: float = 0.01
    batch_size: int = 32
    memory_size: int = 1000

    # Learning weights
    learning_weights: dict[str, float] = field(
        default_factory=lambda: {
            "recent_data_weight": 0.7,
            "historical_data_weight": 0.3,
            "context_weight": 0.5,
            "performance_weight": 0.5,
        }
    )

    # Quality thresholds
    quality_thresholds: dict[str, float] = field(
        default_factory=lambda: {
            "minimum_quality": 0.7,
            "completeness_threshold": 0.8,
            "consistency_threshold": 0.8,
            "validity_threshold": 0.8,
        }
    )

    # Memory configuration
    memory_strategy: str = "fifo"  # "fifo", "lru", "weighted"
    memory_retention_hours: int = 168  # 1 week

    # Data processing
    stream_window_size: int = 100
    required_fields: list[str] = field(default_factory=list)


@dataclass
class DataBatch:
    """Data batch information for learning processing."""

    batch_id: str
    raw_data_size: int
    processed_data_size: int
    batch_count: int
    batch_size: int
    data_batches: list[list[dict[str, Any]]]
    quality_score: float
    processing_metadata: dict[str, Any]
    created_at: str


@dataclass
class ModelEvaluation:
    """Model evaluation results."""

    model_id: str
    performance_metrics: dict[str, float]
    complexity_score: float
    efficiency_metrics: dict[str, float]
    evaluation_timestamp: str
    data_size: int


@dataclass
class MemoryBuffer:
    """Memory buffer for incremental learning."""

    buffer_id: str
    max_size: int
    current_size: int
    retention_strategy: str
    stored_data: list[dict[str, Any]]
    metadata: dict[str, Any]
    created_at: str
    last_accessed: str
