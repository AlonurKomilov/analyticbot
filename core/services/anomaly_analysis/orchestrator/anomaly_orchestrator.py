"""
Anomaly Orchestrator

Coordinator service that orchestrates all anomaly analysis microservices.
Single Responsibility: Coord    async def detect_performance_anomalies(
        self,
        channel_id: int,
        metrics: Optional[List[str]] = None,
        sensitivity: float = 2.0,
        lookback_days: int = 30
    ) -> List[Dict]:nd delegate to specialized anomaly services.

Part of refactored Anomaly Analysis microservices architecture.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import numpy as np

from core.services.nlg import NarrativeStyle

from ..analysis.root_cause_analyzer import RootCauseAnalyzer
from ..assessment.severity_assessor import SeverityAssessor
from ..detection.anomaly_detection_service import AnomalyDetectionService
from ..recommendations.anomaly_recommender import AnomalyRecommender

logger = logging.getLogger(__name__)


class AnomalyOrchestrator:
    """
    🎭 Anomaly Orchestrator

    Lightweight coordinator that delegates to specialized microservices:
    - AnomalyDetectionService: Statistical anomaly detection
    - RootCauseAnalyzer: Root cause analysis
    - SeverityAssessor: Severity and impact assessment
    - AnomalyRecommender: Recommendation generation
    """

    def __init__(self, nlg_service, channel_daily_repo, post_repo, config_manager=None):
        """Initialize orchestrator with all required dependencies"""
        self._nlg_service = nlg_service
        self._daily = channel_daily_repo
        self._posts = post_repo
        self.config_manager = config_manager

        # Initialize microservices
        self.detection_service = AnomalyDetectionService(channel_daily_repo, post_repo)
        self.root_cause_analyzer = RootCauseAnalyzer(config_manager)
        self.severity_assessor = SeverityAssessor(config_manager)
        self.anomaly_recommender = AnomalyRecommender(config_manager)

        logger.info("🎭 AnomalyOrchestrator initialized with 4 microservices")

    async def analyze_and_explain_anomaly(
        self,
        channel_id: int,
        anomaly_data: dict,
        narrative_style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL,
    ) -> dict:
        """
        🚨 Comprehensive Anomaly Analysis with Natural Language Explanation

        Coordinates all anomaly analysis microservices to provide complete analysis.

        Args:
            channel_id: Target channel ID
            anomaly_data: Detected anomaly information
            narrative_style: How to present the explanation

        Returns:
            Comprehensive anomaly analysis with explanations and recommendations
        """
        try:
            # Get historical context for comparison
            now = datetime.now()
            start_date = now - timedelta(days=30)

            # Gather historical data for context
            historical_context = await self._gather_historical_context(channel_id, start_date, now)

            # Delegate to Root Cause Analyzer
            root_causes = await self.root_cause_analyzer.analyze_root_causes(
                channel_id, anomaly_data, historical_context
            )

            # Generate natural language explanation (via NLG service)
            explanation = await self._nlg_service.explain_anomaly(
                anomaly_data, historical_context, narrative_style
            )

            # Delegate to Severity Assessor
            severity_assessment = await self.severity_assessor.assess_severity(
                anomaly_data, historical_context
            )

            # Delegate to Anomaly Recommender
            recommendations = await self.anomaly_recommender.generate_recommendations(
                anomaly_data, root_causes, severity_assessment
            )

            # Calculate overall confidence
            confidence = self.anomaly_recommender.calculate_analysis_confidence(
                anomaly_data, historical_context, root_causes
            )

            return {
                "anomaly_detected": True,
                "anomaly_data": anomaly_data,
                "explanation": explanation,
                "root_cause_analysis": root_causes,
                "severity_assessment": severity_assessment,
                "recommendations": recommendations,
                "narrative_style": narrative_style.value,
                "historical_context_available": bool(historical_context),
                "analyzed_at": datetime.now().isoformat(),
                "confidence": confidence,
            }

        except Exception as e:
            logger.error(f"Anomaly analysis orchestration failed: {e}")
            return {
                "anomaly_detected": True,
                "explanation": "An unusual pattern was detected that requires investigation.",
                "error": str(e),
                "recommendations": [
                    "Manual review recommended",
                    "Check recent changes",
                ],
                "severity": "unknown",
            }

    async def detect_performance_anomalies(
        self,
        channel_id: int,
        metrics: list[str] | None = None,
        sensitivity: float = 2.0,
        days: int = 30,
    ) -> list[dict]:
        """
        Delegate to AnomalyDetectionService for performance anomaly detection

        Args:
            channel_id: Target channel ID
            metrics: List of metrics to analyze
            sensitivity: Detection sensitivity threshold
            days: Historical period to analyze

        Returns:
            List of detected anomalies
        """
        return await self.detection_service.detect_performance_anomalies(
            channel_id, metrics, sensitivity, days
        )

    async def _gather_historical_context(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> dict:
        """Gather comprehensive historical context for anomaly analysis"""
        try:
            context = {}

            # Get historical posts data
            posts = await self._posts.top_by_views(channel_id, start_date, end_date, 100)
            context["posts"] = posts

            # Get time series data
            daily_views = await self._daily.series_data(channel_id, "views", start_date, end_date)
            daily_followers = await self._daily.series_data(
                channel_id, "followers", start_date, end_date
            )

            context["daily_metrics"] = {
                "views": daily_views or [],
                "followers": daily_followers or [],
            }

            # Calculate baseline metrics
            if posts:
                view_counts = [p.get("views", 0) for p in posts]
                context["baselines"] = {
                    "avg_views": np.mean(view_counts),
                    "std_views": np.std(view_counts),
                    "median_views": np.median(view_counts),
                    "percentile_90": np.percentile(view_counts, 90),
                    "percentile_10": np.percentile(view_counts, 10),
                }

                # Calculate engagement baselines
                engagement_scores = []
                for post in posts:
                    views = post.get("views", 0)
                    forwards = post.get("forwards", 0)
                    replies = post.get("replies", 0)

                    if views > 0:
                        engagement = (forwards + replies) / views * 100
                        engagement_scores.append(engagement)

                if engagement_scores:
                    context["baselines"]["avg_engagement"] = np.mean(engagement_scores)
                    context["baselines"]["std_engagement"] = np.std(engagement_scores)

            return context

        except Exception as e:
            logger.error(f"Historical context gathering failed: {e}")
            return {}

    async def health_check(self) -> dict:
        """Health check for anomaly orchestrator and all microservices"""
        try:
            # Check all microservices
            detection_health = await self.detection_service.health_check()
            analyzer_health = await self.root_cause_analyzer.health_check()
            assessor_health = await self.severity_assessor.health_check()
            recommender_health = await self.anomaly_recommender.health_check()

            all_healthy = all(
                [
                    detection_health.get("status") == "healthy",
                    analyzer_health.get("status") == "healthy",
                    assessor_health.get("status") == "healthy",
                    recommender_health.get("status") == "healthy",
                ]
            )

            return {
                "service": "AnomalyOrchestrator",
                "status": "healthy" if all_healthy else "degraded",
                "architecture": "microservices",
                "microservices": {
                    "detection": detection_health,
                    "analysis": analyzer_health,
                    "assessment": assessor_health,
                    "recommendations": recommender_health,
                },
                "capabilities": [
                    "comprehensive_anomaly_analysis",
                    "natural_language_explanations",
                    "root_cause_identification",
                    "severity_assessment",
                    "recommendation_generation",
                ],
                "dependencies": {"nlg_service": True, "numpy": True},
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "service": "AnomalyOrchestrator",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
