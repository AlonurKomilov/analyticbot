"""
Validation Service
==================

Focused microservice for optimization validation and A/B testing.

Single Responsibility:
- Validate optimization impact
- Manage A/B testing for optimizations
- Analyze optimization effectiveness
- Track performance improvements

Core capabilities extracted from AutonomousOptimizationService validation methods.
"""

import logging
import statistics
from datetime import datetime, timedelta
from typing import Any

from ..protocols.optimization_protocols import (
    OptimizationRecommendation,
    ValidationProtocol,
)

logger = logging.getLogger(__name__)


class ValidationService(ValidationProtocol):
    """
    Optimization validation microservice for impact assessment and A/B testing.

    Single responsibility: Validate optimization effectiveness only.
    """

    def __init__(
        self,
        analytics_service=None,
        performance_analysis_service=None,
        config_manager=None,
    ):
        self.analytics_service = analytics_service
        self.performance_analysis = performance_analysis_service
        self.config_manager = config_manager

        # A/B testing tracking
        self.active_ab_tests: dict[str, dict[str, Any]] = {}
        self.completed_ab_tests: list[dict[str, Any]] = []

        # Validation configuration
        self.validation_config = {
            "ab_test_duration_hours": 24,
            "minimum_sample_size": 100,
            "statistical_significance_level": 0.05,
            "validation_window_hours": 72,
            "performance_metrics": [
                "response_time",
                "cpu_usage",
                "memory_usage",
                "cache_hit_rate",
                "error_rate",
            ],
        }

        # Validation history
        self.validation_history: list[dict[str, Any]] = []

        logger.info("🔬 Validation Service initialized - optimization impact validation focus")

    async def validate_optimization_impact(self, optimization_id: str) -> dict[str, Any]:
        """
        Validate the impact of an applied optimization.

        Main method for comprehensive optimization impact validation.
        """
        try:
            logger.info(f"🔍 Validating optimization impact: {optimization_id}")

            # Check if there's an active A/B test for this optimization
            ab_test_result = None
            if optimization_id in self.active_ab_tests:
                ab_test_result = await self.analyze_ab_test_results(optimization_id)

            # Collect performance metrics for validation
            validation_metrics = await self._collect_validation_metrics(optimization_id)

            # Analyze performance impact
            impact_analysis = await self._analyze_performance_impact(
                optimization_id, validation_metrics
            )

            # Calculate effectiveness score
            effectiveness_score = self._calculate_effectiveness_score(impact_analysis)

            # Generate validation summary
            validation_result = {
                "optimization_id": optimization_id,
                "validation_status": "completed",
                "validation_timestamp": datetime.now().isoformat(),
                "ab_test_result": ab_test_result,
                "performance_metrics": validation_metrics,
                "impact_analysis": impact_analysis,
                "effectiveness_score": effectiveness_score,
                "validation_conclusion": self._generate_validation_conclusion(
                    effectiveness_score, impact_analysis
                ),
                "recommendations": self._generate_validation_recommendations(impact_analysis),
            }

            # Store validation history
            self.validation_history.append(validation_result)

            logger.info(
                f"✅ Validation completed for {optimization_id} - Score: {effectiveness_score:.2f}"
            )
            return validation_result

        except Exception as e:
            logger.error(f"❌ Validation failed for {optimization_id}: {e}")
            return {
                "optimization_id": optimization_id,
                "validation_status": "failed",
                "error": str(e),
                "validation_timestamp": datetime.now().isoformat(),
            }

    async def setup_ab_test(self, optimization: OptimizationRecommendation) -> dict[str, Any]:
        """
        Setup A/B test for optimization validation.
        """
        try:
            logger.info(f"🧪 Setting up A/B test for optimization: {optimization.optimization_id}")

            test_id = optimization.optimization_id

            # A/B test configuration
            ab_test_config = {
                "test_id": test_id,
                "optimization_title": optimization.title,
                "optimization_type": optimization.optimization_type.value,
                "start_time": datetime.now().isoformat(),
                "end_time": (
                    datetime.now()
                    + timedelta(hours=self.validation_config["ab_test_duration_hours"])
                ).isoformat(),
                "control_group_size": 50,  # percentage
                "treatment_group_size": 50,  # percentage
                "target_metrics": self.validation_config["performance_metrics"],
                "expected_improvement": optimization.estimated_impact.get("performance_gain", 0),
                "status": "active",
            }

            # Initialize baseline measurements
            baseline_metrics = await self._collect_baseline_metrics()
            ab_test_config["baseline_metrics"] = baseline_metrics

            # Setup traffic splitting (mock implementation)
            traffic_split = await self._setup_traffic_splitting(test_id)
            ab_test_config["traffic_split"] = traffic_split

            # Store active A/B test
            self.active_ab_tests[test_id] = ab_test_config

            logger.info(f"✅ A/B test setup completed for {test_id}")
            return {
                "test_id": test_id,
                "status": "active",
                "setup_result": "success",
                "test_config": ab_test_config,
                "expected_duration_hours": self.validation_config["ab_test_duration_hours"],
            }

        except Exception as e:
            logger.error(f"❌ A/B test setup failed for {optimization.optimization_id}: {e}")
            return {
                "test_id": optimization.optimization_id,
                "status": "setup_failed",
                "error": str(e),
            }

    async def analyze_ab_test_results(self, test_id: str) -> dict[str, Any]:
        """
        Analyze A/B test results for statistical significance.
        """
        try:
            logger.info(f"📊 Analyzing A/B test results: {test_id}")

            if test_id not in self.active_ab_tests:
                return {
                    "test_id": test_id,
                    "status": "test_not_found",
                    "message": "A/B test not found in active tests",
                }

            ab_test = self.active_ab_tests[test_id]

            # Check if test duration is sufficient
            start_time = datetime.fromisoformat(ab_test["start_time"])
            test_duration = datetime.now() - start_time

            if test_duration.total_seconds() < 3600:  # Less than 1 hour
                return {
                    "test_id": test_id,
                    "status": "insufficient_duration",
                    "message": "Test needs more time to collect sufficient data",
                    "current_duration_hours": test_duration.total_seconds() / 3600,
                }

            # Collect A/B test metrics
            control_metrics = await self._collect_control_group_metrics(test_id)
            treatment_metrics = await self._collect_treatment_group_metrics(test_id)

            # Statistical analysis
            statistical_analysis = self._perform_statistical_analysis(
                control_metrics, treatment_metrics, ab_test["target_metrics"]
            )

            # Calculate test results
            test_results = {
                "test_id": test_id,
                "status": "completed",
                "analysis_timestamp": datetime.now().isoformat(),
                "test_duration_hours": test_duration.total_seconds() / 3600,
                "control_group": {
                    "sample_size": control_metrics.get("sample_size", 0),
                    "metrics": control_metrics,
                },
                "treatment_group": {
                    "sample_size": treatment_metrics.get("sample_size", 0),
                    "metrics": treatment_metrics,
                },
                "statistical_analysis": statistical_analysis,
                "conclusion": self._generate_ab_test_conclusion(statistical_analysis),
                "confidence_level": self._calculate_confidence_level(statistical_analysis),
            }

            # Move to completed tests
            self.completed_ab_tests.append(test_results)
            if test_id in self.active_ab_tests:
                del self.active_ab_tests[test_id]

            logger.info(f"✅ A/B test analysis completed for {test_id}")
            return test_results

        except Exception as e:
            logger.error(f"❌ A/B test analysis failed for {test_id}: {e}")
            return {"test_id": test_id, "status": "analysis_failed", "error": str(e)}

    async def _collect_validation_metrics(self, optimization_id: str) -> dict[str, Any]:
        """Collect performance metrics for optimization validation"""
        try:
            validation_metrics = {}

            # Current performance metrics
            if self.performance_analysis:
                current_performance = await self.performance_analysis.analyze_system_performance()
                validation_metrics["current_performance"] = current_performance

            # Historical comparison metrics
            validation_metrics["historical_comparison"] = await self._get_historical_comparison(
                optimization_id
            )

            # Optimization-specific metrics
            validation_metrics[
                "optimization_specific"
            ] = await self._collect_optimization_specific_metrics(optimization_id)

            return validation_metrics

        except Exception as e:
            logger.error(f"❌ Failed to collect validation metrics: {e}")
            return {"collection_error": str(e)}

    async def _analyze_performance_impact(
        self, optimization_id: str, validation_metrics: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze the performance impact of the optimization"""
        try:
            impact_analysis = {}

            current_perf = validation_metrics.get("current_performance", {})
            historical_comp = validation_metrics.get("historical_comparison", {})

            # Calculate improvements for each metric
            for metric_name, current_baseline in current_perf.items():
                if metric_name in historical_comp:
                    historical_value = historical_comp[metric_name].get("average", 0)
                    current_value = current_baseline.current_value

                    if historical_value > 0:
                        improvement = (historical_value - current_value) / historical_value
                        impact_analysis[metric_name] = {
                            "current_value": current_value,
                            "historical_average": historical_value,
                            "improvement_percentage": improvement * 100,
                            "improvement_direction": (
                                "positive" if improvement > 0 else "negative"
                            ),
                        }

            # Overall impact summary
            impact_analysis["overall_impact"] = self._calculate_overall_impact(impact_analysis)

            return impact_analysis

        except Exception as e:
            logger.error(f"❌ Performance impact analysis failed: {e}")
            return {"analysis_error": str(e)}

    async def _collect_baseline_metrics(self) -> dict[str, Any]:
        """Collect baseline metrics before A/B test"""
        # Mock baseline metrics collection
        return {
            "response_time_ms": 245.7,
            "cpu_usage_percent": 72.3,
            "memory_usage_percent": 68.1,
            "cache_hit_rate": 0.82,
            "error_rate_percent": 0.85,
            "throughput_rps": 145.6,
        }

    async def _setup_traffic_splitting(self, test_id: str) -> dict[str, Any]:
        """Setup traffic splitting for A/B test"""
        # Mock traffic splitting setup
        return {
            "split_strategy": "random",
            "control_percentage": 50,
            "treatment_percentage": 50,
            "routing_configured": True,
            "split_implementation": "feature_flag",
        }

    async def _collect_control_group_metrics(self, test_id: str) -> dict[str, Any]:
        """Collect metrics from control group"""
        # Mock control group metrics
        return {
            "sample_size": 1250,
            "response_time_ms": 248.3,
            "cpu_usage_percent": 73.1,
            "memory_usage_percent": 69.2,
            "cache_hit_rate": 0.81,
            "error_rate_percent": 0.92,
            "throughput_rps": 142.8,
        }

    async def _collect_treatment_group_metrics(self, test_id: str) -> dict[str, Any]:
        """Collect metrics from treatment group (with optimization)"""
        # Mock treatment group metrics (showing improvement)
        return {
            "sample_size": 1320,
            "response_time_ms": 198.7,  # 20% improvement
            "cpu_usage_percent": 65.4,  # 10% improvement
            "memory_usage_percent": 62.1,  # 10% improvement
            "cache_hit_rate": 0.89,  # 10% improvement
            "error_rate_percent": 0.65,  # 30% improvement
            "throughput_rps": 165.2,  # 15% improvement
        }

    def _perform_statistical_analysis(
        self,
        control_metrics: dict[str, Any],
        treatment_metrics: dict[str, Any],
        target_metrics: list[str],
    ) -> dict[str, Any]:
        """Perform statistical analysis on A/B test results"""
        statistical_results = {}

        for metric in target_metrics:
            if metric in control_metrics and metric in treatment_metrics:
                control_value = control_metrics[metric]
                treatment_value = treatment_metrics[metric]

                # Calculate improvement
                if isinstance(control_value, (int, float)) and isinstance(
                    treatment_value, (int, float)
                ):
                    if control_value != 0:
                        improvement = (treatment_value - control_value) / control_value
                    else:
                        improvement = 0

                    # Mock statistical significance calculation
                    p_value = 0.023  # Mock p-value
                    is_significant = (
                        p_value < self.validation_config["statistical_significance_level"]
                    )

                    statistical_results[metric] = {
                        "control_value": control_value,
                        "treatment_value": treatment_value,
                        "improvement_percentage": improvement * 100,
                        "p_value": p_value,
                        "is_statistically_significant": is_significant,
                        "confidence_interval": [improvement - 0.05, improvement + 0.05],
                    }

        return statistical_results

    async def _get_historical_comparison(self, optimization_id: str) -> dict[str, Any]:
        """Get historical performance data for comparison"""
        # Mock historical data
        return {
            "avg_query_time": {"average": 285.4, "samples": 1450},
            "cpu_usage": {"average": 78.2, "samples": 720},
            "memory_usage": {"average": 72.6, "samples": 720},
            "cache_hit_rate": {"average": 0.78, "samples": 360},
        }

    async def _collect_optimization_specific_metrics(self, optimization_id: str) -> dict[str, Any]:
        """Collect metrics specific to the optimization type"""
        # Mock optimization-specific metrics
        return {
            "optimization_applied_at": "2025-10-03T10:30:00Z",
            "optimization_type": "cache_strategy",
            "specific_improvements": {
                "cache_operations_optimized": 245,
                "cache_warming_efficiency": 0.92,
                "cache_invalidation_reduced": 0.65,
            },
        }

    def _calculate_effectiveness_score(self, impact_analysis: dict[str, Any]) -> float:
        """Calculate overall effectiveness score for the optimization"""
        if not impact_analysis or "overall_impact" not in impact_analysis:
            return 0.0

        overall_impact = impact_analysis["overall_impact"]

        # Weight different factors
        performance_weight = 0.4
        reliability_weight = 0.3
        efficiency_weight = 0.3

        performance_score = overall_impact.get("performance_improvement", 0) / 100
        reliability_score = overall_impact.get("reliability_improvement", 0) / 100
        efficiency_score = overall_impact.get("efficiency_improvement", 0) / 100

        effectiveness_score = (
            performance_score * performance_weight
            + reliability_score * reliability_weight
            + efficiency_score * efficiency_weight
        )

        return max(0.0, min(1.0, effectiveness_score))  # Clamp between 0 and 1

    def _calculate_overall_impact(self, impact_analysis: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall impact summary"""
        improvements = []

        for metric_name, analysis in impact_analysis.items():
            if isinstance(analysis, dict) and "improvement_percentage" in analysis:
                improvements.append(analysis["improvement_percentage"])

        if not improvements:
            return {
                "performance_improvement": 0,
                "reliability_improvement": 0,
                "efficiency_improvement": 0,
            }

        average_improvement = statistics.mean(improvements)

        return {
            "performance_improvement": max(0, average_improvement),
            "reliability_improvement": max(0, average_improvement * 0.8),
            "efficiency_improvement": max(0, average_improvement * 0.9),
            "metrics_analyzed": len(improvements),
        }

    def _generate_validation_conclusion(
        self, effectiveness_score: float, impact_analysis: dict[str, Any]
    ) -> str:
        """Generate human-readable validation conclusion"""
        if effectiveness_score >= 0.8:
            return "Highly Effective - Optimization achieved significant performance improvements"
        elif effectiveness_score >= 0.6:
            return "Effective - Optimization provided measurable benefits"
        elif effectiveness_score >= 0.4:
            return "Moderately Effective - Some benefits observed, monitor for further improvements"
        elif effectiveness_score >= 0.2:
            return "Limited Effectiveness - Minimal impact observed, consider refinements"
        else:
            return "Ineffective - No significant improvements observed, consider rollback"

    def _generate_validation_recommendations(self, impact_analysis: dict[str, Any]) -> list[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        overall_impact = impact_analysis.get("overall_impact", {})
        performance_improvement = overall_impact.get("performance_improvement", 0)

        if performance_improvement > 20:
            recommendations.append("Continue monitoring optimization - showing excellent results")
            recommendations.append("Consider applying similar optimizations to other areas")
        elif performance_improvement > 10:
            recommendations.append(
                "Optimization is performing well - maintain current configuration"
            )
        elif performance_improvement > 0:
            recommendations.append("Monitor for longer period to confirm benefits")
            recommendations.append("Consider fine-tuning optimization parameters")
        else:
            recommendations.append("Consider rollback - optimization not showing expected benefits")
            recommendations.append("Analyze why optimization underperformed")

        return recommendations

    def _generate_ab_test_conclusion(self, statistical_analysis: dict[str, Any]) -> str:
        """Generate conclusion from A/B test statistical analysis"""
        significant_improvements = 0
        total_metrics = len(statistical_analysis)

        for metric, analysis in statistical_analysis.items():
            if (
                analysis.get("is_statistically_significant", False)
                and analysis.get("improvement_percentage", 0) > 0
            ):
                significant_improvements += 1

        if significant_improvements == 0:
            return "No statistically significant improvements observed"
        elif significant_improvements == total_metrics:
            return "All metrics show statistically significant improvements"
        else:
            return f"{significant_improvements} out of {total_metrics} metrics show significant improvements"

    def _calculate_confidence_level(self, statistical_analysis: dict[str, Any]) -> float:
        """Calculate overall confidence level for A/B test results"""
        confidence_levels = []

        for metric, analysis in statistical_analysis.items():
            p_value = analysis.get("p_value", 1.0)
            confidence = 1.0 - p_value
            confidence_levels.append(confidence)

        return statistics.mean(confidence_levels) if confidence_levels else 0.0

    async def health_check(self) -> dict[str, Any]:
        """Health check for validation service"""
        return {
            "service_name": "ValidationService",
            "status": "operational",
            "version": "1.0.0",
            "type": "microservice",
            "responsibility": "optimization_validation",
            "capabilities": [
                "optimization_impact_validation",
                "ab_testing_setup",
                "ab_test_analysis",
                "statistical_analysis",
                "effectiveness_scoring",
            ],
            "active_ab_tests": len(self.active_ab_tests),
            "completed_ab_tests": len(self.completed_ab_tests),
            "validation_history": len(self.validation_history),
            "validation_config": self.validation_config,
        }
