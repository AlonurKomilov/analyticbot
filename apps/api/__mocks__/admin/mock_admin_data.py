"""
Admin Mock Data Module
Extracted from analytics_router.py to maintain clean separation of mock data
"""

import random
from datetime import datetime


def create_mock_user_channels(user_id: int, count: int = 3) -> list[dict]:
    """Create mock user channels for admin view"""
    return [
        {
            "id": i,
            "name": f"User {user_id} Channel {i}",
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "total_subscribers": random.randint(50, 5000),
        }
        for i in range(1, count + 1)
    ]


def simulate_channel_deletion(channel_id: int) -> dict:
    """Simulate channel deletion for admin operations"""
    return {"message": f"Channel {channel_id} deleted successfully", "success": True}


def create_mock_admin_stats() -> dict:
    """Create mock admin statistics"""
    return {
        "total_users": random.randint(1000, 5000),
        "active_channels": random.randint(2000, 8000),
        "total_posts_today": random.randint(500, 2000),
        "system_health": "operational",
    }
