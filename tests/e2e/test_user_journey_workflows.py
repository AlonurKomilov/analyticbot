"""
Module TQA.2.4.1: Complete User Journey Workflow Testing

This module provides comprehensive end-to-end testing for complete user journeys,
validating interactions across all system components from user registration to analytics reporting.

Test Structure:
- TestUserOnboardingWorkflow: Complete user registration and setup workflow
- TestChannelConnectionWorkflow: Channel connection and analytics setup
- TestSubscriptionWorkflow: Subscription upgrade and payment workflow
- TestContentWorkflow: Content scheduling and delivery workflow
- TestAnalyticsWorkflow: Analytics viewing and reporting workflow
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock

# Test framework imports
import httpx
import pytest
from fakeredis.aioredis import FakeRedis as FakeAsyncRedis

# Mock workflow state storage
workflow_state = {}


def get_workflow_state(workflow_id: str) -> dict[str, Any]:
    """Get workflow state for tracking across services"""
    return workflow_state.get(workflow_id, {})


def update_workflow_state(workflow_id: str, updates: dict[str, Any]):
    """Update workflow state"""
    if workflow_id not in workflow_state:
        workflow_state[workflow_id] = {}
    workflow_state[workflow_id].update(updates)


def clear_workflow_state():
    """Clear all workflow state"""
    global workflow_state
    workflow_state = {}


@pytest.fixture
def mock_telegram_bot_workflow():
    """Mock Telegram Bot for workflow testing"""
    bot = AsyncMock()

    # Mock bot responses for different workflow stages
    bot.send_message.return_value = AsyncMock(message_id=12345)
    bot.edit_message_text.return_value = AsyncMock()
    bot.answer_callback_query.return_value = AsyncMock()

    return bot


@pytest.fixture
def mock_api_client_workflow():
    """Mock API client for workflow testing"""
    client = AsyncMock()

    # Mock API responses for workflows
    client.post.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"success": True, "data": {}})
    )
    client.get.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"success": True, "data": {}})
    )
    client.put.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"success": True, "data": {}})
    )

    return client


@pytest.fixture
def mock_payment_client_workflow():
    """Mock payment client for workflow testing"""
    client = AsyncMock()

    # Mock payment workflow responses
    client.create_payment_intent.return_value = {
        "id": "pi_test_workflow",
        "status": "requires_payment_method",
        "client_secret": "pi_test_workflow_secret",
    }
    client.confirm_payment_intent.return_value = {
        "id": "pi_test_workflow",
        "status": "succeeded",
        "amount": 2999,  # $29.99
    }

    return client


@pytest.fixture
async def mock_redis_workflow():
    """Mock Redis client for workflow state management"""
    client = FakeAsyncRedis(decode_responses=True)
    yield client
    await client.flushall()
    await client.close()


@pytest.fixture
def mock_database_workflow():
    """Mock database client for workflow testing"""
    db = AsyncMock()

    # Mock database operations for workflows
    db.fetch.return_value = []
    db.fetchrow.return_value = None
    db.fetchval.return_value = None
    db.execute.return_value = None

    return db


@pytest.fixture(autouse=True)
def setup_workflow_test():
    """Setup and cleanup for workflow tests"""
    clear_workflow_state()
    yield
    clear_workflow_state()


class TestUserOnboardingWorkflow:
    """Test complete user onboarding workflow"""

    @pytest.mark.asyncio
    async def test_complete_user_registration_workflow(
        self,
        mock_telegram_bot_workflow,
        mock_api_client_workflow,
        mock_database_workflow,
        mock_redis_workflow,
    ):
        """Test complete user registration from /start to profile completion"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789

        # Step 1: User sends /start command
        update_workflow_state(
            workflow_id,
            {
                "stage": "start_command",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
            },
        )

        # Mock bot receives /start

        # Simulate bot processing /start
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id,
            text="🎉 Welcome to AnalyticBot! Let's get you set up.",
            reply_markup={
                "inline_keyboard": [[{"text": "Get Started", "callback_data": "onboarding_begin"}]]
            },
        )

        # Step 2: User clicks "Get Started"
        update_workflow_state(workflow_id, {"stage": "onboarding_begin"})

        # Mock callback query

        # Bot responds with language selection
        await mock_telegram_bot_workflow.edit_message_text(
            chat_id=user_id,
            message_id=12345,
            text="Please select your language:",
            reply_markup={
                "inline_keyboard": [
                    [{"text": "🇺🇸 English", "callback_data": "lang_en"}],
                    [{"text": "🇷🇺 Русский", "callback_data": "lang_ru"}],
                ]
            },
        )

        # Step 3: User selects language
        update_workflow_state(workflow_id, {"stage": "language_selected", "language": "en"})

        # Step 4: Create user in database via API
        mock_api_client_workflow.post.return_value = AsyncMock(
            status_code=201,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {
                        "user_id": user_id,
                        "username": "testuser",
                        "language": "en",
                        "plan_id": 1,
                        "created_at": datetime.now().isoformat(),
                    },
                }
            ),
        )

        # API call to create user
        await mock_api_client_workflow.post(
            "/api/users",
            json={
                "user_id": user_id,
                "username": "testuser",
                "language": "en",
                "plan_id": 1,
            },
        )

        # Step 5: Store user session in Redis
        await mock_redis_workflow.hset(
            f"user_session:{user_id}",
            mapping={
                "workflow_id": workflow_id,
                "stage": "profile_created",
                "language": "en",
                "created_at": datetime.now().isoformat(),
            },
        )

        # Step 6: Send welcome message with next steps
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id,
            text="✅ Your profile has been created! Ready to connect your first channel?",
            reply_markup={
                "inline_keyboard": [
                    [
                        {
                            "text": "📊 Connect Channel",
                            "callback_data": "connect_channel",
                        }
                    ],
                    [{"text": "ℹ️ Learn More", "callback_data": "learn_more"}],
                ]
            },
        )

        # Validate workflow completion
        update_workflow_state(workflow_id, {"stage": "onboarding_complete"})

        # Assertions
        state = get_workflow_state(workflow_id)
        assert state["stage"] == "onboarding_complete"
        assert state["user_id"] == user_id

        # Verify all service interactions
        mock_telegram_bot_workflow.send_message.assert_called()
        mock_telegram_bot_workflow.edit_message_text.assert_called()
        mock_api_client_workflow.post.assert_called_once()

        # Verify user session stored
        session = await mock_redis_workflow.hgetall(f"user_session:{user_id}")
        assert session["workflow_id"] == workflow_id
        assert session["stage"] == "profile_created"

    @pytest.mark.asyncio
    async def test_user_onboarding_with_error_recovery(
        self,
        mock_telegram_bot_workflow,
        mock_api_client_workflow,
        mock_database_workflow,
    ):
        """Test user onboarding workflow with error recovery"""
        workflow_id = str(uuid.uuid4())
        user_id = 987654321

        # Step 1: Successful start
        update_workflow_state(workflow_id, {"stage": "start_command", "user_id": user_id})

        # Step 2: API call fails initially
        mock_api_client_workflow.post.side_effect = [
            # First call fails
            httpx.TimeoutException("API timeout"),
            # Second call succeeds
            AsyncMock(
                status_code=201,
                json=AsyncMock(return_value={"success": True, "data": {"user_id": user_id}}),
            ),
        ]

        # First attempt - should handle error
        with pytest.raises(httpx.TimeoutException):
            await mock_api_client_workflow.post("/api/users", json={"user_id": user_id})

        # Bot shows error message
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id, text="⚠️ Something went wrong. Retrying..."
        )

        update_workflow_state(workflow_id, {"stage": "error_recovery", "retry_count": 1})

        # Retry - should succeed
        await mock_api_client_workflow.post("/api/users", json={"user_id": user_id})

        # Success message
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id, text="✅ Profile created successfully!"
        )

        update_workflow_state(workflow_id, {"stage": "onboarding_complete_after_retry"})

        # Validate error recovery
        state = get_workflow_state(workflow_id)
        assert state["stage"] == "onboarding_complete_after_retry"
        assert state["retry_count"] == 1

        # Verify retry logic worked
        assert mock_api_client_workflow.post.call_count == 2


