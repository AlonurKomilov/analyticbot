"""
Optimization Orchestrator Service
=================================

Main orchestrator for optimization fusion microservices workflow.

Single Responsibility:
- Orchestrate full optimization workflow
- Coordinate between microservices
- Manage optimization lifecycle
- Provide unified optimization interface

Coordinates: PerformanceAnalysisService, RecommendationEngineService, OptimizationApplicationService, ValidationService
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..protocols.optimization_protocols import (
    OptimizationOrchestratorProtocol,
    OptimizationRecommendation,
    PerformanceBaseline,
)

logger = logging.getLogger(__name__)


class OptimizationOrchestratorService(OptimizationOrchestratorProtocol):
    """
    Optimization orchestrator microservice.

    Single responsibility: Orchestrate optimization workflow only.
    Coordinates all optimization microservices for complete optimization lifecycle.
    """

    def __init__(
        self,
        performance_analysis_service=None,
        recommendation_engine_service=None,
        optimization_application_service=None,
        validation_service=None,
    ):
        # Microservices dependencies
        self.performance_analysis = performance_analysis_service
        self.recommendation_engine = recommendation_engine_service
        self.optimization_application = optimization_application_service
        self.validation_service = validation_service

        # Orchestration configuration
        self.orchestration_config = {
            "auto_apply_safe_optimizations": True,
            "validation_enabled": True,
            "max_concurrent_optimizations": 3,
            "optimization_cycle_hours": 24,
            "performance_monitoring_enabled": True,
        }

        # Orchestration state
        self.active_optimization_cycles: list[dict[str, Any]] = []
        self.optimization_history: list[dict[str, Any]] = []

        logger.info(
            "🎼 Optimization Orchestrator Service initialized - workflow orchestration focus"
        )

    async def orchestrate_full_optimization_cycle(
        self, auto_apply_safe: bool = True
    ) -> dict[str, Any]:
        """
        Orchestrate complete optimization workflow.

        Full cycle: Performance analysis → Recommendations → Application → Validation
        """
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            logger.info("🎭 Orchestrating full optimization cycle")

            cycle_start = datetime.now()

            orchestration_result = {
                "cycle_id": cycle_id,
                "cycle_type": "full_optimization",
                "cycle_start": cycle_start.isoformat(),
                "auto_apply_safe": auto_apply_safe,
                "steps": {},
            }

            # Step 1: Performance Analysis
            logger.info("📊 Step 1: Analyzing system performance")
            performance_result = await self.orchestrate_performance_analysis()
            orchestration_result["steps"]["performance_analysis"] = performance_result

            if not performance_result.get("performance_baselines"):
                logger.warning("⚠️ Performance analysis failed - aborting optimization cycle")
                orchestration_result["cycle_status"] = "aborted"
                orchestration_result["abort_reason"] = "performance_analysis_failed"
                return orchestration_result

            # Step 2: Recommendation Generation
            logger.info("🧠 Step 2: Generating optimization recommendations")
            recommendation_result = await self.orchestrate_recommendation_generation(
                performance_result
            )
            orchestration_result["steps"]["recommendation_generation"] = recommendation_result

            recommendations = recommendation_result.get("recommendations", [])
            if not recommendations:
                logger.info("ℹ️ No optimization recommendations generated")
                orchestration_result["cycle_status"] = "completed_no_optimizations"
                return orchestration_result

            # Step 3: Optimization Application (if enabled)
            application_result = {"status": "skipped"}
            if auto_apply_safe:
                logger.info("🔧 Step 3: Applying safe optimizations")
                application_result = await self.orchestrate_optimization_application(
                    recommendations, auto_apply=True
                )
                orchestration_result["steps"]["optimization_application"] = application_result
            else:
                logger.info("⏭️ Step 3: Skipping optimization application (auto_apply disabled)")
                orchestration_result["steps"]["optimization_application"] = application_result

            # Step 4: Validation Setup (for applied optimizations)
            validation_result = {"status": "skipped"}
            successful_apps = application_result.get("successful_applications", 0)
            if (
                self.orchestration_config["validation_enabled"]
                and isinstance(successful_apps, int)
                and successful_apps > 0
            ):
                logger.info("🔬 Step 4: Setting up optimization validation")
                validation_result = await self._setup_validation_for_applied_optimizations(
                    application_result
                )
                orchestration_result["steps"]["validation_setup"] = validation_result
            else:
                logger.info("⏭️ Step 4: Skipping validation setup")
                orchestration_result["steps"]["validation_setup"] = validation_result

            # Cycle completion
            cycle_end = datetime.now()
            cycle_duration = cycle_end - cycle_start

            orchestration_result.update(
                {
                    "cycle_status": "completed",
                    "cycle_end": cycle_end.isoformat(),
                    "cycle_duration_seconds": cycle_duration.total_seconds(),
                    "cycle_summary": self._generate_cycle_summary(orchestration_result),
                    "next_cycle_recommended": cycle_end
                    + timedelta(hours=self.orchestration_config["optimization_cycle_hours"]),
                }
            )

            # Track optimization cycle
            self.optimization_history.append(orchestration_result)

            logger.info(f"🎉 Full optimization cycle completed: {cycle_id}")
            return orchestration_result

        except Exception as e:
            logger.error(f"❌ Optimization cycle failed: {e}")
            return {
                "cycle_id": cycle_id,
                "cycle_type": "full_optimization",
                "cycle_status": "failed",
                "error": str(e),
                "cycle_end": datetime.now().isoformat(),
            }

    async def orchestrate_performance_analysis(self) -> dict[str, Any]:
        """
        Orchestrate performance analysis workflow.
        """
        try:
            logger.info("📊 Orchestrating performance analysis")

            if not self.performance_analysis:
                return {
                    "status": "service_unavailable",
                    "message": "Performance analysis service not available",
                }

            # Run comprehensive performance analysis
            performance_baselines = await self.performance_analysis.analyze_system_performance()

            # Analyze results
            analysis_summary = self._analyze_performance_results(performance_baselines)

            result = {
                "status": "completed",
                "analysis_timestamp": datetime.now().isoformat(),
                "performance_baselines": performance_baselines,
                "analysis_summary": analysis_summary,
                "concerning_metrics_count": sum(
                    1 for baseline in performance_baselines.values() if baseline.is_concerning
                ),
                "total_metrics_analyzed": len(performance_baselines),
            }

            logger.info(
                f"✅ Performance analysis completed - {result['concerning_metrics_count']} concerning metrics found"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Performance analysis orchestration failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def orchestrate_recommendation_generation(
        self, performance_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Orchestrate recommendation generation workflow.
        """
        try:
            logger.info("🎯 Orchestrating recommendation generation")

            if not self.recommendation_engine:
                return {
                    "status": "service_unavailable",
                    "message": "Recommendation engine service not available",
                }

            performance_baselines = performance_data.get("performance_baselines", {})

            if not performance_baselines:
                return {
                    "status": "no_performance_data",
                    "message": "No performance baselines available for recommendation generation",
                }

            # Generate optimization recommendations
            recommendations = (
                await self.recommendation_engine.generate_optimization_recommendations(
                    performance_baselines
                )
            )

            # Analyze recommendations
            recommendation_analysis = self._analyze_recommendations(recommendations)

            result = {
                "status": "completed",
                "generation_timestamp": datetime.now().isoformat(),
                "recommendations": recommendations,
                "recommendation_analysis": recommendation_analysis,
                "total_recommendations": len(recommendations),
                "auto_applicable_count": sum(1 for rec in recommendations if rec.auto_applicable),
                "high_priority_count": sum(
                    1 for rec in recommendations if rec.priority.value == "high"
                ),
            }

            logger.info(
                f"✅ Recommendation generation completed - {len(recommendations)} recommendations generated"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Recommendation generation orchestration failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def orchestrate_optimization_application(
        self, recommendations: list[OptimizationRecommendation], auto_apply: bool = True
    ) -> dict[str, Any]:
        """
        Orchestrate optimization application workflow.
        """
        try:
            logger.info("🔧 Orchestrating optimization application")

            if not self.optimization_application:
                return {
                    "status": "service_unavailable",
                    "message": "Optimization application service not available",
                }

            if not recommendations:
                return {
                    "status": "no_recommendations",
                    "message": "No recommendations provided for application",
                }

            if auto_apply:
                # Auto-apply safe optimizations
                application_result = (
                    await self.optimization_application.auto_apply_safe_optimizations(
                        recommendations
                    )
                )
            else:
                # Manual application workflow
                application_result = {
                    "status": "manual_review_required",
                    "message": "Recommendations prepared for manual review",
                    "recommendations_for_review": len(recommendations),
                    "auto_applicable_count": sum(
                        1 for rec in recommendations if rec.auto_applicable
                    ),
                }

            # Enhance with orchestration metadata
            application_result["orchestration_metadata"] = {
                "application_mode": "auto" if auto_apply else "manual",
                "orchestration_timestamp": datetime.now().isoformat(),
                "total_recommendations_processed": len(recommendations),
            }

            logger.info("✅ Optimization application orchestration completed")
            return application_result

        except Exception as e:
            logger.error(f"❌ Optimization application orchestration failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def _setup_validation_for_applied_optimizations(
        self, application_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Setup validation for successfully applied optimizations"""
        try:
            if not self.validation_service:
                return {
                    "status": "service_unavailable",
                    "message": "Validation service not available",
                }

            applied_optimizations = application_result.get("applied_optimizations", [])
            successful_optimizations = [
                opt for opt in applied_optimizations if opt.get("status") == "success"
            ]

            if not successful_optimizations:
                return {
                    "status": "no_optimizations_to_validate",
                    "message": "No successful optimizations to validate",
                }

            validation_setups = []

            for optimization in successful_optimizations:
                optimization_id = optimization.get("optimization_id")

                # Setup validation monitoring
                validation_setup = {
                    "optimization_id": optimization_id,
                    "validation_start": datetime.now().isoformat(),
                    "validation_scheduled": True,
                    "validation_window_hours": 72,
                }

                validation_setups.append(validation_setup)

            return {
                "status": "completed",
                "validation_setups": validation_setups,
                "validations_scheduled": len(validation_setups),
                "setup_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Validation setup failed: {e}")
            return {"status": "failed", "error": str(e)}

    def _analyze_performance_results(
        self, performance_baselines: dict[str, PerformanceBaseline]
    ) -> dict[str, Any]:
        """Analyze performance analysis results"""
        if not performance_baselines:
            return {"status": "no_data"}

        concerning_metrics = [
            name for name, baseline in performance_baselines.items() if baseline.is_concerning
        ]
        trending_up = [
            name
            for name, baseline in performance_baselines.items()
            if baseline.trend == "increasing"
        ]
        trending_down = [
            name
            for name, baseline in performance_baselines.items()
            if baseline.trend == "decreasing"
        ]

        return {
            "total_metrics": len(performance_baselines),
            "concerning_metrics": concerning_metrics,
            "trending_up_metrics": trending_up,
            "trending_down_metrics": trending_down,
            "system_health_score": self._calculate_system_health_score(performance_baselines),
            "optimization_priority": (
                "high"
                if len(concerning_metrics) > 2
                else "medium"
                if len(concerning_metrics) > 0
                else "low"
            ),
        }

    def _analyze_recommendations(
        self, recommendations: list[OptimizationRecommendation]
    ) -> dict[str, Any]:
        """Analyze generated recommendations"""
        if not recommendations:
            return {"status": "no_recommendations"}

        priority_distribution = {}
        type_distribution = {}
        auto_applicable = 0
        total_expected_impact = 0

        for rec in recommendations:
            # Priority distribution
            priority = rec.priority.value
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1

            # Type distribution
            opt_type = rec.optimization_type.value
            type_distribution[opt_type] = type_distribution.get(opt_type, 0) + 1

            # Auto-applicable count
            if rec.auto_applicable:
                auto_applicable += 1

            # Expected impact
            total_expected_impact += rec.estimated_impact.get("performance_gain", 0)

        return {
            "total_recommendations": len(recommendations),
            "priority_distribution": priority_distribution,
            "type_distribution": type_distribution,
            "auto_applicable_count": auto_applicable,
            "auto_applicable_percentage": (auto_applicable / len(recommendations)) * 100,
            "average_expected_impact": total_expected_impact / len(recommendations),
            "recommendation_quality": (
                "high" if auto_applicable > len(recommendations) * 0.3 else "medium"
            ),
        }

    def _calculate_system_health_score(
        self, performance_baselines: dict[str, PerformanceBaseline]
    ) -> float:
        """Calculate overall system health score"""
        if not performance_baselines:
            return 0.0

        healthy_metrics = sum(
            1 for baseline in performance_baselines.values() if not baseline.is_concerning
        )
        total_metrics = len(performance_baselines)

        return (healthy_metrics / total_metrics) * 100

    def _generate_cycle_summary(self, orchestration_result: dict[str, Any]) -> dict[str, Any]:
        """Generate optimization cycle summary"""
        steps = orchestration_result.get("steps", {})

        performance_step = steps.get("performance_analysis", {})
        recommendation_step = steps.get("recommendation_generation", {})
        application_step = steps.get("optimization_application", {})
        validation_step = steps.get("validation_setup", {})

        return {
            "cycle_effectiveness": self._calculate_cycle_effectiveness(steps),
            "performance_metrics_analyzed": performance_step.get("total_metrics_analyzed", 0),
            "concerning_metrics_found": performance_step.get("concerning_metrics_count", 0),
            "recommendations_generated": recommendation_step.get("total_recommendations", 0),
            "optimizations_applied": application_step.get("successful_applications", 0),
            "validations_scheduled": validation_step.get("validations_scheduled", 0),
            "cycle_completion_status": self._assess_cycle_completion(steps),
        }

    def _calculate_cycle_effectiveness(self, steps: dict[str, Any]) -> str:
        """Calculate overall cycle effectiveness"""
        completed_steps = sum(1 for step in steps.values() if step.get("status") == "completed")
        total_steps = len(steps)

        if total_steps == 0:
            return "incomplete"

        completion_rate = completed_steps / total_steps

        if completion_rate >= 0.9:
            return "excellent"
        elif completion_rate >= 0.7:
            return "good"
        elif completion_rate >= 0.5:
            return "moderate"
        else:
            return "poor"

    def _assess_cycle_completion(self, steps: dict[str, Any]) -> str:
        """Assess completion status of the optimization cycle"""
        required_steps = ["performance_analysis", "recommendation_generation"]
        optional_steps = ["optimization_application", "validation_setup"]

        required_completed = all(
            steps.get(step, {}).get("status") == "completed" for step in required_steps
        )

        if not required_completed:
            return "incomplete"

        optional_completed = sum(
            1 for step in optional_steps if steps.get(step, {}).get("status") == "completed"
        )

        if optional_completed == len(optional_steps):
            return "fully_completed"
        elif optional_completed > 0:
            return "partially_completed"
        else:
            return "basic_completed"

    async def health_check(self) -> dict[str, Any]:
        """Health check for orchestrator and all microservices"""
        # Check all microservices health
        service_health = {}

        try:
            if self.performance_analysis:
                perf_health = await self.performance_analysis.health_check()
                service_health["performance_analysis"] = perf_health.get("status", "unknown")

            if self.recommendation_engine:
                rec_health = await self.recommendation_engine.health_check()
                service_health["recommendation_engine"] = rec_health.get("status", "unknown")

            if self.optimization_application:
                app_health = await self.optimization_application.health_check()
                service_health["optimization_application"] = app_health.get("status", "unknown")

            if self.validation_service:
                val_health = await self.validation_service.health_check()
                service_health["validation_service"] = val_health.get("status", "unknown")

        except Exception as e:
            service_health["health_check_error"] = str(e)

        return {
            "service_name": "OptimizationOrchestratorService",
            "status": "operational",
            "version": "1.0.0",
            "type": "orchestrator_microservice",
            "responsibility": "optimization_orchestration",
            "orchestrated_services": [
                "PerformanceAnalysisService",
                "RecommendationEngineService",
                "OptimizationApplicationService",
                "ValidationService",
            ],
            "service_health": service_health,
            "capabilities": [
                "full_optimization_cycle",
                "performance_analysis_orchestration",
                "recommendation_generation_orchestration",
                "optimization_application_orchestration",
                "validation_orchestration",
            ],
            "configuration": self.orchestration_config,
            "active_cycles": len(self.active_optimization_cycles),
            "completed_cycles": len(self.optimization_history),
        }
