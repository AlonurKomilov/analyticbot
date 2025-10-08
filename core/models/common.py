"""
Common models and base classes for the core domain
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class BaseEntity:
    """Base entity for all domain models"""

    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class TimestampedEntity(BaseEntity):
    """Entity with automatic timestamp management"""


# === ANALYTICS MODELS ===


@dataclass
class AnalyticsRequest:
    """Request model for analytics operations"""

    channel_id: str | None = None
    user_id: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    metrics: list[str] | None = None
    filters: dict[str, Any] | None = None

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = []
        if self.filters is None:
            self.filters = {}


@dataclass
class AnalyticsResult:
    """Result model for analytics operations"""

    data: dict[str, Any]
    metadata: dict[str, Any]
    timestamp: datetime
    processing_time_ms: float


# === PHASE 3 STEP 3: PREDICTIVE INTELLIGENCE MODELS ===


@dataclass
class IntelligenceRequest:
    """Request model for predictive intelligence operations"""

    channel_id: int
    analysis_type: str  # 'contextual', 'temporal', 'cross_channel', 'narrative'
    intelligence_context: list[str] | None = (
        None  # 'temporal', 'environmental', 'competitive', 'behavioral'
    )
    analysis_depth_days: int = 90
    prediction_horizon_days: int = 7
    narrative_style: str = "conversational"  # 'conversational', 'technical', 'executive'
    include_explanations: bool = True
    confidence_threshold: float = 0.7

    def __post_init__(self):
        if self.intelligence_context is None:
            self.intelligence_context = ["temporal", "environmental"]


@dataclass
class IntelligenceResult:
    """Result model for predictive intelligence operations"""

    base_prediction: dict[str, Any]
    contextual_intelligence: dict[str, Any]
    intelligence_insights: dict[str, Any]
    prediction_narrative: dict[str, str] | None = None
    enhanced_confidence: float = 0.0
    temporal_intelligence: dict[str, Any] | None = None
    cross_channel_intelligence: dict[str, Any] | None = None
    analysis_metadata: dict[str, Any] | None = None
    processing_time_ms: float = 0.0
    source: str = "analytics_fusion"

    def __post_init__(self):
        if self.analysis_metadata is None:
            self.analysis_metadata = {
                "intelligence_version": "phase_3_step_3_v1.0",
                "timestamp": datetime.now().isoformat(),
            }


@dataclass
class OptimizationMetrics:
    """Metrics for optimization tracking"""

    metric_name: str
    current_value: float
    baseline_value: float
    target_value: float
    improvement_percentage: float
    measurement_timestamp: datetime
    confidence_score: float = 0.0


@dataclass
class PerformanceInsight:
    """Performance insight for optimization recommendations"""

    insight_id: str
    title: str
    description: str
    severity: str  # critical, high, medium, low
    category: str  # performance, cost, reliability
    impact_score: float
    recommended_actions: list[str]
    technical_details: dict[str, Any]
    created_at: datetime

    def __post_init__(self):
        if self.recommended_actions is None:
            self.recommended_actions = []
        if self.technical_details is None:
            self.technical_details = {}


# Phase 3 Step 4: Advanced Analytics Orchestration Models


@dataclass
class WorkflowStep:
    """Individual step in an orchestration workflow"""

    step_id: str
    step_type: str  # WorkflowStepType enum value
    service_method: str
    parameters: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    timeout: int = 60
    can_run_parallel: bool = False
    continue_on_failure: bool = False
    retry_count: int = 0
    step_metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.step_metadata is None:
            self.step_metadata = {}


@dataclass
class OrchestrationWorkflow:
    """Complete workflow definition for orchestration"""

    workflow_id: str
    name: str
    description: str
    steps: list[WorkflowStep]
    parameters: dict[str, Any] = field(default_factory=dict)
    timeout: int = 300
    created_at: datetime | None = None
    updated_at: datetime | None = None
    workflow_metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.workflow_metadata is None:
            self.workflow_metadata = {
                "orchestration_version": "phase_3_step_4_v1.0",
                "creation_timestamp": datetime.now().isoformat(),
            }


@dataclass
class WorkflowContext:
    """Context maintained across workflow execution"""

    workflow_id: str
    execution_id: str
    current_step: str | None = None
    completed_steps: list[str] = field(default_factory=list)
    step_results: dict[str, Any] = field(default_factory=dict)
    execution_parameters: dict[str, Any] = field(default_factory=dict)
    business_context: dict[str, Any] | None = None
    temporal_context: dict[str, Any] | None = None

    def __post_init__(self):
        if self.business_context is None:
            self.business_context = {}
        if self.temporal_context is None:
            self.temporal_context = {
                "execution_start": datetime.now().isoformat(),
                "timezone": "UTC",
            }


@dataclass
class OrchestrationResult:
    """Comprehensive result from orchestration workflow"""

    execution_id: str
    workflow_id: str
    status: str
    consolidated_results: dict[str, Any]
    synthesis_result: dict[str, Any] = field(default_factory=dict)
    performance_metrics: dict[str, float] = field(default_factory=dict)
    execution_metadata: dict[str, Any] = field(default_factory=dict)
    orchestration_insights: dict[str, Any] | None = None
    quality_assessment: dict[str, Any] | None = None

    def __post_init__(self):
        if self.orchestration_insights is None:
            self.orchestration_insights = {
                "workflow_efficiency": 0.0,
                "cross_service_synergy": 0.0,
                "intelligence_coherence": 0.0,
            }
        if self.quality_assessment is None:
            self.quality_assessment = {
                "result_completeness": 0.0,
                "consistency_score": 0.0,
                "actionability_score": 0.0,
            }