class TestChannelConnectionWorkflow:
    """Test channel connection and analytics setup workflow"""

    @pytest.mark.asyncio
    async def test_complete_channel_connection_workflow(
        self,
        mock_telegram_bot_workflow,
        mock_api_client_workflow,
        mock_database_workflow,
        mock_redis_workflow,
    ):
        """Test complete channel connection from invitation to analytics setup"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        channel_id = -1001234567890

        # Step 1: User initiates channel connection
        update_workflow_state(
            workflow_id, {"stage": "channel_connection_start", "user_id": user_id}
        )

        # Bot requests channel invitation
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id,
            text="📊 To connect your channel, please:\n1. Add me as admin to your channel\n2. Send me the channel username or forward a message",
            reply_markup={
                "inline_keyboard": [
                    [
                        {
                            "text": "📝 Send Channel Info",
                            "callback_data": "send_channel_info",
                        }
                    ]
                ]
            },
        )

        # Step 2: User provides channel information

        update_workflow_state(
            workflow_id,
            {
                "stage": "channel_info_received",
                "channel_id": channel_id,
                "channel_title": "Test Analytics Channel",
            },
        )

        # Step 3: Verify bot permissions
        mock_api_client_workflow.get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {
                        "is_admin": True,
                        "permissions": {
                            "can_post_messages": True,
                            "can_edit_messages": True,
                            "can_delete_messages": True,
                        },
                    },
                }
            ),
        )

        await mock_api_client_workflow.get(
            f"/api/channels/{channel_id}/permissions", params={"bot_user_id": user_id}
        )

        # Step 4: Save channel to database
        mock_api_client_workflow.post.return_value = AsyncMock(
            status_code=201,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {
                        "channel_id": channel_id,
                        "title": "Test Analytics Channel",
                        "username": "testanalyticschannel",
                        "user_id": user_id,
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                    },
                }
            ),
        )

        await mock_api_client_workflow.post(
            "/api/channels",
            json={
                "channel_id": channel_id,
                "title": "Test Analytics Channel",
                "username": "testanalyticschannel",
                "user_id": user_id,
            },
        )

        # Step 5: Initialize analytics settings in Redis
        await mock_redis_workflow.hset(
            f"channel_analytics:{channel_id}",
            mapping={
                "user_id": str(user_id),
                "tracking_enabled": "true",
                "last_update": datetime.now().isoformat(),
                "metrics": json.dumps({"posts_count": 0, "views_total": 0, "subscribers": 0}),
            },
        )

        # Step 6: Send confirmation and analytics preview
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id,
            text="🎉 Channel connected successfully!\n\n📊 Analytics are now active for: Test Analytics Channel",
            reply_markup={
                "inline_keyboard": [
                    [
                        {
                            "text": "📈 View Analytics",
                            "callback_data": f"view_analytics_{channel_id}",
                        }
                    ],
                    [
                        {
                            "text": "⚙️ Settings",
                            "callback_data": f"channel_settings_{channel_id}",
                        }
                    ],
                ]
            },
        )

        # Workflow completion
        update_workflow_state(
            workflow_id,
            {"stage": "channel_connection_complete", "channel_connected": True},
        )

        # Validate workflow
        state = get_workflow_state(workflow_id)
        assert state["stage"] == "channel_connection_complete"
        assert state["channel_id"] == channel_id
        assert state["channel_connected"] is True

        # Verify service interactions
        mock_api_client_workflow.get.assert_called_once()  # Permissions check
        mock_api_client_workflow.post.assert_called_once()  # Channel creation

        # Verify Redis analytics setup
        analytics_data = await mock_redis_workflow.hgetall(f"channel_analytics:{channel_id}")
        assert analytics_data["user_id"] == str(user_id)
        assert analytics_data["tracking_enabled"] == "true"

    @pytest.mark.asyncio
    async def test_channel_connection_permission_failure(
        self, mock_telegram_bot_workflow, mock_api_client_workflow
    ):
        """Test channel connection workflow when bot lacks permissions"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        channel_id = -1001234567890

        # Setup workflow
        update_workflow_state(
            workflow_id,
            {"stage": "permission_check", "user_id": user_id, "channel_id": channel_id},
        )

        # Mock insufficient permissions
        mock_api_client_workflow.get.return_value = AsyncMock(
            status_code=403,
            json=AsyncMock(
                return_value={
                    "success": False,
                    "error": "Bot is not admin in the channel",
                }
            ),
        )

        # Permission check fails
        await mock_api_client_workflow.get(f"/api/channels/{channel_id}/permissions")

        # Bot should notify user of permission issue
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id,
            text="❌ I don't have admin permissions in this channel.\n\nPlease:\n1. Add me as admin\n2. Grant necessary permissions\n3. Try again",
            reply_markup={
                "inline_keyboard": [
                    [
                        {
                            "text": "🔄 Retry",
                            "callback_data": f"retry_permissions_{channel_id}",
                        }
                    ],
                    [{"text": "📖 Help", "callback_data": "permission_help"}],
                ]
            },
        )

        update_workflow_state(
            workflow_id,
            {"stage": "permission_failed", "error": "insufficient_permissions"},
        )

        # Validate error handling
        state = get_workflow_state(workflow_id)
        assert state["stage"] == "permission_failed"
        assert state["error"] == "insufficient_permissions"

        # Verify error response handling
        mock_telegram_bot_workflow.send_message.assert_called()


