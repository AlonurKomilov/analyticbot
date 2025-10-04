"""
🚨 Intelligence Service

This service handles all intelligence and monitoring capabilities including:
- Intelligent alert system setup and monitoring
- Real-time metrics and live monitoring
- Competitive intelligence analysis
- Alert baselines and rule creation
- Statistical anomaly detection
- Performance monitoring and notifications

Extracted from AnalyticsFusionService as part of God Object refactoring.
"""

import logging
from datetime import datetime, timedelta

import numpy as np

from core.protocols import (
    ChannelRepositoryProtocol,
    DailyRepositoryProtocol,
    PostsRepositoryProtocol,
)

logger = logging.getLogger(__name__)


class IntelligenceService:
    """
    🚨 Intelligence Service

    Provides intelligent monitoring and analysis including:
    - Alert system setup and monitoring
    - Real-time live metrics
    - Competitive intelligence
    - Anomaly detection
    """

    def __init__(
        self,
        posts_repo: PostsRepositoryProtocol,
        daily_repo: DailyRepositoryProtocol,
        channels_repo: ChannelRepositoryProtocol,
    ):
        self._posts = posts_repo
        self._daily = daily_repo
        self._channels = channels_repo

    async def get_live_metrics(self, channel_id: int, hours: int = 6) -> dict:
        """
        Get real-time live metrics for a channel
        Replaces mock data with actual analytics data
        """
        try:
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
                "avg_views_per_post": round(avg_views_per_post, 2),
                "total_posts": posts_count,
                "current_subscribers": current_subs or 0,
                "time_range_hours": hours,
                "last_updated": now.isoformat(),
                "status": "active" if posts_count > 0 else "inactive",
            }

        except Exception as e:
            logger.error(f"Live metrics retrieval failed for channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def setup_intelligent_alerts(self, channel_id: int, alert_config: dict = None) -> dict:
        """
        🚨 Intelligent Alert System Setup

        Configures AI-powered alerts for:
        - Sudden performance drops/spikes
        - Anomaly detection
        - Growth trajectory changes
        - Engagement pattern shifts
        - Competitive intelligence alerts

        Args:
            channel_id: Target channel ID
            alert_config: Custom alert configuration

        Returns:
            Alert system status and configuration
        """
        try:
            # Default alert configuration
            default_config = {
                "engagement_drop_threshold": 0.3,  # 30% drop triggers alert
                "engagement_spike_threshold": 2.0,  # 200% increase triggers alert
                "anomaly_detection": True,
                "growth_rate_alerts": True,
                "competitor_alerts": False,
                "alert_frequency": "immediate",  # immediate, hourly, daily
                "channels": ["email", "webhook"],  # notification channels
                "severity_levels": ["critical", "warning", "info"],
            }

            # Merge with user config
            config = {**default_config, **(alert_config or {})}

            # Get baseline metrics for alert thresholds
            baseline = await self._establish_alert_baselines(channel_id)

            if not baseline:
                return {
                    "channel_id": channel_id,
                    "status": "insufficient_data",
                    "message": "Need more historical data to establish alert baselines",
                    "recommendation": "Run analytics for at least 7 days before setting up alerts",
                }

            # Create alert rules based on configuration and baseline
            alert_rules = await self._create_alert_rules(channel_id, config, baseline)

            # Initialize monitoring system
            monitoring_status = await self._initialize_alert_monitoring(channel_id, alert_rules)

            return {
                "channel_id": channel_id,
                "status": "configured",
                "alert_rules_count": len(alert_rules),
                "baseline_period": baseline.get("period_days", 7),
                "configuration": config,
                "monitoring_status": monitoring_status,
                "created_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Alert setup failed for channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def check_real_time_alerts(self, channel_id: int) -> dict:
        """
        🔍 Real-time Alert Checking

        Checks current metrics against established alert thresholds
        and triggers notifications for anomalies or significant changes
        """
        try:
            # Get current metrics
            current_metrics = await self._get_current_metrics(channel_id)

            if not current_metrics:
                return {
                    "channel_id": channel_id,
                    "status": "no_data",
                    "alerts": [],
                    "message": "No current metrics available for analysis",
                }

            # Get alert configuration
            alert_config = await self._get_alert_configuration(channel_id)

            if not alert_config:
                return {
                    "channel_id": channel_id,
                    "status": "not_configured",
                    "alerts": [],
                    "message": "Alert system not configured for this channel",
                }

            # Check different types of alerts
            all_alerts = []

            # Engagement alerts
            engagement_alerts = await self._check_engagement_alerts(
                channel_id, current_metrics, alert_config
            )
            all_alerts.extend(engagement_alerts)

            # Growth alerts
            growth_alerts = await self._check_growth_alerts(
                channel_id, current_metrics, alert_config
            )
            all_alerts.extend(growth_alerts)

            # Performance alerts
            performance_alerts = await self._check_performance_alerts(
                channel_id, current_metrics, alert_config
            )
            all_alerts.extend(performance_alerts)

            # Statistical anomaly detection
            anomaly_alerts = await self._check_statistical_anomalies(
                channel_id, current_metrics, alert_config
            )
            all_alerts.extend(anomaly_alerts)

            # Sort alerts by severity
            severity_scores = {"critical": 3, "warning": 2, "info": 1}
            all_alerts.sort(
                key=lambda x: severity_scores.get(x.get("severity", "info"), 0),
                reverse=True,
            )

            # Trigger notifications if there are critical or warning alerts
            if any(alert.get("severity") in ["critical", "warning"] for alert in all_alerts):
                await self._trigger_alert_notifications(channel_id, all_alerts)

            return {
                "channel_id": channel_id,
                "status": "checked",
                "total_alerts": len(all_alerts),
                "critical_alerts": len([a for a in all_alerts if a.get("severity") == "critical"]),
                "warning_alerts": len([a for a in all_alerts if a.get("severity") == "warning"]),
                "alerts": all_alerts,
                "checked_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Real-time alert check failed for channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _get_current_metrics(self, channel_id: int) -> dict:
        """Get current performance metrics for alert comparison"""
        try:
            now = datetime.now()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)

            # Get today's metrics
            daily_views = await self._daily.series_value(channel_id, "views", today)
            daily_followers = await self._daily.series_value(channel_id, "followers", today)
            if daily_followers is None:
                daily_followers = await self._daily.series_value(channel_id, "subscribers", today)

            # Get recent posts for engagement calculation
            recent_posts = await self._posts.get_channel_posts(
                channel_id=channel_id, limit=10, start_date=today, end_date=now
            )

            # Calculate engagement metrics
            total_views = sum(p.get("views", 0) for p in recent_posts)
            total_forwards = sum(p.get("forwards", 0) for p in recent_posts)
            total_replies = sum(p.get("replies", 0) for p in recent_posts)

            engagement_rate = 0
            if total_views > 0:
                engagement_rate = (total_forwards + total_replies) / total_views

            return {
                "daily_views": daily_views or 0,
                "daily_followers": daily_followers or 0,
                "posts_today": len(recent_posts),
                "total_views_today": total_views,
                "engagement_rate": engagement_rate,
                "avg_views_per_post": (total_views / len(recent_posts) if recent_posts else 0),
                "timestamp": now.isoformat(),
            }

        except Exception as e:
            logger.error(f"Current metrics retrieval failed: {e}")
            return {}

    async def _establish_alert_baselines(self, channel_id: int) -> dict:
        """Establish baseline metrics for alert thresholds"""
        try:
            now = datetime.now()
            start_date = now - timedelta(days=14)  # 2 weeks of baseline data

            # Get historical daily metrics
            daily_views = await self._daily.series_data(channel_id, "views", start_date, now)
            daily_followers = await self._daily.series_data(
                channel_id, "followers", start_date, now
            )
            if not daily_followers:
                daily_followers = await self._daily.series_data(
                    channel_id, "subscribers", start_date, now
                )

            if not daily_views or len(daily_views) < 7:
                return {}

            # Calculate baseline statistics
            views_values = [item.get("value", 0) for item in daily_views]
            follower_values = (
                [item.get("value", 0) for item in daily_followers] if daily_followers else []
            )

            # Views baseline
            views_baseline = {
                "mean": np.mean(views_values),
                "std": np.std(views_values),
                "median": np.median(views_values),
                "percentile_75": np.percentile(views_values, 75),
                "percentile_25": np.percentile(views_values, 25),
            }

            # Followers baseline
            followers_baseline = {}
            if follower_values:
                # Calculate growth rates
                growth_rates = []
                for i in range(1, len(follower_values)):
                    if follower_values[i - 1] > 0:
                        rate = (follower_values[i] - follower_values[i - 1]) / follower_values[
                            i - 1
                        ]
                        growth_rates.append(rate)

                followers_baseline = {
                    "mean_growth": np.mean(growth_rates) if growth_rates else 0,
                    "std_growth": np.std(growth_rates) if growth_rates else 0,
                    "current_count": follower_values[-1] if follower_values else 0,
                }

            # Posts baseline
            posts = await self._posts.get_channel_posts(
                channel_id=channel_id, limit=100, start_date=start_date, end_date=now
            )

            posts_per_day = len(posts) / 14  # Average posts per day

            return {
                "period_days": 14,
                "views": views_baseline,
                "followers": followers_baseline,
                "posts_per_day": posts_per_day,
                "total_posts": len(posts),
                "established_at": now.isoformat(),
            }

        except Exception as e:
            logger.error(f"Baseline establishment failed: {e}")
            return {}

    async def _create_alert_rules(self, channel_id: int, config: dict, baseline: dict) -> list:
        """Create specific alert rules based on configuration and baseline metrics"""
        try:
            rules = []

            # Engagement drop alert
            if baseline.get("views"):
                views_baseline = baseline["views"]
                drop_threshold = config.get("engagement_drop_threshold", 0.3)

                rules.append(
                    {
                        "type": "engagement_drop",
                        "metric": "daily_views",
                        "threshold": views_baseline["mean"] * (1 - drop_threshold),
                        "condition": "below",
                        "severity": "warning",
                        "description": f"Daily views dropped below {drop_threshold * 100}% of baseline",
                    }
                )

            # Engagement spike alert
            if baseline.get("views"):
                views_baseline = baseline["views"]
                spike_threshold = config.get("engagement_spike_threshold", 2.0)

                rules.append(
                    {
                        "type": "engagement_spike",
                        "metric": "daily_views",
                        "threshold": views_baseline["mean"] * spike_threshold,
                        "condition": "above",
                        "severity": "info",
                        "description": f"Daily views spiked above {spike_threshold * 100}% of baseline",
                    }
                )

            # Growth rate alerts
            if config.get("growth_rate_alerts") and baseline.get("followers"):
                followers_baseline = baseline["followers"]

                rules.append(
                    {
                        "type": "negative_growth",
                        "metric": "follower_growth",
                        "threshold": followers_baseline.get("mean_growth", 0)
                        - (2 * followers_baseline.get("std_growth", 0)),
                        "condition": "below",
                        "severity": "warning",
                        "description": "Follower growth rate significantly below baseline",
                    }
                )

            # Anomaly detection rule
            if config.get("anomaly_detection"):
                rules.append(
                    {
                        "type": "statistical_anomaly",
                        "metric": "multiple",
                        "threshold": 2.0,  # 2 standard deviations
                        "condition": "statistical",
                        "severity": "warning",
                        "description": "Statistical anomaly detected in metrics",
                    }
                )

            logger.info(f"Created {len(rules)} alert rules for channel {channel_id}")
            return rules

        except Exception as e:
            logger.error(f"Alert rule creation failed: {e}")
            return []

    async def _check_engagement_alerts(
        self, channel_id: int, current_metrics: dict, alert_config: dict
    ) -> list:
        """Check for engagement-related alerts"""
        alerts = []

        try:
            current_views = current_metrics.get("daily_views", 0)
            engagement_rate = current_metrics.get("engagement_rate", 0)

            # Check for engagement drops (placeholder logic)
            alert_config.get("engagement_drop_threshold", 0.3)

            # This would compare against historical baseline
            if current_views < 100:  # Simplified threshold
                alerts.append(
                    {
                        "type": "low_engagement",
                        "severity": "warning",
                        "message": f"Daily views ({current_views}) below expected threshold",
                        "metric": "daily_views",
                        "current_value": current_views,
                        "triggered_at": datetime.now().isoformat(),
                    }
                )

            if engagement_rate < 0.01:  # Less than 1% engagement
                alerts.append(
                    {
                        "type": "low_engagement_rate",
                        "severity": "warning",
                        "message": f"Engagement rate ({engagement_rate:.2%}) is critically low",
                        "metric": "engagement_rate",
                        "current_value": engagement_rate,
                        "triggered_at": datetime.now().isoformat(),
                    }
                )

        except Exception as e:
            logger.error(f"Engagement alerts check failed: {e}")

        return alerts

    async def _check_growth_alerts(
        self, channel_id: int, current_metrics: dict, alert_config: dict
    ) -> list:
        """Check for growth-related alerts"""
        alerts = []

        try:
            current_followers = current_metrics.get("daily_followers", 0)

            # Simplified growth check
            if current_followers > 0:
                # This would compare against baseline growth rates
                # For now, just checking if growth exists
                pass

        except Exception as e:
            logger.error(f"Growth alerts check failed: {e}")

        return alerts

    async def _check_performance_alerts(
        self, channel_id: int, current_metrics: dict, alert_config: dict
    ) -> list:
        """Check for performance-related alerts"""
        alerts = []

        try:
            posts_today = current_metrics.get("posts_today", 0)
            avg_views = current_metrics.get("avg_views_per_post", 0)

            # Check posting frequency
            if posts_today == 0:
                alerts.append(
                    {
                        "type": "no_posts",
                        "severity": "info",
                        "message": "No posts published today",
                        "metric": "posts_today",
                        "current_value": posts_today,
                        "triggered_at": datetime.now().isoformat(),
                    }
                )

            # Check average performance
            if avg_views < 50 and posts_today > 0:  # Simplified threshold
                alerts.append(
                    {
                        "type": "low_performance",
                        "severity": "warning",
                        "message": f"Average views per post ({avg_views:.0f}) below threshold",
                        "metric": "avg_views_per_post",
                        "current_value": avg_views,
                        "triggered_at": datetime.now().isoformat(),
                    }
                )

        except Exception as e:
            logger.error(f"Performance alerts check failed: {e}")

        return alerts

    async def _check_statistical_anomalies(
        self, channel_id: int, current_metrics: dict, alert_config: dict
    ) -> list:
        """Check for statistical anomalies in metrics"""
        alerts = []

        try:
            # This would implement statistical anomaly detection
            # For now, return empty list
            pass

        except Exception as e:
            logger.error(f"Statistical anomaly check failed: {e}")

        return alerts

    async def _get_alert_configuration(self, channel_id: int) -> dict:
        """Get alert configuration for a channel"""
        try:
            # This would retrieve stored configuration
            # For now, return default configuration
            return {
                "engagement_drop_threshold": 0.3,
                "engagement_spike_threshold": 2.0,
                "anomaly_detection": True,
                "growth_rate_alerts": True,
                "alert_frequency": "immediate",
            }
        except Exception as e:
            logger.error(f"Alert configuration retrieval failed: {e}")
            return {}

    async def _initialize_alert_monitoring(self, channel_id: int, alert_rules: list) -> dict:
        """Initialize monitoring system for alerts"""
        try:
            return {
                "status": "active",
                "rules_count": len(alert_rules),
                "initialized_at": datetime.now().isoformat(),
                "next_check": (datetime.now() + timedelta(hours=1)).isoformat(),
            }
        except Exception as e:
            logger.error(f"Alert monitoring initialization failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _trigger_alert_notifications(self, channel_id: int, alerts: list) -> bool:
        """Trigger notifications for alerts"""
        try:
            # This would send notifications via configured channels
            # For now, just log the alerts
            for alert in alerts:
                logger.warning(
                    f"ALERT for channel {channel_id}: {alert.get('message', 'Unknown alert')}"
                )

            return True
        except Exception as e:
            logger.error(f"Alert notification failed: {e}")
            return False

    async def generate_competitive_intelligence(
        self,
        channel_id: int,
        competitor_ids: list = None,
        analysis_depth: str = "standard",
    ) -> dict:
        """
        🎯 Competitive Intelligence Analysis

        Analyzes competitive landscape and provides strategic insights:
        - Market position analysis
        - Performance benchmarking
        - Content strategy comparison
        - Growth trajectory analysis
        - Opportunity identification
        """
        try:
            # Discover competitors if not provided
            if not competitor_ids:
                competitor_ids = await self._discover_competitor_channels(
                    channel_id, max_competitors=5
                )

            if not competitor_ids:
                return {
                    "channel_id": channel_id,
                    "status": "no_competitors",
                    "message": "No competitor channels found for analysis",
                    "recommendations": ["Manual competitor identification required"],
                }

            # Gather competitive data
            all_data = await self._gather_competitive_data([channel_id] + competitor_ids)

            if not all_data or len(all_data) < 2:
                return {
                    "channel_id": channel_id,
                    "status": "insufficient_data",
                    "message": "Insufficient competitive data for analysis",
                }

            # Perform competitive analysis
            analysis = {
                "market_position": await self._analyze_market_position(channel_id, all_data),
                "performance_comparison": await self._compare_performance_metrics(
                    channel_id, all_data
                ),
                "content_analysis": await self._analyze_competitive_content(channel_id, all_data),
                "growth_comparison": await self._compare_growth_trajectories(channel_id, all_data),
            }

            # Identify opportunities
            opportunities = await self._identify_market_opportunities(
                channel_id, all_data, analysis
            )

            # Generate recommendations
            recommendations = await self._generate_competitive_recommendations(channel_id, analysis)

            return {
                "channel_id": channel_id,
                "competitor_count": len(competitor_ids),
                "analysis_depth": analysis_depth,
                "market_analysis": analysis,
                "opportunities": opportunities,
                "recommendations": recommendations,
                "competitive_score": analysis.get("market_position", {}).get("overall_score", 0.5),
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Competitive intelligence generation failed: {e}")
            return {
                "channel_id": channel_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _discover_competitor_channels(
        self, channel_id: int, max_competitors: int = 5
    ) -> list:
        """Discover competitor channels based on similar metrics and content"""
        try:
            # This would implement competitor discovery logic
            # For now, return empty list (competitors would need to be manually specified)
            return []
        except Exception as e:
            logger.error(f"Competitor discovery failed: {e}")
            return []

    async def _get_channel_profile(self, channel_id: int) -> dict:
        """Get comprehensive channel profile for competitive analysis"""
        try:
            now = datetime.now()
            start_date = now - timedelta(days=30)

            # Get channel metrics
            posts = await self._posts.get_channel_posts(
                channel_id=channel_id, limit=50, start_date=start_date, end_date=now
            )

            # Get follower data
            followers = await self._daily.series_value(channel_id, "followers", now)
            if followers is None:
                followers = await self._daily.series_value(channel_id, "subscribers", now)

            # Calculate profile metrics
            total_views = sum(p.get("views", 0) for p in posts)
            total_forwards = sum(p.get("forwards", 0) for p in posts)
            avg_views = total_views / len(posts) if posts else 0

            return {
                "channel_id": channel_id,
                "followers": followers or 0,
                "posts_count": len(posts),
                "total_views": total_views,
                "avg_views_per_post": avg_views,
                "engagement_rate": ((total_forwards / total_views) if total_views > 0 else 0),
                "posting_frequency": len(posts) / 30,  # Posts per day
                "profile_date": now.isoformat(),
            }
        except Exception as e:
            logger.error(f"Channel profile creation failed: {e}")
            return {}

    async def _gather_competitive_data(self, channel_ids: list) -> dict:
        """Gather comprehensive data for all channels in competitive analysis"""
        try:
            all_data = {}

            for channel_id in channel_ids:
                profile = await self._get_channel_profile(channel_id)
                if profile:
                    all_data[channel_id] = profile

            return all_data
        except Exception as e:
            logger.error(f"Competitive data gathering failed: {e}")
            return {}

    async def _analyze_market_position(self, channel_id: int, all_data: dict) -> dict:
        """Analyze market position relative to competitors"""
        try:
            if channel_id not in all_data:
                return {"error": "Channel data not available"}

            channel_data = all_data[channel_id]
            competitors = {cid: data for cid, data in all_data.items() if cid != channel_id}

            if not competitors:
                return {"error": "No competitor data available"}

            # Calculate rankings
            all_channels = list(all_data.values())

            # Follower ranking
            follower_rank = (
                len(
                    [
                        c
                        for c in all_channels
                        if c.get("followers", 0) > channel_data.get("followers", 0)
                    ]
                )
                + 1
            )

            # Engagement ranking
            engagement_rank = (
                len(
                    [
                        c
                        for c in all_channels
                        if c.get("engagement_rate", 0) > channel_data.get("engagement_rate", 0)
                    ]
                )
                + 1
            )

            # Views ranking
            views_rank = (
                len(
                    [
                        c
                        for c in all_channels
                        if c.get("avg_views_per_post", 0)
                        > channel_data.get("avg_views_per_post", 0)
                    ]
                )
                + 1
            )

            # Overall score (normalized)
            total_channels = len(all_channels)
            overall_score = 1 - (
                (follower_rank + engagement_rank + views_rank) / (3 * total_channels)
            )

            return {
                "follower_rank": follower_rank,
                "engagement_rank": engagement_rank,
                "views_rank": views_rank,
                "total_competitors": len(competitors),
                "overall_score": round(overall_score, 3),
                "market_position": (
                    "leader"
                    if overall_score > 0.7
                    else "competitive"
                    if overall_score > 0.4
                    else "challenger"
                ),
            }
        except Exception as e:
            logger.error(f"Market position analysis failed: {e}")
            return {"error": str(e)}

    async def _compare_performance_metrics(self, channel_id: int, all_data: dict) -> dict:
        """Compare performance metrics against competitors"""
        try:
            if channel_id not in all_data:
                return {"error": "Channel data not available"}

            channel_data = all_data[channel_id]
            competitors = [data for cid, data in all_data.items() if cid != channel_id]

            if not competitors:
                return {"error": "No competitor data available"}

            # Calculate competitor averages
            competitor_followers = [c.get("followers", 0) for c in competitors]
            competitor_engagement = [c.get("engagement_rate", 0) for c in competitors]
            competitor_views = [c.get("avg_views_per_post", 0) for c in competitors]

            avg_competitor_followers = np.mean(competitor_followers) if competitor_followers else 0
            avg_competitor_engagement = (
                np.mean(competitor_engagement) if competitor_engagement else 0
            )
            avg_competitor_views = np.mean(competitor_views) if competitor_views else 0

            # Calculate performance ratios
            follower_ratio = (
                (channel_data.get("followers", 0) / avg_competitor_followers)
                if avg_competitor_followers > 0
                else 0
            )
            engagement_ratio = (
                (channel_data.get("engagement_rate", 0) / avg_competitor_engagement)
                if avg_competitor_engagement > 0
                else 0
            )
            views_ratio = (
                (channel_data.get("avg_views_per_post", 0) / avg_competitor_views)
                if avg_competitor_views > 0
                else 0
            )

            return {
                "follower_performance": {
                    "channel_value": channel_data.get("followers", 0),
                    "competitor_average": round(avg_competitor_followers, 0),
                    "performance_ratio": round(follower_ratio, 2),
                    "status": ("above_average" if follower_ratio > 1 else "below_average"),
                },
                "engagement_performance": {
                    "channel_value": round(channel_data.get("engagement_rate", 0), 4),
                    "competitor_average": round(avg_competitor_engagement, 4),
                    "performance_ratio": round(engagement_ratio, 2),
                    "status": ("above_average" if engagement_ratio > 1 else "below_average"),
                },
                "views_performance": {
                    "channel_value": round(channel_data.get("avg_views_per_post", 0), 0),
                    "competitor_average": round(avg_competitor_views, 0),
                    "performance_ratio": round(views_ratio, 2),
                    "status": "above_average" if views_ratio > 1 else "below_average",
                },
            }
        except Exception as e:
            logger.error(f"Performance comparison failed: {e}")
            return {"error": str(e)}

    async def _analyze_competitive_content(self, channel_id: int, all_data: dict) -> dict:
        """Analyze content strategy compared to competitors"""
        try:
            # This would implement content analysis
            # For now, return placeholder analysis
            return {
                "posting_frequency": {
                    "channel_frequency": all_data.get(channel_id, {}).get("posting_frequency", 0),
                    "competitor_average": 0.5,
                    "recommendation": "increase_frequency",
                },
                "content_themes": [],
                "optimal_timing": {},
                "content_gaps": [],
            }
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return {"error": str(e)}

    async def _compare_growth_trajectories(self, channel_id: int, all_data: dict) -> dict:
        """Compare growth trajectories with competitors"""
        try:
            # This would implement growth comparison
            # For now, return placeholder analysis
            return {
                "growth_rate": 0.05,
                "competitor_average_growth": 0.03,
                "growth_rank": 1,
                "trajectory": "positive",
            }
        except Exception as e:
            logger.error(f"Growth comparison failed: {e}")
            return {"error": str(e)}

    async def _identify_market_opportunities(
        self, channel_id: int, all_data: dict, analysis: dict
    ) -> list:
        """Identify market opportunities based on competitive analysis"""
        try:
            opportunities = []

            # Example opportunity identification
            performance = analysis.get("performance_comparison", {})

            if performance.get("engagement_performance", {}).get("performance_ratio", 0) < 0.8:
                opportunities.append(
                    {
                        "opportunity": "Engagement Optimization",
                        "description": "Engagement rate below competitor average",
                        "impact": "high",
                        "difficulty": "medium",
                    }
                )

            return opportunities
        except Exception as e:
            logger.error(f"Opportunity identification failed: {e}")
            return []

    async def _generate_competitive_recommendations(self, channel_id: int, analysis: dict) -> list:
        """Generate actionable recommendations from competitive analysis"""
        try:
            recommendations = []

            # Market position recommendations
            market_position = analysis.get("market_position", {})
            if market_position.get("overall_score", 0) < 0.5:
                recommendations.append(
                    {
                        "category": "market_position",
                        "recommendation": "Focus on improving market position through increased engagement and content quality",
                        "priority": "high",
                        "timeframe": "short_term",
                    }
                )

            # Performance recommendations
            performance = analysis.get("performance_comparison", {})
            if performance.get("engagement_performance", {}).get("status") == "below_average":
                recommendations.append(
                    {
                        "category": "engagement",
                        "recommendation": "Implement engagement strategies to reach competitor average",
                        "priority": "medium",
                        "timeframe": "short_term",
                    }
                )

            # Sort by priority
            priority_scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            recommendations.sort(key=lambda x: priority_scores.get(x["priority"], 0), reverse=True)

            return recommendations[:8]  # Top 8 recommendations

        except Exception as e:
            logger.error(f"Competitive recommendations generation failed: {e}")
            return []
