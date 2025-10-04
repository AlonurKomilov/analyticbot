"""
Autonomous Optimization Service - Phase 3 Step 2
============================================

Intelligent optimization engine that autonomously analyzes system performance,
identifies optimization opportunities, and automatically applies improvements.

Key Capabilities:
- Performance bottleneck detection and resolution
- Query optimization with automatic index suggestions
- Resource allocation optimization
- Predictive scaling based on usage patterns
- Automated A/B testing for optimization validation
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class OptimizationPriority(Enum):
    """Priority levels for optimization recommendations"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OptimizationType(Enum):
    """Types of optimizations the engine can perform"""

    QUERY_OPTIMIZATION = "query_optimization"
    INDEX_SUGGESTION = "index_suggestion"
    CACHE_STRATEGY = "cache_strategy"
    RESOURCE_ALLOCATION = "resource_allocation"
    DATA_PARTITIONING = "data_partitioning"
    AGGREGATION_PRECOMPUTE = "aggregation_precompute"


@dataclass
class OptimizationRecommendation:
    """Structured optimization recommendation with impact analysis"""

    id: str
    type: OptimizationType
    priority: OptimizationPriority
    title: str
    description: str
    technical_details: dict[str, Any]
    estimated_impact: dict[str, float]  # performance_gain, cost_reduction, etc.
    implementation_complexity: str
    auto_applicable: bool
    validation_metrics: list[str]
    created_at: datetime


@dataclass
class PerformanceBaseline:
    """Performance baseline for optimization comparison"""

    metric_name: str
    current_value: float
    historical_average: float
    target_value: float
    trend_direction: str
    measurement_timestamp: datetime


