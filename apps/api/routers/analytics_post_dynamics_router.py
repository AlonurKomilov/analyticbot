"""
Post Dynamics Analytics Router
Handles post view dynamics and time-series analytics for posts
"""

import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from apps.di.analytics_container import get_analytics_fusion_service, get_cache
from core.protocols import AnalyticsFusionServiceProtocol

logger = logging.getLogger(__name__)

# ✅ FIXED: Removed prefix - now configured in main.py
router = APIRouter(tags=["analytics-post-dynamics"])


# Optional auth helper
async def get_optional_user(request: Request) -> dict | None:
    """Get current user if authenticated, None otherwise"""
    try:
        from fastapi.security import HTTPBearer

        security_scheme = HTTPBearer(auto_error=False)
        credentials = await security_scheme(request)

        if credentials:
            from apps.api.middleware.auth import get_user_repository

            user_repo = await get_user_repository()
            from apps.api.auth_utils import auth_utils

            user = await auth_utils.get_user_from_token(credentials, user_repo)
            return user
    except Exception as e:
        logger.debug(f"Optional auth failed (this is OK): {e}")

    return None


class PostDynamicsPoint(BaseModel):
    """Single data point in post dynamics time series"""

    timestamp: datetime
    time: str
    views: int
    likes: int
    shares: int
    comments: int
    post_count: int = 0  # Number of posts in this time bucket


class PostDynamicsResponse(BaseModel):
    """Response model for post dynamics endpoint"""

    channel_id: str
    period: str
    data: list[PostDynamicsPoint]
    total_points: int
    period_start: datetime
    period_end: datetime


def parse_period(period: str) -> tuple[datetime, datetime]:
    """Parse period string (e.g., '24h', '7d', '30d', '90d', 'all') to datetime range"""
    now = datetime.utcnow()

    # Support "all" for complete history
    if period == "all":
        # Go back 10 years to cover all possible data
        from_date = now - timedelta(days=3650)
        return from_date, now

    period_map = {
        "1h": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "12h": timedelta(hours=12),
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90),
    }

    delta = period_map.get(period, timedelta(hours=24))
    from_date = now - delta

    return from_date, now


