"""
Predictive Fusion Protocols
===========================

Protocol interfaces for predictive intelligence microservices dependency injection.

Defines contracts for:
- Contextual analysis
- Temporal intelligence
- Predictive modeling
- Cross-channel analysis
- Orchestration workflow
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol


class IntelligenceContext(Enum):
    """Context types for intelligence analysis"""

    TEMPORAL = "temporal"
    ENVIRONMENTAL = "environmental"
    COMPETITIVE = "competitive"
    BEHAVIORAL = "behavioral"
    SEASONAL = "seasonal"
    # Orchestration contexts
    COMPREHENSIVE = "comprehensive"
    PERFORMANCE_FOCUSED = "performance_focused"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    MARKET_INTELLIGENCE = "market_intelligence"


class ConfidenceLevel(Enum):
    """Confidence levels for intelligence predictions"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PredictionHorizon(Enum):
    """Time horizons for predictions"""

    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 1-4 weeks
    LONG_TERM = "long_term"  # 1-6 months


@dataclass
class ContextualIntelligence:
    """Intelligence layer context analysis results"""

    environmental_factors: dict[str, Any] = field(default_factory=dict)
    temporal_patterns: dict[str, Any] = field(default_factory=dict)
    competitive_landscape: dict[str, Any] = field(default_factory=dict)
    behavioral_insights: dict[str, Any] = field(default_factory=dict)
    context_confidence: float = 0.0
    analysis_timestamp: str = ""


@dataclass
class TemporalIntelligence:
    """Temporal pattern analysis results"""

    analysis_id: str = ""
    channel_id: int = 0
    time_patterns: dict[str, Any] = field(default_factory=dict)
    trends: list[dict[str, Any]] = field(default_factory=list)
    predictions: dict[str, Any] = field(default_factory=dict)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    horizon: PredictionHorizon = PredictionHorizon.MEDIUM_TERM
    timestamp: datetime = field(default_factory=datetime.now)
    # Legacy fields for backwards compatibility
    daily_patterns: dict[str, Any] = field(default_factory=dict)
    weekly_cycles: dict[str, Any] = field(default_factory=dict)
    seasonal_trends: dict[str, Any] = field(default_factory=dict)
    cyclical_patterns: dict[str, Any] = field(default_factory=dict)
    temporal_anomalies: list[dict[str, Any]] = field(default_factory=list)
    prediction_windows: dict[str, float] = field(default_factory=dict)


@dataclass
class PredictionNarrative:
    """Natural language prediction explanations"""

    summary: str = ""
    detailed_explanation: str = ""
    key_factors: list[str] = field(default_factory=list)
    confidence_explanation: str = ""
    recommendations: list[str] = field(default_factory=list)
    narrative_style: str = "conversational"


@dataclass
class CrossChannelIntelligence:
    """Cross-channel analysis results"""

    analysis_id: str = ""
    channel_ids: list[int] = field(default_factory=list)
    correlation_matrix: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    timestamp: datetime = field(default_factory=datetime.now)
    # Legacy fields for backwards compatibility
    channel_correlations: dict[str, float] = field(default_factory=dict)
    influence_patterns: dict[str, Any] = field(default_factory=dict)
    cross_promotion_opportunities: list[dict[str, Any]] = field(default_factory=list)
    synergy_scores: dict[str, float] = field(default_factory=dict)


class ContextualAnalysisProtocol(Protocol):
    """Protocol for contextual analysis microservice"""

    @abstractmethod
    async def analyze_context_factors(
        self, prediction_request: dict[str, Any], context_types: list[IntelligenceContext]
    ) -> ContextualIntelligence:
        """Analyze contextual factors for predictions"""
        pass

    @abstractmethod
    async def analyze_environmental_context(self, request: dict[str, Any]) -> dict[str, Any]:
        """Analyze environmental context factors"""
        pass

    @abstractmethod
    async def analyze_competitive_context(self, request: dict[str, Any]) -> dict[str, Any]:
        """Analyze competitive landscape context"""
        pass

    @abstractmethod
    async def analyze_behavioral_context(self, request: dict[str, Any]) -> dict[str, Any]:
        """Analyze behavioral pattern context"""
        pass


