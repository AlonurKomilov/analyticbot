"""
Demo Data Service
Provides comprehensive mock data tailored to different demo user types
"""

import random
from datetime import datetime, timedelta
from typing import Any


class DemoDataService:
    """Service to provide tailored demo data based on user type"""

    def __init__(self):
        self.base_date = datetime.now()

    def get_demo_initial_data(self, demo_type: str = "full_featured") -> dict[str, Any]:
        """Get initial data tailored to demo user type"""

        if demo_type == "full_featured":
            return self._get_full_featured_data()
        elif demo_type == "read_only":
            return self._get_read_only_data()
        elif demo_type == "limited":
            return self._get_limited_data()
        elif demo_type == "admin":
            return self._get_admin_data()
        else:
            return self._get_limited_data()

    def _get_full_featured_data(self) -> dict[str, Any]:
        """Full-featured demo with all Pro capabilities"""
        return {
            "user": {
                "id": "demo_user_001",
                "username": "Demo User",
                "email": "demo@analyticbot.com",
                "plan": "pro",
                "is_demo": True,
            },
            "plan": {
                "name": "Pro Demo",
                "max_channels": 50,
                "max_posts_per_month": 5000,
                "features": [
                    "Advanced Analytics",
                    "AI Insights",
                    "Custom Branding",
                    "Priority Support",
                    "Unlimited Exports",
                    "Real-time Monitoring",
                ],
            },
            "channels": self._create_demo_channels(8),
            "scheduled_posts": self._create_demo_scheduled_posts(12),
            "analytics_summary": self._create_rich_analytics(),
        }

    def _get_read_only_data(self) -> dict[str, Any]:
        """Read-only demo focused on viewing analytics"""
        return {
            "user": {
                "id": "demo_viewer_002",
                "username": "Demo Viewer",
                "email": "viewer@analyticbot.com",
                "plan": "basic",
                "is_demo": True,
            },
            "plan": {
                "name": "Basic Demo",
                "max_channels": 10,
                "max_posts_per_month": 500,
                "features": ["Basic Analytics", "Standard Reports"],
            },
            "channels": self._create_demo_channels(3),
            "scheduled_posts": [],  # Read-only, no scheduling
            "analytics_summary": self._create_basic_analytics(),
        }

    def _get_limited_data(self) -> dict[str, Any]:
        """Limited demo with basic features"""
        return {
            "user": {
                "id": "demo_guest_003",
                "username": "Demo Guest",
                "email": "guest@analyticbot.com",
                "plan": "free",
                "is_demo": True,
            },
            "plan": {
                "name": "Free Demo",
                "max_channels": 3,
                "max_posts_per_month": 100,
                "features": ["Basic Analytics", "Manual Posting"],
            },
            "channels": self._create_demo_channels(2),
            "scheduled_posts": self._create_demo_scheduled_posts(2),
            "analytics_summary": self._create_basic_analytics(),
        }

    def _get_admin_data(self) -> dict[str, Any]:
        """Admin demo with system-wide access"""
        base_data = self._get_full_featured_data()
        base_data.update(
            {
                "user": {
                    "id": "demo_admin_999",
                    "username": "Demo Admin",
                    "email": "admin@analyticbot.com",
                    "plan": "enterprise",
                    "is_demo": True,
                    "is_admin": True,
                },
                "plan": {
                    "name": "Enterprise Demo",
                    "max_channels": 1000,
                    "max_posts_per_month": 50000,
                    "features": [
                        "All Pro Features",
                        "Admin Dashboard",
                        "User Management",
                        "System Analytics",
                        "Custom Integrations",
                    ],
                },
                "admin_stats": {
                    "total_users": 1247,
                    "active_channels": 3589,
                    "daily_posts": 892,
                    "system_health": "excellent",
                },
            }
        )
        return base_data

    def _create_demo_channels(self, count: int) -> list[dict[str, Any]]:
        """Create demo channels with realistic data"""
        channel_templates = [
            {
                "name": "Tech Innovations",
                "username": "@tech_innovations",
                "category": "technology",
            },
            {
                "name": "Marketing Tips",
                "username": "@marketing_pro",
                "category": "business",
            },
            {"name": "Daily News", "username": "@daily_news_hub", "category": "news"},
            {
                "name": "Creative Studio",
                "username": "@creative_studio",
                "category": "design",
            },
            {
                "name": "Business Insights",
                "username": "@biz_insights",
                "category": "business",
            },
            {
                "name": "Health & Wellness",
                "username": "@health_wellness",
                "category": "health",
            },
            {
                "name": "Travel Adventures",
                "username": "@travel_adventures",
                "category": "travel",
            },
            {"name": "Food & Recipe", "username": "@food_recipes", "category": "food"},
        ]

        channels = []
        for i in range(min(count, len(channel_templates))):
            template = channel_templates[i]
            channels.append(
                {
                    "id": f"demo_channel_{i + 1}",
                    "title": template["name"],
                    "username": template["username"],
                    "category": template["category"],
                    "member_count": random.randint(1000, 50000),
                    "is_active": True,
                    "created_at": (
                        self.base_date - timedelta(days=random.randint(30, 365))
                    ).isoformat(),
                    "last_post_date": (
                        self.base_date - timedelta(hours=random.randint(1, 72))
                    ).isoformat(),
                }
            )

        return channels

    def _create_demo_scheduled_posts(self, count: int) -> list[dict[str, Any]]:
        """Create demo scheduled posts"""
        post_templates = [
            "🚀 Exciting new features coming soon! Stay tuned for updates.",
            "📊 Weekly analytics report: Growth is looking fantastic!",
            "🎯 Pro tip: Best posting times are between 6-9 PM",
            "💡 Innovation spotlight: AI-powered content optimization",
            "📈 Market trends: What to watch this week",
            "🔥 Hot topic: Latest industry developments",
            "🌟 Customer success story: Amazing results!",
            "📅 Event reminder: Join our webinar tomorrow",
            "🎨 Design inspiration: Creative content ideas",
            "🤖 AI insights: Optimize your engagement",
            "📱 Mobile optimization tips for better reach",
            "🎉 Celebrating our community milestones!",
        ]

        posts = []
        for i in range(count):
            posts.append(
                {
                    "id": f"demo_scheduled_{i + 1}",
                    "channel_id": f"demo_channel_{(i % 3) + 1}",
                    "text": post_templates[i % len(post_templates)],
                    "scheduled_at": (
                        self.base_date + timedelta(hours=random.randint(1, 168))
                    ).isoformat(),
                    "status": "scheduled",
                    "media_type": random.choice([None, "photo", "video", "document"]),
                }
            )

        return posts

    def _create_rich_analytics(self) -> dict[str, Any]:
        """Create rich analytics data for full-featured demo"""
        return {
            "overview": {
                "total_views": random.randint(50000, 200000),
                "total_subscribers": random.randint(10000, 80000),
                "engagement_rate": round(random.uniform(4.5, 8.2), 2),
                "growth_rate": round(random.uniform(8.0, 25.0), 1),
            },
            "trending_posts": self._generate_trending_posts(10),
            "best_times": self._generate_best_times(),
            "ai_recommendations": self._generate_ai_recommendations(),
        }

    def _create_basic_analytics(self) -> dict[str, Any]:
        """Create basic analytics data for limited demos"""
        return {
            "overview": {
                "total_views": random.randint(5000, 20000),
                "total_subscribers": random.randint(500, 5000),
                "engagement_rate": round(random.uniform(2.5, 5.5), 2),
                "growth_rate": round(random.uniform(3.0, 12.0), 1),
            },
            "recent_posts": self._generate_recent_posts(5),
        }

    def _generate_trending_posts(self, count: int) -> list[dict[str, Any]]:
        """Generate trending posts data"""
        titles = [
            "🚀 AI Revolution in Content Creation",
            "📊 Data-Driven Marketing Strategies",
            "🎯 Engagement Optimization Techniques",
            "💡 Innovation in Digital Communication",
            "📈 Growth Hacking Success Stories",
            "🔥 Viral Content Secrets Revealed",
            "🌟 Community Building Best Practices",
            "📱 Mobile-First Content Strategy",
            "🎨 Visual Storytelling Masterclass",
            "🤖 Automation Tools for Creators",
        ]

        posts = []
        for i in range(count):
            posts.append(
                {
                    "id": f"trending_{i + 1}",
                    "title": titles[i % len(titles)],
                    "views": random.randint(5000, 50000),
                    "reactions": random.randint(200, 2000),
                    "shares": random.randint(50, 500),
                    "engagement_rate": round(random.uniform(5.0, 12.0), 2),
                    "published_at": (
                        self.base_date - timedelta(days=random.randint(1, 7))
                    ).isoformat(),
                }
            )

        return sorted(posts, key=lambda x: x["views"], reverse=True)

    def _generate_recent_posts(self, count: int) -> list[dict[str, Any]]:
        """Generate recent posts data"""
        posts = []
        for i in range(count):
            posts.append(
                {
                    "id": f"recent_{i + 1}",
                    "title": f"Recent Post {i + 1}",
                    "views": random.randint(100, 5000),
                    "reactions": random.randint(10, 200),
                    "published_at": (
                        self.base_date - timedelta(hours=random.randint(1, 48))
                    ).isoformat(),
                }
            )

        return posts

    def _generate_best_times(self) -> dict[str, Any]:
        """Generate best posting times"""
        return {
            "optimal_times": [
                {"day": "Monday", "time": "18:00", "engagement": 8.5},
                {"day": "Tuesday", "time": "19:30", "engagement": 9.2},
                {"day": "Wednesday", "time": "17:45", "engagement": 8.8},
                {"day": "Thursday", "time": "18:15", "engagement": 9.0},
                {"day": "Friday", "time": "16:30", "engagement": 7.8},
            ],
            "peak_engagement": {"time": "19:30", "day": "Tuesday", "score": 9.2},
        }

    def _generate_ai_recommendations(self) -> list[dict[str, Any]]:
        """Generate AI-powered recommendations"""
        return [
            {
                "type": "timing",
                "title": "Optimize posting schedule",
                "description": "Post during peak hours (6-9 PM) for 45% better engagement",
                "impact": "high",
                "confidence": 92,
            },
            {
                "type": "content",
                "title": "Add more visual content",
                "description": "Posts with images get 67% more engagement",
                "impact": "medium",
                "confidence": 85,
            },
            {
                "type": "hashtags",
                "title": "Optimize hashtag usage",
                "description": "Use 3-5 targeted hashtags for better discoverability",
                "impact": "medium",
                "confidence": 78,
            },
        ]


# Global demo data service instance
demo_data_service = DemoDataService()
