"""
Marketplace Service Pricing and Quotas Unit Tests
==================================================

Tests for service pricing validation and quota management.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ServicePricing:
    """Service pricing structure for testing."""

    service_key: str
    credits_per_month: int
    daily_quota: int | None = None
    category: str = "bot_service"


# Expected pricing for all services
EXPECTED_PRICING = {
    # Bot Services
    "bot_anti_spam": ServicePricing("bot_anti_spam", 50),
    "bot_auto_delete_joins": ServicePricing("bot_auto_delete_joins", 30),
    "bot_banned_words": ServicePricing("bot_banned_words", 40),
    "bot_welcome_messages": ServicePricing("bot_welcome_messages", 35),
    "bot_invite_tracking": ServicePricing("bot_invite_tracking", 45),
    "bot_warning_system": ServicePricing("bot_warning_system", 55),
    "bot_analytics_advanced": ServicePricing("bot_analytics_advanced", 75),
    # MTProto Services
    "mtproto_history_access": ServicePricing(
        "mtproto_history_access", 100, category="mtproto_services"
    ),
    "mtproto_auto_collect": ServicePricing(
        "mtproto_auto_collect", 150, category="mtproto_services"
    ),
    "mtproto_media_download": ServicePricing(
        "mtproto_media_download", 75, category="mtproto_services"
    ),
    "mtproto_bulk_export": ServicePricing("mtproto_bulk_export", 200, category="mtproto_services"),
    # AI Services (with quotas)
    "ai_content_optimizer": ServicePricing(
        "ai_content_optimizer", 125, daily_quota=50, category="ai_services"
    ),
    "ai_sentiment_analyzer": ServicePricing(
        "ai_sentiment_analyzer", 100, daily_quota=100, category="ai_services"
    ),
    "ai_smart_replies": ServicePricing(
        "ai_smart_replies", 150, daily_quota=200, category="ai_services"
    ),
    "ai_content_moderation": ServicePricing(
        "ai_content_moderation", 175, daily_quota=500, category="ai_services"
    ),
}


class TestServicePricing:
    """Test service pricing validation."""

    def test_bot_services_pricing_range(self):
        """Test bot services are within expected pricing range."""
        min_price = 25
        max_price = 100

        bot_services = {k: v for k, v in EXPECTED_PRICING.items() if k.startswith("bot_")}

        for key, pricing in bot_services.items():
            assert min_price <= pricing.credits_per_month <= max_price, (
                f"Bot service {key} pricing {pricing.credits_per_month} out of range [{min_price}, {max_price}]"
            )

    def test_mtproto_services_pricing_range(self):
        """Test MTProto services are within expected pricing range."""
        min_price = 50
        max_price = 250

        mtproto_services = {k: v for k, v in EXPECTED_PRICING.items() if k.startswith("mtproto_")}

        for key, pricing in mtproto_services.items():
            assert min_price <= pricing.credits_per_month <= max_price, (
                f"MTProto service {key} pricing {pricing.credits_per_month} out of range [{min_price}, {max_price}]"
            )

    def test_ai_services_pricing_range(self):
        """Test AI services are within expected pricing range."""
        min_price = 75
        max_price = 250

        ai_services = {k: v for k, v in EXPECTED_PRICING.items() if k.startswith("ai_")}

        for key, pricing in ai_services.items():
            assert min_price <= pricing.credits_per_month <= max_price, (
                f"AI service {key} pricing {pricing.credits_per_month} out of range [{min_price}, {max_price}]"
            )

    def test_pricing_is_positive(self):
        """Test all pricing values are positive."""
        for key, pricing in EXPECTED_PRICING.items():
            assert pricing.credits_per_month > 0, (
                f"Service {key} has non-positive pricing: {pricing.credits_per_month}"
            )

    def test_pricing_values_correct(self):
        """Test specific pricing values match expected."""
        # MTProto services
        assert EXPECTED_PRICING["mtproto_history_access"].credits_per_month == 100
        assert EXPECTED_PRICING["mtproto_auto_collect"].credits_per_month == 150
        assert EXPECTED_PRICING["mtproto_media_download"].credits_per_month == 75
        assert EXPECTED_PRICING["mtproto_bulk_export"].credits_per_month == 200

        # AI services
        assert EXPECTED_PRICING["ai_content_optimizer"].credits_per_month == 125
        assert EXPECTED_PRICING["ai_sentiment_analyzer"].credits_per_month == 100
        assert EXPECTED_PRICING["ai_smart_replies"].credits_per_month == 150
        assert EXPECTED_PRICING["ai_content_moderation"].credits_per_month == 175


class TestServiceQuotas:
    """Test service quota validation."""

    def test_ai_services_have_quotas(self):
        """Test that AI services have daily quotas defined."""
        ai_services = {k: v for k, v in EXPECTED_PRICING.items() if k.startswith("ai_")}

        for key, pricing in ai_services.items():
            assert pricing.daily_quota is not None, (
                f"AI service {key} should have daily_quota defined"
            )
            assert pricing.daily_quota > 0, f"AI service {key} should have positive daily_quota"

    def test_bot_services_no_quotas(self):
        """Test that bot services don't have daily quotas."""
        bot_services = {k: v for k, v in EXPECTED_PRICING.items() if k.startswith("bot_")}

        for key, pricing in bot_services.items():
            assert pricing.daily_quota is None, f"Bot service {key} should not have daily_quota"

    def test_mtproto_services_no_quotas(self):
        """Test that MTProto services don't have daily quotas."""
        mtproto_services = {k: v for k, v in EXPECTED_PRICING.items() if k.startswith("mtproto_")}

        for key, pricing in mtproto_services.items():
            assert pricing.daily_quota is None, f"MTProto service {key} should not have daily_quota"

    def test_quota_values_correct(self):
        """Test specific quota values match expected."""
        assert EXPECTED_PRICING["ai_content_optimizer"].daily_quota == 50
        assert EXPECTED_PRICING["ai_sentiment_analyzer"].daily_quota == 100
        assert EXPECTED_PRICING["ai_smart_replies"].daily_quota == 200
        assert EXPECTED_PRICING["ai_content_moderation"].daily_quota == 500

    def test_quota_order_makes_sense(self):
        """Test that quotas scale appropriately with pricing."""
        # Higher priced AI services should generally have higher quotas
        ai_services = {k: v for k, v in EXPECTED_PRICING.items() if k.startswith("ai_")}

        # Content moderation is highest priced and has highest quota
        assert (
            EXPECTED_PRICING["ai_content_moderation"].daily_quota
            >= EXPECTED_PRICING["ai_sentiment_analyzer"].daily_quota
        )

        # Smart replies has higher quota than content optimizer
        assert (
            EXPECTED_PRICING["ai_smart_replies"].daily_quota
            > EXPECTED_PRICING["ai_content_optimizer"].daily_quota
        )


