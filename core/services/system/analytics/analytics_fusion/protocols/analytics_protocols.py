"""
Analytics Core Protocol Interfaces
==================================

Protocol definitions for core analytics processing microservice.
"""

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


@dataclass
class MetricsData:
    """Analytics metrics data structure"""

    channel_id: int
    timestamp: datetime
    engagement_metrics: dict[str, float]
    performance_metrics: dict[str, float]
    content_metrics: dict[str, Any]
    metadata: dict[str, Any]


@dataclass
class AnalyticsResult:
    """Analytics processing result"""

    channel_id: int
    analysis_type: str
    results: dict[str, Any]
    confidence_score: float
    timestamp: datetime
    processing_time_ms: int


@dataclass
class ProcessingConfig:
    """Analytics processing configuration"""

    include_engagement: bool = True
    include_performance: bool = True
    include_content: bool = True
    time_range_days: int = 30
    min_data_points: int = 10
    confidence_threshold: float = 0.8


class AnalyticsCoreProtocol(Protocol):
    """Protocol for core analytics processing service"""

    @abstractmethod
    async def process_channel_metrics(
        self, channel_id: int, config: ProcessingConfig | None = None
    ) -> AnalyticsResult:
        """Process comprehensive metrics for a channel"""
        ...

    @abstractmethod
    async def calculate_performance_scores(self, metrics: MetricsData) -> dict[str, float]:
        """Calculate normalized performance scores"""
        ...

    @abstractmethod
    async def analyze_engagement_patterns(
        self, channel_id: int, time_range_days: int = 30
    ) -> dict[str, Any]:
        """Analyze engagement patterns and trends"""
        ...

    @abstractmethod
    async def validate_analytics_data(self, data: MetricsData) -> bool:
        """Validate analytics data quality"""
        ...

    @abstractmethod
    async def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""
        ...


class DataProcessorProtocol(Protocol):
    """Protocol for data processing components"""

    @abstractmethod
    async def process_raw_data(self, raw_data: dict[str, Any]) -> MetricsData:
        """Process raw data into structured metrics"""
        ...

    @abstractmethod
    async def normalize_metrics(self, metrics: dict[str, float]) -> dict[str, float]:
        """Normalize metrics to standard scales"""
        ...

    @abstractmethod
    async def validate_data_quality(self, data: Any) -> bool:
        """Validate data quality and completeness"""
        ...


class MetricsProcessorProtocol(Protocol):
    """Protocol for metrics processing components"""

    @abstractmethod
    async def calculate_engagement_metrics(self, channel_data: dict[str, Any]) -> dict[str, float]:
        """Calculate engagement metrics"""
        ...

    @abstractmethod
    async def calculate_performance_metrics(self, channel_data: dict[str, Any]) -> dict[str, float]:
        """Calculate performance metrics"""
        ...

    @abstractmethod
    async def aggregate_metrics(self, metrics_list: list[dict[str, float]]) -> dict[str, float]:
        """Aggregate multiple metric sets"""
        ...


class AnalyticsEngineProtocol(Protocol):
    """Protocol for analytics engine components"""

    @abstractmethod
    async def run_analytics_pipeline(
        self, channel_id: int, config: ProcessingConfig
    ) -> AnalyticsResult:
        """Run complete analytics pipeline"""
        ...

    @abstractmethod
    async def analyze_channel_performance(self, channel_id: int) -> dict[str, Any]:
        """Analyze overall channel performance"""
        ...

    @abstractmethod
    async def compare_channel_metrics(self, channel_ids: list[int]) -> dict[str, Any]:
        """Compare metrics across multiple channels"""
        ...
