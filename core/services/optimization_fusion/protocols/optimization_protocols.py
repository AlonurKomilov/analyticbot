"""
Optimization Fusion Protocols
=============================

Protocol interfaces for optimization microservices dependency injection.

Defines contracts for:
- Performance analysis
- Recommendation engine
- Optimization application
- Impact validation
- Orchestration workflow
"""

from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol


class OptimizationPriority(Enum):
    """Priority levels for optimization recommendations"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OptimizationType(Enum):
    """Types of optimizations the engine can perform"""

    QUERY_OPTIMIZATION = "query_optimization"
    INDEX_SUGGESTION = "index_suggestion"
    CACHE_STRATEGY = "cache_strategy"
    RESOURCE_ALLOCATION = "resource_allocation"
    DATA_PARTITIONING = "data_partitioning"
    AGGREGATION_PRECOMPUTE = "aggregation_precompute"


@dataclass
class OptimizationRecommendation:
    """Structured optimization recommendation"""

    optimization_id: str
    optimization_type: OptimizationType
    priority: OptimizationPriority
    title: str
    description: str
    estimated_impact: dict[str, Any]
    implementation_steps: list[str]
    risks: list[str]
    auto_applicable: bool
    baseline_metric: str
    created_at: str


@dataclass
class PerformanceBaseline:
    """Performance baseline for comparison"""

    metric_name: str
    current_value: float
    historical_average: float
    trend: str
    threshold: float
    is_concerning: bool


class PerformanceAnalysisProtocol(Protocol):
    """Protocol for performance analysis microservice"""

    @abstractmethod
    async def analyze_system_performance(self) -> dict[str, PerformanceBaseline]:
        """Analyze current system performance across all metrics"""

    @abstractmethod
    async def collect_performance_metrics(self) -> dict[str, Any]:
        """Collect raw performance metrics"""

    @abstractmethod
    async def analyze_query_performance(self) -> dict[str, Any]:
        """Analyze query performance metrics"""

    @abstractmethod
    async def analyze_resource_utilization(self) -> dict[str, Any]:
        """Analyze CPU, memory, and resource usage"""

    @abstractmethod
    async def analyze_cache_performance(self) -> dict[str, Any]:
        """Analyze cache effectiveness and hit rates"""


class RecommendationEngineProtocol(Protocol):
    """Protocol for recommendation engine microservice"""

    @abstractmethod
    async def generate_optimization_recommendations(
        self, performance_baselines: dict[str, PerformanceBaseline]
    ) -> list[OptimizationRecommendation]:
        """Generate optimization recommendations based on performance analysis"""

    @abstractmethod
    async def generate_query_optimizations(
        self, baseline: PerformanceBaseline
    ) -> list[OptimizationRecommendation]:
        """Generate query-specific optimizations"""

    @abstractmethod
    async def generate_resource_optimizations(
        self, baseline: PerformanceBaseline
    ) -> list[OptimizationRecommendation]:
        """Generate resource utilization optimizations"""

    @abstractmethod
    async def generate_cache_optimizations(
        self, baseline: PerformanceBaseline
    ) -> list[OptimizationRecommendation]:
        """Generate cache strategy optimizations"""


class OptimizationApplicationProtocol(Protocol):
    """Protocol for optimization application microservice"""

    @abstractmethod
    async def auto_apply_safe_optimizations(
        self, recommendations: list[OptimizationRecommendation]
    ) -> dict[str, Any]:
        """Automatically apply safe optimizations"""

    @abstractmethod
    async def apply_optimization(
        self, recommendation: OptimizationRecommendation
    ) -> dict[str, Any]:
        """Apply a specific optimization"""

    @abstractmethod
    async def rollback_optimization(self, optimization_id: str) -> dict[str, Any]:
        """Rollback a previously applied optimization"""


class ValidationProtocol(Protocol):
    """Protocol for optimization validation microservice"""

    @abstractmethod
    async def validate_optimization_impact(self, optimization_id: str) -> dict[str, Any]:
        """Validate the impact of an applied optimization"""

    @abstractmethod
    async def setup_ab_test(self, optimization: OptimizationRecommendation) -> dict[str, Any]:
        """Setup A/B test for optimization validation"""

    @abstractmethod
    async def analyze_ab_test_results(self, test_id: str) -> dict[str, Any]:
        """Analyze A/B test results"""


class OptimizationOrchestratorProtocol(Protocol):
    """Protocol for optimization orchestrator microservice"""

    @abstractmethod
    async def orchestrate_full_optimization_cycle(
        self, auto_apply_safe: bool = True
    ) -> dict[str, Any]:
        """Orchestrate complete optimization workflow"""

    @abstractmethod
    async def orchestrate_performance_analysis(self) -> dict[str, Any]:
        """Orchestrate performance analysis workflow"""

    @abstractmethod
    async def orchestrate_recommendation_generation(
        self, performance_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Orchestrate recommendation generation workflow"""

    @abstractmethod
    async def orchestrate_optimization_application(
        self, recommendations: list[OptimizationRecommendation], auto_apply: bool = True
    ) -> dict[str, Any]:
        """Orchestrate optimization application workflow"""
