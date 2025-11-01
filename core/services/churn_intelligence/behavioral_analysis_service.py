"""
Behavioral Analysis Service
==========================

Microservice for analyzing user behavioral patterns related to churn prediction.

Single Responsibility:
- Analyze engagement patterns and trends
- Detect churn trigger events
- Calculate engagement scores and behavioral metrics
- Identify behavioral anomalies that indicate churn risk

Provides the behavioral intelligence foundation for churn prediction.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from .protocols.churn_protocols import BehavioralAnalysisProtocol

logger = logging.getLogger(__name__)


class BehavioralAnalysisService(BehavioralAnalysisProtocol):
    """
    Microservice for behavioral pattern analysis in churn context.

    Analyzes user behavior patterns, engagement trends, and interaction quality
    to provide insights for churn prediction and retention strategies.
    """

    def __init__(self, config_manager=None):
        """Initialize behavioral analysis service"""
        self.config_manager = config_manager

        # Engagement scoring weights
        self.engagement_weights = {
            "session_frequency": 0.25,
            "session_duration": 0.20,
            "feature_diversity": 0.20,
            "interaction_depth": 0.15,
            "content_consumption": 0.10,
            "social_engagement": 0.10,
        }

        # Behavioral anomaly thresholds
        self.anomaly_thresholds = {
            "session_drop_threshold": 0.3,  # 30% drop in sessions
            "duration_drop_threshold": 0.4,  # 40% drop in session duration
            "feature_usage_drop": 0.25,  # 25% drop in feature usage
            "interaction_quality_drop": 0.2,  # 20% drop in interaction quality
        }

        # Common churn triggers
        self.churn_trigger_patterns = [
            "sudden_activity_drop",
            "feature_abandonment",
            "support_ticket_unresolved",
            "negative_feedback_spike",
            "competitor_interaction",
            "price_sensitivity_signals",
        ]

        logger.info("BehavioralAnalysisService initialized")

    async def analyze_engagement_patterns(
        self, user_id: int, channel_id: int, lookback_days: int = 90
    ) -> dict[str, Any]:
        """
        Analyze user engagement patterns for churn signals.

        Args:
            user_id: User identifier
            channel_id: Channel identifier
            lookback_days: Days of historical data to analyze

        Returns:
            Comprehensive engagement pattern analysis
        """
        try:
            # Collect behavioral data
            behavioral_data = await self._collect_user_behavioral_data(
                user_id, channel_id, lookback_days
            )

            # Analyze different pattern dimensions
            session_patterns = await self._analyze_session_patterns(behavioral_data)
            feature_patterns = await self._analyze_feature_usage_patterns(behavioral_data)
            interaction_patterns = await self._analyze_interaction_patterns(behavioral_data)
            temporal_patterns = await self._analyze_temporal_patterns(behavioral_data)

            # Calculate trend analysis
            trend_analysis = await self._calculate_engagement_trends(behavioral_data)

            # Detect behavioral anomalies
            anomalies = await self._detect_behavioral_anomalies(behavioral_data)

            # Generate engagement score
            engagement_score = await self._calculate_comprehensive_engagement_score(behavioral_data)

            # Compile analysis results
            analysis_results = {
                "user_id": user_id,
                "channel_id": channel_id,
                "analysis_period": {
                    "start_date": datetime.now() - timedelta(days=lookback_days),
                    "end_date": datetime.now(),
                    "days_analyzed": lookback_days,
                },
                "engagement_score": engagement_score,
                "session_patterns": session_patterns,
                "feature_patterns": feature_patterns,
                "interaction_patterns": interaction_patterns,
                "temporal_patterns": temporal_patterns,
                "trend_analysis": trend_analysis,
                "behavioral_anomalies": anomalies,
                "churn_risk_indicators": self._identify_churn_risk_indicators(
                    session_patterns, feature_patterns, interaction_patterns, anomalies
                ),
                "analysis_timestamp": datetime.now(),
            }

            logger.info(
                f"Analyzed engagement patterns for user {user_id}: "
                f"score={engagement_score:.3f}, anomalies={len(anomalies)}"
            )

            return analysis_results

        except Exception as e:
            logger.error(f"Error analyzing engagement patterns for user {user_id}: {e}")
            return {
                "user_id": user_id,
                "channel_id": channel_id,
                "error": str(e),
                "analysis_timestamp": datetime.now(),
            }

    async def detect_churn_triggers(
        self, channel_id: int, analysis_period_days: int = 30
    ) -> list[dict[str, Any]]:
        """
        Detect common churn trigger events across the channel.

        Args:
            channel_id: Channel identifier
            analysis_period_days: Period to analyze for triggers

        Returns:
            List of detected churn trigger patterns
        """
        try:
            # Get channel user activity data
            channel_data = await self._collect_channel_behavioral_data(
                channel_id, analysis_period_days
            )

            # Detect different types of triggers
            triggers = []

            # Sudden activity drops
            activity_drop_triggers = await self._detect_activity_drop_triggers(channel_data)
            triggers.extend(activity_drop_triggers)

            # Feature abandonment patterns
            feature_abandonment_triggers = await self._detect_feature_abandonment_triggers(
                channel_data
            )
            triggers.extend(feature_abandonment_triggers)

            # Support and feedback triggers
            support_triggers = await self._detect_support_related_triggers(channel_data)
            triggers.extend(support_triggers)

            # Competitive triggers
            competitive_triggers = await self._detect_competitive_triggers(channel_data)
            triggers.extend(competitive_triggers)

            # Sort by impact and frequency
            triggers.sort(
                key=lambda t: t.get("impact_score", 0) * t.get("frequency", 0),
                reverse=True,
            )

            logger.info(
                f"Detected {len(triggers)} churn triggers for channel {channel_id} "
                f"over {analysis_period_days} days"
            )

            return triggers

        except Exception as e:
            logger.error(f"Error detecting churn triggers for channel {channel_id}: {e}")
            return []

    async def calculate_engagement_scores(
        self, user_ids: list[int], channel_id: int
    ) -> dict[int, float]:
        """
        Calculate engagement scores for multiple users.

        Args:
            user_ids: List of user identifiers
            channel_id: Channel identifier

        Returns:
            Dictionary mapping user_id to engagement score
        """
        try:
            engagement_scores = {}

            for user_id in user_ids:
                # Get recent behavioral data
                behavioral_data = await self._collect_user_behavioral_data(
                    user_id, channel_id, lookback_days=30
                )

                # Calculate engagement score
                score = await self._calculate_comprehensive_engagement_score(behavioral_data)

                engagement_scores[user_id] = score

            logger.info(
                f"Calculated engagement scores for {len(user_ids)} users in channel {channel_id}"
            )

            return engagement_scores

        except Exception as e:
            logger.error(f"Error calculating engagement scores: {e}")
            return {}

    # Private helper methods

    async def _collect_user_behavioral_data(
        self, user_id: int, channel_id: int, lookback_days: int
    ) -> dict[str, Any]:
        """Collect comprehensive user behavioral data"""
        # In real implementation, this would query database
        # For now, simulate behavioral data

        import random

        now = datetime.now()

        # Simulate session data
        sessions = []
        for i in range(lookback_days):
            date = now - timedelta(days=i)
            if random.random() > 0.3:  # User was active this day
                sessions.append(
                    {
                        "date": date,
                        "session_count": random.randint(1, 5),
                        "total_duration": random.uniform(5, 120),  # minutes
                        "features_used": random.randint(1, 8),
                        "interactions": random.randint(2, 50),
                        "quality_score": random.uniform(0.2, 0.9),
                    }
                )

        return {
            "user_id": user_id,
            "channel_id": channel_id,
            "sessions": sessions,
            "total_sessions": len(sessions),
            "active_days": len(sessions),
            "avg_session_duration": sum(s["total_duration"] for s in sessions)
            / max(len(sessions), 1),
            "total_features_used": len(set(range(random.randint(3, 15)))),
            "avg_interactions_per_session": sum(s["interactions"] for s in sessions)
            / max(len(sessions), 1),
            "recent_activity": sessions[:7] if sessions else [],
            "data_collection_timestamp": now,
        }

    async def _analyze_session_patterns(self, behavioral_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze user session patterns"""
        sessions = behavioral_data.get("sessions", [])

        if not sessions:
            return {"pattern_type": "inactive", "sessions_analyzed": 0}

        # Calculate session metrics
        session_counts = [s["session_count"] for s in sessions]
        session_durations = [s["total_duration"] for s in sessions]

        # Analyze trends
        recent_sessions = sessions[:14]  # Last 2 weeks
        older_sessions = sessions[14:28] if len(sessions) > 14 else []

        recent_avg = sum(s["session_count"] for s in recent_sessions) / max(len(recent_sessions), 1)
        older_avg = (
            sum(s["session_count"] for s in older_sessions) / max(len(older_sessions), 1)
            if older_sessions
            else recent_avg
        )

        frequency_trend = (recent_avg - older_avg) / max(older_avg, 0.1)

        return {
            "pattern_type": "regular" if len(sessions) > 20 else "sporadic",
            "sessions_analyzed": len(sessions),
            "avg_sessions_per_day": sum(session_counts) / len(session_counts),
            "avg_session_duration": sum(session_durations) / len(session_durations),
            "frequency_trend": frequency_trend,
            "consistency_score": 1.0 - (len(set(session_counts)) / max(len(session_counts), 1)),
            "last_session_days_ago": (
                (datetime.now() - sessions[0]["date"]).days if sessions else 999
            ),
        }

    async def _analyze_feature_usage_patterns(
        self, behavioral_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze feature usage patterns"""
        sessions = behavioral_data.get("sessions", [])

        if not sessions:
            return {"feature_diversity": 0, "usage_trend": "no_data"}

        # Calculate feature usage metrics
        feature_counts = [s["features_used"] for s in sessions]
        total_features = behavioral_data.get("total_features_used", 0)

        # Trend analysis
        recent_features = feature_counts[:7]
        older_features = feature_counts[7:14] if len(feature_counts) > 7 else []

        recent_avg = sum(recent_features) / max(len(recent_features), 1)
        older_avg = (
            sum(older_features) / max(len(older_features), 1) if older_features else recent_avg
        )

        usage_trend = (recent_avg - older_avg) / max(older_avg, 0.1)

        return {
            "feature_diversity": total_features,
            "avg_features_per_session": sum(feature_counts) / len(feature_counts),
            "usage_trend": usage_trend,
            "feature_exploration_score": min(total_features / 10, 1.0),  # Normalized to 10 features
            "usage_consistency": 1.0 - (len(set(feature_counts)) / max(len(feature_counts), 1)),
        }

    async def _analyze_interaction_patterns(
        self, behavioral_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze interaction quality patterns"""
        sessions = behavioral_data.get("sessions", [])

        if not sessions:
            return {"interaction_quality": 0, "engagement_depth": "low"}

        # Calculate interaction metrics
        interactions = [s["interactions"] for s in sessions]
        quality_scores = [s["quality_score"] for s in sessions]

        avg_interactions = sum(interactions) / len(interactions)
        avg_quality = sum(quality_scores) / len(quality_scores)

        # Determine engagement depth
        if avg_quality > 0.7 and avg_interactions > 20:
            depth = "high"
        elif avg_quality > 0.5 and avg_interactions > 10:
            depth = "medium"
        else:
            depth = "low"

        return {
            "interaction_quality": avg_quality,
            "avg_interactions_per_session": avg_interactions,
            "engagement_depth": depth,
            "quality_trend": self._calculate_trend(quality_scores),
            "interaction_trend": self._calculate_trend(interactions),
        }

    async def _analyze_temporal_patterns(self, behavioral_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze temporal usage patterns"""
        sessions = behavioral_data.get("sessions", [])

        if not sessions:
            return {"pattern": "inactive", "regularity": 0}

        # Analyze usage timing
        active_days = len(sessions)
        total_days = len(behavioral_data.get("sessions", [])) + 10  # Include inactive days

        activity_rate = active_days / max(total_days, 1)

        # Analyze recent vs historical activity
        recent_activity = len([s for s in sessions[:7]])  # Last week
        historical_activity = len([s for s in sessions[7:21]])  # Previous 2 weeks

        recency_score = recent_activity / 7.0  # Normalize to daily rate

        return {
            "pattern": "regular" if activity_rate > 0.6 else "sporadic",
            "activity_rate": activity_rate,
            "recency_score": recency_score,
            "regularity": min(activity_rate * 2, 1.0),
            "days_since_last_activity": (
                (datetime.now() - sessions[0]["date"]).days if sessions else 999
            ),
        }

    async def _calculate_engagement_trends(self, behavioral_data: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall engagement trends"""
        sessions = behavioral_data.get("sessions", [])

        if len(sessions) < 7:
            return {"trend": "insufficient_data", "direction": "unknown"}

        # Calculate weekly engagement scores
        weekly_scores = []
        for week_start in range(0, min(len(sessions), 28), 7):
            week_sessions = sessions[week_start : week_start + 7]
            if week_sessions:
                week_score = sum(
                    s["session_count"] * s["quality_score"] for s in week_sessions
                ) / len(week_sessions)
                weekly_scores.append(week_score)

        if len(weekly_scores) < 2:
            return {"trend": "stable", "direction": "none"}

        # Calculate trend
        trend_slope = (weekly_scores[0] - weekly_scores[-1]) / len(weekly_scores)

        if trend_slope > 0.1:
            direction = "improving"
        elif trend_slope < -0.1:
            direction = "declining"
        else:
            direction = "stable"

        return {
            "trend": direction,
            "direction": direction,
            "slope": trend_slope,
            "weekly_scores": weekly_scores,
            "volatility": self._calculate_volatility(weekly_scores),
        }

    async def _detect_behavioral_anomalies(
        self, behavioral_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Detect behavioral anomalies that may indicate churn risk"""
        sessions = behavioral_data.get("sessions", [])
        anomalies = []

        if len(sessions) < 10:
            return anomalies

        # Detect sudden activity drops
        recent_activity = len(sessions[:7])
        historical_activity = len(sessions[7:21]) / 2  # Average over 2 weeks

        if historical_activity > 0 and recent_activity / historical_activity < (
            1 - self.anomaly_thresholds["session_drop_threshold"]
        ):
            anomalies.append(
                {
                    "type": "sudden_activity_drop",
                    "severity": "high",
                    "description": f"Session frequency dropped by {(1 - recent_activity / historical_activity) * 100:.1f}%",
                    "detected_at": datetime.now(),
                }
            )

        # Detect feature usage drops
        recent_features = [s["features_used"] for s in sessions[:7]]
        historical_features = [s["features_used"] for s in sessions[7:21]]

        if recent_features and historical_features:
            recent_avg = sum(recent_features) / len(recent_features)
            historical_avg = sum(historical_features) / len(historical_features)

            if historical_avg > 0 and recent_avg / historical_avg < (
                1 - self.anomaly_thresholds["feature_usage_drop"]
            ):
                anomalies.append(
                    {
                        "type": "feature_usage_decline",
                        "severity": "medium",
                        "description": f"Feature usage dropped by {(1 - recent_avg / historical_avg) * 100:.1f}%",
                        "detected_at": datetime.now(),
                    }
                )

        # Detect interaction quality drops
        recent_quality = [s["quality_score"] for s in sessions[:7]]
        historical_quality = [s["quality_score"] for s in sessions[7:21]]

        if recent_quality and historical_quality:
            recent_avg = sum(recent_quality) / len(recent_quality)
            historical_avg = sum(historical_quality) / len(historical_quality)

            if historical_avg > 0 and recent_avg / historical_avg < (
                1 - self.anomaly_thresholds["interaction_quality_drop"]
            ):
                anomalies.append(
                    {
                        "type": "interaction_quality_decline",
                        "severity": "medium",
                        "description": f"Interaction quality dropped by {(1 - recent_avg / historical_avg) * 100:.1f}%",
                        "detected_at": datetime.now(),
                    }
                )

        return anomalies

    async def _calculate_comprehensive_engagement_score(
        self, behavioral_data: dict[str, Any]
    ) -> float:
        """Calculate comprehensive engagement score"""
        sessions = behavioral_data.get("sessions", [])

        if not sessions:
            return 0.0

        # Session frequency score
        active_days = len(sessions)
        frequency_score = min(active_days / 30, 1.0)  # Normalize to 30 days

        # Session duration score
        avg_duration = sum(s["total_duration"] for s in sessions) / len(sessions)
        duration_score = min(avg_duration / 60, 1.0)  # Normalize to 60 minutes

        # Feature diversity score
        total_features = behavioral_data.get("total_features_used", 0)
        diversity_score = min(total_features / 10, 1.0)  # Normalize to 10 features

        # Interaction depth score
        avg_interactions = sum(s["interactions"] for s in sessions) / len(sessions)
        interaction_score = min(avg_interactions / 30, 1.0)  # Normalize to 30 interactions

        # Content consumption score (simulated)
        content_score = 0.5  # Would be calculated from actual content metrics

        # Social engagement score (simulated)
        social_score = 0.5  # Would be calculated from social interactions

        # Weighted combination
        engagement_score = (
            frequency_score * self.engagement_weights["session_frequency"]
            + duration_score * self.engagement_weights["session_duration"]
            + diversity_score * self.engagement_weights["feature_diversity"]
            + interaction_score * self.engagement_weights["interaction_depth"]
            + content_score * self.engagement_weights["content_consumption"]
            + social_score * self.engagement_weights["social_engagement"]
        )

        return min(1.0, max(0.0, engagement_score))

    def _identify_churn_risk_indicators(
        self,
        session_patterns: dict,
        feature_patterns: dict,
        interaction_patterns: dict,
        anomalies: list,
    ) -> list[str]:
        """Identify specific churn risk indicators"""
        indicators = []

        # Session-based indicators
        if session_patterns.get("frequency_trend", 0) < -0.2:
            indicators.append("Declining session frequency")

        if session_patterns.get("last_session_days_ago", 0) > 7:
            indicators.append("Extended period of inactivity")

        # Feature-based indicators
        if feature_patterns.get("usage_trend", 0) < -0.15:
            indicators.append("Declining feature engagement")

        if feature_patterns.get("feature_diversity", 0) < 3:
            indicators.append("Limited feature adoption")

        # Interaction-based indicators
        if interaction_patterns.get("interaction_quality", 1) < 0.4:
            indicators.append("Low interaction quality")

        if interaction_patterns.get("engagement_depth") == "low":
            indicators.append("Shallow engagement patterns")

        # Anomaly-based indicators
        for anomaly in anomalies:
            if anomaly.get("severity") == "high":
                indicators.append(f"Behavioral anomaly: {anomaly.get('type', 'unknown')}")

        return indicators

    def _calculate_trend(self, values: list[float]) -> float:
        """Calculate trend slope for a series of values"""
        if len(values) < 2:
            return 0.0

        # Simple linear trend calculation
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x_squared_sum = sum(i * i for i in range(n))

        slope = (n * xy_sum - x_sum * y_sum) / (n * x_squared_sum - x_sum * x_sum)
        return slope

    def _calculate_volatility(self, values: list[float]) -> float:
        """Calculate volatility (standard deviation) of values"""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance**0.5

    async def _collect_channel_behavioral_data(
        self, channel_id: int, analysis_period_days: int
    ) -> dict[str, Any]:
        """Collect behavioral data for entire channel"""
        # Simulate channel-wide behavioral data collection
        # In real implementation, aggregate user behaviors

        import random

        return {
            "channel_id": channel_id,
            "analysis_period_days": analysis_period_days,
            "total_users": random.randint(100, 1000),
            "active_users": random.randint(50, 500),
            "churned_users_period": random.randint(5, 50),
            "support_tickets": random.randint(10, 100),
            "negative_feedback": random.randint(2, 20),
            "feature_adoption_rates": {f"feature_{i}": random.uniform(0.1, 0.9) for i in range(5)},
            "competitor_mentions": random.randint(0, 10),
        }

    async def _detect_activity_drop_triggers(
        self, channel_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Detect activity drop patterns that trigger churn"""
        triggers = []

        # Simulate trigger detection
        if channel_data.get("churned_users_period", 0) > 20:
            triggers.append(
                {
                    "type": "sudden_activity_drop",
                    "description": "Significant increase in user activity drops detected",
                    "impact_score": 0.8,
                    "frequency": channel_data.get("churned_users_period", 0),
                    "pattern": "channel_wide_decline",
                }
            )

        return triggers

    async def _detect_feature_abandonment_triggers(
        self, channel_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Detect feature abandonment patterns"""
        triggers = []

        # Check feature adoption rates
        adoption_rates = channel_data.get("feature_adoption_rates", {})
        for feature, rate in adoption_rates.items():
            if rate < 0.3:  # Low adoption rate
                triggers.append(
                    {
                        "type": "feature_abandonment",
                        "description": f"Low adoption rate for {feature}: {rate:.1%}",
                        "impact_score": 0.6,
                        "frequency": int((1 - rate) * 100),
                        "feature": feature,
                    }
                )

        return triggers

    async def _detect_support_related_triggers(
        self, channel_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Detect support and feedback related triggers"""
        triggers = []

        support_tickets = channel_data.get("support_tickets", 0)
        negative_feedback = channel_data.get("negative_feedback", 0)

        if support_tickets > 50:
            triggers.append(
                {
                    "type": "support_ticket_spike",
                    "description": f"High volume of support tickets: {support_tickets}",
                    "impact_score": 0.7,
                    "frequency": support_tickets,
                }
            )

        if negative_feedback > 10:
            triggers.append(
                {
                    "type": "negative_feedback_spike",
                    "description": f"Increase in negative feedback: {negative_feedback}",
                    "impact_score": 0.8,
                    "frequency": negative_feedback,
                }
            )

        return triggers

    async def _detect_competitive_triggers(
        self, channel_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Detect competitive pressure triggers"""
        triggers = []

        competitor_mentions = channel_data.get("competitor_mentions", 0)

        if competitor_mentions > 5:
            triggers.append(
                {
                    "type": "competitor_pressure",
                    "description": f"Increased competitor mentions: {competitor_mentions}",
                    "impact_score": 0.6,
                    "frequency": competitor_mentions,
                }
            )

        return triggers
