"""
Unit Tests for Domain Models
Tests core domain models and business logic without external dependencies
"""

import pytest
from pydantic import ValidationError
from src.domain.constants import (
    DEFAULT_FREE_CHANNELS,
    DEFAULT_PREMIUM_CHANNELS,
    AnalyticsEventType,
    PlanType,
    ServiceStatus,
)

# Domain model imports
from src.domain.models import (
    AnalyticsMetrics,
    InlineButton,
    InlineButtonsPayload,
    ServiceHealth,
    SubscriptionStatus,
)


class TestSubscriptionStatus:
    """Test SubscriptionStatus domain model"""

    def test_subscription_status_creation(self):
        """Test creating a SubscriptionStatus instance"""
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

    def test_subscription_status_free_plan(self):
        """Test creating a free plan subscription status"""
        status = SubscriptionStatus(
            plan_name=PlanType.FREE,
            max_channels=DEFAULT_FREE_CHANNELS,
            current_channels=1,
            max_posts_per_month=30,
            current_posts_this_month=15,
        )

        assert status.plan_name == PlanType.FREE
        assert status.max_channels == DEFAULT_FREE_CHANNELS


class TestInlineButton:
    """Test InlineButton domain model"""

    def test_inline_button_with_url(self):
        """Test creating an InlineButton with URL"""
        button = InlineButton(text="Visit Website", url="https://example.com")

        assert button.text == "Visit Website"
        assert str(button.url) == "https://example.com/"
        assert button.callback_data is None

    def test_inline_button_with_callback_data(self):
        """Test creating an InlineButton with callback data"""
        button = InlineButton(text="Click Me", callback_data="action_click")

        assert button.text == "Click Me"
        assert button.callback_data == "action_click"
        assert button.url is None

    def test_inline_button_callback_data_validation(self):
        """Test callback_data length validation"""
        # Valid callback data (<=60 chars)
        valid_callback = "a" * 60
        button = InlineButton(text="Valid", callback_data=valid_callback)
        assert button.callback_data == valid_callback

        # Invalid callback data (>60 chars)
        with pytest.raises(ValidationError):
            InlineButton(text="Invalid", callback_data="a" * 61)


class TestInlineButtonsPayload:
    """Test InlineButtonsPayload domain model"""

    def test_inline_buttons_payload_creation(self):
        """Test creating an InlineButtonsPayload"""
        buttons = [
            [InlineButton(text="Button 1", callback_data="btn1")],
            [InlineButton(text="Button 2", url="https://example.com")],
        ]

        payload = InlineButtonsPayload(buttons=buttons)
        assert len(payload.buttons) == 2
        assert payload.buttons[0][0].text == "Button 1"
        assert payload.buttons[1][0].text == "Button 2"

    def test_inline_buttons_payload_validation(self):
        """Test InlineButtonsPayload validation"""
        # Valid payload
        buttons = [[InlineButton(text="Test", callback_data="test")]]
        payload = InlineButtonsPayload(buttons=buttons)
        assert len(payload.buttons) == 1

        # Invalid empty buttons
        with pytest.raises(ValidationError):
            InlineButtonsPayload(buttons=[])


class TestAnalyticsMetrics:
    """Test AnalyticsMetrics domain model"""

    def test_analytics_metrics_creation(self):
        """Test creating an AnalyticsMetrics instance"""
        metrics = AnalyticsMetrics(
            total_posts=150,
            total_views=25000,
            engagement_rate=0.15,
            timestamp="2024-01-15T10:30:00Z",
        )

        assert metrics.total_posts == 150
        assert metrics.total_views == 25000
        assert metrics.engagement_rate == 0.15
        assert metrics.timestamp == "2024-01-15T10:30:00Z"

    def test_analytics_metrics_zero_values(self):
        """Test analytics metrics with zero values"""
        metrics = AnalyticsMetrics(
            total_posts=0,
            total_views=0,
            engagement_rate=0.0,
            timestamp="2024-01-15T10:30:00Z",
        )

        assert metrics.total_posts == 0
        assert metrics.total_views == 0
        assert metrics.engagement_rate == 0.0


