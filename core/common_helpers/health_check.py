"""
DEPRECATED: Enhanced Health Check System for AnalyticBot Services

⚠️  THIS FILE IS DEPRECATED ⚠️  
Use core.common.health instead for all health check functionality.

This file is kept for backward compatibility but will be removed in a future version.
Provides comprehensive health monitoring with dependency verification
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from core.common.health.models import HealthStatus, ComponentHealth

logger = logging.getLogger(__name__)

class DependencyType(str, Enum):
    """Types of service dependencies"""
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    QUEUE = "queue"
    STORAGE = "storage"
    SERVICE = "service"

@dataclass
class DependencyCheck:
    """Individual dependency health check result - DEPRECATED: Use ComponentHealth instead"""
    name: str
    type: DependencyType
    status: HealthStatus
    response_time_ms: float
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    last_checked: Optional[datetime] = None

    # Deprecated: use core.common.health.models.HealthStatus


class DependencyType(str, Enum):
    """Types of service dependencies"""
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    QUEUE = "queue"
    STORAGE = "storage"
    SERVICE = "service"


    # Deprecated: use core.common.health.models.ComponentHealth


@dataclass
class HealthCheckResult:
    """Complete health check result"""
    service_name: str
    overall_status: HealthStatus
    dependencies: List[DependencyCheck]
    response_time_ms: float
    timestamp: datetime
    version: str
    environment: str
    metadata: Optional[Dict[str, Any]] = None


class HealthChecker:
    """Enhanced health check coordinator"""
    
    def __init__(self, service_name: str, version: str = "1.0.0"):
        self.service_name = service_name
        self.version = version
        self.dependencies: Dict[str, callable] = {}
        self.thresholds = {
            "response_time_warning_ms": 1000,
            "response_time_critical_ms": 5000,
        }
    
    def register_dependency(
        self, 
        name: str, 
        check_func: callable, 
        dependency_type: DependencyType,
        critical: bool = True
    ):
        """Register a dependency check function"""
        self.dependencies[name] = {
            "func": check_func,
            "type": dependency_type,
            "critical": critical
        }
    
    async def check_dependency(self, name: str, config: dict) -> DependencyCheck:
        """Check individual dependency health"""
        start_time = time.time()
        
        try:
            result = await config["func"]()
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on result and response time
            if result.get("healthy", False):
                if response_time > self.thresholds["response_time_critical_ms"]:
                    status = HealthStatus.UNHEALTHY
                elif response_time > self.thresholds["response_time_warning_ms"]:
                    status = HealthStatus.DEGRADED
                else:
                    status = HealthStatus.HEALTHY
            else:
                status = HealthStatus.UNHEALTHY
            
            return DependencyCheck(
                name=name,
                type=config["type"],
                status=status,
                response_time_ms=response_time,
                details=result,
                last_checked=datetime.now()
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Health check failed for {name}: {e}")
            
            return DependencyCheck(
                name=name,
                type=config["type"],
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error=str(e),
                last_checked=datetime.now()
            )
    
    async def perform_health_check(self, environment: str = "unknown") -> HealthCheckResult:
        """Perform comprehensive health check"""
        start_time = time.time()
        
        # Check all dependencies
        dependency_checks = []
        for name, config in self.dependencies.items():
            check_result = await self.check_dependency(name, config)
            dependency_checks.append(check_result)
        
        # Determine overall health status
        overall_status = self._determine_overall_status(dependency_checks)
        
        total_response_time = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            service_name=self.service_name,
            overall_status=overall_status,
            dependencies=dependency_checks,
            response_time_ms=total_response_time,
            timestamp=datetime.now(),
            version=self.version,
            environment=environment
        )
    
    def _determine_overall_status(self, checks: List[DependencyCheck]) -> HealthStatus:
        """Determine overall health based on dependency checks"""
        if not checks:
            return HealthStatus.UNKNOWN
        
        critical_checks = [
            check for check in checks 
            if self.dependencies[check.name]["critical"]
        ]
        
        # If any critical dependency is unhealthy, overall is unhealthy
        for check in critical_checks:
            if check.status == HealthStatus.UNHEALTHY:
                return HealthStatus.UNHEALTHY
        
        # If any critical dependency is degraded, overall is degraded
        for check in critical_checks:
            if check.status == HealthStatus.DEGRADED:
                return HealthStatus.DEGRADED
        
        # Check non-critical dependencies
        unhealthy_count = sum(1 for check in checks if check.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for check in checks if check.status == HealthStatus.DEGRADED)
        
        if unhealthy_count > len(checks) * 0.5:  # More than 50% unhealthy
            return HealthStatus.DEGRADED
        elif unhealthy_count > 0 or degraded_count > 0:
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    def to_dict(self, result: HealthCheckResult) -> Dict[str, Any]:
        """Convert health check result to dictionary"""
        return {
            "service": result.service_name,
            "status": result.overall_status.value,
            "version": result.version,
            "environment": result.environment,
            "response_time_ms": round(result.response_time_ms, 2),
            "timestamp": result.timestamp.isoformat(),
            "dependencies": [
                {
                    "name": dep.name,
                    "type": dep.type.value,
                    "status": dep.status.value,
                    "response_time_ms": round(dep.response_time_ms, 2),
                    "error": dep.error,
                    "details": dep.details,
                    "last_checked": dep.last_checked.isoformat() if dep.last_checked else None
                }
                for dep in result.dependencies
            ],
            "metadata": result.metadata
        }


class StandardHealthChecks:
    """Collection of standard health check implementations"""
    
    @staticmethod
    async def database_health_check(db_manager) -> Dict[str, Any]:
        """Standard database health check"""
        try:
            health_data = await db_manager.health_check()
            return {
                "healthy": health_data.get("healthy", False),
                "pool_size": health_data.get("pool_size", 0),
                "idle_connections": health_data.get("idle_connections", 0),
                "used_connections": health_data.get("used_connections", 0),
                "avg_query_time": health_data.get("avg_query_time", 0),
                "total_queries": health_data.get("total_queries", 0)
            }
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    @staticmethod
    async def redis_health_check(redis_client) -> Dict[str, Any]:
        """Standard Redis health check"""
        try:
            await redis_client.ping()
            info = await redis_client.info()
            return {
                "healthy": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "redis_version": info.get("redis_version", "unknown")
            }
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    @staticmethod
    async def external_api_health_check(url: str, timeout: int = 5) -> Dict[str, Any]:
        """Standard external API health check"""
        import aiohttp
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get(url) as response:
                    return {
                        "healthy": response.status < 400,
                        "status_code": response.status,
                        "content_length": response.headers.get("content-length", "unknown")
                    }
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    @staticmethod 
    async def telegram_api_health_check(bot_token: str) -> Dict[str, Any]:
        """Telegram Bot API health check"""
        import aiohttp
        try:
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "healthy": data.get("ok", False),
                            "bot_username": data.get("result", {}).get("username", "unknown")
                        }
                    else:
                        return {"healthy": False, "status_code": response.status}
        except Exception as e:
            return {"healthy": False, "error": str(e)}