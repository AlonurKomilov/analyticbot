"""
Time Analysis Repository
========================

Database queries for posting time analytics.
Single Responsibility: Data access only - no business logic.
"""

import json
import logging
import os

from core.monitoring import QueryPerformanceLogger

from .models.posting_time_models import AnalysisParameters, RawMetricsData

logger = logging.getLogger(__name__)

# Feature flags for safe deployment
ENABLE_ADVANCED_RECOMMENDATIONS = (
    os.getenv("ENABLE_ADVANCED_RECOMMENDATIONS", "true").lower() == "true"
)
ENABLE_TIME_WEIGHTING = os.getenv("ENABLE_TIME_WEIGHTING", "true").lower() == "true"
ENABLE_CONTENT_TYPE_ANALYSIS = os.getenv("ENABLE_CONTENT_TYPE_ANALYSIS", "true").lower() == "true"


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
            params: Analysis parameters including channel_id, days (None = all-time), thresholds

        Returns:
            RawMetricsData with best_hours, best_days, daily_performance, total_posts
            None if insufficient data or error
        """
        query_name = (
            "advanced_recommendations"
            if ENABLE_ADVANCED_RECOMMENDATIONS
            else "simple_recommendations"
        )
        period_desc = "all-time (up to 10k posts)" if params.days is None else f"{params.days} days"

        with QueryPerformanceLogger(f"get_posting_time_metrics_{query_name}"):
            try:
                logger.info(
                    f"⏰ Getting posting time metrics for channel {params.channel_id} ({period_desc})"
                )
                logger.info(
                    f"🎛️ Feature flags - Advanced: {ENABLE_ADVANCED_RECOMMENDATIONS}, "
                    f"Time-weighting: {ENABLE_TIME_WEIGHTING}, Content-type: {ENABLE_CONTENT_TYPE_ANALYSIS}"
                )

                # Choose query based on feature flags
                if ENABLE_ADVANCED_RECOMMENDATIONS:
                    query = self._get_advanced_posting_time_query(params.days)
                    logger.info("Using ADVANCED query with new features")
                else:
                    query = self._get_simple_posting_time_query(params.days)
                    logger.info("Using SIMPLE query (legacy mode)")

                async with self.db_pool.acquire() as conn:
                    # For all-time query (days=None), we pass a very large number or omit the filter
                    if params.days is None:
                        # All-time: fetch up to 10k most recent posts for performance
                        result_raw = await conn.fetchval(
                            query,
                            params.channel_id,
                            params.min_posts_per_hour,
                            params.min_posts_per_day,
                        )
                    else:
                        # Time-bounded: normal query with days parameter
                        result_raw = await conn.fetchval(
                            query,
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
                        best_day_hour_combinations=result.get("best_day_hour_combinations", [])
                        if ENABLE_ADVANCED_RECOMMENDATIONS
                        else None,
                        content_type_recommendations=result.get("content_type_recommendations", [])
                        if ENABLE_ADVANCED_RECOMMENDATIONS
                        else None,
                        content_type_summary=result.get("content_type_summary")
                        if ENABLE_ADVANCED_RECOMMENDATIONS
                        else None,
                    )

            except Exception as e:
                logger.error(
                    f"Failed to get posting time metrics for channel {params.channel_id}: {e}",
                    exc_info=True,
                )
                return None

    def _get_advanced_posting_time_query(self, days: int | None = None) -> str:
        """
        Advanced PostgreSQL query with new features:
        - Time-weighted engagement calculation
        - Content type detection and analysis
        - Day-hour combination recommendations

        Used when ENABLE_ADVANCED_RECOMMENDATIONS=true

        Args:
            days: Number of days to analyze, or None for all-time (limited to 10k posts)
        """
        # Determine if we should use time weighting
        time_weight_expr = (
            "EXP(-0.05 * EXTRACT(DAY FROM (NOW() - p.date)))" if ENABLE_TIME_WEIGHTING else "1.0"
        )

        # Determine if we should detect content types
        # FIXED: Use actual media type flags from database
        # IMPORTANT: Order matters! Check more specific types first (gif before video, voice before audio)
        content_type_detection = (
            """CASE
                WHEN p.has_gif = TRUE THEN 'gif'
                WHEN p.has_video = TRUE THEN 'video'
                WHEN p.has_photo = TRUE THEN 'image'
                WHEN p.has_voice = TRUE THEN 'voice'
                WHEN p.has_audio = TRUE THEN 'audio'
                WHEN p.has_document = TRUE THEN 'document'
                WHEN p.has_sticker = TRUE THEN 'sticker'
                WHEN p.has_poll = TRUE THEN 'poll'
                WHEN p.has_link = TRUE OR p.text ~ 'https?://' THEN 'link'
                WHEN p.has_media = TRUE THEN 'media'
                ELSE 'text'
            END as content_type,"""
            if ENABLE_CONTENT_TYPE_ANALYSIS
            else ""
        )

        content_type_group = ", p.has_video, p.has_photo, p.has_media, p.text" if ENABLE_CONTENT_TYPE_ANALYSIS else ", p.text"

        # For all-time, use a subquery with LIMIT instead of date filter
        if days is None:
            # All-time: limit to 10k most recent posts
            return f"""
            WITH post_times AS (
                SELECT DISTINCT ON (p.msg_id)
                    p.msg_id,
                    p.date as post_time,
                    EXTRACT(HOUR FROM p.date) as hour,
                    EXTRACT(DOW FROM p.date) as day_of_week,
                    MAX(pm.views) OVER (PARTITION BY p.msg_id) as views,
                    MAX(pm.forwards) OVER (PARTITION BY p.msg_id) as forwards,
                    MAX(pm.reactions_count) OVER (PARTITION BY p.msg_id) as reactions,
                    MAX(pm.replies_count) OVER (PARTITION BY p.msg_id) as replies,
                    -- Raw media flags for content_type_summary (Telegram counts separately)
                    p.has_photo,
                    p.has_video,
                    p.has_voice,
                    p.has_audio,
                    p.has_document,
                    p.has_gif,
                    p.has_link,
                    -- Content type detection (for CASE-based single category)
                    {content_type_detection}
                    -- Post length category
                    CASE
                        WHEN LENGTH(p.text) < 100 THEN 'short'
                        WHEN LENGTH(p.text) < 500 THEN 'medium'
                        ELSE 'long'
                    END as length_category,
                    -- Time-decay weight (recent posts weighted more)
                    {time_weight_expr} as time_weight
                FROM (
                    SELECT * FROM posts
                    WHERE channel_id = $1 AND is_deleted = FALSE
                    ORDER BY date DESC LIMIT 10000
                ) p
                LEFT JOIN post_metrics pm ON p.channel_id = pm.channel_id
                    AND p.msg_id = pm.msg_id
                ORDER BY p.msg_id, pm.views DESC NULLS LAST
            ),
            -- Global average for relative performance calculation
            global_stats AS (
                SELECT 
                    AVG(views) as global_avg_views,
                    AVG(forwards + reactions + replies) as global_avg_engagement,
                    COUNT(*) as total_posts
                FROM post_times
                WHERE views > 0
            ),
            hourly_stats AS (
                SELECT
                    hour,
                    COUNT(*) as post_count,
                    AVG(views) as avg_views,
                    -- Time-weighted engagement (for channels with engagement data)
                    SUM((forwards + reactions + replies) * time_weight) / NULLIF(SUM(time_weight), 0) as avg_engagement,
                    -- NEW: View-based performance score (primary metric)
                    -- Weighted by sample size: reaches 100% confidence at 20+ posts
                    AVG(views) * LEAST(1.0, COUNT(*)::float / 20.0) as view_score,
                    -- NEW: Relative performance vs channel average (percentage above/below)
                    CASE WHEN (SELECT global_avg_views FROM global_stats) > 0
                        THEN ((AVG(views) / (SELECT global_avg_views FROM global_stats)) - 1) * 100
                        ELSE 0
                    END as relative_performance,
                    -- Confidence level: high (30+), medium (15-30), low (<15)
                    CASE 
                        WHEN COUNT(*) >= 30 THEN 'high'
                        WHEN COUNT(*) >= 15 THEN 'medium'
                        ELSE 'low'
                    END as confidence_level
                FROM post_times
                WHERE views > 0
                GROUP BY hour
                HAVING COUNT(*) >= $2
            ),
            -- Day-Hour combination analysis (best times per specific day)
            -- IMPROVED: View-based scoring with relative performance
            day_hour_stats AS (
                SELECT
                    day_of_week,
                    hour,
                    COUNT(*) as post_count,
                    AVG(views) as avg_views,
                    SUM((forwards + reactions + replies) * time_weight) / NULLIF(SUM(time_weight), 0) as avg_engagement,
                    -- NEW: View-based performance score (primary ranking metric)
                    AVG(views) * LEAST(1.0, COUNT(*)::float / 20.0) as view_score,
                    -- NEW: Relative performance vs channel average
                    CASE WHEN (SELECT global_avg_views FROM global_stats) > 0
                        THEN ((AVG(views) / (SELECT global_avg_views FROM global_stats)) - 1) * 100
                        ELSE 0
                    END as relative_performance,
                    -- Confidence level for UI display
                    CASE 
                        WHEN COUNT(*) >= 30 THEN 'high'
                        WHEN COUNT(*) >= 15 THEN 'medium'
                        ELSE 'low'
                    END as confidence_level
                FROM post_times
                WHERE views > 0
                GROUP BY day_of_week, hour
                HAVING COUNT(*) >= 5  -- Minimum 5 posts for statistical significance
            ),
            -- Content type performance analysis
            -- IMPROVED: View-based scoring for content types
            content_type_stats AS (
                SELECT
                    content_type,
                    hour,
                    COUNT(*) as post_count,
                    AVG(views) as avg_views,
                    SUM((forwards + reactions + replies) * time_weight) / NULLIF(SUM(time_weight), 0) as avg_engagement,
                    -- View-based score with sample size weighting
                    AVG(views) * LEAST(1.0, COUNT(*)::float / 15.0) as view_score,
                    -- Relative performance
                    CASE WHEN (SELECT global_avg_views FROM global_stats) > 0
                        THEN ((AVG(views) / (SELECT global_avg_views FROM global_stats)) - 1) * 100
                        ELSE 0
                    END as relative_performance
                FROM post_times
                WHERE views > 0
                GROUP BY content_type, hour
                HAVING COUNT(*) >= 3  -- Minimum 3 posts per content type
            ),
            daily_stats AS (
                SELECT
                    day_of_week,
                    COUNT(*) as post_count,
                    AVG(views) as avg_views,
                    -- Time-weighted engagement
                    SUM((forwards + reactions + replies) * time_weight) / NULLIF(SUM(time_weight), 0) as avg_engagement,
                    -- View-based score
                    AVG(views) * LEAST(1.0, COUNT(*)::float / 20.0) as view_score,
                    -- Relative performance
                    CASE WHEN (SELECT global_avg_views FROM global_stats) > 0
                        THEN ((AVG(views) / (SELECT global_avg_views FROM global_stats)) - 1) * 100
                        ELSE 0
                    END as relative_performance
                FROM post_times
                WHERE views > 0
                GROUP BY day_of_week
                HAVING COUNT(*) >= $3
            ),
            -- Daily performance for calendar heatmap
            -- Returns data for last 60 days to support month navigation
            -- Uses avg_views as primary metric (engagement is often 0)
            daily_performance AS (
                SELECT
                    EXTRACT(DAY FROM post_time)::int as date,
                    EXTRACT(DOW FROM post_time)::int as day_of_week,
                    EXTRACT(MONTH FROM post_time)::int as month,
                    EXTRACT(YEAR FROM post_time)::int as year,
                    COUNT(*) as post_count,
                    AVG(forwards + reactions + replies) as avg_engagement,
                    AVG(views) as avg_views
                FROM post_times
                WHERE views > 0
                    -- Get last 60 days of data for calendar
                    AND post_time >= (SELECT MAX(post_time) FROM post_times) - INTERVAL '60 days'
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
                                -- View-based confidence (normalized 0-100)
                                LEAST(100, ROUND((view_score / NULLIF((SELECT MAX(view_score) FROM hourly_stats), 0) * 100)::numeric, 1)) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views,
                                ROUND(relative_performance::numeric, 1) as relative_performance,
                                confidence_level,
                                post_count::int
                            FROM hourly_stats
                            ORDER BY view_score DESC
                            LIMIT 5
                        ) t
                    ),
                    'best_days', (
                        SELECT json_agg(row_to_json(d))
                        FROM (
                            SELECT
                                day_of_week::int as day,
                                LEAST(100, ROUND((view_score / NULLIF((SELECT MAX(view_score) FROM daily_stats), 0) * 100)::numeric, 1)) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views,
                                ROUND(relative_performance::numeric, 1) as relative_performance,
                                post_count::int
                            FROM daily_stats
                            ORDER BY view_score DESC
                            LIMIT 3
                        ) d
                    ),
                    'daily_performance', (
                        SELECT json_agg(row_to_json(dp) ORDER BY year, month, date)
                        FROM (
                            SELECT
                                date::int,
                                day_of_week::int,
                                month::int,
                                year::int,
                                post_count::int,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views
                            FROM daily_performance
                        ) dp
                    ),
                    'total_posts_analyzed', (
                        SELECT COUNT(*) FROM post_times WHERE views > 0
                    ),
                    'global_avg_views', (
                        SELECT ROUND(global_avg_views::numeric, 1) FROM global_stats
                    ),
                    'best_day_hour_combinations', (
                        SELECT json_agg(row_to_json(dh))
                        FROM (
                            SELECT
                                day_of_week::int as day,
                                hour::int,
                                LEAST(100, ROUND((view_score / NULLIF((SELECT MAX(view_score) FROM day_hour_stats), 0) * 100)::numeric, 1)) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views,
                                ROUND(relative_performance::numeric, 1) as relative_performance,
                                confidence_level,
                                post_count::int
                            FROM day_hour_stats
                            ORDER BY view_score DESC
                            LIMIT 10
                        ) dh
                    ),
                    'content_type_recommendations', (
                        SELECT json_agg(row_to_json(ct))
                        FROM (
                            SELECT
                                content_type,
                                hour::int,
                                LEAST(100, ROUND((view_score / NULLIF((SELECT MAX(view_score) FROM content_type_stats), 0) * 100)::numeric, 1)) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views,
                                ROUND(relative_performance::numeric, 1) as relative_performance,
                                post_count::int
                            FROM content_type_stats
                            ORDER BY view_score DESC
                            LIMIT 15
                        ) ct
                    ),
                    'content_type_summary', (
                        -- Use direct flag counts to match Telegram's separate category counting
                        -- Telegram counts each type separately (a post with photo+link counts in BOTH)
                        SELECT json_build_object(
                            'image', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_photo = TRUE),
                            'video', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_video = TRUE),
                            'voice', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_voice = TRUE),
                            'audio', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_audio = TRUE),
                            'document', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_document = TRUE),
                            'gif', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_gif = TRUE),
                            'link', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_link = TRUE),
                            'text', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE 
                                has_photo = FALSE AND has_video = FALSE AND has_voice = FALSE 
                                AND has_audio = FALSE AND has_document = FALSE AND has_gif = FALSE
                                AND has_link = FALSE)
                        )
                    )
                ) as analysis
        """
        else:
            # Time-bounded: filter by days, parameters: channel_id, days, min_hour, min_day
            return f"""
            WITH post_times AS (
                SELECT DISTINCT ON (p.msg_id)
                    p.msg_id,
                    p.date as post_time,
                    EXTRACT(HOUR FROM p.date) as hour,
                    EXTRACT(DOW FROM p.date) as day_of_week,
                    MAX(pm.views) OVER (PARTITION BY p.msg_id) as views,
                    MAX(pm.forwards) OVER (PARTITION BY p.msg_id) as forwards,
                    MAX(pm.reactions_count) OVER (PARTITION BY p.msg_id) as reactions,
                    MAX(pm.replies_count) OVER (PARTITION BY p.msg_id) as replies,
                    -- Raw media flags for content_type_summary (Telegram counts separately)
                    p.has_photo,
                    p.has_video,
                    p.has_voice,
                    p.has_audio,
                    p.has_document,
                    p.has_gif,
                    p.has_link,
                    -- Content type detection (for CASE-based single category)
                    {content_type_detection}
                    -- Post length category
                    CASE
                        WHEN LENGTH(p.text) < 100 THEN 'short'
                        WHEN LENGTH(p.text) < 500 THEN 'medium'
                        ELSE 'long'
                    END as length_category,
                    -- Time-decay weight (recent posts weighted more)
                    {time_weight_expr} as time_weight
                FROM posts p
                LEFT JOIN post_metrics pm ON p.channel_id = pm.channel_id
                    AND p.msg_id = pm.msg_id
                WHERE p.channel_id = $1
                    AND p.date >= NOW() - INTERVAL '1 day' * $2
                    AND p.is_deleted = FALSE
                ORDER BY p.msg_id, pm.views DESC NULLS LAST
            ),
            -- Global average for relative performance calculation
            global_stats AS (
                SELECT 
                    AVG(views) as global_avg_views,
                    AVG(forwards + reactions + replies) as global_avg_engagement,
                    COUNT(*) as total_posts
                FROM post_times
                WHERE views > 0
            ),
            hourly_stats AS (
                SELECT
                    hour,
                    COUNT(*) as post_count,
                    AVG(views) as avg_views,
                    SUM((forwards + reactions + replies) * time_weight) / NULLIF(SUM(time_weight), 0) as avg_engagement,
                    -- View-based performance score (primary metric)
                    AVG(views) * LEAST(1.0, COUNT(*)::float / 20.0) as view_score,
                    -- Relative performance vs channel average
                    CASE WHEN (SELECT global_avg_views FROM global_stats) > 0
                        THEN ((AVG(views) / (SELECT global_avg_views FROM global_stats)) - 1) * 100
                        ELSE 0
                    END as relative_performance,
                    CASE 
                        WHEN COUNT(*) >= 30 THEN 'high'
                        WHEN COUNT(*) >= 15 THEN 'medium'
                        ELSE 'low'
                    END as confidence_level
                FROM post_times
                WHERE views > 0
                GROUP BY hour
                HAVING COUNT(*) >= $3
            ),
            -- Day-Hour combination analysis with view-based scoring
            day_hour_stats AS (
                SELECT
                    day_of_week,
                    hour,
                    COUNT(*) as post_count,
                    AVG(views) as avg_views,
                    SUM((forwards + reactions + replies) * time_weight) / NULLIF(SUM(time_weight), 0) as avg_engagement,
                    AVG(views) * LEAST(1.0, COUNT(*)::float / 20.0) as view_score,
                    CASE WHEN (SELECT global_avg_views FROM global_stats) > 0
                        THEN ((AVG(views) / (SELECT global_avg_views FROM global_stats)) - 1) * 100
                        ELSE 0
                    END as relative_performance,
                    CASE 
                        WHEN COUNT(*) >= 30 THEN 'high'
                        WHEN COUNT(*) >= 15 THEN 'medium'
                        ELSE 'low'
                    END as confidence_level
                FROM post_times
                WHERE views > 0
                GROUP BY day_of_week, hour
                HAVING COUNT(*) >= 5
            ),
            -- Content type performance with view-based scoring
            content_type_stats AS (
                SELECT
                    content_type,
                    hour,
                    COUNT(*) as post_count,
                    AVG(views) as avg_views,
                    SUM((forwards + reactions + replies) * time_weight) / NULLIF(SUM(time_weight), 0) as avg_engagement,
                    AVG(views) * LEAST(1.0, COUNT(*)::float / 15.0) as view_score,
                    CASE WHEN (SELECT global_avg_views FROM global_stats) > 0
                        THEN ((AVG(views) / (SELECT global_avg_views FROM global_stats)) - 1) * 100
                        ELSE 0
                    END as relative_performance
                FROM post_times
                WHERE views > 0
                GROUP BY content_type, hour
                HAVING COUNT(*) >= 3
            ),
            daily_stats AS (
                SELECT
                    day_of_week,
                    COUNT(*) as post_count,
                    AVG(views) as avg_views,
                    SUM((forwards + reactions + replies) * time_weight) / NULLIF(SUM(time_weight), 0) as avg_engagement,
                    AVG(views) * LEAST(1.0, COUNT(*)::float / 20.0) as view_score,
                    CASE WHEN (SELECT global_avg_views FROM global_stats) > 0
                        THEN ((AVG(views) / (SELECT global_avg_views FROM global_stats)) - 1) * 100
                        ELSE 0
                    END as relative_performance
                FROM post_times
                WHERE views > 0
                GROUP BY day_of_week
                HAVING COUNT(*) >= $4
            ),
            -- Daily performance for calendar heatmap
            daily_performance AS (
                SELECT
                    EXTRACT(DAY FROM post_time)::int as date,
                    EXTRACT(DOW FROM post_time)::int as day_of_week,
                    EXTRACT(MONTH FROM post_time)::int as month,
                    EXTRACT(YEAR FROM post_time)::int as year,
                    COUNT(*) as post_count,
                    AVG(forwards + reactions + replies) as avg_engagement,
                    AVG(views) as avg_views
                FROM post_times
                WHERE views > 0
                    AND post_time >= (SELECT MAX(post_time) FROM post_times) - INTERVAL '60 days'
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
                                -- View-based confidence (normalized 0-100)
                                LEAST(100, ROUND((view_score / NULLIF((SELECT MAX(view_score) FROM hourly_stats), 0) * 100)::numeric, 1)) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views,
                                ROUND(relative_performance::numeric, 1) as relative_performance,
                                confidence_level,
                                post_count::int
                            FROM hourly_stats
                            ORDER BY view_score DESC
                            LIMIT 5
                        ) t
                    ),
                    'best_days', (
                        SELECT json_agg(row_to_json(d))
                        FROM (
                            SELECT
                                day_of_week::int as day,
                                LEAST(100, ROUND((view_score / NULLIF((SELECT MAX(view_score) FROM daily_stats), 0) * 100)::numeric, 1)) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views,
                                ROUND(relative_performance::numeric, 1) as relative_performance,
                                post_count::int
                            FROM daily_stats
                            ORDER BY view_score DESC
                            LIMIT 3
                        ) d
                    ),
                    'daily_performance', (
                        SELECT json_agg(row_to_json(dp) ORDER BY year, month, date)
                        FROM (
                            SELECT
                                date::int,
                                day_of_week::int,
                                month::int,
                                year::int,
                                post_count::int,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views
                            FROM daily_performance
                        ) dp
                    ),
                    'total_posts_analyzed', (
                        SELECT COUNT(*) FROM post_times WHERE views > 0
                    ),
                    'global_avg_views', (
                        SELECT ROUND(global_avg_views::numeric, 1) FROM global_stats
                    ),
                    'best_day_hour_combinations', (
                        SELECT json_agg(row_to_json(dh))
                        FROM (
                            SELECT
                                day_of_week::int as day,
                                hour::int,
                                LEAST(100, ROUND((view_score / NULLIF((SELECT MAX(view_score) FROM day_hour_stats), 0) * 100)::numeric, 1)) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views,
                                ROUND(relative_performance::numeric, 1) as relative_performance,
                                confidence_level,
                                post_count::int
                            FROM day_hour_stats
                            ORDER BY view_score DESC
                            LIMIT 10
                        ) dh
                    ),
                    'content_type_recommendations', (
                        SELECT json_agg(row_to_json(ct))
                        FROM (
                            SELECT
                                content_type,
                                hour::int,
                                LEAST(100, ROUND((view_score / NULLIF((SELECT MAX(view_score) FROM content_type_stats), 0) * 100)::numeric, 1)) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views,
                                ROUND(relative_performance::numeric, 1) as relative_performance,
                                post_count::int
                            FROM content_type_stats
                            ORDER BY view_score DESC
                            LIMIT 15
                        ) ct
                    ),
                    'content_type_summary', (
                        -- Use direct flag counts to match Telegram's separate category counting
                        SELECT json_build_object(
                            'image', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_photo = TRUE),
                            'video', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_video = TRUE),
                            'voice', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_voice = TRUE),
                            'audio', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_audio = TRUE),
                            'document', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_document = TRUE),
                            'gif', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_gif = TRUE),
                            'link', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE has_link = TRUE),
                            'text', (SELECT COUNT(DISTINCT msg_id) FROM post_times WHERE 
                                has_photo = FALSE AND has_video = FALSE AND has_voice = FALSE 
                                AND has_audio = FALSE AND has_document = FALSE AND has_gif = FALSE
                                AND has_link = FALSE)
                        )
                    )
                ) as analysis
        """

    def _get_simple_posting_time_query(self, days: int | None = None) -> str:
        """
        Simple/Legacy PostgreSQL query without advanced features.
        Used when ENABLE_ADVANCED_RECOMMENDATIONS=false for safe fallback.

        This is the original working query without:
        - Time-weighted calculations
        - Content type analysis
        - Day-hour combinations

        Args:
            days: Number of days to analyze, or None for all-time (limited to 10k posts)
        """

        # All-time: limit to 10k most recent posts, parameters: channel_id, min_hour, min_day
        if days is None:
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
                FROM (
                    SELECT * FROM posts
                    WHERE channel_id = $1 AND is_deleted = FALSE
                    ORDER BY date DESC LIMIT 10000
                ) p
                LEFT JOIN post_metrics pm ON p.channel_id = pm.channel_id
                    AND p.msg_id = pm.msg_id
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
                HAVING COUNT(*) >= $2
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
                HAVING COUNT(*) >= $3
            ),
            -- Daily performance for calendar heatmap
            daily_performance AS (
                SELECT
                    EXTRACT(DAY FROM post_time)::int as date,
                    EXTRACT(DOW FROM post_time)::int as day_of_week,
                    EXTRACT(MONTH FROM post_time)::int as month,
                    EXTRACT(YEAR FROM post_time)::int as year,
                    COUNT(*) as post_count,
                    AVG(forwards + reactions + replies) as avg_engagement,
                    AVG(views) as avg_views
                FROM post_times
                WHERE views > 0
                    AND post_time >= (SELECT MAX(post_time) FROM post_times) - INTERVAL '60 days'
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
                                -- View-based confidence (normalized 0-100)
                                LEAST(100, ROUND((view_score / NULLIF((SELECT MAX(view_score) FROM hourly_stats), 0) * 100)::numeric, 1)) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views,
                                ROUND(relative_performance::numeric, 1) as relative_performance,
                                confidence_level,
                                post_count::int
                            FROM hourly_stats
                            ORDER BY view_score DESC
                            LIMIT 5
                        ) t
                    ),
                    'best_days', (
                        SELECT json_agg(row_to_json(d))
                        FROM (
                            SELECT
                                day_of_week::int as day,
                                LEAST(100, ROUND((view_score / NULLIF((SELECT MAX(view_score) FROM daily_stats), 0) * 100)::numeric, 1)) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views,
                                ROUND(relative_performance::numeric, 1) as relative_performance,
                                post_count::int
                            FROM daily_stats
                            ORDER BY view_score DESC
                            LIMIT 3
                        ) d
                    ),
                    'daily_performance', (
                        SELECT json_agg(row_to_json(dp) ORDER BY year, month, date)
                        FROM (
                            SELECT
                                date::int,
                                day_of_week::int,
                                month::int,
                                year::int,
                                post_count::int,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views
                            FROM daily_performance
                        ) dp
                    ),
                    'total_posts_analyzed', (
                        SELECT COUNT(*) FROM post_times WHERE views > 0
                    )
                ) as analysis
        """
        else:
            # Time-bounded: filter by days parameter, parameters: channel_id, days, min_hour, min_day
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
            -- Daily performance for calendar heatmap
            daily_performance AS (
                SELECT
                    EXTRACT(DAY FROM post_time)::int as date,
                    EXTRACT(DOW FROM post_time)::int as day_of_week,
                    EXTRACT(MONTH FROM post_time)::int as month,
                    EXTRACT(YEAR FROM post_time)::int as year,
                    COUNT(*) as post_count,
                    AVG(forwards + reactions + replies) as avg_engagement,
                    AVG(views) as avg_views
                FROM post_times
                WHERE views > 0
                    AND post_time >= (SELECT MAX(post_time) FROM post_times) - INTERVAL '60 days'
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
                                -- View-based confidence (normalized 0-100)
                                LEAST(100, ROUND((view_score / NULLIF((SELECT MAX(view_score) FROM hourly_stats), 0) * 100)::numeric, 1)) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views,
                                ROUND(relative_performance::numeric, 1) as relative_performance,
                                confidence_level,
                                post_count::int
                            FROM hourly_stats
                            ORDER BY view_score DESC
                            LIMIT 5
                        ) t
                    ),
                    'best_days', (
                        SELECT json_agg(row_to_json(d))
                        FROM (
                            SELECT
                                day_of_week::int as day,
                                LEAST(100, ROUND((view_score / NULLIF((SELECT MAX(view_score) FROM daily_stats), 0) * 100)::numeric, 1)) as confidence,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views,
                                ROUND(relative_performance::numeric, 1) as relative_performance,
                                post_count::int
                            FROM daily_stats
                            ORDER BY view_score DESC
                            LIMIT 3
                        ) d
                    ),
                    'daily_performance', (
                        SELECT json_agg(row_to_json(dp) ORDER BY year, month, date)
                        FROM (
                            SELECT
                                date::int,
                                day_of_week::int,
                                month::int,
                                year::int,
                                post_count::int,
                                ROUND(avg_engagement::numeric, 2) as avg_engagement,
                                ROUND(avg_views::numeric, 1) as avg_views
                            FROM daily_performance
                        ) dp
                    ),
                    'total_posts_analyzed', (
                        SELECT COUNT(*) FROM post_times WHERE views > 0
                    )
                ) as analysis
        """
