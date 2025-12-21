"""Action models for AI Worker system"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ActionType(str, Enum):
    """Types of actions that can be executed"""

    # Configuration actions
    UPDATE_CONFIG = "update_config"
    SET_INTERVAL = "set_interval"
    SET_RESOURCE_LIMIT = "set_resource_limit"

    # Control actions
    START_WORKER = "start_worker"
    STOP_WORKER = "stop_worker"
    RESTART_WORKER = "restart_worker"
    PAUSE_WORKER = "pause_worker"
    RESUME_WORKER = "resume_worker"

    # Scaling actions
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    AUTO_SCALE = "auto_scale"

    # Monitoring actions
    CHECK_HEALTH = "check_health"
    GET_METRICS = "get_metrics"
    ANALYZE_LOGS = "analyze_logs"

    # Maintenance actions
    CLEAR_CACHE = "clear_cache"
    ROTATE_LOGS = "rotate_logs"
    CLEANUP_RESOURCES = "cleanup_resources"

    # Integration actions
    REGISTER_WORKER = "register_worker"
    DISCOVER_SERVICES = "discover_services"

    # User AI actions
    ANALYZE_CHANNEL = "analyze_channel"
    GENERATE_CONTENT = "generate_content"
    ANALYZE_AUDIENCE = "analyze_audience"
    EXECUTE_SERVICE = "execute_service"


class ActionStatus(str, Enum):
    """Status of an action"""

    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


@dataclass
class Action:
    """An executable action"""

    # Identity
    action_id: str
    action_type: ActionType
    target_worker: str

    # Parameters
    parameters: dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 60

    # Execution context
    triggered_by: str = "ai_worker"  # 'ai_worker', 'user', 'system'
    related_decision_id: str | None = None

    # Safety
    dry_run: bool = False  # Simulate without executing
    requires_confirmation: bool = False
    confirmed: bool = False

    # Status
    status: ActionStatus = ActionStatus.PENDING
    status_message: str = ""

    # Execution
    started_at: datetime | None = None
    completed_at: datetime | None = None
    execution_time_seconds: float = 0.0

    # Result
    result_data: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    error_traceback: str | None = None

    # Rollback
    rollback_action: dict[str, Any] | None = None  # How to undo this action
    can_rollback: bool = True

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    priority: int = 5  # 1-10, higher = more urgent


@dataclass
class ActionResult:
    """Result of an executed action"""

    action_id: str
    success: bool
    message: str = ""

    # Output data
    output: dict[str, Any] = field(default_factory=dict)

    # Performance
    execution_time_seconds: float = 0.0
    resources_used: dict[str, Any] = field(default_factory=dict)

    # Side effects
    side_effects: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Rollback info
    rollback_available: bool = False
    rollback_instructions: str = ""

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)