class AutonomousOptimizationService:
    """
    AI-powered autonomous optimization engine that continuously analyzes
    system performance and automatically applies intelligent optimizations.
    """

    def __init__(self, analytics_service, nlg_service, cache_service):
        self.analytics_service = analytics_service
        self.nlg_service = nlg_service
        self.cache_service = cache_service

        # Optimization tracking
        self.active_recommendations: list[OptimizationRecommendation] = []
        self.applied_optimizations: list[dict[str, Any]] = []
        self.performance_baselines: dict[str, PerformanceBaseline] = {}

        # Configuration
        self.optimization_thresholds = {
            "query_time_ms": 1000,
            "memory_usage_percent": 80,
            "cpu_usage_percent": 75,
            "cache_hit_rate": 0.85,
            "error_rate_percent": 1.0,
        }

        # A/B testing for optimization validation
        self.ab_tests: dict[str, dict[str, Any]] = {}

    async def analyze_system_performance(self) -> dict[str, PerformanceBaseline]:
        """
        Comprehensive analysis of current system performance across all metrics.
        """
        try:
            logger.info("🔍 Starting autonomous performance analysis")

            # Collect performance metrics
            await self._collect_performance_metrics()

            # Analyze query performance
            query_metrics = await self._analyze_query_performance()

            # Check resource utilization
            resource_metrics = await self._analyze_resource_utilization()

            # Evaluate cache effectiveness
            cache_metrics = await self._analyze_cache_performance()

            # Create performance baselines
            baselines = {}

            # Query performance baselines
            if query_metrics:
                baselines["avg_query_time"] = PerformanceBaseline(
                    metric_name="Average Query Time",
                    current_value=query_metrics.get("avg_time_ms", 0),
                    historical_average=query_metrics.get("historical_avg", 0),
                    target_value=500.0,  # 500ms target
                    trend_direction=self._calculate_trend(query_metrics.get("trend_data", [])),
                    measurement_timestamp=datetime.now(),
                )

                baselines["slow_query_count"] = PerformanceBaseline(
                    metric_name="Slow Query Count",
                    current_value=query_metrics.get("slow_queries", 0),
                    historical_average=query_metrics.get("historical_slow_queries", 0),
                    target_value=0.0,
                    trend_direction=self._calculate_trend(
                        query_metrics.get("slow_query_trend", [])
                    ),
                    measurement_timestamp=datetime.now(),
                )

            # Resource utilization baselines
            if resource_metrics:
                baselines["cpu_usage"] = PerformanceBaseline(
                    metric_name="CPU Usage",
                    current_value=resource_metrics.get("cpu_percent", 0),
                    historical_average=resource_metrics.get("cpu_avg", 0),
                    target_value=60.0,  # 60% target
                    trend_direction=self._calculate_trend(resource_metrics.get("cpu_trend", [])),
                    measurement_timestamp=datetime.now(),
                )

                baselines["memory_usage"] = PerformanceBaseline(
                    metric_name="Memory Usage",
                    current_value=resource_metrics.get("memory_percent", 0),
                    historical_average=resource_metrics.get("memory_avg", 0),
                    target_value=70.0,  # 70% target
                    trend_direction=self._calculate_trend(resource_metrics.get("memory_trend", [])),
                    measurement_timestamp=datetime.now(),
                )

            # Cache performance baselines
            if cache_metrics:
                baselines["cache_hit_rate"] = PerformanceBaseline(
                    metric_name="Cache Hit Rate",
                    current_value=cache_metrics.get("hit_rate", 0),
                    historical_average=cache_metrics.get("historical_hit_rate", 0),
                    target_value=0.90,  # 90% target
                    trend_direction=self._calculate_trend(cache_metrics.get("hit_rate_trend", [])),
                    measurement_timestamp=datetime.now(),
                )

            # Store baselines for comparison
            self.performance_baselines.update(baselines)

            logger.info(f"✅ Performance analysis completed: {len(baselines)} metrics analyzed")
            return baselines

        except Exception as e:
            logger.error(f"❌ Error in performance analysis: {str(e)}")
            return {}

    async def generate_optimization_recommendations(
        self,
    ) -> list[OptimizationRecommendation]:
        """
        Generate intelligent optimization recommendations based on performance analysis.
        """
        try:
            logger.info("🧠 Generating autonomous optimization recommendations")

            recommendations = []

            # Analyze each performance baseline for optimization opportunities
            for metric_name, baseline in self.performance_baselines.items():
                # Query optimization recommendations
                if (
                    metric_name == "avg_query_time"
                    and baseline.current_value > self.optimization_thresholds["query_time_ms"]
                ):
                    recommendations.extend(await self._generate_query_optimizations(baseline))

                # Resource optimization recommendations
                elif (
                    metric_name == "cpu_usage"
                    and baseline.current_value > self.optimization_thresholds["cpu_usage_percent"]
                ):
                    recommendations.extend(await self._generate_cpu_optimizations(baseline))

                elif (
                    metric_name == "memory_usage"
                    and baseline.current_value
                    > self.optimization_thresholds["memory_usage_percent"]
                ):
                    recommendations.extend(await self._generate_memory_optimizations(baseline))

                # Cache optimization recommendations
                elif (
                    metric_name == "cache_hit_rate"
                    and baseline.current_value < self.optimization_thresholds["cache_hit_rate"]
                ):
                    recommendations.extend(await self._generate_cache_optimizations(baseline))

            # Advanced optimization patterns
            recommendations.extend(await self._generate_advanced_optimizations())

            # Sort by priority and impact
            recommendations.sort(
                key=lambda x: (
                    x.priority.value,
                    -x.estimated_impact.get("performance_gain", 0),
                )
            )

            self.active_recommendations = recommendations

            logger.info(f"✅ Generated {len(recommendations)} optimization recommendations")
            return recommendations

        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {str(e)}")
            return []

    async def auto_apply_safe_optimizations(self) -> dict[str, Any]:
        """
        Automatically apply safe optimizations that have low risk and high impact.
        """
        try:
            logger.info("🤖 Auto-applying safe optimizations")

            applied_count = 0
            results = {"applied": [], "skipped": [], "errors": []}

            for recommendation in self.active_recommendations:
                if recommendation.auto_applicable and recommendation.priority in [
                    OptimizationPriority.CRITICAL,
                    OptimizationPriority.HIGH,
                ]:
                    try:
                        # Apply the optimization
                        success = await self._apply_optimization(recommendation)

                        if success:
                            # Set up A/B testing to validate
                            await self._setup_optimization_validation(recommendation)

                            results["applied"].append(
                                {
                                    "id": recommendation.id,
                                    "type": recommendation.type.value,
                                    "title": recommendation.title,
                                    "applied_at": datetime.now().isoformat(),
                                }
                            )
                            applied_count += 1

                            # Track applied optimization
                            self.applied_optimizations.append(
                                {
                                    "recommendation": recommendation,
                                    "applied_at": datetime.now(),
                                    "status": "active",
                                }
                            )

                        else:
                            results["skipped"].append(
                                {
                                    "id": recommendation.id,
                                    "reason": "application_failed",
                                }
                            )

                    except Exception as e:
                        results["errors"].append({"id": recommendation.id, "error": str(e)})
                        logger.error(
                            f"❌ Error applying optimization {recommendation.id}: {str(e)}"
                        )

                else:
                    results["skipped"].append(
                        {
                            "id": recommendation.id,
                            "reason": "not_auto_applicable_or_low_priority",
                        }
                    )

            logger.info(f"✅ Auto-applied {applied_count} optimizations")
            return results

        except Exception as e:
            logger.error(f"❌ Error in auto-application: {str(e)}")
            return {"applied": [], "skipped": [], "errors": [str(e)]}

    async def validate_optimization_impact(self) -> dict[str, Any]:
        """
        Validate the impact of applied optimizations using A/B testing and metrics comparison.
        """
        try:
            logger.info("📊 Validating optimization impact")

            validation_results = []

            for optimization in self.applied_optimizations:
                if optimization["status"] == "active":
                    recommendation = optimization["recommendation"]
                    applied_at = optimization["applied_at"]

                    # Get performance data before and after optimization
                    before_metrics = await self._get_historical_metrics(
                        applied_at - timedelta(hours=24), applied_at
                    )
                    after_metrics = await self._get_historical_metrics(applied_at, datetime.now())

                    # Calculate impact
                    impact_analysis = await self._calculate_optimization_impact(
                        recommendation, before_metrics, after_metrics
                    )

                    validation_results.append(
                        {
                            "optimization_id": recommendation.id,
                            "type": recommendation.type.value,
                            "expected_impact": recommendation.estimated_impact,
                            "actual_impact": impact_analysis,
                            "validation_status": self._determine_validation_status(
                                recommendation.estimated_impact, impact_analysis
                            ),
                            "confidence_score": impact_analysis.get("confidence", 0.0),
                        }
                    )

            logger.info(f"✅ Validated {len(validation_results)} optimizations")
            return {
                "validation_results": validation_results,
                "overall_success_rate": self._calculate_overall_success_rate(validation_results),
                "validated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Error in optimization validation: {str(e)}")
            return {"validation_results": [], "error": str(e)}

    async def generate_optimization_narrative(
        self, recommendations: list[OptimizationRecommendation]
    ) -> str:
        """
        Generate natural language narrative explaining optimization recommendations and impact.
        """
        try:
            logger.info("📝 Generating optimization narrative")

            if not recommendations:
                return "No optimization recommendations available at this time. System performance is within acceptable parameters."

            # Categorize recommendations
            critical_recs = [
                r for r in recommendations if r.priority == OptimizationPriority.CRITICAL
            ]
            high_recs = [r for r in recommendations if r.priority == OptimizationPriority.HIGH]

            # Calculate total potential impact
            total_performance_gain = sum(
                r.estimated_impact.get("performance_gain", 0) for r in recommendations
            )
            total_cost_reduction = sum(
                r.estimated_impact.get("cost_reduction", 0) for r in recommendations
            )

            # Use NLG service to create narrative
            narrative_context = {
                "total_recommendations": len(recommendations),
                "critical_count": len(critical_recs),
                "high_priority_count": len(high_recs),
                "estimated_performance_gain": total_performance_gain,
                "estimated_cost_reduction": total_cost_reduction,
                "top_recommendations": recommendations[:5],
                "auto_applicable_count": len([r for r in recommendations if r.auto_applicable]),
            }

            # Import the enum values from nlg_service
            from core.services.nlg_service import InsightType, NarrativeStyle

            narrative_result = await self.nlg_service.generate_insight_narrative(
                analytics_data=narrative_context,
                insight_type=InsightType.PERFORMANCE,
                style=NarrativeStyle.EXECUTIVE,
            )

            # Extract the narrative text from the result
            narrative = (
                narrative_result.narrative
                if hasattr(narrative_result, "narrative")
                else str(narrative_result)
            )

            return narrative

        except Exception as e:
            logger.error(f"❌ Error generating optimization narrative: {str(e)}")
            return f"Error generating optimization narrative: {str(e)}"

    # === PRIVATE HELPER METHODS ===

    async def _collect_performance_metrics(self) -> dict[str, Any]:
        """Collect comprehensive performance metrics from all system components."""
        try:
            # This would integrate with actual monitoring systems
            # For now, return simulated metrics
            return {
                "timestamp": datetime.now().isoformat(),
                "collection_duration_ms": 150,
                "metrics_collected": 45,
            }
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {str(e)}")
            return {}

    async def _analyze_query_performance(self) -> dict[str, Any]:
        """Analyze database query performance patterns."""
        try:
            # Simulate query analysis - in production would analyze actual query logs
            return {
                "avg_time_ms": 850,
                "historical_avg": 720,
                "slow_queries": 12,
                "historical_slow_queries": 8,
                "most_expensive_queries": [
                    {
                        "query": "SELECT * FROM analytics_data WHERE...",
                        "avg_time_ms": 2400,
                    },
                    {"query": "SELECT channel_stats FROM...", "avg_time_ms": 1800},
                ],
                "trend_data": [650, 720, 780, 850],  # Last 4 periods
                "slow_query_trend": [5, 6, 8, 12],
            }
        except Exception as e:
            logger.error(f"Error analyzing query performance: {str(e)}")
            return {}

    async def _analyze_resource_utilization(self) -> dict[str, Any]:
        """Analyze system resource utilization patterns."""
        try:
            # Simulate resource analysis
            return {
                "cpu_percent": 78,
                "cpu_avg": 65,
                "memory_percent": 82,
                "memory_avg": 70,
                "disk_io_wait": 15,
                "network_utilization": 45,
                "cpu_trend": [60, 65, 72, 78],
                "memory_trend": [65, 70, 75, 82],
            }
        except Exception as e:
            logger.error(f"Error analyzing resource utilization: {str(e)}")
            return {}

    async def _analyze_cache_performance(self) -> dict[str, Any]:
        """Analyze cache effectiveness and hit rates."""
        try:
            # Simulate cache analysis
            return {
                "hit_rate": 0.78,
                "historical_hit_rate": 0.85,
                "miss_rate": 0.22,
                "eviction_rate": 0.05,
                "hit_rate_trend": [0.85, 0.82, 0.80, 0.78],
            }
        except Exception as e:
            logger.error(f"Error analyzing cache performance: {str(e)}")
            return {}

    def _calculate_trend(self, trend_data: list[float]) -> str:
        """Calculate trend direction from data points."""
        if len(trend_data) < 2:
            return "stable"

        recent_avg = sum(trend_data[-2:]) / 2
        earlier_avg = sum(trend_data[:-2]) / max(1, len(trend_data) - 2)

        if recent_avg > earlier_avg * 1.05:
            return "increasing"
        elif recent_avg < earlier_avg * 0.95:
            return "decreasing"
        else:
            return "stable"

    async def _generate_query_optimizations(
        self, baseline: PerformanceBaseline
    ) -> list[OptimizationRecommendation]:
        """Generate query-specific optimization recommendations."""
        recommendations = []

        # Index optimization
        recommendations.append(
            OptimizationRecommendation(
                id=f"idx_opt_{int(datetime.now().timestamp())}",
                type=OptimizationType.INDEX_SUGGESTION,
                priority=OptimizationPriority.HIGH,
                title="Add Missing Database Indexes",
                description="Add strategic indexes to improve query performance for slow analytics queries",
                technical_details={
                    "suggested_indexes": [
                        "CREATE INDEX idx_analytics_channel_date ON analytics_data(channel_id, date_recorded)",
                        "CREATE INDEX idx_user_metrics_timestamp ON user_metrics(timestamp DESC)",
                    ],
                    "estimated_query_improvement": "60-80%",
                },
                estimated_impact={
                    "performance_gain": 0.65,
                    "cost_reduction": 0.15,
                    "user_experience_improvement": 0.70,
                },
                implementation_complexity="low",
                auto_applicable=True,
                validation_metrics=["avg_query_time", "slow_query_count"],
                created_at=datetime.now(),
            )
        )

        return recommendations

    async def _generate_cpu_optimizations(
        self, baseline: PerformanceBaseline
    ) -> list[OptimizationRecommendation]:
        """Generate CPU-specific optimization recommendations."""
        recommendations = []

        # Query optimization for CPU reduction
        recommendations.append(
            OptimizationRecommendation(
                id=f"cpu_opt_{int(datetime.now().timestamp())}",
                type=OptimizationType.QUERY_OPTIMIZATION,
                priority=OptimizationPriority.HIGH,
                title="Optimize CPU-Intensive Analytics Queries",
                description="Refactor expensive aggregation queries to reduce CPU utilization",
                technical_details={
                    "optimization_strategies": [
                        "Use materialized views for complex aggregations",
                        "Implement query result caching",
                        "Optimize JSON parsing operations",
                    ]
                },
                estimated_impact={
                    "performance_gain": 0.40,
                    "cpu_reduction": 0.25,
                    "cost_reduction": 0.20,
                },
                implementation_complexity="medium",
                auto_applicable=False,
                validation_metrics=["cpu_usage", "query_execution_time"],
                created_at=datetime.now(),
            )
        )

        return recommendations

    async def _generate_memory_optimizations(
        self, baseline: PerformanceBaseline
    ) -> list[OptimizationRecommendation]:
        """Generate memory-specific optimization recommendations."""
        recommendations = []

        # Memory-efficient data processing
        recommendations.append(
            OptimizationRecommendation(
                id=f"mem_opt_{int(datetime.now().timestamp())}",
                type=OptimizationType.RESOURCE_ALLOCATION,
                priority=OptimizationPriority.MEDIUM,
                title="Optimize Memory Usage for Large Datasets",
                description="Implement streaming data processing to reduce memory footprint",
                technical_details={
                    "strategies": [
                        "Implement data streaming for large analytics queries",
                        "Add pagination to data-heavy endpoints",
                        "Optimize object lifecycle management",
                    ]
                },
                estimated_impact={
                    "memory_reduction": 0.30,
                    "performance_gain": 0.20,
                    "stability_improvement": 0.40,
                },
                implementation_complexity="medium",
                auto_applicable=False,
                validation_metrics=["memory_usage", "response_time"],
                created_at=datetime.now(),
            )
        )

        return recommendations

    async def _generate_cache_optimizations(
        self, baseline: PerformanceBaseline
    ) -> list[OptimizationRecommendation]:
        """Generate cache-specific optimization recommendations."""
        recommendations = []

        # Cache strategy optimization
        recommendations.append(
            OptimizationRecommendation(
                id=f"cache_opt_{int(datetime.now().timestamp())}",
                type=OptimizationType.CACHE_STRATEGY,
                priority=OptimizationPriority.HIGH,
                title="Improve Cache Hit Rate Strategy",
                description="Optimize cache TTL and implement intelligent pre-warming",
                technical_details={
                    "improvements": [
                        "Implement predictive cache pre-warming",
                        "Optimize TTL based on data access patterns",
                        "Add cache compression for large objects",
                    ]
                },
                estimated_impact={
                    "cache_hit_improvement": 0.15,
                    "performance_gain": 0.35,
                    "cost_reduction": 0.10,
                },
                implementation_complexity="low",
                auto_applicable=True,
                validation_metrics=["cache_hit_rate", "response_time"],
                created_at=datetime.now(),
            )
        )

        return recommendations

    async def _generate_advanced_optimizations(
        self,
    ) -> list[OptimizationRecommendation]:
        """Generate advanced optimization recommendations."""
        recommendations = []

        # Data partitioning optimization
        recommendations.append(
            OptimizationRecommendation(
                id=f"partition_opt_{int(datetime.now().timestamp())}",
                type=OptimizationType.DATA_PARTITIONING,
                priority=OptimizationPriority.MEDIUM,
                title="Implement Time-Based Data Partitioning",
                description="Partition analytics data by time periods to improve query performance",
                technical_details={
                    "partitioning_strategy": "Monthly partitions for analytics_data table",
                    "expected_benefits": "40-60% improvement in historical data queries",
                },
                estimated_impact={
                    "query_performance_gain": 0.50,
                    "maintenance_reduction": 0.30,
                },
                implementation_complexity="high",
                auto_applicable=False,
                validation_metrics=["query_time", "index_efficiency"],
                created_at=datetime.now(),
            )
        )

        return recommendations

    async def _apply_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Apply a specific optimization recommendation."""
        try:
            logger.info(f"🔧 Applying optimization: {recommendation.title}")

            if recommendation.type == OptimizationType.INDEX_SUGGESTION:
                return await self._apply_index_optimization(recommendation)
            elif recommendation.type == OptimizationType.CACHE_STRATEGY:
                return await self._apply_cache_optimization(recommendation)
            elif recommendation.type == OptimizationType.QUERY_OPTIMIZATION:
                return await self._apply_query_optimization(recommendation)
            else:
                logger.warning(f"Optimization type {recommendation.type} not yet implemented")
                return False

        except Exception as e:
            logger.error(f"Error applying optimization {recommendation.id}: {str(e)}")
            return False

    async def _apply_index_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Apply database index optimizations."""
        try:
            # In production, this would execute the actual index creation
            logger.info(f"✅ Applied index optimization: {recommendation.id}")
            return True
        except Exception as e:
            logger.error(f"Error applying index optimization: {str(e)}")
            return False

    async def _apply_cache_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Apply cache strategy optimizations."""
        try:
            # In production, this would update cache configurations
            logger.info(f"✅ Applied cache optimization: {recommendation.id}")
            return True
        except Exception as e:
            logger.error(f"Error applying cache optimization: {str(e)}")
            return False

    async def _apply_query_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Apply query optimizations."""
        try:
            # In production, this would modify query patterns
            logger.info(f"✅ Applied query optimization: {recommendation.id}")
            return True
        except Exception as e:
            logger.error(f"Error applying query optimization: {str(e)}")
            return False

    async def _setup_optimization_validation(
        self, recommendation: OptimizationRecommendation
    ) -> None:
        """Set up A/B testing framework to validate optimization impact."""
        try:
            test_id = f"opt_test_{recommendation.id}"

            self.ab_tests[test_id] = {
                "optimization_id": recommendation.id,
                "start_time": datetime.now(),
                "test_duration_hours": 24,
                "metrics_to_track": recommendation.validation_metrics,
                "status": "active",
            }

            logger.info(f"✅ Set up A/B test for optimization: {test_id}")

        except Exception as e:
            logger.error(f"Error setting up optimization validation: {str(e)}")

    async def _get_historical_metrics(
        self, start_time: datetime, end_time: datetime
    ) -> dict[str, Any]:
        """Get historical performance metrics for comparison."""
        try:
            # In production, this would query actual metrics store
            return {
                "avg_query_time": 750 + (end_time.hour * 10),  # Simulate variation
                "cpu_usage": 60 + (end_time.hour % 24),
                "memory_usage": 65 + (end_time.minute % 20),
                "cache_hit_rate": 0.80 + (end_time.hour % 10) / 100,
            }
        except Exception as e:
            logger.error(f"Error getting historical metrics: {str(e)}")
            return {}

    async def _calculate_optimization_impact(
        self,
        recommendation: OptimizationRecommendation,
        before_metrics: dict[str, Any],
        after_metrics: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate actual impact of applied optimization."""
        try:
            impact = {}

            # Calculate percentage improvements
            for metric in recommendation.validation_metrics:
                if metric in before_metrics and metric in after_metrics:
                    before_value = before_metrics[metric]
                    after_value = after_metrics[metric]

                    if before_value > 0:
                        improvement = (before_value - after_value) / before_value
                        impact[f"{metric}_improvement"] = improvement

            # Calculate confidence based on data quality
            impact["confidence"] = min(0.95, len(impact) / len(recommendation.validation_metrics))

            return impact

        except Exception as e:
            logger.error(f"Error calculating optimization impact: {str(e)}")
            return {"confidence": 0.0}

    def _determine_validation_status(
        self, expected_impact: dict[str, float], actual_impact: dict[str, Any]
    ) -> str:
        """Determine if optimization met expectations."""
        try:
            if actual_impact.get("confidence", 0) < 0.7:
                return "insufficient_data"

            # Check if actual improvements meet expectations
            met_expectations = 0
            total_checks = 0

            for expected_key, expected_value in expected_impact.items():
                actual_key = f"{expected_key}_improvement"
                if actual_key in actual_impact:
                    total_checks += 1
                    if actual_impact[actual_key] >= expected_value * 0.8:  # 80% of expected
                        met_expectations += 1

            if total_checks == 0:
                return "no_comparable_metrics"

            success_rate = met_expectations / total_checks

            if success_rate >= 0.8:
                return "successful"
            elif success_rate >= 0.5:
                return "partially_successful"
            else:
                return "unsuccessful"

        except Exception as e:
            logger.error(f"Error determining validation status: {str(e)}")
            return "error"

    def _calculate_overall_success_rate(self, validation_results: list[dict[str, Any]]) -> float:
        """Calculate overall success rate of applied optimizations."""
        if not validation_results:
            return 0.0

        successful = len([r for r in validation_results if r["validation_status"] == "successful"])
        return successful / len(validation_results)
