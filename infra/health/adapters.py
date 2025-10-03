"""
🏥 Health Check Infrastructure Adapters

Framework-specific implementations for health monitoring ports.
Contains all the infrastructure dependencies that were previously
in the core domain.
"""

import logging
import time
from datetime import datetime

from core.ports.health_ports import (
    CacheHealthPort,
    ComponentHealth,
    DatabaseHealthPort,
    ExternalServiceHealthPort,
    HealthStatus,
    SystemResourcesPort,
)

logger = logging.getLogger(__name__)


class PostgreSQLHealthAdapter(DatabaseHealthPort):
    """PostgreSQL health check adapter"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    async def check_connection(self) -> ComponentHealth:
        """Check PostgreSQL connection health"""
        start_time = time.time()

        try:
            import asyncpg

            conn = await asyncpg.connect(self.connection_string, timeout=5.0)
            await conn.execute("SELECT 1")
            await conn.close()

            response_time = (time.time() - start_time) * 1000

            return ComponentHealth(
                name="database_connection",
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                response_time_ms=response_time,
                last_checked=datetime.utcnow(),
            )

        except ImportError:
            return ComponentHealth(
                name="database_connection",
                status=HealthStatus.UNKNOWN,
                message="asyncpg not available",
                error="Missing asyncpg dependency",
                last_checked=datetime.utcnow(),
            )
        except Exception as e:
            return ComponentHealth(
                name="database_connection",
                status=HealthStatus.UNHEALTHY,
                message="Database connection failed",
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.utcnow(),
            )

    async def check_query_performance(self) -> ComponentHealth:
        """Check database query performance"""
        start_time = time.time()

        try:
            import asyncpg

            conn = await asyncpg.connect(self.connection_string, timeout=5.0)

            # Simple performance test
            await conn.execute("SELECT COUNT(*) FROM pg_stat_activity")

            await conn.close()

            response_time = (time.time() - start_time) * 1000

            status = HealthStatus.HEALTHY
            message = "Database query performance good"

            if response_time > 1000:  # > 1 second
                status = HealthStatus.DEGRADED
                message = f"Database query slow: {response_time:.0f}ms"
            elif response_time > 5000:  # > 5 seconds
                status = HealthStatus.UNHEALTHY
                message = f"Database query very slow: {response_time:.0f}ms"

            return ComponentHealth(
                name="database_performance",
                status=status,
                message=message,
                response_time_ms=response_time,
                last_checked=datetime.utcnow(),
            )

        except ImportError:
            return ComponentHealth(
                name="database_performance",
                status=HealthStatus.UNKNOWN,
                message="asyncpg not available",
                error="Missing asyncpg dependency",
                last_checked=datetime.utcnow(),
            )
        except Exception as e:
            return ComponentHealth(
                name="database_performance",
                status=HealthStatus.UNHEALTHY,
                message="Database performance check failed",
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.utcnow(),
            )


class RedisHealthAdapter(CacheHealthPort):
    """Redis health check adapter"""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url

    async def check_connection(self) -> ComponentHealth:
        """Check Redis connection health"""
        start_time = time.time()

        try:
            import redis.asyncio as redis

            client = redis.from_url(self.redis_url)
            await client.ping()
            await client.close()

            response_time = (time.time() - start_time) * 1000

            return ComponentHealth(
                name="cache_connection",
                status=HealthStatus.HEALTHY,
                message="Redis connection successful",
                response_time_ms=response_time,
                last_checked=datetime.utcnow(),
            )

        except ImportError:
            return ComponentHealth(
                name="cache_connection",
                status=HealthStatus.UNKNOWN,
                message="redis not available",
                error="Missing redis dependency",
                last_checked=datetime.utcnow(),
            )
        except Exception as e:
            return ComponentHealth(
                name="cache_connection",
                status=HealthStatus.UNHEALTHY,
                message="Redis connection failed",
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.utcnow(),
            )

    async def check_memory_usage(self) -> ComponentHealth:
        """Check Redis memory usage"""
        start_time = time.time()

        try:
            import redis.asyncio as redis

            client = redis.from_url(self.redis_url)
            info = await client.info("memory")
            await client.close()

            used_memory = info.get("used_memory", 0)
            max_memory = info.get("maxmemory", 0)

            response_time = (time.time() - start_time) * 1000

            if max_memory == 0:
                # No memory limit set
                status = HealthStatus.HEALTHY
                message = f"Redis memory usage: {used_memory / 1024 / 1024:.1f}MB (no limit)"
            else:
                memory_usage_percent = (used_memory / max_memory) * 100

                if memory_usage_percent < 80:
                    status = HealthStatus.HEALTHY
                    message = f"Redis memory usage: {memory_usage_percent:.1f}%"
                elif memory_usage_percent < 90:
                    status = HealthStatus.DEGRADED
                    message = f"Redis memory usage high: {memory_usage_percent:.1f}%"
                else:
                    status = HealthStatus.UNHEALTHY
                    message = f"Redis memory usage critical: {memory_usage_percent:.1f}%"

            return ComponentHealth(
                name="cache_memory",
                status=status,
                message=message,
                response_time_ms=response_time,
                details={"used_memory_mb": used_memory / 1024 / 1024},
                last_checked=datetime.utcnow(),
            )

        except ImportError:
            return ComponentHealth(
                name="cache_memory",
                status=HealthStatus.UNKNOWN,
                message="redis not available",
                error="Missing redis dependency",
                last_checked=datetime.utcnow(),
            )
        except Exception as e:
            return ComponentHealth(
                name="cache_memory",
                status=HealthStatus.UNHEALTHY,
                message="Redis memory check failed",
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.utcnow(),
            )


class HTTPHealthAdapter(ExternalServiceHealthPort):
    """HTTP external service health adapter"""

    async def check_service(self, url: str, timeout: float = 5.0) -> ComponentHealth:
        """Check external service health via HTTP"""
        start_time = time.time()

        try:
            import httpx

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)

            response_time = (time.time() - start_time) * 1000

            if 200 <= response.status_code < 300:
                status = HealthStatus.HEALTHY
                message = f"Service responded with {response.status_code}"
            elif 400 <= response.status_code < 500:
                status = HealthStatus.DEGRADED
                message = f"Service client error: {response.status_code}"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Service error: {response.status_code}"

            return ComponentHealth(
                name=f"external_service_{url}",
                status=status,
                message=message,
                response_time_ms=response_time,
                details={"status_code": response.status_code, "url": url},
                last_checked=datetime.utcnow(),
            )

        except ImportError:
            return ComponentHealth(
                name=f"external_service_{url}",
                status=HealthStatus.UNKNOWN,
                message="httpx not available",
                error="Missing httpx dependency",
                last_checked=datetime.utcnow(),
            )
        except Exception as e:
            return ComponentHealth(
                name=f"external_service_{url}",
                status=HealthStatus.UNHEALTHY,
                message=f"Service check failed: {str(e)}",
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.utcnow(),
            )


class SystemResourcesAdapter(SystemResourcesPort):
    """System resources health adapter using psutil"""

    async def check_cpu_usage(self) -> ComponentHealth:
        """Check CPU usage"""
        start_time = time.time()

        try:
            import psutil

            # Get CPU usage over 1 second interval
            cpu_percent = psutil.cpu_percent(interval=1)

            response_time = (time.time() - start_time) * 1000

            if cpu_percent < 80:
                status = HealthStatus.HEALTHY
                message = f"CPU usage: {cpu_percent:.1f}%"
            elif cpu_percent < 90:
                status = HealthStatus.DEGRADED
                message = f"CPU usage high: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"CPU usage critical: {cpu_percent:.1f}%"

            return ComponentHealth(
                name="cpu_usage",
                status=status,
                message=message,
                response_time_ms=response_time,
                details={"cpu_percent": cpu_percent},
                last_checked=datetime.utcnow(),
            )

        except ImportError:
            return ComponentHealth(
                name="cpu_usage",
                status=HealthStatus.UNKNOWN,
                message="psutil not available",
                error="Missing psutil dependency",
                last_checked=datetime.utcnow(),
            )
        except Exception as e:
            return ComponentHealth(
                name="cpu_usage",
                status=HealthStatus.UNHEALTHY,
                message=f"CPU check failed: {str(e)}",
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.utcnow(),
            )

    async def check_memory_usage(self) -> ComponentHealth:
        """Check memory usage"""
        start_time = time.time()

        try:
            import psutil

            memory = psutil.virtual_memory()

            response_time = (time.time() - start_time) * 1000

            if memory.percent < 80:
                status = HealthStatus.HEALTHY
                message = f"Memory usage: {memory.percent:.1f}%"
            elif memory.percent < 90:
                status = HealthStatus.DEGRADED
                message = f"Memory usage high: {memory.percent:.1f}%"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage critical: {memory.percent:.1f}%"

            return ComponentHealth(
                name="memory_usage",
                status=status,
                message=message,
                response_time_ms=response_time,
                details={
                    "memory_percent": memory.percent,
                    "available_gb": memory.available / (1024**3),
                    "total_gb": memory.total / (1024**3),
                },
                last_checked=datetime.utcnow(),
            )

        except ImportError:
            return ComponentHealth(
                name="memory_usage",
                status=HealthStatus.UNKNOWN,
                message="psutil not available",
                error="Missing psutil dependency",
                last_checked=datetime.utcnow(),
            )
        except Exception as e:
            return ComponentHealth(
                name="memory_usage",
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}",
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.utcnow(),
            )

    async def check_disk_usage(self, path: str = "/") -> ComponentHealth:
        """Check disk usage"""
        start_time = time.time()

        try:
            import shutil

            total, used, free = shutil.disk_usage(path)
            usage_percent = (used / total) * 100

            response_time = (time.time() - start_time) * 1000

            if usage_percent < 80:
                status = HealthStatus.HEALTHY
                message = f"Disk usage: {usage_percent:.1f}%"
            elif usage_percent < 90:
                status = HealthStatus.DEGRADED
                message = f"Disk usage high: {usage_percent:.1f}%"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Disk usage critical: {usage_percent:.1f}%"

            return ComponentHealth(
                name="disk_usage",
                status=status,
                message=message,
                response_time_ms=response_time,
                details={
                    "disk_percent": usage_percent,
                    "free_gb": free / (1024**3),
                    "total_gb": total / (1024**3),
                    "path": path,
                },
                last_checked=datetime.utcnow(),
            )

        except Exception as e:
            return ComponentHealth(
                name="disk_usage",
                status=HealthStatus.UNHEALTHY,
                message=f"Disk check failed: {str(e)}",
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.utcnow(),
            )