@router.get("/post-dynamics/{channel_id}", response_model=list[PostDynamicsPoint])
async def get_post_dynamics(
    channel_id: str,
    request: Request,
    period: str = Query(default="24h", regex="^(1h|6h|12h|24h|7d|30d|90d|all)$"),
    start_date: str | None = Query(
        default=None, description="Custom start date (ISO format: YYYY-MM-DD)"
    ),
    end_date: str | None = Query(
        default=None, description="Custom end date (ISO format: YYYY-MM-DD)"
    ),
    start_time: str | None = Query(
        default=None,
        description="Custom start time for minute drill-down (ISO format: YYYY-MM-DDTHH:MM:SS)",
    ),
    end_time: str | None = Query(
        default=None,
        description="Custom end time for minute drill-down (ISO format: YYYY-MM-DDTHH:MM:SS)",
    ),
    service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 📊 Post View Dynamics

    Get time-series data for post views, engagement, and interactions over a specified period.

    **Parameters:**
    - `channel_id`: Channel identifier (can be numeric ID or string identifier)
    - `period`: Time period for analysis (1h, 6h, 12h, 24h, 7d, 30d, 90d, all)
    - `start_date`: (Optional) Custom start date in ISO format (YYYY-MM-DD) for drilling into specific days
    - `end_date`: (Optional) Custom end date in ISO format (YYYY-MM-DD) for drilling into specific days
    - `start_time`: (Optional) Custom start time for minute-level drill-down (YYYY-MM-DDTHH:MM:SS)
    - `end_time`: (Optional) Custom end time for minute-level drill-down (YYYY-MM-DDTHH:MM:SS)

    **3-Level Drill-Down Feature (like Telegram):**
    - **Level 1**: Days (90d period) → Click day
    - **Level 2**: Hours (specific day) → Click hour
    - **Level 3**: Minutes (specific hour) → See minute-by-minute breakdown

    **Returns:**
    - Array of data points with timestamps and metrics
    - Each point includes: views, likes, shares, comments

    **Example Response:**
    ```json
    [
        {
            "timestamp": "2025-10-14T10:00:00",
            "time": "10:00",
            "views": 1500,
            "likes": 120,
            "shares": 45,
            "comments": 23
        }
    ]
    ```
    """
    try:
        logger.info(
            f"Fetching post dynamics for channel {channel_id}, period {period}, start_date={start_date}, end_date={end_date}, start_time={start_time}, end_time={end_time}"
        )

        # Parse period to date range (or use custom dates/times if provided)
        if start_time and end_time:
            # Minute-level drill-down for specific hour
            from_date = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            to_date = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

            # Ensure timezone-aware (should already be, but safety check)
            if from_date.tzinfo is None:
                from_date = from_date.replace(tzinfo=UTC)
            if to_date.tzinfo is None:
                to_date = to_date.replace(tzinfo=UTC)

            period = "minute_drill_down"
        elif start_date and end_date:
            # Custom date range for day drill-down (hourly breakdown)
            # Parse date and ensure it has timezone (assume UTC if not provided)
            from_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            to_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

            # If parsed as naive datetime, make it timezone-aware (UTC)
            if from_date.tzinfo is None:
                from_date = from_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC)
            if to_date.tzinfo is None:
                to_date = to_date.replace(
                    hour=23, minute=59, second=59, microsecond=999999, tzinfo=UTC
                )
            else:
                # Set to end of the day (23:59:59)
                to_date = to_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            period = "drill_down"
        else:
            from_date, to_date = parse_period(period)

        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
            "period": period,
        }
        cache_key = cache.generate_cache_key("post_dynamics", cache_params)

        # Try cache first (5 minutes TTL for recent data)
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            logger.info(f"Cache hit for post dynamics: {cache_key}")
            return cached_data

        # Get real data from database
        data_points = []

        # Convert channel_id to int
        try:
            channel_id_int = int(channel_id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid channel ID")

        # Get database pool
        from apps.di import get_container

        container = get_container()
        pool = await container.database.asyncpg_pool()

        async with pool.acquire() as conn:
            # Query uses POST DATE for time buckets (when published)
            # but shows LATEST METRICS (most recent views/reactions)
            # This ensures timeline accuracy while showing current engagement

            # Adaptive time granularity - like Telegram:
            # - Short periods (hours): Show hourly breakdown
            # - Single day (24h): Show hourly breakdown
            # - Multi-day (7d, 30d, 90d): Show daily totals
            # - All time: Show daily totals
            # - Drill-down (day): Show hourly for specific date
            # - Minute drill-down (hour): Show minute-by-minute for specific hour
            if period == "minute_drill_down":
                # Minute-by-minute buckets for specific hour drill-down
                trunc_unit = "minute"
                time_format = "HH24:MI"
            elif period in ["1h", "6h", "12h", "24h", "drill_down"]:
                # Hourly buckets for intraday analysis or day drill-down
                trunc_unit = "hour"
                time_format = "HH24:MI"
            else:
                # Daily buckets for multi-day periods
                trunc_unit = "day"
                time_format = "YYYY-MM-DD"

            # OPTIMIZED QUERY: Groups by post.date (when published)
            # Uses LATERAL JOIN to get latest metrics snapshot for each post
            # Shows SUM of views (total engagement) across all posts in time bucket
            query = """
                SELECT
                    date_trunc($1, p.date) as time_bucket,
                    SUM(latest_metrics.views)::int as avg_views,
                    SUM(latest_metrics.forwards)::int as avg_forwards,
                    SUM(latest_metrics.replies_count)::int as avg_replies,
                    SUM(latest_metrics.reactions_count)::int as avg_reactions,
                    COUNT(DISTINCT p.msg_id) as post_count
                FROM posts p
                LEFT JOIN LATERAL (
                    SELECT views, forwards, replies_count, reactions_count
                    FROM post_metrics
                    WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                    ORDER BY snapshot_time DESC
                    LIMIT 1
                ) latest_metrics ON true
                WHERE p.channel_id = $2
                    AND p.date >= $3
                    AND p.date <= $4
                    AND p.is_deleted = FALSE
                GROUP BY time_bucket
                ORDER BY time_bucket ASC
            """

            # Execute query with determined time bucket granularity
            raw_records = await conn.fetch(query, trunc_unit, channel_id_int, from_date, to_date)

            # Fill missing time buckets with zeros for complete timeline
            if trunc_unit == "hour" and period == "drill_down":
                # Fill missing hours for 24-hour day view
                # Convert asyncpg Records to dicts and create lookup by hour
                records_dict = {}
                for record in raw_records:
                    # Get the hour timestamp (asyncpg returns timezone-aware datetime)
                    hour_timestamp = record["time_bucket"]
                    # Create a normalized key (hour only, no minutes/seconds)
                    # Keep timezone info to match with generated hours
                    hour_key = hour_timestamp.replace(minute=0, second=0, microsecond=0)
                    records_dict[hour_key] = {
                        "time_bucket": hour_timestamp,
                        "avg_views": record["avg_views"],
                        "avg_forwards": record["avg_forwards"],
                        "avg_replies": record["avg_replies"],
                        "avg_reactions": record["avg_reactions"],
                        "post_count": record["post_count"],
                    }

                # Generate all 24 hours for the selected date
                # Keep timezone info to prevent naive/aware datetime mixing
                current_hour = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_hour = from_date.replace(hour=23, minute=0, second=0, microsecond=0)

                records = []
                while current_hour <= end_hour:
                    if current_hour in records_dict:
                        # Use existing record with real data
                        records.append(records_dict[current_hour])
                    else:
                        # Create zero-filled record for missing hour
                        records.append(
                            {
                                "time_bucket": current_hour,
                                "avg_views": 0,
                                "avg_forwards": 0,
                                "avg_replies": 0,
                                "avg_reactions": 0,
                                "post_count": 0,
                            }
                        )
                    current_hour += timedelta(hours=1)
            elif trunc_unit == "minute" and period == "minute_drill_down":
                # Fill missing minutes for 60-minute hour view
                # Convert asyncpg Records to dicts and create lookup by minute
                records_dict = {}
                for record in raw_records:
                    # Get the minute timestamp
                    minute_timestamp = record["time_bucket"]
                    # Create a normalized key (minute only, no seconds)
                    minute_key = minute_timestamp.replace(second=0, microsecond=0, tzinfo=None)
                    records_dict[minute_key] = {
                        "time_bucket": minute_timestamp,
                        "avg_views": record["avg_views"],
                        "avg_forwards": record["avg_forwards"],
                        "avg_replies": record["avg_replies"],
                        "avg_reactions": record["avg_reactions"],
                        "post_count": record["post_count"],
                    }

                # Generate all 60 minutes for the selected hour
                # IMPORTANT: Keep timezone info to prevent display confusion
                current_minute = from_date.replace(second=0, microsecond=0)
                end_minute = to_date.replace(second=0, microsecond=0)

                records = []
                while current_minute <= end_minute:
                    # Create normalized key without timezone for lookup
                    minute_key = current_minute.replace(tzinfo=None)
                    if minute_key in records_dict:
                        # Use existing record with real data
                        records.append(records_dict[minute_key])
                    else:
                        # Create zero-filled record for missing minute
                        # Keep timezone info in time_bucket for correct display
                        records.append(
                            {
                                "time_bucket": current_minute,
                                "avg_views": 0,
                                "avg_forwards": 0,
                                "avg_replies": 0,
                                "avg_reactions": 0,
                                "post_count": 0,
                            }
                        )
                    current_minute += timedelta(minutes=1)
            else:
                # For non-drill-down, just use records as-is
                records = [dict(r) for r in raw_records]

            for record in records:
                # Handle both database records (dict-like) and our filled records (dict)
                time_bucket = (
                    record["time_bucket"] if isinstance(record, dict) else record["time_bucket"]
                )

                data_point = PostDynamicsPoint(
                    timestamp=time_bucket,
                    time=time_bucket.strftime(
                        "%H:%M" if trunc_unit in ["hour", "minute"] else "%Y-%m-%d"
                    ),
                    views=record["avg_views"] or 0,
                    likes=record["avg_reactions"] or 0,  # Using reactions as "likes"
                    shares=record["avg_forwards"] or 0,
                    comments=record["avg_replies"] or 0,
                    post_count=record.get("post_count", 0),
                )
                data_points.append(data_point)

        # If no data, return empty array instead of mock data
        if not data_points:
            logger.warning(f"No post metrics found for channel {channel_id} in period {period}")
            return []

        # Convert to dict for response
        response_data = [point.model_dump() for point in data_points]

        # Cache for 5 minutes
        await cache.set_json(cache_key, response_data, ttl_s=300)

        logger.info(f"Generated {len(data_points)} post dynamics points for channel {channel_id}")
        return response_data

    except Exception as e:
        logger.error(f"Post dynamics fetch failed for channel {channel_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch post dynamics: {str(e)}")
