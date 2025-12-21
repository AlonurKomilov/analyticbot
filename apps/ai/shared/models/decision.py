"""Decision models for AI Worker system"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DecisionType(str, Enum):
    """Types of decisions the AI can make"""

    SCALE = "scale"  # Scale worker instances
    CONFIGURE = "configure"  # Modify configuration
    RESTART = "restart"  # Restart worker
    OPTIMIZE = "optimize"  # Optimize performance
    HEAL = "heal"  # Fix detected issue
    PREVENT = "prevent"  # Prevent predicted issue
    DISCOVER = "discover"  # Discover new service
    INTEGRATE = "integrate"  # Integrate new service


class ApprovalLevel(str, Enum):
    """Level of approval required for a decision"""

    AUTO = "auto"  # Execute immediately
    REVIEW = "review"  # Human review recommended
    APPROVAL = "approval"  # Human approval required
    FORBIDDEN = "forbidden"  # AI cannot make this change


@dataclass
class DecisionContext:
    """Context information for a decision"""

    # Triggering information
    trigger: str  # What triggered this decision
    trigger_data: dict[str, Any] = field(default_factory=dict)

    # System state
    worker_states: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    recent_errors: list[str] = field(default_factory=list)

    # Historical context
    similar_situations: list[dict] = field(default_factory=list)
    past_decisions: list[str] = field(default_factory=list)

    # Time context
    timestamp: datetime = field(default_factory=datetime.utcnow)
    time_constraints: dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """An AI-made decision"""

    # Identity
    decision_id: str
    decision_type: DecisionType
    target_worker: str

    # Decision details
    action: str  # Action to take
    action_params: dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""  # AI's reasoning

    # Approval
    approval_level: ApprovalLevel = ApprovalLevel.AUTO
    approved: bool = False
    approved_by: str | None = None
    approved_at: datetime | None = None

    # Context
    context: DecisionContext = field(default_factory=DecisionContext)

    # Risk assessment
    risk_level: str = "low"  # low, medium, high
    potential_impact: str = ""
    rollback_plan: str = ""

    # Execution
    executed: bool = False
    executed_at: datetime | None = None
    execution_result: str | None = None

    # Monitoring
    monitoring_duration_minutes: int = 30  # How long to monitor after execution
    success_criteria: dict[str, Any] = field(default_factory=dict)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    confidence_score: float = 0.0  # 0.0 to 1.0


@dataclass
class DecisionOutcome:
    """Outcome of an executed decision"""

    decision_id: str
    success: bool
    outcome_message: str = ""

    # Metrics before/after
    metrics_before: dict[str, float] = field(default_factory=dict)
    metrics_after: dict[str, float] = field(default_factory=dict)
    improvement_percent: float = 0.0

    # Issues detected
    issues_detected: list[str] = field(default_factory=list)
    rolled_back: bool = False
    rollback_reason: str = ""

    # Learning
    lessons_learned: list[str] = field(default_factory=list)
    should_repeat: bool = True  # Should we make similar decision in future?

    # Timestamps
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