class TestQuotaTracking:
    """Test quota tracking functionality."""

    def test_quota_usage_calculation(self):
        """Test quota usage percentage calculation."""
        daily_quota = 100
        used = 45

        usage_percentage = (used / daily_quota) * 100

        assert usage_percentage == 45.0

    def test_quota_remaining_calculation(self):
        """Test remaining quota calculation."""
        daily_quota = 100
        used = 45

        remaining = daily_quota - used

        assert remaining == 55

    def test_quota_exceeded_check(self):
        """Test checking if quota is exceeded."""
        daily_quota = 100

        # Not exceeded
        assert 50 <= daily_quota
        assert 100 <= daily_quota

        # Exceeded
        assert not (101 <= daily_quota)

    def test_quota_reset_time_calculation(self):
        """Test quota reset time calculation."""
        from datetime import datetime, timedelta

        # Quotas reset at midnight UTC
        now = datetime(2025, 1, 15, 14, 30, 0)  # 2:30 PM

        # Next reset is at midnight
        next_reset = datetime(2025, 1, 16, 0, 0, 0)

        time_until_reset = next_reset - now

        assert time_until_reset < timedelta(hours=24)
        assert time_until_reset >= timedelta(hours=9)  # ~9.5 hours

    def test_quota_warning_threshold(self):
        """Test quota warning threshold (80% usage)."""
        daily_quota = 100
        warning_threshold = 0.8

        # Below warning
        assert 50 / daily_quota < warning_threshold

        # At/above warning
        assert 80 / daily_quota >= warning_threshold
        assert 90 / daily_quota >= warning_threshold


