"""
Predictive Modeling Data Models
================================

Shared dataclasses and configuration for predictive modeling microservices.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelingConfig:
    """Configuration for predictive modeling services."""

    # Confidence thresholds
    confidence_thresholds: dict[str, float] = field(
        default_factory=lambda: {
            "very_high": 0.85,
            "high": 0.70,
            "medium": 0.55,
            "low": 0.40,
        }
    )

    # Prediction horizons
    prediction_horizons: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "short_term": {"days": 7, "confidence_factor": 0.9},
            "medium_term": {"days": 30, "confidence_factor": 0.7},
            "long_term": {"days": 180, "confidence_factor": 0.5},
        }
    )

    # Narrative styles
    narrative_styles: dict[str, str] = field(
        default_factory=lambda: {
            "conversational": "friendly and accessible",
            "technical": "detailed and analytical",
            "executive": "concise and strategic",
        }
    )

    # Context weight factors
    context_weight_factors: dict[str, float] = field(
        default_factory=lambda: {
            "environmental": 0.25,
            "temporal": 0.30,
            "competitive": 0.25,
            "behavioral": 0.20,
        }
    )


@dataclass
class EnhancedPrediction:
    """Enhanced prediction result with intelligence context."""

    prediction_id: str
    base_predictions: dict[str, Any]
    enhanced_predictions: dict[str, Any]
    intelligence_enhancements: dict[str, Any]
    confidence_analysis: Any  # ConfidenceLevel from protocols
    prediction_metadata: dict[str, Any]
    generated_at: str

    # Legacy simple fields for backwards compatibility
    prediction_target: str = ""
    prediction_horizon: str = ""
    confidence_level: Any = None
    contextual_factors: list[str] = field(default_factory=list)
    temporal_factors: list[str] = field(default_factory=list)
    enhancement_impact: float = 0.0


@dataclass
class ValidationResult:
    """Prediction validation result with accuracy metrics."""

    prediction_id: str = ""
    validation_status: str = "completed"
    validation_timestamp: str = ""
    accuracy_metrics: dict[str, Any] = field(default_factory=dict)
    error_analysis: dict[str, Any] = field(default_factory=dict)
    confidence_calibration: dict[str, Any] = field(default_factory=dict)
    learning_insights: list[str] = field(default_factory=list)
    overall_accuracy_score: float = 0.0

    # Simplified constructor parameters
    overall_accuracy: float = 0.0
    accuracy_by_metric: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        # Set overall_accuracy_score from overall_accuracy if provided
        if self.overall_accuracy > 0:
            self.overall_accuracy_score = self.overall_accuracy
        if self.accuracy_by_metric:
            self.accuracy_metrics = self.accuracy_by_metric
