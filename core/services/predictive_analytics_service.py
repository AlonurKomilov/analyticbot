"""
🔮 Predictive Analytics Service

This service handles all predictive analytics capabilities including:
- ML-powered engagement predictions
- Growth trajectory forecasting
- Performance optimization predictions
- ML insights generation
- Training data preparation
- Feature extraction and modeling

Extracted from AnalyticsFusionService as part of God Object refactoring.
"""

import logging
from datetime import datetime, timedelta

import numpy as np

from core.protocols import (
    ChannelRepositoryProtocol,
    DailyRepositoryProtocol,
    PostsRepositoryProtocol,
)

logger = logging.getLogger(__name__)


class PredictiveAnalyticsService:
    """
    🔮 Predictive Analytics Service

    Provides ML-powered predictive analytics including:
    - Engagement pattern predictions
    - Growth trajectory forecasting
    - Optimization opportunity detection
    - ML model integration
    """

    def __init__(
        self,
        posts_repo: PostsRepositoryProtocol,
        daily_repo: DailyRepositoryProtocol,
        channels_repo: ChannelRepositoryProtocol,
    ):
        self._posts = posts_repo
        self._daily = daily_repo
        self._channels = channels_repo

    async def generate_predictive_analytics(
        self,
        channel_id: int,
        prediction_type: str = "comprehensive",
        forecast_horizon: int = 30,
        use_ml_models: bool = True,
    ) -> dict:
        """
        🔮 Advanced Predictive Analytics with ML Integration

        Uses machine learning models and statistical forecasting to predict:
        - Future engagement rates
        - Optimal content timing
        - Growth trajectory forecasts
        - Performance optimization recommendations

        Args:
            channel_id: Target channel ID
            prediction_type: Type of prediction ('engagement', 'growth', 'optimization', 'comprehensive')
            forecast_horizon: Days to forecast ahead
            use_ml_models: Whether to use ML models from PredictiveAnalyticsEngine

        Returns:
            Comprehensive predictive analytics with confidence scores and recommendations
        """
        try:
            now = datetime.now()

            # Initialize prediction results
            predictions = {
                "channel_id": channel_id,
                "prediction_type": prediction_type,
                "forecast_horizon": forecast_horizon,
                "generated_at": now.isoformat(),
                "confidence_score": 0.0,
                "engagement_predictions": {},
                "growth_predictions": {},
                "optimization_predictions": {},
                "ml_insights": {},
                "recommendations": [],
                "model_performance": {},
            }

            # Get historical data for ML training
            training_data = await self._prepare_ml_training_data(channel_id, days=90)

            if not training_data or len(training_data["posts"]) < 10:
                return {
                    "channel_id": channel_id,
                    "status": "insufficient_data",
                    "message": "Need at least 10 posts for predictive modeling",
                    "recommendations": ["Publish more content to enable ML predictions"],
                }

            # Engagement predictions
            if prediction_type in ["engagement", "comprehensive"]:
                predictions["engagement_predictions"] = await self._predict_engagement_patterns(
                    training_data, forecast_horizon, use_ml_models
                )
                predictions["confidence_score"] += (
                    predictions["engagement_predictions"].get("confidence", 0.0) * 0.4
                )

            # Growth predictions
            if prediction_type in ["growth", "comprehensive"]:
                predictions["growth_predictions"] = await self._predict_growth_trajectory(
                    training_data, forecast_horizon, use_ml_models
                )
                predictions["confidence_score"] += (
                    predictions["growth_predictions"].get("confidence", 0.0) * 0.3
                )

            # Optimization predictions
            if prediction_type in ["optimization", "comprehensive"]:
                predictions[
                    "optimization_predictions"
                ] = await self._predict_optimization_opportunities(training_data, use_ml_models)
                predictions["confidence_score"] += (
                    predictions["optimization_predictions"].get("confidence", 0.0) * 0.3
                )

            # ML-powered insights if models are available
            if use_ml_models:
                try:
                    # Try to integrate with existing ML engine
                    from apps.bot.services.ml.predictive_engine import (
                        PredictiveAnalyticsEngine,
                    )

                    ml_engine = PredictiveAnalyticsEngine()

                    predictions["ml_insights"] = await self._generate_ml_insights(
                        ml_engine, training_data, channel_id
                    )
                except ImportError:
                    logger.warning("ML engine not available, using statistical models only")
                    predictions["ml_insights"] = {"status": "ml_engine_unavailable"}

            # Generate actionable recommendations
            predictions["recommendations"] = await self._generate_predictive_recommendations(
                predictions
            )

            # Normalize confidence score
            predictions["confidence_score"] = min(1.0, max(0.0, predictions["confidence_score"]))

            logger.info(
                f"Predictive analytics generated for channel {channel_id} with confidence {predictions['confidence_score']:.2f}"
            )
            return predictions

        except Exception as e:
            logger.error(f"Predictive analytics generation failed: {e}")
            return {
                "channel_id": channel_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _prepare_ml_training_data(self, channel_id: int, days: int = 90) -> dict:
        """Prepare comprehensive training data for ML models"""
        try:
            now = datetime.now()
            start_date = now - timedelta(days=days)

            # Get comprehensive historical data
            posts = await self._posts.top_by_views(channel_id, start_date, now, 200)

            # Get time series data
            daily_views = await self._get_daily_views(channel_id, start_date, now)
            daily_engagement = await self._get_daily_engagement(channel_id, start_date, now)
            daily_growth = await self._get_daily_growth(channel_id, start_date, now)

            # Get follower data
            follower_series = await self._daily.series_data(
                channel_id, "followers", start_date, now
            )
            if not follower_series:
                follower_series = await self._daily.series_data(
                    channel_id, "subscribers", start_date, now
                )

            # Prepare feature matrix for ML
            features = []
            targets = []

            for i, post in enumerate(posts):
                # Extract features
                post_features = self._extract_post_features(post, i, posts)

                # Target variable (performance score)
                target = self._calculate_post_performance_score(post)

                features.append(post_features)
                targets.append(target)

            return {
                "posts": posts,
                "features": features,
                "targets": targets,
                "daily_views": daily_views,
                "daily_engagement": daily_engagement,
                "daily_growth": daily_growth,
                "follower_series": follower_series,
                "period_days": days,
            }

        except Exception as e:
            logger.error(f"ML training data preparation failed: {e}")
            return {}

    async def _get_daily_views(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> list:
        """Get daily views time series"""
        try:
            daily_data = await self._daily.series_data(channel_id, "views", start_date, end_date)
            return [item.get("value", 0) for item in daily_data]
        except Exception as e:
            logger.error(f"Daily views retrieval failed: {e}")
            return []

    async def _get_daily_engagement(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> list:
        """Get daily engagement time series"""
        try:
            daily_data = await self._daily.series_data(
                channel_id, "engagement", start_date, end_date
            )
            return [item.get("value", 0) for item in daily_data]
        except Exception as e:
            logger.error(f"Daily engagement retrieval failed: {e}")
            return []

    async def _get_daily_growth(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> list:
        """Get daily growth time series"""
        try:
            daily_data = await self._daily.series_data(channel_id, "growth", start_date, end_date)
            return [item.get("value", 0) for item in daily_data]
        except Exception as e:
            logger.error(f"Daily growth retrieval failed: {e}")
            return []

    def _extract_post_features(self, post: dict, index: int, all_posts: list) -> dict:
        """Extract ML features from post data"""
        try:
            # Basic post features
            title = post.get("title", "")
            views = post.get("views", 0)
            forwards = post.get("forwards", 0)
            replies = post.get("replies", 0)
            reactions = post.get("reactions", {})

            # Time-based features
            post_date = post.get("date")
            hour_of_day = 12  # Default
            day_of_week = 1  # Default

            if post_date:
                try:
                    dt = datetime.fromisoformat(post_date.replace("Z", "+00:00"))
                    hour_of_day = dt.hour
                    day_of_week = dt.weekday()
                except:
                    pass

            # Content features
            content_length = len(title)
            word_count = len(title.split())
            has_emoji = bool(any(ord(char) > 127 for char in title))
            exclamation_count = title.count("!")
            question_count = title.count("?")

            # Engagement features
            total_reactions = sum(reactions.values()) if isinstance(reactions, dict) else 0
            engagement_score = (forwards * 3 + replies * 2 + total_reactions) / max(views, 1)

            # Historical context features
            if index > 0:
                prev_post_views = all_posts[index - 1].get("views", 0)
                view_change = views - prev_post_views
            else:
                view_change = 0

            # Recent performance features
            recent_posts = all_posts[max(0, index - 5) : index]
            avg_recent_views = (
                np.mean([p.get("views", 0) for p in recent_posts]) if recent_posts else views
            )

            return {
                "hour_of_day": hour_of_day,
                "day_of_week": day_of_week,
                "content_length": content_length,
                "word_count": word_count,
                "has_emoji": int(has_emoji),
                "exclamation_count": exclamation_count,
                "question_count": question_count,
                "engagement_score": engagement_score,
                "view_change": view_change,
                "avg_recent_views": avg_recent_views,
            }

        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {}

    def _calculate_post_performance_score(self, post: dict) -> float:
        """Calculate normalized performance score for ML target"""
        try:
            views = post.get("views", 0)
            forwards = post.get("forwards", 0)
            replies = post.get("replies", 0)
            reactions = post.get("reactions", {})

            total_reactions = sum(reactions.values()) if isinstance(reactions, dict) else 0

            # Weighted performance score
            score = views * 1.0 + forwards * 5.0 + replies * 3.0 + total_reactions * 2.0

            # Normalize to 0-100 scale
            return min(100.0, score / 100.0)

        except Exception as e:
            logger.error(f"Performance score calculation failed: {e}")
            return 50.0  # Default average score

    async def _predict_engagement_patterns(
        self, training_data: dict, forecast_horizon: int, use_ml: bool
    ) -> dict:
        """Predict future engagement patterns"""
        try:
            daily_engagement = training_data.get("daily_engagement", [])

            if len(daily_engagement) < 14:
                return {"confidence": 0.0, "message": "Insufficient engagement data"}

            # Statistical forecast
            recent_engagement = daily_engagement[-14:]  # Last 2 weeks
            avg_engagement = np.mean(recent_engagement)
            trend = np.polyfit(range(len(recent_engagement)), recent_engagement, 1)[0]

            # Generate forecast
            forecast = []
            for day in range(forecast_horizon):
                predicted_value = avg_engagement + (trend * day)
                forecast.append(max(0, predicted_value))

            # Calculate confidence based on trend consistency
            variance = np.var(recent_engagement)
            confidence = max(0.1, min(0.9, 1.0 - (variance / (avg_engagement + 1))))

            # Detect optimal posting times
            posts = training_data.get("posts", [])
            if posts:
                posting_times = {}
                for post in posts:
                    post_date = post.get("date")
                    if post_date:
                        try:
                            dt = datetime.fromisoformat(post_date.replace("Z", "+00:00"))
                            hour = dt.hour
                            engagement = post.get("forwards", 0) + post.get("replies", 0)
                            if hour not in posting_times:
                                posting_times[hour] = []
                            posting_times[hour].append(engagement)
                        except:
                            continue

                # Find best hour
                hour_avg = {
                    hour: np.mean(engagements) for hour, engagements in posting_times.items()
                }
                best_hour = max(hour_avg, key=hour_avg.get) if hour_avg else 12

                optimal_posting_times = {
                    "best_hour": best_hour,
                    "confidence": confidence,
                    "hour_analysis": hour_avg,
                }
            else:
                optimal_posting_times = {"confidence": 0.0}

            return {
                "forecast": forecast,
                "confidence": confidence,
                "trend_direction": "increasing" if trend > 0 else "decreasing",
                "trend_strength": abs(trend),
                "optimal_posting_times": optimal_posting_times,
                "avg_engagement": avg_engagement,
            }

        except Exception as e:
            logger.error(f"Engagement pattern prediction failed: {e}")
            return {"confidence": 0.0, "error": str(e)}

    async def _predict_growth_trajectory(
        self, training_data: dict, forecast_horizon: int, use_ml: bool
    ) -> dict:
        """Predict growth trajectory"""
        try:
            daily_growth = training_data.get("daily_growth", [])
            follower_series = training_data.get("follower_series", [])

            if len(daily_growth) < 7:
                return {"confidence": 0.0, "message": "Insufficient growth data"}

            # Calculate growth metrics
            recent_growth = daily_growth[-7:]  # Last week
            avg_growth = np.mean(recent_growth)
            growth_trend = np.polyfit(range(len(recent_growth)), recent_growth, 1)[0]

            # Forecast growth
            growth_forecast = []
            for day in range(forecast_horizon):
                predicted_growth = avg_growth + (growth_trend * day)
                growth_forecast.append(max(0, predicted_growth))

            # Calculate follower projection
            current_followers = follower_series[-1] if follower_series else 1000
            projected_followers = current_followers + sum(growth_forecast)

            # Growth quality assessment
            if avg_growth > 0:
                growth_trajectory = "positive"
            elif avg_growth < -10:
                growth_trajectory = "negative"
            else:
                growth_trajectory = "stable"

            confidence = max(0.1, min(0.9, 1.0 - (np.var(recent_growth) / (abs(avg_growth) + 1))))

            return {
                "growth_forecast": growth_forecast,
                "confidence": confidence,
                "growth_trajectory": growth_trajectory,
                "avg_daily_growth": avg_growth,
                "projected_followers": projected_followers,
                "growth_trend": growth_trend,
            }

        except Exception as e:
            logger.error(f"Growth trajectory prediction failed: {e}")
            return {"confidence": 0.0, "error": str(e)}

    async def _predict_optimization_opportunities(self, training_data: dict, use_ml: bool) -> dict:
        """Predict optimization opportunities"""
        try:
            posts = training_data.get("posts", [])
            daily_views = training_data.get("daily_views", [])

            if len(posts) < 5:
                return {
                    "confidence": 0.0,
                    "message": "Insufficient post data for optimization",
                }

            opportunities = []

            # Content length optimization
            length_analysis = {}
            for post in posts:
                title = post.get("title", "")
                length = len(title)
                views = post.get("views", 0)

                length_bucket = "short" if length < 50 else "medium" if length < 100 else "long"
                if length_bucket not in length_analysis:
                    length_analysis[length_bucket] = []
                length_analysis[length_bucket].append(views)

            # Find best performing length
            length_avg = {bucket: np.mean(views) for bucket, views in length_analysis.items()}
            best_length = max(length_avg, key=length_avg.get) if length_avg else "medium"

            opportunities.append(
                {
                    "type": "content_length",
                    "recommendation": f"Optimize for {best_length} content length",
                    "confidence": 0.7,
                    "impact": "medium",
                }
            )

            # Posting frequency optimization
            if len(daily_views) > 14:
                recent_views = daily_views[-14:]
                view_variance = np.var(recent_views)
                avg_views = np.mean(recent_views)

                if view_variance > avg_views * 0.5:
                    opportunities.append(
                        {
                            "type": "posting_consistency",
                            "recommendation": "Maintain more consistent posting schedule",
                            "confidence": 0.6,
                            "impact": "high",
                        }
                    )

            # Engagement optimization
            engagement_scores = []
            for post in posts:
                views = post.get("views", 0)
                forwards = post.get("forwards", 0)
                replies = post.get("replies", 0)

                if views > 0:
                    engagement_rate = (forwards + replies) / views
                    engagement_scores.append(engagement_rate)

            if engagement_scores:
                avg_engagement = np.mean(engagement_scores)
                if avg_engagement < 0.05:  # Less than 5% engagement
                    opportunities.append(
                        {
                            "type": "engagement_rate",
                            "recommendation": "Focus on content that encourages interaction",
                            "confidence": 0.8,
                            "impact": "high",
                        }
                    )

            confidence = 0.7 if len(opportunities) > 0 else 0.0

            return {
                "opportunities": opportunities,
                "confidence": confidence,
                "analysis": {
                    "length_analysis": length_avg,
                    "avg_engagement": (np.mean(engagement_scores) if engagement_scores else 0),
                },
            }

        except Exception as e:
            logger.error(f"Optimization opportunity prediction failed: {e}")
            return {"confidence": 0.0, "error": str(e)}

    async def _generate_ml_insights(self, ml_engine, training_data: dict, channel_id: int) -> dict:
        """Generate ML-powered insights"""
        try:
            # This would integrate with the ML engine
            # For now, return placeholder structure
            return {
                "model_predictions": {},
                "feature_importance": {},
                "model_confidence": 0.0,
                "recommendations": [],
                "status": "ml_engine_integration_pending",
            }
        except Exception as e:
            logger.error(f"ML insights generation failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _generate_predictive_recommendations(self, predictions: dict) -> list:
        """Generate actionable recommendations from predictions"""
        recommendations = []

        try:
            # Engagement recommendations
            engagement_pred = predictions.get("engagement_predictions", {})
            if engagement_pred.get("trend_direction") == "decreasing":
                recommendations.append(
                    {
                        "category": "engagement",
                        "recommendation": "Engagement is predicted to decline - implement re-engagement strategies",
                        "priority": "high",
                        "confidence": engagement_pred.get("confidence", 0.5),
                    }
                )

            optimal_times = engagement_pred.get("optimal_posting_times", {})
            if optimal_times.get("confidence", 0) > 0.6:
                recommendations.append(
                    {
                        "category": "timing",
                        "recommendation": f"Optimal posting time: {optimal_times['best_hour']}:00",
                        "priority": "medium",
                        "confidence": optimal_times["confidence"],
                    }
                )

            # Growth recommendations
            growth_pred = predictions.get("growth_predictions", {})
            if growth_pred.get("growth_trajectory") == "negative":
                recommendations.append(
                    {
                        "category": "growth",
                        "recommendation": "Negative growth predicted - focus on retention strategies",
                        "priority": "high",
                        "confidence": growth_pred.get("confidence", 0.5),
                    }
                )

            # Optimization recommendations
            opt_pred = predictions.get("optimization_predictions", {})
            for opportunity in opt_pred.get("opportunities", []):
                if opportunity.get("confidence", 0) > 0.6:
                    recommendations.append(
                        {
                            "category": "optimization",
                            "recommendation": f"Optimize {opportunity['type']}: {opportunity.get('recommendation', 'See details')}",
                            "priority": "medium",
                            "confidence": opportunity["confidence"],
                        }
                    )

            # Sort by priority and confidence
            priority_scores = {"high": 3, "medium": 2, "low": 1}
            recommendations.sort(
                key=lambda x: (priority_scores.get(x["priority"], 0), x["confidence"]),
                reverse=True,
            )

            return recommendations[:10]  # Top 10 recommendations

        except Exception as e:
            logger.error(f"Predictive recommendations generation failed: {e}")
            return [
                {
                    "category": "error",
                    "recommendation": "Failed to generate recommendations",
                    "priority": "low",
                }
            ]
