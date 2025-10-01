"""
Analytics Fusion Service - Core Business Logic
Unifies MTProto ingested metrics with existing analytics data
"""

from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta
from typing import Literal

logger = logging.getLogger(__name__)


class AnalyticsFusionService:
    """Core service for unified analytics combining MTProto and legacy data"""

    def __init__(
        self,
        channel_daily_repo,
        post_repo,
        metrics_repo,
        edges_repo,
        stats_raw_repo=None,
    ):
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

    async def get_growth(
        self, channel_id: int, frm: datetime, to: datetime, window: str = "D"
    ) -> dict:
        """Get growth time series data"""
        try:
            # Get followers/subscribers series data
            followers_data = await self._daily.series_data(channel_id, "followers", frm, to)

            if not followers_data:
                # Try subscribers metric as fallback
                followers_data = await self._daily.series_data(channel_id, "subscribers", frm, to)

            if not followers_data:
                return {"label": "Growth", "points": []}

            # Calculate growth (difference between consecutive points)
            points = []
            prev_value = None

            for data_point in followers_data:
                if prev_value is not None:
                    growth = data_point["value"] - prev_value
                    points.append({"t": data_point["day"].isoformat(), "y": growth})
                prev_value = data_point["value"]

            return {"label": "Growth", "points": points}

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

                points.append({"t": current_date.isoformat(), "y": round(avg_reach, 2)})

                current_date = next_date

            return {"label": "Average Reach", "points": points}

        except Exception as e:
            logger.error(f"Error getting reach for channel {channel_id}: {e}")
            return {"label": "Average Reach", "points": []}

    async def get_top_posts(
        self, channel_id: int, frm: datetime, to: datetime, limit: int = 10
    ) -> list[dict]:
        """Get top performing posts"""
        try:
            rows = await self._posts.top_by_views(channel_id, frm, to, limit)
            return [self._map_post(r) for r in rows]
        except Exception as e:
            logger.error(f"Error getting top posts for channel {channel_id}: {e}")
            return []

    async def get_sources(
        self,
        channel_id: int,
        frm: datetime,
        to: datetime,
        kind: Literal["mention", "forward"],
    ) -> list[dict]:
        """Get traffic sources (mentions/forwards)"""
        try:
            rows = await self._edges.top_edges(channel_id, frm, to, kind)
            return [
                {
                    "src": r.get("src", 0),
                    "dst": r.get("dst", 0),
                    "count": r.get("count", 0),
                }
                for r in rows
            ]
        except Exception as e:
            logger.error(f"Error getting sources for channel {channel_id}: {e}")
            return []

    async def get_trending(
        self,
        channel_id: int,
        frm: datetime,
        to: datetime,
        method: str = "zscore",
        window_hours: int = 48,
    ) -> list[dict]:
        """Get trending posts using statistical analysis"""
        try:
            # Get posts with metrics for the period
            posts = await self._posts.top_by_views(
                channel_id, frm, to, 100
            )  # Get more for analysis

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

    def _calculate_zscore_trending(
        self, posts: list[dict], view_counts: list[int], window_hours: int
    ) -> list[dict]:
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

    def _calculate_ewma_trending(
        self, posts: list[dict], view_counts: list[int], window_hours: int
    ) -> list[dict]:
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

        date_value = record.get("date")
        return {
            "msg_id": record.get("msg_id", 0),
            "date": date_value.isoformat() if date_value is not None else "",
            "views": record.get("views", 0),
            "forwards": record.get("forwards", 0),
            "replies": record.get("replies", 0),
            "reactions": reactions,
            "title": record.get("title", f"Post {record.get('msg_id', 'Unknown')}"),
            "permalink": record.get("permalink", ""),
        }

    async def get_last_updated_at(self, channel_id: int) -> datetime | None:
        """Get the latest update timestamp for cache control"""
        try:
            timestamps = []

            # Check latest post metrics snapshot
            if hasattr(self._metrics, "get_latest_metrics"):
                latest_metric = await self._metrics.get_latest_metrics(
                    channel_id, 0
                )  # Get any metric
                if latest_metric and latest_metric.get("snapshot_time"):
                    timestamps.append(latest_metric["snapshot_time"])

            # Check latest channel_daily entry
            try:
                latest_daily = await self._daily.get_latest_metric(channel_id, "followers")
                if latest_daily and latest_daily.get("day"):
                    # Convert date to datetime for comparison
                    day_datetime = datetime.combine(latest_daily["day"], datetime.min.time())
                    timestamps.append(day_datetime)
            except Exception as e:
                logger.warning(f"Error processing latest daily data for channel {channel_id}: {e}")

            # Check latest stats_raw entry if available
            if self._stats_raw and hasattr(self._stats_raw, "get_stats_summary"):
                try:
                    stats_summary = await self._stats_raw.get_stats_summary(channel_id)
                    if stats_summary and stats_summary.get("latest_fetch"):
                        timestamps.append(stats_summary["latest_fetch"])
                except Exception as e:
                    logger.warning(f"Error getting stats summary for channel {channel_id}: {e}")

            return max(timestamps) if timestamps else None

        except Exception as e:
            logger.error(f"Error getting last updated time for channel {channel_id}: {e}")
            return None

    # CONSOLIDATED PERFORMANCE ANALYTICS METHODS (from PerformanceAnalyticsService)
    def calculate_performance_score(self, metrics: dict) -> int:
        """
        Calculate overall performance score based on multiple metrics
        Consolidated from PerformanceAnalyticsService
        """
        try:
            # Configuration for performance scoring weights
            weights = {
                "growth_rate": 0.3,
                "engagement_rate": 0.4,
                "reach_score": 0.2,
                "consistency": 0.1,
            }

            # Thresholds for normalization
            thresholds = {
                "growth_rate_max": 20,
                "engagement_rate_max": 10,
            }

            # Normalize metrics to 0-100 scale
            growth_score = min(
                100,
                max(
                    0,
                    (metrics.get("growth_rate", 0) / thresholds["growth_rate_max"]) * 100,
                ),
            )
            engagement_score = min(
                100,
                max(
                    0,
                    (metrics.get("engagement_rate", 0) / thresholds["engagement_rate_max"]) * 100,
                ),
            )
            reach_score = metrics.get("reach_score", 0)
            consistency_score = 75.0  # Default good consistency

            # Calculate weighted total score
            total_score = (
                growth_score * weights["growth_rate"]
                + engagement_score * weights["engagement_rate"]
                + reach_score * weights["reach_score"]
                + consistency_score * weights["consistency"]
            )

            return int(min(100, max(0, total_score)))

        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 50  # Default middle score on error

    def analyze_performance_trends(self, historical_metrics: list[dict]) -> dict:
        """
        Analyze performance trends over time
        Consolidated from PerformanceAnalyticsService
        """
        if not historical_metrics:
            return {
                "trend_direction": "unknown",
                "stability": "unknown",
                "recommendation": "Insufficient data for analysis",
            }

        # Calculate trend direction
        scores = [self.calculate_performance_score(metrics) for metrics in historical_metrics]

        if len(scores) < 2:
            trend_direction = "stable"
        else:
            recent_avg = sum(scores[-3:]) / len(scores[-3:])  # Last 3 periods
            earlier_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else scores[0]

            if recent_avg > earlier_avg + 5:
                trend_direction = "improving"
            elif recent_avg < earlier_avg - 5:
                trend_direction = "declining"
            else:
                trend_direction = "stable"

        # Calculate stability (coefficient of variation)
        if len(scores) > 1:
            mean_score = sum(scores) / len(scores)
            variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
            std_dev = variance**0.5
            cv = std_dev / mean_score if mean_score > 0 else 0

            if cv < 0.1:
                stability = "very_stable"
            elif cv < 0.2:
                stability = "stable"
            elif cv < 0.3:
                stability = "moderate"
            else:
                stability = "volatile"
        else:
            stability = "unknown"

        return {
            "trend_direction": trend_direction,
            "stability": stability,
            "current_score": scores[-1] if scores else 0,
            "average_score": sum(scores) / len(scores) if scores else 0,
            "score_range": (
                {"min": min(scores), "max": max(scores)} if scores else {"min": 0, "max": 0}
            ),
        }

    def get_performance_recommendations(self, metrics: dict, score: int) -> list[str]:
        """
        Generate performance improvement recommendations
        Consolidated from PerformanceAnalyticsService
        """
        recommendations = []

        # Score-based recommendations
        if score < 30:
            recommendations.append(
                "Performance is critically low. Consider comprehensive strategy review."
            )
        elif score < 50:
            recommendations.append("Performance needs improvement. Focus on key growth metrics.")
        elif score < 70:
            recommendations.append("Good performance with room for optimization.")
        else:
            recommendations.append("Excellent performance! Maintain current strategies.")

        # Metric-specific recommendations
        growth_rate = metrics.get("growth_rate", 0)
        if growth_rate < 0:
            recommendations.append(
                "Negative growth detected. Review content strategy and engagement tactics."
            )
        elif growth_rate < 2:
            recommendations.append(
                "Low growth rate. Consider increasing posting frequency or content variety."
            )

        engagement_rate = metrics.get("engagement_rate", 0)
        if engagement_rate < 2:
            recommendations.append(
                "Low engagement. Try interactive content like polls, questions, or contests."
            )
        elif engagement_rate < 5:
            recommendations.append(
                "Moderate engagement. Focus on community building and response time."
            )

        reach_score = metrics.get("reach_score", 0)
        if reach_score < 30:
            recommendations.append(
                "Limited reach. Optimize posting times and use relevant hashtags."
            )

        return recommendations

    async def get_live_metrics(self, channel_id: int, hours: int = 6) -> dict:
        """
        Get real-time live metrics for a channel
        Replaces mock data with actual analytics data
        """
        try:
            from datetime import datetime, timedelta

            # Get time range
            now = datetime.now()
            from_time = now - timedelta(hours=hours)

            # Get recent posts and views
            posts_count = await self._posts.count(channel_id, from_time, now)
            total_views = await self._posts.sum_views(channel_id, from_time, now)

            # Get current subscriber count
            current_subs = await self._daily.series_value(channel_id, "followers", now)
            if current_subs is None:
                current_subs = await self._daily.series_value(channel_id, "subscribers", now)

            # Calculate engagement metrics
            avg_views_per_post = (total_views / posts_count) if posts_count > 0 else 0
            engagement_rate = (
                (avg_views_per_post / current_subs * 100)
                if current_subs and current_subs > 0
                else 0
            )

            # Get recent posts for trend analysis
            recent_posts = await self._posts.get_channel_posts(
                channel_id=channel_id, limit=20, start_date=from_time, end_date=now
            )

            # Calculate view trend (comparing last hour with previous)
            one_hour_ago = now - timedelta(hours=1)
            recent_hour_posts = [p for p in recent_posts if p.get("date", now) > one_hour_ago]
            posts_last_hour = len(recent_hour_posts)

            # Calculate trend by comparing recent views to baseline
            view_trend = 0
            if len(recent_posts) >= 2:
                latest_views = recent_posts[0].get("views", 0) if recent_posts else 0
                previous_views = recent_posts[1].get("views", 0) if len(recent_posts) > 1 else 0
                view_trend = latest_views - previous_views

            return {
                "channel_id": channel_id,
                "current_views": total_views,
                "view_trend": view_trend,
                "engagement_rate": round(engagement_rate, 2),
                "posts_last_hour": posts_last_hour,
                "total_posts": posts_count,
                "avg_views_per_post": round(avg_views_per_post, 2),
                "current_subscribers": current_subs,
                "data_freshness": "real-time",
                "source": "analytics_fusion_service",
                "last_updated": now.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting live metrics for channel {channel_id}: {e}")
            # Return minimal fallback data instead of failing
            return {
                "channel_id": channel_id,
                "current_views": 0,
                "view_trend": 0,
                "engagement_rate": 0.0,
                "posts_last_hour": 0,
                "total_posts": 0,
                "avg_views_per_post": 0.0,
                "current_subscribers": None,
                "data_freshness": "error",
                "source": "analytics_fusion_service_fallback",
                "last_updated": datetime.now().isoformat(),
                "error": str(e),
            }

    async def generate_analytical_report(
        self, channel_id: int, report_type: str, days: int
    ) -> dict:
        """
        Generate comprehensive analytical reports using real data
        Replaces mock data with actual analytics
        """
        try:
            from datetime import datetime, timedelta

            # Calculate time range
            now = datetime.now()
            from_date = now - timedelta(days=days)

            if report_type == "growth":
                # Get growth data using existing methods
                growth_data = await self.get_growth(channel_id, from_date, now, interval="day")

                return {
                    "report_type": "growth",
                    "channel_id": channel_id,
                    "period_days": days,
                    "data": growth_data,
                    "summary": {
                        "total_growth": growth_data.get("current_growth", 0),
                        "growth_rate": growth_data.get("growth_rate", 0),
                        "trend": (
                            "improving" if growth_data.get("growth_rate", 0) > 0 else "declining"
                        ),
                    },
                    "generated_at": now.isoformat(),
                    "source": "analytics_fusion_service",
                }

            elif report_type == "reach":
                # Get reach data
                reach_data = await self.get_reach(channel_id, from_date, now)

                return {
                    "report_type": "reach",
                    "channel_id": channel_id,
                    "period_days": days,
                    "data": reach_data,
                    "summary": {
                        "avg_reach": reach_data.get("avg_reach", 0),
                        "total_views": reach_data.get("total_views", 0),
                        "reach_trend": "stable",  # Could be enhanced with trend analysis
                    },
                    "generated_at": now.isoformat(),
                    "source": "analytics_fusion_service",
                }

            elif report_type == "trending":
                # Get trending posts
                trending_data = await self.get_trending(channel_id, from_date, now)

                return {
                    "report_type": "trending",
                    "channel_id": channel_id,
                    "period_days": days,
                    "data": {
                        "trending_posts": trending_data,
                        "total_trending": len(trending_data),
                    },
                    "summary": {
                        "trending_posts_count": len(trending_data),
                        "avg_trend_score": (
                            sum(p.get("trend_score", 0) for p in trending_data) / len(trending_data)
                            if trending_data
                            else 0
                        ),
                    },
                    "generated_at": now.isoformat(),
                    "source": "analytics_fusion_service",
                }

            elif report_type == "comprehensive":
                # Get comprehensive overview
                overview_data = await self.get_overview(channel_id, from_date, now)
                growth_data = await self.get_growth(channel_id, from_date, now)
                reach_data = await self.get_reach(channel_id, from_date, now)
                top_posts = await self.get_top_posts(channel_id, from_date, now, 10)

                return {
                    "report_type": "comprehensive",
                    "channel_id": channel_id,
                    "period_days": days,
                    "data": {
                        "overview": overview_data,
                        "growth": growth_data,
                        "reach": reach_data,
                        "top_posts": top_posts,
                    },
                    "summary": {
                        "total_posts": overview_data.get("posts", 0),
                        "total_views": overview_data.get("views", 0),
                        "avg_engagement": overview_data.get("err", 0),
                        "growth_rate": growth_data.get("growth_rate", 0),
                        "performance_score": self.calculate_performance_score(
                            {
                                "growth_rate": growth_data.get("growth_rate", 0),
                                "engagement_rate": overview_data.get("err", 0),
                                "reach_score": 75,  # Default good reach score
                            }
                        ),
                    },
                    "generated_at": now.isoformat(),
                    "source": "analytics_fusion_service",
                }

            else:
                return {
                    "error": f"Unknown report type: {report_type}",
                    "available_types": ["growth", "reach", "trending", "comprehensive"],
                }

        except Exception as e:
            logger.error(f"Error generating {report_type} report for channel {channel_id}: {e}")
            return {
                "error": f"Failed to generate {report_type} report",
                "channel_id": channel_id,
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "source": "analytics_fusion_service_error",
                "details": str(e),
            }
