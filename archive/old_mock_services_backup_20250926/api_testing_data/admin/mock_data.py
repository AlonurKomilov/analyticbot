"""
Admin Mock Data Module
Provides comprehensive admin functionality mock data for demo system
"""


def get_mock_admin_dashboard(demo_type: str = "admin") -> dict:
    """Generate mock admin dashboard data"""
    if demo_type != "admin":
        return {"error": "Access denied - admin privileges required"}

    return {
        "total_users": 15847,
        "active_users_today": 2456,
        "total_channels": 8934,
        "total_posts_today": 1247,
        "system_health": {
            "status": "healthy",
            "uptime": "99.97%",
            "response_time": "89ms",
            "error_rate": "0.02%",
        },
        "recent_activity": [
            {
                "timestamp": "2024-01-15T14:30:00Z",
                "event": "New user registration",
                "details": "user@example.com",
            },
            {
                "timestamp": "2024-01-15T14:25:00Z",
                "event": "Channel created",
                "details": "TechNews Channel by demo_user",
            },
            {
                "timestamp": "2024-01-15T14:20:00Z",
                "event": "High engagement post",
                "details": "Post #12847 reached 10k views",
            },
        ],
        "alerts": [
            {
                "level": "info",
                "message": "System backup completed successfully",
                "timestamp": "2024-01-15T14:00:00Z",
            }
        ],
    }


def get_mock_user_channels(user_id: int) -> list[dict]:
    """Generate mock user channels for admin view"""
    import random
    from datetime import datetime

    return [
        {
            "id": i,
            "name": f"User {user_id} Channel {i}",
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "total_subscribers": random.randint(50, 5000),
            "status": "active",
            "last_post_at": datetime.utcnow().isoformat(),
            "engagement_rate": round(random.uniform(2.5, 8.5), 2),
        }
        for i in range(1, 4)  # Mock 3 channels per user
    ]


def get_mock_admin_operations_log() -> list[dict]:
    """Generate mock admin operations log"""
    import random
    from datetime import datetime, timedelta

    operations = [
        "User account created",
        "Channel deleted",
        "Post moderated",
        "Payment processed",
        "Security alert resolved",
        "System maintenance completed",
    ]

    return [
        {
            "id": i,
            "timestamp": (datetime.utcnow() - timedelta(hours=random.randint(0, 72))).isoformat(),
            "operation": random.choice(operations),
            "admin_user": "demo_admin",
            "target": f"target_{random.randint(1000, 9999)}",
            "status": "success" if random.random() > 0.1 else "warning",
        }
        for i in range(1, 21)  # Last 20 operations
    ]


def get_mock_system_metrics() -> dict:
    """Generate mock system performance metrics"""
    import random

    return {
        "cpu_usage": round(random.uniform(15.0, 85.0), 1),
        "memory_usage": round(random.uniform(45.0, 75.0), 1),
        "disk_usage": round(random.uniform(25.0, 60.0), 1),
        "network_in": round(random.uniform(50.0, 200.0), 1),
        "network_out": round(random.uniform(30.0, 150.0), 1),
        "active_connections": random.randint(1200, 3500),
        "requests_per_minute": random.randint(800, 2400),
        "error_rate": round(random.uniform(0.01, 0.05), 3),
        "response_time": round(random.uniform(45.0, 120.0), 1),
        "database_connections": random.randint(25, 95),
    }
