"""
Mock Demo Data Service Implementation
Protocol-compliant demo data service for demo mode
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.shared_kernel.domain.protocols import DemoDataServiceProtocol
from src.mock_services.constants import DEMO_API_DELAY_MS


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
    
    async def get_initial_data(self, user_id: int = None, demo_type: str = None):
        """Get initial demo data for TWA initialization"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        
        # Import here to avoid circular import
        from src.bot_service.models.twa import InitialDataResponse
        
        # Generate demo user data
        demo_user = {
            "id": user_id or 1,
            "telegram_id": user_id or 12345,
            "username": f"demo_user_{demo_type or 'limited'}",
            "full_name": "Demo User",
            "email": f"demo_{demo_type or 'limited'}@example.com"
        }
        
        # Generate demo plan based on demo_type
        if demo_type == "premium":
            plan = {
                "name": "Premium",
                "channels_limit": 50,
                "posts_limit": 10000,
                "analytics_enabled": True
            }
        else:
            plan = {
                "name": "Free",
                "channels_limit": 5,
                "posts_limit": 100,
                "analytics_enabled": True
            }
        
        # Generate demo channels
        channels = await self.seed_demo_channels(user_id or 1)
        channels = [
            {
                "id": ch["id"],
                "name": ch["name"],
                "username": ch.get("username"),
                "subscriber_count": ch.get("members", 0),
                "is_active": ch.get("is_active", True)
            } for ch in channels
        ]
        
        # Generate demo features
        features = {
            "analytics_enabled": True,
            "export_enabled": True,
            "ai_insights_enabled": demo_type == "premium",
            "advanced_features_enabled": demo_type == "premium",
            "alerts_enabled": True,
            "share_links_enabled": True
        }
        
        return InitialDataResponse(
            user=demo_user,
            plan=plan,
            channels=channels,
            scheduled_posts=[],  # Empty for demo
            features=features
        )
    
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