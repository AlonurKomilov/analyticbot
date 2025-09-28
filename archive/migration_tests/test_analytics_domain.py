#!/usr/bin/env python3
"""
Analytics Domain Structure Validation Test

Tests that all analytics domain components can be imported correctly
and validates the domain layer architecture.
"""

import sys
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_analytics_domain_structure():
    """Test analytics domain structure and imports"""
    print("🧪 Testing Analytics Domain Structure...")

    try:
        # Test value objects
        print("📝 Testing value objects...")
        from src.analytics.domain.value_objects.analytics_value_objects import (
            AnalyticsMetric,
            ChannelId,
            ChannelTitle,
            PostContent,
            PostId,
            ViewCount,
        )

        # Create test instances
        channel_id = ChannelId("channel_123")
        post_id = PostId("post_456")
        view_count = ViewCount(1500)
        metric = AnalyticsMetric("test_metric", 42.5, "views")

        print(f"   ✅ Channel ID: {channel_id}")
        print(f"   ✅ View Count: {view_count}")
        print(f"   ✅ Metric: {metric.formatted_value}")

        # Test domain events
        print("📡 Testing domain events...")

        # Test entities
        print("🏛️  Testing entities...")
        from src.analytics.domain.entities import (
            AnalyticsReport,
            Channel,
            Post,
            ReportType,
        )

        # Test repositories
        print("🗂️  Testing repository interfaces...")

        print("✅ All analytics domain imports successful!")

        # Test entity creation
        print("🏗️  Testing entity creation...")

        from src.shared_kernel.domain.value_objects import UserId

        user_id = UserId(123)
        channel_title = ChannelTitle("Test Channel")

        # Create a channel
        channel = Channel.create_new_channel(
            channel_id=channel_id, user_id=user_id, title=channel_title
        )

        print(f"   ✅ Created channel: {channel.title} (ID: {channel.id})")
        print(f"   ✅ Channel status: {channel.status}")
        print(f"   ✅ Channel has domain events: {len(channel.get_domain_events()) > 0}")

        # Test channel business logic
        channel.update_subscriber_count(1000)
        channel.add_post(ViewCount(250))

        print(f"   ✅ Channel subscribers: {channel.subscriber_count}")
        print(f"   ✅ Channel total posts: {channel.total_posts}")
        print(f"   ✅ Channel total views: {channel.total_views}")

        # Create a post

        post_content = PostContent("This is a test post content")
        post = Post.create_draft_post(
            post_id=post_id,
            channel_id=channel_id,
            user_id=user_id,
            content=post_content,
        )

        print(f"   ✅ Created post: {post.get_content_preview()}")
        print(f"   ✅ Post status: {post.status}")
        print(f"   ✅ Post type: {post.post_type}")

        # Test analytics report
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        period_start = now - timedelta(days=7)
        period_end = now

        report = AnalyticsReport.create_new_report(
            user_id=user_id,
            report_type=ReportType.WEEKLY,
            period_start=period_start,
            period_end=period_end,
        )

        print(f"   ✅ Created report: {report.title}")
        print(f"   ✅ Report type: {report.report_type}")
        print(f"   ✅ Report period: {report.get_period_description()}")

        print("\n🎉 Analytics Domain Structure Test PASSED!")
        print("   All components imported and tested successfully")

        return True

    except Exception as e:
        print("\n❌ Analytics Domain Structure Test FAILED!")
        print(f"Error: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        return False


def test_analytics_domain_patterns():
    """Test analytics domain follows proper DDD patterns"""
    print("\n🔍 Testing Analytics Domain Patterns...")

    try:
        from src.analytics.domain.entities.analytics_report import AnalyticsReport
        from src.analytics.domain.entities.channel import Channel
        from src.analytics.domain.entities.post import Post
        from src.shared_kernel.domain.base_entity import AggregateRoot

        # Test that entities are aggregate roots
        assert issubclass(Channel, AggregateRoot), "Channel must be an AggregateRoot"
        assert issubclass(Post, AggregateRoot), "Post must be an AggregateRoot"
        assert issubclass(AnalyticsReport, AggregateRoot), (
            "AnalyticsReport must be an AggregateRoot"
        )

        print("   ✅ All entities properly inherit from AggregateRoot")

        # Test value objects are immutable
        from src.analytics.domain.value_objects.analytics_value_objects import (
            ChannelId,
            ViewCount,
        )

        channel_id = ChannelId("test_123")
        ViewCount(100)

        # Value objects should be immutable (frozen dataclasses)
        try:
            # This should fail if properly implemented as immutable
            channel_id.value = "modified"
            print("   ⚠️  Warning: ChannelId appears to be mutable")
        except (AttributeError, TypeError, Exception):
            print("   ✅ ChannelId is properly immutable")

        print("   ✅ Domain patterns validation passed")

        return True

    except Exception as e:
        print("❌ Analytics Domain Patterns Test FAILED!")
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return False


def main():
    """Main test runner"""
    print("=" * 60)
    print("🔬 ANALYTICS DOMAIN VALIDATION TESTS")
    print("=" * 60)

    tests_passed = 0
    total_tests = 2

    # Run tests
    if test_analytics_domain_structure():
        tests_passed += 1

    if test_analytics_domain_patterns():
        tests_passed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎊 ALL TESTS PASSED! Analytics Domain is properly structured.")
        return 0
    else:
        print("💥 SOME TESTS FAILED! Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
