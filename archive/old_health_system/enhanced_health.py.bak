"""
Enhanced Health Check System for AnalyticBot
Provides comprehensive health monitoring with dependency verification,
performance metrics, and intelligent failure detection.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import json
import os

import asyncpg
import httpx
from pydantic import BaseModel

try:
    import redis.asyncio as redis
except Exception:
    redis = None


class HealthStatus(str, Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentHealth(BaseModel):
    """Health information for a single component"""
    name: str
    status: HealthStatus
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    details: Dict[str, Any] = {}
    last_check: datetime
    dependencies: List[str] = []


class SystemHealth(BaseModel):
    """Overall system health information"""
    status: HealthStatus
    timestamp: datetime
    uptime_seconds: int
    version: str
    environment: str
    components: Dict[str, ComponentHealth]
    performance_metrics: Dict[str, Any] = {}
    alerts: List[str] = []


class EnhancedHealthChecker:
    """Enhanced health checking with dependency verification and performance monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.now()
        self.health_history: List[SystemHealth] = []
        self.max_history_size = 100
        
        # Configurable thresholds
        self.thresholds = {
            "response_time_warning_ms": 1000,
            "response_time_critical_ms": 5000,
            "db_connection_timeout": 5.0,
            "redis_timeout": 2.0,
            "http_timeout": 10.0,
        }
    
    async def get_comprehensive_health(self) -> SystemHealth:
        """Get comprehensive system health with all components"""
        components = {}
        alerts = []
        
        # Check all components in parallel for better performance
        component_checks = [
            ("database", self._check_database_health()),
            ("redis", self._check_redis_health()),
            ("api_internal", self._check_api_health()),
            ("mtproto", self._check_mtproto_health()),
            ("frontend", self._check_frontend_health()),
            ("disk_space", self._check_disk_space()),
            ("memory", self._check_memory_usage()),
        ]
        
        start_time = time.time()
        results = await asyncio.gather(
            *[check for _, check in component_checks],
            return_exceptions=True
        )
        total_check_time = (time.time() - start_time) * 1000
        
        # Process results
        for (name, _), result in zip(component_checks, results):
            if isinstance(result, Exception):
                components[name] = ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    error=str(result),
                    last_check=datetime.now()
                )
                alerts.append(f"{name} health check failed: {str(result)}")
            else:
                components[name] = result
                
                # Add alerts based on component status
                if result.status == HealthStatus.UNHEALTHY:
                    alerts.append(f"{name} is unhealthy: {result.error}")
                elif result.status == HealthStatus.DEGRADED:
                    alerts.append(f"{name} is degraded: {result.error}")
                    
                # Performance alerts
                if result.response_time_ms and result.response_time_ms > self.thresholds["response_time_critical_ms"]:
                    alerts.append(f"{name} response time critical: {result.response_time_ms:.2f}ms")
                elif result.response_time_ms and result.response_time_ms > self.thresholds["response_time_warning_ms"]:
                    alerts.append(f"{name} response time high: {result.response_time_ms:.2f}ms")
        
        # Determine overall system status
        overall_status = self._calculate_overall_status(components)
        
        # Performance metrics
        performance_metrics = {
            "health_check_duration_ms": total_check_time,
            "components_checked": len(components),
            "uptime_seconds": int((datetime.now() - self.start_time).total_seconds()),
            "avg_response_time_ms": self._calculate_avg_response_time(components),
        }
        
        system_health = SystemHealth(
            status=overall_status,
            timestamp=datetime.now(),
            uptime_seconds=int((datetime.now() - self.start_time).total_seconds()),
            version=os.getenv("APP_VERSION", "2.1.0"),
            environment=os.getenv("ENVIRONMENT", "development"),
            components=components,
            performance_metrics=performance_metrics,
            alerts=alerts
        )
        
        # Store in history
        self._store_health_history(system_health)
        
        return system_health
    
    async def _check_database_health(self) -> ComponentHealth:
        """Enhanced database health check with performance monitoring"""
        start_time = time.time()
        
        try:
            dsn = os.getenv("DATABASE_URL")
            if not dsn:
                return ComponentHealth(
                    name="database",
                    status=HealthStatus.UNKNOWN,
                    error="DATABASE_URL not configured",
                    last_check=datetime.now()
                )
            
            # Test connection and basic query
            conn = await asyncpg.connect(dsn, timeout=self.thresholds["db_connection_timeout"])
            
            # Perform health checks
            await conn.execute("SELECT 1")  # Basic connectivity
            pool_stats = await conn.fetchrow("SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active'")
            db_size = await conn.fetchrow("SELECT pg_size_pretty(pg_database_size(current_database())) as size")
            
            await conn.close()
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on response time
            if response_time > self.thresholds["response_time_critical_ms"]:
                status = HealthStatus.UNHEALTHY
                error = f"Response time too high: {response_time:.2f}ms"
            elif response_time > self.thresholds["response_time_warning_ms"]:
                status = HealthStatus.DEGRADED
                error = f"Response time elevated: {response_time:.2f}ms"
            else:
                status = HealthStatus.HEALTHY
                error = None
            
            return ComponentHealth(
                name="database",
                status=status,
                response_time_ms=response_time,
                error=error,
                details={
                    "active_connections": pool_stats["active_connections"] if pool_stats else 0,
                    "database_size": db_size["size"] if db_size else "unknown",
                    "connection_timeout": self.thresholds["db_connection_timeout"],
                },
                last_check=datetime.now(),
                dependencies=[]
            )
            
        except asyncio.TimeoutError:
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                error="Connection timeout",
                last_check=datetime.now()
            )
        except Exception as e:
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
                last_check=datetime.now()
            )
    
    async def _check_redis_health(self) -> ComponentHealth:
        """Enhanced Redis health check"""
        start_time = time.time()
        
        try:
            if not redis:
                return ComponentHealth(
                    name="redis",
                    status=HealthStatus.UNKNOWN,
                    error="Redis client not available",
                    last_check=datetime.now()
                )
            
            redis_url = os.getenv("REDIS_URL")
            if not redis_url:
                return ComponentHealth(
                    name="redis",
                    status=HealthStatus.UNKNOWN,
                    error="REDIS_URL not configured",
                    last_check=datetime.now()
                )
            
            # Test Redis connection
            r = redis.from_url(redis_url, socket_timeout=self.thresholds["redis_timeout"])
            
            # Perform health checks
            await r.ping()
            info = await r.info()
            await r.close()
            
            response_time = (time.time() - start_time) * 1000
            
            # Check memory usage
            used_memory = info.get("used_memory", 0)
            max_memory = info.get("maxmemory", 0)
            memory_usage_pct = (used_memory / max_memory * 100) if max_memory > 0 else 0
            
            # Determine status
            if response_time > self.thresholds["response_time_critical_ms"]:
                status = HealthStatus.UNHEALTHY
                error = f"Response time too high: {response_time:.2f}ms"
            elif memory_usage_pct > 90:
                status = HealthStatus.DEGRADED
                error = f"High memory usage: {memory_usage_pct:.1f}%"
            elif response_time > self.thresholds["response_time_warning_ms"]:
                status = HealthStatus.DEGRADED
                error = f"Response time elevated: {response_time:.2f}ms"
            else:
                status = HealthStatus.HEALTHY
                error = None
            
            return ComponentHealth(
                name="redis",
                status=status,
                response_time_ms=response_time,
                error=error,
                details={
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "unknown"),
                    "memory_usage_pct": f"{memory_usage_pct:.1f}%",
                    "redis_version": info.get("redis_version", "unknown"),
                },
                last_check=datetime.now(),
                dependencies=[]
            )
            
        except Exception as e:
            return ComponentHealth(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
                last_check=datetime.now()
            )
    
    async def _check_api_health(self) -> ComponentHealth:
        """Check API internal health"""
        start_time = time.time()
        
        try:
            # Try to connect to the API internally
            api_url = os.getenv("API_INTERNAL_URL", "http://localhost:10400")
            
            async with httpx.AsyncClient(timeout=self.thresholds["http_timeout"]) as client:
                response = await client.get(f"{api_url}/health")
                response.raise_for_status()
                
                response_time = (time.time() - start_time) * 1000
                
                # Parse response
                health_data = response.json()
                
                status = HealthStatus.HEALTHY if health_data.get("status") == "ok" else HealthStatus.DEGRADED
                
                return ComponentHealth(
                    name="api_internal",
                    status=status,
                    response_time_ms=response_time,
                    details={
                        "api_version": health_data.get("version", "unknown"),
                        "environment": health_data.get("environment", "unknown"),
                        "response_status": response.status_code,
                    },
                    last_check=datetime.now(),
                    dependencies=["database"]
                )
                
        except Exception as e:
            return ComponentHealth(
                name="api_internal",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
                last_check=datetime.now(),
                dependencies=["database"]
            )
    
    async def _check_mtproto_health(self) -> ComponentHealth:
        """Check MTProto service health"""
        start_time = time.time()
        
        try:
            mtproto_url = os.getenv("MTPROTO_URL", "http://localhost:8091")
            
            async with httpx.AsyncClient(timeout=self.thresholds["http_timeout"]) as client:
                response = await client.get(f"{mtproto_url}/health")
                response.raise_for_status()
                
                response_time = (time.time() - start_time) * 1000
                health_data = response.json()
                
                # Check if MTProto is enabled and healthy
                mtproto_enabled = health_data.get("mtproto_enabled", False)
                status_str = health_data.get("status", "unknown")
                
                if status_str == "healthy":
                    status = HealthStatus.HEALTHY
                elif status_str == "degraded":
                    status = HealthStatus.DEGRADED
                else:
                    status = HealthStatus.UNHEALTHY
                
                return ComponentHealth(
                    name="mtproto",
                    status=status,
                    response_time_ms=response_time,
                    details={
                        "mtproto_enabled": mtproto_enabled,
                        "uptime_seconds": health_data.get("uptime_seconds", 0),
                        "version": health_data.get("version", "unknown"),
                        "components": health_data.get("components", {}),
                    },
                    last_check=datetime.now(),
                    dependencies=[]
                )
                
        except Exception as e:
            return ComponentHealth(
                name="mtproto",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
                last_check=datetime.now()
            )
    
    async def _check_frontend_health(self) -> ComponentHealth:
        """Check frontend service health"""
        start_time = time.time()
        
        try:
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:10300")
            
            async with httpx.AsyncClient(timeout=self.thresholds["http_timeout"]) as client:
                response = await client.get(frontend_url)
                response.raise_for_status()
                
                response_time = (time.time() - start_time) * 1000
                
                return ComponentHealth(
                    name="frontend",
                    status=HealthStatus.HEALTHY,
                    response_time_ms=response_time,
                    details={
                        "response_status": response.status_code,
                        "content_length": len(response.content),
                    },
                    last_check=datetime.now(),
                    dependencies=["api_internal"]
                )
                
        except Exception as e:
            return ComponentHealth(
                name="frontend",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
                last_check=datetime.now(),
                dependencies=["api_internal"]
            )
    
    async def _check_disk_space(self) -> ComponentHealth:
        """Check disk space usage"""
        start_time = time.time()
        
        try:
            import shutil
            
            # Check disk usage for current directory
            total, used, free = shutil.disk_usage(".")
            usage_pct = (used / total) * 100
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on disk usage
            if usage_pct > 90:
                status = HealthStatus.UNHEALTHY
                error = f"Critical disk usage: {usage_pct:.1f}%"
            elif usage_pct > 80:
                status = HealthStatus.DEGRADED
                error = f"High disk usage: {usage_pct:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                error = None
            
            return ComponentHealth(
                name="disk_space",
                status=status,
                response_time_ms=response_time,
                error=error,
                details={
                    "total_gb": f"{total / (1024**3):.2f}",
                    "used_gb": f"{used / (1024**3):.2f}",
                    "free_gb": f"{free / (1024**3):.2f}",
                    "usage_pct": f"{usage_pct:.1f}%",
                },
                last_check=datetime.now()
            )
            
        except Exception as e:
            return ComponentHealth(
                name="disk_space",
                status=HealthStatus.UNKNOWN,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
                last_check=datetime.now()
            )
    
    async def _check_memory_usage(self) -> ComponentHealth:
        """Check memory usage"""
        start_time = time.time()
        
        try:
            import psutil
            
            # Get memory information
            memory = psutil.virtual_memory()
            usage_pct = memory.percent
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on memory usage
            if usage_pct > 90:
                status = HealthStatus.UNHEALTHY
                error = f"Critical memory usage: {usage_pct:.1f}%"
            elif usage_pct > 80:
                status = HealthStatus.DEGRADED
                error = f"High memory usage: {usage_pct:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                error = None
            
            return ComponentHealth(
                name="memory",
                status=status,
                response_time_ms=response_time,
                error=error,
                details={
                    "total_gb": f"{memory.total / (1024**3):.2f}",
                    "available_gb": f"{memory.available / (1024**3):.2f}",
                    "used_gb": f"{memory.used / (1024**3):.2f}",
                    "usage_pct": f"{usage_pct:.1f}%",
                },
                last_check=datetime.now()
            )
            
        except ImportError:
            return ComponentHealth(
                name="memory",
                status=HealthStatus.UNKNOWN,
                error="psutil not available",
                last_check=datetime.now()
            )
        except Exception as e:
            return ComponentHealth(
                name="memory",
                status=HealthStatus.UNKNOWN,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
                last_check=datetime.now()
            )
    
    def _calculate_overall_status(self, components: Dict[str, ComponentHealth]) -> HealthStatus:
        """Calculate overall system status based on component health"""
        if not components:
            return HealthStatus.UNKNOWN
        
        # Count status types
        healthy = sum(1 for c in components.values() if c.status == HealthStatus.HEALTHY)
        degraded = sum(1 for c in components.values() if c.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for c in components.values() if c.status == HealthStatus.UNHEALTHY)
        
        total = len(components)
        
        # Critical components that must be healthy
        critical_components = ["database", "api_internal"]
        critical_unhealthy = any(
            components.get(name, ComponentHealth(name=name, status=HealthStatus.UNKNOWN, last_check=datetime.now())).status == HealthStatus.UNHEALTHY
            for name in critical_components
        )
        
        if critical_unhealthy or unhealthy > total // 2:
            return HealthStatus.UNHEALTHY
        elif degraded > 0 or unhealthy > 0:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def _calculate_avg_response_time(self, components: Dict[str, ComponentHealth]) -> float:
        """Calculate average response time across components"""
        response_times = [
            c.response_time_ms for c in components.values() 
            if c.response_time_ms is not None
        ]
        
        if not response_times:
            return 0.0
        
        return sum(response_times) / len(response_times)
    
    def _store_health_history(self, health: SystemHealth) -> None:
        """Store health check in history for trend analysis"""
        self.health_history.append(health)
        
        # Keep only recent history
        if len(self.health_history) > self.max_history_size:
            self.health_history = self.health_history[-self.max_history_size:]
    
    async def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trends over specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_health = [
            h for h in self.health_history 
            if h.timestamp >= cutoff_time
        ]
        
        if not recent_health:
            return {"error": "No health data available for specified time period"}
        
        # Calculate trends
        status_counts = {}
        component_trends = {}
        avg_response_times = []
        
        for health in recent_health:
            # Overall status trends
            status = health.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Component trends
            for name, component in health.components.items():
                if name not in component_trends:
                    component_trends[name] = {
                        HealthStatus.HEALTHY.value: 0,
                        HealthStatus.DEGRADED.value: 0,
                        HealthStatus.UNHEALTHY.value: 0,
                        HealthStatus.UNKNOWN.value: 0,
                    }
                component_trends[name][component.status.value] += 1
            
            # Response time trends
            if health.performance_metrics.get("avg_response_time_ms"):
                avg_response_times.append(health.performance_metrics["avg_response_time_ms"])
        
        return {
            "time_period_hours": hours,
            "total_checks": len(recent_health),
            "overall_status_distribution": status_counts,
            "component_trends": component_trends,
            "avg_response_time_trend": {
                "current": avg_response_times[-1] if avg_response_times else 0,
                "min": min(avg_response_times) if avg_response_times else 0,
                "max": max(avg_response_times) if avg_response_times else 0,
                "avg": sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0,
            }
        }


# Global health checker instance
health_checker = EnhancedHealthChecker()