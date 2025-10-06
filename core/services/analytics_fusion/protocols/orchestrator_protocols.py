"""
Orchestrator Protocol Interfaces
================================

Protocol definitions for orchestrator service coordination.
"""

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Protocol


class ServiceType(Enum):
    """Types of analytics services"""

    CORE = "core"
    REPORTING = "reporting"
    INTELLIGENCE = "intelligence"
    MONITORING = "monitoring"
    OPTIMIZATION = "optimization"


class RequestType(Enum):
    """Types of orchestration requests"""

    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"
    PERFORMANCE_REPORT = "performance_report"
    INSIGHTS_GENERATION = "insights_generation"
    REAL_TIME_MONITORING = "real_time_monitoring"
    OPTIMIZATION_ANALYSIS = "optimization_analysis"


@dataclass
class OrchestrationRequest:
    """Request for orchestrated analytics processing"""

    request_id: str
    request_type: RequestType
    channel_id: int
    parameters: dict[str, Any]
    priority: int = 1
    timeout_seconds: int = 300
    requested_at: datetime | None = None


@dataclass
class ServiceHealth:
    """Service health status"""

    service_name: str
    service_type: ServiceType
    is_healthy: bool
    response_time_ms: int | None
    last_check: datetime
    error_message: str | None = None
    metrics: dict[str, Any] | None = None


@dataclass
class RoutingRule:
    """Request routing configuration"""

    request_type: RequestType
    target_services: list[ServiceType]
    execution_order: list[ServiceType]
    parallel_execution: bool = False
    timeout_seconds: int = 300


@dataclass
class CoordinationResult:
    """Result of orchestrated processing"""

    request_id: str
    request_type: RequestType
    success: bool
    results: dict[str, Any]
    execution_time_ms: int
    services_used: list[str]
    errors: list[str] | None = None


class OrchestratorProtocol(Protocol):
    """Protocol for analytics orchestrator service"""

    @abstractmethod
    async def coordinate_comprehensive_analysis(
        self, channel_id: int, parameters: dict[str, Any] | None = None
    ) -> CoordinationResult:
        """Coordinate comprehensive analytics analysis"""
        ...

    @abstractmethod
    async def route_analytics_request(self, request: OrchestrationRequest) -> CoordinationResult:
        """Route request to appropriate services"""
        ...

    @abstractmethod
    async def get_service_health(self) -> dict[str, ServiceHealth]:
        """Get health status of all services"""
        ...

    @abstractmethod
    async def start_services(self) -> bool:
        """Start and register all analytics services"""
        ...

    @abstractmethod
    async def stop_services(self) -> bool:
        """Stop all analytics services"""
        ...


class ServiceCoordinatorProtocol(Protocol):
    """Protocol for service coordination components"""

    @abstractmethod
    async def register_service(self, service_name: str, service_instance: Any) -> bool:
        """Register a service instance"""
        ...

    @abstractmethod
    async def unregister_service(self, service_name: str) -> bool:
        """Unregister a service instance"""
        ...

    @abstractmethod
    async def execute_service_call(
        self, service_name: str, method_name: str, parameters: dict[str, Any]
    ) -> Any:
        """Execute a call to a registered service"""
        ...


class RequestRouterProtocol(Protocol):
    """Protocol for request routing components"""

    @abstractmethod
    async def route_request(
        self, request: OrchestrationRequest, routing_rules: list[RoutingRule]
    ) -> CoordinationResult:
        """Route request based on routing rules"""
        ...

    @abstractmethod
    async def execute_parallel_requests(self, service_calls: list[dict[str, Any]]) -> list[Any]:
        """Execute multiple service calls in parallel"""
        ...

    @abstractmethod
    async def execute_sequential_requests(self, service_calls: list[dict[str, Any]]) -> list[Any]:
        """Execute multiple service calls sequentially"""
        ...


class HealthMonitorProtocol(Protocol):
    """Protocol for service health monitoring components"""

    @abstractmethod
    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """Check health of a specific service"""
        ...

    @abstractmethod
    async def check_all_services_health(self) -> dict[str, ServiceHealth]:
        """Check health of all registered services"""
        ...

    @abstractmethod
    async def monitor_service_performance(self, service_name: str) -> dict[str, Any]:
        """Monitor service performance metrics"""
        ...
