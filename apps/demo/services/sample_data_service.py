"""
Sample Data Service
===================

Generates high-quality sample data for demo showcases.
Provides realistic and engaging data that demonstrates project capabilities.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class SampleDataService:
    """Service for generating sample data for demo showcases"""

    @staticmethod
    async def generate_post_dynamics_data(channel_id: int, days: int = 30) -> dict[str, Any]:
        """Generate realistic post engagement dynamics over time"""

        base_views = random.randint(2000, 8000)
        trend_factor = random.choice([1.05, 1.02, 0.98, 0.95])  # Growth or decline trend

        dynamics = []
        for i in range(days):
            day_multiplier = 1 + (i * 0.02 * (trend_factor - 1))

            # Simulate weekly patterns (weekend dips)
            date_obj = datetime.now() - timedelta(days=days - i)
            weekday = date_obj.weekday()
            weekend_factor = 0.7 if weekday >= 5 else 1.0

            # Add some randomness
            random_factor = random.uniform(0.8, 1.3)

            daily_views = int(base_views * day_multiplier * weekend_factor * random_factor)
            daily_reactions = int(daily_views * random.uniform(0.08, 0.15))
            daily_shares = int(daily_views * random.uniform(0.02, 0.05))
            daily_comments = int(daily_views * random.uniform(0.01, 0.03))

            engagement_rate = (
                ((daily_reactions + daily_shares + daily_comments) / daily_views * 100)
                if daily_views > 0
                else 0
            )

            dynamics.append(
                {
                    "date": date_obj.isoformat(),
                    "views": daily_views,
                    "reactions": daily_reactions,
                    "shares": daily_shares,
                    "comments": daily_comments,
                    "engagement_rate": round(engagement_rate, 2),
                }
            )

        # Calculate summary statistics
        total_views = sum(d["views"] for d in dynamics)
        avg_engagement = (
            sum(d["engagement_rate"] for d in dynamics) / len(dynamics) if dynamics else 0
        )

        return {
            "channel_id": channel_id,
            "period_days": days,
            "dynamics": dynamics,
            "summary": {
                "total_views": total_views,
                "avg_engagement": round(avg_engagement, 2),
                "trend": "increasing"
                if trend_factor > 1
                else "stable"
                if trend_factor == 1
                else "decreasing",
                "best_performing_time": "19:00-21:00",
                "peak_day": "Tuesday",
                "growth_rate": round((trend_factor - 1) * 100, 1),
            },
        }

    @staticmethod
    async def generate_top_posts_data(
        channel_id: int, limit: int = 15, period: str = "week"
    ) -> list[dict[str, Any]]:
        """Generate sample top-performing posts"""

        from apps.demo.config import demo_config

        quality = demo_config.get_demo_quality_level()

        # Base engagement numbers vary by quality level
        if quality == "high":
            base_views = (8000, 20000)
            base_reactions = (600, 2000)
        elif quality == "medium":
            base_views = (3000, 12000)
            base_reactions = (250, 1200)
        else:  # basic
            base_views = (1000, 6000)
            base_reactions = (100, 600)

        sample_topics = [
            "AI and Machine Learning Trends",
            "Clean Architecture Best Practices",
            "FastAPI Performance Tips",
            "Telegram Bot Development Guide",
            "Data Analytics Insights",
            "Python Advanced Patterns",
            "Microservices Architecture",
            "API Design Principles",
            "Database Optimization Techniques",
            "Real-time Analytics Dashboard",
            "User Experience in Analytics",
            "Automation Success Stories",
            "Tech Industry Analysis",
            "Developer Productivity Hacks",
            "Cloud Infrastructure Scaling",
        ]

        posts = []
        for i in range(limit):
            views = random.randint(*base_views) - (i * 200)
            reactions = random.randint(*base_reactions) - (i * 20)
            shares = int(reactions * random.uniform(0.15, 0.25))
            comments = int(reactions * random.uniform(0.1, 0.2))

            engagement_rate = ((reactions + shares + comments) / views * 100) if views > 0 else 0
            performance_score = max(70, 98 - (i * 2) + random.randint(-5, 5))

            post = {
                "id": f"post_{channel_id}_{i+1}",
                "title": f"{sample_topics[i % len(sample_topics)]}",
                "content": f"Detailed analysis and insights about {sample_topics[i % len(sample_topics)].lower()}. "
                f"This post generated significant engagement with our community and sparked "
                f"valuable discussions about industry best practices.",
                "published_at": (
                    datetime.now() - timedelta(days=i + 1, hours=random.randint(0, 23))
                ).isoformat(),
                "metrics": {
                    "views": max(100, views),
                    "reactions": max(10, reactions),
                    "shares": max(5, shares),
                    "comments": max(2, comments),
                    "engagement_rate": round(engagement_rate, 2),
                },
                "performance_score": performance_score,
                "content_type": random.choice(["text", "text_with_image", "video", "infographic"]),
                "tags": random.sample(
                    ["analytics", "development", "ai", "automation", "insights"], 3
                ),
            }
            posts.append(post)

        return posts

    @staticmethod
    async def generate_best_times_data(channel_id: int, timezone: str = "UTC") -> dict[str, Any]:
        """Generate optimal posting time recommendations"""

        # Generate realistic posting recommendations
        optimal_windows = []

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        base_scores = [8.2, 9.1, 8.8, 9.4, 8.7, 7.5, 7.8]  # Realistic weekly pattern

        for day, base_score in zip(days, base_scores, strict=False):
            # Generate 1-2 optimal time windows per day
            primary_hour = random.choice([9, 12, 18, 19, 20, 21])
            secondary_hour = random.choice([8, 10, 13, 17, 22]) if random.random() > 0.3 else None

            times = [f"{primary_hour:02d}:00-{primary_hour+2:02d}:00"]
            if secondary_hour and secondary_hour != primary_hour:
                times.append(f"{secondary_hour:02d}:00-{secondary_hour+2:02d}:00")

            optimal_windows.append(
                {
                    "day": day,
                    "times": times,
                    "engagement_score": round(base_score + random.uniform(-0.3, 0.3), 1),
                }
            )

        # Find peak engagement time
        peak_window = max(optimal_windows, key=lambda x: x["engagement_score"])
        peak_time = f"{peak_window['day']} {peak_window['times'][0]}"

        recommendations = {
            "timezone": timezone,
            "analysis_period": "30 days",
            "optimal_posting_windows": optimal_windows,
            "peak_engagement_time": peak_time,
            "audience_activity_pattern": random.choice(
                ["evening_focused", "business_hours_active", "mixed_schedule", "global_audience"]
            ),
            "confidence_level": "high",
            "data_points_analyzed": random.randint(2000, 8000),
        }

        # Extract top 3 optimal times
        sorted_windows = sorted(optimal_windows, key=lambda x: x["engagement_score"], reverse=True)
        optimal_times = []
        for window in sorted_windows[:3]:
            for time_slot in window["times"]:
                optimal_times.append(f"{window['day']} {time_slot}")

        return {
            "recommendations": recommendations,
            "optimal_times": optimal_times[:5],  # Limit to top 5
        }

    @staticmethod
    async def generate_ai_recommendations(channel_id: int, category: str = "all") -> dict[str, Any]:
        """Generate AI-powered content and strategy recommendations"""

        all_recommendations = [
            {
                "id": "rec_content_visual",
                "type": "content",
                "title": "Increase Visual Content Usage",
                "description": "Posts with high-quality visuals receive 73% more engagement than text-only content. Your current visual content ratio is 35%.",
                "priority": "high",
                "impact_score": 8.9,
                "confidence": 0.92,
                "suggested_actions": [
                    "Create custom infographics for data-heavy posts",
                    "Add relevant images to all upcoming posts",
                    "Develop consistent visual branding guidelines",
                    "Consider short video content for complex topics",
                ],
                "expected_improvement": "65-75% increase in engagement",
            },
            {
                "id": "rec_timing_optimization",
                "type": "timing",
                "title": "Optimize Evening Posting Schedule",
                "description": "Your audience shows highest activity between 7-9 PM, but 60% of your posts are scheduled for afternoon hours.",
                "priority": "medium",
                "impact_score": 7.6,
                "confidence": 0.88,
                "suggested_actions": [
                    "Reschedule key posts for 7-9 PM window",
                    "Test weekend morning slots (9-11 AM)",
                    "Reduce afternoon posting frequency",
                    "Use scheduled posting for consistency",
                ],
                "expected_improvement": "35-45% increase in reach",
            },
            {
                "id": "rec_interactive_content",
                "type": "engagement",
                "title": "Add More Interactive Elements",
                "description": "Posts with questions, polls, or calls-to-action generate 58% more comments and drive higher engagement rates.",
                "priority": "high",
                "impact_score": 9.3,
                "confidence": 0.95,
                "suggested_actions": [
                    "End posts with thought-provoking questions",
                    "Create weekly polls on relevant topics",
                    "Respond to comments within 2 hours",
                    "Use call-to-action phrases consistently",
                ],
                "expected_improvement": "50-60% increase in comments",
            },
            {
                "id": "rec_content_variety",
                "type": "content",
                "title": "Diversify Content Types",
                "description": "Your content mix is heavily weighted toward text posts (78%). Audiences prefer varied content types for sustained engagement.",
                "priority": "medium",
                "impact_score": 7.1,
                "confidence": 0.86,
                "suggested_actions": [
                    "Share behind-the-scenes development content",
                    "Create video tutorials for complex topics",
                    "Post user success stories and testimonials",
                    "Share industry news with commentary",
                ],
                "expected_improvement": "25-35% increase in follower retention",
            },
            {
                "id": "rec_hashtag_strategy",
                "type": "strategy",
                "title": "Refine Hashtag Strategy",
                "description": "Strategic hashtag usage can increase discoverability by 40%. Your current hashtag consistency needs improvement.",
                "priority": "low",
                "impact_score": 6.4,
                "confidence": 0.79,
                "suggested_actions": [
                    "Develop 3-5 core branded hashtags",
                    "Research trending hashtags in your niche",
                    "Use 5-8 hashtags per post consistently",
                    "Track hashtag performance monthly",
                ],
                "expected_improvement": "20-30% increase in discoverability",
            },
        ]

        # Filter by category if specified
        if category != "all":
            recommendations = [r for r in all_recommendations if r["type"] == category]
        else:
            recommendations = all_recommendations

        # Generate insights
        insights = {
            "channel_performance": random.choice(
                ["excellent", "above_average", "good", "needs_improvement"]
            ),
            "growth_trend": random.choice(
                ["rapid_growth", "steady_increase", "stable", "slight_decline"]
            ),
            "engagement_health": random.choice(["excellent", "good", "fair"]),
            "content_strategy_score": round(random.uniform(6.5, 9.2), 1),
            "optimization_potential": f"{random.randint(15, 45)}% improvement possible",
            "audience_satisfaction": round(random.uniform(0.75, 0.95), 2),
            "key_strengths": [
                "Consistent posting schedule",
                "High-quality content creation",
                "Good audience retention rates",
                "Strong technical expertise",
                "Engaging writing style",
            ],
            "improvement_areas": [
                "Visual content integration",
                "Posting time optimization",
                "Interactive engagement",
                "Content type diversification",
                "Hashtag strategy refinement",
            ],
            "next_milestone": "Reach 10K engaged followers",
            "estimated_timeline": "3-4 months with recommended optimizations",
        }

        return {"recommendations": recommendations, "insights": insights}

    @staticmethod
    async def get_initial_data(user_id: int | str, demo_type: str = "standard") -> dict[str, Any]:
        """Generate initial data for demo users"""

        from apps.demo.config import demo_config

        quality = demo_config.get_demo_quality_level()

        # Generate different data based on demo type
        base_data = {
            "user": {
                "id": user_id,
                "type": demo_type,
                "welcome_message": f"Welcome to AnalyticBot demo! ({demo_type} experience)",
                "features_available": [],
            },
            "channels": [],
            "recent_analytics": {},
            "ai_insights": {},
            "notifications": [],
        }

        # Add features based on demo type
        if demo_type == "showcase":
            base_data["user"]["features_available"] = [
                "Full Analytics Dashboard",
                "AI Recommendations",
                "Content Optimization",
                "Advanced Reports",
            ]
            # Generate rich sample channels
            base_data["channels"] = [
                {
                    "id": 1,
                    "name": "Tech Insights",
                    "subscribers": 15000,
                    "growth_rate": 12.5,
                    "engagement": 8.9,
                },
                {
                    "id": 2,
                    "name": "AI Updates",
                    "subscribers": 8500,
                    "growth_rate": 18.2,
                    "engagement": 9.4,
                },
                {
                    "id": 3,
                    "name": "Developer Tips",
                    "subscribers": 12000,
                    "growth_rate": 6.8,
                    "engagement": 7.8,
                },
            ]
        elif demo_type == "limited":
            base_data["user"]["features_available"] = ["Basic Analytics", "Sample Reports"]
            # Generate basic sample data
            base_data["channels"] = [
                {
                    "id": 1,
                    "name": "Sample Channel",
                    "subscribers": 5000,
                    "growth_rate": 5.0,
                    "engagement": 6.5,
                }
            ]
        else:  # standard
            base_data["user"]["features_available"] = [
                "Analytics Dashboard",
                "Basic AI Insights",
                "Performance Reports",
            ]
            base_data["channels"] = [
                {
                    "id": 1,
                    "name": "Demo Channel",
                    "subscribers": 10000,
                    "growth_rate": 8.5,
                    "engagement": 7.5,
                },
                {
                    "id": 2,
                    "name": "Sample Content",
                    "subscribers": 6500,
                    "growth_rate": 10.2,
                    "engagement": 8.1,
                },
            ]

        # Add recent analytics summary
        base_data["recent_analytics"] = {
            "total_views": sum(c["subscribers"] for c in base_data["channels"]) * 2,
            "avg_engagement": sum(c["engagement"] for c in base_data["channels"])
            / len(base_data["channels"])
            if base_data["channels"]
            else 0,
            "growth_trend": "positive",
            "top_performing_channel": base_data["channels"][0]["name"]
            if base_data["channels"]
            else "N/A",
        }

        # Add AI insights preview
        if demo_type in ["showcase", "standard"]:
            base_data["ai_insights"] = {
                "recommendations_count": 5,
                "optimization_potential": "35% improvement possible",
                "next_action": "Review content timing optimization",
                "confidence": "high",
            }

        # Add notifications
        base_data["notifications"] = [
            {
                "type": "info",
                "message": f"You're viewing a {demo_type} demo experience",
                "action": "Explore all features in the demo showcase",
            },
            {"type": "success", "message": "Demo data loaded successfully", "action": None},
        ]

        return base_data


# Convenience instance
sample_data_service = SampleDataService()
