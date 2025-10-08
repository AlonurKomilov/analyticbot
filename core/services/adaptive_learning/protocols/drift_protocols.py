"""
Drift Detection Protocols for Adaptive Learning
===============================================

Defines interfaces for detecting data drift, concept drift, and performance drift
in machine learning models. These protocols ensure clean separation of concerns
and dependency injection for drift detection services.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np


class DriftType(Enum):
    """Types of drift that can be detected"""

    DATA_DRIFT = "data_drift"  # Input distribution changes
    CONCEPT_DRIFT = "concept_drift"  # Target relationship changes
    PERFORMANCE_DRIFT = "performance_drift"  # Model performance degradation
    COVARIATE_SHIFT = "covariate_shift"  # Feature distribution changes
    LABEL_SHIFT = "label_shift"  # Target distribution changes


class DriftSeverity(Enum):
    """Severity levels of detected drift"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DriftDetectionMethod(Enum):
    """Methods for detecting drift"""

    STATISTICAL = "statistical"  # Statistical tests (KS, Chi-square, etc.)
    DISTANCE_BASED = "distance_based"  # Distance metrics (KL divergence, etc.)
    MODEL_BASED = "model_based"  # Model performance monitoring
    ENSEMBLE = "ensemble"  # Combination of multiple methods


@dataclass
class DriftAlert:
    """Drift alert data structure"""

    alert_id: str
    model_id: str
    drift_type: DriftType
    severity: DriftSeverity
    detection_method: DriftDetectionMethod
    confidence_score: float
    detected_at: datetime
    description: str
    affected_features: list[str]
    recommended_actions: list[str]
    resolved: bool = False
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass
class DriftAnalysis:
    """Comprehensive drift analysis results"""

    analysis_id: str
    model_id: str
    analysis_period: tuple[datetime, datetime]
    drift_alerts: list[DriftAlert]
    overall_drift_score: float
    feature_drift_scores: dict[str, float]
    performance_metrics: dict[str, float]
    recommendations: list[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DataDistribution:
    """Data distribution summary"""

    feature_name: str
    mean: float
    std: float
    min_value: float
    max_value: float
    percentiles: dict[str, float]  # 25th, 50th, 75th, etc.
    timestamp: datetime = field(default_factory=datetime.utcnow)
    histogram: dict[str, Any] | None = field(default_factory=dict)


class DriftDetectionProtocol(ABC):
    """
    Protocol for drift detection services.

    This interface defines the contract for detecting various types
    of drift in machine learning models and data.
    """

    @abstractmethod
    async def detect_drift(
        self,
        model_id: str,
        current_data: np.ndarray,
        reference_data: np.ndarray | None = None,
        feature_names: list[str] | None = None,
    ) -> list[DriftAlert]:
        """
        Detect drift in data

        Args:
            model_id: ID of the model
            current_data: Current data to analyze
            reference_data: Reference data for comparison
            feature_names: Names of features

        Returns:
            List of drift alerts
        """

    @abstractmethod
    async def analyze_drift_trends(
        self, model_id: str, time_window: tuple[datetime, datetime]
    ) -> DriftAnalysis:
        """
        Analyze drift trends over time

        Args:
            model_id: ID of the model
            time_window: Time window for analysis

        Returns:
            Comprehensive drift analysis
        """

    @abstractmethod
    async def get_drift_alerts(
        self, model_id: str | None = None, severity: DriftSeverity | None = None
    ) -> list[DriftAlert]:
        """
        Get drift alerts

        Args:
            model_id: Filter by model ID
            severity: Filter by severity level

        Returns:
            List of drift alerts
        """


class DriftAnalyzerProtocol(ABC):
    """
    Protocol for drift analysis services.

    This interface defines methods for analyzing drift patterns,
    calculating drift scores, and providing recommendations.
    """

    @abstractmethod
    async def calculate_drift_score(
        self,
        reference_distribution: DataDistribution,
        current_distribution: DataDistribution,
    ) -> float:
        """
        Calculate drift score between distributions

        Args:
            reference_distribution: Reference data distribution
            current_distribution: Current data distribution

        Returns:
            Drift score (0.0 = no drift, 1.0 = maximum drift)
        """

    @abstractmethod
    async def analyze_feature_drift(
        self,
        reference_data: np.ndarray,
        current_data: np.ndarray,
        feature_names: list[str],
    ) -> dict[str, float]:
        """
        Analyze drift for individual features

        Args:
            reference_data: Reference dataset
            current_data: Current dataset
            feature_names: Names of features

        Returns:
            Dictionary mapping feature names to drift scores
        """

    @abstractmethod
    async def generate_recommendations(self, drift_analysis: DriftAnalysis) -> list[str]:
        """
        Generate recommendations based on drift analysis

        Args:
            drift_analysis: Drift analysis results

        Returns:
            List of recommended actions
        """


class PerformanceDriftDetectorProtocol(ABC):
    """
    Protocol for performance-based drift detection.

    This interface defines methods for detecting drift through
    model performance monitoring.
    """

    @abstractmethod
    async def monitor_performance_drift(
        self,
        model_id: str,
        performance_metrics: dict[str, float],
        baseline_metrics: dict[str, float],
    ) -> DriftAlert | None:
        """
        Monitor for performance drift

        Args:
            model_id: ID of the model
            performance_metrics: Current performance metrics
            baseline_metrics: Baseline performance metrics

        Returns:
            Drift alert if performance drift detected, None otherwise
        """

    @abstractmethod
    async def set_performance_thresholds(self, model_id: str, thresholds: dict[str, float]) -> bool:
        """
        Set performance thresholds for drift detection

        Args:
            model_id: ID of the model
            thresholds: Performance thresholds

        Returns:
            True if thresholds were set successfully
        """


class StatisticalDriftDetectorProtocol(ABC):
    """
    Protocol for statistical drift detection.

    This interface defines methods for detecting drift using
    statistical tests and distance metrics.
    """

    @abstractmethod
    async def kolmogorov_smirnov_test(
        self,
        reference_data: np.ndarray,
        current_data: np.ndarray,
        significance_level: float = 0.05,
    ) -> tuple[float, float]:
        """
        Perform Kolmogorov-Smirnov test for drift detection

        Args:
            reference_data: Reference dataset
            current_data: Current dataset
            significance_level: Significance level for test

        Returns:
            Tuple of (test_statistic, p_value)
        """

    @abstractmethod
    async def jensen_shannon_divergence(
        self, reference_distribution: np.ndarray, current_distribution: np.ndarray
    ) -> float:
        """
        Calculate Jensen-Shannon divergence between distributions

        Args:
            reference_distribution: Reference distribution
            current_distribution: Current distribution

        Returns:
            Jensen-Shannon divergence value
        """

    @abstractmethod
    async def population_stability_index(
        self, reference_data: np.ndarray, current_data: np.ndarray, bins: int = 10
    ) -> float:
        """
        Calculate Population Stability Index (PSI)

        Args:
            reference_data: Reference dataset
            current_data: Current dataset
            bins: Number of bins for discretization

        Returns:
            PSI value
        """
