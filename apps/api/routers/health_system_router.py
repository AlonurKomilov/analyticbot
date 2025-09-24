"""
Health System Router - Comprehensive Health Monitoring
=====================================================

Provides centralized health monitoring endpoints for the entire system.
Consolidates health checks from all services and components.

UPDATED: Renamed from enhanced_health.py for clarity
PHASE 3B: Will consolidate health endpoints from all other routers
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from core.common.health.checker import health_checker
from core.common.health.models import HealthStatus, SystemHealth

# Global health checker instance now imported from unified system

class HealthResponse(BaseModel):
    """Standard health response format"""
    status: str
    timestamp: str
    service: str
    version: str

class DetailedHealthResponse(BaseModel):
    """Detailed health response with components"""
    status: str
    timestamp: str
    uptime_seconds: int
    version: str
    environment: str
    components: Dict[str, Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    alerts: list[str]

class ReadinessResponse(BaseModel):
    """Readiness probe response"""
    ready: bool
    timestamp: str
    components: Dict[str, str]
    dependencies_met: bool


class LivenessResponse(BaseModel):
    """Liveness probe response"""
    alive: bool
    timestamp: str
    uptime_seconds: int


router = APIRouter(prefix="/health", tags=["Health Monitoring"])


@router.get("/", response_model=HealthResponse, summary="Basic Health Check")
async def basic_health_check():
    """
    ## Basic Health Check
    
    Simple health check endpoint for load balancers and basic monitoring.
    Returns basic service status without detailed component checks.
    
    **Use Cases:**
    - Load balancer health checks
    - Basic monitoring systems
    - Quick status verification
    
    **Response:**
    - `status`: "healthy", "degraded", or "unhealthy"
    - `timestamp`: ISO timestamp of check
    - `service`: Service identifier
    - `version`: Application version
    """
    system_health = await health_checker.get_system_health()
    
    return HealthResponse(
        status=system_health.status.value,
        timestamp=system_health.timestamp.isoformat(),
        service=system_health.service_name,
        version=system_health.version
    )


@router.get("/detailed", response_model=DetailedHealthResponse, summary="Detailed Health Check")
async def detailed_health_check():
    """
    ## Detailed Health Check
    
    Comprehensive health check with component-level details, performance metrics,
    and system alerts. Provides deep visibility into system state.
    
    **Features:**
    - Component-level health status
    - Response time monitoring
    - Performance metrics
    - System alerts and warnings
    - Dependency verification
    
    **Components Monitored:**
    - Database connectivity and performance
    - Redis cache status
    - Internal API health
    - MTProto service status
    - Frontend availability
    - System resources (disk, memory)
    
    **Use Cases:**
    - Operations monitoring
    - Debugging system issues
    - Performance analysis
    - Capacity planning
    """
    system_health = await health_checker.get_system_health()
    
    # Convert components to serializable format
    components_dict = {}
    for name, component in system_health.components.items():
        components_dict[name] = {
            "status": component.status.value,
            "response_time_ms": component.response_time_ms,
            "error": component.error,
            "details": component.details,
            "last_check": component.last_check.isoformat(),
            "dependencies": component.dependencies,
        }
    
    return DetailedHealthResponse(
        status=system_health.status.value,
        timestamp=system_health.timestamp.isoformat(),
        uptime_seconds=system_health.uptime_seconds,
        version=system_health.version,
        environment=system_health.environment,
        components=components_dict,
        performance_metrics=system_health.performance_metrics,
        alerts=system_health.alerts
    )


@router.get("/ready", response_model=ReadinessResponse, summary="Readiness Probe")
async def readiness_check():
    """
    ## Readiness Probe
    
    Kubernetes-style readiness probe to determine if the service is ready 
    to accept traffic. Checks critical dependencies and initialization status.
    
    **Readiness Criteria:**
    - Database connectivity established
    - Critical services initialized
    - All dependencies available
    - No critical component failures
    
    **Use Cases:**
    - Kubernetes readiness probes
    - Load balancer backend registration
    - Deployment health gates
    - Traffic routing decisions
    
    **Response:**
    - `ready`: true if service can accept traffic
    - `components`: Status of critical components
    - `dependencies_met`: Whether all dependencies are satisfied
    """
    system_health = await health_checker.get_comprehensive_health()
    
    # Define critical components for readiness
    critical_components = ["database", "api_internal"]
    
    # Check if critical components are healthy
    ready = True
    components_status = {}
    
    for component_name in critical_components:
        if component_name in system_health.components:
            component = system_health.components[component_name]
            components_status[component_name] = component.status.value
            
            if component.status in [HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN]:
                ready = False
        else:
            components_status[component_name] = "missing"
            ready = False
    
    # Add non-critical components status
    for name, component in system_health.components.items():
        if name not in critical_components:
            components_status[name] = component.status.value
    
    # Dependencies are met if all critical components are healthy
    dependencies_met = all(
        components_status.get(name) == "healthy" 
        for name in critical_components
    )
    
    return ReadinessResponse(
        ready=ready,
        timestamp=datetime.now().isoformat(),
        components=components_status,
        dependencies_met=dependencies_met
    )


@router.get("/live", response_model=LivenessResponse, summary="Liveness Probe")
async def liveness_check():
    """
    ## Liveness Probe
    
    Kubernetes-style liveness probe to determine if the service is alive 
    and should be restarted if not responding. Minimal check for basic process health.
    
    **Liveness Criteria:**
    - Process is running and responsive
    - Basic service functionality available
    - No deadlocks or hanging states
    
    **Use Cases:**
    - Kubernetes liveness probes
    - Process monitoring
    - Automatic restart triggers
    - Basic availability monitoring
    
    **Response:**
    - `alive`: true if process is healthy
    - `uptime_seconds`: Process uptime
    """
    system_health = await health_checker.get_comprehensive_health()
    
    return LivenessResponse(
        alive=True,  # If we can respond, we're alive
        timestamp=datetime.now().isoformat(),
        uptime_seconds=system_health.uptime_seconds
    )


@router.get("/trends", summary="Health Trends Analysis")
async def health_trends(
    hours: int = Query(default=24, ge=1, le=168, description="Hours of history to analyze")
):
    """
    ## Health Trends Analysis
    
    Analyze health trends over time to identify patterns, degradation,
    and performance trends.
    
    **Features:**
    - Status distribution over time
    - Component reliability trends
    - Performance trend analysis
    - Failure pattern identification
    
    **Parameters:**
    - `hours`: Number of hours of history to analyze (1-168)
    
    **Use Cases:**
    - Performance trend analysis
    - Reliability monitoring
    - Capacity planning
    - Root cause analysis
    """
    try:
        trends = await health_checker.get_health_trends(hours=hours)
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "analysis_period_hours": hours,
            "trends": trends
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate health trends: {str(e)}"
        )


@router.get("/metrics", summary="Performance Metrics")
async def performance_metrics():
    """
    ## Performance Metrics
    
    Current performance metrics and system statistics for monitoring
    and alerting systems.
    
    **Metrics Included:**
    - Response times by component
    - System resource utilization
    - Error rates and availability
    - Performance thresholds status
    
    **Use Cases:**
    - Monitoring system integration
    - Performance dashboards
    - Alerting rule configuration
    - SLA monitoring
    """
    system_health = await health_checker.get_comprehensive_health()
    
    # Extract performance metrics
    metrics = {
        "timestamp": system_health.timestamp.isoformat(),
        "uptime_seconds": system_health.uptime_seconds,
        "overall_status": system_health.status.value,
        "performance": system_health.performance_metrics,
        "component_response_times": {},
        "system_health_score": 0,
        "alerts_count": len(system_health.alerts),
    }
    
    # Component response times
    for name, component in system_health.components.items():
        if component.response_time_ms is not None:
            metrics["component_response_times"][name] = component.response_time_ms
    
    # Calculate health score (0-100)
    healthy_count = sum(
        1 for c in system_health.components.values() 
        if c.status == HealthStatus.HEALTHY
    )
    total_count = len(system_health.components)
    
    if total_count > 0:
        metrics["system_health_score"] = int((healthy_count / total_count) * 100)
    
    return metrics


@router.get("/debug", summary="Debug Information")
async def debug_info():
    """
    ## Debug Information
    
    Detailed debug information for troubleshooting system issues.
    Includes component details, error information, and diagnostic data.
    
    **⚠️ Warning:** This endpoint may expose sensitive diagnostic information.
    Use with caution in production environments.
    
    **Use Cases:**
    - Development debugging
    - Operations troubleshooting
    - Performance analysis
    - System diagnostics
    """
    system_health = await health_checker.get_comprehensive_health()
    
    debug_data = {
        "timestamp": datetime.now().isoformat(),
        "system_health": {
            "status": system_health.status.value,
            "uptime_seconds": system_health.uptime_seconds,
            "version": system_health.version,
            "environment": system_health.environment,
        },
        "components": {},
        "alerts": system_health.alerts,
        "performance_metrics": system_health.performance_metrics,
        "thresholds": health_checker.thresholds,
        "history_size": len(health_checker.health_history),
    }
    
    # Detailed component information
    for name, component in system_health.components.items():
        debug_data["components"][name] = {
            "status": component.status.value,
            "response_time_ms": component.response_time_ms,
            "error": component.error,
            "details": component.details,
            "last_check": component.last_check.isoformat(),
            "dependencies": component.dependencies,
        }
    
    return debug_data