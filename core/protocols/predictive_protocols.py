"""
Predictive Fusion Protocol Definitions

Defines the protocol interfaces for predictive intelligence services.
"""

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class ConfidenceLevel(Enum):
    """Confidence levels for predictions"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PredictionHorizon(Enum):
    """Prediction time horizons"""

    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 1-4 weeks
    LONG_TERM = "long_term"  # 1-6 months


@dataclass
class IntelligenceContext:
    """Context for intelligence analysis"""

    channel_id: int
    timeframe_start: datetime
    timeframe_end: datetime
    analysis_type: str
    parameters: dict[str, Any]
    confidence_threshold: float = 0.7


@dataclass
class ContextualIntelligence:
    """Contextual intelligence analysis result"""

    context_id: str
    channel_id: int
    analysis_type: str
    insights: list[str]
    recommendations: list[str]
    confidence: ConfidenceLevel
    metadata: dict[str, Any]
    timestamp: datetime


@dataclass
class TemporalIntelligence:
    """Temporal intelligence analysis result"""

    analysis_id: str
    channel_id: int
    time_patterns: dict[str, Any]
    trends: list[str]
    predictions: dict[str, Any]
    confidence: ConfidenceLevel
    horizon: PredictionHorizon
    timestamp: datetime


@dataclass
class PredictionNarrative:
    """Narrative description of predictions"""

    narrative_id: str
    title: str
    summary: str
    detailed_analysis: str
    key_insights: list[str]
    recommendations: list[str]
    confidence: ConfidenceLevel
    timestamp: datetime


@dataclass
class CrossChannelIntelligence:
    """Cross-channel intelligence analysis result"""

    analysis_id: str
    channel_ids: list[int]
    correlation_matrix: dict[str, dict[str, float]]
    influence_patterns: dict[str, Any]
    recommendations: list[str]
    confidence: ConfidenceLevel
    timestamp: datetime


@runtime_checkable
class ContextualAnalysisProtocol(Protocol):
    """Protocol for contextual analysis services"""

    @abstractmethod
    async def analyze_context(self, context: IntelligenceContext) -> ContextualIntelligence:
        """Analyze contextual intelligence"""
        ...

    @abstractmethod
    async def get_contextual_insights(self, channel_id: int, context_type: str) -> list[str]:
        """Get contextual insights for a channel"""
        ...


@runtime_checkable
class TemporalIntelligenceProtocol(Protocol):
    """Protocol for temporal intelligence services"""

    @abstractmethod
    async def analyze_temporal_patterns(
        self, channel_id: int, days: int = 30
    ) -> TemporalIntelligence:
        """Analyze temporal patterns"""
        ...

    @abstractmethod
    async def predict_performance(
        self, channel_id: int, horizon: PredictionHorizon
    ) -> dict[str, Any]:
        """Predict future performance"""
        ...


@runtime_checkable
class PredictiveModelingProtocol(Protocol):
    """Protocol for predictive modeling services"""

    @abstractmethod
    async def generate_predictions(self, channel_id: int, model_type: str) -> dict[str, Any]:
        """Generate predictions using specified model"""
        ...

    @abstractmethod
    async def create_prediction_narrative(self, channel_id: int) -> PredictionNarrative:
        """Create narrative description of predictions"""
        ...


@runtime_checkable
class CrossChannelAnalysisProtocol(Protocol):
    """Protocol for cross-channel analysis services"""

    @abstractmethod
    async def analyze_cross_channel_patterns(
        self, channel_ids: list[int]
    ) -> CrossChannelIntelligence:
        """Analyze patterns across multiple channels"""
        ...

    @abstractmethod
    async def detect_influence_patterns(self, channel_ids: list[int]) -> dict[str, Any]:
        """Detect influence patterns between channels"""
        ...


@runtime_checkable
class PredictiveOrchestratorProtocol(Protocol):
    """Protocol for predictive orchestrator services"""

    @abstractmethod
    async def orchestrate_intelligence_workflow(
        self, workflow_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Orchestrate intelligence analysis workflow"""
        ...

    @abstractmethod
    async def aggregate_intelligence(
        self, intelligence_results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Aggregate multiple intelligence results"""
        ...