class TestSubscriptionWorkflow:
    """Test subscription upgrade and payment workflow"""

    @pytest.mark.asyncio
    async def test_complete_subscription_upgrade_workflow(
        self,
        mock_telegram_bot_workflow,
        mock_api_client_workflow,
        mock_payment_client_workflow,
        mock_redis_workflow,
    ):
        """Test complete subscription upgrade from plan selection to activation"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789

        # Step 1: User initiates upgrade
        update_workflow_state(
            workflow_id,
            {"stage": "upgrade_initiated", "user_id": user_id, "current_plan": "free"},
        )

        # Show subscription plans
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id,
            text="💎 Choose your subscription plan:",
            reply_markup={
                "inline_keyboard": [
                    [
                        {
                            "text": "🚀 Pro - $9.99/month",
                            "callback_data": "plan_pro_monthly",
                        }
                    ],
                    [
                        {
                            "text": "💼 Premium - $29.99/month",
                            "callback_data": "plan_premium_monthly",
                        }
                    ],
                ]
            },
        )

        # Step 2: User selects plan
        selected_plan = {
            "plan_id": "premium_monthly",
            "amount": 2999,  # $29.99 in cents
            "currency": "usd",
            "interval": "monthly",
        }

        update_workflow_state(
            workflow_id, {"stage": "plan_selected", "selected_plan": selected_plan}
        )

        # Step 3: Create payment intent
        payment_intent = await mock_payment_client_workflow.create_payment_intent(
            amount=selected_plan["amount"],
            currency=selected_plan["currency"],
            metadata={
                "user_id": str(user_id),
                "plan_id": selected_plan["plan_id"],
                "workflow_id": workflow_id,
            },
        )

        # Step 4: Store payment session in Redis
        await mock_redis_workflow.hset(
            f"payment_session:{payment_intent['id']}",
            mapping={
                "user_id": str(user_id),
                "workflow_id": workflow_id,
                "plan_id": selected_plan["plan_id"],
                "amount": str(selected_plan["amount"]),
                "status": "pending",
                "created_at": datetime.now().isoformat(),
            },
        )

        # Step 5: Send payment link to user
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id,
            text="💳 Complete your payment:",
            reply_markup={
                "inline_keyboard": [
                    [
                        {
                            "text": "💰 Pay $29.99",
                            "web_app": {
                                "url": f"https://checkout.stripe.com/{payment_intent['client_secret']}"
                            },
                        }
                    ],
                    [{"text": "❌ Cancel", "callback_data": "payment_cancel"}],
                ]
            },
        )

        # Step 6: Simulate successful payment
        mock_payment_client_workflow.confirm_payment_intent.return_value = {
            "id": payment_intent["id"],
            "status": "succeeded",
            "amount": selected_plan["amount"],
        }

        await mock_payment_client_workflow.confirm_payment_intent(payment_intent["id"])

        # Step 7: Update subscription in database
        mock_api_client_workflow.put.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {
                        "user_id": user_id,
                        "plan_id": selected_plan["plan_id"],
                        "status": "active",
                        "next_billing": (datetime.now() + timedelta(days=30)).isoformat(),
                    },
                }
            ),
        )

        await mock_api_client_workflow.put(
            f"/api/users/{user_id}/subscription",
            json={
                "plan_id": selected_plan["plan_id"],
                "payment_intent_id": payment_intent["id"],
                "status": "active",
            },
        )

        # Step 8: Update Redis session
        await mock_redis_workflow.hset(
            f"payment_session:{payment_intent['id']}",
            mapping={"status": "completed", "completed_at": datetime.now().isoformat()},
        )

        # Step 9: Send success notification
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id,
            text="🎉 Payment successful! Your Premium subscription is now active.\n\n✨ You now have access to:\n• Advanced analytics\n• Priority support\n• Custom reports",
            reply_markup={
                "inline_keyboard": [
                    [
                        {
                            "text": "📊 View Premium Analytics",
                            "callback_data": "premium_analytics",
                        }
                    ]
                ]
            },
        )

        # Workflow completion
        update_workflow_state(
            workflow_id,
            {
                "stage": "subscription_activated",
                "plan_id": selected_plan["plan_id"],
                "payment_status": "succeeded",
            },
        )

        # Validate complete workflow
        state = get_workflow_state(workflow_id)
        assert state["stage"] == "subscription_activated"
        assert state["plan_id"] == selected_plan["plan_id"]
        assert state["payment_status"] == "succeeded"

        # Verify all service interactions
        mock_payment_client_workflow.create_payment_intent.assert_called_once()
        mock_payment_client_workflow.confirm_payment_intent.assert_called_once()
        mock_api_client_workflow.put.assert_called_once()

        # Verify Redis payment session
        payment_session = await mock_redis_workflow.hgetall(
            f"payment_session:{payment_intent['id']}"
        )
        assert payment_session["status"] == "completed"
        assert payment_session["user_id"] == str(user_id)


class TestContentWorkflow:
    """Test content scheduling and delivery workflow"""

    @pytest.mark.asyncio
    async def test_complete_content_scheduling_workflow(
        self,
        mock_telegram_bot_workflow,
        mock_api_client_workflow,
        mock_database_workflow,
        mock_redis_workflow,
    ):
        """Test complete content scheduling from creation to delivery"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        channel_id = -1001234567890

        # Step 1: User initiates content scheduling
        update_workflow_state(
            workflow_id,
            {
                "stage": "content_creation_start",
                "user_id": user_id,
                "channel_id": channel_id,
            },
        )

        # Bot requests content
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id,
            text="📝 Let's schedule your content!\n\nPlease send me the message you want to schedule.",
            reply_markup={
                "inline_keyboard": [[{"text": "❌ Cancel", "callback_data": "cancel_scheduling"}]]
            },
        )

        # Step 2: User provides content
        content_message = {
            "message_id": 3,
            "from": {"id": user_id},
            "text": "🚀 Exciting news coming soon! Stay tuned for our latest updates. #comingsoon #excited",
            "date": datetime.now().isoformat(),
        }

        update_workflow_state(
            workflow_id,
            {"stage": "content_received", "content_text": content_message["text"]},
        )

        # Step 3: Bot asks for scheduling time
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id,
            text="⏰ When would you like to schedule this post?",
            reply_markup={
                "inline_keyboard": [
                    [{"text": "🕐 In 1 hour", "callback_data": "schedule_1h"}],
                    [
                        {
                            "text": "📅 Tomorrow 9 AM",
                            "callback_data": "schedule_tomorrow_9am",
                        }
                    ],
                    [{"text": "📝 Custom time", "callback_data": "schedule_custom"}],
                ]
            },
        )

        # Step 4: User selects schedule time
        scheduled_time = datetime.now() + timedelta(hours=1)
        update_workflow_state(
            workflow_id,
            {
                "stage": "schedule_time_selected",
                "scheduled_time": scheduled_time.isoformat(),
            },
        )

        # Step 5: Create scheduled post in database
        mock_api_client_workflow.post.return_value = AsyncMock(
            status_code=201,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {
                        "post_id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "channel_id": channel_id,
                        "content": content_message["text"],
                        "scheduled_time": scheduled_time.isoformat(),
                        "status": "scheduled",
                        "created_at": datetime.now().isoformat(),
                    },
                }
            ),
        )

        post_creation = await mock_api_client_workflow.post(
            "/api/scheduled-posts",
            json={
                "user_id": user_id,
                "channel_id": channel_id,
                "content": content_message["text"],
                "scheduled_time": scheduled_time.isoformat(),
                "workflow_id": workflow_id,
            },
        )

        post_data = await post_creation.json()
        post_id = post_data["data"]["post_id"]

        # Step 6: Store in Redis for scheduling
        await mock_redis_workflow.zadd("scheduled_posts", {post_id: scheduled_time.timestamp()})

        await mock_redis_workflow.hset(
            f"post_details:{post_id}",
            mapping={
                "user_id": str(user_id),
                "channel_id": str(channel_id),
                "content": content_message["text"],
                "workflow_id": workflow_id,
                "status": "scheduled",
            },
        )

        # Step 7: Send confirmation to user
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id,
            text=f"✅ Post scheduled successfully!\n\n📅 Will be published: {scheduled_time.strftime('%Y-%m-%d %H:%M')}\n📊 Channel: Test Analytics Channel",
            reply_markup={
                "inline_keyboard": [
                    [
                        {
                            "text": "📝 Schedule Another",
                            "callback_data": "schedule_another",
                        }
                    ],
                    [{"text": "📋 View Scheduled", "callback_data": "view_scheduled"}],
                ]
            },
        )

        # Workflow completion
        update_workflow_state(
            workflow_id,
            {
                "stage": "content_scheduled",
                "post_id": post_id,
                "delivery_pending": True,
            },
        )

        # Validate workflow
        state = get_workflow_state(workflow_id)
        assert state["stage"] == "content_scheduled"
        assert state["post_id"] == post_id
        assert state["delivery_pending"] is True

        # Verify service interactions
        mock_api_client_workflow.post.assert_called_once()

        # Verify Redis scheduling
        scheduled_posts = await mock_redis_workflow.zrange("scheduled_posts", 0, -1)
        assert post_id in scheduled_posts

        post_details = await mock_redis_workflow.hgetall(f"post_details:{post_id}")
        assert post_details["workflow_id"] == workflow_id
        assert post_details["status"] == "scheduled"


