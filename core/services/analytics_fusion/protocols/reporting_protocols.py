"""
Remaining Protocol Interfaces
============================

Placeholder protocol definitions for other analytics microservices.
"""

from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol


# Reporting Protocols
class ReportingProtocol(Protocol):
    @abstractmethod
    async def generate_performance_report(self, channel_id: int) -> dict[str, Any]: ...


class ReportGeneratorProtocol(Protocol):
    @abstractmethod
    async def generate_report(self, data: dict[str, Any]) -> dict[str, Any]: ...


class DashboardGeneratorProtocol(Protocol):
    @abstractmethod
    async def create_dashboard(self, metrics: dict[str, Any]) -> dict[str, Any]: ...


class ReportFormatterProtocol(Protocol):
    @abstractmethod
    async def format_report(self, report: dict[str, Any]) -> dict[str, Any]: ...


# Intelligence Protocols
class IntelligenceProtocol(Protocol):
    @abstractmethod
    async def generate_insights(self, channel_id: int) -> dict[str, Any]: ...


class TrendAnalyzerProtocol(Protocol):
    @abstractmethod
    async def analyze_trends(self, data: list[dict[str, Any]]) -> dict[str, Any]: ...


class PatternAnalyzerProtocol(Protocol):
    @abstractmethod
    async def analyze_patterns(self, data: dict[str, Any]) -> dict[str, Any]: ...


class InsightGeneratorProtocol(Protocol):
    @abstractmethod
    async def generate_insights(self, analysis: dict[str, Any]) -> list[str]: ...


# Monitoring Protocols
class MonitoringProtocol(Protocol):
    @abstractmethod
    async def track_real_time_metrics(self, channel_id: int) -> dict[str, Any]: ...


class MetricsCollectorProtocol(Protocol):
    @abstractmethod
    async def collect_metrics(self, source: str) -> dict[str, Any]: ...


class DataCollectorProtocol(Protocol):
    @abstractmethod
    async def collect_data(self, channel_id: int) -> dict[str, Any]: ...


class PerformanceTrackerProtocol(Protocol):
    @abstractmethod
    async def track_performance(self, metrics: dict[str, Any]) -> dict[str, Any]: ...


# Optimization Protocols
class OptimizationProtocol(Protocol):
    @abstractmethod
    async def optimize_content_strategy(self, channel_id: int) -> dict[str, Any]: ...


class PerformanceOptimizerProtocol(Protocol):
    @abstractmethod
    async def optimize_performance(self, metrics: dict[str, Any]) -> dict[str, Any]: ...


class ContentOptimizerProtocol(Protocol):
    @abstractmethod
    async def optimize_content(self, content: dict[str, Any]) -> dict[str, Any]: ...


class RecommendationEngineProtocol(Protocol):
    @abstractmethod
    async def generate_recommendations(self, analysis: dict[str, Any]) -> list[str]: ...


# Data classes for type hints
@dataclass
class ReportData:
    channel_id: int
    report_type: str
    data: dict[str, Any]


@dataclass
class DashboardConfig:
    dashboard_type: str
    layout: str
    widgets: list[str]


@dataclass
class InsightData:
    insight_type: str
    confidence: float
    description: str


@dataclass
class MonitoringAlert:
    alert_type: str
    severity: str
    message: str


@dataclass
class OptimizationResult:
    channel_id: int
    optimization_type: str
    recommendations: list[str]


# Enums
class ReportFormat(Enum):
    JSON = "json"
    PDF = "pdf"
    HTML = "html"


class ReportType(Enum):
    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    GROWTH = "growth"


class InsightType(Enum):
    TREND = "trend"
    PATTERN = "pattern"
    ANOMALY = "anomaly"


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
