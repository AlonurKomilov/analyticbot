"""
Materialized View Refresh Service

Handles refreshing of PostgreSQL materialized views for analytics data.
Ensures dashboard analytics remain up-to-date without impacting live queries.
"""

import logging
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class MaterializedViewService:
    """
    Service for managing PostgreSQL materialized views.

    Materialized views provide pre-computed analytics data for faster queries.
    They must be periodically refreshed to show current data.
    """

    # Views defined in migration 0010
    VIEWS = [
        "mv_channel_daily_recent",  # Channel performance aggregations
        "mv_post_metrics_recent",  # Post metrics summaries
    ]

    @staticmethod
    async def refresh_all_views(session: AsyncSession, concurrent: bool = True) -> dict[str, any]:
        """
        Refresh all materialized views.

        Args:
            session: Database session to use for operations
            concurrent: If True, uses CONCURRENTLY to avoid locking tables.
                       This is slower but doesn't block regular queries.

        Returns:
            Dictionary with refresh results and timing information.
        """
        start_time = datetime.utcnow()
        results = {
            "started_at": start_time.isoformat(),
            "concurrent": concurrent,
            "views": [],
            "success": True,
            "total_duration_seconds": 0,
        }

        logger.info(f"Starting materialized view refresh (concurrent={concurrent})")

        try:
            for view_name in MaterializedViewService.VIEWS:
                view_result = await MaterializedViewService._refresh_single_view(
                    session, view_name, concurrent
                )
                results["views"].append(view_result)

                if not view_result["success"]:
                    results["success"] = False
                    logger.error(f"Failed to refresh view {view_name}: {view_result.get('error')}")

            # Commit transaction
            await session.commit()

        except Exception as e:
            logger.error(f"Error during view refresh: {str(e)}", exc_info=True)
            results["success"] = False
            results["error"] = str(e)

        end_time = datetime.utcnow()
        results["completed_at"] = end_time.isoformat()
        results["total_duration_seconds"] = (end_time - start_time).total_seconds()

        logger.info(
            f"Materialized view refresh completed in {results['total_duration_seconds']:.2f}s "
            f"(success={results['success']})"
        )

        return results

    @staticmethod
    async def _refresh_single_view(
        session: AsyncSession, view_name: str, concurrent: bool
    ) -> dict[str, any]:
        """
        Refresh a single materialized view.

        Args:
            session: Database session
            view_name: Name of the materialized view
            concurrent: Whether to use CONCURRENTLY option

        Returns:
            Dictionary with refresh result for this view.
        """
        start_time = datetime.utcnow()
        result = {
            "view_name": view_name,
            "started_at": start_time.isoformat(),
            "success": False,
            "duration_seconds": 0,
        }

        try:
            # Build REFRESH command
            concurrent_keyword = "CONCURRENTLY" if concurrent else ""
            sql = f"REFRESH MATERIALIZED VIEW {concurrent_keyword} {view_name}"

            logger.debug(f"Executing: {sql}")
            await session.execute(text(sql))

            result["success"] = True
            logger.info(f"Successfully refreshed view: {view_name}")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Failed to refresh view {view_name}: {str(e)}", exc_info=True)

        end_time = datetime.utcnow()
        result["completed_at"] = end_time.isoformat()
        result["duration_seconds"] = (end_time - start_time).total_seconds()

        return result

    @staticmethod
    async def get_view_stats(session: AsyncSession) -> dict[str, any]:
        """
        Get statistics about materialized views (size, last refresh time, row count).

        Args:
            session: Database session to use for operations

        Returns:
            Dictionary with view statistics.
        """
        stats = {
            "views": [],
            "total_size_bytes": 0,
        }

        try:
            for view_name in MaterializedViewService.VIEWS:
                view_stat = await MaterializedViewService._get_single_view_stat(session, view_name)
                stats["views"].append(view_stat)
                stats["total_size_bytes"] += view_stat.get("size_bytes", 0)

        except Exception as e:
            logger.error(f"Error getting view stats: {str(e)}", exc_info=True)
            stats["error"] = str(e)

        return stats

    @staticmethod
    async def _get_single_view_stat(session: AsyncSession, view_name: str) -> dict[str, any]:
        """
        Get statistics for a single materialized view.

        Args:
            session: Database session
            view_name: Name of the materialized view

        Returns:
            Dictionary with view statistics.
        """
        stat = {
            "view_name": view_name,
            "row_count": 0,
            "size_bytes": 0,
            "size_human": "0 B",
        }

        try:
            # Get row count
            count_sql = f"SELECT COUNT(*) as count FROM {view_name}"
            count_result = await session.execute(text(count_sql))
            count_row = count_result.fetchone()
            stat["row_count"] = count_row[0] if count_row else 0

            # Get size
            size_sql = """
                SELECT pg_size_pretty(pg_total_relation_size(:view_name)) as size_human,
                       pg_total_relation_size(:view_name) as size_bytes
            """
            size_result = await session.execute(text(size_sql), {"view_name": view_name})
            size_row = size_result.fetchone()

            if size_row:
                stat["size_human"] = size_row[0]
                stat["size_bytes"] = size_row[1]

            logger.debug(f"View {view_name}: {stat['row_count']} rows, {stat['size_human']}")

        except Exception as e:
            stat["error"] = str(e)
            logger.error(f"Failed to get stats for view {view_name}: {str(e)}")

        return stat

    @staticmethod
    async def verify_views_exist(session: AsyncSession) -> dict[str, bool]:
        """
        Verify that all expected materialized views exist in the database.

        Args:
            session: Database session to use for operations

        Returns:
            Dictionary mapping view names to existence boolean.
        """
        existence = {}

        try:
            sql = """
                SELECT matviewname
                FROM pg_matviews
                WHERE schemaname = 'public'
            """
            result = await session.execute(text(sql))
            existing_views = {row[0] for row in result.fetchall()}

            for view_name in MaterializedViewService.VIEWS:
                existence[view_name] = view_name in existing_views

            logger.info(f"View existence check: {existence}")

        except Exception as e:
            logger.error(f"Error checking view existence: {str(e)}", exc_info=True)
            for view_name in MaterializedViewService.VIEWS:
                existence[view_name] = False

        return existence
