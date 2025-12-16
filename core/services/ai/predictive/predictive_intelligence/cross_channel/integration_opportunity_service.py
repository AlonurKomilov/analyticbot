"""
Integration Opportunity Service
================================

Focused microservice for identifying cross-channel integration patterns and opportunities.

Single Responsibility:
- Identify integration opportunities between channels
- Analyze content sync patterns
- Evaluate audience overlap opportunities
- Generate integration recommendations

Extracted from CrossChannelAnalysisService (lines 1234-1395)
"""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class IntegrationOpportunityService:
    """
    Integration opportunity analysis microservice.

    Single responsibility: Identify and analyze integration opportunities only.
    """

    def __init__(self, config_manager=None):
        self.config_manager = config_manager

        # Integration configuration
        self.integration_config = {
            "opportunity_types": {
                "content_sync": {
                    "weight": 0.30,
                    "threshold": 0.6,
                    "description": "Synchronized content posting across channels",
                },
                "audience_overlap": {
                    "weight": 0.25,
                    "threshold": 0.5,
                    "description": "Shared audience targeting",
                },
                "timing_coordination": {
                    "weight": 0.20,
                    "threshold": 0.5,
                    "description": "Coordinated posting times",
                },
                "cross_promotion": {
                    "weight": 0.25,
                    "threshold": 0.6,
                    "description": "Cross-channel promotion campaigns",
                },
            },
            "feasibility_factors": {
                "platform_compatibility": 0.35,
                "resource_requirements": 0.25,
                "audience_alignment": 0.25,
                "content_fit": 0.15,
            },
            "priority_levels": {"critical": 0.8, "high": 0.6, "medium": 0.4, "low": 0.2},
        }

        # Opportunity tracking
        self.identified_opportunities: list[dict[str, Any]] = []

        logger.info("🔗 Integration Opportunity Service initialized")

    async def identify_integration_opportunities(
        self,
        channels_data: dict[int, dict[str, Any]],
        correlation_patterns: dict[str, Any] | None = None,
        influence_relationships: dict[str, dict[str, dict[str, Any]]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Identify integration opportunities between channels.

        Args:
            channels_data: Channel metrics and data
            correlation_patterns: Pre-calculated correlation patterns
            influence_relationships: Pre-calculated influence relationships

        Returns:
            List of integration opportunities with details
        """
        try:
            logger.info(
                f"🔍 Identifying integration opportunities for {len(channels_data)} channels"
            )

            opportunities = []

            # Analyze content sync patterns
            content_sync = await self._analyze_content_sync_patterns(channels_data)
            if content_sync.get("opportunities"):
                opportunities.extend(content_sync["opportunities"])

            # Analyze audience overlap patterns
            audience_overlap = await self._analyze_audience_overlap_patterns(channels_data)
            if audience_overlap.get("opportunities"):
                opportunities.extend(audience_overlap["opportunities"])

            # Analyze timing coordination patterns
            timing_coordination = await self._analyze_timing_coordination_patterns(channels_data)
            if timing_coordination.get("opportunities"):
                opportunities.extend(timing_coordination["opportunities"])

            # Analyze cross-promotion patterns
            cross_promotion = await self._analyze_cross_promotion_patterns(channels_data)
            if cross_promotion.get("opportunities"):
                opportunities.extend(cross_promotion["opportunities"])

            # Rank opportunities by potential impact
            ranked_opportunities = self._rank_opportunities_by_impact(opportunities)

            # Cache identified opportunities
            self.identified_opportunities = ranked_opportunities

            logger.info(f"✅ Identified {len(ranked_opportunities)} integration opportunities")
            return ranked_opportunities

        except Exception as e:
            logger.error(f"❌ Integration opportunity identification failed: {e}")
            return []

    async def _analyze_content_sync_patterns(
        self, channels_data: dict[int, dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Analyze opportunities for synchronized content posting.
        """
        opportunities = []
        channel_ids = list(channels_data.keys())

        # Analyze pairwise content sync potential
        for i, channel_a_id in enumerate(channel_ids):
            for channel_b_id in channel_ids[i + 1 :]:
                channel_a = channels_data[channel_a_id]
                channel_b = channels_data[channel_b_id]

                # Calculate content sync score
                sync_score = self._calculate_content_sync_score(channel_a, channel_b)

                if (
                    sync_score
                    >= self.integration_config["opportunity_types"]["content_sync"]["threshold"]
                ):
                    opportunities.append(
                        {
                            "type": "content_sync",
                            "channels": [channel_a_id, channel_b_id],
                            "score": sync_score,
                            "description": f"High potential for synchronized content between channels {channel_a_id} and {channel_b_id}",
                            "action": "Create unified content calendar for both channels",
                        }
                    )

        return {"opportunities": opportunities}

    def _calculate_content_sync_score(
        self, channel_a: dict[str, Any], channel_b: dict[str, Any]
    ) -> float:
        """Calculate content synchronization potential score."""
        # Platform compatibility
        platform_a = channel_a.get("platform", "unknown")
        platform_b = channel_b.get("platform", "unknown")

        if platform_a == platform_b:
            platform_score = 1.0
        elif self._are_platforms_compatible(platform_a, platform_b):
            platform_score = 0.7
        else:
            platform_score = 0.3

        # Engagement alignment
        engagement_a = channel_a.get("metrics", {}).get("engagement_rate", 0)
        engagement_b = channel_b.get("metrics", {}).get("engagement_rate", 0)
        engagement_score = 1.0 - abs(engagement_a - engagement_b) / max(
            engagement_a, engagement_b, 1
        )

        # Combined score
        sync_score = platform_score * 0.6 + engagement_score * 0.4
        return round(sync_score, 3)

    def _are_platforms_compatible(self, platform_a: str, platform_b: str) -> bool:
        """Check if two platforms are compatible for content sync."""
        compatible_groups = [
            {"telegram", "discord", "slack"},
            {"youtube", "tiktok", "instagram"},
            {"twitter", "linkedin", "facebook"},
        ]

        for group in compatible_groups:
            if platform_a in group and platform_b in group:
                return True

        return False

    async def _analyze_audience_overlap_patterns(
        self, channels_data: dict[int, dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Analyze opportunities for audience overlap and shared targeting.
        """
        opportunities = []
        channel_ids = list(channels_data.keys())

        for i, channel_a_id in enumerate(channel_ids):
            for channel_b_id in channel_ids[i + 1 :]:
                channel_a = channels_data[channel_a_id]
                channel_b = channels_data[channel_b_id]

                # Estimate audience overlap potential
                overlap_score = self._calculate_audience_overlap_score(channel_a, channel_b)

                if (
                    overlap_score
                    >= self.integration_config["opportunity_types"]["audience_overlap"]["threshold"]
                ):
                    opportunities.append(
                        {
                            "type": "audience_overlap",
                            "channels": [channel_a_id, channel_b_id],
                            "score": overlap_score,
                            "description": f"Significant audience overlap potential between channels {channel_a_id} and {channel_b_id}",
                            "action": "Implement cross-channel audience targeting campaigns",
                        }
                    )

        return {"opportunities": opportunities}

    def _calculate_audience_overlap_score(
        self, channel_a: dict[str, Any], channel_b: dict[str, Any]
    ) -> float:
        """Calculate audience overlap potential."""
        # Audience size similarity
        size_a = channel_a.get("metrics", {}).get("audience_size", 1)
        size_b = channel_b.get("metrics", {}).get("audience_size", 1)
        size_ratio = min(size_a, size_b) / max(size_a, size_b)

        # Platform factor (same platform = higher overlap potential)
        platform_a = channel_a.get("platform", "unknown")
        platform_b = channel_b.get("platform", "unknown")
        platform_factor = 1.0 if platform_a == platform_b else 0.6

        overlap_score = size_ratio * 0.5 + platform_factor * 0.5
        return round(overlap_score, 3)

    async def _analyze_timing_coordination_patterns(
        self, channels_data: dict[int, dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Analyze opportunities for coordinated posting times.
        """
        opportunities = []

        # Simplified: check for channels that could benefit from coordinated timing
        channel_ids = list(channels_data.keys())

        if len(channel_ids) >= 2:
            # Create coordinated timing opportunity for all channels
            timing_score = 0.7  # Placeholder score

            opportunities.append(
                {
                    "type": "timing_coordination",
                    "channels": channel_ids,
                    "score": timing_score,
                    "description": f"Opportunity for coordinated posting across {len(channel_ids)} channels",
                    "action": "Implement unified posting schedule with optimal timing",
                }
            )

        return {"opportunities": opportunities}

    async def _analyze_cross_promotion_patterns(
        self, channels_data: dict[int, dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Analyze opportunities for cross-channel promotion.
        """
        opportunities = []
        channel_ids = list(channels_data.keys())

        # Find channel pairs with good cross-promotion potential
        for i, channel_a_id in enumerate(channel_ids):
            for channel_b_id in channel_ids[i + 1 :]:
                channel_a = channels_data[channel_a_id]
                channel_b = channels_data[channel_b_id]

                # Calculate cross-promotion score
                promo_score = self._calculate_cross_promotion_score(channel_a, channel_b)

                if (
                    promo_score
                    >= self.integration_config["opportunity_types"]["cross_promotion"]["threshold"]
                ):
                    # Determine which channel should promote which
                    size_a = channel_a.get("metrics", {}).get("audience_size", 0)
                    size_b = channel_b.get("metrics", {}).get("audience_size", 0)

                    if size_a > size_b:
                        action = f"Promote channel {channel_b_id} on larger channel {channel_a_id}"
                    else:
                        action = f"Promote channel {channel_a_id} on larger channel {channel_b_id}"

                    opportunities.append(
                        {
                            "type": "cross_promotion",
                            "channels": [channel_a_id, channel_b_id],
                            "score": promo_score,
                            "description": "Strong cross-promotion opportunity between channels",
                            "action": action,
                        }
                    )

        return {"opportunities": opportunities}

    def _calculate_cross_promotion_score(
        self, channel_a: dict[str, Any], channel_b: dict[str, Any]
    ) -> float:
        """Calculate cross-promotion potential score."""
        # Different audience sizes make better cross-promotion opportunities
        size_a = channel_a.get("metrics", {}).get("audience_size", 1)
        size_b = channel_b.get("metrics", {}).get("audience_size", 1)
        size_difference = abs(size_a - size_b) / max(size_a, size_b)

        # Engagement rates
        engagement_a = channel_a.get("metrics", {}).get("engagement_rate", 0)
        engagement_b = channel_b.get("metrics", {}).get("engagement_rate", 0)
        avg_engagement = (engagement_a + engagement_b) / 2

        # Cross-promotion score (higher for size difference + good engagement)
        promo_score = size_difference * 0.6 + avg_engagement * 0.4
        return round(promo_score, 3)

    def _rank_opportunities_by_impact(
        self, opportunities: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Rank opportunities by potential impact.

        Considers:
        - Opportunity score
        - Opportunity type weight
        - Number of channels involved
        """
        for opp in opportunities:
            opp_type = opp.get("type", "unknown")
            type_weight = (
                self.integration_config["opportunity_types"].get(opp_type, {}).get("weight", 0.25)
            )
            opp_score = opp.get("score", 0)
            num_channels = len(opp.get("channels", []))

            # Calculate impact score
            impact_score = opp_score * 0.5 + type_weight * 0.3 + min(num_channels / 5, 1.0) * 0.2

            opp["impact_score"] = round(impact_score, 3)
            opp["priority"] = self._determine_priority_level(impact_score)

        # Sort by impact score
        return sorted(opportunities, key=lambda x: x.get("impact_score", 0), reverse=True)

    def _determine_priority_level(self, impact_score: float) -> str:
        """Determine priority level from impact score."""
        priority_levels = self.integration_config["priority_levels"]

        if impact_score >= priority_levels["critical"]:
            return "critical"
        elif impact_score >= priority_levels["high"]:
            return "high"
        elif impact_score >= priority_levels["medium"]:
            return "medium"
        else:
            return "low"

    def calculate_integration_feasibility(
        self, opportunity: dict[str, Any], channels_data: dict[int, dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Calculate feasibility of implementing an integration opportunity.

        Returns:
            Feasibility assessment with score and factors
        """
        try:
            channel_ids = opportunity.get("channels", [])

            if not channel_ids or len(channel_ids) < 2:
                return {"feasibility": 0.0, "rating": "not_feasible"}

            # Get channel data
            channels = [channels_data.get(ch_id, {}) for ch_id in channel_ids]

            # Calculate feasibility factors
            platform_compat = self._calculate_platform_compatibility(channels)
            resource_req = self._estimate_resource_requirements(opportunity)
            audience_align = self._calculate_audience_alignment(channels)
            content_fit = self._calculate_content_fit(channels)

            # Weighted feasibility score
            weights = self.integration_config["feasibility_factors"]
            feasibility = (
                platform_compat * weights["platform_compatibility"]
                + resource_req * weights["resource_requirements"]
                + audience_align * weights["audience_alignment"]
                + content_fit * weights["content_fit"]
            )

            return {
                "feasibility_score": round(feasibility, 3),
                "rating": "high"
                if feasibility >= 0.7
                else ("medium" if feasibility >= 0.5 else "low"),
                "factors": {
                    "platform_compatibility": platform_compat,
                    "resource_requirements": resource_req,
                    "audience_alignment": audience_align,
                    "content_fit": content_fit,
                },
            }

        except Exception as e:
            logger.error(f"Feasibility calculation failed: {e}")
            return {"feasibility_score": 0.0, "rating": "error", "error": str(e)}

    def _calculate_platform_compatibility(self, channels: list[dict[str, Any]]) -> float:
        """Calculate platform compatibility score."""
        platforms = [ch.get("platform", "unknown") for ch in channels]

        # All same platform = high compatibility
        if len(set(platforms)) == 1:
            return 1.0

        # Mixed but compatible platforms
        compatible_count = 0
        for i, platform_a in enumerate(platforms):
            for platform_b in platforms[i + 1 :]:
                if self._are_platforms_compatible(platform_a, platform_b):
                    compatible_count += 1

        total_pairs = len(platforms) * (len(platforms) - 1) // 2
        return compatible_count / total_pairs if total_pairs > 0 else 0.5

    def _estimate_resource_requirements(self, opportunity: dict[str, Any]) -> float:
        """Estimate resource requirements (inverse score - lower = better)."""
        opp_type = opportunity.get("type", "unknown")

        # Resource complexity by type
        resource_complexity = {
            "content_sync": 0.6,  # Moderate resources
            "audience_overlap": 0.4,  # Lower resources
            "timing_coordination": 0.3,  # Low resources
            "cross_promotion": 0.5,  # Moderate resources
        }

        complexity = resource_complexity.get(opp_type, 0.5)

        # Inverse score (lower complexity = higher score)
        return 1.0 - complexity

    def _calculate_audience_alignment(self, channels: list[dict[str, Any]]) -> float:
        """Calculate audience alignment score."""
        if len(channels) < 2:
            return 0.5

        # Calculate average engagement rate variance
        engagement_rates = [ch.get("metrics", {}).get("engagement_rate", 0) for ch in channels]
        avg_engagement = sum(engagement_rates) / len(engagement_rates)

        if avg_engagement == 0:
            return 0.5

        variance = sum((er - avg_engagement) ** 2 for er in engagement_rates) / len(
            engagement_rates
        )
        alignment = max(0, 1.0 - (variance**0.5))

        return round(alignment, 3)

    def _calculate_content_fit(self, channels: list[dict[str, Any]]) -> float:
        """Calculate content fit score."""
        # Simplified: based on platform compatibility
        return self._calculate_platform_compatibility(channels)

    def generate_integration_recommendations(
        self, opportunities: list[dict[str, Any]], top_n: int = 5
    ) -> list[dict[str, Any]]:
        """
        Generate top integration recommendations with action plans.

        Args:
            opportunities: List of identified opportunities
            top_n: Number of top recommendations to return

        Returns:
            Top recommendations with detailed action plans
        """
        # Get top opportunities by impact
        top_opportunities = sorted(
            opportunities, key=lambda x: x.get("impact_score", 0), reverse=True
        )[:top_n]

        recommendations = []

        for i, opp in enumerate(top_opportunities, 1):
            recommendation = {
                "rank": i,
                "opportunity_type": opp.get("type"),
                "channels": opp.get("channels"),
                "impact_score": opp.get("impact_score"),
                "priority": opp.get("priority"),
                "description": opp.get("description"),
                "action_plan": self._create_action_plan(opp),
                "expected_benefits": self._estimate_benefits(opp),
            }
            recommendations.append(recommendation)

        return recommendations

    def _create_action_plan(self, opportunity: dict[str, Any]) -> list[str]:
        """Create step-by-step action plan for opportunity."""
        opp_type = opportunity.get("type", "unknown")

        action_plans = {
            "content_sync": [
                "1. Analyze posting patterns across channels",
                "2. Create unified content calendar",
                "3. Implement cross-posting automation",
                "4. Monitor engagement metrics",
            ],
            "audience_overlap": [
                "1. Conduct audience analysis survey",
                "2. Identify common interests and demographics",
                "3. Create targeted cross-channel campaigns",
                "4. Track audience migration patterns",
            ],
            "timing_coordination": [
                "1. Analyze optimal posting times per channel",
                "2. Create coordinated posting schedule",
                "3. Implement scheduling automation",
                "4. Monitor engagement timing patterns",
            ],
            "cross_promotion": [
                "1. Design cross-promotion campaign strategy",
                "2. Create promotional content for each channel",
                "3. Implement promotion schedule",
                "4. Track conversion metrics",
            ],
        }

        return action_plans.get(
            opp_type,
            [
                "1. Analyze opportunity",
                "2. Plan implementation",
                "3. Execute",
                "4. Monitor results",
            ],
        )

    def _estimate_benefits(self, opportunity: dict[str, Any]) -> dict[str, str]:
        """Estimate expected benefits from opportunity."""
        opp_type = opportunity.get("type", "unknown")
        impact_score = opportunity.get("impact_score", 0)

        # Estimate percentage improvements
        if impact_score >= 0.8:
            engagement_boost = "20-30%"
            reach_increase = "25-40%"
        elif impact_score >= 0.6:
            engagement_boost = "10-20%"
            reach_increase = "15-25%"
        else:
            engagement_boost = "5-10%"
            reach_increase = "10-15%"

        return {
            "engagement_boost": engagement_boost,
            "reach_increase": reach_increase,
            "audience_growth": f"{int(impact_score * 20)}-{int(impact_score * 30)}%",
            "efficiency_gain": "15-25% time savings"
            if opp_type == "content_sync"
            else "10-20% resource optimization",
        }

    async def health_check(self) -> dict[str, Any]:
        """Health check for integration opportunity service."""
        return {
            "service": "IntegrationOpportunityService",
            "status": "operational",
            "opportunities_identified": len(self.identified_opportunities),
            "config_loaded": bool(self.integration_config),
            "timestamp": datetime.now().isoformat(),
        }
