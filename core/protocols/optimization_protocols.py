"""
Optimization Fusion Protocol Definitions

Defines the protocol interfaces for optimization services.
"""

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class OptimizationType(Enum):
    """Types of optimization"""

    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    GROWTH = "growth"
    CONTENT = "content"
    TIMING = "timing"


class OptimizationPriority(Enum):
    """Priority levels for optimization recommendations"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceBaseline:
    """Baseline performance metrics"""

    channel_id: int
    baseline_date: datetime
    engagement_rate: float
    growth_rate: float
    content_quality: float
    posting_frequency: float
    metadata: dict[str, Any]


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""

    id: str
    channel_id: int
    optimization_type: OptimizationType
    priority: OptimizationPriority
    title: str
    description: str
    expected_impact: str
    implementation_effort: str
    success_metrics: list[str]
    confidence_score: float
    created_at: datetime


@runtime_checkable
class RecommendationEngineProtocol(Protocol):
    """Protocol for recommendation engine services"""

    @abstractmethod
    async def generate_recommendations(self, channel_id: int) -> list[OptimizationRecommendation]:
        """Generate optimization recommendations"""
        ...

    @abstractmethod
    async def evaluate_recommendation_impact(self, recommendation_id: str) -> dict[str, Any]:
        """Evaluate the impact of a recommendation"""
        ...


@runtime_checkable
class OptimizationOrchestratorProtocol(Protocol):
    """Protocol for optimization orchestrator services"""

    @abstractmethod
    async def orchestrate_optimization_cycle(self, cycle_config: dict[str, Any]) -> dict[str, Any]:
        """Orchestrate an optimization cycle"""
        ...

    @abstractmethod
    async def apply_recommendations(
        self, recommendations: list[OptimizationRecommendation]
    ) -> dict[str, Any]:
        """Apply optimization recommendations"""
        ...
