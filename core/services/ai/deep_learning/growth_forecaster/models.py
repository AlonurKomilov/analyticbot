"""
Growth Forecaster Models & Protocols
====================================

Shared data models and protocols for growth forecaster microservices.
Defines interfaces and data structures used across all services.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

import numpy as np
import pandas as pd


@dataclass
class PredictionRequest:
    """Request for growth prediction"""

    data: pd.DataFrame | list[dict] | dict
    forecast_periods: int = 30
    confidence_interval: float = 0.95
    include_uncertainty: bool = True
    cache_key: str | None = None


@dataclass
class PredictionResult:
    """Result of growth prediction"""

    predictions: np.ndarray
    confidence_lower: np.ndarray | None = None
    confidence_upper: np.ndarray | None = None
    uncertainty_score: float | None = None
    execution_time_ms: int = 0
    model_version: str = "unknown"
    cached: bool = False


@dataclass
class GrowthPattern:
    """Growth pattern analysis result"""

    pattern_type: str
    confidence: float
    characteristics: dict[str, Any]
    recommendations: list[str]


@dataclass
class ModelInfo:
    """Model information and metadata"""

    model_path: str
    version: str
    created_at: datetime
    metrics: dict[str, float]
    config: dict[str, Any]


class PredictionEngineProtocol(Protocol):
    """Protocol for prediction engine service"""

    async def predict_growth(self, request: PredictionRequest) -> PredictionResult:
        """Make growth prediction"""
        ...

    async def predict_batch(self, requests: list[PredictionRequest]) -> list[PredictionResult]:
        """Make batch predictions"""
        ...

    def predict_sync(self, request: PredictionRequest) -> PredictionResult:
        """Synchronous prediction"""
        ...


class DataAnalyzerProtocol(Protocol):
    """Protocol for data analysis service"""

    def analyze_patterns(self, data: pd.DataFrame) -> dict[str, Any]:
        """Analyze growth patterns in data"""
        ...

    def prepare_data(self, raw_data: pd.DataFrame | list[dict] | dict) -> pd.DataFrame:
        """Prepare and validate input data"""
        ...

    def classify_patterns(self, data: pd.DataFrame) -> GrowthPattern:
        """Classify growth patterns"""
        ...


class ModelManagerProtocol(Protocol):
    """Protocol for model management service"""

    async def load_model(self, model_path: str) -> bool:
        """Load a pretrained model"""
        ...

    async def save_model(self, model_path: str, include_processor: bool = True) -> bool:
        """Save current model"""
        ...

    def get_model_info(self) -> ModelInfo:
        """Get current model information"""
        ...


class CacheServiceProtocol(Protocol):
    """Protocol for caching service"""

    def get_cached_result(self, cache_key: str) -> PredictionResult | None:
        """Get cached prediction result"""
        ...

    def cache_result(self, cache_key: str, result: PredictionResult) -> None:
        """Cache prediction result"""
        ...

    def generate_key(self, request: PredictionRequest) -> str:
        """Generate cache key for request"""
        ...

    def clear_cache(self) -> None:
        """Clear all cached results"""
        ...


class TaskProcessorProtocol(Protocol):
    """Protocol for async task processing"""

    async def process_async_prediction(self, request: PredictionRequest) -> str:
        """Process prediction via async task queue"""
        ...


class ResultFormatterProtocol(Protocol):
    """Protocol for result formatting service"""

    def format_result(self, prediction: np.ndarray, metadata: dict[str, Any]) -> dict[str, Any]:
        """Format prediction result"""
        ...

    def create_features(self, prediction: np.ndarray) -> np.ndarray:
        """Create features from prediction"""
        ...


# Health check data structures
@dataclass
class HealthMetrics:
    """Health metrics for services"""

    total_predictions: int = 0
    successful_predictions: int = 0
    failed_predictions: int = 0
    average_response_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    last_prediction_time: datetime | None = None


@dataclass
class ServiceHealth:
    """Service health status"""

    service_name: str
    is_healthy: bool
    metrics: HealthMetrics
    error_message: str | None = None
    last_check: datetime = datetime.utcnow()


# Constants
DEFAULT_FORECAST_PERIODS = 30
DEFAULT_CONFIDENCE_INTERVAL = 0.95
MAX_CACHE_SIZE = 1000
DEFAULT_TIMEOUT_SECONDS = 300
