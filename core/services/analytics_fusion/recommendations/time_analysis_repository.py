"""
Time Analysis Repository
========================

Database queries for posting time analytics.
Single Responsibility: Data access only - no business logic.
"""

import json
import logging

from .models.posting_time_models import AnalysisParameters, RawMetricsData

logger = logging.getLogger(__name__)


class TimeAnalysisRepository:
    """
    Repository for time-based analytics database queries.
    Handles all SQL operations related to posting time analysis.
    """

    def __init__(self, db_pool):
        self.db_pool = db_pool

    async def get_posting_time_metrics(self, params: AnalysisParameters) -> RawMetricsData | None:
        """
        Get comprehensive posting time metrics from database.

        Args:
            params: Analysis parameters including channel_id, days, thresholds

        Returns:
            RawMetricsData with best_hours, best_days, daily_performance, total_posts
            None if insufficient data or error
        """
        try:
            logger.info(
                f"⏰ Getting posting time metrics for channel {params.channel_id} (last {params.days} days)"
            )

            async with self.db_pool.acquire() as conn:
                result_raw = await conn.fetchval(
                    self._get_posting_time_query(),
                    params.channel_id,
                    params.days,
                    params.min_posts_per_hour,
                    params.min_posts_per_day,
                )

                if not result_raw:
                    logger.warning(f"No data returned for channel {params.channel_id}")
                    return None

                # Parse JSON result from PostgreSQL
                result = json.loads(result_raw)

                return RawMetricsData(
                    best_hours=result.get("best_hours", []),
                    best_days=result.get("best_days", []),
                    daily_performance=result.get("daily_performance", []),
                    total_posts_analyzed=result.get("total_posts_analyzed", 0),
                )

        except Exception as e:
            logger.error(
                f"Failed to get posting time metrics for channel {params.channel_id}: {e}",
                exc_info=True,
            )
            return None

    def _get_posting_time_query(self) -> str:
        """
        Complex PostgreSQL query for posting time analysis.
        Separated from business logic for maintainability.
        """
        return """
            WITH post_times AS (
                SELECT
                    p.msg_id,
                    p.date as post_time,
                    EXTRACT(HOUR FROM p.date) as hour,
                    EXTRACT(DOW FROM p.date) as day_of_week,
                    COALESCE(MAX(pm.views), 0) as views,
                    COALESCE(MAX(pm.forwards), 0) as forwards,
                    COALESCE(MAX(pm.reactions_count), 0) as reactions,
                    COALESCE(MAX(pm.replies_count), 0) as replies
                FROM posts p
                LEFT JOIN post_metrics pm ON p.channel_id = pm.channel_id
                    AND p.msg_id = pm.msg_id
                WHERE p.channel_id = $1
                    AND p.date >= NOW() - INTERVAL '1 day' * $2
                    AND p.is_deleted = FALSE
                GROUP BY p.msg_id, p.date
            ),
            hourly_stats AS (
                SELECT
                    hour,
                    COUNT(*) as post_count,
                    AVG(views) as avg_views,
                    AVG(forwards + reactions + replies) as avg_engagement,
                    CASE
                        WHEN AVG(views) > 0 THEN (AVG(forwards + reactions + replies) / AVG(views)) * 100
                        ELSE 0
                    END as engagement_rate
                FROM post_times
                WHERE views > 0
                GROUP BY hour
                HAVING COUNT(*) >= $3
            ),
            daily_stats AS (
                SELECT
                    day_of_week,
                    COUNT(*) as post_count,
                    AVG(views) as avg_views,
                    AVG(forwards + reactions + replies) as avg_engagement,
                    CASE
                        WHEN AVG(views) > 0 THEN (AVG(forwards + reactions + replies) / AVG(views)) * 100
                        ELSE 0
                    END as engagement_rate
                FROM post_times
                WHERE views > 0
                GROUP BY day_of_week
                HAVING COUNT(*) >= $4
            ),
            daily_performance AS (
                SELECT
                    EXTRACT(DAY FROM post_time)::int as date,
                    EXTRACT(DOW FROM post_time)::int as day_of_week,
                    EXTRACT(MONTH FROM post_time)::int as month,
                    EXTRACT(YEAR FROM post_time)::int as year,
                    COUNT(*) as post_count,
                    AVG(forwards + reactions + replies) as avg_engagement
                FROM post_times
                WHERE views > 0
                    AND post_time >= DATE_TRUNC('month', (SELECT MAX(post_time) FROM post_times)) - INTERVAL '30 days'
                GROUP BY EXTRACT(DAY FROM post_time), EXTRACT(DOW FROM post_time),
                         EXTRACT(MONTH FROM post_time), EXTRACT(YEAR FROM post_time)
            )
            SELECT
                json_build_object(
                    'best_hours', (
                        SELECT json_agg(row_to_json(t))
                        FROM (
                            SELECT
                                hour::int,
                                ROUND(engagement_rate::numeric, 2) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                post_count::int
                            FROM hourly_stats
                            ORDER BY engagement_rate DESC
                            LIMIT 5
                        ) t
                    ),
                    'best_days', (
                        SELECT json_agg(row_to_json(d))
                        FROM (
                            SELECT
                                day_of_week::int as day,
                                ROUND(engagement_rate::numeric, 2) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                post_count::int
                            FROM daily_stats
                            ORDER BY engagement_rate DESC
                            LIMIT 3
                        ) d
                    ),
                    'daily_performance', (
                        SELECT json_agg(row_to_json(dp))
                        FROM (
                            SELECT
                                date::int,
                                day_of_week::int,
                                post_count::int,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement
                            FROM daily_performance
                            ORDER BY date
                        ) dp
                    ),
                    'total_posts_analyzed', (
                        SELECT COUNT(*) FROM post_times WHERE views > 0
                    )
                ) as analysis
        """
