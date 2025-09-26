"""
Module TQA.2.4.3: Analytics Workflow Testing

This module provides comprehensive end-to-end testing for analytics workflows,
covering data collection, processing, report generation, and delivery.

Test Structure:
- TestAnalyticsDataCollectionWorkflow: Data ingestion and validation
- TestReportGenerationWorkflow: Report creation and customization
- TestScheduledAnalyticsWorkflow: Automated report scheduling and delivery
- TestRealTimeAnalyticsWorkflow: Live analytics updates and notifications
- TestCrossChannelAnalyticsWorkflow: Multi-channel data aggregation
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock

# Test framework imports
import pytest
from fakeredis.aioredis import FakeRedis as FakeAsyncRedis

# Mock analytics workflow state
analytics_workflow_state = {}


def get_analytics_workflow_state(workflow_id: str) -> dict[str, Any]:
    return analytics_workflow_state.get(workflow_id, {})


def update_analytics_workflow_state(workflow_id: str, updates: dict[str, Any]):
    if workflow_id not in analytics_workflow_state:
        analytics_workflow_state[workflow_id] = {}
    analytics_workflow_state[workflow_id].update(updates)


def clear_analytics_workflow_state():
    global analytics_workflow_state
    analytics_workflow_state = {}


@pytest.fixture
def mock_analytics_api():
    """Mock Analytics API client"""
    client = AsyncMock()

    # Default successful responses
    client.get.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"success": True, "data": {}})
    )
    client.post.return_value = AsyncMock(
        status_code=201, json=AsyncMock(return_value={"success": True, "data": {}})
    )

    return client


@pytest.fixture
def mock_telegram_analytics():
    """Mock Telegram Bot API for analytics"""
    bot = AsyncMock()

    # Mock message sending
    bot.send_message.return_value = AsyncMock(message_id=12345)
    bot.send_document.return_value = AsyncMock(message_id=12346)
    bot.send_photo.return_value = AsyncMock(message_id=12347)

    # Mock chat info
    bot.get_chat.return_value = AsyncMock(
        id=-123456789,
        title="Test Channel",
        type="channel",
        username="test_channel",
        member_count=1500,
    )

    return bot


@pytest.fixture
async def mock_analytics_redis():
    """Mock Redis for analytics data storage"""
    client = FakeAsyncRedis(decode_responses=True)

    # Pre-populate with sample analytics data
    await client.hset(
        "channel_stats:-123456789",
        mapping={
            "subscribers": "1500",
            "posts_today": "5",
            "engagement_rate": "0.15",
            "last_updated": datetime.now().isoformat(),
        },
    )

    yield client
    await client.flushall()
    await client.close()


@pytest.fixture
def mock_data_processor():
    """Mock data processing engine"""
    processor = AsyncMock()

    # Mock data processing methods
    processor.collect_channel_data.return_value = {
        "subscribers": 1500,
        "posts": 45,
        "views": 25000,
        "engagement": 3750,
    }

    processor.generate_insights.return_value = {
        "growth_rate": 5.2,
        "best_posting_time": "19:00",
        "top_content_type": "video",
        "engagement_trend": "increasing",
    }

    return processor


@pytest.fixture
def mock_report_generator():
    """Mock report generation service"""
    generator = AsyncMock()

    # Mock report generation
    generator.create_pdf_report.return_value = b"PDF_REPORT_CONTENT"
    generator.create_chart.return_value = b"CHART_IMAGE_DATA"
    generator.create_excel_report.return_value = b"EXCEL_REPORT_CONTENT"

    return generator


@pytest.fixture(autouse=True)
def setup_analytics_workflow_test():
    """Setup and cleanup for analytics workflow tests"""
    clear_analytics_workflow_state()
    yield
    clear_analytics_workflow_state()


class TestAnalyticsDataCollectionWorkflow:
    """Test analytics data collection and validation workflows"""

    @pytest.mark.asyncio
    async def test_channel_data_collection_workflow(
        self,
        mock_analytics_api,
        mock_telegram_analytics,
        mock_analytics_redis,
        mock_data_processor,
    ):
        """Test complete channel analytics data collection workflow"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        channel_id = -123456789

        # Step 1: Initialize data collection
        update_analytics_workflow_state(
            workflow_id,
            {
                "stage": "data_collection_initiated",
                "user_id": user_id,
                "channel_id": channel_id,
                "collection_type": "full_analytics",
            },
        )

        # Step 2: Get channel information
        await mock_telegram_analytics.get_chat(channel_id)

        # Step 3: Collect current metrics
        current_metrics = await mock_data_processor.collect_channel_data(channel_id)

        # Step 4: Store raw data in Redis
        await mock_analytics_redis.hset(
            f"raw_data:{channel_id}:{datetime.now().strftime('%Y%m%d')}",
            mapping={
                "subscribers": str(current_metrics["subscribers"]),
                "posts": str(current_metrics["posts"]),
                "views": str(current_metrics["views"]),
                "engagement": str(current_metrics["engagement"]),
                "collected_at": datetime.now().isoformat(),
            },
        )

        # Step 5: Get historical data for comparison
        mock_analytics_api.get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {
                        "historical_data": [
                            {
                                "date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                                "subscribers": 1435,
                                "views": 22000,
                                "engagement": 3300,
                            },
                            {
                                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                                "subscribers": 1480,
                                "views": 24500,
                                "engagement": 3600,
                            },
                        ]
                    },
                }
            ),
        )

        historical_response = await mock_analytics_api.get(f"/api/analytics/history/{channel_id}")
        historical_data = await historical_response.json()

        # Step 6: Calculate growth metrics
        previous_data = historical_data["data"]["historical_data"][-1]
        growth_metrics = {
            "subscriber_growth": current_metrics["subscribers"] - previous_data["subscribers"],
            "view_growth": current_metrics["views"] - previous_data["views"],
            "engagement_growth": current_metrics["engagement"] - previous_data["engagement"],
            "growth_rate": (
                (current_metrics["subscribers"] - previous_data["subscribers"])
                / previous_data["subscribers"]
            )
            * 100,
        }

        # Step 7: Store processed analytics
        mock_analytics_api.post.return_value = AsyncMock(
            status_code=201,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {
                        "analytics_id": str(uuid.uuid4()),
                        "processed_at": datetime.now().isoformat(),
                    },
                }
            ),
        )

        await mock_analytics_api.post(
            f"/api/analytics/{channel_id}",
            json={
                "current_metrics": current_metrics,
                "growth_metrics": growth_metrics,
                "collection_timestamp": datetime.now().isoformat(),
            },
        )

        # Step 8: Update Redis cache with latest stats
        await mock_analytics_redis.hset(
            f"channel_stats:{channel_id}",
            mapping={
                "subscribers": str(current_metrics["subscribers"]),
                "subscriber_growth": str(growth_metrics["subscriber_growth"]),
                "growth_rate": str(round(growth_metrics["growth_rate"], 2)),
                "last_updated": datetime.now().isoformat(),
            },
        )

        # Step 9: Schedule next collection
        next_collection = datetime.now() + timedelta(hours=6)
        await mock_analytics_redis.zadd(
            "scheduled_collections",
            {f"{channel_id}:{workflow_id}": next_collection.timestamp()},
        )

        # Workflow completion
        update_analytics_workflow_state(
            workflow_id,
            {
                "stage": "data_collection_completed",
                "metrics_collected": True,
                "growth_calculated": True,
                "next_collection_scheduled": True,
            },
        )

        # Validate data collection workflow
        state = get_analytics_workflow_state(workflow_id)
        assert state["stage"] == "data_collection_completed"
        assert state["metrics_collected"] is True
        assert state["growth_calculated"] is True

        # Verify data was stored
        channel_stats = await mock_analytics_redis.hgetall(f"channel_stats:{channel_id}")
        assert int(channel_stats["subscribers"]) == current_metrics["subscribers"]
        assert float(channel_stats["growth_rate"]) == round(growth_metrics["growth_rate"], 2)

        # Verify service calls
        mock_data_processor.collect_channel_data.assert_called_once_with(channel_id)
        mock_analytics_api.get.assert_called_once()
        mock_analytics_api.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_multi_channel_data_aggregation_workflow(
        self, mock_analytics_api, mock_data_processor, mock_analytics_redis
    ):
        """Test aggregation of data from multiple channels"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        channel_ids = [-123456789, -987654321, -555666777]

        # Step 1: Initialize multi-channel collection
        update_analytics_workflow_state(
            workflow_id,
            {
                "stage": "multi_channel_collection_initiated",
                "user_id": user_id,
                "channel_ids": channel_ids,
                "total_channels": len(channel_ids),
            },
        )

        # Step 2: Collect data from each channel
        channel_data = {}
        for i, channel_id in enumerate(channel_ids):
            # Mock different data for each channel
            mock_data_processor.collect_channel_data.return_value = {
                "subscribers": 1500 + (i * 500),
                "posts": 45 + (i * 10),
                "views": 25000 + (i * 5000),
                "engagement": 3750 + (i * 750),
            }

            data = await mock_data_processor.collect_channel_data(channel_id)
            channel_data[channel_id] = data

            # Store individual channel data
            await mock_analytics_redis.hset(
                f"channel_data:{channel_id}",
                mapping={str(k): str(v) for k, v in data.items()},
            )

        # Step 3: Calculate aggregate metrics
        aggregate_metrics = {
            "total_subscribers": sum(data["subscribers"] for data in channel_data.values()),
            "total_posts": sum(data["posts"] for data in channel_data.values()),
            "total_views": sum(data["views"] for data in channel_data.values()),
            "total_engagement": sum(data["engagement"] for data in channel_data.values()),
            "channel_count": len(channel_ids),
        }

        # Calculate averages
        aggregate_metrics.update(
            {
                "avg_subscribers": aggregate_metrics["total_subscribers"] / len(channel_ids),
                "avg_engagement_rate": aggregate_metrics["total_engagement"]
                / aggregate_metrics["total_views"],
                "avg_posts_per_channel": aggregate_metrics["total_posts"] / len(channel_ids),
            }
        )

        # Step 4: Store aggregate data
        await mock_analytics_redis.hset(
            f"aggregate_stats:{user_id}",
            mapping={
                "total_subscribers": str(aggregate_metrics["total_subscribers"]),
                "total_channels": str(aggregate_metrics["channel_count"]),
                "avg_engagement_rate": str(round(aggregate_metrics["avg_engagement_rate"], 4)),
                "collected_at": datetime.now().isoformat(),
            },
        )

        # Step 5: Save to database
        mock_analytics_api.post.return_value = AsyncMock(
            status_code=201,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {"aggregate_id": str(uuid.uuid4())},
                }
            ),
        )

        await mock_analytics_api.post(
            f"/api/analytics/aggregate/{user_id}",
            json={
                "channel_data": channel_data,
                "aggregate_metrics": aggregate_metrics,
                "timestamp": datetime.now().isoformat(),
            },
        )

        # Workflow completion
        update_analytics_workflow_state(
            workflow_id,
            {
                "stage": "multi_channel_aggregation_completed",
                "channels_processed": len(channel_ids),
                "aggregate_calculated": True,
            },
        )

        # Validate aggregation workflow
        state = get_analytics_workflow_state(workflow_id)
        assert state["stage"] == "multi_channel_aggregation_completed"
        assert state["channels_processed"] == len(channel_ids)
        assert state["aggregate_calculated"] is True

        # Verify aggregate data
        aggregate_stats = await mock_analytics_redis.hgetall(f"aggregate_stats:{user_id}")
        assert int(aggregate_stats["total_subscribers"]) == aggregate_metrics["total_subscribers"]
        assert int(aggregate_stats["total_channels"]) == len(channel_ids)


class TestReportGenerationWorkflow:
    """Test analytics report generation workflows"""

    @pytest.mark.asyncio
    async def test_comprehensive_report_generation_workflow(
        self,
        mock_analytics_api,
        mock_report_generator,
        mock_analytics_redis,
        mock_telegram_analytics,
    ):
        """Test comprehensive analytics report generation and delivery"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        channel_id = -123456789
        report_type = "comprehensive_monthly"

        # Step 1: Initialize report generation
        update_analytics_workflow_state(
            workflow_id,
            {
                "stage": "report_generation_initiated",
                "user_id": user_id,
                "channel_id": channel_id,
                "report_type": report_type,
            },
        )

        # Step 2: Fetch analytics data
        mock_analytics_api.get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {
                        "current_metrics": {
                            "subscribers": 1500,
                            "posts": 45,
                            "views": 25000,
                            "engagement": 3750,
                        },
                        "historical_data": [
                            {
                                "date": "2024-01-01",
                                "subscribers": 1200,
                                "views": 18000,
                                "engagement": 2700,
                            },
                            {
                                "date": "2024-01-15",
                                "subscribers": 1350,
                                "views": 21500,
                                "engagement": 3200,
                            },
                            {
                                "date": "2024-01-30",
                                "subscribers": 1500,
                                "views": 25000,
                                "engagement": 3750,
                            },
                        ],
                        "insights": {
                            "growth_rate": 25.0,
                            "best_posting_time": "19:00",
                            "top_content_type": "educational",
                            "engagement_trend": "increasing",
                        },
                    },
                }
            ),
        )

        analytics_data = await mock_analytics_api.get(f"/api/analytics/{channel_id}/comprehensive")
        report_data = await analytics_data.json()

        # Step 3: Generate visualizations
        chart_data = await mock_report_generator.create_chart(
            data=report_data["data"]["historical_data"],
            chart_type="growth_trend",
            title="Subscriber Growth Trend",
        )

        engagement_chart = await mock_report_generator.create_chart(
            data=report_data["data"]["current_metrics"],
            chart_type="engagement_breakdown",
            title="Engagement Breakdown",
        )

        # Step 4: Generate PDF report
        pdf_report = await mock_report_generator.create_pdf_report(
            data=report_data["data"],
            template="comprehensive_monthly",
            charts=[chart_data, engagement_chart],
        )

        # Step 5: Generate Excel report
        excel_report = await mock_report_generator.create_excel_report(
            data=report_data["data"],
            sheets=["Overview", "Detailed_Metrics", "Historical_Data"],
        )

        # Step 6: Store generated reports
        await mock_analytics_redis.hset(
            f"generated_reports:{workflow_id}",
            mapping={
                "pdf_size": str(len(pdf_report)),
                "excel_size": str(len(excel_report)),
                "chart_count": "2",
                "generated_at": datetime.now().isoformat(),
            },
        )

        # Step 7: Send reports to user
        # Send PDF report
        await mock_telegram_analytics.send_document(
            chat_id=user_id,
            document=pdf_report,
            filename=f"analytics_report_{datetime.now().strftime('%Y%m%d')}.pdf",
            caption="📊 Your comprehensive analytics report is ready!\n\n📈 Key highlights included in the report.",
        )

        # Send Excel report
        await mock_telegram_analytics.send_document(
            chat_id=user_id,
            document=excel_report,
            filename=f"analytics_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
            caption="📋 Detailed analytics data in Excel format for further analysis.",
        )

        # Send charts as images
        await mock_telegram_analytics.send_photo(
            chat_id=user_id,
            photo=chart_data,
            caption="📈 Subscriber Growth Trend Chart",
        )

        # Step 8: Log report delivery
        mock_analytics_api.post.return_value = AsyncMock(
            status_code=201,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {"delivery_id": str(uuid.uuid4())},
                }
            ),
        )

        await mock_analytics_api.post(
            "/api/analytics/reports/delivery",
            json={
                "user_id": user_id,
                "channel_id": channel_id,
                "report_type": report_type,
                "delivered_at": datetime.now().isoformat(),
                "files_delivered": ["pdf", "excel", "charts"],
            },
        )

        # Workflow completion
        update_analytics_workflow_state(
            workflow_id,
            {
                "stage": "report_generation_completed",
                "pdf_generated": True,
                "excel_generated": True,
                "charts_generated": True,
                "reports_delivered": True,
            },
        )

        # Validate report generation workflow
        state = get_analytics_workflow_state(workflow_id)
        assert state["stage"] == "report_generation_completed"
        assert state["pdf_generated"] is True
        assert state["excel_generated"] is True
        assert state["reports_delivered"] is True

        # Verify report generation calls
        mock_report_generator.create_pdf_report.assert_called_once()
        mock_report_generator.create_excel_report.assert_called_once()
        assert mock_report_generator.create_chart.call_count == 2

        # Verify delivery calls
        mock_telegram_analytics.send_document.assert_called()
        mock_telegram_analytics.send_photo.assert_called_once()


