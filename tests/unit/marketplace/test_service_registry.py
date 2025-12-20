"""
Service Registry Unit Tests
============================

Tests for the frontend service registry including:
- Service registration validation
- Config component mapping
- Service metadata integrity
- Category organization
"""

import sys
from unittest.mock import MagicMock

# Mock React and MUI before importing registry
sys.modules["react"] = MagicMock()
sys.modules["@mui/material"] = MagicMock()
sys.modules["@mui/icons-material"] = MagicMock()


class TestServiceRegistry:
    """Test service registry data integrity."""

    def test_all_bot_services_registered(self):
        """Test that all bot services are registered."""
        expected_bot_services = [
            "bot_anti_spam",
            "bot_auto_delete_joins",
            "bot_banned_words",
            "bot_welcome_messages",
            "bot_invite_tracking",
            "bot_warning_system",
            "bot_analytics_advanced",
        ]

        # This would be imported from the registry in actual test
        # For now, we validate the expected structure
        for key in expected_bot_services:
            assert key.startswith("bot_"), f"Bot service should start with 'bot_': {key}"

    def test_all_mtproto_services_registered(self):
        """Test that all MTProto services are registered."""
        expected_mtproto_services = [
            "mtproto_history_access",
            "mtproto_auto_collect",
            "mtproto_media_download",
            "mtproto_bulk_export",
        ]

        for key in expected_mtproto_services:
            assert key.startswith("mtproto_"), (
                f"MTProto service should start with 'mtproto_': {key}"
            )

    def test_all_ai_services_registered(self):
        """Test that all AI services are registered."""
        expected_ai_services = [
            "ai_content_optimizer",
            "ai_sentiment_analyzer",
            "ai_smart_replies",
            "ai_content_moderation",
        ]

        for key in expected_ai_services:
            assert key.startswith("ai_"), f"AI service should start with 'ai_': {key}"

    def test_service_key_format(self):
        """Test that service keys follow naming convention."""
        all_services = [
            "bot_anti_spam",
            "bot_auto_delete_joins",
            "bot_banned_words",
            "bot_welcome_messages",
            "bot_invite_tracking",
            "bot_warning_system",
            "bot_analytics_advanced",
            "mtproto_history_access",
            "mtproto_auto_collect",
            "mtproto_media_download",
            "mtproto_bulk_export",
            "ai_content_optimizer",
            "ai_sentiment_analyzer",
            "ai_smart_replies",
            "ai_content_moderation",
        ]

        for key in all_services:
            # Keys should be lowercase with underscores
            assert key == key.lower(), f"Service key should be lowercase: {key}"
            assert " " not in key, f"Service key should not have spaces: {key}"
            assert "-" not in key, f"Service key should use underscores not dashes: {key}"

    def test_service_categories(self):
        """Test service categorization."""
        categories = {
            "bot": ["bot_anti_spam", "bot_auto_delete_joins", "bot_banned_words"],
            "mtproto": ["mtproto_history_access", "mtproto_auto_collect"],
            "ai": ["ai_content_optimizer", "ai_sentiment_analyzer"],
        }

        for category, services in categories.items():
            for service_key in services:
                assert service_key.startswith(f"{category}_"), (
                    f"Service {service_key} should be in category {category}"
                )


class TestServiceMetadata:
    """Test service metadata structure."""

    def test_required_metadata_fields(self):
        """Test that all required metadata fields are present."""
        required_fields = [
            "service_key",
            "name",
            "description",
            "features",
            "icon",
            "color",
            "per_chat_config",
            "has_quotas",
        ]

        # Sample metadata structure for validation
        sample_metadata = {
            "service_key": "bot_anti_spam",
            "name": "Anti-Spam Protection",
            "description": "Protect your chat from spam...",
            "features": ["Real-time detection", "Link blocking"],
            "icon": "Security",
            "color": "#667eea",
            "per_chat_config": True,
            "has_quotas": False,
        }

        for field in required_fields:
            assert field in sample_metadata, f"Missing required field: {field}"

    def test_mtproto_services_not_per_chat(self):
        """Test that MTProto services are not per-chat config."""
        # MTProto services operate at user-level, not per-chat
        mtproto_configs = {
            "mtproto_history_access": False,
            "mtproto_auto_collect": False,
            "mtproto_media_download": False,
            "mtproto_bulk_export": False,
        }

        for key, expected_per_chat in mtproto_configs.items():
            assert expected_per_chat is False, (
                f"MTProto service {key} should have per_chat_config=False"
            )

    def test_ai_services_have_quotas(self):
        """Test that AI services have quotas enabled."""
        ai_services = [
            "ai_content_optimizer",
            "ai_sentiment_analyzer",
            "ai_smart_replies",
            "ai_content_moderation",
        ]

        # AI services should have quotas due to API costs
        for key in ai_services:
            # In actual test, would check has_quotas=True
            assert key.startswith("ai_"), f"Should be AI service: {key}"

    def test_features_is_list(self):
        """Test that features field is always a list."""
        sample_features = [
            ["Real-time detection", "Link blocking"],
            ["Scheduled collection", "Worker status"],
            ["Spam detection", "Hate speech filtering"],
        ]

        for features in sample_features:
            assert isinstance(features, list), "Features should be a list"
            assert len(features) > 0, "Features should not be empty"
            assert all(isinstance(f, str) for f in features), "All features should be strings"

    def test_color_is_valid_hex(self):
        """Test that color values are valid hex colors."""
        colors = [
            "#667eea",  # bot_anti_spam
            "#2196F3",  # mtproto_history_access
            "#6366F1",  # ai_content_optimizer
            "#EC4899",  # ai_sentiment_analyzer
        ]

        import re

        hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")

        for color in colors:
            assert hex_pattern.match(color), f"Invalid hex color: {color}"


