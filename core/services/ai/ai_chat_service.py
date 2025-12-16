"""
AI Chat Service - Conversational Analytics Interface

Extracted from AIInsightsService to maintain Single Responsibility Principle.
Handles conversational AI interface for analytics questions.

Part of Phase 3 AI-First Architecture.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import numpy as np

logger = logging.getLogger(__name__)


class AIChatService:
    """
    💬 AI Chat Service for Analytics

    Specialized service for conversational analytics interface:
    - Natural language question processing
    - Intent recognition and parsing
    - Contextual analytics responses
    - Follow-up question generation
    """

    def __init__(self, ai_insights_service, channel_daily_repo, post_repo):
        """Initialize with required dependencies"""
        self._ai_insights_service = ai_insights_service
        self._daily = channel_daily_repo
        self._posts = post_repo

    async def process_user_question(
        self, channel_id: int, user_question: str, context: dict | None = None
    ) -> dict:
        """
        💬 Process User Question and Generate AI Response

        Allows users to ask questions about their analytics in natural language
        and receive AI-powered answers with insights.

        Examples:
        - "Why did my engagement drop last week?"
        - "What's my best performing content type?"
        - "When should I post for maximum reach?"
        """
        try:
            # Parse user intent from question
            intent = self._parse_user_intent(user_question)

            # Get relevant analytics data based on intent
            relevant_data = await self._fetch_relevant_analytics(channel_id, intent, context)

            # Generate AI-powered response
            if intent["type"] == "performance_question":
                response = await self._answer_performance_question(
                    user_question, relevant_data, intent
                )
            elif intent["type"] == "comparison_question":
                response = await self._answer_comparison_question(
                    user_question, relevant_data, intent
                )
            elif intent["type"] == "recommendation_request":
                response = await self._provide_ai_recommendations(
                    user_question, relevant_data, intent
                )
            elif intent["type"] == "trend_inquiry":
                response = await self._explain_trends(user_question, relevant_data, intent)
            elif intent["type"] == "timing_question":
                response = await self._answer_timing_question(user_question, relevant_data, intent)
            else:
                response = await self._general_analytics_response(user_question, relevant_data)

            return {
                "user_question": user_question,
                "ai_response": response,
                "intent_detected": intent,
                "data_sources": list(relevant_data.keys()),
                "confidence": intent.get("confidence", 0.7),
                "follow_up_suggestions": self._generate_follow_up_questions(intent),
                "response_type": "ai_chat",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"AI chat response generation failed: {e}")
            return {
                "user_question": user_question,
                "ai_response": "I'm having trouble processing your question right now. Please try asking about specific metrics or check your analytics dashboard.",
                "error": str(e),
                "response_type": "error_fallback",
            }

    def _parse_user_intent(self, question: str) -> dict:
        """
        🧠 Parse User Intent from Natural Language Question

        Analyzes the question to understand what the user is asking about
        and determines the appropriate response strategy.
        """
        question_lower = question.lower()

        # Performance questions (why, drop, decline, down, low, poor)
        if any(
            word in question_lower
            for word in ["why", "drop", "decline", "down", "low", "poor", "falling"]
        ):
            return {"type": "performance_question", "focus": "decline", "confidence": 0.8}

        # Comparison questions (compare, vs, versus, better, worse)
        if any(
            word in question_lower
            for word in ["compare", "vs", "versus", "better", "worse", "difference"]
        ):
            return {"type": "comparison_question", "focus": "comparison", "confidence": 0.8}

        # Recommendation requests (should, recommend, suggest, improve, optimize)
        if any(
            word in question_lower
            for word in ["should", "recommend", "suggest", "improve", "optimize", "how to"]
        ):
            return {"type": "recommendation_request", "focus": "optimization", "confidence": 0.9}

        # Trend inquiries (trend, growing, trending, pattern)
        if any(
            word in question_lower
            for word in ["trend", "growing", "trending", "pattern", "direction"]
        ):
            return {"type": "trend_inquiry", "focus": "trends", "confidence": 0.8}

        # Best time questions (when, time, best time, schedule)
        if any(
            word in question_lower for word in ["when", "time", "best time", "schedule", "timing"]
        ):
            return {"type": "timing_question", "focus": "optimization", "confidence": 0.9}

        # Content questions (what, which, content, post)
        if any(word in question_lower for word in ["what", "which", "content", "post", "type"]):
            return {"type": "content_question", "focus": "content", "confidence": 0.7}

        # Audience questions (who, audience, followers, viewers)
        if any(
            word in question_lower
            for word in ["who", "audience", "followers", "viewers", "demographic"]
        ):
            return {"type": "audience_question", "focus": "audience", "confidence": 0.7}

        return {"type": "general", "focus": "general", "confidence": 0.5}

    async def _fetch_relevant_analytics(
        self, channel_id: int, intent: dict, context: dict | None
    ) -> dict:
        """
        📊 Fetch Analytics Data Relevant to User's Question

        Based on the detected intent, retrieves the most relevant analytics data
        to answer the user's question effectively.
        """
        data = {}

        try:
            # Always get basic overview for context
            now = datetime.now()
            start_date = now - timedelta(days=30)

            # Get AI insights for comprehensive data
            if hasattr(self._ai_insights_service, "_gather_ai_analysis_data"):
                data["overview"] = await self._ai_insights_service._gather_ai_analysis_data(
                    channel_id, start_date, now
                )
            else:
                # Fallback: get basic data directly
                data["overview"] = {
                    "posts": await self._posts.top_by_views(channel_id, start_date, now, 50),
                    "daily_metrics": {
                        "views": await self._daily.series_data(
                            channel_id, "views", start_date, now
                        ),
                        "followers": await self._daily.series_data(
                            channel_id, "followers", start_date, now
                        ),
                    },
                }

            # Get specific data based on intent
            if intent["type"] in ["performance_question", "trend_inquiry"]:
                # For performance and trends, we need historical comparison
                extended_start = now - timedelta(days=60)
                data["historical"] = {
                    "posts": await self._posts.top_by_views(
                        channel_id, extended_start, start_date, 50
                    ),
                    "daily_metrics": {
                        "views": await self._daily.series_data(
                            channel_id, "views", extended_start, start_date
                        )
                    },
                }

            if intent["type"] == "recommendation_request":
                # For recommendations, get optimization opportunities
                if hasattr(self._ai_insights_service, "_identify_optimization_opportunities"):
                    data[
                        "optimization"
                    ] = await self._ai_insights_service._identify_optimization_opportunities(
                        channel_id, data["overview"], "engagement"
                    )

            return data

        except Exception as e:
            logger.error(f"Failed to fetch relevant analytics: {e}")
            return {"overview": {}}

    async def _answer_performance_question(self, question: str, data: dict, intent: dict) -> str:
        """Answer performance-related questions with specific insights"""
        try:
            overview = data.get("overview", {})
            posts = overview.get("posts", [])

            if "engagement" in question.lower():
                if posts:
                    # Calculate recent engagement trends
                    recent_posts = posts[:10]  # Last 10 posts
                    engagement_scores = []

                    for post in recent_posts:
                        views = post.get("views", 0)
                        forwards = post.get("forwards", 0)
                        replies = post.get("replies", 0)

                        if views > 0:
                            engagement = (forwards + replies) / views * 100
                            engagement_scores.append(engagement)

                    if engagement_scores:
                        avg_engagement = np.mean(engagement_scores)
                        if avg_engagement < 2:
                            return f"Your engagement has been lower recently (average {avg_engagement:.1f}%). This could be due to changes in content timing, format, or audience preferences. I recommend reviewing your most successful posts and replicating those patterns."
                        else:
                            return f"Your engagement is performing reasonably well with an average rate of {avg_engagement:.1f}%. To improve further, consider analyzing your peak engagement times and content formats."

                return "I need more engagement data to provide specific insights. Try posting more content to build a baseline for analysis."

            elif "views" in question.lower() or "reach" in question.lower():
                if posts:
                    recent_views = [p.get("views", 0) for p in posts[:10]]
                    if recent_views:
                        avg_views = np.mean(recent_views)
                        # Compare with historical if available
                        historical = data.get("historical", {})
                        hist_posts = historical.get("posts", [])

                        if hist_posts:
                            hist_views = [p.get("views", 0) for p in hist_posts[:10]]
                            hist_avg = np.mean(hist_views) if hist_views else avg_views

                            change = (
                                ((avg_views - hist_avg) / hist_avg * 100) if hist_avg > 0 else 0
                            )

                            if change < -10:
                                return f"Your views have decreased by {abs(change):.1f}% compared to the previous period. Consider reviewing your content strategy, posting times, and audience engagement patterns."
                            elif change > 10:
                                return f"Great news! Your views have increased by {change:.1f}% compared to the previous period. Keep up the successful content patterns you've been using."
                            else:
                                return f"Your views are relatively stable with an average of {avg_views:.0f} views per post. For growth, consider experimenting with new content formats or posting times."

                        return f"Your recent posts average {avg_views:.0f} views. For specific improvement recommendations, I'd need more historical data to compare against."

                return "I need more view data to analyze your reach performance. Please ensure you have published content recently."

            return "Based on your analytics, I can see some patterns in your performance. Could you be more specific about which metric you're concerned about? (engagement, views, growth, etc.)"

        except Exception as e:
            logger.error(f"Performance question answering failed: {e}")
            return "I'm having trouble analyzing your performance data right now. Please try asking about a specific metric."

    async def _answer_comparison_question(self, question: str, data: dict, intent: dict) -> str:
        """Answer comparison-related questions"""
        try:
            overview = data.get("overview", {})
            historical = data.get("historical", {})

            current_posts = overview.get("posts", [])
            hist_posts = historical.get("posts", [])

            if current_posts and hist_posts:
                # Compare recent vs previous period
                current_avg_views = np.mean([p.get("views", 0) for p in current_posts[:10]])
                hist_avg_views = np.mean([p.get("views", 0) for p in hist_posts[:10]])

                if hist_avg_views > 0:
                    change = (current_avg_views - hist_avg_views) / hist_avg_views * 100

                    if abs(change) < 5:
                        return f"Your performance is quite consistent. Current average views ({current_avg_views:.0f}) are very similar to the previous period ({hist_avg_views:.0f}), showing stable performance."
                    elif change > 0:
                        return f"Your recent performance is {change:.1f}% better than the previous period. Current average: {current_avg_views:.0f} views vs previous: {hist_avg_views:.0f} views."
                    else:
                        return f"Your performance has declined by {abs(change):.1f}% compared to the previous period. Current average: {current_avg_views:.0f} views vs previous: {hist_avg_views:.0f} views. Consider reviewing what changed in your content strategy."

            return "To provide accurate comparisons, I need more historical data. Generally, comparing similar time periods and accounting for external factors gives the most reliable insights."

        except Exception as e:
            logger.error(f"Comparison question answering failed: {e}")
            return "I'm having trouble comparing your data right now. Please ensure you have sufficient historical content for comparison."

    async def _provide_ai_recommendations(self, question: str, data: dict, intent: dict) -> str:
        """Provide AI-powered recommendations based on data analysis"""
        try:
            optimization = data.get("optimization", [])
            overview = data.get("overview", {})
            posts = overview.get("posts", [])

            if optimization:
                top_recommendation = optimization[0] if optimization else {}
                return f"Based on your analytics, I recommend: {top_recommendation.get('description', 'focusing on content optimization')}. This could improve your {top_recommendation.get('metric', 'engagement')} by an estimated {top_recommendation.get('potential_improvement', '10-15%')}."

            elif posts:
                # Generate basic recommendations from post analysis
                post_views = [p.get("views", 0) for p in posts]
                if post_views:
                    top_performers = sorted(posts, key=lambda x: x.get("views", 0), reverse=True)[
                        :3
                    ]

                    if top_performers:
                        # Analyze top performers for patterns
                        avg_length = np.mean([len(p.get("title", "")) for p in top_performers])

                        recommendations = []
                        recommendations.append("Study your top-performing posts for patterns")
                        recommendations.append(
                            f"Your successful content averages {avg_length:.0f} characters in titles"
                        )
                        recommendations.append(
                            "Maintain consistent posting schedule for best results"
                        )

                        return "Here are my recommendations: " + ". ".join(recommendations) + "."

            return "For optimization, I recommend analyzing your top-performing content patterns and posting during your audience's most active hours. Consider experimenting with different content formats to see what resonates best."

        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return "I'm having trouble generating specific recommendations right now. Focus on consistency and analyzing what content performs best for your audience."

    async def _explain_trends(self, question: str, data: dict, intent: dict) -> str:
        """Explain trend-related questions with data analysis"""
        try:
            overview = data.get("overview", {})
            posts = overview.get("posts", [])
            daily_metrics = overview.get("daily_metrics", {})

            if posts:
                # Analyze posting trends
                post_dates = []
                post_views = []

                for post in posts:
                    if post.get("date") and post.get("views"):
                        try:
                            post_date = datetime.fromisoformat(post["date"].replace("Z", "+00:00"))
                            post_dates.append(post_date)
                            post_views.append(post.get("views", 0))
                        except:
                            continue

                if len(post_views) >= 5:
                    # Calculate trend
                    trend_slope = np.polyfit(range(len(post_views)), post_views, 1)[0]

                    if trend_slope > 0:
                        return f"Your content shows a positive growth trend! Views are generally increasing over time. Your recent posts are performing {abs(trend_slope):.0f} views better on average. This suggests your content strategy is working well."
                    elif trend_slope < -50:  # Significant decline
                        return "Your content shows a declining trend with views decreasing over time. Consider refreshing your content approach, analyzing successful competitors, or adjusting your posting schedule."
                    else:
                        return "Your content performance is relatively stable with no strong upward or downward trend. This consistency is good, but you might want to experiment with new formats to boost growth."

                return "Your content shows interesting patterns. Recent posts suggest your audience responds well to certain formats and timing. I can help you identify these patterns more specifically if you'd like."

            # Check daily metrics trends if available
            views_data = daily_metrics.get("views", [])
            if views_data and len(views_data) >= 7:
                recent_views = [v.get("value", 0) for v in views_data[-7:]]
                if recent_views:
                    recent_avg = np.mean(recent_views)
                    return f"Based on your daily metrics, you're averaging {recent_avg:.0f} views per day recently. To identify specific trends, try asking about particular aspects like 'engagement trends' or 'growth patterns'."

            return "To analyze trends effectively, I need more data points. Try asking about specific metrics like engagement, views, or growth patterns."

        except Exception as e:
            logger.error(f"Trend explanation failed: {e}")
            return "I'm having trouble analyzing trends right now. Please ensure you have enough historical content data."

    async def _answer_timing_question(self, question: str, data: dict, intent: dict) -> str:
        """Answer questions about optimal timing and scheduling"""
        try:
            overview = data.get("overview", {})
            posts = overview.get("posts", [])

            if posts:
                # Analyze posting times and performance
                time_performance = {}

                for post in posts:
                    post_date = post.get("date")
                    views = post.get("views", 0)

                    if post_date and views > 0:
                        try:
                            dt = datetime.fromisoformat(post_date.replace("Z", "+00:00"))
                            hour = dt.hour

                            if hour not in time_performance:
                                time_performance[hour] = []
                            time_performance[hour].append(views)
                        except:
                            continue

                if time_performance:
                    # Find best performing hours
                    hour_averages = {}
                    for hour, views_list in time_performance.items():
                        hour_averages[hour] = np.mean(views_list)

                    if hour_averages:
                        best_hour = max(hour_averages, key=hour_averages.get)
                        best_performance = hour_averages[best_hour]

                        # Format time nicely
                        time_str = f"{best_hour:02d}:00"

                        # Calculate performance difference
                        avg_performance = np.mean(list(hour_averages.values()))
                        if best_performance > avg_performance * 1.2:
                            boost = (best_performance - avg_performance) / avg_performance * 100
                            return f"Based on your posting history, {time_str} appears to be your optimal posting time, with {boost:.1f}% better performance than average. Your posts at this time average {best_performance:.0f} views."
                        else:
                            return f"Your posting times show relatively consistent performance. {time_str} is slightly better than average, but the difference isn't dramatic. Focus on consistency rather than precise timing."

                return "I need more data with timestamps to analyze your optimal posting times. Try posting at different times and ask me again after you have more data points."

            return "To determine your best posting times, I need to analyze your historical posts with their timestamps and performance. Please ensure you have published content at various times."

        except Exception as e:
            logger.error(f"Timing question answering failed: {e}")
            return "I'm having trouble analyzing your posting times right now. Try posting consistently for a few weeks and then ask me to analyze your optimal timing."

    async def _general_analytics_response(self, question: str, data: dict) -> str:
        """General analytics response for unclear questions"""
        overview = data.get("overview", {})
        posts = overview.get("posts", [])

        if posts:
            post_count = len(posts)
            avg_views = np.mean([p.get("views", 0) for p in posts])

            return f"I can help you understand your analytics! You have {post_count} recent posts averaging {avg_views:.0f} views. You can ask me about engagement trends, performance comparisons, optimal posting times, or request specific recommendations for improvement."

        return "I can help you understand your analytics! You can ask me about engagement trends, performance comparisons, optimal posting times, or request specific recommendations for improvement. For better insights, please ensure you have published some content first."

    def _generate_follow_up_questions(self, intent: dict) -> list:
        """Generate relevant follow-up questions based on intent"""
        follow_ups = {
            "performance_question": [
                "What's my best performing content type?",
                "When should I post for maximum engagement?",
                "How does this compare to last month?",
            ],
            "recommendation_request": [
                "What specific changes should I make?",
                "How long will it take to see results?",
                "What metrics should I monitor?",
            ],
            "trend_inquiry": [
                "Is this trend sustainable?",
                "What's driving this pattern?",
                "How can I capitalize on this trend?",
            ],
            "timing_question": [
                "What days work best for posting?",
                "How often should I post?",
                "Does posting frequency affect performance?",
            ],
            "content_question": [
                "What content format works best?",
                "How long should my posts be?",
                "What topics get the most engagement?",
            ],
            "comparison_question": [
                "How do I compare to industry standards?",
                "What time period should I compare?",
                "Which metrics matter most?",
            ],
        }

        return follow_ups.get(
            intent["type"],
            [
                "Tell me more about my analytics",
                "What should I focus on improving?",
                "How is my channel performing overall?",
            ],
        )

    async def health_check(self) -> dict:
        """Health check for AI chat service"""
        return {
            "service": "AIChatService",
            "status": "healthy",
            "capabilities": [
                "natural_language_processing",
                "intent_recognition",
                "performance_analysis",
                "trend_explanation",
                "recommendation_generation",
                "timing_optimization",
                "follow_up_suggestions",
            ],
            "supported_question_types": [
                "performance_question",
                "comparison_question",
                "recommendation_request",
                "trend_inquiry",
                "timing_question",
                "content_question",
                "audience_question",
            ],
            "dependencies": {"ai_insights_service": True, "numpy": True},
            "timestamp": datetime.now().isoformat(),
        }
