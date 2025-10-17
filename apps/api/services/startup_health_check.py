"""
Backend Startup Health Check System
====================================

Validates all critical services and dependencies on application startup.
Logs comprehensive diagnostics without blocking startup (fail-fast mode optional).

Checks:
- Database connectivity and schema
- Redis cache availability
- External service dependencies
- Critical configuration validation
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CheckStatus(str, Enum):
    """Health check status"""

    PASSED = "passed"
    FAILED = "failed"
    DEGRADED = "degraded"
    SKIPPED = "skipped"


class CheckSeverity(str, Enum):
    """Check severity level"""

    CRITICAL = "critical"  # Must pass for production
    IMPORTANT = "important"  # Should pass, degraded mode possible
    OPTIONAL = "optional"  # Nice to have


@dataclass
class HealthCheckResult:
    """Individual health check result"""

    name: str
    severity: CheckSeverity
    status: CheckStatus
    duration_ms: float = 0.0
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StartupHealthReport:
    """Complete startup health report"""

    checks: list[HealthCheckResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime | None = None

    @property
    def duration_ms(self) -> float:
        """Total duration in milliseconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0

    @property
    def critical_failures(self) -> list[HealthCheckResult]:
        """Get all critical failures"""
        return [
            c
            for c in self.checks
            if c.severity == CheckSeverity.CRITICAL and c.status == CheckStatus.FAILED
        ]

    @property
    def is_production_ready(self) -> bool:
        """Check if system is production ready (no critical failures)"""
        return len(self.critical_failures) == 0

    @property
    def overall_status(self) -> CheckStatus:
        """Overall system status"""
        if self.critical_failures:
            return CheckStatus.FAILED

        important_failures = [
            c
            for c in self.checks
            if c.severity == CheckSeverity.IMPORTANT and c.status == CheckStatus.FAILED
        ]
        if important_failures:
            return CheckStatus.DEGRADED

        return CheckStatus.PASSED


