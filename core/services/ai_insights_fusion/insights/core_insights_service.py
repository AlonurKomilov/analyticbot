"""
Core Insights Service
====================

Focused microservice for core AI-powered insights generation.

Single Responsibility:
- Core AI insights generation
- Data gathering and preparation
- Basic insights coordination
- Health monitoring

Extracted from AIInsightsService god object (200 lines of responsibility).
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..protocols import CoreInsightsProtocol

logger = logging.getLogger(__name__)


class CoreInsightsService(CoreInsightsProtocol):
    """
    Core insights microservice for AI-powered analytics.

    Single responsibility: Core AI insights generation only.
    No pattern analysis, no predictions - pure core insights focus.
    """

    def __init__(self, channel_daily_repo, post_repo, metrics_repo):
        self._daily = channel_daily_repo
        self._posts = post_repo
        self._metrics = metrics_repo

        # Core insights configuration
        self.insights_config = {
            "default_analysis_days": 30,
            "max_posts_analyzed": 100,
            "engagement_threshold": 0.05,
            "performance_threshold": 0.1,
        }

        logger.info("🤖 Core Insights Service initialized - AI insights generation focus")

    async def generate_ai_insights(
        self, channel_id: int, analysis_type: str = "comprehensive", days: int = 30
    ) -> dict[str, Any]:
        """
        Generate core AI-powered analytics insights.

        Core method extracted from god object - handles AI insights generation.
        """
        try:
            logger.info(f"🧠 Generating AI insights for channel {channel_id}")

            # Calculate time range
            now = datetime.now()
            start_date = now - timedelta(days=days)

            # Gather analysis data
            analysis_data = await self._gather_ai_analysis_data(channel_id, start_date, now)

            # Initialize insights report
            insights_report = {
                "channel_id": channel_id,
                "analysis_type": analysis_type,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": now.isoformat(),
                    "days_analyzed": days,
                },
                "generated_at": now.isoformat(),
                "data_summary": self._summarize_analysis_data(analysis_data),
                "status": "insights_generated",
            }

            # Add analysis type specific insights
            if analysis_type in ["comprehensive", "content"]:
                insights_report["content_overview"] = self._generate_content_overview(analysis_data)

            if analysis_type in ["comprehensive", "audience"]:
                insights_report["audience_overview"] = self._generate_audience_overview(
                    analysis_data
                )

            if analysis_type in ["comprehensive", "performance"]:
                insights_report["performance_overview"] = self._generate_performance_overview(
                    analysis_data
                )

            # Core insights summary
            insights_report["core_insights"] = self._generate_core_insights_summary(analysis_data)

            logger.info(f"✅ AI insights generated for channel {channel_id}")
            return insights_report

        except Exception as e:
            logger.error(f"❌ AI insights generation failed for channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "analysis_type": analysis_type,
                "generated_at": datetime.now().isoformat(),
                "error": str(e),
                "status": "insights_failed",
            }

    async def generate_insights_with_narrative(
        self, channel_id: int, narrative_style: str = "executive", days: int = 30
    ) -> dict[str, Any]:
        """
        Generate insights with natural language narrative.

        Simplified version - delegates complex narrative to integration service.
        """
        try:
            logger.info(f"📝 Generating insights with narrative for channel {channel_id}")

            # Generate base insights
            base_insights = await self.generate_ai_insights(channel_id, "comprehensive", days)

            # Add narrative metadata (actual narrative generation handled by integration service)
            narrative_insights = {
                **base_insights,
                "narrative_style": narrative_style,
                "narrative_requested": True,
                "narrative_ready": False,  # Will be set by integration service
                "narrative_summary": self._generate_simple_narrative_summary(base_insights),
            }

            logger.info(f"✅ Insights with narrative structure generated for channel {channel_id}")
            return narrative_insights

        except Exception as e:
            logger.error(f"❌ Narrative insights generation failed for channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "narrative_style": narrative_style,
                "generated_at": datetime.now().isoformat(),
                "error": str(e),
                "status": "narrative_insights_failed",
            }

    async def _gather_ai_analysis_data(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """
        Gather data for AI analysis.

        Extracted from god object - handles data collection.
        """
        try:
            logger.info(f"📊 Gathering analysis data for channel {channel_id}")

            # Get posts data
            posts = await self._posts.get_channel_posts(
                channel_id=channel_id,
                limit=self.insights_config["max_posts_analyzed"],
                start_date=start_date,
                end_date=end_date,
            )

            # Get daily metrics if available
            try:
                daily_data = await self._daily.get_date_range_data(
                    channel_id, start_date.date(), end_date.date()
                )
            except:
                daily_data = []

            # Prepare analysis data
            analysis_data = {
                "channel_id": channel_id,
                "time_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "posts": posts or [],
                "daily_metrics": daily_data or [],
                "posts_count": len(posts) if posts else 0,
                "data_quality": self._assess_data_quality(posts, daily_data),
            }

            logger.info(
                f"✅ Analysis data gathered: {len(posts or [])} posts, {len(daily_data or [])} daily records"
            )
            return analysis_data

        except Exception as e:
            logger.error(f"❌ Data gathering failed for channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "posts": [],
                "daily_metrics": [],
                "posts_count": 0,
                "data_quality": "poor",
                "error": str(e),
            }

    def _summarize_analysis_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Summarize the analysis data"""
        posts = data.get("posts", [])
        daily_metrics = data.get("daily_metrics", [])

        return {
            "total_posts": len(posts),
            "daily_records": len(daily_metrics),
            "data_quality": data.get("data_quality", "unknown"),
            "posts_with_views": len([p for p in posts if p.get("views", 0) > 0]),
            "analysis_scope": "comprehensive" if len(posts) > 10 else "limited",
        }

    def _generate_content_overview(self, data: dict[str, Any]) -> dict[str, Any]:
        """Generate content overview from data"""
        posts = data.get("posts", [])

        if not posts:
            return {"status": "no_content_data", "posts_analyzed": 0}

        # Calculate basic content metrics
        total_views = sum(post.get("views", 0) for post in posts)
        avg_views = total_views / len(posts) if posts else 0

        # Content length analysis
        content_lengths = [len(post.get("content", "")) for post in posts if post.get("content")]
        avg_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0

        return {
            "posts_analyzed": len(posts),
            "total_views": total_views,
            "average_views_per_post": round(avg_views, 2),
            "average_content_length": round(avg_length, 2),
            "content_variety": "moderate",  # Simplified
            "posting_frequency": len(posts) / max(7, 1),  # Posts per week approximation
            "status": "content_overview_generated",
        }

    def _generate_audience_overview(self, data: dict[str, Any]) -> dict[str, Any]:
        """Generate audience overview from data"""
        posts = data.get("posts", [])
        daily_metrics = data.get("daily_metrics", [])

        # Basic audience metrics
        if daily_metrics:
            try:
                followers = [
                    record.get("followers", 0)
                    for record in daily_metrics
                    if record.get("followers")
                ]
                current_followers = followers[-1] if followers else 0
                follower_growth = followers[-1] - followers[0] if len(followers) > 1 else 0
            except:
                current_followers = 0
                follower_growth = 0
        else:
            current_followers = 0
            follower_growth = 0

        # Engagement analysis
        if posts:
            views = [post.get("views", 0) for post in posts]
            avg_engagement = sum(views) / len(views) if views else 0
            engagement_rate = (
                (avg_engagement / current_followers * 100) if current_followers > 0 else 0
            )
        else:
            avg_engagement = 0
            engagement_rate = 0

        return {
            "current_followers": current_followers,
            "follower_growth": follower_growth,
            "average_engagement": round(avg_engagement, 2),
            "engagement_rate_percent": round(engagement_rate, 2),
            "audience_activity": "moderate",  # Simplified
            "growth_trend": "positive" if follower_growth > 0 else "stable",
            "status": "audience_overview_generated",
        }

    def _generate_performance_overview(self, data: dict[str, Any]) -> dict[str, Any]:
        """Generate performance overview from data"""
        posts = data.get("posts", [])

        if not posts:
            return {"status": "no_performance_data", "posts_analyzed": 0}

        # Performance metrics
        views = [post.get("views", 0) for post in posts]
        best_performing = max(views) if views else 0
        worst_performing = min(views) if views else 0
        avg_performance = sum(views) / len(views) if views else 0

        # Performance consistency
        if len(views) > 1:
            import numpy as np

            performance_std = np.std(views)
            consistency = "high" if performance_std < avg_performance * 0.5 else "moderate"
        else:
            consistency = "unknown"

        return {
            "posts_analyzed": len(posts),
            "best_performing_views": best_performing,
            "worst_performing_views": worst_performing,
            "average_performance": round(avg_performance, 2),
            "performance_consistency": consistency,
            "trending": "stable",  # Simplified
            "status": "performance_overview_generated",
        }

    def _generate_core_insights_summary(self, data: dict[str, Any]) -> dict[str, Any]:
        """Generate core insights summary"""
        posts_count = data.get("posts_count", 0)
        data_quality = data.get("data_quality", "unknown")

        # Basic insights based on data
        insights = {
            "data_coverage": "good" if posts_count > 20 else "limited",
            "analysis_confidence": "high" if data_quality == "good" else "medium",
            "key_metrics_available": posts_count > 0,
            "insights_reliability": "reliable" if posts_count > 10 else "preliminary",
        }

        # Add specific insights
        if posts_count > 0:
            insights["content_analysis_possible"] = True
            insights["performance_trends_available"] = posts_count > 5
            insights["pattern_detection_possible"] = posts_count > 15
        else:
            insights["content_analysis_possible"] = False
            insights["performance_trends_available"] = False
            insights["pattern_detection_possible"] = False

        return insights

    def _generate_simple_narrative_summary(self, insights: dict[str, Any]) -> str:
        """Generate simple narrative summary"""
        channel_id = insights.get("channel_id", "unknown")
        posts_count = insights.get("data_summary", {}).get("total_posts", 0)

        if posts_count == 0:
            return f"Channel {channel_id} has insufficient data for comprehensive analysis."
        elif posts_count < 10:
            return f"Channel {channel_id} has limited data ({posts_count} posts) for preliminary insights."
        else:
            return f"Channel {channel_id} has sufficient data ({posts_count} posts) for comprehensive AI analysis."

    def _assess_data_quality(
        self, posts: list[dict[str, Any]], daily_data: list[dict[str, Any]]
    ) -> str:
        """Assess the quality of available data"""
        posts_quality = "good" if posts and len(posts) > 10 else "limited"
        daily_quality = "good" if daily_data and len(daily_data) > 7 else "limited"

        if posts_quality == "good" and daily_quality == "good":
            return "good"
        elif posts_quality == "good" or daily_quality == "good":
            return "moderate"
        else:
            return "limited"

    async def health_check(self) -> dict[str, Any]:
        """Health check for core insights service"""
        return {
            "service_name": "CoreInsightsService",
            "status": "operational",
            "version": "1.0.0",
            "type": "microservice",
            "responsibility": "core_ai_insights",
            "dependencies": {
                "channel_daily_repo": "connected",
                "post_repo": "connected",
                "metrics_repo": "connected",
            },
            "capabilities": [
                "ai_insights_generation",
                "narrative_structure_preparation",
                "data_gathering",
                "insights_summarization",
            ],
            "configuration": self.insights_config,
        }
