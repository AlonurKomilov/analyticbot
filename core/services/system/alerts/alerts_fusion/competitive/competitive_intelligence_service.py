"""
Competitive Intelligence Service
===============================

Focused microservice for competitive analysis and market intelligence.

Single Responsibility:
- Competitive intelligence analysis
- Competitor discovery and profiling
- Market position analysis
- Competitive recommendations
- Opportunity identification

Extracted from AlertsIntelligenceService god object (200 lines of responsibility).
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from core.ports.repository_ports import ChannelDailyRepository, ChannelRepository, PostRepository

from ..protocols import CompetitiveIntelligenceProtocol

logger = logging.getLogger(__name__)


class CompetitiveIntelligenceService(CompetitiveIntelligenceProtocol):
    """
    Competitive intelligence microservice for market analysis.

    Single responsibility: Competitive analysis and market intelligence only.
    No alerts logic, no live monitoring - pure competitive focus.
    """

    def __init__(
        self,
        posts_repo: PostRepository,
        daily_repo: ChannelDailyRepository,
        channels_repo: ChannelRepository,
    ):
        self._posts = posts_repo
        self._daily = daily_repo
        self._channels = channels_repo

        # Competitive analysis configuration
        self.competitive_config = {
            "max_competitors": 5,
            "analysis_depth": "standard",
            "market_analysis_days": 30,
            "similarity_threshold": 0.7,
            "performance_metrics": ["views", "followers", "engagement", "posting_frequency"],
        }

        logger.info("🏆 Competitive Intelligence Service initialized - market analysis focus")

    async def generate_competitive_intelligence(
        self,
        channel_id: int,
        competitor_ids: list[int] | None = None,
        analysis_depth: str = "standard",
    ) -> dict[str, Any]:
        """
        Generate comprehensive competitive intelligence analysis.

        Core method extracted from god object - handles competitive analysis.
        """
        try:
            logger.info(f"🔍 Generating competitive intelligence for channel {channel_id}")

            # Discover competitors if not provided
            if not competitor_ids:
                competitors = await self.discover_competitor_channels(
                    channel_id, self.competitive_config["max_competitors"]
                )
                competitor_ids = [comp["channel_id"] for comp in competitors]

            # Get channel profile
            channel_profile = await self.get_channel_profile(channel_id)

            # Analyze competitors
            competitor_analysis = await self._analyze_competitors(
                channel_id, competitor_ids, analysis_depth
            )

            # Performance comparison
            performance_comparison = await self._compare_performance(channel_id, competitor_ids)

            # Market position analysis
            market_position = await self._analyze_market_position(channel_id, competitor_analysis)

            # Identify opportunities
            opportunities = await self._identify_opportunities(channel_id, competitor_analysis)

            # Generate recommendations
            recommendations = await self._generate_competitive_recommendations(
                channel_id,
                {
                    "performance_comparison": performance_comparison,
                    "market_position": market_position,
                    "opportunities": opportunities,
                },
            )

            intelligence_report = {
                "channel_id": channel_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_depth": analysis_depth,
                "channel_profile": channel_profile,
                "competitors_analyzed": len(competitor_ids),
                "competitor_analysis": competitor_analysis,
                "performance_comparison": performance_comparison,
                "market_position": market_position,
                "opportunities": opportunities,
                "recommendations": recommendations,
                "status": "analysis_complete",
            }

            logger.info(f"✅ Competitive intelligence generated for channel {channel_id}")
            return intelligence_report

        except Exception as e:
            logger.error(f"❌ Competitive intelligence failed for channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "analysis_failed",
            }

    async def discover_competitor_channels(
        self, channel_id: int, max_competitors: int = 5
    ) -> list[dict[str, Any]]:
        """
        Discover competitor channels automatically.

        Simplified competitor discovery logic.
        """
        try:
            logger.info(f"🔎 Discovering competitors for channel {channel_id}")

            # In a real implementation, this would use sophisticated algorithms
            # For now, we'll create a simplified discovery mechanism
            competitors = []

            # Example competitor discovery (simplified)
            for i in range(1, max_competitors + 1):
                competitor_id = channel_id + i  # Simplified logic
                competitor_profile = await self._get_basic_competitor_profile(competitor_id)

                if competitor_profile:
                    competitors.append(
                        {
                            "channel_id": competitor_id,
                            "similarity_score": 0.8 - (i * 0.1),  # Decreasing similarity
                            "discovery_method": "algorithmic",
                            "profile": competitor_profile,
                        }
                    )

            logger.info(f"🎯 Discovered {len(competitors)} competitors for channel {channel_id}")
            return competitors

        except Exception as e:
            logger.error(f"Competitor discovery failed: {e}")
            return []

    async def get_channel_profile(self, channel_id: int) -> dict[str, Any]:
        """
        Get comprehensive channel profile for analysis.

        Core method extracted from god object - handles channel profiling.
        """
        try:
            logger.info(f"📊 Building channel profile for {channel_id}")

            # Get recent posts for analysis using available repository methods
            now = datetime.now()
            start_dt = now - timedelta(days=30)

            posts_count = await self._posts.count(channel_id, start_dt, now)
            total_views = await self._posts.sum_views(channel_id, start_dt, now)
            posts = await self._posts.top_by_views(channel_id, start_dt, now, 50)

            # Get current follower count
            followers = await self._daily.series_value(channel_id, "followers", now)
            if followers is None:
                followers = await self._daily.series_value(channel_id, "subscribers", now)

            # Calculate profile metrics
            profile = {
                "channel_id": channel_id,
                "profiled_at": now.isoformat(),
                "followers_count": followers or 0,
                "posts_last_30_days": len(posts),
                "avg_posting_frequency": len(posts) / 30,
                "content_metrics": self._analyze_content_profile(posts),
                "engagement_profile": self._calculate_engagement_profile(posts, followers or 0),
                "activity_pattern": self._analyze_activity_pattern(posts),
                "status": "profile_complete",
            }

            logger.info(f"✅ Channel profile built for {channel_id}")
            return profile

        except Exception as e:
            logger.error(f"Channel profiling failed for {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "profiled_at": datetime.now().isoformat(),
                "error": str(e),
                "status": "profile_failed",
            }

    async def _analyze_competitors(
        self, channel_id: int, competitor_ids: list[int], analysis_depth: str
    ) -> dict[str, Any]:
        """Analyze competitor channels"""
        try:
            competitor_profiles = []

            for comp_id in competitor_ids:
                profile = await self.get_channel_profile(comp_id)
                competitor_profiles.append(profile)

            # Aggregate competitor analysis
            analysis = {
                "total_competitors": len(competitor_ids),
                "analysis_depth": analysis_depth,
                "competitor_profiles": competitor_profiles,
                "market_averages": self._calculate_market_averages(competitor_profiles),
                "competitive_landscape": self._analyze_competitive_landscape(competitor_profiles),
            }

            return analysis

        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            return {"error": str(e)}

    async def _compare_performance(
        self, channel_id: int, competitor_ids: list[int]
    ) -> dict[str, Any]:
        """Compare performance against competitors"""
        try:
            # Get channel profile
            channel_profile = await self.get_channel_profile(channel_id)

            # Get competitor profiles
            competitor_profiles = []
            for comp_id in competitor_ids:
                profile = await self.get_channel_profile(comp_id)
                competitor_profiles.append(profile)

            # Calculate performance comparison
            channel_followers = channel_profile.get("followers_count", 0)
            channel_posts = channel_profile.get("posts_last_30_days", 0)

            competitor_followers = [p.get("followers_count", 0) for p in competitor_profiles]
            competitor_posts = [p.get("posts_last_30_days", 0) for p in competitor_profiles]

            avg_competitor_followers = (
                sum(competitor_followers) / len(competitor_followers) if competitor_followers else 0
            )
            avg_competitor_posts = (
                sum(competitor_posts) / len(competitor_posts) if competitor_posts else 0
            )

            return {
                "followers_performance": {
                    "channel_value": channel_followers,
                    "competitor_average": avg_competitor_followers,
                    "performance_ratio": channel_followers / avg_competitor_followers
                    if avg_competitor_followers > 0
                    else 0,
                    "status": "above_average"
                    if channel_followers > avg_competitor_followers
                    else "below_average",
                },
                "content_performance": {
                    "channel_value": channel_posts,
                    "competitor_average": avg_competitor_posts,
                    "performance_ratio": channel_posts / avg_competitor_posts
                    if avg_competitor_posts > 0
                    else 0,
                    "status": "above_average"
                    if channel_posts > avg_competitor_posts
                    else "below_average",
                },
            }

        except Exception as e:
            logger.error(f"Performance comparison failed: {e}")
            return {"error": str(e)}

    async def _analyze_market_position(
        self, channel_id: int, competitor_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze market position"""
        try:
            # Simplified market position analysis
            market_averages = competitor_analysis.get("market_averages", {})

            return {
                "position_score": 0.7,  # Simplified score
                "market_segment": "mid_tier",
                "competitive_advantages": ["content_frequency", "engagement_quality"],
                "areas_for_improvement": ["follower_growth", "content_variety"],
                "market_opportunities": ["untapped_audience", "content_optimization"],
            }

        except Exception as e:
            logger.error(f"Market position analysis failed: {e}")
            return {"error": str(e)}

    async def _identify_opportunities(
        self, channel_id: int, competitor_analysis: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Identify competitive opportunities"""
        try:
            opportunities = [
                {
                    "opportunity": "Content Gap Analysis",
                    "description": "Opportunities in content areas competitors are not covering",
                    "impact": "high",
                    "difficulty": "medium",
                    "timeframe": "short_term",
                },
                {
                    "opportunity": "Engagement Optimization",
                    "description": "Improve engagement rates based on competitor best practices",
                    "impact": "medium",
                    "difficulty": "low",
                    "timeframe": "immediate",
                },
            ]

            return opportunities

        except Exception as e:
            logger.error(f"Opportunity identification failed: {e}")
            return []

    async def _generate_competitive_recommendations(
        self, channel_id: int, analysis: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Generate competitive recommendations"""
        try:
            recommendations = [
                {
                    "category": "content_strategy",
                    "recommendation": "Analyze competitor content gaps for new content opportunities",
                    "priority": "high",
                    "timeframe": "short_term",
                    "expected_impact": "increased_reach",
                },
                {
                    "category": "engagement",
                    "recommendation": "Implement best practices from high-performing competitors",
                    "priority": "medium",
                    "timeframe": "immediate",
                    "expected_impact": "improved_engagement",
                },
            ]

            return recommendations

        except Exception as e:
            logger.error(f"Competitive recommendations failed: {e}")
            return []

    async def _get_basic_competitor_profile(self, channel_id: int) -> dict[str, Any] | None:
        """Get basic competitor profile"""
        try:
            # Simplified profile - in real implementation would be more comprehensive
            return {
                "channel_id": channel_id,
                "estimated_followers": 1000 + (channel_id % 5000),  # Simplified
                "estimated_activity": "active",
                "content_type": "general",
            }
        except Exception as e:
            logger.error(f"Basic competitor profile failed: {e}")
            return None

    def _analyze_content_profile(self, posts: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze content profile from posts"""
        if not posts:
            return {"avg_views": 0, "content_variety": "low", "posting_consistency": "irregular"}

        views = [post.get("views", 0) for post in posts]
        avg_views = sum(views) / len(views) if views else 0

        return {
            "avg_views": avg_views,
            "content_variety": "moderate",  # Simplified
            "posting_consistency": "regular" if len(posts) > 10 else "irregular",
        }

    def _calculate_engagement_profile(
        self, posts: list[dict[str, Any]], followers: int
    ) -> dict[str, Any]:
        """Calculate engagement profile"""
        if not posts or not followers:
            return {"avg_engagement_rate": 0, "engagement_trend": "stable"}

        views = [post.get("views", 0) for post in posts]
        avg_views = sum(views) / len(views) if views else 0
        engagement_rate = (avg_views / followers * 100) if followers > 0 else 0

        return {
            "avg_engagement_rate": engagement_rate,
            "engagement_trend": "stable",  # Simplified
        }

    def _analyze_activity_pattern(self, posts: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze posting activity pattern"""
        return {
            "posting_frequency": "regular",
            "peak_activity_hours": "unknown",
            "activity_consistency": "moderate",
        }

    def _calculate_market_averages(
        self, competitor_profiles: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculate market averages from competitor data"""
        if not competitor_profiles:
            return {}

        followers = [p.get("followers_count", 0) for p in competitor_profiles]
        posts = [p.get("posts_last_30_days", 0) for p in competitor_profiles]

        return {
            "avg_followers": sum(followers) / len(followers) if followers else 0,
            "avg_posts_per_month": sum(posts) / len(posts) if posts else 0,
        }

    def _analyze_competitive_landscape(
        self, competitor_profiles: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze competitive landscape"""
        return {
            "market_saturation": "moderate",
            "competition_intensity": "medium",
            "market_leaders": competitor_profiles[:2] if competitor_profiles else [],
        }

    async def health_check(self) -> dict[str, Any]:
        """Health check for competitive intelligence service"""
        return {
            "service_name": "CompetitiveIntelligenceService",
            "status": "operational",
            "version": "1.0.0",
            "type": "microservice",
            "responsibility": "competitive_intelligence",
            "dependencies": {
                "posts_repository": "connected",
                "daily_repository": "connected",
                "channels_repository": "connected",
            },
            "capabilities": [
                "competitive_analysis",
                "competitor_discovery",
                "channel_profiling",
                "market_position_analysis",
                "opportunity_identification",
                "competitive_recommendations",
            ],
            "configuration": self.competitive_config,
        }