class StartupHealthChecker:
    """Backend startup health check orchestrator"""

    def __init__(
        self, fail_fast: bool = False, skip_optional: bool = True, timeout_seconds: float = 10.0
    ):
        """
        Initialize health checker

        Args:
            fail_fast: Raise exception on critical failure (blocks startup)
            skip_optional: Skip optional checks for faster startup
            timeout_seconds: Timeout per check
        """
        self.fail_fast = fail_fast
        self.skip_optional = skip_optional
        self.timeout_seconds = timeout_seconds

    async def run_all_checks(self) -> StartupHealthReport:
        """Run all startup health checks"""
        report = StartupHealthReport()

        logger.info("🏥 Running backend startup health checks...")

        # Define all checks
        checks = [
            # Critical checks
            (self._check_database, CheckSeverity.CRITICAL),
            (self._check_redis_cache, CheckSeverity.IMPORTANT),
            (self._check_configuration, CheckSeverity.CRITICAL),
            # Optional checks
            (self._check_file_permissions, CheckSeverity.OPTIONAL),
            (self._check_environment, CheckSeverity.OPTIONAL),
        ]

        # Filter checks based on skip_optional
        if self.skip_optional:
            checks = [(fn, sev) for fn, sev in checks if sev != CheckSeverity.OPTIONAL]

        # Run checks sequentially
        for check_fn, severity in checks:
            try:
                result = await asyncio.wait_for(check_fn(severity), timeout=self.timeout_seconds)
                report.checks.append(result)

                # Log result
                emoji = (
                    "✅"
                    if result.status == CheckStatus.PASSED
                    else "⚠️"
                    if result.status == CheckStatus.DEGRADED
                    else "❌"
                )
                logger.info(
                    f"{emoji} {result.name}: {result.status.value} " f"({result.duration_ms:.0f}ms)"
                )

                # Fail fast on critical failure
                if (
                    self.fail_fast
                    and result.severity == CheckSeverity.CRITICAL
                    and result.status == CheckStatus.FAILED
                ):
                    logger.error(f"❌ Critical check failed: {result.name}")
                    break

            except TimeoutError:
                result = HealthCheckResult(
                    name=check_fn.__name__.replace("_check_", "").replace("_", " ").title(),
                    severity=severity,
                    status=CheckStatus.FAILED,
                    error="Check timed out",
                    duration_ms=self.timeout_seconds * 1000,
                )
                report.checks.append(result)
                logger.error(f"⏱️ Check timed out: {result.name}")
            except Exception as e:
                result = HealthCheckResult(
                    name=check_fn.__name__.replace("_check_", "").replace("_", " ").title(),
                    severity=severity,
                    status=CheckStatus.FAILED,
                    error=str(e),
                    duration_ms=0,
                )
                report.checks.append(result)
                logger.error(f"💥 Check error: {result.name} - {e}")

        report.end_time = datetime.utcnow()

        # Log summary
        self._log_summary(report)

        return report

    async def _check_database(self, severity: CheckSeverity) -> HealthCheckResult:
        """Check database connectivity and health"""
        import time

        start = time.time()

        result = HealthCheckResult(
            name="Database Connectivity", severity=severity, status=CheckStatus.FAILED
        )

        try:
            from apps.shared.di import get_container

            container = get_container()
            pool = await container.asyncpg_pool()

            # Test query
            async with pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                result.details["postgres_version"] = version.split()[1] if version else "unknown"
                result.details["pool_size"] = pool.get_size()
                result.details["pool_max"] = pool.get_max_size()

            result.status = CheckStatus.PASSED

        except Exception as e:
            result.error = f"Database connection failed: {e}"
            logger.error(f"Database health check failed: {e}", exc_info=True)

        result.duration_ms = (time.time() - start) * 1000
        return result

    async def _check_redis_cache(self, severity: CheckSeverity) -> HealthCheckResult:
        """Check Redis cache connectivity"""
        import time

        start = time.time()

        result = HealthCheckResult(name="Redis Cache", severity=severity, status=CheckStatus.FAILED)

        try:
            import redis.asyncio as aioredis

            from config import settings

            # Use Redis DB 1 for caching
            redis_url = settings.REDIS_URL.replace("/0", "/1")
            redis_client = aioredis.from_url(redis_url, decode_responses=True)

            # Test connection
            await redis_client.ping()
            info = await redis_client.info()

            result.details["redis_version"] = info.get("redis_version", "unknown")
            result.details["connected_clients"] = info.get("connected_clients", 0)
            result.details["used_memory_human"] = info.get("used_memory_human", "unknown")
            result.status = CheckStatus.PASSED

            await redis_client.close()

        except Exception as e:
            result.error = f"Redis connection failed: {e}"
            result.status = CheckStatus.DEGRADED  # App can run without cache
            logger.warning(f"Redis health check failed (degraded): {e}")

        result.duration_ms = (time.time() - start) * 1000
        return result

    async def _check_configuration(self, severity: CheckSeverity) -> HealthCheckResult:
        """Check critical configuration settings"""
        import time

        start = time.time()

        result = HealthCheckResult(
            name="Configuration Validation", severity=severity, status=CheckStatus.PASSED
        )

        try:
            from config import settings

            issues = []

            # Check database URL
            if not settings.DATABASE_URL:
                issues.append("DATABASE_URL not configured")

            # Check Redis URL
            if not settings.REDIS_URL:
                issues.append("REDIS_URL not configured")

            # Check JWT secret
            jwt_secret = getattr(settings, "JWT_SECRET_KEY", None)
            if not jwt_secret or str(jwt_secret) == "change-me-in-production":
                issues.append("JWT SECRET_KEY not properly configured")

            if issues:
                result.error = f"Configuration issues: {', '.join(issues)}"
                result.status = CheckStatus.FAILED
            else:
                result.details["database_configured"] = True
                result.details["redis_configured"] = True
                result.details["jwt_configured"] = True
                result.details["debug_mode"] = settings.DEBUG

        except Exception as e:
            result.error = f"Configuration check failed: {e}"
            result.status = CheckStatus.FAILED

        result.duration_ms = (time.time() - start) * 1000
        return result

    async def _check_file_permissions(self, severity: CheckSeverity) -> HealthCheckResult:
        """Check file system permissions"""
        import os
        import time

        start = time.time()

        result = HealthCheckResult(
            name="File Permissions", severity=severity, status=CheckStatus.PASSED
        )

        try:
            # Check logs directory
            logs_dir = "logs"
            if os.path.exists(logs_dir):
                result.details["logs_writable"] = os.access(logs_dir, os.W_OK)
            else:
                result.details["logs_exists"] = False
                result.status = CheckStatus.DEGRADED

            # Check data directory
            data_dir = "data"
            if os.path.exists(data_dir):
                result.details["data_writable"] = os.access(data_dir, os.W_OK)
            else:
                result.details["data_exists"] = False

        except Exception as e:
            result.error = str(e)
            result.status = CheckStatus.DEGRADED

        result.duration_ms = (time.time() - start) * 1000
        return result

    async def _check_environment(self, severity: CheckSeverity) -> HealthCheckResult:
        """Check environment and runtime"""
        import platform
        import sys
        import time

        start = time.time()

        result = HealthCheckResult(
            name="Environment Info", severity=severity, status=CheckStatus.PASSED
        )

        try:
            result.details["python_version"] = sys.version.split()[0]
            result.details["platform"] = platform.platform()
            result.details["architecture"] = platform.machine()
        except Exception as e:
            result.error = str(e)
            result.status = CheckStatus.DEGRADED

        result.duration_ms = (time.time() - start) * 1000
        return result

    def _log_summary(self, report: StartupHealthReport):
        """Log comprehensive summary"""
        logger.info("═" * 60)
        logger.info("         🏥 STARTUP HEALTH CHECK REPORT")
        logger.info("═" * 60)
        logger.info(f"Overall Status: {report.overall_status.value.upper()}")
        logger.info(f"Production Ready: {'YES ✅' if report.is_production_ready else 'NO ❌'}")
        logger.info(f"Duration: {report.duration_ms:.0f}ms")
        logger.info("")

        if report.critical_failures:
            logger.error("❌ CRITICAL FAILURES:")
            for check in report.critical_failures:
                logger.error(f"  - {check.name}: {check.error}")
            logger.info("")

        # Group by status
        passed = [c for c in report.checks if c.status == CheckStatus.PASSED]
        degraded = [c for c in report.checks if c.status == CheckStatus.DEGRADED]
        failed = [c for c in report.checks if c.status == CheckStatus.FAILED]

        if passed:
            logger.info(f"✅ PASSED ({len(passed)}):")
            for check in passed:
                logger.info(f"  - {check.name} ({check.duration_ms:.0f}ms)")

        if degraded:
            logger.warning(f"⚠️ DEGRADED ({len(degraded)}):")
            for check in degraded:
                logger.warning(f"  - {check.name}: {check.error}")

        if failed and not report.critical_failures:
            logger.error(f"❌ FAILED ({len(failed)}):")
            for check in failed:
                logger.error(f"  - {check.name}: {check.error}")

        logger.info("═" * 60)


async def run_startup_health_check(
    fail_fast: bool = False, skip_optional: bool = True
) -> StartupHealthReport:
    """
    Run startup health checks

    Args:
        fail_fast: Raise exception on critical failure
        skip_optional: Skip optional checks

    Returns:
        Complete health report

    Raises:
        RuntimeError: If fail_fast=True and critical check fails
    """
    checker = StartupHealthChecker(fail_fast=fail_fast, skip_optional=skip_optional)

    report = await checker.run_all_checks()

    if fail_fast and not report.is_production_ready:
        raise RuntimeError(
            f"Startup health check failed: {len(report.critical_failures)} critical failures"
        )

    return report
