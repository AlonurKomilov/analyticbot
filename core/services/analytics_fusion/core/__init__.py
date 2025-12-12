"""
Analytics Core Microservice Package
===================================

Core analytics processing microservice with single responsibility.
Handles metrics calculation, engagement analysis, and performance scoring.
"""

from .analytics_core_service import AnalyticsCoreService
from .engines.analytics_engine import AnalyticsEngine
from .models.analytics_models import ChannelMetrics, EngagementData, PerformanceScore
from .processors.data_processor import DataProcessor
from .processors.metrics_processor import MetricsProcessor

__all__ = [
    # Main service
    "AnalyticsCoreService",
    # Processors
    "DataProcessor",
    "MetricsProcessor",
    # Engine
    "AnalyticsEngine",
    # Models
    "ChannelMetrics",
    "EngagementData",
    "PerformanceScore",
]

# Microservice metadata
__microservice__ = {
    "name": "analytics_core",
    "version": "1.0.0",
    "description": "Core analytics processing with single responsibility",
    "responsibility": "Analytics calculations and processing only",
    "components": [
        "AnalyticsCoreService",
        "DataProcessor",
        "MetricsProcessor",
        "AnalyticsEngine",
    ],
}
