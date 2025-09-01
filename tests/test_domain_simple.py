"""
Simple Unit Tests for Domain Models - No External Dependencies
Tests core domain models without any database or external service dependencies
"""

import pytest
from pydantic import ValidationError

from apps.bot.domain.constants import (
    DEFAULT_FREE_CHANNELS,
    DEFAULT_PREMIUM_CHANNELS,
    PlanType,
    ServiceStatus,
)

# Domain model imports
from apps.bot.domain.models import (
    AnalyticsMetrics,
    InlineButton,
    ServiceHealth,
    SubscriptionStatus,
)


class TestSubscriptionStatusSimple:
    """Test SubscriptionStatus domain model - Simple"""

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


class TestInlineButtonSimple:
    """Test InlineButton domain model - Simple"""

    def test_inline_button_with_url(self):
        """Test creating an InlineButton with URL"""
        button = InlineButton(text="Visit Website", url="https://example.com")

        assert button.text == "Visit Website"
        assert str(button.url) == "https://example.com"
        assert button.callback_data is None

    def test_inline_button_callback_data_validation(self):
        """Test callback_data length validation"""
        # Valid callback data (<=60 chars)
        valid_callback = "a" * 60
        button = InlineButton(text="Valid", callback_data=valid_callback)
        assert button.callback_data == valid_callback

        # Invalid callback data (>60 chars) should raise ValidationError
        with pytest.raises(ValidationError):
            InlineButton(text="Invalid", callback_data="a" * 61)


class TestAnalyticsMetricsSimple:
    """Test AnalyticsMetrics domain model - Simple"""

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


class TestServiceHealthSimple:
    """Test ServiceHealth domain model - Simple"""

    def test_service_health_healthy(self):
        """Test creating a healthy ServiceHealth instance"""
        health = ServiceHealth(
            service_name="telegram_bot", is_healthy=True, last_check="2024-01-15T10:30:00Z"
        )

        assert health.service_name == "telegram_bot"
        assert health.is_healthy is True
        assert health.last_check == "2024-01-15T10:30:00Z"
        assert health.error_message is None


class TestDomainConstantsSimple:
    """Test domain constants - Simple"""

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

    def test_default_limits(self):
        """Test default limits constants"""
        assert DEFAULT_FREE_CHANNELS == 1
        assert DEFAULT_PREMIUM_CHANNELS == 10
