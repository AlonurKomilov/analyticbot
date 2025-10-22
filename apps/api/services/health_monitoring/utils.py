"""
Health Check Utilities
Framework-specific health check implementations
"""

import os
import shutil
from typing import Any

import asyncpg
import httpx
import psutil

from apps.api.services.health_monitoring.base import logger

# Redis is optional dependency
try:
    import redis.asyncio as redis_module  # type: ignore[no-redef]
except ImportError:
    redis_module = None  # type: ignore[assignment]


async def check_database_health(connection_string: str | None = None) -> dict[str, Any]:
    """Database health check using asyncpg"""
    try:
        # Use provided connection string or environment variable
        conn_str = connection_string or os.getenv("DATABASE_URL")
        if not conn_str:
            return {"healthy": False, "error": "No database connection string configured"}

        # Test database connection
        conn = await asyncpg.connect(conn_str)
        await conn.execute("SELECT 1")
        await conn.close()

        return {"healthy": True, "database_type": "postgresql"}

    except Exception as e:
        return {"healthy": False, "error": f"Database connection failed: {str(e)}"}


async def check_redis_health(
    host: str = "localhost", port: int = 10200, db: int = 0
) -> dict[str, Any]:
    """Redis health check using redis.asyncio

    Updated to use port 10200 (production Redis port) by default
    instead of 6379 (standard Redis port).
    """
    if not redis_module:
        return {"healthy": False, "error": "Redis client not available"}

    try:
        # Try to get Redis URL from environment first
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            # Parse URL to extract host, port, db
            # Format: redis://host:port/db
            try:
                from urllib.parse import urlparse

                parsed = urlparse(redis_url)
                host = parsed.hostname or host
                port = parsed.port or port
                db = int(parsed.path.lstrip("/")) if parsed.path and parsed.path != "/" else db
            except Exception as e:
                logger.warning(f"Failed to parse REDIS_URL, using defaults: {e}")

        redis_client = redis_module.Redis(host=host, port=port, db=db, decode_responses=True)
        await redis_client.ping()
        await redis_client.close()

        return {"healthy": True, "redis_host": f"{host}:{port}/{db}"}

    except Exception as e:
        return {"healthy": False, "error": f"Redis connection failed: {str(e)}"}


async def check_http_endpoint(url: str, timeout: float = 5.0) -> dict[str, Any]:
    """HTTP endpoint health check using httpx"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)

        healthy = 200 <= response.status_code < 400
        return {"healthy": healthy, "status_code": response.status_code, "url": url}

    except Exception as e:
        return {"healthy": False, "error": f"HTTP check failed: {str(e)}", "url": url}


async def check_disk_space(path: str = "/", warning_percent: float = 80) -> dict[str, Any]:
    """Disk space health check using shutil"""
    try:
        total, used, free = shutil.disk_usage(path)
        used_percent = (used / total) * 100

        healthy = used_percent < warning_percent

        return {
            "healthy": healthy,
            "used_percent": round(used_percent, 2),
            "free_gb": round(free / (1024**3), 2),
            "total_gb": round(total / (1024**3), 2),
            "path": path,
        }

    except Exception as e:
        return {"healthy": False, "error": f"Disk check failed: {str(e)}", "path": path}


async def check_memory_usage(warning_percent: float = 85) -> dict[str, Any]:
    """Memory usage health check using psutil"""
    try:
        memory = psutil.virtual_memory()
        used_percent = memory.percent

        healthy = used_percent < warning_percent

        return {
            "healthy": healthy,
            "used_percent": used_percent,
            "available_gb": round(memory.available / (1024**3), 2),
            "total_gb": round(memory.total / (1024**3), 2),
        }

    except Exception as e:
        return {"healthy": False, "error": f"Memory check failed: {str(e)}"}
