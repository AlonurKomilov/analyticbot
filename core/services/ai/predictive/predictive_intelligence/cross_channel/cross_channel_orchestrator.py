"""
Cross-Channel Analysis Orchestrator
====================================

Lightweight orchestrator coordinating cross-channel analysis microservices.

Single Responsibility:
- Coordinate correlation, influence, and integration services
- Aggregate cross-channel intelligence
- Provide unified API interface
- Handle data fetching and caching

This replaces the original 1,608-line CrossChannelAnalysisService with
a clean orchestrator pattern coordinating 3 focused microservices.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from ..protocols.predictive_protocols import (
    ConfidenceLevel,
    CrossChannelAnalysisProtocol,
    CrossChannelIntelligence,
)
from .channel_influence_service import ChannelInfluenceService
from .correlation_analysis_service import CorrelationAnalysisService
from .integration_opportunity_service import IntegrationOpportunityService

logger = logging.getLogger(__name__)


class CrossChannelOrchestrator(CrossChannelAnalysisProtocol):
    """
    Lightweight orchestrator for cross-channel analysis.

    Coordinates 3 focused microservices:
    - CorrelationAnalysisService: Channel correlations
    - ChannelInfluenceService: Influence mapping
    - IntegrationOpportunityService: Integration patterns

    Lines: ~400 (vs original 1,608 lines)
    """

    def __init__(self, analytics_service=None, data_access_service=None, config_manager=None):
        self.analytics_service = analytics_service
        self.data_access_service = data_access_service
        self.config_manager = config_manager

        # Initialize microservices
        self.correlation_service = CorrelationAnalysisService(config_manager)
        self.influence_service = ChannelInfluenceService(config_manager)
        self.integration_service = IntegrationOpportunityService(config_manager)

        # Orchestrator cache
        self.analysis_cache: dict[str, CrossChannelIntelligence] = {}
        # Cache stores channel data with metadata (allow Any for flexibility)
        self.data_cache: dict[str, dict[Any, Any]] = {}

        logger.info("🔗 Cross-Channel Orchestrator initialized with 3 microservices")

    async def analyze_cross_channel_intelligence(
        self, channel_predictions: dict[str, Any]
    ) -> CrossChannelIntelligence:
        """
        Main orchestration method for comprehensive cross-channel analysis.

        Coordinates all three microservices to produce unified intelligence.

        Args:
            channel_predictions: Dict containing channel_ids and optional prediction data

        Returns:
            Unified cross-channel intelligence
        """
        try:
            # Extract channel IDs from predictions dict
            channel_ids = channel_predictions.get("channel_ids", [])

            if not channel_ids:
                logger.warning("No channel_ids provided in channel_predictions")
                return self._create_empty_intelligence([])

            logger.info(
                f"🎯 Starting cross-channel intelligence analysis for {len(channel_ids)} channels"
            )

            # Get channels data
            channels_data = await self._get_channels_data(channel_ids)

            if not channels_data:
                logger.warning("No channel data available")
                return self._create_empty_intelligence(channel_ids)

            # Step 1: Calculate correlations
            logger.info("📊 Step 1/4: Calculating correlations...")
            correlation_matrix = await self.correlation_service.calculate_correlation_matrix(
                channels_data
            )
            correlation_patterns = self.correlation_service.identify_correlation_patterns(
                correlation_matrix
            )

            # Step 2: Map influences
            logger.info("🎯 Step 2/4: Mapping influence relationships...")
            influence_relationships = (
                await self.influence_service.calculate_influence_relationships(
                    channels_data, correlation_matrix
                )
            )
            strongest_influences = self.influence_service.identify_strongest_influences(
                influence_relationships
            )

            # Step 3: Identify integration opportunities
            logger.info("🔗 Step 3/4: Identifying integration opportunities...")
            integration_opportunities = (
                await self.integration_service.identify_integration_opportunities(
                    channels_data, correlation_patterns, influence_relationships
                )
            )

            # Step 4: Generate recommendations
            logger.info("💡 Step 4/4: Generating recommendations...")
            recommendations = self.integration_service.generate_integration_recommendations(
                integration_opportunities, top_n=5
            )

            # Calculate overall confidence
            correlation_confidence = self.correlation_service.calculate_correlation_confidence(
                correlation_matrix, channels_data
            )

            # Create unified intelligence (all fields are optional with defaults)
            intelligence = CrossChannelIntelligence()
            intelligence.analysis_id = f"cross_channel_{uuid.uuid4().hex[:8]}"
            intelligence.channel_ids = channel_ids
            intelligence.correlation_matrix = correlation_matrix
            intelligence.influence_patterns = influence_relationships
            intelligence.recommendations = [str(rec) for rec in recommendations]
            intelligence.confidence = self._map_confidence_level(correlation_confidence)
            intelligence.timestamp = datetime.now()

            # Cache results
            cache_key = (
                f"analysis_{'-'.join(map(str, channel_ids))}_{datetime.now().strftime('%Y%m%d')}"
            )
            self.analysis_cache[cache_key] = intelligence

            logger.info(
                f"✅ Cross-channel intelligence analysis completed - {len(recommendations)} recommendations"
            )
            return intelligence

        except Exception as e:
            logger.error(f"❌ Cross-channel intelligence analysis failed: {e}", exc_info=True)
            # Extract channel_ids again in case of early failure
            fail_channel_ids = channel_predictions.get("channel_ids", [])
            return self._create_error_intelligence(fail_channel_ids, str(e))

    async def calculate_channel_correlations(
        self, channel_predictions: dict[str, Any]
    ) -> dict[str, dict[str, float]]:
        """
        Calculate correlations between channels (protocol method).

        Delegates to CorrelationAnalysisService.

        Args:
            channel_predictions: Dict containing channel_ids and optional prediction data

        Returns:
            Nested dict of channel-to-channel correlations
        """
        try:
            # Extract channel IDs
            channel_ids = channel_predictions.get("channel_ids", [])

            if not channel_ids:
                return {}

            logger.info(f"📊 Calculating channel correlations for {len(channel_ids)} channels")

            channels_data = await self._get_channels_data(channel_ids)

            if not channels_data:
                # Return empty dict matching protocol return type
                return {}

            correlation_matrix = await self.correlation_service.calculate_correlation_matrix(
                channels_data
            )

            # Convert to protocol-expected format: Dict[str, Dict[str, float]]
            correlations_dict: dict[str, dict[str, float]] = {}

            for channel_id in channel_ids:
                correlations_dict[str(channel_id)] = {}
                for other_id in channel_ids:
                    if channel_id != other_id:
                        pair_key = f"{min(channel_id, other_id)}_{max(channel_id, other_id)}"
                        score = correlation_matrix.get("correlations", {}).get(pair_key, 0.0)
                        correlations_dict[str(channel_id)][str(other_id)] = float(score)

            return correlations_dict

        except Exception as e:
            logger.error(f"❌ Correlation calculation failed: {e}")
            return {}

    async def analyze_influence_patterns(
        self, predictions: dict[str, Any], correlations: dict[str, dict[str, float]]
    ) -> dict[str, Any]:
        """
        Analyze influence patterns between channels (protocol method).

        Delegates to ChannelInfluenceService.

        Args:
            predictions: Dict containing channel_ids and prediction data
            correlations: Pre-calculated correlations

        Returns:
            Dict with influence patterns and insights
        """
        try:
            # Extract channel IDs
            channel_ids = predictions.get("channel_ids", [])

            if not channel_ids:
                return {"influences": {}}

            logger.info(f"🎯 Analyzing influence patterns for {len(channel_ids)} channels")

            channels_data = await self._get_channels_data(channel_ids)

            if not channels_data:
                return {"influences": {}, "error": "No channel data available"}

            influence_relationships = (
                await self.influence_service.calculate_influence_relationships(channels_data)
            )
            strongest_influences = self.influence_service.identify_strongest_influences(
                influence_relationships
            )
            insights = self.influence_service.generate_influence_insights(
                influence_relationships, channels_data
            )

            return {
                "influence_relationships": influence_relationships,
                "strongest_influences": strongest_influences,
                "insights": insights,
                "quality": self.influence_service.assess_influence_analysis_quality(
                    influence_relationships
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Influence analysis failed: {e}")
            return {"influences": {}, "error": str(e)}

    async def identify_cross_promotion_opportunities(
        self, predictions: dict[str, Any], correlations: dict[str, dict[str, float]]
    ) -> list[dict[str, Any]]:
        """
        Identify cross-promotion opportunities (protocol method).

        Delegates to IntegrationOpportunityService.

        Args:
            predictions: Dict containing channel_ids and prediction data
            correlations: Pre-calculated correlations

        Returns:
            List of cross-promotion opportunities
        """
        try:
            # Extract channel IDs
            channel_ids = predictions.get("channel_ids", [])

            if not channel_ids:
                return []

            logger.info(
                f"🔗 Identifying cross-promotion opportunities for {len(channel_ids)} channels"
            )

            channels_data = await self._get_channels_data(channel_ids)

            if not channels_data:
                return []

            # Get all integration opportunities
            opportunities = await self.integration_service.identify_integration_opportunities(
                channels_data
            )

            # Filter for cross-promotion type
            cross_promo_opportunities = [
                opp for opp in opportunities if opp.get("type") == "cross_promotion"
            ]

            # Generate recommendations
            recommendations = self.integration_service.generate_integration_recommendations(
                cross_promo_opportunities, top_n=10
            )

            return recommendations

        except Exception as e:
            logger.error(f"❌ Cross-promotion identification failed: {e}")
            return []

    async def _get_channels_data(self, channel_ids: list[int]) -> dict[int, dict[str, Any]]:
        """
        Fetch channel data for analysis.

        Checks cache first, then fetches from data sources.
        """
        cache_key = f"data_{'-'.join(map(str, sorted(channel_ids)))}"

        # Check cache
        if cache_key in self.data_cache:
            cached_entry = self.data_cache[cache_key]
            # Check if cache has timestamp and is still valid
            if "_cache_time" in cached_entry:
                cache_time_value = cached_entry.get("_cache_time")  # type: ignore
                if (
                    isinstance(cache_time_value, datetime)
                    and (datetime.now() - cache_time_value).seconds < 3600
                ):  # 1 hour cache
                    logger.debug(f"Using cached channel data for {len(channel_ids)} channels")
                    # Return data without cache metadata (filter out string keys from int Dict)
                    data: dict[int, dict[str, Any]] = {}
                    for k, v in cached_entry.items():
                        if k != "_cache_time" and isinstance(k, int):
                            data[k] = v
                    return data

        # Fetch fresh data
        channels_data = {}

        for channel_id in channel_ids:
            try:
                # Try to fetch from data access service
                if self.data_access_service:
                    channel_data = await self._fetch_channel_data(channel_id)
                    if channel_data:
                        channels_data[channel_id] = channel_data
                        continue

                # Fallback to mock data
                channels_data[channel_id] = self._generate_mock_channel_data(channel_id)

            except Exception as e:
                logger.warning(f"Failed to fetch data for channel {channel_id}: {e}")
                channels_data[channel_id] = self._generate_mock_channel_data(channel_id)

        # Cache the data
        cached_data = dict(channels_data)
        cached_data["_cache_time"] = datetime.now()
        self.data_cache[cache_key] = cached_data

        return channels_data

    async def _fetch_channel_data(self, channel_id: int) -> dict[str, Any] | None:
        """
        Fetch channel data from data access service.

        Future: implement actual data fetching logic.
        """
        # Placeholder for actual data fetching
        return None

    def _generate_mock_channel_data(self, channel_id: int) -> dict[str, Any]:
        """
        Generate mock channel data for testing/development.
        """
        import random

        platforms = ["telegram", "youtube", "twitter", "instagram", "discord", "linkedin"]

        return {
            "channel_id": channel_id,
            "platform": random.choice(platforms),
            "metrics": {
                "audience_size": random.randint(1000, 100000),
                "engagement_rate": round(random.uniform(0.02, 0.15), 3),
                "growth_rate": round(random.uniform(-0.05, 0.25), 3),
                "posts_per_day": random.randint(1, 10),
                "avg_reach": random.randint(500, 50000),
            },
            "last_updated": datetime.now().isoformat(),
        }

    def _create_empty_intelligence(self, channel_ids: list[int]) -> CrossChannelIntelligence:
        """Create empty intelligence result for error cases."""
        intelligence = CrossChannelIntelligence()
        intelligence.analysis_id = f"empty_{uuid.uuid4().hex[:8]}"
        intelligence.channel_ids = channel_ids
        intelligence.correlation_matrix = {}
        intelligence.influence_patterns = {}
        intelligence.recommendations = []
        intelligence.confidence = ConfidenceLevel.LOW
        intelligence.timestamp = datetime.now()
        return intelligence

    def _create_error_intelligence(
        self, channel_ids: list[int], error_message: str
    ) -> CrossChannelIntelligence:
        """Create error intelligence result."""
        intelligence = CrossChannelIntelligence()
        intelligence.analysis_id = f"error_{uuid.uuid4().hex[:8]}"
        intelligence.channel_ids = channel_ids
        intelligence.correlation_matrix = {"error": error_message}
        intelligence.influence_patterns = {}
        intelligence.recommendations = [f"Error: {error_message}"]
        intelligence.confidence = ConfidenceLevel.LOW
        intelligence.timestamp = datetime.now()
        return intelligence

    def _map_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """Map numeric confidence to ConfidenceLevel enum."""
        if confidence_score >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.6:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    async def health_check(self) -> dict[str, Any]:
        """
        Comprehensive health check for orchestrator and all microservices.
        """
        try:
            # Check all microservices
            correlation_health = await self.correlation_service.health_check()
            influence_health = await self.influence_service.health_check()
            integration_health = await self.integration_service.health_check()

            all_operational = all(
                [
                    correlation_health.get("status") == "operational",
                    influence_health.get("status") == "operational",
                    integration_health.get("status") == "operational",
                ]
            )

            return {
                "service_name": "CrossChannelOrchestrator",
                "status": "operational" if all_operational else "degraded",
                "version": "2.0.0",
                "architecture": "microservices",
                "microservices": {
                    "correlation_analysis": correlation_health,
                    "influence_analysis": influence_health,
                    "integration_opportunities": integration_health,
                },
                "cache_stats": {
                    "analysis_cache_size": len(self.analysis_cache),
                    "data_cache_size": len(self.data_cache),
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "service_name": "CrossChannelOrchestrator",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
