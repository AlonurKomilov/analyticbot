"""
Churn Intelligence Protocols
============================

Protocol interfaces for churn prediction and retention analytics microservices.

Defines contracts for:
- Churn prediction and risk assessment
- Retention strategy optimization
- Customer lifecycle analysis
- Behavioral churn detection
- Engagement recovery orchestration
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol


class ChurnRiskLevel(Enum):
    """Risk levels for churn prediction"""

    VERY_LOW = "very_low"  # < 10% probability
    LOW = "low"  # 10-25% probability
    MEDIUM = "medium"  # 25-50% probability
    HIGH = "high"  # 50-75% probability
    VERY_HIGH = "very_high"  # > 75% probability
    CRITICAL = "critical"  # Imminent churn


class ChurnStage(Enum):
    """Customer lifecycle stages related to churn"""

    ONBOARDING = "onboarding"
    ACTIVE = "active"
    DECLINING = "declining"
    AT_RISK = "at_risk"
    CHURNED = "churned"
    RECOVERED = "recovered"


class RetentionStrategy(Enum):
    """Retention intervention strategies"""

    ENGAGEMENT_BOOST = "engagement_boost"
    CONTENT_PERSONALIZATION = "content_personalization"
    INCENTIVE_OFFER = "incentive_offer"
    SUPPORT_OUTREACH = "support_outreach"
    FEATURE_EDUCATION = "feature_education"
    COMMUNITY_CONNECTION = "community_connection"
    NONE_REQUIRED = "none_required"


class ConfidenceLevel(Enum):
    """Confidence levels for predictions"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class ChurnRiskProfile:
    """Comprehensive churn risk assessment"""

    user_id: int = 0
    channel_id: int = 0
    risk_level: ChurnRiskLevel = ChurnRiskLevel.LOW
    churn_probability: float = 0.0
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    current_stage: ChurnStage = ChurnStage.ACTIVE

    # Risk factors
    engagement_score: float = 0.0
    activity_trend: str = "stable"
    last_active: datetime = field(default_factory=datetime.now)
    days_since_active: int = 0

    # Behavioral indicators
    session_frequency_decline: float = 0.0
    feature_usage_decline: float = 0.0
    interaction_quality_score: float = 0.0

    # Predictive factors
    risk_factors: list[str] = field(default_factory=list)
    protective_factors: list[str] = field(default_factory=list)
    trigger_events: list[dict[str, Any]] = field(default_factory=list)

    # Temporal context
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    prediction_horizon_days: int = 30


@dataclass
class RetentionRecommendation:
    """Retention strategy recommendations"""

    user_id: int = 0
    strategy: RetentionStrategy = RetentionStrategy.NONE_REQUIRED
    priority: str = "medium"
    intervention_timing: str = "immediate"

    # Strategy details
    recommended_actions: list[str] = field(default_factory=list)
    personalization_factors: dict[str, Any] = field(default_factory=dict)
    success_probability: float = 0.0

    # Implementation
    suggested_channels: list[str] = field(default_factory=list)
    resource_requirements: dict[str, Any] = field(default_factory=dict)
    expected_impact: str = ""

    # Tracking
    recommendation_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ChurnAnalytics:
    """Comprehensive churn analysis results"""

    analysis_id: str = ""
    channel_id: int = 0
    analysis_period: dict[str, datetime] = field(default_factory=dict)

    # Overall metrics
    total_users_analyzed: int = 0
    churn_rate: float = 0.0
    retention_rate: float = 0.0

    # Risk distribution
    risk_distribution: dict[ChurnRiskLevel, int] = field(default_factory=dict)
    stage_distribution: dict[ChurnStage, int] = field(default_factory=dict)

    # Insights
    primary_churn_drivers: list[str] = field(default_factory=list)
    retention_opportunities: list[str] = field(default_factory=list)
    trend_analysis: dict[str, Any] = field(default_factory=dict)

    # Predictions
    projected_churn_next_30days: int = 0
    recommended_interventions: int = 0

    timestamp: datetime = field(default_factory=datetime.now)


