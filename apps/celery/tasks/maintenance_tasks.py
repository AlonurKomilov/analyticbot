"""
Maintenance Tasks - Database and System Maintenance

Periodic tasks for database optimization, cleanup, and maintenance operations.
Includes materialized view refresh, vacuum operations, and cleanup jobs.
"""

import logging
from typing import Any

from apps.celery.celery_app import celery_app, enhanced_retry_task
from apps.di import get_db_session
from core.services.materialized_view_service import MaterializedViewService

logger = logging.getLogger(__name__)


@celery_app.task(
    name="apps.celery.tasks.maintenance_tasks.refresh_materialized_views",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
@enhanced_retry_task()
async def refresh_materialized_views(self) -> dict[str, Any]:
    """
    Refresh all materialized views to ensure analytics data is up-to-date.

    Scheduled to run every 4 hours to keep dashboard analytics current.
    Uses CONCURRENTLY option to avoid locking tables during refresh.

    Returns:
        Dictionary with refresh results and timing information.
    """
    logger.info("Starting scheduled materialized view refresh")

    try:
        async for session in get_db_session():
            # Verify views exist before attempting refresh
            view_existence = await MaterializedViewService.verify_views_exist(session)
            missing_views = [name for name, exists in view_existence.items() if not exists]

            if missing_views:
                logger.warning(f"Missing materialized views: {missing_views}")
                return {
                    "success": False,
                    "error": f"Missing views: {', '.join(missing_views)}",
                    "views": view_existence,
                }

            # Refresh all views with CONCURRENTLY to avoid locking
            result = await MaterializedViewService.refresh_all_views(session, concurrent=True)

            if result["success"]:
                logger.info(
                    f"✅ Materialized views refreshed successfully in "
                    f"{result['total_duration_seconds']:.2f}s"
                )
            else:
                logger.error(f"❌ Materialized view refresh failed: {result.get('error')}")

            return result

    except Exception as e:
        logger.error(f"Error in refresh_materialized_views task: {str(e)}", exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries)) from e


@celery_app.task(
    name="apps.celery.tasks.maintenance_tasks.get_view_statistics",
    bind=True,
)
async def get_view_statistics(self) -> dict[str, Any]:
    """
    Get statistics about materialized views.

    Returns row counts, sizes, and metadata for monitoring.
    Can be called on-demand or scheduled for monitoring purposes.

    Returns:
        Dictionary with view statistics.
    """
    logger.info("Collecting materialized view statistics")

    try:
        async for session in get_db_session():
            stats = await MaterializedViewService.get_view_stats(session)

            # Log summary
            total_rows = sum(v.get("row_count", 0) for v in stats.get("views", []))
            logger.info(
                f"Materialized view stats: {len(stats.get('views', []))} views, "
                f"{total_rows:,} total rows, "
                f"{stats.get('total_size_bytes', 0) / 1024 / 1024:.2f} MB"
            )

            return stats

    except Exception as e:
        logger.error(f"Error collecting view statistics: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}
