"""
Channel status and statistics endpoints.

Handles: Get channel status, get channels statistics overview.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

logger = logging.getLogger(__name__)

from apps.api.middleware.auth import get_current_user, require_channel_access
from apps.api.routers.channels.deps import get_channel_management_service
from apps.api.services.channel_management_service import ChannelManagementService
from apps.shared.performance import performance_timer

router = APIRouter()


@router.get("/{channel_id}/status")
async def get_channel_status(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 📊 Get Channel Status

    Get the current status and basic statistics of a channel.

    **Parameters:**
    - channel_id: Target channel ID

    **Returns:**
    - Channel status information
    """
    try:
        await require_channel_access(channel_id, current_user["id"])

        with performance_timer("channel_status_fetch"):
            status_info = await channel_service.get_channel_status(channel_id)

            return {
                "channel_id": channel_id,
                "is_active": status_info.get("is_active", False),
                "last_update": status_info.get("last_update"),
                "subscriber_count": status_info.get("subscriber_count", 0),
                "total_posts": status_info.get("total_posts", 0),
                "analytics_enabled": status_info.get("analytics_enabled", False),
                "connection_status": status_info.get("connection_status", "unknown"),
                "last_sync": status_info.get("last_sync"),
                "checked_at": datetime.now().isoformat(),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel status fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch channel status")


@router.get("/statistics/overview")
async def get_channels_statistics_overview(
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 📊 Get Channels Statistics Overview

    Get aggregate statistics for all user's channels plus individual channel stats.

    **Returns:**
    - Aggregate statistics (total subscribers, posts, views across all channels)
    - Per-channel statistics with detailed metrics
    """
    try:
        user_id = current_user["id"]

        with performance_timer("channels_statistics_overview"):
            # Get user's channels
            channels = await channel_service.get_user_channels(user_id=user_id)

            if not channels:
                return {
                    "aggregate": {
                        "total_channels": 0,
                        "total_subscribers": 0,
                        "total_posts": 0,
                        "total_views": 0,
                        "active_channels": 0,
                    },
                    "channels": [],
                }

            # Get database pool for stats queries
            from apps.di import get_container

            container = get_container()
            pool = await container.database.asyncpg_pool()

            channel_stats_list = []
            total_subscribers = 0
            total_posts = 0
            total_views = 0
            active_channels = 0

            async with pool.acquire() as conn:
                for channel in channels:
                    # Get post count and views for this channel
                    # Check both positive and negative ID formats for compatibility
                    channel_id = abs(channel.id)  # Normalize to positive
                    stats = await conn.fetchrow(
                        """
                        SELECT
                            COUNT(DISTINCT p.msg_id) as post_count,
                            COALESCE(SUM(latest_metrics.views), 0)::bigint as total_views,
                            MAX(p.date) as latest_post_date
                        FROM posts p
                        LEFT JOIN LATERAL (
                            SELECT views
                            FROM post_metrics
                            WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                            ORDER BY snapshot_time DESC
                            LIMIT 1
                        ) latest_metrics ON true
                        WHERE (p.channel_id = $1 OR p.channel_id = $2) AND p.is_deleted = FALSE
                        """,
                        channel_id,
                        -channel_id,
                    )

                    post_count = stats["post_count"] or 0
                    views_count = stats["total_views"] or 0
                    latest_post = stats["latest_post_date"]

                    # Count as active if has posts
                    if channel.is_active and post_count > 0:
                        active_channels += 1

                    # Aggregate totals
                    total_subscribers += channel.subscriber_count
                    total_posts += post_count
                    total_views += views_count

                    # Add to per-channel stats
                    channel_stats_list.append(
                        {
                            "id": channel.id,
                            "name": channel.name,
                            "username": getattr(channel, "username", None),
                            "subscriber_count": channel.subscriber_count,
                            "post_count": post_count,
                            "total_views": views_count,
                            "avg_views_per_post": (
                                round(views_count / post_count) if post_count > 0 else 0
                            ),
                            "latest_post_date": (latest_post.isoformat() if latest_post else None),
                            "is_active": channel.is_active,
                            "created_at": channel.created_at.isoformat(),
                        }
                    )

            return {
                "aggregate": {
                    "total_channels": len(channels),
                    "total_subscribers": total_subscribers,
                    "total_posts": total_posts,
                    "total_views": total_views,
                    "active_channels": active_channels,
                    "avg_views_per_post": (
                        round(total_views / total_posts) if total_posts > 0 else 0
                    ),
                },
                "channels": sorted(
                    channel_stats_list, key=lambda x: x["total_views"], reverse=True
                ),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel statistics overview failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch channel statistics")
