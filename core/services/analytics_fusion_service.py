"""
Analytics Fusion Service - Core Business Logic
Unifies MTProto ingested metrics with existing analytics data
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional, Literal
import logging
import math

logger = logging.getLogger(__name__)


class AnalyticsFusionService:
    """Core service for unified analytics combining MTProto and legacy data"""
    
    def __init__(self, channel_daily_repo, post_repo, metrics_repo, edges_repo, stats_raw_repo=None):
        self._daily = channel_daily_repo
        self._posts = post_repo
        self._metrics = metrics_repo
        self._edges = edges_repo
        self._stats_raw = stats_raw_repo

    async def get_overview(self, channel_id: int, frm: datetime, to: datetime) -> dict:
        """Get overview analytics combining all data sources"""
        try:
            # Get basic post counts and views
            posts = await self._posts.count(channel_id, frm, to)
            views = await self._posts.sum_views(channel_id, frm, to)
            
            # Get follower/subscriber count from channel_daily
            subs = await self._daily.series_value(channel_id, "followers", to)
            if subs is None:
                # Fallback to subscribers metric
                subs = await self._daily.series_value(channel_id, "subscribers", to)
            
            # Calculate metrics
            avg_reach = (views / posts) if posts > 0 else 0.0
            err = (avg_reach / subs * 100.0) if subs and subs > 0 else None
            
            return {
                "posts": posts,
                "views": views,
                "avg_reach": round(avg_reach, 2),
                "err": round(err, 2) if err is not None else None,
                "followers": subs,
                "period": {"from": frm.isoformat(), "to": to.isoformat()},
            }
        except Exception as e:
            logger.error(f"Error getting overview for channel {channel_id}: {e}")
            # Graceful degradation
            return {
                "posts": 0,
                "views": 0,
                "avg_reach": 0.0,
                "err": None,
                "followers": None,
                "period": {"from": frm.isoformat(), "to": to.isoformat()},
            }

    async def get_growth(self, channel_id: int, frm: datetime, to: datetime, window: str = "D") -> dict:
        """Get growth time series data"""
        try:
            # Get followers/subscribers series data
            followers_data = await self._daily.series_data(channel_id, "followers", frm, to)
            
            if not followers_data:
                # Try subscribers metric as fallback
                followers_data = await self._daily.series_data(channel_id, "subscribers", frm, to)
            
            if not followers_data:
                return {
                    "label": "Growth",
                    "points": []
                }
            
            # Calculate growth (difference between consecutive points)
            points = []
            prev_value = None
            
            for data_point in followers_data:
                if prev_value is not None:
                    growth = data_point["value"] - prev_value
                    points.append({
                        "t": data_point["day"].isoformat(),
                        "y": growth
                    })
                prev_value = data_point["value"]
            
            return {
                "label": "Growth",
                "points": points
            }
            
        except Exception as e:
            logger.error(f"Error getting growth for channel {channel_id}: {e}")
            return {"label": "Growth", "points": []}

    async def get_reach(self, channel_id: int, frm: datetime, to: datetime) -> dict:
        """Get reach time series (average views per post over time)"""
        try:
            # Get daily post counts and view sums
            current_date = frm
            points = []
            
            while current_date <= to:
                next_date = current_date + timedelta(days=1)
                daily_posts = await self._posts.count(channel_id, current_date, next_date)
                daily_views = await self._posts.sum_views(channel_id, current_date, next_date)
                
                avg_reach = (daily_views / daily_posts) if daily_posts > 0 else 0.0
                
                points.append({
                    "t": current_date.isoformat(),
                    "y": round(avg_reach, 2)
                })
                
                current_date = next_date
            
            return {
                "label": "Average Reach",
                "points": points
            }
            
        except Exception as e:
            logger.error(f"Error getting reach for channel {channel_id}: {e}")
            return {"label": "Average Reach", "points": []}

    async def get_top_posts(self, channel_id: int, frm: datetime, to: datetime, limit: int = 10) -> list[dict]:
        """Get top performing posts"""
        try:
            rows = await self._posts.top_by_views(channel_id, frm, to, limit)
            return [self._map_post(r) for r in rows]
        except Exception as e:
            logger.error(f"Error getting top posts for channel {channel_id}: {e}")
            return []

    async def get_sources(self, channel_id: int, frm: datetime, to: datetime, kind: Literal["mention", "forward"]) -> list[dict]:
        """Get traffic sources (mentions/forwards)"""
        try:
            rows = await self._edges.top_edges(channel_id, frm, to, kind)
            return [{"src": r.get("src", 0), "dst": r.get("dst", 0), "count": r.get("count", 0)} for r in rows]
        except Exception as e:
            logger.error(f"Error getting sources for channel {channel_id}: {e}")
            return []

    async def get_trending(
        self, 
        channel_id: int, 
        frm: datetime, 
        to: datetime, 
        method: str = "zscore", 
        window_hours: int = 48
    ) -> list[dict]:
        """Get trending posts using statistical analysis"""
        try:
            # Get posts with metrics for the period
            posts = await self._posts.top_by_views(channel_id, frm, to, 100)  # Get more for analysis
            
            if len(posts) < 3:  # Need minimum posts for statistical analysis
                return posts[:10] if posts else []
            
            # Extract view counts for analysis
            view_counts = [post.get("views", 0) for post in posts]
            
            if method == "zscore":
                trending_posts = self._calculate_zscore_trending(posts, view_counts, window_hours)
            elif method == "ewma":
                trending_posts = self._calculate_ewma_trending(posts, view_counts, window_hours)
            else:
                # Fallback to simple top posts
                trending_posts = posts[:10]
            
            return [self._map_post(post) for post in trending_posts[:10]]
            
        except Exception as e:
            logger.error(f"Error getting trending posts for channel {channel_id}: {e}")
            return []

    def _calculate_zscore_trending(self, posts: list[dict], view_counts: list[int], window_hours: int) -> list[dict]:
        """Calculate trending posts using z-score method"""
        if not view_counts or len(view_counts) < 2:
            return posts
        
        mean_views = sum(view_counts) / len(view_counts)
        variance = sum((x - mean_views) ** 2 for x in view_counts) / len(view_counts)
        std_dev = math.sqrt(variance) if variance > 0 else 1
        
        # Calculate z-scores and filter trending posts
        trending = []
        for i, post in enumerate(posts):
            views = view_counts[i]
            z_score = (views - mean_views) / std_dev
            
            # Consider posts with z-score > 1.5 as trending
            if z_score > 1.5:
                post_copy = post.copy()
                post_copy["trend_score"] = round(z_score, 2)
                trending.append(post_copy)
        
        # Sort by trend score descending
        trending.sort(key=lambda x: x.get("trend_score", 0), reverse=True)
        return trending

    def _calculate_ewma_trending(self, posts: list[dict], view_counts: list[int], window_hours: int) -> list[dict]:
        """Calculate trending posts using EWMA (Exponentially Weighted Moving Average)"""
        if not view_counts or len(view_counts) < 2:
            return posts
        
        # Calculate EWMA with alpha = 0.3 (giving more weight to recent posts)
        alpha = 0.3
        ewma = view_counts[0]
        
        trending = []
        for i, post in enumerate(posts[1:], 1):  # Start from second post
            views = view_counts[i]
            ewma = alpha * views + (1 - alpha) * ewma
            
            # Check if this post significantly exceeds the EWMA
            spike_ratio = views / ewma if ewma > 0 else 0
            
            if spike_ratio > 1.5:  # Post has 50% more views than expected
                post_copy = post.copy()
                post_copy["trend_score"] = round(spike_ratio, 2)
                trending.append(post_copy)
        
        # Sort by trend score descending
        trending.sort(key=lambda x: x.get("trend_score", 0), reverse=True)
        return trending

    def _map_post(self, record: dict) -> dict:
        """Map database record to PostDTO format"""
        reactions = record.get("reactions", {})
        if isinstance(reactions, str):
            import json
            try:
                reactions = json.loads(reactions)
            except (json.JSONDecodeError, TypeError):
                reactions = {}
        
        return {
            "msg_id": record.get("msg_id", 0),
            "date": record.get("date").isoformat() if record.get("date") else "",
            "views": record.get("views", 0),
            "forwards": record.get("forwards", 0),
            "replies": record.get("replies", 0),
            "reactions": reactions,
            "title": record.get("title", f"Post {record.get('msg_id', 'Unknown')}"),
            "permalink": record.get("permalink", "")
        }

    async def get_last_updated_at(self, channel_id: int) -> Optional[datetime]:
        """Get the latest update timestamp for cache control"""
        try:
            timestamps = []
            
            # Check latest post metrics snapshot
            if hasattr(self._metrics, 'get_latest_metrics'):
                latest_metric = await self._metrics.get_latest_metrics(channel_id, 0)  # Get any metric
                if latest_metric and latest_metric.get("snapshot_time"):
                    timestamps.append(latest_metric["snapshot_time"])
            
            # Check latest channel_daily entry
            try:
                latest_daily = await self._daily.get_latest_metric(channel_id, "followers")
                if latest_daily and latest_daily.get("day"):
                    # Convert date to datetime for comparison
                    day_datetime = datetime.combine(latest_daily["day"], datetime.min.time())
                    timestamps.append(day_datetime)
            except:
                pass
            
            # Check latest stats_raw entry if available
            if self._stats_raw and hasattr(self._stats_raw, 'get_stats_summary'):
                try:
                    stats_summary = await self._stats_raw.get_stats_summary(channel_id)
                    if stats_summary and stats_summary.get("latest_fetch"):
                        timestamps.append(stats_summary["latest_fetch"])
                except:
                    pass
            
            return max(timestamps) if timestamps else None
            
        except Exception as e:
            logger.error(f"Error getting last updated time for channel {channel_id}: {e}")
            return None
