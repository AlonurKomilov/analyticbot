"""
Top Posts Analytics Router
Handles top performing posts analytics and rankings
"""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from apps.di.analytics_container import get_analytics_fusion_service, get_cache
from core.protocols import AnalyticsFusionServiceProtocol

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analytics-top-posts"])


class TopPostMetrics(BaseModel):
    """Metrics for a single top performing post"""

    msg_id: int
    date: str
    text: str
    views: int
    forwards: int
    replies_count: int
    reactions_count: int
    engagement_rate: float


class TopPostsSummary(BaseModel):
    """Summary statistics for top posts"""

    total_views: int
    total_forwards: int
    total_reactions: int
    average_engagement_rate: float
    post_count: int


def parse_period(period: str) -> tuple[datetime, datetime]:
    """Parse period string to datetime range"""
    now = datetime.utcnow()

    if period == "all":
        # Go back 10 years to cover all possible data
        from_date = now - timedelta(days=3650)
        return from_date, now

    # Time-based periods
    period_map = {
        "1h": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90),
    }

    delta = period_map.get(period, timedelta(days=30))
    from_date = now - delta

    return from_date, now


@router.get("/top-posts/{channel_id}", response_model=list[TopPostMetrics])
async def get_top_posts(
    channel_id: str,
    request: Request,
    period: str = Query(default="30d", regex="^(1h|6h|24h|7d|30d|90d|all)$"),
    sort_by: str = Query(
        default="views",
        regex="^(views|forwards|replies_count|reactions_count|engagement_rate)$",
    ),
    limit: int = Query(default=10, ge=1, le=50),
    service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 🏆 Top Performing Posts

    Get the top performing posts for a channel based on selected metric.

    **Parameters:**
    - `channel_id`: Channel identifier
    - `period`: Time period (1h, 6h, 24h, 7d, 30d, 90d, all)
    - `sort_by`: Sort metric (views, forwards, replies_count, reactions_count, engagement_rate)
    - `limit`: Number of posts to return (1-50, default 10)

    **Returns:**
    - Array of top posts with performance metrics, sorted by selected metric

    **Performance Optimizations:**
    - Uses LATERAL JOIN for latest metrics (single query)
    - 5-minute cache TTL for balanced freshness
    - Indexes on channel_id, date, is_deleted for fast filtering

    **Example Response:**
    ```json
    [
        {
            "msg_id": 123,
            "date": "2025-10-29T11:07:59+00:00",
            "text": "Post content...",
            "media_type": "photo",
            "views": 751,
            "forwards": 12,
            "replies_count": 5,
            "reactions_count": 23,
            "engagement_rate": 5.33
        }
    ]
    ```
    """
    try:
        logger.info(
            f"📊 Fetching top posts for channel {channel_id}, period={period}, sort_by={sort_by}, limit={limit}"
        )

        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "period": period,
            "sort_by": sort_by,
            "limit": limit,
        }
        cache_key = cache.generate_cache_key("top_posts", cache_params)

        # Try cache first (5 minutes TTL)
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            logger.info(f"✅ Cache hit: returning {len(cached_data)} cached top posts")
            return cached_data

        # Parse period to date range
        from_date, to_date = parse_period(period)

        # Convert channel_id to int for database query
        try:
            channel_id_int = int(channel_id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid channel ID format")

        # Get database pool using container
        from apps.di import get_container

        container = get_container()
        pool = await container.database.asyncpg_pool()

        # OPTIMIZED QUERY: Get top posts with latest metrics
        # Uses LATERAL JOIN to get the most recent metrics snapshot for each post
        # This is much faster than GROUP BY with MAX(snapshot_time)
        query = """
            SELECT
                p.msg_id,
                p.date,
                p.text,
                latest_metrics.views,
                latest_metrics.forwards,
                latest_metrics.replies_count,
                latest_metrics.reactions_count,
                CASE
                    WHEN latest_metrics.views > 0 THEN
                        ((latest_metrics.forwards + latest_metrics.replies_count + latest_metrics.reactions_count)::float / latest_metrics.views * 100)
                    ELSE 0
                END as engagement_rate
            FROM posts p
            LEFT JOIN LATERAL (
                SELECT views, forwards, replies_count, reactions_count
                FROM post_metrics
                WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                ORDER BY snapshot_time DESC
                LIMIT 1
            ) latest_metrics ON true
            WHERE p.channel_id = $1
                AND p.date >= $2
                AND p.date <= $3
                AND p.is_deleted = FALSE
                AND latest_metrics.views IS NOT NULL
            ORDER BY {order_clause} DESC
            LIMIT $4
        """

        # Handle sort column - engagement_rate is computed, others are from metrics
        if sort_by == "engagement_rate":
            order_clause = "engagement_rate"
        else:
            order_clause = f"latest_metrics.{sort_by}"

        # Safely inject sort column (already validated by Query regex)
        safe_query = query.format(order_clause=order_clause)

        async with pool.acquire() as conn:
            records = await conn.fetch(safe_query, channel_id_int, from_date, to_date, limit)

        if not records:
            logger.warning(f"⚠️  No posts found for channel {channel_id} in period {period}")
            return []

        # Convert to response format
        top_posts = []
        for record in records:
            post_data = TopPostMetrics(
                msg_id=record["msg_id"],
                date=record["date"].isoformat() if record["date"] else "",
                text=(record["text"][:200] if record["text"] else ""),  # Truncate for API response
                views=record["views"] or 0,
                forwards=record["forwards"] or 0,
                replies_count=record["replies_count"] or 0,
                reactions_count=record["reactions_count"] or 0,
                engagement_rate=round(
                    (float(record["engagement_rate"]) if record["engagement_rate"] else 0),
                    2,
                ),
            )
            top_posts.append(post_data)

        logger.info(f"✅ Returning {len(top_posts)} top posts for channel {channel_id}")

        # Convert to dict for caching
        response_data = [post.model_dump() for post in top_posts]

        # Cache for 5 minutes
        await cache.set_json(cache_key, response_data, ttl_s=300)

        return top_posts

    except Exception as e:
        logger.error(f"❌ Top posts fetch failed for channel {channel_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch top posts: {str(e)}")


@router.get("/top-posts/{channel_id}/summary", response_model=TopPostsSummary)
async def get_top_posts_summary(
    channel_id: str,
    request: Request,
    period: str = Query(default="30d", regex="^(1h|6h|24h|7d|30d|90d|all)$"),
    service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 📈 Top Posts Summary Statistics

    Get aggregated statistics for top posts in the specified period.

    **Parameters:**
    - `channel_id`: Channel identifier
    - `period`: Time period (1h, 6h, 24h, 7d, 30d, 90d, all)

    **Returns:**
    - Aggregated metrics across all top posts
    """
    try:
        logger.info(f"📊 Fetching top posts summary for channel {channel_id}, period={period}")

        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "period": period,
        }
        cache_key = cache.generate_cache_key("top_posts_summary", cache_params)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            logger.info("✅ Cache hit: returning cached summary")
            return cached_data

        # Parse period to date range
        from_date, to_date = parse_period(period)

        # Convert channel_id to int for database query
        try:
            channel_id_int = int(channel_id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid channel ID format")

        # Get database pool using container
        from apps.di import get_container

        container = get_container()
        pool = await container.database.asyncpg_pool()

        # Query for summary statistics
        query = """
            SELECT
                COUNT(DISTINCT p.msg_id) as post_count,
                COALESCE(SUM(latest_metrics.views), 0)::int as total_views,
                COALESCE(SUM(latest_metrics.forwards), 0)::int as total_forwards,
                COALESCE(SUM(latest_metrics.reactions_count), 0)::int as total_reactions,
                CASE
                    WHEN SUM(latest_metrics.views) > 0 THEN
                        (SUM(latest_metrics.forwards + latest_metrics.replies_count + latest_metrics.reactions_count)::float
                         / SUM(latest_metrics.views) * 100)
                    ELSE 0
                END as avg_engagement_rate
            FROM posts p
            LEFT JOIN LATERAL (
                SELECT views, forwards, replies_count, reactions_count
                FROM post_metrics
                WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                ORDER BY snapshot_time DESC
                LIMIT 1
            ) latest_metrics ON true
            WHERE p.channel_id = $1
                AND p.date >= $2
                AND p.date <= $3
                AND p.is_deleted = FALSE
                AND latest_metrics.views IS NOT NULL
        """

        async with pool.acquire() as conn:
            record = await conn.fetchrow(query, channel_id_int, from_date, to_date)

        if not record or record["post_count"] == 0:
            logger.warning(f"⚠️  No posts found for summary in channel {channel_id}")
            return TopPostsSummary(
                total_views=0,
                total_forwards=0,
                total_reactions=0,
                average_engagement_rate=0.0,
                post_count=0,
            )

        summary = TopPostsSummary(
            total_views=record["total_views"],
            total_forwards=record["total_forwards"],
            total_reactions=record["total_reactions"],
            average_engagement_rate=round(float(record["avg_engagement_rate"]), 2),
            post_count=record["post_count"],
        )

        logger.info(
            f"✅ Returning summary: {summary.post_count} posts, {summary.total_views} total views"
        )

        # Cache for 5 minutes
        await cache.set_json(cache_key, summary.model_dump(), ttl_s=300)

        return summary

    except Exception as e:
        logger.error(f"❌ Summary fetch failed for channel {channel_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary: {str(e)}")