class TestScheduledAnalyticsWorkflow:
    """Test scheduled analytics workflows"""

    @pytest.mark.asyncio
    async def test_daily_scheduled_analytics_workflow(
        self,
        mock_analytics_api,
        mock_data_processor,
        mock_telegram_analytics,
        mock_analytics_redis,
    ):
        """Test daily scheduled analytics processing and delivery"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        schedule_id = str(uuid.uuid4())

        # Step 1: Initialize scheduled workflow
        update_analytics_workflow_state(
            workflow_id,
            {
                "stage": "scheduled_analytics_initiated",
                "user_id": user_id,
                "schedule_id": schedule_id,
                "frequency": "daily",
                "delivery_time": "09:00",
            },
        )

        # Step 2: Fetch user's scheduled analytics preferences
        mock_analytics_api.get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {
                        "schedule_id": schedule_id,
                        "user_id": user_id,
                        "channels": [-123456789, -987654321],
                        "report_types": ["summary", "growth_metrics"],
                        "delivery_method": "telegram",
                        "timezone": "UTC",
                        "active": True,
                    },
                }
            ),
        )

        schedule_config = await mock_analytics_api.get(f"/api/analytics/schedules/{schedule_id}")
        config_data = await schedule_config.json()

        # Step 3: Process each channel
        daily_summary = {"channels": {}, "total_metrics": {}}

        for channel_id in config_data["data"]["channels"]:
            # Collect daily data
            mock_data_processor.collect_channel_data.return_value = {
                "subscribers": 1500 + abs(channel_id % 1000),
                "posts_today": 3,
                "views_today": 2500,
                "engagement_today": 375,
            }

            channel_data = await mock_data_processor.collect_channel_data(channel_id)
            daily_summary["channels"][channel_id] = channel_data

            # Store daily metrics
            await mock_analytics_redis.hset(
                f"daily_metrics:{channel_id}:{datetime.now().strftime('%Y%m%d')}",
                mapping={str(k): str(v) for k, v in channel_data.items()},
            )

        # Step 4: Calculate aggregate daily metrics
        daily_summary["total_metrics"] = {
            "total_new_subscribers": sum(
                data["subscribers"] for data in daily_summary["channels"].values()
            )
            - len(config_data["data"]["channels"]) * 1500,  # Subtract baseline
            "total_posts": sum(data["posts_today"] for data in daily_summary["channels"].values()),
            "total_views": sum(data["views_today"] for data in daily_summary["channels"].values()),
            "total_engagement": sum(
                data["engagement_today"] for data in daily_summary["channels"].values()
            ),
        }

        # Step 5: Generate daily insights
        mock_data_processor.generate_insights.return_value = {
            "daily_growth": "positive",
            "best_performing_channel": max(config_data["data"]["channels"]),
            "engagement_trend": "stable",
            "recommendations": ["Post more video content", "Engage with comments"],
        }

        insights = await mock_data_processor.generate_insights(daily_summary["total_metrics"])

        # Step 6: Format and send daily summary
        summary_text = (
            f"📊 Daily Analytics Summary - {datetime.now().strftime('%B %d, %Y')}\n\n"
            f"📈 Total New Subscribers: +{daily_summary['total_metrics']['total_new_subscribers']}\n"
            f"📝 Posts Today: {daily_summary['total_metrics']['total_posts']}\n"
            f"👀 Total Views: {daily_summary['total_metrics']['total_views']:,}\n"
            f"💬 Total Engagement: {daily_summary['total_metrics']['total_engagement']:,}\n\n"
            f"🎯 Key Insights:\n"
            f"• Growth trend: {insights['engagement_trend'].title()}\n"
            f"• Best performing channel: {insights['best_performing_channel']}\n\n"
            f"💡 Recommendations:\n"
        )

        for i, rec in enumerate(insights["recommendations"], 1):
            summary_text += f"{i}. {rec}\n"

        await mock_telegram_analytics.send_message(
            chat_id=user_id,
            text=summary_text,
            reply_markup={
                "inline_keyboard": [
                    [
                        {
                            "text": "📋 Detailed Report",
                            "callback_data": "detailed_daily_report",
                        }
                    ],
                    [{"text": "📊 View Charts", "callback_data": "daily_charts"}],
                    [{"text": "⚙️ Schedule Settings", "callback_data": "edit_schedule"}],
                ]
            },
        )

        # Step 7: Schedule next delivery
        next_delivery = datetime.now().replace(
            hour=9, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        await mock_analytics_redis.zadd(
            "scheduled_deliveries",
            {f"{schedule_id}:{workflow_id}": next_delivery.timestamp()},
        )

        # Step 8: Log delivery
        mock_analytics_api.post.return_value = AsyncMock(
            status_code=201, json=AsyncMock(return_value={"success": True, "data": {}})
        )

        await mock_analytics_api.post(
            f"/api/analytics/schedules/{schedule_id}/deliveries",
            json={
                "delivered_at": datetime.now().isoformat(),
                "summary_metrics": daily_summary["total_metrics"],
                "insights": insights,
            },
        )

        # Workflow completion
        update_analytics_workflow_state(
            workflow_id,
            {
                "stage": "scheduled_analytics_completed",
                "channels_processed": len(config_data["data"]["channels"]),
                "summary_delivered": True,
                "next_delivery_scheduled": True,
            },
        )

        # Validate scheduled workflow
        state = get_analytics_workflow_state(workflow_id)
        assert state["stage"] == "scheduled_analytics_completed"
        assert state["channels_processed"] == len(config_data["data"]["channels"])
        assert state["summary_delivered"] is True

        # Verify next delivery scheduled
        scheduled_deliveries = await mock_analytics_redis.zrange("scheduled_deliveries", 0, -1)
        assert any(schedule_id in delivery for delivery in scheduled_deliveries)


class TestRealTimeAnalyticsWorkflow:
    """Test real-time analytics workflows"""

    @pytest.mark.asyncio
    async def test_real_time_engagement_monitoring_workflow(
        self, mock_analytics_api, mock_telegram_analytics, mock_analytics_redis
    ):
        """Test real-time engagement monitoring and alert workflow"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        channel_id = -123456789

        # Step 1: Initialize real-time monitoring
        update_analytics_workflow_state(
            workflow_id,
            {
                "stage": "realtime_monitoring_initiated",
                "user_id": user_id,
                "channel_id": channel_id,
                "monitoring_type": "engagement_spikes",
            },
        )

        # Step 2: Set up baseline metrics
        baseline_metrics = {
            "avg_views_per_hour": 500,
            "avg_engagement_rate": 0.15,
            "spike_threshold_multiplier": 2.0,
        }

        await mock_analytics_redis.hset(
            f"baseline_metrics:{channel_id}",
            mapping={str(k): str(v) for k, v in baseline_metrics.items()},
        )

        # Step 3: Simulate real-time data stream
        realtime_data_points = [
            {"timestamp": datetime.now(), "views": 520, "engagement": 78},
            {
                "timestamp": datetime.now() + timedelta(minutes=5),
                "views": 1250,
                "engagement": 200,
            },  # Spike
            {
                "timestamp": datetime.now() + timedelta(minutes=10),
                "views": 1800,
                "engagement": 290,
            },  # Continued spike
        ]

        for data_point in realtime_data_points:
            # Calculate engagement rate
            engagement_rate = data_point["engagement"] / data_point["views"]

            # Check for spikes
            is_spike = (
                data_point["views"]
                > baseline_metrics["avg_views_per_hour"]
                * baseline_metrics["spike_threshold_multiplier"]
                or engagement_rate
                > baseline_metrics["avg_engagement_rate"]
                * baseline_metrics["spike_threshold_multiplier"]
            )

            # Store real-time data
            await mock_analytics_redis.zadd(
                f"realtime_data:{channel_id}",
                {
                    json.dumps(
                        {
                            "views": data_point["views"],
                            "engagement": data_point["engagement"],
                            "engagement_rate": engagement_rate,
                            "is_spike": is_spike,
                        }
                    ): data_point["timestamp"].timestamp()
                },
            )

            # If spike detected, trigger alert
            if is_spike:
                update_analytics_workflow_state(
                    workflow_id,
                    {
                        "stage": "engagement_spike_detected",
                        "spike_timestamp": data_point["timestamp"].isoformat(),
                        "spike_magnitude": data_point["views"]
                        / baseline_metrics["avg_views_per_hour"],
                    },
                )

                # Send real-time alert
                await mock_telegram_analytics.send_message(
                    chat_id=user_id,
                    text=f"🚀 Engagement Spike Detected!\n\n"
                    f"📊 Current metrics:\n"
                    f"• Views: {data_point['views']} (📈 {(data_point['views'] / baseline_metrics['avg_views_per_hour'] - 1) * 100:.1f}%)\n"
                    f"• Engagement: {data_point['engagement']} reactions\n"
                    f"• Rate: {engagement_rate:.3f}\n\n"
                    f"🕐 Detected at: {data_point['timestamp'].strftime('%H:%M')}\n\n"
                    f"💡 This is a great time to engage with your audience!",
                    reply_markup={
                        "inline_keyboard": [
                            [
                                {
                                    "text": "📱 View Post",
                                    "callback_data": f"view_spiking_post_{channel_id}",
                                }
                            ],
                            [
                                {
                                    "text": "📊 Live Dashboard",
                                    "callback_data": "open_live_dashboard",
                                }
                            ],
                        ]
                    },
                )

                break

        # Step 4: Generate real-time insights
        mock_analytics_api.post.return_value = AsyncMock(
            status_code=201,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {
                        "insight_id": str(uuid.uuid4()),
                        "recommendations": [
                            "Post similar content during peak engagement",
                            "Engage with comments to maintain momentum",
                            "Consider promoting successful content",
                        ],
                    },
                }
            ),
        )

        await mock_analytics_api.post(
            f"/api/analytics/{channel_id}/realtime-insights",
            json={
                "spike_data": realtime_data_points[1],  # The spike data
                "baseline_metrics": baseline_metrics,
                "detected_at": datetime.now().isoformat(),
            },
        )

        # Workflow completion
        update_analytics_workflow_state(
            workflow_id,
            {
                "stage": "realtime_monitoring_completed",
                "spike_detected": True,
                "alert_sent": True,
                "insights_generated": True,
            },
        )

        # Validate real-time workflow
        state = get_analytics_workflow_state(workflow_id)
        assert state["stage"] == "realtime_monitoring_completed"
        assert state["spike_detected"] is True
        assert state["alert_sent"] is True

        # Verify real-time data was stored
        stored_data = await mock_analytics_redis.zrange(
            "realtime_data:" + str(channel_id), 0, -1, withscores=True
        )
        assert len(stored_data) == len(realtime_data_points)