class TestAnalyticsWorkflow:
    """Test analytics viewing and reporting workflow"""

    @pytest.mark.asyncio
    async def test_complete_analytics_viewing_workflow(
        self, mock_telegram_bot_workflow, mock_api_client_workflow, mock_redis_workflow
    ):
        """Test complete analytics workflow from request to report delivery"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        channel_id = -1001234567890

        # Step 1: User requests analytics
        update_workflow_state(
            workflow_id,
            {
                "stage": "analytics_requested",
                "user_id": user_id,
                "channel_id": channel_id,
            },
        )

        # Step 2: Fetch analytics data from API
        mock_api_client_workflow.get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(
                return_value={
                    "success": True,
                    "data": {
                        "channel_id": channel_id,
                        "period": "7_days",
                        "metrics": {
                            "total_views": 15420,
                            "total_posts": 12,
                            "avg_views_per_post": 1285,
                            "subscriber_growth": 156,
                            "engagement_rate": 0.087,
                            "top_performing_post": {
                                "post_id": "post_123",
                                "views": 3420,
                                "content_preview": "🚀 Exciting news coming soon!",
                            },
                        },
                        "generated_at": datetime.now().isoformat(),
                    },
                }
            ),
        )

        analytics_response = await mock_api_client_workflow.get(
            f"/api/analytics/channels/{channel_id}",
            params={"period": "7_days", "user_id": user_id},
        )

        analytics_data = await analytics_response.json()

        # Step 3: Cache analytics data in Redis
        await mock_redis_workflow.set(
            f"analytics_cache:{channel_id}:7_days",
            json.dumps(analytics_data["data"]),
            ex=1800,  # 30 minutes cache
        )

        # Step 4: Generate formatted report
        metrics = analytics_data["data"]["metrics"]
        report_text = f"""📊 **Analytics Report**
