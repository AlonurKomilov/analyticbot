"""
Initial Data Mock Module
Extracted from main.py to maintain clean separation of mock data
"""

from datetime import datetime

from apps.bot.models.twa import Channel, Plan, ScheduledPost, User


def create_mock_user(user_id: str = "demo_user_123") -> User:
    """Create mock user data"""
    return User(id=user_id, username="demo_user")


def create_mock_plan() -> Plan:
    """Create mock plan data"""
    return Plan(name="Pro", max_channels=10, max_posts_per_month=1000)


def create_mock_channels() -> list[Channel]:
    """Create mock channels data"""
    return [
        Channel(id=1, title="Tech News", username="@technews"),
        Channel(id=2, title="Daily Updates", username="@dailyupdates"),
        Channel(id=3, title="Business Insights", username="@bizinsights"),
    ]


def create_mock_scheduled_posts() -> list[ScheduledPost]:
    """Create mock scheduled posts data"""
    return [
        ScheduledPost(
            id=1,
            channel_id=1,
            scheduled_at=datetime.now(),
            text="Sample scheduled post 1",
        ),
        ScheduledPost(
            id=2,
            channel_id=2,
            scheduled_at=datetime.now(),
            text="Sample scheduled post 2",
        ),
    ]


def get_mock_initial_data(user_id: str = "demo_user_123") -> dict:
    """Get complete mock initial data structure"""
    return {
        "user": create_mock_user(user_id),
        "plan": create_mock_plan(),
        "channels": create_mock_channels(),
        "scheduled_posts": create_mock_scheduled_posts(),
    }
