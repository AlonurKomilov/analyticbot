"""
Unified Health Check Models

Consolidated health status models that replace duplicated definitions from:
- apps/shared/enhanced_health.py (ComponentHealth, SystemHealth, HealthStatus)
- core/common_helpers/health_check.py (HealthStatus, DependencyCheck)
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """
    Canonical health status levels - unified from 3 duplicate definitions
    
    HEALTHY: Component is fully operational
    DEGRADED: Component is operational but experiencing issues  
    UNHEALTHY: Component is not operational
    UNKNOWN: Component status cannot be determined
    """
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class DependencyType(str, Enum):
    """Types of service dependencies"""
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    QUEUE = "queue"
    STORAGE = "storage"
    SERVICE = "service"
    FILESYSTEM = "filesystem"
    NETWORK = "network"


@dataclass
class DependencyCheck:
    """Individual dependency health check result"""
    name: str
    type: DependencyType
    status: HealthStatus
    response_time_ms: float
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    last_checked: Optional[datetime] = None


@dataclass
class ComponentHealth:
    """
    Health information for a single component
    
    Unified model combining features from:
    - apps/shared/enhanced_health.py ComponentHealth
    - core/common_helpers/health_check.py DependencyCheck
    """
    name: str
    status: HealthStatus
    last_check: datetime
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    
    # Additional fields from core/common_helpers version
    dependency_type: Optional[DependencyType] = None
    critical: bool = True
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class SystemHealth:
    """
    Overall system health information
    
    Enhanced model with best features from all implementations
    """
    status: HealthStatus
    timestamp: datetime
    uptime_seconds: int
    version: str
    environment: str
    components: Dict[str, ComponentHealth]
    performance_metrics: Optional[Dict[str, Any]] = None
    alerts: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.alerts is None:
            self.alerts = []
    
    # Additional metadata
    service_name: str = "analyticbot"
    check_duration_ms: Optional[float] = None
    health_check_id: Optional[str] = None


@dataclass
class HealthCheckResult:
    """Complete health check result - for backward compatibility"""
    service_name: str
    overall_status: HealthStatus
    dependencies: List['DependencyCheck']
    response_time_ms: float
    timestamp: datetime
    version: str
    environment: str
    metadata: Optional[Dict[str, Any]] = None


# Health check thresholds configuration
class HealthThresholds:
    """Centralized health check threshold configuration"""
    
    def __init__(self):
        self.response_time_warning_ms = 1000
        self.response_time_critical_ms = 5000
        self.db_connection_timeout = 5.0
        self.redis_timeout = 2.0
        self.http_timeout = 10.0
        self.disk_usage_warning_percent = 80
        self.disk_usage_critical_percent = 90
        self.memory_usage_warning_percent = 85
        self.memory_usage_critical_percent = 95
        
    def is_response_time_degraded(self, response_time_ms: float) -> bool:
        """Check if response time indicates degraded performance"""
        return response_time_ms > self.response_time_warning_ms
        
    def is_response_time_unhealthy(self, response_time_ms: float) -> bool:
        """Check if response time indicates unhealthy status"""
        return response_time_ms > self.response_time_critical_ms
        
    def determine_status_from_response_time(self, response_time_ms: float, base_healthy: bool = True) -> HealthStatus:
        """Determine health status based on response time"""
        if not base_healthy:
            return HealthStatus.UNHEALTHY
            
        if self.is_response_time_unhealthy(response_time_ms):
            return HealthStatus.UNHEALTHY
        elif self.is_response_time_degraded(response_time_ms):
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


# Global thresholds instance
default_thresholds = HealthThresholds()