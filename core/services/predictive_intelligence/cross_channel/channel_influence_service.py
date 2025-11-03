"""
Channel Influence Service
=========================

Focused microservice for channel influence mapping and analysis.

Single Responsibility:
- Calculate influence relationships between channels
- Map bidirectional influence patterns
- Analyze audience, content, and timing influence
- Generate influence insights

Extracted from CrossChannelAnalysisService (lines 629-995)
"""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class ChannelInfluenceService:
    """
    Channel influence analysis microservice.

    Single responsibility: Analyze channel influence relationships only.
    """

    def __init__(self, config_manager=None):
        self.config_manager = config_manager

        # Influence configuration
        self.influence_config = {
            "factors": {
                "audience_overlap": 0.3,
                "content_similarity": 0.25,
                "temporal_alignment": 0.25,
                "engagement_correlation": 0.2,
            },
            "influence_types": {
                "dominant": 0.8,  # Strong one-way influence
                "mutual": 0.6,  # Strong two-way influence
                "moderate": 0.4,  # Moderate influence
                "weak": 0.2,  # Weak influence
            },
            "analysis_depth": {
                "direct_influence": True,
                "indirect_influence": False,  # Future: 2nd degree influence
                "network_effects": False,  # Future: network-wide influence
            },
        }

        # Influence tracking
        self.influence_maps: dict[str, dict[str, Any]] = {}

        logger.info("🎯 Channel Influence Service initialized")

    async def calculate_influence_relationships(
        self,
        channels_data: dict[int, dict[str, Any]],
        correlation_matrix: dict[str, Any] | None = None,
    ) -> dict[str, dict[str, dict[str, Any]]]:
        """
        Calculate influence relationships between all channel pairs.

        Args:
            channels_data: Channel metrics data
            correlation_matrix: Optional pre-calculated correlations

        Returns:
            Influence map: source_channel -> target_channel -> influence data
        """
        try:
            logger.info(f"🎯 Calculating influence relationships for {len(channels_data)} channels")

            channel_ids = list(channels_data.keys())
            influence_map = {}

            # Calculate pairwise influences
            for source_id in channel_ids:
                influence_map[str(source_id)] = {}

                for target_id in channel_ids:
                    if source_id != target_id:
                        # Calculate influence metrics
                        influence_data = await self._calculate_influence_metrics(
                            channels_data[source_id],
                            channels_data[target_id],
                            source_id,
                            target_id,
                        )

                        influence_map[str(source_id)][str(target_id)] = influence_data

            # Cache the influence map
            cache_key = (
                f"influence_{'-'.join(map(str, channel_ids))}_{datetime.now().strftime('%Y%m%d')}"
            )
            self.influence_maps[cache_key] = influence_map

            logger.info(f"✅ Influence relationships calculated for {len(influence_map)} sources")
            return influence_map

        except Exception as e:
            logger.error(f"❌ Influence relationship calculation failed: {e}")
            return {}

    async def _calculate_influence_metrics(
        self,
        source_data: dict[str, Any],
        target_data: dict[str, Any],
        source_id: int,
        target_id: int,
    ) -> dict[str, Any]:
        """
        Calculate detailed influence metrics from source to target channel.
        """
        # Calculate individual influence factors
        audience_influence = self._calculate_audience_influence(source_data, target_data)
        content_influence = self._calculate_content_influence(source_data, target_data)
        timing_influence = self._calculate_timing_influence(source_data, target_data)

        # Get engagement correlation if available
        source_engagement = source_data.get("metrics", {}).get("engagement_rate", 0)
        target_engagement = target_data.get("metrics", {}).get("engagement_rate", 0)
        engagement_correlation = 1.0 - abs(source_engagement - target_engagement) / max(
            source_engagement, target_engagement, 1
        )

        # Calculate overall influence score
        influence_score = self._calculate_influence_score(
            audience_influence,
            content_influence,
            timing_influence,
            engagement_correlation,
        )

        # Determine influence type
        influence_type = self._determine_influence_type(influence_score)

        return {
            "influence_score": influence_score,
            "influence_type": influence_type,
            "factors": {
                "audience": audience_influence,
                "content": content_influence,
                "timing": timing_influence,
                "engagement": engagement_correlation,
            },
            "source_id": source_id,
            "target_id": target_id,
        }

    def _calculate_influence_score(
        self,
        audience_influence: float,
        content_influence: float,
        timing_influence: float,
        engagement_correlation: float,
    ) -> float:
        """
        Calculate weighted influence score from individual factors.
        """
        weights = self.influence_config["factors"]

        influence_score = (
            audience_influence * weights["audience_overlap"]
            + content_influence * weights["content_similarity"]
            + timing_influence * weights["temporal_alignment"]
            + engagement_correlation * weights["engagement_correlation"]
        )

        return round(influence_score, 3)

    def _determine_influence_type(self, influence_score: float) -> str:
        """Determine influence type category based on score."""
        thresholds = self.influence_config["influence_types"]

        if influence_score >= thresholds["dominant"]:
            return "dominant"
        elif influence_score >= thresholds["mutual"]:
            return "mutual"
        elif influence_score >= thresholds["moderate"]:
            return "moderate"
        else:
            return "weak"

    def _analyze_influence_factors(
        self, source_data: dict[str, Any], target_data: dict[str, Any]
    ) -> dict[str, float]:
        """
        Analyze detailed influence factors.

        Returns breakdown of influence components.
        """
        return {
            "audience_overlap": self._calculate_audience_influence(source_data, target_data),
            "content_similarity": self._calculate_content_influence(source_data, target_data),
            "timing_alignment": self._calculate_timing_influence(source_data, target_data),
            "platform_synergy": self._calculate_platform_synergy(source_data, target_data),
        }

    def _calculate_audience_influence(
        self, source_data: dict[str, Any], target_data: dict[str, Any]
    ) -> float:
        """
        Calculate audience-based influence score.

        Factors:
        - Relative audience sizes
        - Potential audience overlap
        - Audience growth patterns
        """
        source_metrics = source_data.get("metrics", {})
        target_metrics = target_data.get("metrics", {})

        source_size = source_metrics.get("audience_size", 1)
        target_size = target_metrics.get("audience_size", 1)

        # Larger channels have more influence on smaller ones
        if source_size > target_size:
            size_influence = min(source_size / target_size, 2.0) / 2.0
        else:
            size_influence = 0.5

        return round(size_influence, 3)

    def _calculate_content_influence(
        self, source_data: dict[str, Any], target_data: dict[str, Any]
    ) -> float:
        """
        Calculate content-based influence score.

        Currently simplified - future: analyze actual content similarity.
        """
        # Placeholder: check if platforms suggest similar content types
        source_platform = source_data.get("platform", "unknown")
        target_platform = target_data.get("platform", "unknown")

        if source_platform == target_platform:
            return 0.8
        return 0.5

    def _calculate_timing_influence(
        self, source_data: dict[str, Any], target_data: dict[str, Any]
    ) -> float:
        """
        Calculate timing-based influence score.

        Future: analyze posting patterns and temporal correlations.
        """
        # Placeholder: simplified timing score
        return 0.6

    def _calculate_platform_synergy(
        self, source_data: dict[str, Any], target_data: dict[str, Any]
    ) -> float:
        """Calculate platform synergy score."""
        source_platform = source_data.get("platform", "unknown")
        target_platform = target_data.get("platform", "unknown")

        # Same platform = high synergy
        if source_platform == target_platform:
            return 1.0

        # Compatible platforms
        compatible_platforms = {
            "telegram": ["discord", "slack"],
            "youtube": ["tiktok", "instagram"],
            "twitter": ["linkedin", "reddit"],
        }

        if target_platform in compatible_platforms.get(source_platform, []):
            return 0.7

        return 0.4

    def identify_strongest_influences(
        self, influence_maps: dict[str, dict[str, dict[str, Any]]], top_n: int = 10
    ) -> list[dict[str, Any]]:
        """
        Identify the strongest influence relationships across all channels.

        Args:
            influence_maps: Full influence mapping
            top_n: Number of top influences to return

        Returns:
            List of strongest influence relationships
        """
        all_influences = []

        for source_id, targets in influence_maps.items():
            for target_id, influence_data in targets.items():
                all_influences.append(
                    {
                        "source": source_id,
                        "target": target_id,
                        "score": influence_data.get("influence_score", 0),
                        "type": influence_data.get("influence_type", "unknown"),
                        "factors": influence_data.get("factors", {}),
                    }
                )

        # Sort by influence score
        all_influences.sort(key=lambda x: x["score"], reverse=True)

        return all_influences[:top_n]

    def analyze_bidirectional_influences(
        self,
        influence_maps: dict[str, dict[str, dict[str, Any]]],
        channel_a_id: str,
        channel_b_id: str,
    ) -> dict[str, Any]:
        """
        Analyze bidirectional influence between two channels.

        Determines:
        - Which channel has stronger influence
        - If influence is mutual or one-way
        - Asymmetry in influence relationship
        """
        try:
            # Get influence in both directions
            a_to_b = influence_maps.get(channel_a_id, {}).get(channel_b_id, {})
            b_to_a = influence_maps.get(channel_b_id, {}).get(channel_a_id, {})

            a_to_b_score = a_to_b.get("influence_score", 0)
            b_to_a_score = b_to_a.get("influence_score", 0)

            # Determine relationship type
            if abs(a_to_b_score - b_to_a_score) < 0.2:
                relationship_type = "mutual"
                dominant_channel = None
            elif a_to_b_score > b_to_a_score:
                relationship_type = "unidirectional"
                dominant_channel = channel_a_id
            else:
                relationship_type = "unidirectional"
                dominant_channel = channel_b_id

            return {
                "channel_a": channel_a_id,
                "channel_b": channel_b_id,
                "a_to_b_influence": a_to_b_score,
                "b_to_a_influence": b_to_a_score,
                "relationship_type": relationship_type,
                "dominant_channel": dominant_channel,
                "influence_asymmetry": abs(a_to_b_score - b_to_a_score),
            }

        except Exception as e:
            logger.error(f"Bidirectional analysis failed: {e}")
            return {"error": str(e), "relationship_type": "unknown"}

    def generate_influence_insights(
        self,
        influence_maps: dict[str, dict[str, dict[str, Any]]],
        channels_data: dict[int, dict[str, Any]],
    ) -> list[str]:
        """
        Generate actionable insights from influence analysis.

        Returns:
            List of human-readable insight strings
        """
        insights = []

        # Find strongest influencers
        strongest = self.identify_strongest_influences(influence_maps, top_n=5)

        if strongest:
            top_influencer = strongest[0]
            insights.append(
                f"Channel {top_influencer['source']} has the strongest influence "
                f"on channel {top_influencer['target']} (score: {top_influencer['score']})"
            )

        # Identify mutual influence pairs
        mutual_pairs = []
        processed_pairs = set()

        for source_id, targets in influence_maps.items():
            for target_id, influence_data in targets.items():
                pair_key = tuple(sorted([source_id, target_id]))

                if pair_key not in processed_pairs:
                    bidirectional = self.analyze_bidirectional_influences(
                        influence_maps, source_id, target_id
                    )

                    if bidirectional.get("relationship_type") == "mutual":
                        mutual_pairs.append(bidirectional)

                    processed_pairs.add(pair_key)

        if mutual_pairs:
            insights.append(
                f"Found {len(mutual_pairs)} mutual influence relationships, "
                f"indicating strong bidirectional engagement opportunities"
            )

        # Identify isolated channels (low influence)
        channel_avg_influences = {}
        for source_id, targets in influence_maps.items():
            if targets:
                avg_influence = sum(t.get("influence_score", 0) for t in targets.values()) / len(
                    targets
                )
                channel_avg_influences[source_id] = avg_influence

        if channel_avg_influences:
            min_influence = min(channel_avg_influences.values())
            if min_influence < 0.3:
                low_influence_channels = [
                    ch for ch, inf in channel_avg_influences.items() if inf < 0.3
                ]
                if low_influence_channels:
                    insights.append(
                        f"{len(low_influence_channels)} channels have low influence scores, "
                        f"suggesting opportunities for improved cross-promotion"
                    )

        return insights

    def assess_influence_analysis_quality(
        self, influence_maps: dict[str, dict[str, dict[str, Any]]]
    ) -> str:
        """
        Assess quality/reliability of influence analysis.

        Returns quality rating: "high", "medium", or "low"
        """
        if not influence_maps:
            return "low"

        # Calculate average influence scores
        all_scores = []
        for targets in influence_maps.values():
            for influence_data in targets.values():
                all_scores.append(influence_data.get("influence_score", 0))

        if not all_scores:
            return "low"

        avg_score = sum(all_scores) / len(all_scores)
        score_variance = sum((s - avg_score) ** 2 for s in all_scores) / len(all_scores)

        # High quality if:
        # - Reasonable average score (not too low/high)
        # - Moderate variance (differentiation between channels)
        if 0.3 <= avg_score <= 0.7 and 0.05 <= score_variance <= 0.15:
            return "high"
        elif 0.2 <= avg_score <= 0.8:
            return "medium"
        else:
            return "low"

    async def health_check(self) -> dict[str, Any]:
        """Health check for influence service."""
        return {
            "service": "ChannelInfluenceService",
            "status": "operational",
            "influence_maps_cached": len(self.influence_maps),
            "config_loaded": bool(self.influence_config),
            "timestamp": datetime.now().isoformat(),
        }
