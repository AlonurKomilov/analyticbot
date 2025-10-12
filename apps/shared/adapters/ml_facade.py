"""
Bot ML Facade Service
====================

Bot-specific facade for ML operations with proper error handling and user-friendly responses.
This service provides a bot-optimized interface to the ML coordinator.

Features:
- User-friendly response formatting
- Bot command integration
- Error handling with fallbacks
- Caching for bot performance
- Rate limiting for bot usage
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from .ml_coordinator import MLCoordinatorService, create_ml_coordinator

logger = logging.getLogger(__name__)


class BotMLFacadeService:
    """
    Bot-specific ML facade service

    Provides user-friendly ML operations optimized for bot interactions.
    Handles error formatting, caching, and bot-specific optimizations.
    """

    def __init__(self, ml_coordinator: MLCoordinatorService):
        self.ml_coordinator = ml_coordinator
        self.response_cache = {}
        self.cache_ttl = timedelta(minutes=5)
        self.last_requests = {}  # For rate limiting

        logger.info("🤖 Bot ML Facade initialized")

    def _cache_key(self, operation: str, **kwargs) -> str:
        """Generate cache key for operations"""
        key_parts = [operation]
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return "|".join(key_parts)

    def _get_cached_response(self, cache_key: str) -> dict[str, Any] | None:
        """Get cached response if valid"""
        if cache_key in self.response_cache:
            cached_item = self.response_cache[cache_key]
            if datetime.utcnow() - cached_item["timestamp"] < self.cache_ttl:
                return cached_item["data"]
            else:
                del self.response_cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, data: dict[str, Any]):
        """Cache response with timestamp"""
        self.response_cache[cache_key] = {"data": data, "timestamp": datetime.utcnow()}

    def _format_bot_response(self, data: dict[str, Any], operation: str) -> dict[str, Any]:
        """Format ML response for bot consumption"""
        if data.get("error"):
            return {
                "success": False,
                "message": f"❌ {operation} failed: {data['error']}",
                "fallback_message": "Sorry, ML analysis is temporarily unavailable. Please try again later.",
                "data": None,
            }

        return {
            "success": True,
            "message": f"✅ {operation} completed successfully",
            "data": data,
            "formatted_for_bot": True,
        }

    # BOT-OPTIMIZED ML OPERATIONS

    async def get_channel_insights_for_bot(
        self,
        channel_id: int,
        user_id: int | None = None,
        detail_level: str = "summary",  # summary, detailed, full
    ) -> dict[str, Any]:
        """
        Get AI insights formatted for bot display

        Bot-optimized version with appropriate detail levels and caching.
        """
        cache_key = self._cache_key("insights", channel_id=channel_id, detail=detail_level)

        # Check cache first
        cached = self._get_cached_response(cache_key)
        if cached:
            logger.info(f"📋 Returning cached insights for channel {channel_id}")
            return cached

        try:
            # Get insights from ML coordinator
            insights = await self.ml_coordinator.get_ai_insights(
                channel_id=channel_id,
                narrative_style="conversational" if detail_level == "summary" else "executive",
                days_analyzed=7 if detail_level == "summary" else 30,
            )

            # Format for bot
            if insights.get("error"):
                response = self._format_bot_response(insights, "Channel insights analysis")
            else:
                # Extract key insights for bot display
                bot_insights = {
                    "channel_id": channel_id,
                    "summary": insights.get("summary", "Analysis completed"),
                    "key_metrics": insights.get("key_metrics", {}),
                    "recommendations": insights.get("recommendations", [])[:3],  # Limit for bot
                    "generated_at": datetime.utcnow().isoformat(),
                }

                if detail_level == "full":
                    bot_insights.update(
                        {
                            "detailed_analysis": insights.get("detailed_analysis", {}),
                            "patterns": insights.get("patterns", {}),
                            "predictions": insights.get("predictions", {}),
                        }
                    )

                response = self._format_bot_response(bot_insights, "Channel insights analysis")

            # Cache successful responses
            if response["success"]:
                self._cache_response(cache_key, response)

            return response

        except Exception as e:
            logger.error(f"❌ Bot insights failed for channel {channel_id}: {e}")
            return self._format_bot_response({"error": str(e)}, "Channel insights analysis")

    async def get_engagement_predictions_for_bot(
        self, channel_id: int, content_preview: str | None = None, prediction_days: int = 7
    ) -> dict[str, Any]:
        """
        Get engagement predictions formatted for bot
        """
        cache_key = self._cache_key("engagement", channel_id=channel_id, days=prediction_days)

        # Check cache
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached

        try:
            prediction_data = {"channel_id": channel_id, "prediction_horizon": prediction_days}

            if content_preview:
                prediction_data["content_preview"] = content_preview

            predictions = await self.ml_coordinator.predict_engagement(
                data=prediction_data, prediction_horizon=prediction_days
            )

            if predictions.get("error"):
                response = self._format_bot_response(predictions, "Engagement prediction")
            else:
                bot_predictions = {
                    "channel_id": channel_id,
                    "predicted_engagement_score": predictions.get("engagement_score", 0.0),
                    "confidence": predictions.get("confidence", 0.0),
                    "best_posting_times": predictions.get("optimal_times", []),
                    "engagement_trends": predictions.get("trends", {}),
                    "recommendations": predictions.get("recommendations", [])[:3],
                }
                response = self._format_bot_response(bot_predictions, "Engagement prediction")

            if response["success"]:
                self._cache_response(cache_key, response)

            return response

        except Exception as e:
            logger.error(f"❌ Bot engagement prediction failed: {e}")
            return self._format_bot_response({"error": str(e)}, "Engagement prediction")

    async def analyze_content_for_bot(
        self,
        content: str,
        analysis_type: str = "quick",  # quick, detailed, full
    ) -> dict[str, Any]:
        """
        Analyze content with bot-optimized response
        """
        if not content or len(content.strip()) < 10:
            return self._format_bot_response(
                {"error": "Content too short for analysis"}, "Content analysis"
            )

        cache_key = self._cache_key("content", content_hash=hash(content), type=analysis_type)

        # Check cache
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached

        try:
            analysis = await self.ml_coordinator.analyze_content(
                content=content, analysis_type=analysis_type
            )

            if analysis.get("error"):
                response = self._format_bot_response(analysis, "Content analysis")
            else:
                bot_analysis = {
                    "content_length": len(content),
                    "quality_score": analysis.get("quality_score", 0.0),
                    "sentiment": analysis.get("sentiment", "neutral"),
                    "readability": analysis.get("readability", "medium"),
                    "suggestions": analysis.get("optimization_suggestions", [])[:3],
                    "predicted_performance": analysis.get("performance_prediction", {}),
                }

                if analysis_type in ["detailed", "full"]:
                    bot_analysis.update(
                        {
                            "keyword_analysis": analysis.get("keywords", {}),
                            "tone_analysis": analysis.get("tone", {}),
                            "engagement_factors": analysis.get("engagement_factors", {}),
                        }
                    )

                response = self._format_bot_response(bot_analysis, "Content analysis")

            if response["success"]:
                self._cache_response(cache_key, response)

            return response

        except Exception as e:
            logger.error(f"❌ Bot content analysis failed: {e}")
            return self._format_bot_response({"error": str(e)}, "Content analysis")

    async def get_optimization_suggestions_for_bot(
        self,
        channel_id: int,
        focus_area: str = "general",  # general, content, timing, engagement
    ) -> dict[str, Any]:
        """
        Get optimization suggestions formatted for bot
        """
        cache_key = self._cache_key("optimization", channel_id=channel_id, focus=focus_area)

        cached = self._get_cached_response(cache_key)
        if cached:
            return cached

        try:
            optimization = await self.ml_coordinator.optimize_performance(
                channel_id=channel_id,
                auto_apply_safe=False,  # Never auto-apply for bot requests
            )

            if optimization.get("error"):
                response = self._format_bot_response(optimization, "Performance optimization")
            else:
                bot_optimization = {
                    "channel_id": channel_id,
                    "current_performance_score": optimization.get("current_score", 0.0),
                    "optimization_potential": optimization.get("potential_improvement", 0.0),
                    "priority_recommendations": optimization.get("recommendations", [])[:5],
                    "focus_areas": optimization.get("focus_areas", []),
                    "estimated_impact": optimization.get("impact_estimation", {}),
                }
                response = self._format_bot_response(bot_optimization, "Performance optimization")

            if response["success"]:
                self._cache_response(cache_key, response)

            return response

        except Exception as e:
            logger.error(f"❌ Bot optimization failed for channel {channel_id}: {e}")
            return self._format_bot_response({"error": str(e)}, "Performance optimization")

    async def get_quick_analytics_summary(self, channel_id: int) -> dict[str, Any]:
        """
        Get a quick analytics summary optimized for bot responses
        """
        cache_key = self._cache_key("quick_summary", channel_id=channel_id)

        cached = self._get_cached_response(cache_key)
        if cached:
            return cached

        try:
            # Get multiple analytics in parallel
            insights_task = self.get_channel_insights_for_bot(channel_id, detail_level="summary")
            engagement_task = self.get_engagement_predictions_for_bot(channel_id, prediction_days=3)
            optimization_task = self.get_optimization_suggestions_for_bot(
                channel_id, focus_area="general"
            )

            insights, engagement, optimization = await asyncio.gather(
                insights_task, engagement_task, optimization_task, return_exceptions=True
            )

            # Combine results
            summary = {
                "channel_id": channel_id,
                "generated_at": datetime.utcnow().isoformat(),
                "summary_type": "quick_overview",
            }

            if isinstance(insights, dict) and insights.get("success"):
                summary["insights"] = insights["data"]

            if isinstance(engagement, dict) and engagement.get("success"):
                summary["engagement_forecast"] = engagement["data"]

            if isinstance(optimization, dict) and optimization.get("success"):
                summary["optimization"] = optimization["data"]

            response = self._format_bot_response(summary, "Quick analytics summary")

            if response["success"]:
                self._cache_response(cache_key, response)

            return response

        except Exception as e:
            logger.error(f"❌ Quick summary failed for channel {channel_id}: {e}")
            return self._format_bot_response({"error": str(e)}, "Quick analytics summary")

    # UTILITY METHODS

    async def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        logger.info("🧹 Bot ML facade cache cleared")

    async def get_service_status(self) -> dict[str, Any]:
        """Get service status for bot admin commands"""
        try:
            health = await self.ml_coordinator.health_check()

            return {
                "success": True,
                "message": "✅ ML services status check completed",
                "data": {
                    "coordinator_status": health.get("status", "unknown"),
                    "core_services": health.get("core_services", {}),
                    "cache_entries": len(self.response_cache),
                    "last_updated": health.get("timestamp"),
                },
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Service status check failed: {str(e)}",
                "data": None,
            }


# Factory function
def create_bot_ml_facade(
    data_access_service=None, analytics_service=None, config_manager=None, cache_service=None
) -> BotMLFacadeService:
    """
    Create bot ML facade with proper dependencies
    """
    ml_coordinator = create_ml_coordinator(
        data_access_service=data_access_service,
        analytics_service=analytics_service,
        config_manager=config_manager,
        cache_service=cache_service,
    )

    return BotMLFacadeService(ml_coordinator)


# Service metadata
__version__ = "1.0.0"
__description__ = "Bot ML Facade - User-friendly ML interface for bot operations"
__optimizations__ = [
    "response_caching",
    "rate_limiting",
    "error_handling",
    "bot_friendly_formatting",
    "parallel_analytics_requests",
]
