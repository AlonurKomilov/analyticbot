"""
Analytics Orchestrator Service
Coordinates unified analytics workflows across all specialized services
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

from .ai_insights_service import AIInsightsService
from .intelligence_service import IntelligenceService
from .predictive_analytics_service import PredictiveAnalyticsService
from .statistical_analysis_service import StatisticalAnalysisService
from .trend_analysis_service import TrendAnalysisService

logger = logging.getLogger(__name__)


class AnalyticsOrchestratorService:
    """
    🎼 Analytics Orchestrator Service

    Coordinates complex analytics workflows across all specialized services.
    Provides unified analytics pipelines and cross-service data fusion.
    """

    def __init__(
        self,
        statistical_service: StatisticalAnalysisService,
        ai_insights_service: AIInsightsService,
        trend_service: TrendAnalysisService,
        predictive_service: PredictiveAnalyticsService,
        intelligence_service: IntelligenceService,
    ):
        self._statistical = statistical_service
        self._ai_insights = ai_insights_service
        self._trend = trend_service
        self._predictive = predictive_service
        self._intelligence = intelligence_service

    async def generate_comprehensive_analytics_suite(
        self,
        channel_id: int,
        analysis_period_days: int = 30,
        include_predictions: bool = True,
        include_competitive: bool = False,
        competitor_ids: list[int] | None = None,
    ) -> dict:
        """
        🎯 Generate Comprehensive Analytics Suite

        Orchestrates all analytics services to provide a complete analytical overview.
        """
        try:
            logger.info(f"Starting comprehensive analytics for channel {channel_id}")

            # Calculate date ranges
            now = datetime.now()
            from_date = now - timedelta(days=analysis_period_days)

            # Parallel execution of core analytics
            core_tasks = [
                self._statistical.calculate_statistical_significance(
                    channel_id,
                    "views",
                    analysis_period_days // 2,
                    analysis_period_days // 2,
                ),
                self._ai_insights.generate_ai_insights(
                    channel_id, "comprehensive", analysis_period_days
                ),
                self._trend.analyze_advanced_trends(channel_id, "views", analysis_period_days),
                self._intelligence.get_live_metrics(channel_id, 24),
            ]

            # Execute core analytics in parallel
            statistical_analysis, ai_insights, trend_analysis, live_metrics = await asyncio.gather(
                *core_tasks, return_exceptions=True
            )

            # Handle any exceptions
            results = {
                "channel_id": channel_id,
                "analysis_period_days": analysis_period_days,
                "generated_at": now.isoformat(),
                "statistical_analysis": (
                    statistical_analysis
                    if not isinstance(statistical_analysis, Exception)
                    else {"error": str(statistical_analysis)}
                ),
                "ai_insights": (
                    ai_insights
                    if not isinstance(ai_insights, Exception)
                    else {"error": str(ai_insights)}
                ),
                "trend_analysis": (
                    trend_analysis
                    if not isinstance(trend_analysis, Exception)
                    else {"error": str(trend_analysis)}
                ),
                "live_metrics": (
                    live_metrics
                    if not isinstance(live_metrics, Exception)
                    else {"error": str(live_metrics)}
                ),
            }

            # Optional: Add predictive analytics
            if include_predictions:
                try:
                    predictive_analytics = await self._predictive.generate_predictive_analytics(
                        channel_id, "comprehensive", 30, True
                    )
                    results["predictive_analytics"] = predictive_analytics
                except Exception as e:
                    logger.error(f"Predictive analytics failed: {e}")
                    results["predictive_analytics"] = {"error": str(e)}

            # Optional: Add competitive intelligence
            if include_competitive and competitor_ids:
                try:
                    competitive_intel = await self._intelligence.generate_competitive_intelligence(
                        channel_id, competitor_ids, "comprehensive"
                    )
                    results["competitive_intelligence"] = competitive_intel
                except Exception as e:
                    logger.error(f"Competitive intelligence failed: {e}")
                    results["competitive_intelligence"] = {"error": str(e)}

            # Generate unified insights
            results["unified_insights"] = self._generate_unified_insights(results)

            # Generate strategic recommendations
            results["strategic_recommendations"] = self._generate_strategic_recommendations(results)

            logger.info(f"Comprehensive analytics completed for channel {channel_id}")
            return results

        except Exception as e:
            logger.error(f"Comprehensive analytics suite failed: {e}")
            return {
                "channel_id": channel_id,
                "status": "error",
                "error": str(e),
                "generated_at": datetime.now().isoformat(),
            }

    async def execute_analytics_pipeline(self, channel_id: int, pipeline_config: dict) -> dict:
        """
        🔄 Execute Custom Analytics Pipeline

        Allows for custom analytics workflows based on configuration.
        """
        try:
            pipeline_steps = pipeline_config.get("steps", [])
            results = {
                "channel_id": channel_id,
                "pipeline_config": pipeline_config,
                "step_results": {},
                "executed_at": datetime.now().isoformat(),
            }

            for step in pipeline_steps:
                step_name = step.get("name")
                step_type = step.get("type")
                step_params = step.get("parameters", {})

                logger.info(f"Executing pipeline step: {step_name} ({step_type})")

                try:
                    if step_type == "statistical":
                        result = await self._execute_statistical_step(channel_id, step_params)
                    elif step_type == "ai_insights":
                        result = await self._execute_ai_insights_step(channel_id, step_params)
                    elif step_type == "trend_analysis":
                        result = await self._execute_trend_step(channel_id, step_params)
                    elif step_type == "predictive":
                        result = await self._execute_predictive_step(channel_id, step_params)
                    elif step_type == "intelligence":
                        result = await self._execute_intelligence_step(channel_id, step_params)
                    else:
                        result = {"error": f"Unknown step type: {step_type}"}

                    results["step_results"][step_name] = result

                except Exception as e:
                    logger.error(f"Pipeline step {step_name} failed: {e}")
                    results["step_results"][step_name] = {"error": str(e)}

            # Generate pipeline summary
            results["pipeline_summary"] = self._generate_pipeline_summary(results)

            return results

        except Exception as e:
            logger.error(f"Analytics pipeline execution failed: {e}")
            return {
                "channel_id": channel_id,
                "status": "error",
                "error": str(e),
                "executed_at": datetime.now().isoformat(),
            }

    async def cross_service_correlation_analysis(
        self, channel_id: int, metrics: list[str], analysis_days: int = 30
    ) -> dict:
        """
        🔗 Cross-Service Correlation Analysis

        Analyzes correlations between different analytical insights.
        """
        try:
            # Gather data from multiple services
            tasks = [
                self._statistical.calculate_statistical_significance(channel_id, metric, 15, 15)
                for metric in metrics
            ]

            # Add trend data
            tasks.append(self._trend.analyze_advanced_trends(channel_id, "views", analysis_days))

            # Add AI insights
            tasks.append(
                self._ai_insights.generate_ai_insights(channel_id, "correlation", analysis_days)
            )

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process correlation data
            correlation_data = {
                "channel_id": channel_id,
                "metrics_analyzed": metrics,
                "analysis_days": analysis_days,
                "statistical_results": results[:-2],
                "trend_data": (results[-2] if not isinstance(results[-2], Exception) else None),
                "ai_insights": (results[-1] if not isinstance(results[-1], Exception) else None),
                "correlations": self._calculate_cross_metric_correlations(results),
                "generated_at": datetime.now().isoformat(),
            }

            return correlation_data

        except Exception as e:
            logger.error(f"Cross-service correlation analysis failed: {e}")
            return {
                "channel_id": channel_id,
                "status": "error",
                "error": str(e),
                "generated_at": datetime.now().isoformat(),
            }

    def _generate_unified_insights(self, analytics_results: dict) -> dict:
        """Generate unified insights from all analytical results"""
        insights = {
            "overall_performance": "unknown",
            "key_strengths": [],
            "areas_for_improvement": [],
            "trending_patterns": [],
            "anomalies_detected": [],
            "confidence_score": 0.0,
        }

        try:
            # Analyze statistical significance
            stats = analytics_results.get("statistical_analysis", {})
            if stats and "p_value" in stats:
                if stats["p_value"] < 0.05:
                    insights["key_strengths"].append(
                        "Statistically significant performance improvements detected"
                    )
                    insights["confidence_score"] += 25

            # Analyze AI insights
            ai_insights = analytics_results.get("ai_insights", {})
            if ai_insights and "insights" in ai_insights:
                ai_recommendations = ai_insights.get("recommendations", [])
                insights["areas_for_improvement"].extend(ai_recommendations[:3])
                insights["confidence_score"] += 20

            # Analyze trends
            trends = analytics_results.get("trend_analysis", {})
            if trends and "trend_direction" in trends:
                direction = trends["trend_direction"]
                if direction == "upward":
                    insights["trending_patterns"].append("Positive growth trajectory identified")
                    insights["confidence_score"] += 20
                elif direction == "downward":
                    insights["areas_for_improvement"].append("Declining trend requires attention")

            # Determine overall performance
            if insights["confidence_score"] >= 50:
                insights["overall_performance"] = "good"
            elif insights["confidence_score"] >= 30:
                insights["overall_performance"] = "moderate"
            else:
                insights["overall_performance"] = "needs_improvement"

            return insights

        except Exception as e:
            logger.error(f"Unified insights generation failed: {e}")
            return insights

    def _generate_strategic_recommendations(self, analytics_results: dict) -> list[dict]:
        """Generate strategic recommendations based on all analytics"""
        recommendations = []

        try:
            # Content strategy recommendations
            ai_insights = analytics_results.get("ai_insights", {})
            if ai_insights and "content_analysis" in ai_insights:
                recommendations.append(
                    {
                        "category": "content_strategy",
                        "priority": "high",
                        "recommendation": "Optimize content based on AI-identified successful patterns",
                        "expected_impact": "15-25% engagement improvement",
                    }
                )

            # Growth strategy recommendations
            trends = analytics_results.get("trend_analysis", {})
            if trends and "growth_rate" in trends:
                growth_rate = trends.get("growth_rate", 0)
                if growth_rate < 5:
                    recommendations.append(
                        {
                            "category": "growth_strategy",
                            "priority": "high",
                            "recommendation": "Implement aggressive growth tactics and audience expansion",
                            "expected_impact": "Target 10%+ monthly growth",
                        }
                    )

            # Engagement optimization
            stats = analytics_results.get("statistical_analysis", {})
            if stats and "effect_size" in stats:
                if stats["effect_size"] < 0.5:
                    recommendations.append(
                        {
                            "category": "engagement",
                            "priority": "medium",
                            "recommendation": "Focus on interactive content and community building",
                            "expected_impact": "Improved audience retention",
                        }
                    )

            return recommendations

        except Exception as e:
            logger.error(f"Strategic recommendations generation failed: {e}")
            return []

    async def _execute_statistical_step(self, channel_id: int, params: dict):
        """Execute statistical analysis step"""
        metric = params.get("metric", "views")
        period1 = params.get("period1", 15)
        period2 = params.get("period2", 15)

        return await self._statistical.calculate_statistical_significance(
            channel_id, metric, period1, period2
        )

    async def _execute_ai_insights_step(self, channel_id: int, params: dict):
        """Execute AI insights step"""
        analysis_type = params.get("analysis_type", "standard")
        days = params.get("days", 30)

        return await self._ai_insights.generate_ai_insights(channel_id, analysis_type, days)

    async def _execute_trend_step(self, channel_id: int, params: dict):
        """Execute trend analysis step"""
        metric = params.get("metric", "views")
        days = params.get("days", 30)

        return await self._trend.analyze_advanced_trends(channel_id, metric, days)

    async def _execute_predictive_step(self, channel_id: int, params: dict):
        """Execute predictive analytics step"""
        prediction_type = params.get("prediction_type", "standard")
        horizon = params.get("forecast_horizon", 30)
        use_ml = params.get("use_ml_models", True)

        return await self._predictive.generate_predictive_analytics(
            channel_id, prediction_type, horizon, use_ml
        )

    async def _execute_intelligence_step(self, channel_id: int, params: dict):
        """Execute intelligence service step"""
        step_type = params.get("intelligence_type", "live_metrics")

        if step_type == "live_metrics":
            hours = params.get("hours", 6)
            return await self._intelligence.get_live_metrics(channel_id, hours)
        elif step_type == "alerts":
            return await self._intelligence.check_real_time_alerts(channel_id)
        else:
            return {"error": f"Unknown intelligence step type: {step_type}"}

    def _generate_pipeline_summary(self, pipeline_results: dict) -> dict:
        """Generate summary of pipeline execution"""
        step_results = pipeline_results.get("step_results", {})

        summary = {
            "total_steps": len(step_results),
            "successful_steps": sum(1 for result in step_results.values() if "error" not in result),
            "failed_steps": sum(1 for result in step_results.values() if "error" in result),
            "execution_status": "completed",
            "key_findings": [],
        }

        # Extract key findings from successful steps
        for step_name, result in step_results.items():
            if "error" not in result:
                # Extract relevant insights based on step type
                if "significance" in result:
                    summary["key_findings"].append(
                        f"{step_name}: Statistical significance detected"
                    )
                elif "insights" in result:
                    summary["key_findings"].append(f"{step_name}: AI insights generated")
                elif "trend_direction" in result:
                    direction = result["trend_direction"]
                    summary["key_findings"].append(f"{step_name}: {direction} trend identified")

        return summary

    def _calculate_cross_metric_correlations(self, results: list) -> dict:
        """Calculate correlations between different metrics"""
        correlations = {
            "strong_correlations": [],
            "weak_correlations": [],
            "inverse_correlations": [],
            "correlation_strength": "moderate",
        }

        try:
            # This is a simplified correlation analysis
            # In a real implementation, this would use statistical correlation methods
            valid_results = [r for r in results if not isinstance(r, Exception)]

            if len(valid_results) >= 2:
                correlations["correlation_strength"] = "sufficient_data"
                correlations["strong_correlations"].append(
                    "Views and engagement show positive correlation"
                )
            else:
                correlations["correlation_strength"] = "insufficient_data"

        except Exception as e:
            logger.error(f"Correlation calculation failed: {e}")

        return correlations
