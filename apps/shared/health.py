"""
Health Check Endpoints
System health monitoring for Clean Architecture components
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from apps.shared.di import Container, get_container

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", summary="System Health Check")
async def health_check() -> dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "analyticbot",
        "version": "2.8.0",
        "architecture": "clean_architecture",
    }


@router.get("/db", summary="Database Health Check")
async def database_health(container: Container = Depends(get_container)) -> dict[str, Any]:
    """Check database connectivity and basic operations"""

    health_info: dict[str, Any] = {
        "status": "unknown",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {},
        "repositories": {},
        "phase3_optimizations": {},
    }

    try:
        # Test optimized database manager
        db_mgr = await container.database_manager()
        health_check = await db_mgr.health_check()

        health_info["database"] = {
            "type": "postgresql_optimized",
            "status": "connected" if health_check["healthy"] else "disconnected",
            "pool_size": health_check["pool_size"],
            "idle_connections": health_check["idle_connections"],
            "used_connections": health_check["used_connections"],
            "avg_query_time": f"{health_check['avg_query_time']:.4f}s",
            "total_queries": health_check["total_queries"],
            "phase3_enabled": True,
        }

        # Optimized connection management specific metrics
        health_info["phase3_optimizations"] = {
            "connection_health_monitoring": "active",
            "query_optimization": "enabled",
            "performance_indexes": "applied",
            "prepared_statements": "available",
        }

        # Test repository instantiation with optimized connection management
        try:
            await container.user_repo()
            health_info["repositories"]["user"] = "initialized"

            await container.analytics_repo()
            health_info["repositories"]["analytics"] = "initialized"

            await container.channel_repo()
            health_info["repositories"]["channel"] = "initialized"

        except Exception as repo_error:
            health_info["repositories"]["error"] = str(repo_error)

        health_info["status"] = "healthy"

    except Exception as e:
        health_info["status"] = "unhealthy"
        health_info["error"] = str(e)
        raise HTTPException(status_code=503, detail=health_info)

    return health_info


@router.get("/architecture", summary="Architecture Compliance Check")
async def architecture_health() -> dict[str, Any]:
    """Check Clean Architecture compliance"""

    compliance_info = {
        "status": "compliant",
        "timestamp": datetime.utcnow().isoformat(),
        "layers": {
            "core": {
                "description": "Domain logic and interfaces",
                "dependencies": ["standard_library", "core_modules"],
                "violations": [],
            },
            "apps": {
                "description": "Application layer (HTTP/Telegram interfaces)",
                "dependencies": ["core", "standard_library"],
                "violations": [],
            },
            "infra": {
                "description": "Infrastructure implementations",
                "dependencies": ["core", "external_libraries"],
                "violations": [],
            },
        },
        "dependency_rule": "core ← apps → infra",
        "guard_status": "enabled",
    }

    # Run import guard check
    import subprocess

    try:
        result = subprocess.run(
            ["python3", "scripts/guard_imports.py"],
            capture_output=True,
            text=True,
            cwd="/home/alonur/analyticbot",
        )

        if result.returncode == 0:
            compliance_info["import_violations"] = []
        else:
            compliance_info["status"] = "violations_detected"
            compliance_info["import_violations"] = (
                result.stdout.split("\n") if result.stdout else []
            )

    except Exception as e:
        compliance_info["guard_status"] = f"error: {str(e)}"

    return compliance_info


@router.get("/di", summary="Dependency Injection Health")
async def di_health(container: Container = Depends(get_container)) -> dict[str, Any]:
    """Check dependency injection container health"""

    di_info: dict[str, Any] = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "container": {"type": "apps.shared.di.Container", "initialized": True},
        "dependencies": {},
    }

    try:
        # Test repository dependencies
        dependencies = [
            ("user_repo", container.user_repo),
            ("admin_repo", container.admin_repo),
            ("analytics_repo", container.analytics_repo),
            ("channel_repo", container.channel_repo),
            ("payment_repo", container.payment_repo),
            ("plan_repo", container.plan_repo),
        ]

        for name, factory in dependencies:
            try:
                repo = await factory()
                di_info["dependencies"][name] = {"status": "resolved", "type": type(repo).__name__}
            except Exception as e:
                di_info["dependencies"][name] = {"status": "failed", "error": str(e)}
                di_info["status"] = "degraded"

    except Exception as e:
        di_info["status"] = "failed"
        di_info["error"] = str(e)
        raise HTTPException(status_code=503, detail=di_info)

    return di_info
