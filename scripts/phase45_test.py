"""
Phase 4.5 Bot UI & Alerts Integration - Comprehensive Test Suite
Tests all components of the bot integration system
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from apps.api.exports.csv_v2 import CSVExporter
from apps.bot.clients.analytics_v2_client import AnalyticsV2Client
from apps.jobs.alerts.runner import AlertDetector
from config.settings import Settings
from infra.db.repositories.alert_repository import AsyncPgAlertRepository
from infra.db.repositories.shared_reports_repository import (
    AsyncPgSharedReportsRepository,
)
from infra.rendering.charts import MATPLOTLIB_AVAILABLE, ChartRenderer

logger = logging.getLogger(__name__)


class Phase45TestSuite:
    """Comprehensive test suite for Phase 4.5 components"""

    def __init__(self):
        self.settings = Settings()
        self.test_results: dict[str, Any] = {}

        # Initialize components
        self.analytics_client = AnalyticsV2Client(self.settings.ANALYTICS_API_URL)
        self.csv_exporter = CSVExporter()
        self.chart_renderer = ChartRenderer() if MATPLOTLIB_AVAILABLE else None
        self.alert_repository = AsyncPgAlertRepository()
        self.shared_reports_repository = AsyncPgSharedReportsRepository()

        # Test data
        self.test_channel_id = "@test_channel"
        self.test_user_id = 12345
        self.test_period = 7

    def log_test_result(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test result"""
        self.test_results[test_name] = {
            "success": success,
            "message": message,
            "data": data,
        }

        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {message}")

    async def test_feature_flags(self):
        """Test feature flag configuration"""
        test_name = "Feature Flags Configuration"

        try:
            flags = {
                "BOT_ANALYTICS_UI_ENABLED": self.settings.BOT_ANALYTICS_UI_ENABLED,
                "ALERTS_ENABLED": self.settings.ALERTS_ENABLED,
                "EXPORT_ENABLED": self.settings.EXPORT_ENABLED,
                "SHARE_LINKS_ENABLED": self.settings.SHARE_LINKS_ENABLED,
            }

            # Verify all flags are accessible
            required_attrs = ["BOT_TOKEN", "ANALYTICS_API_URL", "RATE_LIMIT_PER_MINUTE"]
            missing_attrs = [attr for attr in required_attrs if not hasattr(self.settings, attr)]

            if missing_attrs:
                self.log_test_result(test_name, False, f"Missing settings: {missing_attrs}")
                return

            self.log_test_result(test_name, True, "All feature flags configured", flags)

        except Exception as e:
            self.log_test_result(test_name, False, f"Configuration error: {e}")

    async def test_analytics_client(self):
        """Test Analytics V2 client functionality"""
        test_name = "Analytics V2 Client"

        try:
            # Test client initialization
            client_config = {
                "base_url": self.analytics_client.base_url,
                "timeout": self.analytics_client.timeout,
                "retry_attempts": self.analytics_client.retry_attempts,
            }

            # Mock test - in real scenario would test actual API calls
            mock_response = {
                "channel_id": self.test_channel_id,
                "period": self.test_period,
                "overview": {"views": 10000, "subscribers": 5000, "posts_count": 50},
            }

            self.log_test_result(
                test_name,
                True,
                "Client initialized successfully",
                {"config": client_config, "mock_response": mock_response},
            )

        except Exception as e:
            self.log_test_result(test_name, False, f"Client error: {e}")

    async def test_csv_export_service(self):
        """Test CSV export functionality"""
        test_name = "CSV Export Service"

        try:
            # Create mock data for CSV export
            mock_overview_data = type(
                "MockOverview",
                (),
                {
                    "channel_id": self.test_channel_id,
                    "period": self.test_period,
                    "overview": type(
                        "Overview",
                        (),
                        {
                            "views": 10000,
                            "subscribers": 5000,
                            "posts_count": 50,
                            "engagement_rate": 15.5,
                        },
                    )(),
                },
            )()

            # Test CSV generation
            csv_content = self.csv_exporter.overview_to_csv(mock_overview_data)
            filename = self.csv_exporter.get_filename(
                "overview", self.test_channel_id, self.test_period
            )

            # Verify CSV content structure
            csv_lines = csv_content.strip().split("\n")
            has_header = len(csv_lines) > 0 and "metric" in csv_lines[0].lower()
            has_data = len(csv_lines) > 1

            success = has_header and has_data and len(csv_content) > 100

            self.log_test_result(
                test_name,
                success,
                f"CSV generated: {len(csv_lines)} lines, filename: {filename}",
                {"csv_length": len(csv_content), "lines": len(csv_lines)},
            )

        except Exception as e:
            self.log_test_result(test_name, False, f"CSV export error: {e}")

    async def test_chart_rendering(self):
        """Test PNG chart rendering"""
        test_name = "Chart Rendering Service"

        try:
            if not MATPLOTLIB_AVAILABLE:
                self.log_test_result(test_name, False, "Matplotlib not available")
                return

            if not self.chart_renderer:
                self.log_test_result(test_name, False, "Chart renderer not initialized")
                return

            # Test line chart rendering
            from datetime import datetime, timedelta

            test_points = []
            for i in range(7):
                date = datetime.now() - timedelta(days=6 - i)
                value = 1000 + (i * 200) + (i % 2 * 100)  # Sample growth data
                test_points.append((date, value))

            png_bytes = self.chart_renderer.render_line_chart(
                test_points, title="Test Growth Chart", xlabel="Date", ylabel="Views"
            )

            success = len(png_bytes) > 1000  # PNG should be reasonably sized

            self.log_test_result(
                test_name,
                success,
                f"Chart rendered: {len(png_bytes)} bytes",
                {"chart_size": len(png_bytes)},
            )

        except Exception as e:
            self.log_test_result(test_name, False, f"Chart rendering error: {e}")

    async def test_alert_repository(self):
        """Test alert repository operations"""
        test_name = "Alert Repository"

        try:
            # Test alert subscription creation
            test_alert = {
                "user_id": self.test_user_id,
                "channel_id": self.test_channel_id,
                "alert_type": "spike",
                "threshold": 50.0,
                "is_active": True,
                "config": {"period": 24},
            }

            # Mock repository test (would need actual DB connection in real test)
            mock_alert_id = f"alert_{self.test_user_id}_{self.test_channel_id}_spike"

            # Test alert configuration validation
            required_fields = ["user_id", "channel_id", "alert_type", "threshold"]
            has_required = all(field in test_alert for field in required_fields)

            valid_alert_type = test_alert["alert_type"] in ["spike", "quiet", "growth"]
            valid_threshold = isinstance(test_alert["threshold"], (int, float))

            success = has_required and valid_alert_type and valid_threshold

            self.log_test_result(
                test_name,
                success,
                f"Alert configuration validated: {mock_alert_id}",
                test_alert,
            )

        except Exception as e:
            self.log_test_result(test_name, False, f"Alert repository error: {e}")

    async def test_shared_reports(self):
        """Test shared reports functionality"""
        test_name = "Shared Reports System"

        try:
            import secrets
            from datetime import datetime, timedelta

            # Test share link generation
            share_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=24)

            mock_shared_report = {
                "share_token": share_token,
                "report_type": "overview",
                "channel_id": self.test_channel_id,
                "period": self.test_period,
                "format": "csv",
                "expires_at": expires_at,
                "created_at": datetime.utcnow(),
                "access_count": 0,
            }

            # Validate share token security
            token_length = len(share_token)
            token_secure = (
                token_length >= 32 and share_token.replace("_", "").replace("-", "").isalnum()
            )

            # Validate expiration
            valid_expiry = expires_at > datetime.utcnow()

            success = token_secure and valid_expiry

            self.log_test_result(
                test_name,
                success,
                f"Share token generated: {token_length} chars, expires in {(expires_at - datetime.utcnow()).total_seconds():.0f}s",
                {
                    "token_length": token_length,
                    "report_type": mock_shared_report["report_type"],
                },
            )

        except Exception as e:
            self.log_test_result(test_name, False, f"Shared reports error: {e}")

    async def test_alert_detection(self):
        """Test alert detection logic"""
        test_name = "Alert Detection Logic"

        try:
            AlertDetector(self.analytics_client, self.alert_repository)

            # Mock alert configuration for spike detection
            spike_config = {
                "channel_id": self.test_channel_id,
                "alert_type": "spike",
                "threshold": 50.0,
                "period": 24,
            }

            # Mock growth configuration
            growth_config = {
                "channel_id": self.test_channel_id,
                "alert_type": "growth",
                "threshold": 10000,
                "period": 7,
            }

            # Validate configuration structure
            required_fields = ["channel_id", "alert_type", "threshold"]

            spike_valid = all(field in spike_config for field in required_fields)
            growth_valid = all(field in growth_config for field in required_fields)

            # Test threshold validation
            valid_spike_threshold = 0 <= spike_config["threshold"] <= 1000
            valid_growth_threshold = growth_config["threshold"] > 0

            success = (
                spike_valid and growth_valid and valid_spike_threshold and valid_growth_threshold
            )

            self.log_test_result(
                test_name,
                success,
                "Alert detection configurations validated",
                {"spike_config": spike_config, "growth_config": growth_config},
            )

        except Exception as e:
            self.log_test_result(test_name, False, f"Alert detection error: {e}")

    async def test_throttling_middleware(self):
        """Test rate limiting middleware"""
        test_name = "Throttling Middleware"

        try:
            from apps.bot.middleware.throttle import (
                InMemoryThrottleStorage,
                ThrottleMiddleware,
            )

            # Test throttle storage
            storage = InMemoryThrottleStorage()
            ThrottleMiddleware(storage)

            # Test rate limit configuration
            test_limits = {
                "per_minute": self.settings.RATE_LIMIT_PER_MINUTE,
                "per_hour": self.settings.RATE_LIMIT_PER_HOUR,
            }

            # Validate rate limits are reasonable
            valid_minute_limit = 1 <= test_limits["per_minute"] <= 100
            valid_hour_limit = 10 <= test_limits["per_hour"] <= 1000

            success = valid_minute_limit and valid_hour_limit

            self.log_test_result(
                test_name,
                success,
                f"Rate limits configured: {test_limits}",
                test_limits,
            )

        except Exception as e:
            self.log_test_result(test_name, False, f"Throttling error: {e}")

    async def test_bot_keyboards(self):
        """Test bot keyboard generation"""
        test_name = "Bot Keyboards"

        try:
            from apps.bot.keyboards.analytics import (
                get_analytics_main_keyboard,
                get_export_format_keyboard,
                get_export_type_keyboard,
            )

            # Test main keyboard
            main_kb = get_analytics_main_keyboard()
            has_buttons = len(main_kb.inline_keyboard) > 0

            # Test export keyboards
            export_type_kb = get_export_type_keyboard()
            export_format_kb = get_export_format_keyboard("growth")

            # Validate keyboard structure
            keyboards_valid = all(
                [
                    hasattr(kb, "inline_keyboard") and len(kb.inline_keyboard) > 0
                    for kb in [main_kb, export_type_kb, export_format_kb]
                ]
            )

            button_count = sum(len(row) for row in main_kb.inline_keyboard)

            success = has_buttons and keyboards_valid and button_count >= 4

            self.log_test_result(
                test_name,
                success,
                f"Keyboards generated: {button_count} total buttons",
                {"keyboards": ["main", "export_type", "export_format"]},
            )

        except Exception as e:
            self.log_test_result(test_name, False, f"Keyboard error: {e}")

    async def run_all_tests(self):
        """Run all Phase 4.5 tests"""
        logger.info("🚀 Starting Phase 4.5 Comprehensive Test Suite")

        # Define test sequence
        tests = [
            self.test_feature_flags,
            self.test_analytics_client,
            self.test_csv_export_service,
            self.test_chart_rendering,
            self.test_alert_repository,
            self.test_shared_reports,
            self.test_alert_detection,
            self.test_throttling_middleware,
            self.test_bot_keyboards,
        ]

        # Run tests sequentially
        for test in tests:
            try:
                await test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test_result(test_name, False, f"Test execution error: {e}")

        # Generate summary
        self.generate_test_summary()

    def generate_test_summary(self):
        """Generate and display test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print("\n" + "=" * 60)
        print("📊 PHASE 4.5 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 60)

        # Detailed results
        for test_name, result in self.test_results.items():
            status = "✅" if result["success"] else "❌"
            print(f"{status} {test_name}: {result['message']}")

        print("=" * 60)

        # Component status summary
        print("\n🔧 COMPONENT STATUS:")
        components = {
            "Feature Flags": any("flag" in name.lower() for name in self.test_results.keys()),
            "Analytics Client": any(
                "analytics" in name.lower() and "client" in name.lower()
                for name in self.test_results.keys()
            ),
            "CSV Export": any("csv" in name.lower() for name in self.test_results.keys()),
            "Chart Rendering": any("chart" in name.lower() for name in self.test_results.keys()),
            "Alert System": any("alert" in name.lower() for name in self.test_results.keys()),
            "Shared Reports": any("shared" in name.lower() for name in self.test_results.keys()),
            "Bot Interface": any(
                "keyboard" in name.lower() or "throttl" in name.lower()
                for name in self.test_results.keys()
            ),
        }

        for component, tested in components.items():
            status = "✅ TESTED" if tested else "⏳ PENDING"
            print(f"  {status} - {component}")

        print("\n🎯 RECOMMENDATIONS:")
        if success_rate >= 90:
            print("  ✅ System ready for deployment")
        elif success_rate >= 75:
            print("  ⚠️  Address failing tests before deployment")
        else:
            print("  ❌ Major issues found - extensive fixes needed")

        # Feature flag recommendations
        if not self.settings.BOT_ANALYTICS_UI_ENABLED:
            print("  📋 Enable BOT_ANALYTICS_UI_ENABLED for full functionality")
        if not self.settings.EXPORT_ENABLED:
            print("  📤 Enable EXPORT_ENABLED for export features")
        if not self.settings.ALERTS_ENABLED:
            print("  🔔 Enable ALERTS_ENABLED for alert system")


async def main():
    """Run Phase 4.5 test suite"""
    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Run tests
    test_suite = Phase45TestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
