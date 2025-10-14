"""
Post Dynamics Analytics Router
Handles post view dynamics and time-series analytics for posts
"""

import logging
from datetime import datetime, timedelta
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from apps.api.di_analytics import get_analytics_fusion_service, get_cache
from core.protocols import AnalyticsFusionServiceProtocol

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics-post-dynamics"])


# Optional auth helper
async def get_optional_user(request: Request) -> dict | None:
    """Get current user if authenticated, None otherwise"""
    try:
        from apps.api.middleware.auth import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

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


class PostDynamicsResponse(BaseModel):
    """Response model for post dynamics endpoint"""
    channel_id: str
    period: str
    data: List[PostDynamicsPoint]
    total_points: int
    period_start: datetime
    period_end: datetime


def parse_period(period: str) -> tuple[datetime, datetime]:
    """Parse period string (e.g., '24h', '7d', '30d') to datetime range"""
    now = datetime.utcnow()

    period_map = {
        '1h': timedelta(hours=1),
        '6h': timedelta(hours=6),
        '12h': timedelta(hours=12),
        '24h': timedelta(hours=24),
        '7d': timedelta(days=7),
        '30d': timedelta(days=30),
    }

    delta = period_map.get(period, timedelta(hours=24))
    from_date = now - delta

    return from_date, now


@router.get("/post-dynamics/{channel_id}", response_model=List[PostDynamicsPoint])
async def get_post_dynamics(
    channel_id: str,
    request: Request,
    period: str = Query(default="24h", regex="^(1h|6h|12h|24h|7d|30d)$"),
    service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 📊 Post View Dynamics

    Get time-series data for post views, engagement, and interactions over a specified period.

    **Parameters:**
    - `channel_id`: Channel identifier (can be numeric ID or string identifier)
    - `period`: Time period for analysis (1h, 6h, 12h, 24h, 7d, 30d)

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
        logger.info(f"Fetching post dynamics for channel {channel_id}, period {period}")

        # Parse period to date range
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

        # For demo/development: Generate mock data
        # In production, this would query the database
        data_points = []

        # Convert channel_id to int if possible
        try:
            channel_id_int = int(channel_id)
        except (ValueError, TypeError):
            # Use demo channel if invalid
            channel_id_int = 0

        # Determine number of points based on period
        period_hours = {
            '1h': 1, '6h': 6, '12h': 12, '24h': 24,
            '7d': 24 * 7, '30d': 24 * 30
        }
        total_hours = period_hours.get(period, 24)

        # Generate data points (one per hour for simplicity)
        num_points = min(total_hours, 100)  # Cap at 100 points
        interval_hours = total_hours / num_points

        import random
        base_views = 1000
        base_likes = 80
        base_shares = 30
        base_comments = 15

        for i in range(num_points):
            point_time = from_date + timedelta(hours=i * interval_hours)

            # Add some variance to make it realistic
            variance = random.uniform(0.7, 1.3)
            trend = 1 + (i / num_points) * 0.2  # Slight upward trend

            data_point = PostDynamicsPoint(
                timestamp=point_time,
                time=point_time.strftime("%H:%M"),
                views=int(base_views * variance * trend),
                likes=int(base_likes * variance * trend),
                shares=int(base_shares * variance * trend),
                comments=int(base_comments * variance * trend),
            )
            data_points.append(data_point)

        # Convert to dict for response
        response_data = [point.model_dump() for point in data_points]

        # Cache for 5 minutes
        await cache.set_json(cache_key, response_data, ttl_s=300)

        logger.info(f"Generated {len(data_points)} post dynamics points for channel {channel_id}")
        return response_data

    except Exception as e:
        logger.error(f"Post dynamics fetch failed for channel {channel_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch post dynamics: {str(e)}"
        )


@router.get("/top-posts/{channel_id}")
async def get_top_posts(
    channel_id: str,
    request: Request,
    period: str = Query(default="today", regex="^(today|week|month)$"),
    sortBy: str = Query(default="views", regex="^(views|likes|shares|comments)$"),
    service: AnalyticsFusionServiceProtocol = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    ## 🏆 Top Performing Posts

    Get the top performing posts for a channel based on selected metric.

    **Parameters:**
    - `channel_id`: Channel identifier
    - `period`: Time period (today, week, month)
    - `sortBy`: Sort metric (views, likes, shares, comments)

    **Returns:**
    - Array of top posts with performance metrics
    """
    try:
        # Generate cache key
        cache_params = {
            "channel_id": channel_id,
            "period": period,
            "sortBy": sortBy,
        }
        cache_key = cache.generate_cache_key("top_posts", cache_params)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            return cached_data

        # Generate mock top posts data
        import random

        posts = []
        for i in range(10):
            post = {
                "id": f"post_{i+1}",
                "title": f"Post Title {i+1}",
                "views": random.randint(500, 5000),
                "likes": random.randint(50, 500),
                "shares": random.randint(10, 100),
                "comments": random.randint(5, 50),
                "published_at": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
            }
            posts.append(post)

        # Sort by selected metric
        posts.sort(key=lambda x: x[sortBy], reverse=True)

        response_data = {
            "posts": posts,
            "period": period,
            "sortBy": sortBy,
            "total": len(posts),
        }

        # Cache for 10 minutes
        await cache.set_json(cache_key, response_data, ttl_s=600)

        return response_data

    except Exception as e:
        logger.error(f"Top posts fetch failed for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch top posts: {str(e)}"
        )
