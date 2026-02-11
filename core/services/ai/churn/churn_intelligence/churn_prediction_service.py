"""
Churn Prediction Service
========================

Core microservice for predicting user churn risk and analyzing churn patterns.

Single Responsibility:
- User churn risk assessment
- Cohort churn analysis
- Channel-level churn analytics
- Behavioral pattern analysis for churn prediction

This service focuses purely on prediction logic without retention strategies.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from .protocols.churn_protocols import (
    ChurnAnalytics,
    ChurnPredictionProtocol,
    ChurnRiskLevel,
    ChurnRiskProfile,
    ChurnStage,
    ConfidenceLevel,
)

logger = logging.getLogger(__name__)


class ChurnPredictionService(ChurnPredictionProtocol):
    """
    Core churn prediction microservice.

    Focuses on analyzing user behavior patterns and predicting churn probability
    using multiple signals and machine learning models.
    """

    def __init__(self, config_manager=None):
        """Initialize churn prediction service"""
        self.config_manager = config_manager

        # Risk thresholds
        self.risk_thresholds = {
            "very_low": 0.1,
            "low": 0.25,
            "medium": 0.5,
            "high": 0.75,
            "very_high": 0.9,
        }

        # Behavioral weights for risk calculation
        self.behavioral_weights = {
            "session_frequency": 0.3,
            "feature_usage": 0.25,
            "interaction_quality": 0.2,
            "recency": 0.15,
            "engagement_trend": 0.1,
        }

        # Cache for predictions
        self.prediction_cache: dict[str, ChurnRiskProfile] = {}
        self.cache_ttl_hours = 6

        logger.info("ChurnPredictionService initialized")

    async def predict_user_churn_risk(
        self, user_id: int, channel_id: int, analysis_days: int = 30
    ) -> ChurnRiskProfile:
        """
        Predict churn risk for a specific user based on behavioral analysis.

        Args:
            user_id: User identifier
            channel_id: Channel identifier
            analysis_days: Days of historical data to analyze

        Returns:
            ChurnRiskProfile with comprehensive risk assessment
        """
        try:
            # Check cache first
            cache_key = f"{user_id}_{channel_id}_{analysis_days}"
            if self._is_prediction_cached(cache_key):
                logger.debug(f"Returning cached prediction for user {user_id}")
                return self.prediction_cache[cache_key]

            # Gather behavioral data
            behavioral_data = await self._collect_user_behavioral_data(
                user_id, channel_id, analysis_days
            )

            # Calculate risk components
            engagement_score = self._calculate_engagement_score(behavioral_data)
            recency_risk = self._calculate_recency_risk(behavioral_data)
            trend_risk = self._calculate_trend_risk(behavioral_data)

            # Composite risk calculation
            churn_probability = self._calculate_composite_risk(
                engagement_score, recency_risk, trend_risk, behavioral_data
            )

            # Determine risk level and stage
            risk_level = self._classify_risk_level(churn_probability)
            current_stage = self._determine_lifecycle_stage(behavioral_data, risk_level)

            # Generate risk profile
            risk_profile = ChurnRiskProfile(
                user_id=user_id,
                channel_id=channel_id,
                risk_level=risk_level,
                churn_probability=churn_probability,
                confidence=self._calculate_confidence(behavioral_data),
                current_stage=current_stage,
                engagement_score=engagement_score,
                activity_trend=behavioral_data.get("activity_trend", "stable"),
                last_active=behavioral_data.get("last_active", datetime.now()),
                days_since_active=behavioral_data.get("days_since_active", 0),
                session_frequency_decline=behavioral_data.get("session_decline", 0.0),
                feature_usage_decline=behavioral_data.get("feature_decline", 0.0),
                interaction_quality_score=behavioral_data.get("interaction_quality", 0.5),
                risk_factors=self._identify_risk_factors(behavioral_data),
                protective_factors=self._identify_protective_factors(behavioral_data),
                trigger_events=behavioral_data.get("trigger_events", []),
                analysis_timestamp=datetime.now(),
                prediction_horizon_days=analysis_days,
            )

            # Cache the prediction
            self.prediction_cache[cache_key] = risk_profile

            logger.info(
                f"Predicted churn risk for user {user_id}: "
                f"{risk_level.value} ({churn_probability:.3f})"
            )

            return risk_profile

        except Exception as e:
            logger.error(f"Error predicting churn risk for user {user_id}: {e}")
            # Return safe default
            return ChurnRiskProfile(
                user_id=user_id,
                channel_id=channel_id,
                risk_level=ChurnRiskLevel.LOW,
                churn_probability=0.1,
                confidence=ConfidenceLevel.LOW,
                analysis_timestamp=datetime.now(),
            )

    async def analyze_cohort_churn_risk(
        self,
        channel_id: int,
        user_ids: list[int] | None = None,
        risk_threshold: ChurnRiskLevel = ChurnRiskLevel.MEDIUM,
    ) -> list[ChurnRiskProfile]:
        """
        Analyze churn risk for a cohort of users.

        Args:
            channel_id: Channel identifier
            user_ids: Specific users to analyze (if None, analyze all active users)
            risk_threshold: Minimum risk level to include in results

        Returns:
            List of ChurnRiskProfile objects above threshold
        """
        try:
            # Get user list
            if user_ids is None:
                user_ids = await self._get_active_channel_users(channel_id)

            # Analyze each user
            risk_profiles = []
            for user_id in user_ids:
                profile = await self.predict_user_churn_risk(user_id, channel_id)

                # Filter by threshold
                if self._meets_risk_threshold(profile.risk_level, risk_threshold):
                    risk_profiles.append(profile)

            # Sort by risk level (highest first)
            risk_profiles.sort(key=lambda p: p.churn_probability, reverse=True)

            logger.info(
                f"Analyzed cohort churn risk: {len(risk_profiles)} users "
                f"above {risk_threshold.value} threshold"
            )

            return risk_profiles

        except Exception as e:
            logger.error(f"Error analyzing cohort churn risk: {e}")
            return []

    async def get_channel_churn_analytics(
        self, channel_id: int, analysis_days: int = 30
    ) -> ChurnAnalytics:
        """
        Get comprehensive churn analytics for a channel.

        Args:
            channel_id: Channel identifier
            analysis_days: Analysis period in days

        Returns:
            ChurnAnalytics with comprehensive channel metrics
        """
        try:
            # Get all users for analysis
            user_ids = await self._get_active_channel_users(channel_id)

            # Analyze all users
            risk_profiles = []
            for user_id in user_ids:
                profile = await self.predict_user_churn_risk(user_id, channel_id, analysis_days)
                risk_profiles.append(profile)

            # Calculate analytics
            analytics = await self._calculate_channel_analytics(
                channel_id, risk_profiles, analysis_days
            )

            logger.info(
                f"Generated channel analytics for {channel_id}: "
                f"{analytics.churn_rate:.2%} churn rate"
            )

            return analytics

        except Exception as e:
            logger.error(f"Error generating channel analytics: {e}")
            return ChurnAnalytics(
                analysis_id=str(uuid.uuid4()),
                channel_id=channel_id,
                churn_rate=0.0,
                retention_rate=1.0,
                timestamp=datetime.now(),
            )

    # Private helper methods

    def _is_prediction_cached(self, cache_key: str) -> bool:
        """Check if prediction is cached and still valid"""
        if cache_key not in self.prediction_cache:
            return False

        prediction = self.prediction_cache[cache_key]
        cache_age = datetime.now() - prediction.analysis_timestamp
        return cache_age < timedelta(hours=self.cache_ttl_hours)

    async def _collect_user_behavioral_data(
        self, user_id: int, channel_id: int, analysis_days: int
    ) -> dict[str, Any]:
        """Collect comprehensive behavioral data for analysis"""
        # In a real implementation, this would query the database
        # For now, return simulated data structure

        import random

        now = datetime.now()
        last_active = now - timedelta(days=random.randint(0, 14))

        return {
            "user_id": user_id,
            "channel_id": channel_id,
            "last_active": last_active,
            "days_since_active": (now - last_active).days,
            "session_count_30d": random.randint(5, 50),
            "session_count_7d": random.randint(1, 15),
            "avg_session_duration": random.uniform(2.0, 30.0),
            "feature_usage_count": random.randint(2, 20),
            "message_count": random.randint(10, 200),
            "interaction_quality": random.uniform(0.2, 0.9),
            "session_decline": random.uniform(-0.2, 0.4),
            "feature_decline": random.uniform(-0.1, 0.3),
            "activity_trend": random.choice(["increasing", "stable", "declining"]),
            "trigger_events": [],
            "engagement_history": [random.uniform(0.3, 0.8) for _ in range(30)],
        }

    def _calculate_engagement_score(self, behavioral_data: dict[str, Any]) -> float:
        """Calculate comprehensive engagement score"""
        session_score = min(behavioral_data.get("session_count_30d", 0) / 30, 1.0)
        duration_score = min(behavioral_data.get("avg_session_duration", 0) / 20, 1.0)
        feature_score = min(behavioral_data.get("feature_usage_count", 0) / 15, 1.0)
        interaction_score = behavioral_data.get("interaction_quality", 0.5)

        return (
            session_score * 0.3
            + duration_score * 0.25
            + feature_score * 0.25
            + interaction_score * 0.2
        )

    def _calculate_recency_risk(self, behavioral_data: dict[str, Any]) -> float:
        """Calculate risk based on recency of activity"""
        days_since_active = behavioral_data.get("days_since_active", 0)
        if days_since_active <= 1:
            return 0.0
        elif days_since_active <= 3:
            return 0.2
        elif days_since_active <= 7:
            return 0.5
        elif days_since_active <= 14:
            return 0.8
        else:
            return 1.0

    def _calculate_trend_risk(self, behavioral_data: dict[str, Any]) -> float:
        """Calculate risk based on activity trends"""
        trend = behavioral_data.get("activity_trend", "stable")
        session_decline = behavioral_data.get("session_decline", 0.0)
        feature_decline = behavioral_data.get("feature_decline", 0.0)

        if trend == "increasing":
            return max(0.0, (session_decline + feature_decline) * 0.3)
        elif trend == "stable":
            return max(0.1, (session_decline + feature_decline) * 0.5)
        else:  # declining
            return min(1.0, 0.6 + (session_decline + feature_decline) * 0.4)

    def _calculate_composite_risk(
        self,
        engagement_score: float,
        recency_risk: float,
        trend_risk: float,
        behavioral_data: dict[str, Any],
    ) -> float:
        """Calculate composite churn probability"""
        # Invert engagement score to get risk
        engagement_risk = 1.0 - engagement_score

        # Weighted combination
        composite_risk = engagement_risk * 0.4 + recency_risk * 0.35 + trend_risk * 0.25

        # Apply behavioral modifiers
        interaction_quality = behavioral_data.get("interaction_quality", 0.5)
        if interaction_quality < 0.3:
            composite_risk += 0.1

        return min(1.0, max(0.0, composite_risk))

    def _classify_risk_level(self, churn_probability: float) -> ChurnRiskLevel:
        """Classify numeric probability into risk level"""
        if churn_probability < self.risk_thresholds["very_low"]:
            return ChurnRiskLevel.VERY_LOW
        elif churn_probability < self.risk_thresholds["low"]:
            return ChurnRiskLevel.LOW
        elif churn_probability < self.risk_thresholds["medium"]:
            return ChurnRiskLevel.MEDIUM
        elif churn_probability < self.risk_thresholds["high"]:
            return ChurnRiskLevel.HIGH
        elif churn_probability < self.risk_thresholds["very_high"]:
            return ChurnRiskLevel.VERY_HIGH
        else:
            return ChurnRiskLevel.CRITICAL

    def _determine_lifecycle_stage(
        self, behavioral_data: dict[str, Any], risk_level: ChurnRiskLevel
    ) -> ChurnStage:
        """Determine current lifecycle stage"""
        days_since_active = behavioral_data.get("days_since_active", 0)
        trend = behavioral_data.get("activity_trend", "stable")

        if days_since_active > 30:
            return ChurnStage.CHURNED
        elif risk_level in [
            ChurnRiskLevel.HIGH,
            ChurnRiskLevel.VERY_HIGH,
            ChurnRiskLevel.CRITICAL,
        ]:
            return ChurnStage.AT_RISK
        elif trend == "declining" or risk_level == ChurnRiskLevel.MEDIUM:
            return ChurnStage.DECLINING
        else:
            return ChurnStage.ACTIVE

    def _calculate_confidence(self, behavioral_data: dict[str, Any]) -> ConfidenceLevel:
        """Calculate confidence in prediction based on data quality"""
        data_points = len([v for v in behavioral_data.values() if v is not None])

        if data_points >= 8:
            return ConfidenceLevel.VERY_HIGH
        elif data_points >= 6:
            return ConfidenceLevel.HIGH
        elif data_points >= 4:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _identify_risk_factors(self, behavioral_data: dict[str, Any]) -> list[str]:
        """Identify specific risk factors"""
        factors = []

        if behavioral_data.get("days_since_active", 0) > 7:
            factors.append("Extended inactivity period")

        if behavioral_data.get("session_decline", 0) > 0.2:
            factors.append("Significant session frequency decline")

        if behavioral_data.get("feature_decline", 0) > 0.1:
            factors.append("Reduced feature engagement")

        if behavioral_data.get("interaction_quality", 1.0) < 0.4:
            factors.append("Low interaction quality")

        if behavioral_data.get("activity_trend") == "declining":
            factors.append("Declining activity trend")

        return factors

    def _identify_protective_factors(self, behavioral_data: dict[str, Any]) -> list[str]:
        """Identify factors that reduce churn risk"""
        factors = []

        if behavioral_data.get("session_count_30d", 0) > 20:
            factors.append("High session frequency")

        if behavioral_data.get("feature_usage_count", 0) > 10:
            factors.append("Diverse feature usage")

        if behavioral_data.get("interaction_quality", 0) > 0.7:
            factors.append("High interaction quality")

        if behavioral_data.get("activity_trend") == "increasing":
            factors.append("Increasing activity trend")

        return factors

    def _meets_risk_threshold(self, risk_level: ChurnRiskLevel, threshold: ChurnRiskLevel) -> bool:
        """Check if risk level meets or exceeds threshold"""
        risk_order = [
            ChurnRiskLevel.VERY_LOW,
            ChurnRiskLevel.LOW,
            ChurnRiskLevel.MEDIUM,
            ChurnRiskLevel.HIGH,
            ChurnRiskLevel.VERY_HIGH,
            ChurnRiskLevel.CRITICAL,
        ]

        return risk_order.index(risk_level) >= risk_order.index(threshold)

    async def _get_active_channel_users(self, channel_id: int) -> list[int]:
        """Get list of active users in channel"""
        # In real implementation, query database
        # For now, return simulated user list
        import random

        return [i for i in range(1, random.randint(50, 200))]

    async def _calculate_channel_analytics(
        self, channel_id: int, risk_profiles: list[ChurnRiskProfile], analysis_days: int
    ) -> ChurnAnalytics:
        """Calculate comprehensive channel analytics"""
        total_users = len(risk_profiles)

        if total_users == 0:
            return ChurnAnalytics(
                analysis_id=str(uuid.uuid4()),
                channel_id=channel_id,
                total_users_analyzed=0,
                churn_rate=0.0,
                retention_rate=1.0,
                timestamp=datetime.now(),
            )

        # Risk distribution
        risk_distribution = {}
        stage_distribution = {}

        for risk_level in ChurnRiskLevel:
            risk_distribution[risk_level] = sum(
                1 for p in risk_profiles if p.risk_level == risk_level
            )

        for stage in ChurnStage:
            stage_distribution[stage] = sum(1 for p in risk_profiles if p.current_stage == stage)

        # Calculate metrics
        high_risk_users = sum(
            1
            for p in risk_profiles
            if p.risk_level
            in [ChurnRiskLevel.HIGH, ChurnRiskLevel.VERY_HIGH, ChurnRiskLevel.CRITICAL]
        )

        churn_rate = high_risk_users / total_users
        retention_rate = 1.0 - churn_rate

        # Projected churn
        projected_churn = sum(int(p.churn_probability > 0.5) for p in risk_profiles)

        return ChurnAnalytics(
            analysis_id=str(uuid.uuid4()),
            channel_id=channel_id,
            analysis_period={
                "start": datetime.now() - timedelta(days=analysis_days),
                "end": datetime.now(),
            },
            total_users_analyzed=total_users,
            churn_rate=churn_rate,
            retention_rate=retention_rate,
            risk_distribution=risk_distribution,
            stage_distribution=stage_distribution,
            primary_churn_drivers=[
                "Extended inactivity",
                "Declining engagement",
                "Reduced feature usage",
            ],
            retention_opportunities=[
                "Engagement campaigns",
                "Feature education",
                "Personalized content",
            ],
            projected_churn_next_30days=projected_churn,
            recommended_interventions=high_risk_users,
            timestamp=datetime.now(),
        )
