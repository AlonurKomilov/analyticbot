"""
Shared Protocols for God Object Dependencies
===========================================

Protocol interfaces to break cross-dependencies between god objects.
These protocols allow services to depend on interfaces rather than concrete implementations.

Usage:
- Import protocols instead of concrete god object classes
- Use dependency injection with protocol types
- Easy testing with mock implementations
- Clean separation of concerns
"""

from .optimization_adapter import OptimizationServiceAdapter, create_optimization_adapter
from .optimization_protocols import AlertsProtocol, OptimizationProtocol, PredictiveProtocol

__all__ = [
    "OptimizationProtocol",
    "PredictiveProtocol",
    "AlertsProtocol",
    "OptimizationServiceAdapter",
    "create_optimization_adapter",
]

# Metadata
__version__ = "1.0.0"
__purpose__ = "Break cross-god-object dependencies"
__pattern__ = "Protocol-based dependency injection"
