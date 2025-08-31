"""
Isolated Unit Tests - No Fixtures
Tests core functionality without any pytest fixtures
"""

def test_simple_domain_constants():
    """Test domain constants without any fixtures"""
    # Direct import and test
    from apps.bot.domain.constants import PlanType, ServiceStatus
    
    assert PlanType.FREE == "free"
    assert PlanType.PREMIUM == "premium"
    assert ServiceStatus.HEALTHY == "healthy"
    print("✅ Domain constants test passed!")


def test_simple_subscription_status():
    """Test SubscriptionStatus without any fixtures"""
    from apps.bot.domain.constants import PlanType
    from apps.bot.domain.models import SubscriptionStatus
    
    status = SubscriptionStatus(
        plan_name=PlanType.PREMIUM,
        max_channels=10,
        current_channels=3,
        max_posts_per_month=500,
        current_posts_this_month=45
    )
    
    assert status.plan_name == PlanType.PREMIUM
    assert status.max_channels == 10
    assert status.current_channels == 3
    print("✅ SubscriptionStatus test passed!")


def test_simple_inline_button():
    """Test InlineButton without any fixtures"""
    from apps.bot.domain.models import InlineButton
    
    button = InlineButton(
        text="Test Button",
        url="https://example.com"
    )
    
    assert button.text == "Test Button"
    assert str(button.url) == "https://example.com/"  # HttpUrl adds trailing slash
    print("✅ InlineButton test passed!")


if __name__ == "__main__":
    # Run tests directly
    test_simple_domain_constants()
    test_simple_subscription_status()
    test_simple_inline_button()
    print("🎉 All isolated tests passed!")
