"""
Mock Demo Data Service Implementation
Protocol-compliant demo data service for demo mode
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from core.protocols import DemoDataServiceProtocol
from apps.api.__mocks__.constants import DEMO_API_DELAY_MS


class MockDemoDataService(DemoDataServiceProtocol):
    """Mock demo data service for demo mode"""
    
    def get_service_name(self) -> str:
        return "mock_demo_data_service"
    
    async def health_check(self) -> Dict[str, Any]:
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        return {
            "service": "demo_data",
            "status": "healthy",
            "demo_mode": True,
            "datasets_available": ["channels", "users", "analytics", "posts"]
        }
    
    async def get_initial_data(self) -> Dict[str, Any]:
        """Get initial demo data"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        
        return {
            "users": [
                {
                    "id": 123,
                    "username": "demo_user",
                    "email": "demo@example.com",
                    "type": "premium",
                    "created_at": (datetime.now() - timedelta(days=30)).isoformat()
                },
                {
                    "id": 456,
                    "username": "free_user",
                    "email": "free@example.com", 
                    "type": "free",
                    "created_at": (datetime.now() - timedelta(days=15)).isoformat()
                }
            ],
            "channels": [
                {
                    "id": "demo_channel_1",
                    "name": "Tech Insights",
                    "username": "tech_insights_demo",
                    "members": 15420,
                    "category": "Technology",
                    "created_at": (datetime.now() - timedelta(days=90)).isoformat()
                },
                {
                    "id": "demo_channel_2", 
                    "name": "Business Today",
                    "username": "business_today_demo",
                    "members": 8340,
                    "category": "Business",
                    "created_at": (datetime.now() - timedelta(days=60)).isoformat()
                }
            ],
            "sample_posts": [
                {
                    "id": "post_1",
                    "channel_id": "demo_channel_1",
                    "content": "🚀 The future of AI is here! Exciting developments in machine learning.",
                    "views": 2450,
                    "likes": 180,
                    "comments": 25,
                    "shares": 12,
                    "created_at": (datetime.now() - timedelta(hours=6)).isoformat()
                },
                {
                    "id": "post_2",
                    "channel_id": "demo_channel_2",
                    "content": "📈 Market trends show significant growth in tech sector.",
                    "views": 1820,
                    "likes": 95,
                    "comments": 18,
                    "shares": 7,
                    "created_at": (datetime.now() - timedelta(hours=12)).isoformat()
                }
            ],
            "demo_mode": True,
            "generated_at": datetime.now().isoformat()
        }
    
    async def reset_demo_data(self) -> Dict[str, Any]:
        """Reset demo data to initial state"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        
        return {
            "status": "success",
            "message": "Demo data has been reset to initial state",
            "reset_components": [
                "user_preferences",
                "channel_analytics", 
                "post_metrics",
                "engagement_data"
            ],
            "reset_at": datetime.now().isoformat(),
            "demo_mode": True
        }
    
    async def seed_demo_channels(self, user_id: int) -> List[Dict[str, Any]]:
        """Seed demo channels for user"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        
        channel_templates = [
            {
                "name": "Tech News Hub",
                "category": "Technology",
                "description": "Latest technology news and trends",
                "members_range": (5000, 15000)
            },
            {
                "name": "Business Insights", 
                "category": "Business",
                "description": "Business strategy and market analysis",
                "members_range": (3000, 10000)
            },
            {
                "name": "Digital Marketing",
                "category": "Marketing", 
                "description": "Digital marketing tips and strategies",
                "members_range": (2000, 8000)
            },
            {
                "name": "Startup Stories",
                "category": "Entrepreneurship",
                "description": "Inspiring startup journeys and lessons",
                "members_range": (1000, 5000)
            }
        ]
        
        seeded_channels = []
        num_channels = random.randint(2, 4)
        
        for i in range(num_channels):
            template = random.choice(channel_templates)
            channel = {
                "id": f"demo_channel_{user_id}_{i+1}",
                "name": template["name"],
                "username": f"{template['name'].lower().replace(' ', '_')}_demo_{i+1}",
                "description": template["description"],
                "category": template["category"],
                "members": random.randint(*template["members_range"]),
                "owner_id": user_id,
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat(),
                "is_active": True,
                "demo_mode": True
            }
            seeded_channels.append(channel)
        
        return seeded_channels