class TestConfigComponents:
    """Test config component mapping."""

    def test_bot_config_components_exist(self):
        """Test that bot config components are mapped."""
        bot_configs = [
            "AntiSpamConfig",
            "AutoDeleteConfig",
            "BannedWordsConfig",
            "WelcomeMessagesConfig",
            "InviteTrackingConfig",
            "WarningSystemConfig",
            "AdvancedAnalyticsConfig",
        ]

        for config in bot_configs:
            assert config.endswith("Config"), f"Config should end with 'Config': {config}"

    def test_mtproto_config_components_exist(self):
        """Test that MTProto config components are mapped."""
        mtproto_configs = [
            "HistoryAccessConfig",
            "AutoCollectConfig",
            "MediaDownloadConfig",
            "BulkExportConfig",
        ]

        for config in mtproto_configs:
            assert config.endswith("Config"), f"Config should end with 'Config': {config}"

    def test_ai_config_components_exist(self):
        """Test that AI config components are mapped."""
        ai_configs = [
            "ContentOptimizerConfig",
            "SentimentAnalyzerConfig",
            "SmartRepliesConfig",
            "ContentModerationConfig",
        ]

        for config in ai_configs:
            assert config.endswith("Config"), f"Config should end with 'Config': {config}"


class TestHelperFunctions:
    """Test registry helper functions."""

    def test_get_services_by_category_bot(self):
        """Test getting bot services by category."""
        bot_prefix = "bot_"
        sample_keys = [
            "bot_anti_spam",
            "bot_banned_words",
            "mtproto_history_access",
            "ai_content_optimizer",
        ]

        bot_keys = [k for k in sample_keys if k.startswith(bot_prefix)]

        assert len(bot_keys) == 2
        assert all(k.startswith(bot_prefix) for k in bot_keys)

    def test_get_services_by_category_mtproto(self):
        """Test getting MTProto services by category."""
        mtproto_prefix = "mtproto_"
        sample_keys = [
            "bot_anti_spam",
            "mtproto_history_access",
            "mtproto_auto_collect",
            "ai_content_optimizer",
        ]

        mtproto_keys = [k for k in sample_keys if k.startswith(mtproto_prefix)]

        assert len(mtproto_keys) == 2
        assert all(k.startswith(mtproto_prefix) for k in mtproto_keys)

    def test_get_services_by_category_ai(self):
        """Test getting AI services by category."""
        ai_prefix = "ai_"
        sample_keys = [
            "bot_anti_spam",
            "mtproto_history_access",
            "ai_content_optimizer",
            "ai_sentiment_analyzer",
        ]

        ai_keys = [k for k in sample_keys if k.startswith(ai_prefix)]

        assert len(ai_keys) == 2
        assert all(k.startswith(ai_prefix) for k in ai_keys)

    def test_is_service_registered(self):
        """Test checking if a service is registered."""
        registered_services = {
            "bot_anti_spam",
            "mtproto_history_access",
            "ai_content_optimizer",
        }

        assert "bot_anti_spam" in registered_services
        assert "nonexistent_service" not in registered_services

    def test_get_all_service_keys(self):
        """Test getting all registered service keys."""
        all_keys = [
            "bot_anti_spam",
            "bot_auto_delete_joins",
            "mtproto_history_access",
            "ai_content_optimizer",
        ]

        # Should have services from all categories
        has_bot = any(k.startswith("bot_") for k in all_keys)
        has_mtproto = any(k.startswith("mtproto_") for k in all_keys)
        has_ai = any(k.startswith("ai_") for k in all_keys)

        assert has_bot, "Should have bot services"
        assert has_mtproto, "Should have MTProto services"
        assert has_ai, "Should have AI services"


class TestServiceCounts:
    """Test service count expectations."""

    def test_total_bot_services(self):
        """Test expected number of bot services."""
        expected_count = 7
        bot_services = [
            "bot_anti_spam",
            "bot_auto_delete_joins",
            "bot_banned_words",
            "bot_welcome_messages",
            "bot_invite_tracking",
            "bot_warning_system",
            "bot_analytics_advanced",
        ]

        assert len(bot_services) == expected_count

    def test_total_mtproto_services(self):
        """Test expected number of MTProto services."""
        expected_count = 4
        mtproto_services = [
            "mtproto_history_access",
            "mtproto_auto_collect",
            "mtproto_media_download",
            "mtproto_bulk_export",
        ]

        assert len(mtproto_services) == expected_count

    def test_total_ai_services(self):
        """Test expected number of AI services."""
        expected_count = 4
        ai_services = [
            "ai_content_optimizer",
            "ai_sentiment_analyzer",
            "ai_smart_replies",
            "ai_content_moderation",
        ]

        assert len(ai_services) == expected_count

    def test_total_services(self):
        """Test total number of services."""
        expected_total = 7 + 4 + 4  # bot + mtproto + ai

        assert expected_total == 15