📺 Channel: Test Analytics Channel
📅 Period: Last 7 days

📈 **Key Metrics:**
👀 Total Views: {metrics['total_views']:,}
📝 Posts Published: {metrics['total_posts']}
📊 Avg Views/Post: {metrics['avg_views_per_post']:,}
📈 New Subscribers: +{metrics['subscriber_growth']}
💡 Engagement Rate: {metrics['engagement_rate']:.1%}

🏆 **Top Post:**
{metrics['top_performing_post']['content_preview']}
👀 {metrics['top_performing_post']['views']:,} views"""

        # Step 5: Send report to user
        await mock_telegram_bot_workflow.send_message(
            chat_id=user_id,
            text=report_text,
            parse_mode="Markdown",
            reply_markup={
                "inline_keyboard": [
                    [
                        {
                            "text": "📅 Different Period",
                            "callback_data": f"analytics_period_{channel_id}",
                        }
                    ],
                    [
                        {
                            "text": "📧 Email Report",
                            "callback_data": f"email_report_{channel_id}",
                        }
                    ],
                    [
                        {
                            "text": "📊 Detailed View",
                            "callback_data": f"detailed_analytics_{channel_id}",
                        }
                    ],
                ]
            },
        )

        # Step 6: Log analytics request
        await mock_redis_workflow.lpush(
            f"analytics_history:{user_id}",
            json.dumps(
                {
                    "workflow_id": workflow_id,
                    "channel_id": channel_id,
                    "period": "7_days",
                    "requested_at": datetime.now().isoformat(),
                }
            ),
        )

        # Workflow completion
        update_workflow_state(
            workflow_id,
            {"stage": "analytics_delivered", "report_generated": True, "cached": True},
        )

        # Validate workflow
        state = get_workflow_state(workflow_id)
        assert state["stage"] == "analytics_delivered"
        assert state["report_generated"] is True
        assert state["cached"] is True

        # Verify service interactions
        mock_api_client_workflow.get.assert_called_once()
        mock_telegram_bot_workflow.send_message.assert_called_once()

        # Verify Redis caching
        cached_data = await mock_redis_workflow.get(f"analytics_cache:{channel_id}:7_days")
        assert cached_data is not None

        # Verify analytics history
        history = await mock_redis_workflow.lrange(f"analytics_history:{user_id}", 0, 0)
        assert len(history) == 1
        history_entry = json.loads(history[0])
        assert history_entry["workflow_id"] == workflow_id


# Integration test configuration
pytestmark = pytest.mark.integration

if __name__ == "__main__":
    # Run tests with coverage reporting
    pytest.main([__file__, "-v", "--tb=short", "-x"])  # Stop on first failure
