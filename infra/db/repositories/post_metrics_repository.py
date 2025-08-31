"""
Post Metrics Repository Implementation  
Repository for storing and managing post engagement metrics snapshots
"""

from typing import Any, Optional
from datetime import datetime
import json
import asyncpg


class AsyncpgPostMetricsRepository:
    """Post metrics repository implementation using asyncpg for engagement tracking"""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def add_or_update_snapshot(
        self,
        channel_id: int,
        msg_id: int,
        views: int = 0,
        forwards: int = 0,
        replies_count: int = 0,
        reactions_json: list = None,
        reactions_count: int = 0,
        ts: datetime = None
    ) -> dict[str, Any]:
        """Add or update a metrics snapshot for a post.
        
        Args:
            channel_id: Channel ID
            msg_id: Message ID
            views: Number of views
            forwards: Number of forwards
            replies_count: Number of replies
            reactions_json: List of reaction data
            reactions_count: Total reaction count
            ts: Timestamp for the snapshot
            
        Returns:
            Dictionary with operation result
        """
        reactions_json = reactions_json or []
        ts = ts or datetime.utcnow()
        
        async with self.pool.acquire() as conn:
            # Use UPSERT to handle existing metrics
            await conn.execute(
                """
                INSERT INTO post_metrics (
                    channel_id, msg_id, views, forwards, replies_count,
                    reactions, reactions_count, snapshot_time, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
                ON CONFLICT (channel_id, msg_id, snapshot_time) DO UPDATE SET
                    views = GREATEST(post_metrics.views, EXCLUDED.views),
                    forwards = GREATEST(post_metrics.forwards, EXCLUDED.forwards),
                    replies_count = GREATEST(post_metrics.replies_count, EXCLUDED.replies_count),
                    reactions = EXCLUDED.reactions,
                    reactions_count = EXCLUDED.reactions_count,
                    updated_at = NOW()
                """,
                channel_id, msg_id, views, forwards, replies_count,
                json.dumps(reactions_json), reactions_count, ts
            )
            
            return {"success": True, "channel_id": channel_id, "msg_id": msg_id}

    async def get_post_metrics(
        self, 
        channel_id: int, 
        msg_id: int,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get metrics history for a specific post.
        
        Args:
            channel_id: Channel ID
            msg_id: Message ID
            limit: Maximum snapshots to return
            
        Returns:
            List of metrics snapshots ordered by time
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT * FROM post_metrics 
                WHERE channel_id = $1 AND msg_id = $2
                ORDER BY snapshot_time DESC
                LIMIT $3
                """,
                channel_id, msg_id, limit
            )
            return [dict(record) for record in records]

    async def get_latest_metrics(
        self, 
        channel_id: int, 
        msg_id: int
    ) -> Optional[dict[str, Any]]:
        """Get the latest metrics snapshot for a post.
        
        Args:
            channel_id: Channel ID
            msg_id: Message ID
            
        Returns:
            Latest metrics dictionary or None if not found
        """
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT * FROM post_metrics 
                WHERE channel_id = $1 AND msg_id = $2
                ORDER BY snapshot_time DESC
                LIMIT 1
                """,
                channel_id, msg_id
            )
            return dict(record) if record else None

    async def get_channel_metrics_summary(
        self,
        channel_id: int,
        hours: int = 24
    ) -> dict[str, Any]:
        """Get aggregated metrics summary for a channel.
        
        Args:
            channel_id: Channel ID
            hours: Hours to look back for the summary
            
        Returns:
            Dictionary with aggregated metrics
        """
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT 
                    COUNT(DISTINCT msg_id) as total_posts,
                    AVG(views) as avg_views,
                    SUM(views) as total_views,
                    AVG(forwards) as avg_forwards,
                    SUM(forwards) as total_forwards,
                    AVG(replies_count) as avg_replies,
                    SUM(replies_count) as total_replies,
                    AVG(reactions_count) as avg_reactions,
                    SUM(reactions_count) as total_reactions
                FROM post_metrics 
                WHERE channel_id = $1 
                AND snapshot_time > NOW() - INTERVAL '%s hours'
                """,
                channel_id
            )
            
            if record:
                return {
                    'channel_id': channel_id,
                    'period_hours': hours,
                    'total_posts': record['total_posts'] or 0,
                    'avg_views': float(record['avg_views'] or 0),
                    'total_views': record['total_views'] or 0,
                    'avg_forwards': float(record['avg_forwards'] or 0),
                    'total_forwards': record['total_forwards'] or 0,
                    'avg_replies': float(record['avg_replies'] or 0),
                    'total_replies': record['total_replies'] or 0,
                    'avg_reactions': float(record['avg_reactions'] or 0),
                    'total_reactions': record['total_reactions'] or 0,
                    'engagement_rate': self._calculate_engagement_rate(
                        record['total_views'] or 0,
                        (record['total_forwards'] or 0) + 
                        (record['total_replies'] or 0) + 
                        (record['total_reactions'] or 0)
                    )
                }
            
            return {
                'channel_id': channel_id,
                'period_hours': hours,
                'total_posts': 0,
                'avg_views': 0.0,
                'total_views': 0,
                'avg_forwards': 0.0,
                'total_forwards': 0,
                'avg_replies': 0.0,
                'total_replies': 0,
                'avg_reactions': 0.0,
                'total_reactions': 0,
                'engagement_rate': 0.0
            }

    async def get_trending_posts(
        self,
        channel_id: int = None,
        hours: int = 24,
        limit: int = 20
    ) -> list[dict[str, Any]]:
        """Get trending posts based on engagement metrics.
        
        Args:
            channel_id: Specific channel ID (None for all channels)
            hours: Hours to look back
            limit: Maximum posts to return
            
        Returns:
            List of trending posts with their metrics
        """
        async with self.pool.acquire() as conn:
            where_clause = "WHERE snapshot_time > NOW() - INTERVAL '%s hours'"
            params = []
            
            if channel_id:
                where_clause += " AND channel_id = $1"
                params.append(channel_id)
            
            query = f"""
                SELECT 
                    channel_id, msg_id,
                    MAX(views) as views,
                    MAX(forwards) as forwards,
                    MAX(replies_count) as replies_count,
                    MAX(reactions_count) as reactions_count,
                    (MAX(forwards) + MAX(replies_count) + MAX(reactions_count)) as total_engagement,
                    MAX(snapshot_time) as latest_snapshot
                FROM post_metrics 
                {where_clause}
                GROUP BY channel_id, msg_id
                ORDER BY total_engagement DESC, views DESC
                LIMIT ${len(params) + 1}
            """
            
            records = await conn.fetch(query, *params, limit)
            return [dict(record) for record in records]

    async def delete_old_snapshots(self, days: int = 30) -> int:
        """Delete old metric snapshots to keep database size manageable.
        
        Args:
            days: Number of days to keep (older snapshots will be deleted)
            
        Returns:
            Number of deleted snapshots
        """
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM post_metrics 
                WHERE snapshot_time < NOW() - INTERVAL '%s days'
                """,
                days
            )
            
            # Extract number from result string like "DELETE 42"
            deleted_count = 0
            if result and result.startswith("DELETE "):
                try:
                    deleted_count = int(result.split(" ")[1])
                except (IndexError, ValueError):
                    pass
                    
            return deleted_count

    def _calculate_engagement_rate(self, views: int, engagements: int) -> float:
        """Calculate engagement rate as percentage.
        
        Args:
            views: Total views
            engagements: Total engagements (forwards + replies + reactions)
            
        Returns:
            Engagement rate as percentage (0.0 to 100.0)
        """
        if views == 0:
            return 0.0
        return (engagements / views) * 100.0