class TemporalIntelligenceProtocol(Protocol):
    """Protocol for temporal intelligence microservice"""

    @abstractmethod
    async def analyze_temporal_patterns(
        self, channel_id: int, depth_days: int = 90
    ) -> TemporalIntelligence:
        """Analyze temporal patterns and cycles"""
        pass

    @abstractmethod
    async def discover_daily_patterns(
        self, channel_id: int, base_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Discover daily intelligence patterns"""
        pass

    @abstractmethod
    async def discover_weekly_cycles(
        self, channel_id: int, base_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Discover weekly intelligence cycles"""
        pass

    @abstractmethod
    async def analyze_seasonal_intelligence(
        self, channel_id: int, base_data: dict[str, Any], depth_days: int
    ) -> dict[str, Any]:
        """Analyze seasonal intelligence patterns"""
        pass

    @abstractmethod
    async def detect_temporal_anomalies(self, base_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Detect temporal anomaly patterns"""
        pass


class PredictiveModelingProtocol(Protocol):
    """Protocol for predictive modeling microservice"""

    @abstractmethod
    async def generate_enhanced_predictions(
        self,
        prediction_request: dict[str, Any],
        contextual_intelligence: ContextualIntelligence,
        temporal_intelligence: TemporalIntelligence,
    ) -> dict[str, Any]:
        """Generate predictions enhanced with intelligence analysis"""
        pass

    @abstractmethod
    async def generate_prediction_narrative(
        self, predictions: dict[str, Any], intelligence_context: dict[str, Any]
    ) -> PredictionNarrative:
        """Generate natural language prediction explanations"""
        pass

    @abstractmethod
    async def calculate_prediction_confidence(
        self, predictions: dict[str, Any], context_factors: dict[str, Any]
    ) -> ConfidenceLevel:
        """Calculate prediction confidence based on context"""
        pass

    @abstractmethod
    async def validate_prediction_accuracy(
        self, prediction_id: str, actual_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate prediction accuracy against actual results"""
        pass


class CrossChannelAnalysisProtocol(Protocol):
    """Protocol for cross-channel analysis microservice"""

    @abstractmethod
    async def analyze_cross_channel_intelligence(
        self, channel_predictions: dict[str, Any]
    ) -> CrossChannelIntelligence:
        """Analyze cross-channel intelligence patterns"""
        pass

    @abstractmethod
    async def calculate_channel_correlations(
        self, channel_predictions: dict[str, Any]
    ) -> dict[str, dict[str, float]]:
        """Calculate correlations between channels - returns nested dict of correlations"""
        pass

    @abstractmethod
    async def analyze_influence_patterns(
        self, predictions: dict[str, Any], correlations: dict[str, dict[str, float]]
    ) -> dict[str, Any]:
        """Analyze influence patterns between channels"""
        pass

    @abstractmethod
    async def identify_cross_promotion_opportunities(
        self, predictions: dict[str, Any], correlations: dict[str, dict[str, float]]
    ) -> list[dict[str, Any]]:
        """Identify cross-promotion opportunities"""
        pass


class PredictiveOrchestratorProtocol(Protocol):
    """Protocol for predictive orchestrator microservice"""

    @abstractmethod
    async def orchestrate_enhanced_prediction(
        self,
        prediction_request: dict[str, Any],
        context_types: list[IntelligenceContext] | None = None,
        include_narrative: bool = True,
    ) -> dict[str, Any]:
        """Orchestrate enhanced prediction with full intelligence analysis"""
        pass

    @abstractmethod
    async def orchestrate_temporal_prediction(
        self, channel_id: int, prediction_horizon: PredictionHorizon, depth_days: int = 90
    ) -> dict[str, Any]:
        """Orchestrate temporal-focused prediction analysis"""
        pass

    @abstractmethod
    async def orchestrate_cross_channel_prediction(
        self, channel_ids: list[int], prediction_horizon: PredictionHorizon
    ) -> dict[str, Any]:
        """Orchestrate cross-channel prediction analysis"""
        pass

    @abstractmethod
    async def orchestrate_adaptive_learning(
        self, prediction_results: dict[str, Any], actual_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Orchestrate adaptive learning from prediction results"""
        pass