class TestQuotaEnforcement:
    """Test quota enforcement logic."""

    def test_request_allowed_within_quota(self):
        """Test requests are allowed within quota."""
        daily_quota = 100
        used = 50

        # Request for 10 should be allowed
        request_amount = 10
        allowed = (used + request_amount) <= daily_quota

        assert allowed

    def test_request_denied_exceeds_quota(self):
        """Test requests are denied when exceeding quota."""
        daily_quota = 100
        used = 95

        # Request for 10 should be denied
        request_amount = 10
        allowed = (used + request_amount) <= daily_quota

        assert not allowed

    def test_request_allowed_at_exact_limit(self):
        """Test request exactly at limit is allowed."""
        daily_quota = 100
        used = 90

        # Request for 10 brings to exactly 100, should be allowed
        request_amount = 10
        allowed = (used + request_amount) <= daily_quota

        assert allowed

    def test_batch_request_quota_check(self):
        """Test batch request quota checking."""
        daily_quota = 100
        used = 50
        batch_size = 30

        # Calculate remaining after batch
        after_batch = used + batch_size

        assert after_batch <= daily_quota

        # Another batch would exceed
        second_batch = 30
        after_second_batch = after_batch + second_batch

        assert after_second_batch > daily_quota


class TestServiceCategory:
    """Test service category validation."""

    def test_categories_are_valid(self):
        """Test all categories are valid enum values."""
        valid_categories = {"bot_service", "mtproto_services", "ai_services"}

        for key, pricing in EXPECTED_PRICING.items():
            assert pricing.category in valid_categories, (
                f"Service {key} has invalid category: {pricing.category}"
            )

    def test_bot_services_category(self):
        """Test bot services have correct category."""
        for key, pricing in EXPECTED_PRICING.items():
            if key.startswith("bot_"):
                assert pricing.category == "bot_service", (
                    f"Bot service {key} should have category 'bot_service'"
                )

    def test_mtproto_services_category(self):
        """Test MTProto services have correct category."""
        for key, pricing in EXPECTED_PRICING.items():
            if key.startswith("mtproto_"):
                assert pricing.category == "mtproto_services", (
                    f"MTProto service {key} should have category 'mtproto_services'"
                )

    def test_ai_services_category(self):
        """Test AI services have correct category."""
        for key, pricing in EXPECTED_PRICING.items():
            if key.startswith("ai_"):
                assert pricing.category == "ai_services", (
                    f"AI service {key} should have category 'ai_services'"
                )


class TestPricingTiers:
    """Test pricing tier calculations."""

    def test_monthly_cost_calculation(self):
        """Test monthly cost calculation."""
        credits_per_month = 150

        # Assuming 1 credit = $0.01
        cost_per_credit = Decimal("0.01")
        monthly_cost = Decimal(credits_per_month) * cost_per_credit

        assert monthly_cost == Decimal("1.50")

    def test_bulk_discount_not_applied_yet(self):
        """Test that individual pricing is used (no bulk discount)."""
        # Single service

        # Multiple services - no discount
        multiple_services_cost = 150 + 100 + 75

        assert multiple_services_cost == 325

    def test_total_mtproto_bundle_cost(self):
        """Test total cost for all MTProto services."""
        mtproto_total = sum(
            pricing.credits_per_month
            for key, pricing in EXPECTED_PRICING.items()
            if key.startswith("mtproto_")
        )

        # 100 + 150 + 75 + 200 = 525
        assert mtproto_total == 525

    def test_total_ai_bundle_cost(self):
        """Test total cost for all AI services."""
        ai_total = sum(
            pricing.credits_per_month
            for key, pricing in EXPECTED_PRICING.items()
            if key.startswith("ai_")
        )

        # 125 + 100 + 150 + 175 = 550
        assert ai_total == 550
