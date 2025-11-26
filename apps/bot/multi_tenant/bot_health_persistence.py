"""
Bot Health Metrics Persistence Service

Handles saving and loading of bot health metrics to/from database.
Runs as a background task to periodically persist in-memory metrics.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_, delete, select

from apps.bot.multi_tenant.bot_health import BotHealthMetrics, get_health_monitor
from infra.db.models.bot_health_orm import BotHealthMetricOrm

logger = logging.getLogger(__name__)


class BotHealthPersistenceService:
    """
    Service for persisting bot health metrics to database.

    Features:
    - Periodic background persistence (every 5 minutes)
    - Load metrics from database on startup
    - Automatic cleanup of old metrics (retention policy)
    - Batch operations for efficiency
    """

    def __init__(
        self,
        db_session_factory,
        persist_interval_seconds: int = 300,  # 5 minutes
        retention_days: int = 30,  # Keep 30 days of history
    ):
        """
        Initialize persistence service.

        Args:
            db_session_factory: Async database session factory
            persist_interval_seconds: How often to persist metrics
            retention_days: How many days of metrics to keep
        """
        self.db_session_factory = db_session_factory
        self.persist_interval_seconds = persist_interval_seconds
        self.retention_days = retention_days
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self):
        """Start the background persistence task."""
        if self._running:
            logger.warning("BotHealthPersistenceService already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._persistence_loop())
        logger.info(
            f"BotHealthPersistenceService started (interval: {self.persist_interval_seconds}s, "
            f"retention: {self.retention_days} days)"
        )

    async def stop(self):
        """Stop the background persistence task."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("BotHealthPersistenceService stopped")

    async def _persistence_loop(self):
        """Background loop that periodically persists metrics."""
        while self._running:
            try:
                await asyncio.sleep(self.persist_interval_seconds)
                await self.persist_all_metrics()
                await self.cleanup_old_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in persistence loop: {e}", exc_info=True)

    async def persist_all_metrics(self):
        """
        Persist all current bot health metrics to database.

        Creates a snapshot of all bot metrics at the current time.
        """
        try:
            health_monitor = get_health_monitor()
            all_metrics = health_monitor.get_all_metrics()

            if not all_metrics:
                logger.debug("No metrics to persist")
                return

            async with self.db_session_factory() as session:
                # Get circuit breaker states
                from apps.bot.multi_tenant.circuit_breaker import get_circuit_breaker_registry

                circuit_registry = get_circuit_breaker_registry()
                circuit_states = circuit_registry.get_all_states()

                # Create ORM objects for all metrics
                timestamp = datetime.now()
                metric_objects = []

                for user_id, metrics in all_metrics.items():
                    # Get circuit breaker state for this user
                    circuit_state = circuit_states.get(user_id, {}).get("state", None)

                    metric_orm = BotHealthMetricOrm(
                        user_id=user_id,
                        timestamp=timestamp,
                        status=metrics.status.value,
                        total_requests=metrics.total_requests,
                        successful_requests=metrics.successful_requests,
                        failed_requests=metrics.failed_requests,
                        consecutive_failures=metrics.consecutive_failures,
                        error_rate=metrics.error_rate,
                        avg_response_time_ms=metrics.avg_response_time_ms,
                        last_success=metrics.last_success,
                        last_failure=metrics.last_failure,
                        last_check=metrics.last_check,
                        is_rate_limited=metrics.is_rate_limited,
                        last_error_type=metrics.last_error_type,
                        circuit_breaker_state=circuit_state,
                    )
                    metric_objects.append(metric_orm)

                # Batch insert all metrics
                session.add_all(metric_objects)
                await session.commit()

                logger.info(f"Persisted {len(metric_objects)} bot health metrics")

        except Exception as e:
            logger.error(f"Failed to persist metrics: {e}", exc_info=True)

    async def cleanup_old_metrics(self):
        """
        Remove metrics older than retention period.

        Keeps database size manageable by removing old historical data.
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)

            async with self.db_session_factory() as session:
                # Delete old metrics
                stmt = delete(BotHealthMetricOrm).where(
                    BotHealthMetricOrm.timestamp < cutoff_date
                )
                result = await session.execute(stmt)
                await session.commit()

                if result.rowcount > 0:
                    logger.info(f"Cleaned up {result.rowcount} old health metrics")

        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}", exc_info=True)

    async def load_latest_metrics(self):
        """
        Load the most recent metrics from database on startup.

        Restores the in-memory health monitor state from last persisted data.
        """
        try:
            async with self.db_session_factory() as session:
                # Get the most recent timestamp
                max_timestamp_stmt = select(BotHealthMetricOrm.timestamp).order_by(
                    BotHealthMetricOrm.timestamp.desc()
                ).limit(1)
                result = await session.execute(max_timestamp_stmt)
                max_timestamp = result.scalar_one_or_none()

                if not max_timestamp:
                    logger.info("No persisted metrics found")
                    return

                # Load all metrics from the most recent snapshot
                stmt = select(BotHealthMetricOrm).where(
                    BotHealthMetricOrm.timestamp == max_timestamp
                )
                result = await session.execute(stmt)
                metrics = result.scalars().all()

                # Restore metrics to health monitor
                health_monitor = get_health_monitor()

                for metric_orm in metrics:
                    # Reconstruct BotHealthMetrics object
                    from apps.bot.multi_tenant.bot_health import BotHealthStatus

                    restored_metrics = BotHealthMetrics(
                        user_id=metric_orm.user_id,
                        status=BotHealthStatus(metric_orm.status),
                        total_requests=metric_orm.total_requests,
                        successful_requests=metric_orm.successful_requests,
                        failed_requests=metric_orm.failed_requests,
                        consecutive_failures=metric_orm.consecutive_failures,
                        error_rate=metric_orm.error_rate,
                        avg_response_time_ms=metric_orm.avg_response_time_ms,
                        last_success=metric_orm.last_success,
                        last_failure=metric_orm.last_failure,
                        last_check=metric_orm.last_check,
                        is_rate_limited=metric_orm.is_rate_limited,
                        last_error_type=metric_orm.last_error_type,
                    )

                    # Restore to monitor
                    health_monitor.metrics[metric_orm.user_id] = restored_metrics

                logger.info(
                    f"Loaded {len(metrics)} bot health metrics from {max_timestamp}"
                )

        except Exception as e:
            logger.error(f"Failed to load metrics: {e}", exc_info=True)

    async def get_user_history(
        self,
        user_id: int,
        hours: int = 24,
    ) -> list[dict[str, Any]]:
        """
        Get historical metrics for a specific user.

        Args:
            user_id: User to get history for
            hours: How many hours of history to retrieve

        Returns:
            List of metric snapshots ordered by timestamp
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            async with self.db_session_factory() as session:
                stmt = (
                    select(BotHealthMetricOrm)
                    .where(
                        and_(
                            BotHealthMetricOrm.user_id == user_id,
                            BotHealthMetricOrm.timestamp >= cutoff_time,
                        )
                    )
                    .order_by(BotHealthMetricOrm.timestamp.asc())
                )

                result = await session.execute(stmt)
                metrics = result.scalars().all()

                return [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "status": m.status,
                        "error_rate": m.error_rate,
                        "total_requests": m.total_requests,
                        "successful_requests": m.successful_requests,
                        "failed_requests": m.failed_requests,
                        "consecutive_failures": m.consecutive_failures,
                        "avg_response_time_ms": m.avg_response_time_ms,
                        "circuit_breaker_state": m.circuit_breaker_state,
                    }
                    for m in metrics
                ]

        except Exception as e:
            logger.error(f"Failed to get user history: {e}", exc_info=True)
            return []

    async def get_unhealthy_history(
        self,
        hours: int = 24,
    ) -> list[dict[str, Any]]:
        """
        Get history of all unhealthy bots.

        Args:
            hours: How many hours of history to retrieve

        Returns:
            List of unhealthy bot snapshots
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            async with self.db_session_factory() as session:
                stmt = (
                    select(BotHealthMetricOrm)
                    .where(
                        and_(
                            BotHealthMetricOrm.timestamp >= cutoff_time,
                            BotHealthMetricOrm.status.in_(["unhealthy", "suspended"]),
                        )
                    )
                    .order_by(BotHealthMetricOrm.timestamp.desc())
                )

                result = await session.execute(stmt)
                metrics = result.scalars().all()

                return [
                    {
                        "user_id": m.user_id,
                        "timestamp": m.timestamp.isoformat(),
                        "status": m.status,
                        "error_rate": m.error_rate,
                        "consecutive_failures": m.consecutive_failures,
                        "last_error_type": m.last_error_type,
                        "circuit_breaker_state": m.circuit_breaker_state,
                    }
                    for m in metrics
                ]

        except Exception as e:
            logger.error(f"Failed to get unhealthy history: {e}", exc_info=True)
            return []


# Global singleton instance
_persistence_service: BotHealthPersistenceService | None = None


def get_persistence_service() -> BotHealthPersistenceService:
    """Get global persistence service singleton (must be initialized first)."""
    global _persistence_service
    if _persistence_service is None:
        raise RuntimeError(
            "BotHealthPersistenceService not initialized. Call initialize_persistence_service() first."
        )
    return _persistence_service


def initialize_persistence_service(
    db_session_factory,
    persist_interval_seconds: int = 300,
    retention_days: int = 30,
) -> BotHealthPersistenceService:
    """
    Initialize the global persistence service.

    Should be called once during application startup.
    """
    global _persistence_service
    _persistence_service = BotHealthPersistenceService(
        db_session_factory=db_session_factory,
        persist_interval_seconds=persist_interval_seconds,
        retention_days=retention_days,
    )
    return _persistence_service