class TestServiceHealth:
    """Test ServiceHealth domain model"""

    def test_service_health_healthy(self):
        """Test creating a healthy ServiceHealth instance"""
        health = ServiceHealth(
            service_name="telegram_bot",
            is_healthy=True,
            last_check="2024-01-15T10:30:00Z",
        )

        assert health.service_name == "telegram_bot"
        assert health.is_healthy is True
        assert health.last_check == "2024-01-15T10:30:00Z"
        assert health.error_message is None

    def test_service_health_unhealthy(self):
        """Test creating an unhealthy ServiceHealth instance"""
        health = ServiceHealth(
            service_name="database",
            is_healthy=False,
            last_check="2024-01-15T10:30:00Z",
            error_message="Connection timeout",
        )

        assert health.service_name == "database"
        assert health.is_healthy is False
        assert health.error_message == "Connection timeout"


class TestDomainConstants:
    """Test domain constants"""

    def test_plan_type_constants(self):
        """Test plan type constants are properly defined"""
        assert PlanType.FREE == "free"
        assert PlanType.PREMIUM == "premium"
        assert PlanType.ENTERPRISE == "enterprise"

    def test_service_status_constants(self):
        """Test service status constants are properly defined"""
        assert ServiceStatus.HEALTHY == "healthy"
        assert ServiceStatus.DEGRADED == "degraded"
        assert ServiceStatus.UNHEALTHY == "unhealthy"
        assert ServiceStatus.UNKNOWN == "unknown"

    def test_analytics_event_type_constants(self):
        """Test analytics event type constants are properly defined"""
        assert AnalyticsEventType.POST_PUBLISHED == "post_published"
        assert AnalyticsEventType.POST_VIEWED == "post_viewed"
        assert AnalyticsEventType.USER_SUBSCRIBED == "user_subscribed"

    def test_default_limits(self):
        """Test default limits constants"""
        assert DEFAULT_FREE_CHANNELS == 1
        assert DEFAULT_PREMIUM_CHANNELS == 10


# Test business logic functions
class TestDomainLogic:
    """Test domain logic and validation"""

    def test_subscription_status_usage_calculation(self):
        """Test subscription usage calculations"""
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

    def test_subscription_status_limits_exceeded(self):
        """Test checking if subscription limits are exceeded"""
        status = SubscriptionStatus(
            plan_name=PlanType.FREE,
            max_channels=1,
            current_channels=2,  # Exceeded
            max_posts_per_month=30,
            current_posts_this_month=35,  # Exceeded
        )

        channels_exceeded = status.current_channels > status.max_channels
        posts_exceeded = status.current_posts_this_month > status.max_posts_per_month

        assert channels_exceeded is True
        assert posts_exceeded is True

    def test_analytics_metrics_engagement_calculation(self):
        """Test engagement rate calculation"""
        metrics = AnalyticsMetrics(
            total_posts=100,
            total_views=5000,
            engagement_rate=0.08,  # 8%
            timestamp="2024-01-15T10:30:00Z",
        )

        # Calculate views per post
        views_per_post = metrics.total_views / metrics.total_posts if metrics.total_posts > 0 else 0

        assert views_per_post == 50.0
        assert metrics.engagement_rate == 0.08

    def test_service_health_status_mapping(self):
        """Test mapping service health to status enum"""
        healthy_service = ServiceHealth(
            service_name="api", is_healthy=True, last_check="2024-01-15T10:30:00Z"
        )

        unhealthy_service = ServiceHealth(
            service_name="database",
            is_healthy=False,
            last_check="2024-01-15T10:30:00Z",
            error_message="Connection failed",
        )

        # Map boolean to status enum
        healthy_status = (
            ServiceStatus.HEALTHY if healthy_service.is_healthy else ServiceStatus.UNHEALTHY
        )
        unhealthy_status = (
            ServiceStatus.HEALTHY if unhealthy_service.is_healthy else ServiceStatus.UNHEALTHY
        )

        assert healthy_status == ServiceStatus.HEALTHY
        assert unhealthy_status == ServiceStatus.UNHEALTHY
