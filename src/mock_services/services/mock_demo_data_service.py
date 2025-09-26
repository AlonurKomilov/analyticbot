"""
Mock Demo Data Service for centralized mock services
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random

from .base_service import BaseMockService


class MockDemoDataService(BaseMockService):
    """Mock Demo Data Service for testing and development"""
    
    def get_service_name(self) -> str:
        return "MockDemoDataService"
    
    def generate_demo_users(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate mock demo users"""
        users = []
        for i in range(count):
            users.append({
                "id": i + 1,
                "username": f"demo_user_{i+1}",
                "email": f"demo{i+1}@example.com",
                "full_name": f"Demo User {i+1}",
                "avatar": f"https://api.dicebear.com/6.x/personas/svg?seed=demo{i+1}",
                "joined_date": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                "is_active": random.choice([True, True, True, False]),  # 75% active
                "role": random.choice(["user", "user", "user", "moderator"]),  # Mostly users
                "channels_count": random.randint(0, 5),
                "total_posts": random.randint(0, 100)
            })
        return users
    
    def generate_demo_channels(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock demo channels"""
        channel_names = [
            "Tech News", "Gaming Central", "Food Lovers", "Travel Diaries", 
            "Fitness Tips", "Book Club", "Movie Reviews", "Photography",
            "Music Discovery", "Business Insights"
        ]
        
        channels = []
        for i in range(min(count, len(channel_names))):
            channels.append({
                "id": i + 1,
                "name": channel_names[i],
                "description": f"Demo channel for {channel_names[i].lower()}",
                "subscriber_count": random.randint(100, 10000),
                "post_count": random.randint(10, 500),
                "created_date": (datetime.now() - timedelta(days=random.randint(30, 730))).isoformat(),
                "category": random.choice(["Entertainment", "Education", "News", "Lifestyle"]),
                "is_public": random.choice([True, True, False]),  # Mostly public
                "engagement_rate": round(random.uniform(0.01, 0.15), 4),
                "avg_views_per_post": random.randint(50, 1000)
            })
        return channels
    
    def generate_demo_posts(self, channel_id: int, count: int = 20) -> List[Dict[str, Any]]:
        """Generate mock demo posts for a channel"""
        post_types = ["text", "image", "video", "link"]
        posts = []
        
        for i in range(count):
            post_date = datetime.now() - timedelta(days=random.randint(0, 90))
            posts.append({
                "id": i + 1,
                "channel_id": channel_id,
                "title": f"Demo Post {i+1}",
                "content": f"This is demo content for post {i+1}. It contains mock data for testing purposes.",
                "type": random.choice(post_types),
                "author": f"demo_user_{random.randint(1, 10)}",
                "created_date": post_date.isoformat(),
                "views": random.randint(10, 5000),
                "likes": random.randint(0, 500),
                "comments": random.randint(0, 50),
                "shares": random.randint(0, 100),
                "engagement_score": round(random.uniform(0.1, 10.0), 2),
                "tags": random.sample(["demo", "test", "sample", "mock", "data"], random.randint(1, 3))
            })
        
        return sorted(posts, key=lambda x: x["created_date"], reverse=True)
    
    def generate_demo_analytics(self, channel_id: int, days: int = 30) -> Dict[str, Any]:
        """Generate mock analytics data"""
        daily_data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            daily_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "views": random.randint(100, 2000),
                "likes": random.randint(10, 200),
                "comments": random.randint(5, 50),
                "shares": random.randint(2, 30),
                "new_subscribers": random.randint(0, 20),
                "engagement_rate": round(random.uniform(0.02, 0.12), 4)
            })
        
        return {
            "channel_id": channel_id,
            "period": f"{days} days",
            "daily_stats": daily_data,
            "summary": {
                "total_views": sum(d["views"] for d in daily_data),
                "total_likes": sum(d["likes"] for d in daily_data),
                "total_comments": sum(d["comments"] for d in daily_data),
                "total_shares": sum(d["shares"] for d in daily_data),
                "avg_engagement_rate": round(sum(d["engagement_rate"] for d in daily_data) / len(daily_data), 4),
                "growth_rate": round(random.uniform(-0.1, 0.25), 4)
            }
        }
    
    def get_demo_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive demo dashboard data"""
        return {
            "overview": {
                "total_users": random.randint(1000, 5000),
                "total_channels": random.randint(50, 200),
                "total_posts": random.randint(10000, 50000),
                "total_engagement": random.randint(100000, 500000)
            },
            "recent_activity": [
                {"action": "New user registered", "timestamp": datetime.now().isoformat()},
                {"action": "Channel created", "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat()},
                {"action": "Post published", "timestamp": (datetime.now() - timedelta(hours=1)).isoformat()}
            ],
            "top_channels": self.generate_demo_channels(5),
            "trending_posts": [
                {"title": "Trending Post 1", "views": 5000, "engagement": 450},
                {"title": "Trending Post 2", "views": 4200, "engagement": 380},
                {"title": "Trending Post 3", "views": 3800, "engagement": 320}
            ]
        }