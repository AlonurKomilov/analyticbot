"""
Strategy Generation Service - AI-Powered Content Strategy Planning

Extracted from AIInsightsService to maintain Single Responsibility Principle.
Handles content strategy generation with natural language planning.

Part of Phase 3 AI-First Architecture.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from .nlg_service import NarrativeStyle

logger = logging.getLogger(__name__)


class StrategyGenerationService:
    """
    📝 Strategy Generation Service

    Specialized service for AI-powered content strategy generation:
    - Content strategy planning
    - Natural language strategy documents
    - Implementation roadmaps
    - Success metrics definition
    - Goal-based optimization
    """

    def __init__(self, nlg_service, ai_insights_service, post_repo):
        """Initialize with required dependencies"""
        self._nlg_service = nlg_service
        self._ai_insights_service = ai_insights_service
        self._posts = post_repo

    async def generate_content_strategy_narrative(
        self,
        channel_id: int,
        goal: str = "engagement",
        timeframe: int = 30,
        narrative_style: NarrativeStyle = NarrativeStyle.ANALYTICAL,
    ) -> dict:
        """
        📝 Generate AI-Powered Content Strategy with Natural Language Planning

        Creates detailed content strategies explained in natural language.
        Perfect for content creators who need actionable, explained guidance.

        Args:
            channel_id: Target channel ID
            goal: Strategy goal (engagement, growth, reach, conversion)
            timeframe: Analysis and planning timeframe in days
            narrative_style: How to present the strategy

        Returns:
            Comprehensive strategy with narrative explanations and roadmap
        """
        try:
            # Analyze current content performance
            content_analysis = await self._analyze_current_performance(channel_id, timeframe)

            # Identify optimization opportunities
            optimization_opportunities = await self._identify_optimization_opportunities(
                channel_id, content_analysis, goal
            )

            # Generate strategy recommendations
            strategy_data = {
                "goal": goal,
                "timeframe": timeframe,
                "current_performance": content_analysis,
                "optimization_opportunities": optimization_opportunities,
                "competitive_analysis": await self._generate_competitive_insights(goal),
                "resource_requirements": await self._assess_resource_requirements(
                    optimization_opportunities
                ),
            }

            # Create natural language strategy document
            strategy_narrative = await self._nlg_service.generate_dynamic_report(
                strategy_data, "strategy", narrative_style
            )

            # Generate implementation roadmap
            implementation_roadmap = await self._create_implementation_roadmap(strategy_data, goal)

            # Define success metrics
            success_metrics = await self._define_strategy_success_metrics(goal, timeframe)

            return {
                "strategy_goal": goal,
                "timeframe_days": timeframe,
                "narrative_strategy": strategy_narrative,
                "current_performance_summary": content_analysis.get("summary", {}),
                "optimization_opportunities": optimization_opportunities,
                "implementation_roadmap": implementation_roadmap,
                "success_metrics": success_metrics,
                "resource_requirements": strategy_data["resource_requirements"],
                "competitive_insights": strategy_data["competitive_analysis"],
                "confidence_score": content_analysis.get("confidence", 0.7),
                "estimated_timeline": await self._estimate_strategy_timeline(
                    optimization_opportunities
                ),
                "risk_assessment": await self._assess_strategy_risks(strategy_data, goal),
                "created_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Content strategy narrative generation failed: {e}")
            return {
                "strategy_goal": goal,
                "error": "Unable to generate strategy narrative",
                "fallback_recommendation": "Review analytics data to identify optimization opportunities",
                "basic_recommendations": await self._generate_basic_recommendations(goal),
            }

    async def generate_quick_strategy_tips(
        self, channel_id: int, focus_area: str = "engagement", count: int = 5
    ) -> dict:
        """
        💡 Generate Quick Strategy Tips

        Provides immediate, actionable strategy tips based on current performance.
        Perfect for quick wins and immediate improvements.
        """
        try:
            # Get recent performance data
            now = datetime.now()
            start_date = now - timedelta(days=14)  # Last 2 weeks

            posts = await self._posts.top_by_views(channel_id, start_date, now, 20)

            quick_tips = []

            if posts:
                # Analyze recent performance for quick wins
                recent_analysis = await self._quick_performance_analysis(posts)

                # Generate focus-specific tips
                if focus_area == "engagement":
                    tips = await self._generate_engagement_tips(recent_analysis)
                elif focus_area == "growth":
                    tips = await self._generate_growth_tips(recent_analysis)
                elif focus_area == "reach":
                    tips = await self._generate_reach_tips(recent_analysis)
                elif focus_area == "consistency":
                    tips = await self._generate_consistency_tips(recent_analysis)
                else:
                    tips = await self._generate_general_tips(recent_analysis)

                quick_tips = tips[:count]

            return {
                "focus_area": focus_area,
                "quick_tips": quick_tips,
                "tip_count": len(quick_tips),
                "confidence": 0.8 if posts else 0.3,
                "data_quality": "good" if len(posts) >= 10 else "limited",
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Quick strategy tips generation failed: {e}")
            return {
                "focus_area": focus_area,
                "quick_tips": await self._get_fallback_tips(focus_area),
                "error": str(e),
            }

    async def analyze_strategy_effectiveness(
        self,
        channel_id: int,
        strategy_start_date: datetime,
        metrics_to_track: list[str] = None,
    ) -> dict:
        """
        📈 Analyze Strategy Effectiveness

        Evaluates how well implemented strategies are performing
        and provides recommendations for adjustments.
        """
        try:
            if metrics_to_track is None:
                metrics_to_track = ["engagement", "growth", "reach", "consistency"]

            now = datetime.now()

            # Get performance data before and after strategy implementation
            pre_strategy_end = strategy_start_date
            pre_strategy_start = strategy_start_date - timedelta(days=30)

            post_strategy_start = strategy_start_date
            post_strategy_end = now

            pre_posts = await self._posts.top_by_views(
                channel_id, pre_strategy_start, pre_strategy_end, 100
            )
            post_posts = await self._posts.top_by_views(
                channel_id, post_strategy_start, post_strategy_end, 100
            )

            effectiveness_analysis = {}

            for metric in metrics_to_track:
                metric_analysis = await self._analyze_metric_effectiveness(
                    metric, pre_posts, post_posts
                )
                effectiveness_analysis[metric] = metric_analysis

            # Overall effectiveness score
            overall_score = await self._calculate_overall_effectiveness(effectiveness_analysis)

            # Recommendations for improvement
            improvement_recommendations = await self._generate_improvement_recommendations(
                effectiveness_analysis, overall_score
            )

            return {
                "strategy_start_date": strategy_start_date.isoformat(),
                "analysis_date": now.isoformat(),
                "days_since_implementation": (now - strategy_start_date).days,
                "overall_effectiveness_score": overall_score,
                "metric_analysis": effectiveness_analysis,
                "improvement_recommendations": improvement_recommendations,
                "strategy_status": await self._determine_strategy_status(overall_score),
                "next_review_date": (now + timedelta(days=14)).isoformat(),
            }

        except Exception as e:
            logger.error(f"Strategy effectiveness analysis failed: {e}")
            return {
                "error": "Unable to analyze strategy effectiveness",
                "recommendation": "Manual review of performance metrics recommended",
            }

    # === PRIVATE HELPER METHODS ===

    async def _analyze_current_performance(self, channel_id: int, timeframe: int) -> dict:
        """Analyze current content performance for strategy planning"""
        try:
            now = datetime.now()
            start_date = now - timedelta(days=timeframe)

            posts = await self._posts.top_by_views(channel_id, start_date, now, 50)

            if not posts:
                return {"status": "insufficient_data", "confidence": 0.1}

            # Basic performance metrics
            views = [p.get("views", 0) for p in posts]
            engagement_scores = []

            for post in posts:
                views_count = post.get("views", 0)
                forwards = post.get("forwards", 0)
                replies = post.get("replies", 0)

                if views_count > 0:
                    engagement = (forwards + replies) / views_count * 100
                    engagement_scores.append(engagement)

            analysis = {
                "total_posts": len(posts),
                "avg_views": sum(views) / len(views) if views else 0,
                "total_views": sum(views),
                "avg_engagement": (
                    sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
                ),
                "posting_frequency": len(posts) / (timeframe / 7),  # Posts per week
                "performance_consistency": self._calculate_consistency_score(views),
                "top_performer_threshold": max(views) * 0.8 if views else 0,
                "confidence": min(0.9, len(posts) / 20),  # Higher confidence with more data
            }

            analysis["summary"] = {
                "status": ("good" if analysis["avg_engagement"] > 2 else "needs_improvement"),
                "strength": (
                    "consistency"
                    if analysis["performance_consistency"] > 0.7
                    else "growth_potential"
                ),
                "primary_opportunity": await self._identify_primary_opportunity(analysis),
            }

            return analysis

        except Exception as e:
            logger.error(f"Current performance analysis failed: {e}")
            return {"status": "error", "confidence": 0.1}

    async def _identify_optimization_opportunities(
        self, channel_id: int, content_analysis: dict, goal: str
    ) -> list[dict]:
        """Identify specific optimization opportunities based on goal"""
        opportunities = []

        try:
            # Goal-specific opportunity identification
            if goal == "engagement":
                opportunities.extend(await self._find_engagement_opportunities(content_analysis))
            elif goal == "growth":
                opportunities.extend(await self._find_growth_opportunities(content_analysis))
            elif goal == "reach":
                opportunities.extend(await self._find_reach_opportunities(content_analysis))
            elif goal == "consistency":
                opportunities.extend(await self._find_consistency_opportunities(content_analysis))
            else:
                # Comprehensive analysis for general goals
                opportunities.extend(await self._find_general_opportunities(content_analysis))

            # Sort by potential impact and feasibility
            opportunities.sort(
                key=lambda x: (x.get("impact_score", 0) + x.get("feasibility_score", 0)),
                reverse=True,
            )

            return opportunities[:8]  # Top 8 opportunities

        except Exception as e:
            logger.error(f"Optimization opportunity identification failed: {e}")
            return [
                {
                    "category": "general_improvement",
                    "description": "Focus on consistent content creation and audience engagement",
                    "impact_score": 0.6,
                    "feasibility_score": 0.8,
                }
            ]

    async def _find_engagement_opportunities(self, analysis: dict) -> list[dict]:
        """Find engagement-specific opportunities"""
        opportunities = []

        avg_engagement = analysis.get("avg_engagement", 0)
        consistency = analysis.get("performance_consistency", 0)

        if avg_engagement < 2:
            opportunities.append(
                {
                    "category": "engagement_optimization",
                    "description": "Implement engagement-driving content formats (questions, polls, discussions)",
                    "impact_score": 0.8,
                    "feasibility_score": 0.9,
                    "expected_improvement": "50-100% engagement increase",
                    "timeline": "2-3 weeks",
                }
            )

        if consistency < 0.6:
            opportunities.append(
                {
                    "category": "content_consistency",
                    "description": "Develop consistent content themes and posting schedule",
                    "impact_score": 0.7,
                    "feasibility_score": 0.8,
                    "expected_improvement": "25-40% engagement stability",
                    "timeline": "1 month",
                }
            )

        return opportunities

    async def _find_growth_opportunities(self, analysis: dict) -> list[dict]:
        """Find growth-specific opportunities"""
        opportunities = []

        posting_freq = analysis.get("posting_frequency", 0)

        if posting_freq < 3:  # Less than 3 posts per week
            opportunities.append(
                {
                    "category": "posting_frequency",
                    "description": "Increase posting frequency to 4-5 times per week for better visibility",
                    "impact_score": 0.7,
                    "feasibility_score": 0.6,
                    "expected_improvement": "30-50% growth acceleration",
                    "timeline": "6-8 weeks",
                }
            )

        opportunities.append(
            {
                "category": "audience_expansion",
                "description": "Implement content promotion and cross-platform strategies",
                "impact_score": 0.8,
                "feasibility_score": 0.5,
                "expected_improvement": "20-35% audience growth",
                "timeline": "2-3 months",
            }
        )

        return opportunities

    async def _find_reach_opportunities(self, analysis: dict) -> list[dict]:
        """Find reach-specific opportunities"""
        opportunities = []

        opportunities.append(
            {
                "category": "content_timing",
                "description": "Optimize posting times based on audience activity patterns",
                "impact_score": 0.6,
                "feasibility_score": 0.9,
                "expected_improvement": "15-25% reach improvement",
                "timeline": "1-2 weeks",
            }
        )

        opportunities.append(
            {
                "category": "content_formats",
                "description": "Experiment with trending content formats and styles",
                "impact_score": 0.7,
                "feasibility_score": 0.7,
                "expected_improvement": "20-40% reach expansion",
                "timeline": "3-4 weeks",
            }
        )

        return opportunities

    async def _find_consistency_opportunities(self, analysis: dict) -> list[dict]:
        """Find consistency-specific opportunities"""
        opportunities = []

        consistency = analysis.get("performance_consistency", 0)

        if consistency < 0.7:
            opportunities.append(
                {
                    "category": "content_standardization",
                    "description": "Develop content templates and quality standards",
                    "impact_score": 0.8,
                    "feasibility_score": 0.8,
                    "expected_improvement": "40-60% performance consistency",
                    "timeline": "2-3 weeks",
                }
            )

        return opportunities

    async def _find_general_opportunities(self, analysis: dict) -> list[dict]:
        """Find general optimization opportunities"""
        opportunities = []

        # Combine opportunities from all categories
        opportunities.extend(await self._find_engagement_opportunities(analysis))
        opportunities.extend(await self._find_reach_opportunities(analysis))

        # Add general optimization
        opportunities.append(
            {
                "category": "comprehensive_optimization",
                "description": "Implement comprehensive content strategy with analytics-driven improvements",
                "impact_score": 0.9,
                "feasibility_score": 0.6,
                "expected_improvement": "25-50% overall performance boost",
                "timeline": "6-8 weeks",
            }
        )

        return opportunities

    async def _create_implementation_roadmap(self, strategy_data: dict, goal: str) -> list[dict]:
        """Create detailed implementation roadmap"""
        opportunities = strategy_data.get("optimization_opportunities", [])

        roadmap = []
        week = 1

        # Phase 1: Quick wins (Week 1-2)
        quick_wins = [opp for opp in opportunities if opp.get("feasibility_score", 0) > 0.8]
        for opportunity in quick_wins[:2]:
            roadmap.append(
                {
                    "phase": 1,
                    "week": week,
                    "action": opportunity.get("description", ""),
                    "category": opportunity.get("category", ""),
                    "expected_outcome": opportunity.get("expected_improvement", ""),
                    "success_criteria": f"Implement {opportunity.get('category', 'optimization')}",
                    "resources_needed": "Content creation, scheduling tools",
                }
            )
            week += 1

        # Phase 2: Medium-term improvements (Week 3-6)
        medium_term = [opp for opp in opportunities if 0.5 < opp.get("feasibility_score", 0) <= 0.8]
        for opportunity in medium_term[:2]:
            roadmap.append(
                {
                    "phase": 2,
                    "week": week,
                    "action": opportunity.get("description", ""),
                    "category": opportunity.get("category", ""),
                    "expected_outcome": opportunity.get("expected_improvement", ""),
                    "success_criteria": f"Achieve {opportunity.get('expected_improvement', '15% improvement')}",
                    "resources_needed": "Analysis tools, content planning",
                }
            )
            week += 2

        # Phase 3: Long-term strategy (Week 7+)
        long_term = [opp for opp in opportunities if opp.get("feasibility_score", 0) <= 0.5]
        for opportunity in long_term[:1]:
            roadmap.append(
                {
                    "phase": 3,
                    "week": week,
                    "action": opportunity.get("description", ""),
                    "category": opportunity.get("category", ""),
                    "expected_outcome": opportunity.get("expected_improvement", ""),
                    "success_criteria": f"Establish {opportunity.get('category', 'strategy')}",
                    "resources_needed": "Strategic planning, potential team expansion",
                }
            )

        return roadmap

    async def _define_strategy_success_metrics(self, goal: str, timeframe: int) -> dict:
        """Define success metrics for strategy implementation"""
        base_timeframe = min(timeframe, 30)  # Cap at 30 days for realistic targets

        metrics_map = {
            "engagement": {
                "primary_metric": "engagement_rate",
                "target": "25% improvement",
                "timeframe": f"{base_timeframe} days",
                "secondary_metrics": ["comments_per_post", "shares_per_post"],
                "measurement_frequency": "weekly",
            },
            "growth": {
                "primary_metric": "follower_growth_rate",
                "target": "30% increase",
                "timeframe": f"{base_timeframe * 2} days",  # Growth takes longer
                "secondary_metrics": ["new_followers_per_week", "retention_rate"],
                "measurement_frequency": "bi-weekly",
            },
            "reach": {
                "primary_metric": "average_reach_per_post",
                "target": "35% improvement",
                "timeframe": f"{base_timeframe} days",
                "secondary_metrics": ["unique_viewers", "content_distribution"],
                "measurement_frequency": "weekly",
            },
            "consistency": {
                "primary_metric": "performance_consistency_score",
                "target": "80% consistency",
                "timeframe": f"{base_timeframe} days",
                "secondary_metrics": ["posting_frequency", "quality_score"],
                "measurement_frequency": "weekly",
            },
        }

        return metrics_map.get(goal, metrics_map["engagement"])

    def _calculate_consistency_score(self, values: list[float]) -> float:
        """Calculate consistency score from performance values"""
        if not values or len(values) < 2:
            return 0.5

        import numpy as np

        mean_val = np.mean(values)
        std_val = np.std(values)

        if mean_val == 0:
            return 0.0

        # Consistency score: lower std relative to mean = higher consistency
        coefficient_of_variation = std_val / mean_val
        consistency_score = max(0.0, 1.0 - coefficient_of_variation)

        return min(1.0, consistency_score)

    async def _identify_primary_opportunity(self, analysis: dict) -> str:
        """Identify the primary opportunity for improvement"""
        avg_engagement = analysis.get("avg_engagement", 0)
        consistency = analysis.get("performance_consistency", 0)
        posting_freq = analysis.get("posting_frequency", 0)

        if avg_engagement < 1.5:
            return "engagement_improvement"
        elif consistency < 0.6:
            return "consistency_improvement"
        elif posting_freq < 2:
            return "frequency_improvement"
        else:
            return "optimization_and_growth"

    async def health_check(self) -> dict:
        """Health check for strategy generation service"""
        return {
            "service": "StrategyGenerationService",
            "status": "healthy",
            "capabilities": [
                "content_strategy_generation",
                "natural_language_planning",
                "implementation_roadmaps",
                "success_metrics_definition",
                "strategy_effectiveness_analysis",
                "quick_strategy_tips",
            ],
            "supported_goals": [
                "engagement",
                "growth",
                "reach",
                "consistency",
                "comprehensive",
            ],
            "dependencies": {"nlg_service": True, "ai_insights_service": True},
            "timestamp": datetime.now().isoformat(),
        }
