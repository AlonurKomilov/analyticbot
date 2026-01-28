"""
Correlation Analysis Service
============================

Focused microservice for cross-channel correlation calculations.

Single Responsibility:
- Calculate correlation matrices between channels
- Identify correlation patterns and clusters
- Assess correlation confidence and data quality

Extracted from CrossChannelAnalysisService (lines 459-855)
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class CorrelationAnalysisService:
    """
    Correlation analysis microservice for channel-to-channel correlation calculations.

    Single responsibility: Calculate and analyze correlations only.
    """

    def __init__(self, config_manager=None):
        self.config_manager = config_manager

        # Correlation configuration
        self.correlation_config = {
            "thresholds": {"strong": 0.7, "moderate": 0.5, "weak": 0.3, "minimal": 0.1},
            "platform_compatibility": {
                "telegram": ["discord", "slack", "twitter"],
                "youtube": ["tiktok", "instagram", "facebook"],
                "twitter": ["telegram", "linkedin", "reddit"],
                "instagram": ["tiktok", "youtube", "facebook"],
            },
            "timeframe_weights": {
                "short_term": 0.4,  # 7 days
                "medium_term": 0.35,  # 30 days
                "long_term": 0.25,  # 90 days
            },
        }

        # Correlation cache
        self.correlation_cache: dict[str, dict[str, Any]] = {}

        logger.info("📊 Correlation Analysis Service initialized")

    async def calculate_correlation_matrix(
        self, channels_data: dict[int, dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Calculate full correlation matrix for given channels.

        Args:
            channels_data: Channel ID -> Channel metrics data

        Returns:
            Correlation matrix with pairwise correlations
        """
        try:
            logger.info(f"📊 Calculating correlation matrix for {len(channels_data)} channels")

            channel_ids = list(channels_data.keys())
            correlation_matrix = {
                "channels": channel_ids,
                "correlations": {},
                "timestamp": datetime.now().isoformat(),
            }

            # Calculate pairwise correlations
            for i, channel_a_id in enumerate(channel_ids):
                for channel_b_id in channel_ids[i + 1 :]:
                    pair_key = f"{channel_a_id}_{channel_b_id}"

                    correlation_score = self._calculate_pairwise_correlation(
                        channels_data[channel_a_id], channels_data[channel_b_id]
                    )

                    correlation_matrix["correlations"][pair_key] = correlation_score

            # Add correlation statistics
            if correlation_matrix["correlations"]:
                correlations = list(correlation_matrix["correlations"].values())
                correlation_matrix["statistics"] = {
                    "average": sum(correlations) / len(correlations),
                    "max": max(correlations),
                    "min": min(correlations),
                    "count": len(correlations),
                }

            logger.info(
                f"✅ Correlation matrix calculated: {len(correlation_matrix['correlations'])} pairs"
            )
            return correlation_matrix

        except Exception as e:
            logger.error(f"❌ Correlation matrix calculation failed: {e}")
            return {"channels": [], "correlations": {}, "error": str(e)}

    def _calculate_pairwise_correlation(
        self, channel_a: dict[str, Any], channel_b: dict[str, Any]
    ) -> float:
        """
        Calculate correlation score between two channels.

        Uses multiple factors:
        - Engagement patterns similarity
        - Audience overlap indicators
        - Content timing alignment
        - Growth pattern correlation
        """
        try:
            # Extract metrics
            metrics_a = channel_a.get("metrics", {})
            metrics_b = channel_b.get("metrics", {})

            # Calculate engagement correlation
            engagement_a = metrics_a.get("engagement_rate", 0)
            engagement_b = metrics_b.get("engagement_rate", 0)
            engagement_correlation = 1.0 - abs(engagement_a - engagement_b) / max(
                engagement_a, engagement_b, 1
            )

            # Calculate growth correlation
            growth_a = metrics_a.get("growth_rate", 0)
            growth_b = metrics_b.get("growth_rate", 0)
            growth_correlation = 1.0 - abs(growth_a - growth_b) / max(
                abs(growth_a), abs(growth_b), 1
            )

            # Calculate audience size correlation
            audience_a = metrics_a.get("audience_size", 1)
            audience_b = metrics_b.get("audience_size", 1)
            size_ratio = min(audience_a, audience_b) / max(audience_a, audience_b)

            # Platform compatibility bonus
            platform_a = channel_a.get("platform", "unknown")
            platform_b = channel_b.get("platform", "unknown")
            platform_bonus = self._calculate_platform_correlation(platform_a, platform_b)

            # Weighted correlation score
            correlation_score = (
                engagement_correlation * 0.35
                + growth_correlation * 0.25
                + size_ratio * 0.20
                + platform_bonus * 0.20
            )

            return round(correlation_score, 3)

        except Exception as e:
            logger.warning(f"Pairwise correlation calculation failed: {e}")
            return 0.0

    def _calculate_platform_correlation(self, platform_a: str, platform_b: str) -> float:
        """Calculate platform compatibility score."""
        if platform_a == platform_b:
            return 1.0

        # Check if platforms are in compatibility list
        compatible_platforms = self.correlation_config["platform_compatibility"].get(platform_a, [])
        if platform_b in compatible_platforms:
            return 0.7

        return 0.3

    def identify_correlation_patterns(self, correlation_matrix: dict[str, Any]) -> dict[str, Any]:
        """
        Identify patterns in correlation matrix.

        Finds:
        - Highly correlated channel groups
        - Correlation clusters
        - Isolated channels
        - Strong vs weak correlations
        """
        try:
            correlations = correlation_matrix.get("correlations", {})

            if not correlations:
                return {"patterns": [], "clusters": [], "isolated": []}

            # Categorize correlations by strength
            strong_correlations = []
            moderate_correlations = []
            weak_correlations = []

            thresholds = self.correlation_config["thresholds"]

            for pair, score in correlations.items():
                if score >= thresholds["strong"]:
                    strong_correlations.append({"pair": pair, "score": score})
                elif score >= thresholds["moderate"]:
                    moderate_correlations.append({"pair": pair, "score": score})
                elif score >= thresholds["weak"]:
                    weak_correlations.append({"pair": pair, "score": score})

            # Identify correlation clusters
            clusters = self._identify_correlation_clusters(correlation_matrix)

            # Identify isolated channels
            isolated = self._identify_isolated_channels(correlation_matrix)

            patterns = {
                "strong_correlations": strong_correlations,
                "moderate_correlations": moderate_correlations,
                "weak_correlations": weak_correlations,
                "clusters": clusters,
                "isolated_channels": isolated,
                "summary": {
                    "total_pairs": len(correlations),
                    "strong_count": len(strong_correlations),
                    "moderate_count": len(moderate_correlations),
                    "weak_count": len(weak_correlations),
                },
            }

            logger.info(
                f"📈 Identified {len(clusters)} correlation clusters, {len(isolated)} isolated channels"
            )
            return patterns

        except Exception as e:
            logger.error(f"Pattern identification failed: {e}")
            return {"patterns": [], "clusters": [], "isolated": [], "error": str(e)}

    def _identify_correlation_clusters(
        self, correlation_matrix: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Identify groups of highly correlated channels (clusters).

        Uses simple clustering based on correlation threshold.
        """
        correlations = correlation_matrix.get("correlations", {})
        threshold = self.correlation_config["thresholds"]["strong"]

        # Build adjacency list for channels with strong correlations
        adjacency: dict[str, list[str]] = defaultdict(list)

        for pair, score in correlations.items():
            if score >= threshold:
                channel_a, channel_b = pair.split("_")
                adjacency[channel_a].append(channel_b)
                adjacency[channel_b].append(channel_a)

        # Find connected components (clusters)
        clusters = []
        visited = set()

        for channel in adjacency:
            if channel not in visited:
                # BFS to find cluster
                cluster = []
                queue = [channel]

                while queue:
                    current = queue.pop(0)
                    if current not in visited:
                        visited.add(current)
                        cluster.append(current)
                        queue.extend(adjacency[current])

                if len(cluster) > 1:
                    avg_correlation = self._calculate_cluster_avg_correlation(
                        cluster, correlation_matrix
                    )
                    clusters.append(
                        {
                            "channels": cluster,
                            "size": len(cluster),
                            "avg_correlation": avg_correlation,
                        }
                    )

        return sorted(clusters, key=lambda x: x["avg_correlation"], reverse=True)

    def _calculate_cluster_avg_correlation(
        self, cluster: list[str], correlation_matrix: dict[str, Any]
    ) -> float:
        """Calculate average correlation within a cluster."""
        correlations = correlation_matrix.get("correlations", {})
        cluster_correlations = []

        for i, channel_a in enumerate(cluster):
            for channel_b in cluster[i + 1 :]:
                pair_key = f"{channel_a}_{channel_b}"
                reverse_key = f"{channel_b}_{channel_a}"

                if pair_key in correlations:
                    cluster_correlations.append(correlations[pair_key])
                elif reverse_key in correlations:
                    cluster_correlations.append(correlations[reverse_key])

        if cluster_correlations:
            return sum(cluster_correlations) / len(cluster_correlations)
        return 0.0

    def _identify_isolated_channels(self, correlation_matrix: dict[str, Any]) -> list[str]:
        """
        Identify channels with no strong correlations (isolated).
        """
        correlations = correlation_matrix.get("correlations", {})
        threshold = self.correlation_config["thresholds"]["moderate"]

        # Track channels with at least one moderate correlation
        connected_channels = set()

        for pair, score in correlations.items():
            if score >= threshold:
                channel_a, channel_b = pair.split("_")
                connected_channels.add(channel_a)
                connected_channels.add(channel_b)

        # Find isolated channels
        all_channels = {str(ch) for ch in correlation_matrix.get("channels", [])}
        isolated = list(all_channels - connected_channels)

        return isolated

    def calculate_correlation_confidence(
        self,
        correlation_matrix: dict[str, Any],
        channels_data: dict[int, dict[str, Any]],
    ) -> float:
        """
        Calculate confidence score for correlation analysis.

        Factors:
        - Data quality and completeness
        - Sample size (number of channels)
        - Correlation consistency
        - Time series depth
        """
        try:
            # Data quality assessment
            data_quality = self._assess_data_quality(channels_data)

            # Sample size factor (more channels = more confidence)
            num_channels = len(channels_data)
            sample_factor = min(num_channels / 10, 1.0)  # Normalize to max 1.0

            # Correlation consistency
            consistency = self._calculate_correlation_consistency(correlation_matrix)

            # Weighted confidence score
            confidence = data_quality * 0.4 + sample_factor * 0.3 + consistency * 0.3

            return round(confidence, 3)

        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5  # Default medium confidence

    def _calculate_correlation_consistency(self, correlation_matrix: dict[str, Any]) -> float:
        """
        Measure how consistent correlations are (low variance = high consistency).
        """
        correlations = list(correlation_matrix.get("correlations", {}).values())

        if not correlations:
            return 0.5

        # Calculate variance
        mean_corr = sum(correlations) / len(correlations)
        variance = sum((c - mean_corr) ** 2 for c in correlations) / len(correlations)
        std_dev = variance**0.5

        # Convert to consistency score (lower std_dev = higher consistency)
        consistency = max(0.0, 1.0 - std_dev)

        return round(consistency, 3)

    def _assess_data_quality(self, channels_data: dict[int, dict[str, Any]]) -> float:
        """
        Assess data quality and completeness.
        """
        if not channels_data:
            return 0.0

        total_quality = 0.0

        for channel_data in channels_data.values():
            metrics = channel_data.get("metrics", {})

            # Check for required metrics
            has_engagement = "engagement_rate" in metrics
            has_growth = "growth_rate" in metrics
            has_audience = "audience_size" in metrics
            has_platform = "platform" in channel_data

            # Calculate completeness score
            completeness = sum([has_engagement, has_growth, has_audience, has_platform]) / 4
            total_quality += completeness

        avg_quality = total_quality / len(channels_data)
        return round(avg_quality, 3)

    async def health_check(self) -> dict[str, Any]:
        """Health check for correlation analysis service."""
        return {
            "service": "CorrelationAnalysisService",
            "status": "operational",
            "cache_size": len(self.correlation_cache),
            "config_loaded": bool(self.correlation_config),
            "timestamp": datetime.now().isoformat(),
        }
