"""
Analytics Fusion Protocol Interfaces
====================================

Service protocol interfaces for analytics fusion microservices.
These protocols define clean contracts for dependency injection and service interaction.

Protocols:
- AnalyticsCoreProtocol: Core analytics processing
- ReportingProtocol: Report generation and dashboards
- IntelligenceProtocol: AI insights and trend analysis
- MonitoringProtocol: Real-time monitoring and alerts
- OptimizationProtocol: Performance optimization
- OrchestratorProtocol: Service coordination

Key Benefits:
- Clean separation of concerns
- Dependency injection support
- Easy testing with mock implementations
- Clear service contracts
- Type safety and documentation
"""

from .analytics_protocols import (
    AnalyticsCoreProtocol,
    AnalyticsEngineProtocol,
    AnalyticsResult,
    DataProcessorProtocol,
    MetricsData,
    MetricsProcessorProtocol,
    ProcessingConfig,
)
from .intelligence_protocols import (
    InsightData,
    InsightGeneratorProtocol,
    InsightType,
    IntelligenceProtocol,
    PatternAnalyzerProtocol,
    PatternResult,
    TrendAnalysis,
    TrendAnalyzerProtocol,
)
from .monitoring_protocols import (
    AlertSeverity,
    CollectorConfig,
    DataCollectorProtocol,
    LiveMetrics,
    MetricsCollectorProtocol,
    MonitoringAlert,
    MonitoringProtocol,
    PerformanceTrackerProtocol,
)
from .optimization_protocols import (
    ContentOptimizerProtocol,
    OptimizationProtocol,
    OptimizationResult,
    OptimizationStrategy,
    PerformanceOptimizerProtocol,
    RecommendationData,
    RecommendationEngineProtocol,
    RecommendationType,
)
from .orchestrator_protocols import (
    CoordinationResult,
    HealthMonitorProtocol,
    OrchestrationRequest,
    OrchestratorProtocol,
    RequestRouterProtocol,
    RoutingRule,
    ServiceCoordinatorProtocol,
    ServiceHealth,
)
from .reporting_protocols import (
    DashboardConfig,
    DashboardGeneratorProtocol,
    ReportData,
    ReportFormat,
    ReportFormatterProtocol,
    ReportGeneratorProtocol,
    ReportingProtocol,
    ReportType,
)

__all__ = [
    # Core Analytics
    "AnalyticsCoreProtocol",
    "DataProcessorProtocol",
    "MetricsProcessorProtocol",
    "AnalyticsEngineProtocol",
    "AnalyticsResult",
    "MetricsData",
    "ProcessingConfig",
    # Reporting
    "ReportingProtocol",
    "ReportGeneratorProtocol",
    "DashboardGeneratorProtocol",
    "ReportFormatterProtocol",
    "ReportData",
    "DashboardConfig",
    "ReportFormat",
    "ReportType",
    # Intelligence
    "IntelligenceProtocol",
    "TrendAnalyzerProtocol",
    "PatternAnalyzerProtocol",
    "InsightGeneratorProtocol",
    "InsightData",
    "TrendAnalysis",
    "PatternResult",
    "InsightType",
    # Monitoring
    "MonitoringProtocol",
    "MetricsCollectorProtocol",
    "DataCollectorProtocol",
    "PerformanceTrackerProtocol",
    "MonitoringAlert",
    "LiveMetrics",
    "CollectorConfig",
    "AlertSeverity",
    # Optimization
    "OptimizationProtocol",
    "PerformanceOptimizerProtocol",
    "ContentOptimizerProtocol",
    "RecommendationEngineProtocol",
    "OptimizationResult",
    "RecommendationData",
    "OptimizationStrategy",
    "RecommendationType",
    # Orchestration
    "OrchestratorProtocol",
    "ServiceCoordinatorProtocol",
    "RequestRouterProtocol",
    "HealthMonitorProtocol",
    "OrchestrationRequest",
    "ServiceHealth",
    "RoutingRule",
    "CoordinationResult",
]

# Microservice metadata
__microservice__ = {
    "name": "analytics_fusion",
    "version": "1.0.0",
    "description": "Clean analytics microservices with single responsibilities",
    "protocols": [
        "AnalyticsCoreProtocol",
        "ReportingProtocol",
        "IntelligenceProtocol",
        "MonitoringProtocol",
        "OptimizationProtocol",
        "OrchestratorProtocol",
    ],
}
