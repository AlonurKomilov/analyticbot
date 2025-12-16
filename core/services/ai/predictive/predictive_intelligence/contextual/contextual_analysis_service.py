"""
Contextual Analysis Service
===========================

Focused microservice for contextual intelligence analysis.

Single Responsibility:
- Environmental context analysis
- Competitive landscape analysis
- Behavioral pattern context
- Context factor integration
- Context confidence scoring

Core capabilities extracted from PredictiveIntelligenceService contextual analysis methods.
"""

import logging
from datetime import datetime
from typing import Any

from ..protocols.predictive_protocols import (
    ContextualAnalysisProtocol,
    ContextualIntelligence,
    IntelligenceContext,
)

logger = logging.getLogger(__name__)


class ContextualAnalysisService(ContextualAnalysisProtocol):
    """
    Contextual analysis microservice for intelligence context factors.

    Single responsibility: Analyze contextual factors for enhanced predictions only.
    """

    def __init__(self, analytics_service=None, market_data_service=None, config_manager=None):
        self.analytics_service = analytics_service
        self.market_data_service = market_data_service
        self.config_manager = config_manager

        # Contextual analysis configuration
        self.context_config = {
            "environmental_factors": [
                "market_conditions",
                "economic_indicators",
                "seasonal_effects",
                "external_events",
            ],
            "competitive_factors": [
                "competitor_activity",
                "market_share_changes",
                "pricing_dynamics",
                "industry_trends",
            ],
            "behavioral_factors": [
                "user_engagement_patterns",
                "content_preferences",
                "interaction_trends",
                "demographic_shifts",
            ],
            "confidence_weights": {
                "environmental": 0.25,
                "competitive": 0.30,
                "behavioral": 0.35,
                "temporal": 0.10,
            },
        }

        # Context caches for performance
        self._context_cache = {}
        self._cache_ttl_minutes = 30

        logger.info("🌍 Contextual Analysis Service initialized - intelligence context focus")

    async def analyze_context_factors(
        self, prediction_request: dict[str, Any], context_types: list[IntelligenceContext]
    ) -> ContextualIntelligence:
        """
        Analyze contextual factors for predictions.

        Main orchestration method for contextual intelligence analysis.
        """
        try:
            logger.info(f"🔍 Analyzing context factors: {[ctx.value for ctx in context_types]}")

            contextual_intelligence = ContextualIntelligence()
            contextual_intelligence.analysis_timestamp = datetime.now().isoformat()

            # Analyze each requested context type
            for context_type in context_types:
                if context_type == IntelligenceContext.ENVIRONMENTAL:
                    environmental_context = await self.analyze_environmental_context(
                        prediction_request
                    )
                    contextual_intelligence.environmental_factors = environmental_context

                elif context_type == IntelligenceContext.COMPETITIVE:
                    competitive_context = await self.analyze_competitive_context(prediction_request)
                    contextual_intelligence.competitive_landscape = competitive_context

                elif context_type == IntelligenceContext.BEHAVIORAL:
                    behavioral_context = await self.analyze_behavioral_context(prediction_request)
                    contextual_intelligence.behavioral_insights = behavioral_context

                elif context_type == IntelligenceContext.TEMPORAL:
                    temporal_context = await self._analyze_temporal_context_factors(
                        prediction_request
                    )
                    contextual_intelligence.temporal_patterns = temporal_context

                elif context_type == IntelligenceContext.SEASONAL:
                    seasonal_context = await self._analyze_seasonal_context_factors(
                        prediction_request
                    )
                    contextual_intelligence.environmental_factors["seasonal"] = seasonal_context

            # Calculate overall context confidence
            contextual_intelligence.context_confidence = self._calculate_context_confidence(
                contextual_intelligence, context_types
            )

            logger.info(
                f"✅ Context analysis completed - Confidence: {contextual_intelligence.context_confidence:.2f}"
            )
            return contextual_intelligence

        except Exception as e:
            logger.error(f"❌ Context factor analysis failed: {e}")
            return ContextualIntelligence(
                analysis_timestamp=datetime.now().isoformat(), context_confidence=0.0
            )

    async def analyze_environmental_context(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze environmental context factors.
        """
        try:
            logger.info("🌿 Analyzing environmental context")

            channel_id = request.get("channel_id", 0)
            analysis_period = request.get("analysis_period", {})

            # Market conditions analysis
            market_conditions = await self._analyze_market_conditions(channel_id)

            # Economic indicators
            economic_indicators = await self._analyze_economic_indicators()

            # Seasonal effects
            seasonal_effects = await self._analyze_seasonal_effects(analysis_period)

            # External events impact
            external_events = await self._analyze_external_events_impact(channel_id)

            environmental_context = {
                "market_conditions": market_conditions,
                "economic_indicators": economic_indicators,
                "seasonal_effects": seasonal_effects,
                "external_events": external_events,
                "environmental_score": self._calculate_environmental_score(
                    market_conditions, economic_indicators, seasonal_effects, external_events
                ),
                "context_strength": "high"
                if market_conditions.get("stability", 0) > 0.7
                else "medium",
            }

            logger.info("✅ Environmental context analysis completed")
            return environmental_context

        except Exception as e:
            logger.error(f"❌ Environmental context analysis failed: {e}")
            return {"analysis_error": str(e), "environmental_score": 0.0}

    async def analyze_competitive_context(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze competitive landscape context.
        """
        try:
            logger.info("🏆 Analyzing competitive context")

            channel_id = request.get("channel_id", 0)

            # Competitor activity analysis
            competitor_activity = await self._analyze_competitor_activity(channel_id)

            # Market share dynamics
            market_share_changes = await self._analyze_market_share_changes(channel_id)

            # Pricing dynamics
            pricing_dynamics = await self._analyze_pricing_dynamics(channel_id)

            # Industry trends
            industry_trends = await self._analyze_industry_trends()

            competitive_context = {
                "competitor_activity": competitor_activity,
                "market_share_changes": market_share_changes,
                "pricing_dynamics": pricing_dynamics,
                "industry_trends": industry_trends,
                "competitive_pressure": self._calculate_competitive_pressure(
                    competitor_activity, market_share_changes, pricing_dynamics
                ),
                "market_position": self._assess_market_position(market_share_changes),
                "competitive_threats": self._identify_competitive_threats(competitor_activity),
                "competitive_opportunities": self._identify_competitive_opportunities(
                    industry_trends
                ),
            }

            logger.info("✅ Competitive context analysis completed")
            return competitive_context

        except Exception as e:
            logger.error(f"❌ Competitive context analysis failed: {e}")
            return {"analysis_error": str(e), "competitive_pressure": 0.5}

    async def analyze_behavioral_context(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze behavioral pattern context.
        """
        try:
            logger.info("👥 Analyzing behavioral context")

            channel_id = request.get("channel_id", 0)

            # User engagement patterns
            engagement_patterns = await self._analyze_engagement_patterns(channel_id)

            # Content preferences
            content_preferences = await self._analyze_content_preferences(channel_id)

            # Interaction trends
            interaction_trends = await self._analyze_interaction_trends(channel_id)

            # Demographic shifts
            demographic_shifts = await self._analyze_demographic_shifts(channel_id)

            behavioral_context = {
                "engagement_patterns": engagement_patterns,
                "content_preferences": content_preferences,
                "interaction_trends": interaction_trends,
                "demographic_shifts": demographic_shifts,
                "behavioral_stability": self._calculate_behavioral_stability(
                    engagement_patterns, interaction_trends
                ),
                "engagement_momentum": self._calculate_engagement_momentum(engagement_patterns),
                "content_fit_score": self._calculate_content_fit_score(content_preferences),
                "audience_evolution": self._assess_audience_evolution(demographic_shifts),
            }

            logger.info("✅ Behavioral context analysis completed")
            return behavioral_context

        except Exception as e:
            logger.error(f"❌ Behavioral context analysis failed: {e}")
            return {"analysis_error": str(e), "behavioral_stability": 0.5}

    async def _analyze_temporal_context_factors(self, request: dict[str, Any]) -> dict[str, Any]:
        """Analyze temporal context factors"""
        try:
            current_time = datetime.now()

            # Time-based context factors
            temporal_context = {
                "hour_of_day_impact": self._calculate_hour_impact(current_time.hour),
                "day_of_week_impact": self._calculate_day_impact(current_time.weekday()),
                "seasonal_impact": self._calculate_seasonal_impact(current_time),
                "time_context_strength": 0.8,
                "temporal_stability": "high",
            }

            return temporal_context

        except Exception as e:
            logger.error(f"❌ Temporal context analysis failed: {e}")
            return {"hour_of_day_impact": 1.0, "day_of_week_impact": 1.0, "seasonal_impact": 1.0}

    async def _analyze_seasonal_context_factors(self, request: dict[str, Any]) -> dict[str, Any]:
        """Analyze seasonal context factors"""
        try:
            current_time = datetime.now()

            seasonal_context = {
                "season": self._get_current_season(current_time),
                "holiday_proximity": self._calculate_holiday_proximity(current_time),
                "seasonal_trends": await self._get_seasonal_trends(),
                "seasonal_multiplier": self._calculate_seasonal_multiplier(current_time),
            }

            return seasonal_context

        except Exception as e:
            logger.error(f"❌ Seasonal context analysis failed: {e}")
            return {"season": "unknown", "seasonal_multiplier": 1.0}

    async def _analyze_market_conditions(self, channel_id: int) -> dict[str, Any]:
        """Analyze current market conditions"""
        # Mock market conditions analysis
        return {
            "market_volatility": 0.3,  # Low volatility
            "market_trend": "stable_growth",
            "stability": 0.8,
            "growth_rate": 0.12,
            "market_sentiment": "positive",
        }

    async def _analyze_economic_indicators(self) -> dict[str, Any]:
        """Analyze relevant economic indicators"""
        # Mock economic indicators
        return {
            "gdp_growth": 0.025,  # 2.5% quarterly
            "inflation_rate": 0.032,  # 3.2% annually
            "unemployment_rate": 0.045,  # 4.5%
            "consumer_confidence": 0.72,  # 72/100
            "economic_outlook": "moderately_positive",
        }

    async def _analyze_seasonal_effects(self, analysis_period: dict[str, Any]) -> dict[str, Any]:
        """Analyze seasonal effects"""
        current_time = datetime.now()

        return {
            "current_season": self._get_current_season(current_time),
            "seasonal_strength": 0.6,
            "holiday_effect": self._calculate_holiday_proximity(current_time),
            "seasonal_trend": "increasing"
            if current_time.month in [3, 4, 5, 9, 10, 11]
            else "stable",
        }

    async def _analyze_external_events_impact(self, channel_id: int) -> dict[str, Any]:
        """Analyze impact of external events"""
        # Mock external events analysis
        return {
            "recent_events": [
                {"event": "industry_conference", "impact": 0.15, "duration_days": 7},
                {"event": "competitor_product_launch", "impact": -0.08, "duration_days": 14},
            ],
            "total_impact": 0.07,
            "event_uncertainty": 0.2,
        }

    async def _analyze_competitor_activity(self, channel_id: int) -> dict[str, Any]:
        """Analyze competitor activity patterns"""
        # Mock competitor analysis
        return {
            "activity_level": 0.7,  # High activity
            "content_frequency": 1.2,  # 20% increase
            "engagement_strategy": "aggressive",
            "pricing_pressure": 0.3,
            "new_entrants": 2,
        }

    async def _analyze_market_share_changes(self, channel_id: int) -> dict[str, Any]:
        """Analyze market share dynamics"""
        # Mock market share analysis
        return {
            "current_share": 0.18,  # 18% market share
            "share_change_30d": 0.02,  # +2% increase
            "share_trend": "growing",
            "competitive_positioning": "strong",
        }

    async def _analyze_pricing_dynamics(self, channel_id: int) -> dict[str, Any]:
        """Analyze pricing dynamics in the market"""
        # Mock pricing analysis
        return {
            "price_elasticity": 0.8,
            "pricing_pressure": 0.4,  # Moderate pressure
            "price_optimization_opportunity": 0.15,
            "competitor_pricing_trend": "stable",
        }

    async def _analyze_industry_trends(self) -> dict[str, Any]:
        """Analyze broader industry trends"""
        # Mock industry trends analysis
        return {
            "growth_rate": 0.08,  # 8% annual growth
            "technological_disruption": 0.3,
            "regulatory_changes": 0.1,
            "market_maturity": "growth_phase",
        }

    async def _analyze_engagement_patterns(self, channel_id: int) -> dict[str, Any]:
        """Analyze user engagement patterns"""
        # Mock engagement analysis
        return {
            "engagement_rate": 0.045,  # 4.5%
            "engagement_trend": "increasing",
            "peak_engagement_hours": [9, 12, 18, 21],
            "engagement_consistency": 0.8,
        }

    async def _analyze_content_preferences(self, channel_id: int) -> dict[str, Any]:
        """Analyze content preferences"""
        # Mock content preferences analysis
        return {
            "preferred_content_types": ["educational", "entertaining", "promotional"],
            "content_performance_variance": 0.3,
            "trending_topics": ["ai", "sustainability", "productivity"],
            "content_saturation": 0.6,
        }

    async def _analyze_interaction_trends(self, channel_id: int) -> dict[str, Any]:
        """Analyze interaction trends"""
        # Mock interaction trends analysis
        return {
            "interaction_growth": 0.12,  # 12% growth
            "interaction_types": {"likes": 0.6, "comments": 0.25, "shares": 0.15},
            "interaction_quality": 0.75,
            "community_health": "good",
        }

    async def _analyze_demographic_shifts(self, channel_id: int) -> dict[str, Any]:
        """Analyze demographic shifts"""
        # Mock demographic analysis
        return {
            "age_distribution_shift": {"18-25": -0.05, "26-35": 0.08, "36-45": 0.02},
            "geographic_expansion": 0.15,
            "demographic_stability": 0.7,
            "target_audience_alignment": 0.85,
        }

    async def _get_seasonal_trends(self) -> dict[str, Any]:
        """Get seasonal trends data"""
        return {
            "spring": {"growth_multiplier": 1.15, "engagement_boost": 0.2},
            "summer": {"growth_multiplier": 0.95, "engagement_boost": -0.1},
            "fall": {"growth_multiplier": 1.25, "engagement_boost": 0.3},
            "winter": {"growth_multiplier": 1.05, "engagement_boost": 0.1},
        }

    def _calculate_context_confidence(
        self,
        contextual_intelligence: ContextualIntelligence,
        context_types: list[IntelligenceContext],
    ) -> float:
        """Calculate overall context confidence score"""
        confidence_scores = []
        weights = self.context_config["confidence_weights"]

        # Environmental confidence
        if IntelligenceContext.ENVIRONMENTAL in context_types:
            env_score = contextual_intelligence.environmental_factors.get("environmental_score", 0)
            confidence_scores.append(env_score * weights["environmental"])

        # Competitive confidence
        if IntelligenceContext.COMPETITIVE in context_types:
            comp_pressure = contextual_intelligence.competitive_landscape.get(
                "competitive_pressure", 0.5
            )
            confidence_scores.append((1.0 - abs(comp_pressure - 0.5) * 2) * weights["competitive"])

        # Behavioral confidence
        if IntelligenceContext.BEHAVIORAL in context_types:
            behavioral_stability = contextual_intelligence.behavioral_insights.get(
                "behavioral_stability", 0.5
            )
            confidence_scores.append(behavioral_stability * weights["behavioral"])

        # Temporal confidence
        if IntelligenceContext.TEMPORAL in context_types:
            temporal_strength = contextual_intelligence.temporal_patterns.get(
                "time_context_strength", 0.5
            )
            confidence_scores.append(temporal_strength * weights["temporal"])

        return sum(confidence_scores) if confidence_scores else 0.0

    def _calculate_environmental_score(
        self, market_conditions, economic_indicators, seasonal_effects, external_events
    ) -> float:
        """Calculate environmental context score"""
        market_score = market_conditions.get("stability", 0.5)
        economic_score = economic_indicators.get("consumer_confidence", 0.5)
        seasonal_score = seasonal_effects.get("seasonal_strength", 0.5)
        events_score = 1.0 - abs(external_events.get("total_impact", 0))

        return market_score * 0.3 + economic_score * 0.3 + seasonal_score * 0.2 + events_score * 0.2

    def _calculate_competitive_pressure(
        self, competitor_activity, market_share_changes, pricing_dynamics
    ) -> float:
        """Calculate competitive pressure score"""
        activity_pressure = competitor_activity.get("activity_level", 0.5)
        share_pressure = 1.0 - market_share_changes.get("current_share", 0.5)
        pricing_pressure = pricing_dynamics.get("pricing_pressure", 0.5)

        return activity_pressure * 0.4 + share_pressure * 0.3 + pricing_pressure * 0.3

    def _assess_market_position(self, market_share_changes) -> str:
        """Assess market position based on share changes"""
        current_share = market_share_changes.get("current_share", 0.1)
        share_trend = market_share_changes.get("share_trend", "stable")

        if current_share > 0.3:
            return "market_leader"
        elif current_share > 0.15 and share_trend == "growing":
            return "strong_challenger"
        elif current_share > 0.05:
            return "established_player"
        else:
            return "niche_player"

    def _identify_competitive_threats(self, competitor_activity) -> list[str]:
        """Identify competitive threats"""
        threats = []

        if competitor_activity.get("activity_level", 0) > 0.7:
            threats.append("high_competitor_activity")
        if competitor_activity.get("pricing_pressure", 0) > 0.6:
            threats.append("aggressive_pricing")
        if competitor_activity.get("new_entrants", 0) > 1:
            threats.append("market_entry_pressure")

        return threats

    def _identify_competitive_opportunities(self, industry_trends) -> list[str]:
        """Identify competitive opportunities"""
        opportunities = []

        if industry_trends.get("growth_rate", 0) > 0.05:
            opportunities.append("market_growth")
        if industry_trends.get("technological_disruption", 0) > 0.5:
            opportunities.append("technology_advantage")
        if industry_trends.get("market_maturity", "") == "growth_phase":
            opportunities.append("expansion_opportunity")

        return opportunities

    def _calculate_behavioral_stability(self, engagement_patterns, interaction_trends) -> float:
        """Calculate behavioral pattern stability"""
        engagement_consistency = engagement_patterns.get("engagement_consistency", 0.5)
        interaction_quality = interaction_trends.get("interaction_quality", 0.5)

        return (engagement_consistency + interaction_quality) / 2

    def _calculate_engagement_momentum(self, engagement_patterns) -> str:
        """Calculate engagement momentum"""
        trend = engagement_patterns.get("engagement_trend", "stable")
        rate = engagement_patterns.get("engagement_rate", 0.03)

        if trend == "increasing" and rate > 0.04:
            return "strong_positive"
        elif trend == "increasing":
            return "positive"
        elif trend == "stable" and rate > 0.04:
            return "stable_high"
        elif trend == "stable":
            return "stable"
        else:
            return "declining"

    def _calculate_content_fit_score(self, content_preferences) -> float:
        """Calculate content fit score"""
        variance = content_preferences.get("content_performance_variance", 0.5)
        saturation = content_preferences.get("content_saturation", 0.5)

        # Lower variance and moderate saturation = higher fit
        return (1.0 - variance) * (1.0 - abs(saturation - 0.5))

    def _assess_audience_evolution(self, demographic_shifts) -> str:
        """Assess audience evolution patterns"""
        stability = demographic_shifts.get("demographic_stability", 0.5)
        alignment = demographic_shifts.get("target_audience_alignment", 0.5)

        if stability > 0.8 and alignment > 0.8:
            return "optimal_stable"
        elif stability < 0.5 and alignment > 0.7:
            return "positive_evolution"
        elif stability > 0.7:
            return "stable"
        else:
            return "dynamic_changing"

    def _calculate_hour_impact(self, hour: int) -> float:
        """Calculate hour of day impact factor"""
        # Peak hours: 9-11, 18-21
        if hour in [9, 10, 18, 19, 20]:
            return 1.3
        elif hour in [8, 11, 12, 17, 21]:
            return 1.1
        elif hour in [7, 13, 14, 15, 16, 22]:
            return 1.0
        else:
            return 0.7

    def _calculate_day_impact(self, weekday: int) -> float:
        """Calculate day of week impact factor"""
        # Monday=0, Sunday=6
        weekday_impacts = [1.0, 1.1, 1.2, 1.15, 1.1, 0.9, 0.8]  # Mon-Sun
        return weekday_impacts[weekday]

    def _calculate_seasonal_impact(self, current_time: datetime) -> float:
        """Calculate seasonal impact factor"""
        month = current_time.month

        # Spring (Mar-May): High growth
        if month in [3, 4, 5]:
            return 1.15
        # Summer (Jun-Aug): Moderate decline
        elif month in [6, 7, 8]:
            return 0.95
        # Fall (Sep-Nov): Peak season
        elif month in [9, 10, 11]:
            return 1.25
        # Winter (Dec-Feb): Moderate growth
        else:
            return 1.05

    def _get_current_season(self, current_time: datetime) -> str:
        """Get current season"""
        month = current_time.month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "fall"
        else:
            return "winter"

    def _calculate_holiday_proximity(self, current_time: datetime) -> float:
        """Calculate holiday proximity effect"""
        # Mock holiday proximity calculation
        return 0.1  # 10% holiday boost

    def _calculate_seasonal_multiplier(self, current_time: datetime) -> float:
        """Calculate seasonal multiplier"""
        return self._calculate_seasonal_impact(current_time)

    async def health_check(self) -> dict[str, Any]:
        """Health check for contextual analysis service"""
        return {
            "service_name": "ContextualAnalysisService",
            "status": "operational",
            "version": "1.0.0",
            "type": "microservice",
            "responsibility": "contextual_intelligence_analysis",
            "capabilities": [
                "environmental_context_analysis",
                "competitive_context_analysis",
                "behavioral_context_analysis",
                "temporal_context_analysis",
                "seasonal_context_analysis",
                "context_confidence_scoring",
            ],
            "context_config": self.context_config,
            "cache_entries": len(self._context_cache),
        }
