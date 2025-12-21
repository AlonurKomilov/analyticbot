"""Worker data models for AI Worker system"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class WorkerType(str, Enum):
    """Types of workers that can be managed"""

    MTPROTO = "mtproto"
    BOT = "bot"
    CELERY = "celery"
    API = "api"
    ML = "ml"
    ANALYTICS = "analytics"
    CUSTOM = "custom"


class WorkerStatus(str, Enum):
    """Worker operational status"""

    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ResourceRequirements:
    """Resource requirements for a worker"""

    cpu_cores: float = 1.0
    memory_mb: int = 512
    max_cpu_percent: float = 80.0
    max_memory_mb: int = 2048
    disk_gb: int | None = None
    network_mbps: int | None = None


@dataclass
class WorkerConfig:
    """Configuration for a worker"""

    # Runtime configuration
    interval_minutes: int | None = None
    batch_size: int | None = None
    max_runtime_hours: float | None = None
    health_check_port: int | None = None

    # Resource limits
    memory_limit_mb: int | None = None
    cpu_limit_percent: float | None = None

    # Auto-scaling
    auto_scaling_enabled: bool = False
    min_instances: int = 1
    max_instances: int = 1
    scale_up_threshold: float = 80.0  # CPU %
    scale_down_threshold: float = 30.0  # CPU %

    # Custom settings
    custom_settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkerDefinition:
    """Complete definition of a manageable worker"""

    # Identity
    name: str
    worker_type: WorkerType
    module_path: str
    description: str = ""

    # Configuration
    config: WorkerConfig = field(default_factory=WorkerConfig)
    resource_requirements: ResourceRequirements = field(default_factory=ResourceRequirements)

    # Monitoring endpoints
    health_endpoint: str | None = None
    metrics_endpoint: str | None = None
    log_file: str | None = None

    # AI Control
    ai_manageable: bool = True  # Can AI modify this worker?
    auto_restart_on_failure: bool = True
    requires_approval_for: list[str] = field(default_factory=list)  # Actions requiring approval

    # Metadata
    version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    # Timestamps
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkerState:
    """Current state of a worker"""

    # Identity
    worker_name: str
    worker_type: WorkerType

    # Status
    status: WorkerStatus
    status_message: str = ""
    last_status_check: datetime = field(default_factory=datetime.utcnow)

    # Process info
    pid: int | None = None
    started_at: datetime | None = None
    uptime_seconds: float = 0.0

    # Resource usage
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_percent: float = 0.0

    # Health
    is_healthy: bool = True
    health_checks_passed: int = 0
    health_checks_failed: int = 0
    last_error: str | None = None
    last_error_at: datetime | None = None

    # Performance
    requests_processed: int = 0
    errors_count: int = 0
    avg_response_time_ms: float = 0.0

    # AI management
    managed_by_ai: bool = False
    last_ai_action: str | None = None
    last_ai_action_at: datetime | None = None

    # Custom metrics
    custom_metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkerInstance:
    """A running instance of a worker (for multi-instance workers)"""

    instance_id: str
    worker_name: str
    state: WorkerState
    started_at: datetime = field(default_factory=datetime.utcnow)
    config_overrides: dict[str, Any] = field(default_factory=dict)
