"""
Posting Time Recommendation Service
===================================

Dedicated service for optimal posting time analysis.
Single Responsibility: Posting time recommendations only.

This service replaces the god object method in analytics_orchestrator_service.py
and provides clean, focused functionality for time-based recommendations.
"""

import logging
from typing import Any

from .models.posting_time_models import AnalysisParameters, PostingTimeAnalysisResult
from .recommendation_engine import RecommendationEngine
from .time_analysis_repository import TimeAnalysisRepository

logger = logging.getLogger(__name__)


class PostingTimeRecommendationService:
    """
    Dedicated service for posting time recommendations.

    Coordinates between repository (data access) and engine (business logic)
    to provide clean, consistent posting time analysis.
    """

    def __init__(self, db_pool):
        """
        Initialize service with database pool.

        Args:
            db_pool: AsyncPG database connection pool
        """
        self.repository = TimeAnalysisRepository(db_pool)
        self.engine = RecommendationEngine()

    async def get_best_posting_times(self, channel_id: int, days: int = 90) -> dict[str, Any]:
        """
        Get optimal posting times for a channel.

        This method replaces the 235-line god object method with clean,
        focused architecture that separates concerns properly.

        Args:
            channel_id: Channel ID to analyze
            days: Number of days to analyze (7, 30, 90, or 365)

        Returns:
            Dictionary with posting time recommendations in API format
        """
        try:
            logger.info(
                f"⏰ Getting best posting times for channel {channel_id} (last {days} days)"
            )

            # Create analysis parameters with intelligent thresholds
            params = self._create_analysis_parameters(channel_id, days)

            # Get raw data from repository (database queries)
            raw_data = await self.repository.get_posting_time_metrics(params)

            if not raw_data:
                return self._create_error_response(
                    channel_id, "Failed to retrieve data from database"
                )

            # Generate recommendations using business logic engine
            result = self.engine.generate_recommendations(raw_data, params)

            if not result:
                return self._create_error_response(channel_id, "Failed to generate recommendations")

            # Convert to API response format
            return self._format_api_response(result)

        except Exception as e:
            logger.error(
                f"Failed to get best posting times for channel {channel_id}: {e}", exc_info=True
            )
            return self._create_error_response(channel_id, str(e))

    def _create_analysis_parameters(self, channel_id: int, days: int) -> AnalysisParameters:
        """
        Create analysis parameters with intelligent thresholds based on time period.
        Shorter periods need lower thresholds to show meaningful results.
        """
        # Adjust minimum post requirements based on time period
        if days < 7:
            min_posts_per_hour = 1
            min_posts_per_day = 1
            min_total_posts = 3
        elif days < 30:
            min_posts_per_hour = 2
            min_posts_per_day = 2
            min_total_posts = 5
        else:
            min_posts_per_hour = 3
            min_posts_per_day = 3
            min_total_posts = 10

        return AnalysisParameters(
            channel_id=channel_id,
            days=days,
            min_posts_per_hour=min_posts_per_hour,
            min_posts_per_day=min_posts_per_day,
            min_total_posts=min_total_posts,
        )

    def _format_api_response(self, result: PostingTimeAnalysisResult) -> dict[str, Any]:
        """
        Format internal result to match expected API response format.
        Maintains backward compatibility with existing frontend code.
        """
        return {
            "channel_id": result.channel_id,
            "best_times": [
                {
                    "hour": bt.hour,
                    "day": bt.day,
                    "confidence": bt.confidence,
                    "avg_engagement": bt.avg_engagement,
                }
                for bt in result.best_times
            ],
            "best_days": [
                {
                    "day": bd.day,
                    "day_number": bd.day_number,
                    "confidence": bd.confidence,
                    "avg_engagement": bd.avg_engagement,
                }
                for bd in result.best_days
            ],
            "hourly_engagement_trend": [
                {"hour": het.hour, "engagement": het.engagement, "postCount": het.post_count}
                for het in result.hourly_engagement_trend
            ],
            "current_avg_engagement": result.current_avg_engagement,
            "daily_performance": [
                {
                    "date": dp.date,
                    "dayOfWeek": dp.day_of_week,
                    "avgEngagement": dp.avg_engagement,
                    "postCount": dp.post_count,
                }
                for dp in result.daily_performance
            ],
            "analysis_period": result.analysis_period,
            "total_posts_analyzed": result.total_posts_analyzed,
            "confidence": result.confidence,
            "generated_at": result.generated_at,
            "data_source": result.data_source,
        }

    def _create_error_response(self, channel_id: int, error_message: str) -> dict[str, Any]:
        """Create standardized error response"""
        return {
            "channel_id": channel_id,
            "best_times": [],
            "error": error_message,
            "status": "failed",
            "data_source": "error",
        }

    async def analyze_engagement_patterns(self, channel_id: int) -> dict[str, Any] | None:
        """
        Analyze engagement patterns for a channel.
        Future method for detailed pattern analysis.
        """
        # TODO: Implement detailed engagement pattern analysis
        logger.info(f"📊 Analyzing engagement patterns for channel {channel_id}")
        return None

    async def generate_hourly_recommendations(self, channel_id: int) -> dict[str, Any] | None:
        """
        Generate hourly posting recommendations.
        Future method for granular hour-by-hour analysis.
        """
        # TODO: Implement hourly recommendation generation
        logger.info(f"⏰ Generating hourly recommendations for channel {channel_id}")
        return None
