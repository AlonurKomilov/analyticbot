"""Optimization Protocol Interfaces"""

from .reporting_protocols import (
    ContentOptimizerProtocol,
    OptimizationProtocol,
    OptimizationResult,
    PerformanceOptimizerProtocol,
    RecommendationEngineProtocol,
)

# Additional optimization-specific types
RecommendationData = dict
OptimizationStrategy = dict
RecommendationType = str

__all__ = [
    "OptimizationProtocol",
    "PerformanceOptimizerProtocol",
    "ContentOptimizerProtocol",
    "RecommendationEngineProtocol",
    "OptimizationResult",
    "RecommendationData",
    "OptimizationStrategy",
    "RecommendationType",
]
