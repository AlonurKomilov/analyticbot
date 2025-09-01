"""
Basic Domain Model Tests - Working Implementation
Tests core domain models with working pytest setup
"""

# Test imports
from apps.bot.domain.constants import DEFAULT_FREE_CHANNELS, PlanType, ServiceStatus
from apps.bot.domain.models import (
    AnalyticsMetrics,
    InlineButton,
    ServiceHealth,
    SubscriptionStatus,
)


def test_subscription_status_basic():
    """Test basic SubscriptionStatus functionality"""
    status = SubscriptionStatus(
        plan_name=PlanType.PREMIUM,
        max_channels=10,
        current_channels=3,
        max_posts_per_month=500,
        current_posts_this_month=45,
    )

    assert status.plan_name == PlanType.PREMIUM
    assert status.max_channels == 10
    assert status.current_channels == 3
    assert status.max_posts_per_month == 500
    assert status.current_posts_this_month == 45


def test_subscription_status_free_plan():
    """Test free plan subscription status"""
    status = SubscriptionStatus(
        plan_name=PlanType.FREE,
        max_channels=DEFAULT_FREE_CHANNELS,
        current_channels=1,
        max_posts_per_month=30,
        current_posts_this_month=15,
    )

    assert status.plan_name == PlanType.FREE
    assert status.max_channels == DEFAULT_FREE_CHANNELS


def test_inline_button_with_url():
    """Test InlineButton with URL"""
    button = InlineButton(text="Visit Website", url="https://example.com")

    assert button.text == "Visit Website"
    assert "example.com" in str(button.url)
    assert button.callback_data is None


def test_inline_button_with_callback():
    """Test InlineButton with callback data"""
    button = InlineButton(text="Click Me", callback_data="action_click")

    assert button.text == "Click Me"
    assert button.callback_data == "action_click"
    assert button.url is None


def test_analytics_metrics_basic():
    """Test basic AnalyticsMetrics functionality"""
    metrics = AnalyticsMetrics(
        total_posts=150, total_views=25000, engagement_rate=0.15, timestamp="2024-01-15T10:30:00Z"
    )

    assert metrics.total_posts == 150
    assert metrics.total_views == 25000
    assert metrics.engagement_rate == 0.15
    assert metrics.timestamp == "2024-01-15T10:30:00Z"


def test_service_health_healthy():
    """Test healthy ServiceHealth"""
    health = ServiceHealth(
        service_name="telegram_bot", is_healthy=True, last_check="2024-01-15T10:30:00Z"
    )

    assert health.service_name == "telegram_bot"
    assert health.is_healthy is True
    assert health.last_check == "2024-01-15T10:30:00Z"
    assert health.error_message is None


def test_service_health_unhealthy():
    """Test unhealthy ServiceHealth"""
    health = ServiceHealth(
        service_name="database",
        is_healthy=False,
        last_check="2024-01-15T10:30:00Z",
        error_message="Connection timeout",
    )

    assert health.service_name == "database"
    assert health.is_healthy is False
    assert health.error_message == "Connection timeout"


def test_plan_type_constants():
    """Test PlanType constants"""
    assert PlanType.FREE == "free"
    assert PlanType.PREMIUM == "premium"
    assert PlanType.ENTERPRISE == "enterprise"


def test_service_status_constants():
    """Test ServiceStatus constants"""
    assert ServiceStatus.HEALTHY == "healthy"
    assert ServiceStatus.DEGRADED == "degraded"
    assert ServiceStatus.UNHEALTHY == "unhealthy"
    assert ServiceStatus.UNKNOWN == "unknown"


def test_business_logic_usage_calculation():
    """Test subscription usage calculation logic"""
    status = SubscriptionStatus(
        plan_name=PlanType.PREMIUM,
        max_channels=10,
        current_channels=7,
        max_posts_per_month=500,
        current_posts_this_month=250,
    )

    # Calculate usage percentages
    channel_usage = (status.current_channels / status.max_channels) * 100
    posts_usage = (status.current_posts_this_month / status.max_posts_per_month) * 100

    assert channel_usage == 70.0
    assert posts_usage == 50.0


def test_analytics_engagement_calculation():
    """Test analytics engagement calculation"""
    metrics = AnalyticsMetrics(
        total_posts=100, total_views=5000, engagement_rate=0.08, timestamp="2024-01-15T10:30:00Z"
    )

    # Calculate views per post
    views_per_post = metrics.total_views / metrics.total_posts if metrics.total_posts > 0 else 0

    assert views_per_post == 50.0
    assert metrics.engagement_rate == 0.08