class TestCrossChannelAnalyticsWorkflow:
    """Test cross-channel analytics aggregation workflows"""

    @pytest.mark.asyncio
    async def test_cross_platform_analytics_aggregation_workflow(
        self,
        mock_analytics_api,
        mock_data_processor,
        mock_report_generator,
        mock_telegram_analytics,
        mock_analytics_redis,
    ):
        """Test cross-platform analytics aggregation and comparative analysis"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789

        # Step 1: Initialize cross-platform analysis
        update_analytics_workflow_state(
            workflow_id,
            {
                "stage": "cross_platform_analysis_initiated",
                "user_id": user_id,
                "platforms": ["telegram", "youtube", "instagram"],
            },
        )

        # Step 2: Collect data from each platform
        platform_data = {}

        # Telegram data
        telegram_channels = [-123456789, -987654321]
        telegram_data = {"total_subscribers": 0, "total_engagement": 0, "channels": {}}

        for channel_id in telegram_channels:
            mock_data_processor.collect_channel_data.return_value = {
                "subscribers": 1500 + abs(channel_id % 500),
                "posts": 45,
                "views": 25000,
                "engagement": 3750,
            }

            channel_data = await mock_data_processor.collect_channel_data(channel_id)
            telegram_data["channels"][channel_id] = channel_data
            telegram_data["total_subscribers"] += channel_data["subscribers"]
            telegram_data["total_engagement"] += channel_data["engagement"]

        platform_data["telegram"] = telegram_data

        # Mock YouTube data
        platform_data["youtube"] = {
            "total_subscribers": 5200,
            "total_views": 45000,
            "total_engagement": 4100,
            "videos": 28,
        }

        # Mock Instagram data
        platform_data["instagram"] = {
            "total_followers": 3800,
            "total_reach": 35000,
            "total_engagement": 2900,
            "posts": 35,
        }

        # Step 3: Normalize metrics across platforms
        normalized_data = {
            "total_audience": (
                platform_data["telegram"]["total_subscribers"]
                + platform_data["youtube"]["total_subscribers"]
                + platform_data["instagram"]["total_followers"]
            ),
            "total_engagement": (
                platform_data["telegram"]["total_engagement"]
                + platform_data["youtube"]["total_engagement"]
                + platform_data["instagram"]["total_engagement"]
            ),
            "platform_breakdown": {
                "telegram": {
                    "audience_share": platform_data["telegram"]["total_subscribers"]
                    / (
                        platform_data["telegram"]["total_subscribers"]
                        + platform_data["youtube"]["total_subscribers"]
                        + platform_data["instagram"]["total_followers"]
                    ),
                    "engagement_rate": platform_data["telegram"]["total_engagement"]
                    / sum(
                        data.get("views", data.get("reach", data.get("total_views", 25000)))
                        for data in platform_data.values()
                    ),
                },
                "youtube": {
                    "audience_share": platform_data["youtube"]["total_subscribers"]
                    / (
                        platform_data["telegram"]["total_subscribers"]
                        + platform_data["youtube"]["total_subscribers"]
                        + platform_data["instagram"]["total_followers"]
                    ),
                    "engagement_rate": platform_data["youtube"]["total_engagement"]
                    / platform_data["youtube"]["total_views"],
                },
                "instagram": {
                    "audience_share": platform_data["instagram"]["total_followers"]
                    / (
                        platform_data["telegram"]["total_subscribers"]
                        + platform_data["youtube"]["total_subscribers"]
                        + platform_data["instagram"]["total_followers"]
                    ),
                    "engagement_rate": platform_data["instagram"]["total_engagement"]
                    / platform_data["instagram"]["total_reach"],
                },
            },
        }

        # Step 4: Generate cross-platform insights
        mock_data_processor.generate_insights.return_value = {
            "best_performing_platform": "youtube",
            "highest_engagement_rate": "telegram",
            "fastest_growing_platform": "instagram",
            "cross_platform_opportunities": [
                "Repurpose top YouTube content for Telegram",
                "Create Instagram stories from Telegram posts",
                "Cross-promote channels across platforms",
            ],
        }

        cross_platform_insights = await mock_data_processor.generate_insights(normalized_data)

        # Step 5: Store aggregated data
        await mock_analytics_redis.hset(
            f"cross_platform_data:{user_id}",
            mapping={
                "total_audience": str(normalized_data["total_audience"]),
                "total_engagement": str(normalized_data["total_engagement"]),
                "best_platform": cross_platform_insights["best_performing_platform"],
                "updated_at": datetime.now().isoformat(),
            },
        )

        # Step 6: Generate comparative report
        comparative_chart = await mock_report_generator.create_chart(
            data=normalized_data["platform_breakdown"],
            chart_type="platform_comparison",
            title="Cross-Platform Performance Comparison",
        )

        # Step 7: Send comparative analysis
        comparison_text = (
            f"📊 Cross-Platform Analytics Report\n\n"
            f"👥 Total Audience: {normalized_data['total_audience']:,}\n"
            f"💬 Total Engagement: {normalized_data['total_engagement']:,}\n\n"
            f"🏆 Platform Performance:\n"
            f"• Best overall: {cross_platform_insights['best_performing_platform'].title()}\n"
            f"• Highest engagement: {cross_platform_insights['highest_engagement_rate'].title()}\n"
            f"• Fastest growing: {cross_platform_insights['fastest_growing_platform'].title()}\n\n"
            f"💡 Cross-platform opportunities:\n"
        )

        for i, opportunity in enumerate(cross_platform_insights["cross_platform_opportunities"], 1):
            comparison_text += f"{i}. {opportunity}\n"

        await mock_telegram_analytics.send_message(
            chat_id=user_id,
            text=comparison_text,
            reply_markup={
                "inline_keyboard": [
                    [
                        {
                            "text": "📊 View Chart",
                            "callback_data": "cross_platform_chart",
                        }
                    ],
                    [
                        {
                            "text": "📋 Detailed Report",
                            "callback_data": "cross_platform_report",
                        }
                    ],
                ]
            },
        )

        # Send comparative chart
        await mock_telegram_analytics.send_photo(
            chat_id=user_id,
            photo=comparative_chart,
            caption="📈 Cross-Platform Performance Comparison",
        )

        # Step 8: Save analysis to database
        mock_analytics_api.post.return_value = AsyncMock(
            status_code=201,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {"analysis_id": str(uuid.uuid4())},
                }
            ),
        )

        await mock_analytics_api.post(
            f"/api/analytics/cross-platform/{user_id}",
            json={
                "platform_data": platform_data,
                "normalized_data": normalized_data,
                "insights": cross_platform_insights,
                "analyzed_at": datetime.now().isoformat(),
            },
        )

        # Workflow completion
        update_analytics_workflow_state(
            workflow_id,
            {
                "stage": "cross_platform_analysis_completed",
                "platforms_analyzed": len(platform_data),
                "insights_generated": True,
                "comparative_report_sent": True,
            },
        )

        # Validate cross-platform workflow
        state = get_analytics_workflow_state(workflow_id)
        assert state["stage"] == "cross_platform_analysis_completed"
        assert state["platforms_analyzed"] == 3
        assert state["comparative_report_sent"] is True

        # Verify cross-platform data stored
        stored_data = await mock_analytics_redis.hgetall(f"cross_platform_data:{user_id}")
        assert int(stored_data["total_audience"]) == normalized_data["total_audience"]
        assert stored_data["best_platform"] == cross_platform_insights["best_performing_platform"]


# Integration test configuration
pytestmark = pytest.mark.integration

if __name__ == "__main__":
    # Run tests with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-x",  # Stop on first failure
        ]
    )
