"""
Optimization Microservice Package
=================================

Performance optimization microservice.
Single responsibility: Optimization only.
"""

from .optimization_service import OptimizationService

__all__ = ["OptimizationService"]

# Microservice metadata
__microservice__ = {
    "name": "optimization",
    "version": "1.0.0",
    "description": "Performance optimization",
    "responsibility": "Optimization recommendations only",
    "components": ["OptimizationService"],
}