# Protocol Interfaces


class ChurnPredictionProtocol(Protocol):
    """Protocol for churn prediction services"""

    @abstractmethod
    async def predict_user_churn_risk(
        self, user_id: int, channel_id: int, analysis_days: int = 30
    ) -> ChurnRiskProfile:
        """Predict churn risk for a specific user"""
        ...

    @abstractmethod
    async def analyze_cohort_churn_risk(
        self,
        channel_id: int,
        user_ids: list[int] | None = None,
        risk_threshold: ChurnRiskLevel = ChurnRiskLevel.MEDIUM,
    ) -> list[ChurnRiskProfile]:
        """Analyze churn risk for a group of users"""
        ...

    @abstractmethod
    async def get_channel_churn_analytics(
        self, channel_id: int, analysis_days: int = 30
    ) -> ChurnAnalytics:
        """Get comprehensive churn analytics for a channel"""
        ...


class RetentionStrategyProtocol(Protocol):
    """Protocol for retention strategy services"""

    @abstractmethod
    async def generate_retention_strategy(
        self, risk_profile: ChurnRiskProfile
    ) -> RetentionRecommendation:
        """Generate personalized retention strategy"""
        ...

    @abstractmethod
    async def optimize_retention_campaigns(
        self, channel_id: int, target_risk_levels: list[ChurnRiskLevel]
    ) -> list[RetentionRecommendation]:
        """Optimize retention campaigns for risk segments"""
        ...

    @abstractmethod
    async def track_intervention_effectiveness(
        self, recommendation_id: str, outcome_metrics: dict[str, Any]
    ) -> dict[str, Any]:
        """Track effectiveness of retention interventions"""
        ...


class BehavioralAnalysisProtocol(Protocol):
    """Protocol for behavioral churn analysis"""

    @abstractmethod
    async def analyze_engagement_patterns(
        self, user_id: int, channel_id: int, lookback_days: int = 90
    ) -> dict[str, Any]:
        """Analyze user engagement patterns for churn signals"""
        ...

    @abstractmethod
    async def detect_churn_triggers(
        self, channel_id: int, analysis_period_days: int = 30
    ) -> list[dict[str, Any]]:
        """Detect common churn trigger events"""
        ...

    @abstractmethod
    async def calculate_engagement_scores(
        self, user_ids: list[int], channel_id: int
    ) -> dict[int, float]:
        """Calculate engagement scores for users"""
        ...


class ChurnOrchestratorProtocol(Protocol):
    """Protocol for churn intelligence orchestration"""

    @abstractmethod
    async def comprehensive_churn_analysis(
        self,
        channel_id: int,
        include_predictions: bool = True,
        include_strategies: bool = True,
    ) -> dict[str, Any]:
        """Perform comprehensive churn analysis and strategy generation"""
        ...

    @abstractmethod
    async def real_time_churn_monitoring(
        self, channel_id: int, alert_threshold: ChurnRiskLevel = ChurnRiskLevel.HIGH
    ) -> dict[str, Any]:
        """Real-time churn risk monitoring and alerting"""
        ...

    @abstractmethod
    async def batch_churn_assessment(
        self, channel_ids: list[int], priority_users_only: bool = False
    ) -> dict[int, ChurnAnalytics]:
        """Batch churn assessment across multiple channels"""
        ...

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check health of churn intelligence services"""
        ...


__all__ = [
    "ChurnRiskLevel",
    "ChurnStage",
    "RetentionStrategy",
    "ConfidenceLevel",
    "ChurnRiskProfile",
    "RetentionRecommendation",
    "ChurnAnalytics",
    "ChurnPredictionProtocol",
    "RetentionStrategyProtocol",
    "BehavioralAnalysisProtocol",
    "ChurnOrchestratorProtocol",
]
