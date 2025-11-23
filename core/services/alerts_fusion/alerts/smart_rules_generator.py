"""
Smart Alert Rules Generator
============================

Analyzes channel metrics and automatically generates personalized alert rules
with thresholds appropriate for the channel's size and performance.

Key Features:
- Channel size-aware thresholds (100 vs 1M subscribers)
- Historical performance analysis
- Industry benchmarks integration
- Dynamic rule generation based on actual channel data
"""

import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class SmartRulesGenerator:
    """
    Generates personalized alert rules based on channel analysis.

    Analyzes:
    - Channel size (subscriber count)
    - Historical engagement rates
    - Growth patterns
    - Content frequency
    - Performance baselines

    Returns intelligent, channel-specific alert rules.
    """

    def __init__(self, channels_repo, daily_repo, posts_repo):
        self._channels = channels_repo
        self._daily = daily_repo
        self._posts = posts_repo

    async def generate_smart_rules_for_channel(self, channel_id: int | str) -> list[dict[str, Any]]:
        """
        Generate personalized alert rules for a specific channel.

        Analyzes channel's current state and historical data to create
        intelligent, size-appropriate alert thresholds.

        Args:
            channel_id: Channel ID to analyze

        Returns:
            List of smart alert rule configurations
        """
        try:
            logger.info(f"🎯 Generating smart alert rules for channel {channel_id}")

            # Get channel info
            channel = await self._get_channel_info(channel_id)
            if not channel:
                logger.warning(f"Channel {channel_id} not found, using default rules")
                return self._get_default_fallback_rules()

            subscriber_count = channel.get("subscriber_count", 0)

            # Analyze historical data
            analysis = await self._analyze_channel_history(channel_id)

            # Generate rules based on analysis
            rules = []

            # 1. Low Engagement Alert (relative to channel's baseline)
            rules.append(self._generate_engagement_rule(subscriber_count, analysis))

            # 2. Subscriber Loss Alert (percentage-based, not fixed number)
            rules.append(self._generate_subscriber_loss_rule(subscriber_count, analysis))

            # 3. High Performance Alert (celebrates wins at channel's scale)
            rules.append(self._generate_high_performance_rule(subscriber_count, analysis))

            # 4. Content Slowdown Alert (based on channel's posting frequency)
            rules.append(self._generate_content_slowdown_rule(subscriber_count, analysis))

            # 5. Viral Potential Alert (relative to channel's normal engagement)
            rules.append(self._generate_viral_potential_rule(subscriber_count, analysis))

            logger.info(
                f"✅ Generated {len(rules)} personalized rules for channel {channel_id} "
                f"({subscriber_count} subscribers)"
            )

            return rules

        except Exception as e:
            logger.error(f"Failed to generate smart rules for channel {channel_id}: {e}")
            return self._get_default_fallback_rules()

    async def _get_channel_info(self, channel_id: int | str) -> dict[str, Any] | None:
        """Get channel information from database"""
        try:
            query = """
                SELECT id, username, title, subscriber_count, created_at
                FROM channels
                WHERE id = $1
            """
            result = await self._channels.db.fetchrow(query, int(channel_id))
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to fetch channel info: {e}")
            return None

    async def _analyze_channel_history(self, channel_id: int | str) -> dict[str, Any]:
        """
        Analyze channel's historical performance to understand baselines.

        Returns metrics like:
        - Average engagement rate
        - Typical subscriber growth
        - Posting frequency
        - Performance variability
        """
        try:
            # Get last 30 days of daily stats
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            query = """
                SELECT
                    AVG(views_count) as avg_views,
                    AVG(likes_count) as avg_likes,
                    AVG(comments_count) as avg_comments,
                    AVG(shares_count) as avg_shares,
                    AVG(subscriber_change) as avg_subscriber_change,
                    STDDEV(views_count) as stddev_views,
                    MAX(views_count) as max_views,
                    MIN(views_count) as min_views,
                    COUNT(*) as days_with_data
                FROM channel_daily_stats
                WHERE channel_id = $1
                AND date >= $2 AND date <= $3
            """

            result = await self._daily.db.fetchrow(query, int(channel_id), start_date, end_date)

            if not result or result["days_with_data"] == 0:
                return self._get_default_analysis()

            # Calculate engagement rate baseline
            avg_views = result["avg_views"] or 0
            avg_engagement = (
                (result["avg_likes"] or 0)
                + (result["avg_comments"] or 0)
                + (result["avg_shares"] or 0)
            )
            engagement_rate = (avg_engagement / avg_views * 100) if avg_views > 0 else 3.0

            # Get posting frequency
            posts_query = """
                SELECT COUNT(*) as post_count
                FROM posts
                WHERE channel_id = $1
                AND published_at >= $2 AND published_at <= $3
            """
            posts_result = await self._posts.db.fetchrow(
                posts_query, int(channel_id), start_date, end_date
            )
            posts_per_month = posts_result["post_count"] if posts_result else 0
            avg_days_between_posts = 30 / posts_per_month if posts_per_month > 0 else 7

            return {
                "avg_views": float(result["avg_views"] or 0),
                "max_views": float(result["max_views"] or 0),
                "min_views": float(result["min_views"] or 0),
                "stddev_views": float(result["stddev_views"] or 0),
                "avg_subscriber_change": float(result["avg_subscriber_change"] or 0),
                "engagement_rate": engagement_rate,
                "posts_per_month": posts_per_month,
                "avg_days_between_posts": avg_days_between_posts,
                "days_with_data": result["days_with_data"],
            }

        except Exception as e:
            logger.error(f"Failed to analyze channel history: {e}")
            return self._get_default_analysis()

    def _generate_engagement_rule(
        self, subscriber_count: int, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate engagement alert rule based on channel's baseline.

        Small channels: Alert at 2% (more sensitive)
        Medium channels: Alert at channel's baseline - 30%
        Large channels: Alert at channel's baseline - 40%
        """
        baseline_engagement = analysis.get("engagement_rate", 3.0)

        # Scale threshold based on channel size
        if subscriber_count < 1000:
            threshold = min(baseline_engagement * 0.5, 2.0)
            description = (
                f"Alert when engagement drops below {threshold:.1f}% (50% of your baseline)"
            )
        elif subscriber_count < 10000:
            threshold = baseline_engagement * 0.7
            description = f"Alert when engagement drops below {threshold:.1f}% (70% of your {baseline_engagement:.1f}% baseline)"
        else:
            threshold = baseline_engagement * 0.6
            description = f"Alert when engagement drops below {threshold:.1f}% (60% of your {baseline_engagement:.1f}% baseline)"

        return {
            "id": "smart_low_engagement",
            "name": "🔔 Low Engagement Alert",
            "description": description,
            "metric_type": "engagement_rate",
            "threshold": round(threshold, 2),
            "comparison": "below",
            "enabled": True,
            "category": "performance",
            "personalized": True,
            "baseline_value": round(baseline_engagement, 2),
        }

    def _generate_subscriber_loss_rule(
        self, subscriber_count: int, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate subscriber loss alert based on percentage, not fixed count.

        Small channels (< 100): Alert at 5% daily loss
        Medium channels (100-10K): Alert at 2% daily loss
        Large channels (10K-100K): Alert at 1% daily loss
        Huge channels (> 100K): Alert at 0.5% daily loss
        """
        if subscriber_count < 100:
            percentage = 5.0
            threshold = max(int(subscriber_count * 0.05), 5)
        elif subscriber_count < 1000:
            percentage = 3.0
            threshold = int(subscriber_count * 0.03)
        elif subscriber_count < 10000:
            percentage = 2.0
            threshold = int(subscriber_count * 0.02)
        elif subscriber_count < 100000:
            percentage = 1.0
            threshold = int(subscriber_count * 0.01)
        else:
            percentage = 0.5
            threshold = int(subscriber_count * 0.005)

        return {
            "id": "smart_subscriber_loss",
            "name": "📉 Subscriber Loss Alert",
            "description": f"Alert when losing more than {threshold:,} subscribers ({percentage}% of your {subscriber_count:,} subscribers)",
            "metric_type": "subscriber_change",
            "threshold": -threshold,  # Negative for loss
            "comparison": "below",
            "enabled": True,
            "category": "growth",
            "personalized": True,
            "percentage": percentage,
        }

    def _generate_high_performance_rule(
        self, subscriber_count: int, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate high performance celebration alert.

        Based on channel's historical maximum + 20% for growth potential.
        """
        baseline_views = analysis.get("avg_views", 0)
        max_views = analysis.get("max_views", 0)

        # Set celebration threshold at 150% of average or 120% of max
        if max_views > 0:
            threshold = int(max_views * 1.2)
        elif baseline_views > 0:
            threshold = int(baseline_views * 1.5)
        else:
            # Fallback based on channel size
            threshold = max(int(subscriber_count * 0.5), 100)

        return {
            "id": "smart_high_performance",
            "name": "🚀 High Performance Alert",
            "description": f"Celebrate when views exceed {threshold:,} (your best performance: {int(max_views):,})",
            "metric_type": "views",
            "threshold": threshold,
            "comparison": "above",
            "enabled": True,
            "category": "celebration",
            "personalized": True,
            "baseline_value": int(baseline_views),
        }

    def _generate_content_slowdown_rule(
        self, subscriber_count: int, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate content frequency alert based on channel's posting habits.

        Active channels (post every 1-2 days): Alert after 3 days
        Regular channels (post every 3-5 days): Alert after 7 days
        Slow channels (post weekly): Alert after 10 days
        """
        avg_days = analysis.get("avg_days_between_posts", 7)

        # Set alert at 2x normal posting frequency
        threshold_days = int(avg_days * 2)
        threshold_days = max(min(threshold_days, 10), 3)  # Between 3-10 days

        if avg_days < 2:
            context = "You usually post daily"
        elif avg_days < 5:
            context = f"You usually post every {int(avg_days)} days"
        else:
            context = "You usually post weekly"

        return {
            "id": "smart_content_slowdown",
            "name": "⏰ Content Slowdown Alert",
            "description": f"Alert when no posts for {threshold_days}+ days ({context})",
            "metric_type": "days_since_post",
            "threshold": threshold_days,
            "comparison": "above",
            "enabled": True,
            "category": "content",
            "personalized": True,
            "baseline_value": round(avg_days, 1),
        }

    def _generate_viral_potential_rule(
        self, subscriber_count: int, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate viral potential alert relative to channel's baseline.

        Detects when content performs exceptionally well.
        """
        baseline_engagement = analysis.get("engagement_rate", 3.0)

        # Set viral threshold at 2x baseline (but minimum 8%)
        threshold = max(baseline_engagement * 2.0, 8.0)

        return {
            "id": "smart_viral_potential",
            "name": "⭐ Viral Potential Alert",
            "description": f"Alert when engagement exceeds {threshold:.1f}% (2x your {baseline_engagement:.1f}% baseline)",
            "metric_type": "engagement_rate",
            "threshold": round(threshold, 2),
            "comparison": "above",
            "enabled": True,
            "category": "opportunity",
            "personalized": True,
            "baseline_value": round(baseline_engagement, 2),
        }

    def _get_default_analysis(self) -> dict[str, Any]:
        """Fallback analysis when no historical data available"""
        return {
            "avg_views": 100,
            "max_views": 200,
            "min_views": 50,
            "stddev_views": 50,
            "avg_subscriber_change": 5,
            "engagement_rate": 3.0,
            "posts_per_month": 15,
            "avg_days_between_posts": 2,
            "days_with_data": 0,
        }

    def _get_default_fallback_rules(self) -> list[dict[str, Any]]:
        """
        Fallback rules when channel analysis fails.
        Uses conservative, universal thresholds.
        """
        return [
            {
                "id": "default_low_engagement",
                "name": "🔔 Low Engagement Alert",
                "description": "Alert when engagement rate drops below 2%",
                "metric_type": "engagement_rate",
                "threshold": 2.0,
                "comparison": "below",
                "enabled": True,
                "category": "performance",
                "personalized": False,
            },
            {
                "id": "default_subscriber_loss",
                "name": "📉 Subscriber Loss Alert",
                "description": "Alert when losing subscribers",
                "metric_type": "subscriber_change",
                "threshold": -10,
                "comparison": "below",
                "enabled": True,
                "category": "growth",
                "personalized": False,
            },
            {
                "id": "default_high_performance",
                "name": "🚀 High Performance Alert",
                "description": "Celebrate when views exceed 1,000",
                "metric_type": "views",
                "threshold": 1000,
                "comparison": "above",
                "enabled": True,
                "category": "celebration",
                "personalized": False,
            },
            {
                "id": "default_content_slowdown",
                "name": "⏰ Content Slowdown Alert",
                "description": "Alert when no posts for 5+ days",
                "metric_type": "days_since_post",
                "threshold": 5,
                "comparison": "above",
                "enabled": True,
                "category": "content",
                "personalized": False,
            },
            {
                "id": "default_viral_potential",
                "name": "⭐ Viral Potential Alert",
                "description": "Alert when engagement rate exceeds 8%",
                "metric_type": "engagement_rate",
                "threshold": 8.0,
                "comparison": "above",
                "enabled": True,
                "category": "opportunity",
                "personalized": False,
            },
        ]
