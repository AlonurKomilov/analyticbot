"""
Drift Detection Coordinator
===========================

Coordinates statistical and multivariate drift analyzers to provide
comprehensive drift detection and alerting capabilities.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np

from ..protocols.drift_protocols import (
    DriftAlert,
    DriftDetectionMethod,
    DriftSeverity,
    DriftType,
)
from ..protocols.monitoring_protocols import MonitoringServiceProtocol
from .multivariate_analyzer import MultivariateDriftAnalyzer, MultivariateDriftResult
from .statistical_analyzer import FeatureAnalysisResult, StatisticalDriftAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class DriftCoordinatorConfig:
    """Configuration for drift coordinator"""

    detection_window_hours: int = 24
    auto_alert_enabled: bool = True
    monitoring_frequency_minutes: int = 60
    min_samples_required: int = 100
    cache_ttl_minutes: int = 30
    drift_severity_thresholds: dict[str, float] | None = None

    def __post_init__(self):
        if self.drift_severity_thresholds is None:
            self.drift_severity_thresholds = {
                "low": 0.1,
                "medium": 0.25,
                "high": 0.5,
                "critical": 0.75,
            }


@dataclass
class ComprehensiveDriftAnalysis:
    """Comprehensive drift analysis result"""

    analysis_id: str
    model_id: str
    drift_type: DriftType
    overall_detected: bool
    overall_severity: DriftSeverity
    overall_drift_score: float
    confidence: float

    # Component results
    feature_results: list[FeatureAnalysisResult]
    multivariate_results: dict[str, MultivariateDriftResult]

    # Aggregated information
    affected_features: list[str]
    recommendation: str
    timestamp: datetime
    metadata: dict[str, Any]


class DriftCoordinator:
    """
    Coordinates drift detection using specialized analyzers.

    Provides a clean interface for comprehensive drift detection
    while delegating specific analysis to specialized services.
    """

    def __init__(
        self,
        statistical_analyzer: StatisticalDriftAnalyzer,
        multivariate_analyzer: MultivariateDriftAnalyzer,
        monitoring_service: MonitoringServiceProtocol,
        config: DriftCoordinatorConfig | None = None,
    ):
        self.statistical_analyzer = statistical_analyzer
        self.multivariate_analyzer = multivariate_analyzer
        self.monitoring_service = monitoring_service
        self.config = config or DriftCoordinatorConfig()

        # Service state
        self.is_running = False
        self.monitored_models: set[str] = set()

        # Data management
        self.reference_data: dict[str, np.ndarray] = {}
        self.performance_baselines: dict[str, dict[str, float]] = {}

        # Analysis tracking
        self.drift_history: dict[str, list[ComprehensiveDriftAnalysis]] = {}
        self.active_alerts: dict[str, DriftAlert] = {}
        self.analysis_cache: dict[str, ComprehensiveDriftAnalysis] = {}

        # Background tasks
        self.monitoring_tasks: list[asyncio.Task] = []

        logger.info("🎯 Drift Detection Coordinator initialized")

    async def start_monitoring(self) -> bool:
        """Start drift monitoring service"""
        try:
            # Start background monitoring
            monitor_task = asyncio.create_task(self._monitoring_loop())
            self.monitoring_tasks.append(monitor_task)

            # Start cache cleanup
            cleanup_task = asyncio.create_task(self._cache_cleanup_loop())
            self.monitoring_tasks.append(cleanup_task)

            self.is_running = True
            logger.info("✅ Drift monitoring started")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start drift monitoring: {e}")
            return False

    async def stop_monitoring(self) -> bool:
        """Stop drift monitoring service"""
        try:
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            self.monitoring_tasks.clear()
            self.is_running = False

            logger.info("⏹️ Drift monitoring stopped")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to stop drift monitoring: {e}")
            return False

    async def add_model_monitoring(
        self, model_id: str, reference_data: np.ndarray | None = None
    ) -> bool:
        """Add a model to drift monitoring"""
        try:
            if model_id in self.monitored_models:
                logger.warning(f"⚠️ Model {model_id} already monitored")
                return True

            # Store reference data if provided
            if reference_data is not None:
                if reference_data.shape[0] < self.config.min_samples_required:
                    logger.warning(
                        f"⚠️ Insufficient reference data: {reference_data.shape[0]} < {self.config.min_samples_required}"
                    )
                    return False

                self.reference_data[model_id] = reference_data

            # Initialize tracking structures
            if model_id not in self.drift_history:
                self.drift_history[model_id] = []

            self.monitored_models.add(model_id)

            logger.info(f"📊 Added model {model_id} to drift monitoring")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to add model monitoring: {e}")
            return False

    async def remove_model_monitoring(self, model_id: str) -> bool:
        """Remove a model from drift monitoring"""
        try:
            if model_id not in self.monitored_models:
                logger.warning(f"⚠️ Model {model_id} not monitored")
                return True

            # Clean up data
            self.monitored_models.discard(model_id)
            if model_id in self.reference_data:
                del self.reference_data[model_id]
            if model_id in self.performance_baselines:
                del self.performance_baselines[model_id]

            # Close active alerts
            alerts_to_close = [
                alert_id
                for alert_id, alert in self.active_alerts.items()
                if alert.model_id == model_id
            ]
            for alert_id in alerts_to_close:
                del self.active_alerts[alert_id]

            logger.info(f"🗑️ Removed model {model_id} from drift monitoring")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to remove model monitoring: {e}")
            return False

    async def detect_data_drift(
        self,
        model_id: str,
        current_data: np.ndarray,
        feature_names: list[str] | None = None,
    ) -> ComprehensiveDriftAnalysis | None:
        """Perform comprehensive data drift detection"""
        try:
            if model_id not in self.monitored_models:
                logger.error(f"❌ Model {model_id} not monitored")
                return None

            if model_id not in self.reference_data:
                logger.error(f"❌ No reference data for model {model_id}")
                return None

            # Validate data
            if current_data.shape[0] < self.config.min_samples_required:
                logger.warning(f"⚠️ Insufficient current data: {current_data.shape[0]}")
                return None

            reference_data = self.reference_data[model_id]
            if current_data.shape[1] != reference_data.shape[1]:
                logger.error(
                    f"❌ Feature dimension mismatch: {current_data.shape[1]} vs {reference_data.shape[1]}"
                )
                return None

            # Check cache
            cache_key = f"{model_id}_data_{hash(current_data.tobytes())}"
            if cache_key in self.analysis_cache:
                cached = self.analysis_cache[cache_key]
                if (
                    datetime.utcnow() - cached.timestamp
                ).total_seconds() < self.config.cache_ttl_minutes * 60:
                    return cached

            analysis_id = f"drift_{model_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

            # Perform statistical analysis
            feature_results = await self.statistical_analyzer.analyze_feature_drift(
                reference_data, current_data, feature_names
            )

            # Perform multivariate analysis
            multivariate_results = await self.multivariate_analyzer.analyze_multivariate_drift(
                reference_data, current_data
            )

            # Aggregate results
            analysis = await self._aggregate_drift_results(
                analysis_id, model_id, feature_results, multivariate_results
            )

            # Cache and store
            self.analysis_cache[cache_key] = analysis
            self.drift_history[model_id].append(analysis)

            # Generate alert if needed
            if analysis.overall_detected and self.config.auto_alert_enabled:
                await self._generate_drift_alert(analysis)

            logger.info(
                f"🔍 Data drift analysis completed: {'DETECTED' if analysis.overall_detected else 'NO DRIFT'}"
            )
            return analysis

        except Exception as e:
            logger.error(f"❌ Data drift detection failed: {e}")
            return None

    async def detect_concept_drift(
        self, model_id: str, current_performance: dict[str, float]
    ) -> ComprehensiveDriftAnalysis | None:
        """Detect concept drift based on performance metrics"""
        try:
            if model_id not in self.monitored_models:
                logger.error(f"❌ Model {model_id} not monitored")
                return None

            analysis_id = f"concept_{model_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

            # Establish or get baseline
            if model_id not in self.performance_baselines:
                self.performance_baselines[model_id] = current_performance.copy()
                logger.info(f"📊 Established performance baseline for {model_id}")
                return None

            baseline = self.performance_baselines[model_id]

            # Analyze performance changes
            performance_analysis = await self._analyze_performance_drift(
                baseline, current_performance
            )

            # Create comprehensive analysis
            analysis = ComprehensiveDriftAnalysis(
                analysis_id=analysis_id,
                model_id=model_id,
                drift_type=DriftType.CONCEPT_DRIFT,
                overall_detected=performance_analysis["detected"],
                overall_severity=performance_analysis["severity"],
                overall_drift_score=performance_analysis["drift_score"],
                confidence=performance_analysis["confidence"],
                feature_results=[],
                multivariate_results={},
                affected_features=performance_analysis["affected_metrics"],
                recommendation=performance_analysis["recommendation"],
                timestamp=datetime.utcnow(),
                metadata={
                    "performance_analysis": performance_analysis,
                    "baseline_metrics": baseline,
                    "current_metrics": current_performance,
                },
            )

            # Store and alert
            self.drift_history[model_id].append(analysis)

            if analysis.overall_detected and self.config.auto_alert_enabled:
                await self._generate_drift_alert(analysis)

            logger.info(
                f"🔍 Concept drift analysis completed: {'DETECTED' if analysis.overall_detected else 'NO DRIFT'}"
            )
            return analysis

        except Exception as e:
            logger.error(f"❌ Concept drift detection failed: {e}")
            return None

    async def get_drift_status(self, model_id: str) -> dict[str, Any]:
        """Get drift status for a model"""
        try:
            if model_id not in self.monitored_models:
                return {"error": f"Model {model_id} not monitored"}

            recent_analyses = self.drift_history.get(model_id, [])[-10:]
            active_alerts = [
                a for a in self.active_alerts.values() if a.model_id == model_id and not a.resolved
            ]

            # Calculate trends
            data_drift_scores = [
                a.overall_drift_score
                for a in recent_analyses
                if a.drift_type == DriftType.DATA_DRIFT
            ]
            concept_drift_scores = [
                a.overall_drift_score
                for a in recent_analyses
                if a.drift_type == DriftType.CONCEPT_DRIFT
            ]

            return {
                "model_id": model_id,
                "monitoring_enabled": True,
                "last_analysis": (
                    recent_analyses[-1].timestamp.isoformat() if recent_analyses else None
                ),
                "active_alerts": len(active_alerts),
                "recent_analyses": len(recent_analyses),
                "drift_trends": {
                    "data_drift_avg": (
                        sum(data_drift_scores) / len(data_drift_scores)
                        if data_drift_scores
                        else 0.0
                    ),
                    "concept_drift_avg": (
                        sum(concept_drift_scores) / len(concept_drift_scores)
                        if concept_drift_scores
                        else 0.0
                    ),
                },
                "reference_data_available": model_id in self.reference_data,
                "performance_baseline_available": model_id in self.performance_baselines,
            }

        except Exception as e:
            logger.error(f"❌ Failed to get drift status: {e}")
            return {"error": str(e)}

    async def get_active_alerts(self, model_id: str | None = None) -> list[DriftAlert]:
        """Get active drift alerts"""
        try:
            alerts = [a for a in self.active_alerts.values() if not a.resolved]

            if model_id:
                alerts = [a for a in alerts if a.model_id == model_id]

            return alerts

        except Exception as e:
            logger.error(f"❌ Failed to get active alerts: {e}")
            return []

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a drift alert"""
        try:
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].resolved = True
                logger.info(f"✅ Resolved drift alert {alert_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"❌ Failed to resolve alert: {e}")
            return False

    async def _aggregate_drift_results(
        self,
        analysis_id: str,
        model_id: str,
        feature_results: list[FeatureAnalysisResult],
        multivariate_results: dict[str, MultivariateDriftResult],
    ) -> ComprehensiveDriftAnalysis:
        """Aggregate feature and multivariate drift results"""

        # Calculate overall drift score
        feature_scores = [f.drift_score for f in feature_results if f.drift_detected]
        multivariate_scores = [m.drift_score for m in multivariate_results.values() if m.detected]

        all_scores = feature_scores + multivariate_scores
        overall_drift_score = max(all_scores) if all_scores else 0.0

        # Determine detection and severity
        overall_detected = overall_drift_score > self.config.drift_severity_thresholds["low"]
        overall_severity = self._calculate_drift_severity(overall_drift_score)

        # Get affected features
        affected_features = [f.feature_name for f in feature_results if f.drift_detected]

        # Calculate confidence
        significant_features = len([f for f in feature_results if f.best_test.detected])
        total_features = len(feature_results)
        multivariate_confidence = (
            sum(m.confidence for m in multivariate_results.values()) / len(multivariate_results)
            if multivariate_results
            else 0.5
        )

        feature_confidence = significant_features / total_features if total_features > 0 else 0.0
        confidence = (feature_confidence + multivariate_confidence) / 2.0

        # Generate recommendation
        recommendation = await self._generate_recommendation(
            DriftType.DATA_DRIFT,
            overall_severity,
            affected_features,
            overall_drift_score,
        )

        return ComprehensiveDriftAnalysis(
            analysis_id=analysis_id,
            model_id=model_id,
            drift_type=DriftType.DATA_DRIFT,
            overall_detected=overall_detected,
            overall_severity=overall_severity,
            overall_drift_score=overall_drift_score,
            confidence=confidence,
            feature_results=feature_results,
            multivariate_results=multivariate_results,
            affected_features=affected_features,
            recommendation=recommendation,
            timestamp=datetime.utcnow(),
            metadata={
                "feature_detection_count": len(feature_scores),
                "multivariate_detection_count": len(multivariate_scores),
                "total_features_analyzed": len(feature_results),
            },
        )

    async def _analyze_performance_drift(
        self, baseline: dict[str, float], current: dict[str, float]
    ) -> dict[str, Any]:
        """Analyze performance drift between baseline and current metrics"""

        significant_degradations = []
        performance_changes = {}

        for metric, current_value in current.items():
            if metric in baseline:
                baseline_value = baseline[metric]
                change_ratio = (
                    (current_value - baseline_value) / baseline_value
                    if baseline_value != 0
                    else 0.0
                )

                performance_changes[metric] = {
                    "baseline": baseline_value,
                    "current": current_value,
                    "change_ratio": change_ratio,
                    "absolute_change": abs(change_ratio),
                }

                # Check for significant degradation
                if change_ratio < -self.config.drift_severity_thresholds["low"]:
                    significant_degradations.append((metric, abs(change_ratio)))

        # Determine overall drift
        if significant_degradations:
            max_degradation = max(deg for _, deg in significant_degradations)
            affected_metrics = [metric for metric, _ in significant_degradations]
            detected = True
            severity = self._calculate_drift_severity(max_degradation)
            drift_score = max_degradation
            confidence = min(0.95, len(significant_degradations) / len(current))
        else:
            detected = False
            severity = DriftSeverity.LOW
            drift_score = 0.0
            confidence = 0.8
            affected_metrics = []

        # Generate recommendation
        recommendation = await self._generate_recommendation(
            DriftType.CONCEPT_DRIFT, severity, affected_metrics, drift_score
        )

        return {
            "detected": detected,
            "severity": severity,
            "drift_score": drift_score,
            "confidence": confidence,
            "affected_metrics": affected_metrics,
            "performance_changes": performance_changes,
            "recommendation": recommendation,
        }

    def _calculate_drift_severity(self, drift_score: float) -> DriftSeverity:
        """Calculate drift severity based on score"""
        thresholds = self.config.drift_severity_thresholds

        if drift_score >= thresholds["critical"]:
            return DriftSeverity.CRITICAL
        elif drift_score >= thresholds["high"]:
            return DriftSeverity.HIGH
        elif drift_score >= thresholds["medium"]:
            return DriftSeverity.MEDIUM
        else:
            return DriftSeverity.LOW

    async def _generate_recommendation(
        self,
        drift_type: DriftType,
        severity: DriftSeverity,
        affected_items: list[str],
        drift_score: float,
    ) -> str:
        """Generate recommendation based on drift analysis"""

        recommendations = []

        if drift_type == DriftType.DATA_DRIFT:
            if severity == DriftSeverity.CRITICAL:
                recommendations.append("IMMEDIATE ACTION: Retrain model with recent data")
                recommendations.append("Consider rollback to previous model version")
            elif severity == DriftSeverity.HIGH:
                recommendations.append("Schedule model retraining within 24 hours")
                recommendations.append("Increase monitoring frequency")
            elif severity == DriftSeverity.MEDIUM:
                recommendations.append("Plan model update within 1 week")
                recommendations.append("Monitor affected features closely")
            else:
                recommendations.append("Continue monitoring")

            if affected_items:
                recommendations.append(f"Focus on features: {', '.join(affected_items[:3])}")

        elif drift_type == DriftType.CONCEPT_DRIFT:
            if severity == DriftSeverity.CRITICAL:
                recommendations.append("CRITICAL: Performance severely degraded")
                recommendations.append("Immediate investigation required")
            elif severity == DriftSeverity.HIGH:
                recommendations.append("Investigate performance degradation")
                recommendations.append("Prepare for model updates")
            else:
                recommendations.append("Monitor performance trends")

        return " | ".join(recommendations)

    async def _generate_drift_alert(self, analysis: ComprehensiveDriftAnalysis) -> None:
        """Generate drift alert"""
        try:
            alert_id = f"alert_{analysis.model_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

            alert = DriftAlert(
                alert_id=alert_id,
                model_id=analysis.model_id,
                drift_type=analysis.drift_type,
                severity=analysis.overall_severity,
                detection_method=DriftDetectionMethod.ENSEMBLE,
                confidence_score=analysis.confidence,
                detected_at=analysis.timestamp,
                description=f"{analysis.drift_type.value} detected with {analysis.overall_severity.value} severity (score: {analysis.overall_drift_score:.3f})",
                affected_features=analysis.affected_features,
                recommended_actions=[analysis.recommendation],
            )

            self.active_alerts[alert_id] = alert

            logger.warning(f"🚨 Generated drift alert {alert_id}: {alert.description}")

        except Exception as e:
            logger.error(f"❌ Failed to generate drift alert: {e}")

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.monitoring_frequency_minutes * 60)

                for model_id in list(self.monitored_models):
                    try:
                        # Check for concept drift via performance monitoring
                        current_metrics = await self.monitoring_service.get_current_metrics(
                            model_id
                        )
                        if current_metrics:
                            performance_dict = {
                                "accuracy": current_metrics.accuracy,
                                "precision": current_metrics.precision,
                                "recall": current_metrics.recall,
                                "f1_score": current_metrics.f1_score,
                                "error_rate": current_metrics.error_rate,
                            }
                            await self.detect_concept_drift(model_id, performance_dict)

                    except Exception as e:
                        logger.error(f"❌ Monitoring failed for {model_id}: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")

    async def _cache_cleanup_loop(self) -> None:
        """Clean up analysis cache"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Clean every hour

                cutoff = datetime.utcnow() - timedelta(minutes=self.config.cache_ttl_minutes)
                expired_keys = [
                    key
                    for key, analysis in self.analysis_cache.items()
                    if analysis.timestamp < cutoff
                ]

                for key in expired_keys:
                    del self.analysis_cache[key]

                if expired_keys:
                    logger.info(f"🧹 Cleaned {len(expired_keys)} cache entries")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Cache cleanup error: {e}")

    async def shutdown(self) -> None:
        """Shutdown coordinator"""
        try:
            await self.stop_monitoring()

            # Clear data
            self.monitored_models.clear()
            self.reference_data.clear()
            self.performance_baselines.clear()
            self.drift_history.clear()
            self.active_alerts.clear()
            self.analysis_cache.clear()

            logger.info("🛑 Drift coordinator shutdown complete")

        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "service": "drift_detection_coordinator",
            "status": "healthy" if self.is_running else "stopped",
            "monitored_models": len(self.monitored_models),
            "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),
            "cache_entries": len(self.analysis_cache),
            "component_health": {
                "statistical_analyzer": self.statistical_analyzer.get_service_health(),
                "multivariate_analyzer": self.multivariate_analyzer.get_service_health(),
            },
        }
