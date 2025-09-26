"""
Monitoring Application Service
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..domain.models import LogEntry, Metric, HealthCheck, LogLevel


class MonitoringService:
    """Monitoring application service"""
    
    def __init__(self):
        self._logs: List[LogEntry] = []
        self._metrics: List[Metric] = []
        self._health_checks: List[HealthCheck] = []
    
    async def log(self, level: LogLevel, message: str, module: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log a message"""
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            module=module,
            extra_data=extra_data
        )
        self._logs.append(log_entry)
        
        # Keep only last 1000 log entries
        if len(self._logs) > 1000:
            self._logs = self._logs[-1000:]
    
    async def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None, metric_type: str = "gauge"):
        """Record a metric"""
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags,
            metric_type=metric_type
        )
        self._metrics.append(metric)
        
        # Keep only last 5000 metrics
        if len(self._metrics) > 5000:
            self._metrics = self._metrics[-5000:]
    
    async def perform_health_check(self, component: str) -> HealthCheck:
        """Perform health check for component"""
        # Basic health check implementation
        health_check = HealthCheck(
            component=component,
            status="healthy",
            timestamp=datetime.now(),
            details={"checked_at": datetime.now().isoformat()}
        )
        
        self._health_checks.append(health_check)
        return health_check
    
    async def get_recent_logs(self, hours: int = 1, level: Optional[LogLevel] = None) -> List[LogEntry]:
        """Get recent log entries"""
        since = datetime.now() - timedelta(hours=hours)
        recent_logs = [log for log in self._logs if log.timestamp >= since]
        
        if level:
            recent_logs = [log for log in recent_logs if log.level == level]
        
        return recent_logs
    
    async def get_metrics(self, name_pattern: Optional[str] = None, hours: int = 1) -> List[Metric]:
        """Get metrics"""
        since = datetime.now() - timedelta(hours=hours)
        recent_metrics = [metric for metric in self._metrics if metric.timestamp >= since]
        
        if name_pattern:
            recent_metrics = [metric for metric in recent_metrics if name_pattern in metric.name]
        
        return recent_metrics
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        recent_health_checks = [hc for hc in self._health_checks 
                              if hc.timestamp >= datetime.now() - timedelta(minutes=5)]
        
        if not recent_health_checks:
            return {"status": "unknown", "details": "No recent health checks"}
        
        healthy_count = sum(1 for hc in recent_health_checks if hc.is_healthy())
        total_count = len(recent_health_checks)
        
        if healthy_count == total_count:
            status = "healthy"
        elif healthy_count > total_count // 2:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "healthy_components": healthy_count,
            "total_components": total_count,
            "timestamp": datetime.now().isoformat()
        }


# Global monitoring service instance
_monitoring_service: Optional[MonitoringService] = None

def get_monitoring_service() -> MonitoringService:
    """Get global monitoring service instance"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service
