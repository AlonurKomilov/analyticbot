"""
AI Insights Service - Core AI-Powered Analytics (Clean Architecture)

Focused service following Single Responsibility Principle.
Handles core AI-powered content analysis and pattern recognition.

Enhanced in Phase 3 with delegation to specialized NLG services.
"""

from __future__ import annotations

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# Phase 3 Enhancement: Specialized Service Imports
from .nlg_integration_service import NLGIntegrationService
from .ai_chat_service import AIChatService
from .anomaly_analysis_service import AnomalyAnalysisService
from .nlg_service import NarrativeStyle

logger = logging.getLogger(__name__)


class AIInsightsService:
    """
    🤖 AI Insights Service (Clean Architecture)
    
    Core service for AI-powered analytics:
    - AI-powered content analysis
    - Pattern recognition and insights
    - Content optimization recommendations
    - Audience behavior analysis
    - Predictive content insights
    
    Phase 3: Delegates specialized tasks to focused services
    """

    def __init__(self, channel_daily_repo, post_repo, metrics_repo):
        """Initialize with required repositories and specialized services"""
        self._daily = channel_daily_repo
        self._posts = post_repo
        self._metrics = metrics_repo
        
        # Phase 3 Enhancement: Initialize specialized services
        self._nlg_integration = NLGIntegrationService()
        self._ai_chat = AIChatService(self, channel_daily_repo, post_repo)
        self._anomaly_analysis = AnomalyAnalysisService(
            self._nlg_integration._nlg_service, channel_daily_repo, post_repo
        )

    async def generate_ai_insights(
        self, 
        channel_id: int, 
        analysis_type: str = "comprehensive",
        days: int = 30
    ) -> dict:
        """
        🤖 Generate Core AI-Powered Analytics Insights
        
        Uses advanced algorithms to analyze content patterns, audience behavior,
        and generate actionable recommendations for content optimization.
        
        Args:
            channel_id: Target channel ID
            analysis_type: Type of analysis ('content', 'audience', 'performance', 'comprehensive')
            days: Number of days of historical data to analyze
            
        Returns:
            Comprehensive AI insights with recommendations and predictions
        """
        try:
            from datetime import datetime, timedelta
            
            now = datetime.now()
            start_date = now - timedelta(days=days)
            
            # Initialize AI insights report
            insights_report = {
                "channel_id": channel_id,
                "analysis_type": analysis_type,
                "analysis_period": {
                    "start": start_date.isoformat(),
                    "end": now.isoformat(), 
                    "days": days
                },
                "generated_at": now.isoformat(),
                "confidence_score": 0.0,
                "content_insights": {},
                "audience_insights": {},
                "performance_insights": {},
                "ai_predictions": {},
                "recommendations": [],
                "key_patterns": []
            }
            
            # Gather comprehensive data for AI analysis
            analysis_data = await self._gather_ai_analysis_data(channel_id, start_date, now)
            
            if not analysis_data or not analysis_data.get("posts"):
                return {
                    "channel_id": channel_id,
                    "status": "insufficient_data",
                    "message": "Insufficient data for AI analysis",
                    "recommendation": "Publish more content to enable AI insights"
                }
            
            # Content pattern analysis
            if analysis_type in ["content", "comprehensive"]:
                insights_report["content_insights"] = await self._analyze_content_patterns(analysis_data)
                insights_report["confidence_score"] += 0.3
            
            # Audience behavior analysis  
            if analysis_type in ["audience", "comprehensive"]:
                insights_report["audience_insights"] = await self._analyze_audience_behavior(analysis_data)
                insights_report["confidence_score"] += 0.3
            
            # Performance pattern analysis
            if analysis_type in ["performance", "comprehensive"]:
                insights_report["performance_insights"] = await self._analyze_performance_patterns(analysis_data)
                insights_report["confidence_score"] += 0.2
            
            # AI predictions
            if analysis_type in ["comprehensive"]:
                insights_report["ai_predictions"] = await self._generate_ai_predictions(analysis_data, channel_id)
                insights_report["confidence_score"] += 0.2
            
            # Generate actionable recommendations
            insights_report["recommendations"] = await self._generate_ai_recommendations(
                insights_report["content_insights"],
                insights_report["audience_insights"], 
                insights_report["performance_insights"]
            )
            
            # Extract key patterns
            insights_report["key_patterns"] = await self._extract_key_patterns(analysis_data, insights_report)
            
            # Normalize confidence score
            insights_report["confidence_score"] = min(1.0, insights_report["confidence_score"])
            
            logger.info(f"AI insights generated for channel {channel_id} with confidence {insights_report['confidence_score']:.2f}")
            return insights_report
            
        except Exception as e:
            logger.error(f"AI insights generation failed: {e}")
            return {
                "channel_id": channel_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    # === PHASE 3 DELEGATION: SPECIALIZED SERVICE METHODS ===
    
    async def generate_insights_with_narrative(
        self,
        channel_id: int,
        analysis_type: str = "comprehensive",
        days: int = 30,
        narrative_style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL
    ) -> dict:
        """🗣️ Generate insights with natural language explanations (delegates to NLGIntegrationService)"""
        try:
            # Get standard AI insights
            insights = await self.generate_ai_insights(channel_id, analysis_type, days)
            
            # Enhance with narratives via delegation
            return await self._nlg_integration.enhance_insights_with_narrative(
                insights, narrative_style, days
            )
        except Exception as e:
            logger.error(f"Narrative insights delegation failed: {e}")
            return await self.generate_ai_insights(channel_id, analysis_type, days)
    
    async def explain_performance_anomaly(
        self,
        channel_id: int,
        anomaly_data: dict,
        narrative_style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL
    ) -> dict:
        """🚨 AI-powered anomaly explanation (delegates to AnomalyAnalysisService)"""
        try:
            return await self._anomaly_analysis.analyze_and_explain_anomaly(
                channel_id, anomaly_data, narrative_style
            )
        except Exception as e:
            logger.error(f"Anomaly explanation delegation failed: {e}")
            return {
                "anomaly_detected": True,
                "explanation": "An unusual pattern was detected that requires investigation.",
                "error": str(e)
            }
    
    async def ai_chat_response(
        self,
        channel_id: int,
        user_question: str,
        context: Optional[dict] = None
    ) -> dict:
        """💬 AI chat interface (delegates to AIChatService)"""
        try:
            return await self._ai_chat.process_user_question(channel_id, user_question, context)
        except Exception as e:
            logger.error(f"AI chat delegation failed: {e}")
            return {
                "user_question": user_question,
                "ai_response": "I'm having trouble processing your question right now. Please try again later.",
                "error": str(e),
                "response_type": "error_fallback"
            }

    # === CORE AI ANALYSIS METHODS (CLEAN AND FOCUSED) ===

    
    async def _gather_ai_analysis_data(self, channel_id: int, start_date: datetime, end_date: datetime) -> dict:
        """Gather comprehensive data for AI analysis"""
        try:
            # Get posts with comprehensive metrics
            posts = await self._posts.top_by_views(channel_id, start_date, end_date, 200)
            
            # Get time series data
            daily_views = await self._daily.series_data(channel_id, "views", start_date, end_date)
            daily_followers = await self._daily.series_data(channel_id, "followers", start_date, end_date)
            
            if not daily_followers:
                daily_followers = await self._daily.series_data(channel_id, "subscribers", start_date, end_date)
            
            # Organize data for AI analysis
            analysis_data = {
                "posts": posts,
                "daily_metrics": {
                    "views": daily_views or [],
                    "followers": daily_followers or []
                },
                "time_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": (end_date - start_date).days
                },
                "sample_size": {
                    "posts": len(posts) if posts else 0,
                    "daily_points": len(daily_views) if daily_views else 0
                }
            }
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"AI analysis data gathering failed: {e}")
            return {}

    async def _analyze_content_patterns(self, data: dict) -> dict:
        """
        🎯 AI-Powered Content Pattern Analysis
        
        Analyzes content characteristics to identify patterns that drive engagement:
        - Content length optimization
        - Timing patterns
        - Topic clustering
        - Engagement drivers
        """
        try:
            posts = data.get("posts", [])
            if not posts:
                return {"status": "no_posts"}
            
            content_insights = {
                "content_length_analysis": {},
                "timing_patterns": {},
                "engagement_drivers": {},
                "optimization_opportunities": []
            }
            
            # Content length analysis
            length_performance = []
            for post in posts:
                title = post.get("title", "")
                content_length = len(title)
                views = post.get("views", 0)
                engagement_score = self._calculate_engagement_score(post)
                
                length_performance.append({
                    "length": content_length,
                    "views": views,
                    "engagement": engagement_score
                })
            
            if length_performance:
                # Find optimal content length
                length_performance.sort(key=lambda x: x["engagement"], reverse=True)
                top_performers = length_performance[:max(1, len(length_performance)//4)]
                
                optimal_length = np.mean([p["length"] for p in top_performers])
                length_correlation = np.corrcoef(
                    [p["length"] for p in length_performance],
                    [p["engagement"] for p in length_performance]
                )[0, 1] if len(length_performance) > 1 else 0
                
                content_insights["content_length_analysis"] = {
                    "optimal_length": int(optimal_length),
                    "length_correlation": float(length_correlation),
                    "recommendation": self._get_length_recommendation(optimal_length, length_correlation)
                }
            
            # Timing pattern analysis
            timing_performance = {}
            for post in posts:
                post_date = post.get("date")
                if post_date:
                    try:
                        dt = datetime.fromisoformat(post_date.replace("Z", "+00:00"))
                        hour = dt.hour
                        
                        if hour not in timing_performance:
                            timing_performance[hour] = []
                        
                        engagement_score = self._calculate_engagement_score(post)
                        timing_performance[hour].append(engagement_score)
                    except:
                        continue
            
            if timing_performance:
                # Calculate average performance by hour
                hour_averages = {}
                for hour, scores in timing_performance.items():
                    hour_averages[hour] = np.mean(scores)
                
                best_hour = max(hour_averages, key=hour_averages.get)
                best_performance = hour_averages[best_hour]
                avg_performance = np.mean(list(hour_averages.values()))
                
                content_insights["timing_patterns"] = {
                    "best_posting_hour": best_hour,
                    "performance_lift": float((best_performance - avg_performance) / avg_performance * 100),
                    "hourly_breakdown": {str(h): float(avg) for h, avg in hour_averages.items()},
                    "confidence": min(0.9, len(timing_performance[best_hour]) / 10)
                }
            
            # Engagement drivers analysis
            engagement_factors = []
            for post in posts:
                title = post.get("title", "")
                factors = {
                    "has_question": "?" in title,
                    "has_exclamation": "!" in title,
                    "has_numbers": any(char.isdigit() for char in title),
                    "has_emoji": any(ord(char) > 127 for char in title),
                    "word_count": len(title.split()),
                    "engagement_score": self._calculate_engagement_score(post)
                }
                engagement_factors.append(factors)
            
            if engagement_factors:
                # Analyze which factors correlate with high engagement
                drivers = {}
                
                # Question marks
                with_questions = [f["engagement_score"] for f in engagement_factors if f["has_question"]]
                without_questions = [f["engagement_score"] for f in engagement_factors if not f["has_question"]]
                
                if with_questions and without_questions:
                    question_boost = (np.mean(with_questions) - np.mean(without_questions)) / np.mean(without_questions) * 100
                    drivers["questions"] = {
                        "boost_percentage": float(question_boost),
                        "recommended": question_boost > 10
                    }
                
                # Emojis
                with_emoji = [f["engagement_score"] for f in engagement_factors if f["has_emoji"]]
                without_emoji = [f["engagement_score"] for f in engagement_factors if not f["has_emoji"]]
                
                if with_emoji and without_emoji:
                    emoji_boost = (np.mean(with_emoji) - np.mean(without_emoji)) / np.mean(without_emoji) * 100
                    drivers["emojis"] = {
                        "boost_percentage": float(emoji_boost),
                        "recommended": emoji_boost > 10
                    }
                
                content_insights["engagement_drivers"] = drivers
            
            # Generate optimization opportunities
            opportunities = []
            
            if content_insights.get("content_length_analysis", {}).get("length_correlation", 0) > 0.3:
                opportunities.append({
                    "type": "content_length",
                    "priority": "high",
                    "description": f"Optimize content length to ~{content_insights['content_length_analysis']['optimal_length']} characters",
                    "expected_impact": "15-25% engagement improvement"
                })
            
            if content_insights.get("timing_patterns", {}).get("performance_lift", 0) > 20:
                best_hour = content_insights["timing_patterns"]["best_posting_hour"]
                opportunities.append({
                    "type": "posting_time",
                    "priority": "medium",
                    "description": f"Post around {best_hour}:00 for optimal engagement",
                    "expected_impact": f"{content_insights['timing_patterns']['performance_lift']:.1f}% performance boost"
                })
            
            for driver_name, driver_data in content_insights.get("engagement_drivers", {}).items():
                if driver_data.get("recommended", False):
                    opportunities.append({
                        "type": f"content_{driver_name}",
                        "priority": "medium",
                        "description": f"Include {driver_name} in content for better engagement",
                        "expected_impact": f"{driver_data['boost_percentage']:.1f}% engagement boost"
                    })
            
            content_insights["optimization_opportunities"] = opportunities
            
            return content_insights
            
        except Exception as e:
            logger.error(f"Content pattern analysis failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _analyze_audience_behavior(self, data: dict) -> dict:
        """Analyze audience engagement patterns and behavior"""
        try:
            posts = data.get("posts", [])
            daily_metrics = data.get("daily_metrics", {})
            
            audience_insights = {
                "engagement_patterns": {},
                "growth_patterns": {},
                "activity_patterns": {},
                "preferences": {}
            }
            
            if posts:
                # Engagement consistency analysis
                engagement_scores = [self._calculate_engagement_score(post) for post in posts]
                
                if engagement_scores:
                    audience_insights["engagement_patterns"] = {
                        "average_engagement": float(np.mean(engagement_scores)),
                        "engagement_volatility": float(np.std(engagement_scores)),
                        "consistency_score": float(1 - (np.std(engagement_scores) / max(np.mean(engagement_scores), 0.001))),
                        "top_quartile_threshold": float(np.percentile(engagement_scores, 75))
                    }
            
            # Growth pattern analysis
            followers_data = daily_metrics.get("followers", [])
            if followers_data and len(followers_data) > 1:
                follower_counts = [f.get("value", 0) for f in followers_data]
                growth_rates = []
                
                for i in range(1, len(follower_counts)):
                    if follower_counts[i-1] > 0:
                        rate = (follower_counts[i] - follower_counts[i-1]) / follower_counts[i-1]
                        growth_rates.append(rate)
                
                if growth_rates:
                    audience_insights["growth_patterns"] = {
                        "average_growth_rate": float(np.mean(growth_rates)),
                        "growth_volatility": float(np.std(growth_rates)),
                        "growth_trend": "positive" if np.mean(growth_rates) > 0 else "negative",
                        "recent_growth": float(np.mean(growth_rates[-7:])) if len(growth_rates) >= 7 else float(np.mean(growth_rates))
                    }
            
            return audience_insights
            
        except Exception as e:
            logger.error(f"Audience behavior analysis failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _analyze_performance_patterns(self, data: dict) -> dict:
        """Analyze performance patterns and trends"""
        try:
            posts = data.get("posts", [])
            
            performance_insights = {
                "performance_distribution": {},
                "trend_analysis": {},
                "outlier_analysis": {}
            }
            
            if posts:
                views = [post.get("views", 0) for post in posts]
                
                if views:
                    performance_insights["performance_distribution"] = {
                        "mean_views": float(np.mean(views)),
                        "median_views": float(np.median(views)),
                        "std_views": float(np.std(views)),
                        "min_views": float(np.min(views)),
                        "max_views": float(np.max(views)),
                        "top_10_percent_threshold": float(np.percentile(views, 90))
                    }
                    
                    # Identify outliers (posts performing 2+ standard deviations above mean)
                    mean_views = np.mean(views)
                    std_views = np.std(views)
                    outlier_threshold = mean_views + (2 * std_views)
                    
                    outliers = [post for post in posts if post.get("views", 0) > outlier_threshold]
                    
                    performance_insights["outlier_analysis"] = {
                        "outlier_count": len(outliers),
                        "outlier_threshold": float(outlier_threshold),
                        "outlier_characteristics": self._analyze_outlier_characteristics(outliers) if outliers else {}
                    }
            
            return performance_insights
            
        except Exception as e:
            logger.error(f"Performance pattern analysis failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _generate_ai_predictions(self, data: dict, channel_id: int) -> dict:
        """Generate AI-powered predictions based on patterns"""
        try:
            posts = data.get("posts", [])
            
            predictions = {
                "next_post_performance": {},
                "optimal_strategy": {},
                "growth_forecast": {}
            }
            
            if posts and len(posts) >= 5:
                # Predict next post performance based on recent trends
                recent_posts = posts[-10:]  # Last 10 posts
                recent_views = [p.get("views", 0) for p in recent_posts]
                
                if recent_views:
                    # Simple trend-based prediction
                    trend = np.polyfit(range(len(recent_views)), recent_views, 1)[0]
                    predicted_views = recent_views[-1] + trend
                    
                    predictions["next_post_performance"] = {
                        "predicted_views": int(max(0, predicted_views)),
                        "confidence": min(0.8, len(recent_posts) / 10),
                        "trend_direction": "increasing" if trend > 0 else "decreasing",
                        "trend_strength": abs(trend)
                    }
                
                # Optimal strategy prediction
                high_performers = sorted(posts, key=lambda x: x.get("views", 0), reverse=True)[:5]
                
                if high_performers:
                    optimal_characteristics = self._extract_optimal_characteristics(high_performers)
                    predictions["optimal_strategy"] = optimal_characteristics
            
            return predictions
            
        except Exception as e:
            logger.error(f"AI predictions generation failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _generate_ai_recommendations(self, content_insights: dict, audience_insights: dict, performance_insights: dict) -> list:
        """Generate actionable AI recommendations"""
        recommendations = []
        
        try:
            # Content optimization recommendations
            content_opportunities = content_insights.get("optimization_opportunities", [])
            for opportunity in content_opportunities:
                recommendations.append({
                    "category": "content_optimization",
                    "priority": opportunity.get("priority", "medium"),
                    "recommendation": opportunity.get("description", ""),
                    "expected_impact": opportunity.get("expected_impact", ""),
                    "confidence": 0.7
                })
            
            # Timing recommendations
            timing_patterns = content_insights.get("timing_patterns", {})
            if timing_patterns.get("performance_lift", 0) > 15:
                recommendations.append({
                    "category": "posting_schedule",
                    "priority": "high",
                    "recommendation": f"Schedule posts around {timing_patterns['best_posting_hour']}:00 for optimal engagement",
                    "expected_impact": f"{timing_patterns['performance_lift']:.1f}% improvement",
                    "confidence": timing_patterns.get("confidence", 0.6)
                })
            
            # Engagement consistency recommendations
            engagement_patterns = audience_insights.get("engagement_patterns", {})
            consistency_score = engagement_patterns.get("consistency_score", 0.5)
            
            if consistency_score < 0.7:
                recommendations.append({
                    "category": "consistency",
                    "priority": "medium",
                    "recommendation": "Focus on improving content consistency to build reliable audience engagement",
                    "expected_impact": "Improved audience retention and predictable performance",
                    "confidence": 0.8
                })
            
            # Growth recommendations
            growth_patterns = audience_insights.get("growth_patterns", {})
            if growth_patterns.get("average_growth_rate", 0) < 0:
                recommendations.append({
                    "category": "growth_recovery",
                    "priority": "critical",
                    "recommendation": "Implement growth recovery strategies - analyze successful competitors and refresh content approach",
                    "expected_impact": "Reverse negative growth trend",
                    "confidence": 0.6
                })
            
            # Sort by priority and confidence
            priority_scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            recommendations.sort(key=lambda x: (priority_scores.get(x["priority"], 0), x["confidence"]), reverse=True)
            
            return recommendations[:8]  # Top 8 recommendations
            
        except Exception as e:
            logger.error(f"AI recommendations generation failed: {e}")
            return []

    async def _extract_key_patterns(self, data: dict, insights_report: dict) -> list:
        """Extract key patterns from the analysis"""
        patterns = []
        
        try:
            # Content length patterns
            content_insights = insights_report.get("content_insights", {})
            length_analysis = content_insights.get("content_length_analysis", {})
            
            if abs(length_analysis.get("length_correlation", 0)) > 0.3:
                correlation_type = "positive" if length_analysis["length_correlation"] > 0 else "negative"
                patterns.append({
                    "pattern_type": "content_length",
                    "description": f"Content length shows {correlation_type} correlation with engagement",
                    "strength": "strong" if abs(length_analysis["length_correlation"]) > 0.5 else "moderate",
                    "actionable": True
                })
            
            # Timing patterns
            timing_patterns = content_insights.get("timing_patterns", {})
            if timing_patterns.get("performance_lift", 0) > 20:
                patterns.append({
                    "pattern_type": "optimal_timing",
                    "description": f"Posts at {timing_patterns['best_posting_hour']}:00 perform {timing_patterns['performance_lift']:.1f}% better",
                    "strength": "strong",
                    "actionable": True
                })
            
            # Engagement driver patterns
            engagement_drivers = content_insights.get("engagement_drivers", {})
            for driver_name, driver_data in engagement_drivers.items():
                if driver_data.get("boost_percentage", 0) > 15:
                    patterns.append({
                        "pattern_type": "engagement_driver",
                        "description": f"Using {driver_name} increases engagement by {driver_data['boost_percentage']:.1f}%",
                        "strength": "moderate",
                        "actionable": True
                    })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Key pattern extraction failed: {e}")
            return []

    def _calculate_engagement_score(self, post: dict) -> float:
        """Calculate normalized engagement score for a post"""
        try:
            views = post.get("views", 0)
            forwards = post.get("forwards", 0)
            replies = post.get("replies", 0)
            reactions = post.get("reactions", {})
            
            if isinstance(reactions, dict):
                total_reactions = sum(reactions.values())
            else:
                total_reactions = 0
            
            if views == 0:
                return 0.0
            
            # Weighted engagement score
            engagement = (forwards * 3 + replies * 2 + total_reactions * 1) / views
            return min(1.0, engagement)  # Cap at 1.0 for normalization
            
        except Exception:
            return 0.0

    def _get_length_recommendation(self, optimal_length: float, correlation: float) -> str:
        """Generate content length recommendation"""
        if abs(correlation) < 0.2:
            return "Content length has minimal impact on engagement"
        elif correlation > 0:
            return f"Longer content performs better. Target ~{int(optimal_length)} characters."
        else:
            return f"Shorter content performs better. Target ~{int(optimal_length)} characters."

    def _analyze_outlier_characteristics(self, outliers: list) -> dict:
        """Analyze characteristics of high-performing outlier posts"""
        try:
            if not outliers:
                return {}
            
            characteristics = {
                "common_elements": [],
                "average_length": 0,
                "common_timing": {}
            }
            
            # Analyze common elements
            total_length = 0
            has_questions = 0
            has_exclamations = 0
            has_emojis = 0
            timing_hours = []
            
            for post in outliers:
                title = post.get("title", "")
                total_length += len(title)
                
                if "?" in title:
                    has_questions += 1
                if "!" in title:
                    has_exclamations += 1
                if any(ord(char) > 127 for char in title):
                    has_emojis += 1
                
                post_date = post.get("date")
                if post_date:
                    try:
                        dt = datetime.fromisoformat(post_date.replace("Z", "+00:00"))
                        timing_hours.append(dt.hour)
                    except:
                        pass
            
            characteristics["average_length"] = int(total_length / len(outliers))
            
            # Identify common elements (if >50% of outliers have them)
            if has_questions / len(outliers) > 0.5:
                characteristics["common_elements"].append("questions")
            if has_exclamations / len(outliers) > 0.5:
                characteristics["common_elements"].append("exclamations")
            if has_emojis / len(outliers) > 0.5:
                characteristics["common_elements"].append("emojis")
            
            # Most common posting time
            if timing_hours:
                most_common_hour = max(set(timing_hours), key=timing_hours.count)
                characteristics["common_timing"] = {
                    "hour": most_common_hour,
                    "frequency": timing_hours.count(most_common_hour) / len(timing_hours)
                }
            
            return characteristics
            
        except Exception as e:
            logger.error(f"Outlier analysis failed: {e}")
            return {}

    def _extract_optimal_characteristics(self, high_performers: list) -> dict:
        """Extract optimal characteristics from high-performing posts"""
        try:
            if not high_performers:
                return {}
            
            lengths = [len(p.get("title", "")) for p in high_performers]
            
            characteristics = {
                "optimal_length_range": {
                    "min": int(np.min(lengths)),
                    "max": int(np.max(lengths)),
                    "average": int(np.mean(lengths))
                },
                "success_patterns": self._analyze_outlier_characteristics(high_performers)
            }
            
            return characteristics
            
        except Exception as e:
            logger.error(f"Optimal characteristics extraction failed: {e}")
            return {}

    async def health_check(self) -> dict:
        """Health check for AI insights service"""
        return {
            "service": "AIInsightsService",
            "status": "healthy",
            "capabilities": [
                "content_pattern_analysis",
                "audience_behavior_analysis", 
                "performance_pattern_analysis",
                "ai_predictions",
                "actionable_recommendations"
            ],
            "phase3_capabilities": [
                "natural_language_insights",
                "narrative_explanations",
                "ai_chat_interface",
                "anomaly_analysis"
            ],
            "dependencies": {
                "numpy": True,
                "nlg_integration_service": True,
                "ai_chat_service": True,
                "anomaly_analysis_service": True
            },
            "architecture": "clean_with_delegation",
            "timestamp": datetime.now().isoformat()
        }
