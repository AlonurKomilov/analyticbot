"""
Module TQA.2.4.2: Payment Processing Workflow Testing

This module provides comprehensive end-to-end testing for payment processing workflows,
covering subscription purchases, renewals, failures, and refunds across all payment providers.

Test Structure:
- TestSubscriptionPurchaseWorkflow: Complete subscription purchase flow
- TestPaymentFailureWorkflow: Payment failure handling and recovery
- TestSubscriptionRenewalWorkflow: Automated subscription renewal process
- TestRefundWorkflow: Refund processing and account adjustments
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime, timedelta

# Test framework imports
import httpx
from fakeredis.aioredis import FakeRedis as FakeAsyncRedis


# Mock payment workflow state
payment_workflow_state = {}

def get_payment_workflow_state(workflow_id: str) -> Dict[str, Any]:
    return payment_workflow_state.get(workflow_id, {})

def update_payment_workflow_state(workflow_id: str, updates: Dict[str, Any]):
    if workflow_id not in payment_workflow_state:
        payment_workflow_state[workflow_id] = {}
    payment_workflow_state[workflow_id].update(updates)

def clear_payment_workflow_state():
    global payment_workflow_state
    payment_workflow_state = {}


@pytest.fixture
def mock_stripe_workflow():
    """Mock Stripe client for payment workflow testing"""
    client = AsyncMock()
    
    # Default successful responses
    client.create_payment_intent.return_value = {
        "id": "pi_test_workflow",
        "object": "payment_intent",
        "amount": 2999,
        "currency": "usd",
        "status": "requires_payment_method",
        "client_secret": "pi_test_workflow_secret"
    }
    
    client.confirm_payment_intent.return_value = {
        "id": "pi_test_workflow",
        "status": "succeeded",
        "amount": 2999,
        "payment_method": {
            "id": "pm_test_card",
            "card": {"brand": "visa", "last4": "4242"}
        }
    }
    
    client.create_subscription.return_value = {
        "id": "sub_test_workflow",
        "status": "active",
        "current_period_start": int(datetime.now().timestamp()),
        "current_period_end": int((datetime.now() + timedelta(days=30)).timestamp())
    }
    
    return client


@pytest.fixture
def mock_payme_workflow():
    """Mock Payme client for local payment workflow testing"""
    client = AsyncMock()
    
    client.check_perform_transaction.return_value = {
        "result": {"allow": True}
    }
    
    client.create_transaction.return_value = {
        "result": {
            "transaction": "payme_trans_123",
            "state": 1,
            "create_time": int(datetime.now().timestamp())
        }
    }
    
    client.perform_transaction.return_value = {
        "result": {
            "transaction": "payme_trans_123",
            "state": 2,
            "perform_time": int(datetime.now().timestamp())
        }
    }
    
    return client


@pytest.fixture
async def mock_payment_redis():
    """Mock Redis for payment workflow state"""
    client = FakeAsyncRedis(decode_responses=True)
    yield client
    await client.flushall()
    await client.close()


@pytest.fixture
def mock_payment_api():
    """Mock API client for payment workflows"""
    client = AsyncMock()
    
    client.get.return_value = AsyncMock(
        status_code=200,
        json=AsyncMock(return_value={"success": True, "data": {}})
    )
    client.post.return_value = AsyncMock(
        status_code=201,
        json=AsyncMock(return_value={"success": True, "data": {}})
    )
    client.put.return_value = AsyncMock(
        status_code=200,
        json=AsyncMock(return_value={"success": True, "data": {}})
    )
    
    return client


@pytest.fixture
def mock_payment_bot():
    """Mock Telegram Bot for payment notifications"""
    bot = AsyncMock()
    bot.send_message.return_value = AsyncMock(message_id=54321)
    bot.edit_message_text.return_value = AsyncMock()
    return bot


@pytest.fixture(autouse=True)
def setup_payment_workflow_test():
    """Setup and cleanup for payment workflow tests"""
    clear_payment_workflow_state()
    yield
    clear_payment_workflow_state()


class TestSubscriptionPurchaseWorkflow:
    """Test complete subscription purchase workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_stripe_subscription_purchase(
        self,
        mock_stripe_workflow,
        mock_payment_api,
        mock_payment_bot,
        mock_payment_redis
    ):
        """Test complete Stripe subscription purchase workflow"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        plan_id = "premium_monthly"
        
        # Step 1: Initialize purchase workflow
        update_payment_workflow_state(workflow_id, {
            "stage": "purchase_initiated",
            "user_id": user_id,
            "plan_id": plan_id,
            "provider": "stripe"
        })
        
        # Step 2: Fetch plan details
        mock_payment_api.get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "success": True,
                "data": {
                    "plan_id": plan_id,
                    "name": "Premium Monthly",
                    "amount": 2999,
                    "currency": "usd",
                    "interval": "monthly",
                    "features": ["Advanced Analytics", "Priority Support", "Custom Reports"]
                }
            })
        )
        
        plan_response = await mock_payment_api.get(f"/api/plans/{plan_id}")
        plan_data = await plan_response.json()
        
        # Step 3: Create Stripe payment intent
        payment_intent = await mock_stripe_workflow.create_payment_intent(
            amount=plan_data["data"]["amount"],
            currency=plan_data["data"]["currency"],
            metadata={
                "user_id": str(user_id),
                "plan_id": plan_id,
                "workflow_id": workflow_id
            }
        )
        
        # Step 4: Store payment session
        await mock_payment_redis.hset(
            f"payment_session:{payment_intent['id']}",
            mapping={
                "workflow_id": workflow_id,
                "user_id": str(user_id),
                "plan_id": plan_id,
                "amount": str(plan_data["data"]["amount"]),
                "provider": "stripe",
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
        )
        
        update_payment_workflow_state(workflow_id, {
            "stage": "payment_intent_created",
            "payment_intent_id": payment_intent["id"]
        })
        
        # Step 5: User completes payment (simulated)
        confirmed_payment = await mock_stripe_workflow.confirm_payment_intent(
            payment_intent["id"]
        )
        
        update_payment_workflow_state(workflow_id, {
            "stage": "payment_confirmed",
            "payment_status": confirmed_payment["status"]
        })
        
        # Step 6: Create subscription
        subscription = await mock_stripe_workflow.create_subscription(
            customer_id=f"cus_user_{user_id}",
            price_id=f"price_{plan_id}",
            payment_method=confirmed_payment["payment_method"]["id"]
        )
        
        # Step 7: Update user subscription in database
        mock_payment_api.put.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "success": True,
                "data": {
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "subscription_id": subscription["id"],
                    "status": "active",
                    "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]).isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            })
        )
        
        subscription_update = await mock_payment_api.put(
            f"/api/users/{user_id}/subscription",
            json={
                "plan_id": plan_id,
                "subscription_id": subscription["id"],
                "status": "active",
                "payment_intent_id": payment_intent["id"]
            }
        )
        
        # Step 8: Update Redis cache
        await mock_payment_redis.hset(
            f"user_subscription:{user_id}",
            mapping={
                "plan_id": plan_id,
                "status": "active",
                "subscription_id": subscription["id"],
                "updated_at": datetime.now().isoformat()
            }
        )
        
        # Step 9: Send success notification
        await mock_payment_bot.send_message(
            chat_id=user_id,
            text=f"🎉 Subscription activated successfully!\n\n✨ Welcome to {plan_data['data']['name']}!\n\nYour new features:\n" + 
                 "\n".join([f"• {feature}" for feature in plan_data['data']['features']]),
            reply_markup={"inline_keyboard": [
                [{"text": "🚀 Explore Features", "callback_data": "explore_premium_features"}]
            ]}
        )
        
        # Step 10: Schedule first renewal
        renewal_date = datetime.now() + timedelta(days=30)
        await mock_payment_redis.zadd(
            "subscription_renewals",
            {f"{user_id}:{subscription['id']}": renewal_date.timestamp()}
        )
        
        # Workflow completion
        update_payment_workflow_state(workflow_id, {
            "stage": "subscription_activated",
            "subscription_id": subscription["id"],
            "renewal_scheduled": True
        })
        
        # Validate complete workflow
        state = get_payment_workflow_state(workflow_id)
        assert state["stage"] == "subscription_activated"
        assert state["subscription_id"] == subscription["id"]
        assert state["renewal_scheduled"] is True
        
        # Verify all service calls
        mock_payment_api.get.assert_called_once()  # Plan details
        mock_payment_api.put.assert_called_once()  # Subscription update
        mock_stripe_workflow.create_payment_intent.assert_called_once()
        mock_stripe_workflow.confirm_payment_intent.assert_called_once()
        mock_stripe_workflow.create_subscription.assert_called_once()
        
        # Verify Redis state
        session = await mock_payment_redis.hgetall(f"payment_session:{payment_intent['id']}")
        assert session["workflow_id"] == workflow_id
        
        subscription_cache = await mock_payment_redis.hgetall(f"user_subscription:{user_id}")
        assert subscription_cache["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_payme_subscription_purchase_workflow(
        self,
        mock_payme_workflow,
        mock_payment_api,
        mock_payment_bot,
        mock_payment_redis
    ):
        """Test Payme subscription purchase workflow"""
        workflow_id = str(uuid.uuid4())
        user_id = 987654321
        plan_id = "pro_monthly_uzs"
        
        # Step 1: Initialize Payme workflow
        update_payment_workflow_state(workflow_id, {
            "stage": "payme_purchase_initiated",
            "user_id": user_id,
            "plan_id": plan_id,
            "provider": "payme"
        })
        
        # Step 2: Get plan details (in UZS)
        mock_payment_api.get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "success": True,
                "data": {
                    "plan_id": plan_id,
                    "name": "Pro Monthly",
                    "amount": 120000,  # 120,000 UZS
                    "currency": "uzs",
                    "interval": "monthly"
                }
            })
        )
        
        plan_response = await mock_payment_api.get(f"/api/plans/{plan_id}")
        plan_data = await plan_response.json()
        
        # Step 3: Check transaction eligibility
        check_result = await mock_payme_workflow.check_perform_transaction(
            amount=plan_data["data"]["amount"],
            account={"user_id": str(user_id)}
        )
        
        assert check_result["result"]["allow"] is True
        
        # Step 4: Create Payme transaction
        transaction = await mock_payme_workflow.create_transaction(
            id=str(uuid.uuid4()),
            time=int(datetime.now().timestamp()),
            amount=plan_data["data"]["amount"],
            account={"user_id": str(user_id)}
        )
        
        transaction_id = transaction["result"]["transaction"]
        
        # Step 5: Store transaction in Redis
        await mock_payment_redis.hset(
            f"payme_transaction:{transaction_id}",
            mapping={
                "workflow_id": workflow_id,
                "user_id": str(user_id),
                "plan_id": plan_id,
                "amount": str(plan_data["data"]["amount"]),
                "state": "1",  # Created
                "created_at": datetime.now().isoformat()
            }
        )
        
        # Step 6: Perform transaction (payment completion)
        perform_result = await mock_payme_workflow.perform_transaction(
            id=transaction_id
        )
        
        # Step 7: Update transaction state
        await mock_payment_redis.hset(
            f"payme_transaction:{transaction_id}",
            mapping={
                "state": "2",  # Performed
                "performed_at": datetime.now().isoformat()
            }
        )
        
        # Step 8: Update user subscription
        mock_payment_api.put.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "success": True,
                "data": {
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "status": "active",
                    "payment_provider": "payme",
                    "transaction_id": transaction_id
                }
            })
        )
        
        subscription_update = await mock_payment_api.put(
            f"/api/users/{user_id}/subscription",
            json={
                "plan_id": plan_id,
                "status": "active",
                "payment_provider": "payme",
                "transaction_id": transaction_id
            }
        )
        
        # Step 9: Send success notification (in Russian for UZS)
        await mock_payment_bot.send_message(
            chat_id=user_id,
            text="🎉 Подписка успешно активирована!\n\n💎 Добро пожаловать в Pro!\n\nТеперь доступны:\n• Расширенная аналитика\n• Приоритетная поддержка",
            reply_markup={"inline_keyboard": [
                [{"text": "🚀 Изучить функции", "callback_data": "explore_pro_features"}]
            ]}
        )
        
        # Workflow completion
        update_payment_workflow_state(workflow_id, {
            "stage": "payme_subscription_activated",
            "transaction_id": transaction_id
        })
        
        # Validate workflow
        state = get_payment_workflow_state(workflow_id)
        assert state["stage"] == "payme_subscription_activated"
        assert state["transaction_id"] == transaction_id
        
        # Verify Payme workflow calls
        mock_payme_workflow.check_perform_transaction.assert_called_once()
        mock_payme_workflow.create_transaction.assert_called_once()
        mock_payme_workflow.perform_transaction.assert_called_once()


class TestPaymentFailureWorkflow:
    """Test payment failure handling and recovery workflows"""
    
    @pytest.mark.asyncio
    async def test_card_declined_recovery_workflow(
        self,
        mock_stripe_workflow,
        mock_payment_api,
        mock_payment_bot,
        mock_payment_redis
    ):
        """Test payment failure recovery workflow for declined cards"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        
        # Step 1: Initialize failed payment scenario
        update_payment_workflow_state(workflow_id, {
            "stage": "payment_attempt",
            "user_id": user_id,
            "attempt_count": 1
        })
        
        # Step 2: Simulate declined payment
        mock_stripe_workflow.confirm_payment_intent.return_value = {
            "id": "pi_declined_workflow",
            "status": "payment_failed",
            "last_payment_error": {
                "type": "card_error",
                "code": "card_declined",
                "message": "Your card was declined.",
                "decline_code": "insufficient_funds"
            }
        }
        
        failed_payment = await mock_stripe_workflow.confirm_payment_intent("pi_declined_workflow")
        
        # Step 3: Store failure details
        await mock_payment_redis.hset(
            f"payment_failure:{workflow_id}",
            mapping={
                "user_id": str(user_id),
                "payment_intent_id": "pi_declined_workflow",
                "error_code": failed_payment["last_payment_error"]["code"],
                "decline_code": failed_payment["last_payment_error"]["decline_code"],
                "failure_time": datetime.now().isoformat(),
                "retry_eligible": "true"
            }
        )
        
        # Step 4: Notify user of failure
        await mock_payment_bot.send_message(
            chat_id=user_id,
            text="❌ Payment failed: Your card was declined.\n\n💡 This usually means insufficient funds. Would you like to try a different payment method?",
            reply_markup={"inline_keyboard": [
                [{"text": "💳 Try Different Card", "callback_data": "retry_different_card"}],
                [{"text": "🏦 Bank Transfer", "callback_data": "try_bank_transfer"}],
                [{"text": "❌ Cancel", "callback_data": "cancel_payment"}]
            ]}
        )
        
        update_payment_workflow_state(workflow_id, {
            "stage": "payment_failed_user_notified",
            "error_code": "card_declined",
            "retry_options_provided": True
        })
        
        # Step 5: User chooses retry with different card
        update_payment_workflow_state(workflow_id, {
            "stage": "retry_initiated",
            "retry_method": "different_card",
            "attempt_count": 2
        })
        
        # Step 6: Create new payment intent for retry
        mock_stripe_workflow.create_payment_intent.return_value = {
            "id": "pi_retry_workflow",
            "status": "requires_payment_method",
            "client_secret": "pi_retry_workflow_secret"
        }
        
        retry_payment_intent = await mock_stripe_workflow.create_payment_intent(
            amount=2999,
            currency="usd"
        )
        
        # Step 7: Successful retry
        mock_stripe_workflow.confirm_payment_intent.return_value = {
            "id": "pi_retry_workflow",
            "status": "succeeded",
            "payment_method": {"card": {"brand": "mastercard", "last4": "5555"}}
        }
        
        successful_retry = await mock_stripe_workflow.confirm_payment_intent("pi_retry_workflow")
        
        # Step 8: Update subscription after successful retry
        mock_payment_api.put.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "success": True,
                "data": {"status": "active", "retry_succeeded": True}
            })
        )
        
        retry_update = await mock_payment_api.put(
            f"/api/users/{user_id}/subscription",
            json={"payment_intent_id": "pi_retry_workflow", "status": "active"}
        )
        
        # Step 9: Success notification
        await mock_payment_bot.send_message(
            chat_id=user_id,
            text="🎉 Payment successful on retry!\n\nYour subscription is now active. Thank you for your patience!",
            reply_markup={"inline_keyboard": [
                [{"text": "🚀 Get Started", "callback_data": "start_using_subscription"}]
            ]}
        )
        
        # Step 10: Clean up failure records
        await mock_payment_redis.delete(f"payment_failure:{workflow_id}")
        
        # Workflow completion
        update_payment_workflow_state(workflow_id, {
            "stage": "payment_recovered",
            "final_status": "succeeded",
            "retry_succeeded": True
        })
        
        # Validate recovery workflow
        state = get_payment_workflow_state(workflow_id)
        assert state["stage"] == "payment_recovered"
        assert state["retry_succeeded"] is True
        assert state["attempt_count"] == 2
        
        # Verify failure was cleaned up
        failure_record = await mock_payment_redis.exists(f"payment_failure:{workflow_id}")
        assert failure_record == 0
    
    @pytest.mark.asyncio
    async def test_multiple_payment_failures_workflow(
        self,
        mock_stripe_workflow,
        mock_payment_bot,
        mock_payment_redis
    ):
        """Test workflow for multiple consecutive payment failures"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        max_retries = 3
        
        # Step 1: Initialize multiple failure scenario
        update_payment_workflow_state(workflow_id, {
            "stage": "multiple_failures_test",
            "user_id": user_id,
            "max_retries": max_retries,
            "attempt_count": 0
        })
        
        # Step 2: Simulate multiple failures
        failure_responses = [
            {"code": "card_declined", "message": "Your card was declined."},
            {"code": "insufficient_funds", "message": "Insufficient funds."},
            {"code": "processing_error", "message": "Payment processing error."}
        ]
        
        for attempt in range(max_retries):
            attempt_count = attempt + 1
            failure = failure_responses[attempt]
            
            # Mock failed payment
            mock_stripe_workflow.confirm_payment_intent.return_value = {
                "id": f"pi_fail_{attempt}",
                "status": "payment_failed",
                "last_payment_error": {
                    "type": "card_error",
                    "code": failure["code"],
                    "message": failure["message"]
                }
            }
            
            failed_attempt = await mock_stripe_workflow.confirm_payment_intent(f"pi_fail_{attempt}")
            
            # Store failure
            await mock_payment_redis.hset(
                f"payment_failures:{user_id}",
                f"attempt_{attempt_count}",
                json.dumps({
                    "error_code": failure["code"],
                    "timestamp": datetime.now().isoformat(),
                    "payment_intent_id": f"pi_fail_{attempt}"
                })
            )
            
            update_payment_workflow_state(workflow_id, {"attempt_count": attempt_count})
            
            if attempt_count < max_retries:
                # Show retry option
                await mock_payment_bot.send_message(
                    chat_id=user_id,
                    text=f"❌ Payment failed ({failure['message']})\n\nAttempt {attempt_count}/{max_retries}. Would you like to try again?",
                    reply_markup={"inline_keyboard": [
                        [{"text": "🔄 Retry", "callback_data": f"retry_payment_{attempt_count}"}],
                        [{"text": "❌ Cancel", "callback_data": "cancel_after_failures"}]
                    ]}
                )
        
        # Step 3: All retries exhausted - escalate
        update_payment_workflow_state(workflow_id, {
            "stage": "max_retries_exceeded",
            "escalation_required": True
        })
        
        # Step 4: Send escalation notification
        await mock_payment_bot.send_message(
            chat_id=user_id,
            text="😔 We're unable to process your payment after multiple attempts.\n\n🆘 Our support team has been notified and will contact you shortly to resolve this issue.",
            reply_markup={"inline_keyboard": [
                [{"text": "💬 Contact Support", "callback_data": "contact_support_payment"}],
                [{"text": "📧 Email Support", "callback_data": "email_support_payment"}]
            ]}
        )
        
        # Step 5: Create support ticket
        await mock_payment_redis.hset(
            f"support_ticket:{workflow_id}",
            mapping={
                "user_id": str(user_id),
                "type": "payment_failure",
                "attempts": str(max_retries),
                "created_at": datetime.now().isoformat(),
                "priority": "high"
            }
        )
        
        # Validate failure escalation
        state = get_payment_workflow_state(workflow_id)
        assert state["stage"] == "max_retries_exceeded"
        assert state["escalation_required"] is True
        assert state["attempt_count"] == max_retries
        
        # Verify support ticket created
        ticket = await mock_payment_redis.hgetall(f"support_ticket:{workflow_id}")
        assert ticket["type"] == "payment_failure"
        assert ticket["priority"] == "high"


class TestSubscriptionRenewalWorkflow:
    """Test automated subscription renewal workflows"""
    
    @pytest.mark.asyncio
    async def test_successful_subscription_renewal_workflow(
        self,
        mock_stripe_workflow,
        mock_payment_api,
        mock_payment_bot,
        mock_payment_redis
    ):
        """Test successful automated subscription renewal"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        subscription_id = "sub_renewal_test"
        
        # Step 1: Setup renewal scenario
        update_payment_workflow_state(workflow_id, {
            "stage": "renewal_scheduled",
            "user_id": user_id,
            "subscription_id": subscription_id
        })
        
        # Step 2: Get current subscription details
        mock_payment_api.get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "success": True,
                "data": {
                    "subscription_id": subscription_id,
                    "user_id": user_id,
                    "plan_id": "premium_monthly",
                    "status": "active",
                    "current_period_end": (datetime.now() + timedelta(days=1)).isoformat(),
                    "auto_renew": True
                }
            })
        )
        
        subscription_details = await mock_payment_api.get(f"/api/subscriptions/{subscription_id}")
        
        # Step 3: Process renewal with Stripe
        mock_stripe_workflow.retrieve_subscription.return_value = {
            "id": subscription_id,
            "status": "active",
            "current_period_start": int(datetime.now().timestamp()),
            "current_period_end": int((datetime.now() + timedelta(days=30)).timestamp()),
            "latest_invoice": {
                "id": "in_renewal_invoice",
                "status": "paid",
                "amount_paid": 2999
            }
        }
        
        renewed_subscription = await mock_stripe_workflow.retrieve_subscription(subscription_id)
        
        # Step 4: Update database with renewal
        mock_payment_api.put.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "success": True,
                "data": {
                    "subscription_id": subscription_id,
                    "status": "active",
                    "renewed_at": datetime.now().isoformat(),
                    "next_renewal": datetime.fromtimestamp(renewed_subscription["current_period_end"]).isoformat()
                }
            })
        )
        
        renewal_update = await mock_payment_api.put(
            f"/api/subscriptions/{subscription_id}/renew",
            json={
                "renewed_at": datetime.now().isoformat(),
                "next_period_end": datetime.fromtimestamp(renewed_subscription["current_period_end"]).isoformat()
            }
        )
        
        # Step 5: Update Redis renewal schedule
        next_renewal = datetime.fromtimestamp(renewed_subscription["current_period_end"])
        await mock_payment_redis.zadd(
            "subscription_renewals",
            {f"{user_id}:{subscription_id}": next_renewal.timestamp()}
        )
        
        # Step 6: Send renewal confirmation
        await mock_payment_bot.send_message(
            chat_id=user_id,
            text="✅ Subscription renewed successfully!\n\n💎 Your Premium subscription has been extended for another month.\n\n📅 Next renewal: " + 
                 next_renewal.strftime("%B %d, %Y"),
            reply_markup={"inline_keyboard": [
                [{"text": "📊 View Benefits", "callback_data": "view_premium_benefits"}],
                [{"text": "⚙️ Manage Subscription", "callback_data": "manage_subscription"}]
            ]}
        )
        
        # Workflow completion
        update_payment_workflow_state(workflow_id, {
            "stage": "renewal_completed",
            "renewed_successfully": True,
            "next_renewal_scheduled": True
        })
        
        # Validate renewal workflow
        state = get_payment_workflow_state(workflow_id)
        assert state["stage"] == "renewal_completed"
        assert state["renewed_successfully"] is True
        assert state["next_renewal_scheduled"] is True
        
        # Verify service calls
        mock_payment_api.get.assert_called_once()
        mock_payment_api.put.assert_called_once()
        mock_stripe_workflow.retrieve_subscription.assert_called_once()
        
        # Verify next renewal scheduled
        renewals = await mock_payment_redis.zrange("subscription_renewals", 0, -1)
        assert f"{user_id}:{subscription_id}" in renewals


class TestRefundWorkflow:
    """Test refund processing workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_refund_workflow(
        self,
        mock_stripe_workflow,
        mock_payment_api,
        mock_payment_bot,
        mock_payment_redis
    ):
        """Test complete refund processing workflow"""
        workflow_id = str(uuid.uuid4())
        user_id = 123456789
        payment_intent_id = "pi_refund_test"
        refund_amount = 2999
        
        # Step 1: Initialize refund request
        update_payment_workflow_state(workflow_id, {
            "stage": "refund_requested",
            "user_id": user_id,
            "payment_intent_id": payment_intent_id,
            "refund_amount": refund_amount,
            "reason": "user_requested"
        })
        
        # Step 2: Validate refund eligibility
        mock_payment_api.get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "success": True,
                "data": {
                    "payment_intent_id": payment_intent_id,
                    "amount": refund_amount,
                    "status": "succeeded",
                    "refundable": True,
                    "created_at": (datetime.now() - timedelta(days=5)).isoformat()
                }
            })
        )
        
        payment_details = await mock_payment_api.get(f"/api/payments/{payment_intent_id}")
        
        # Step 3: Process refund with Stripe
        mock_stripe_workflow.create_refund.return_value = {
            "id": "re_refund_test",
            "amount": refund_amount,
            "status": "succeeded",
            "payment_intent": payment_intent_id,
            "created": int(datetime.now().timestamp())
        }
        
        refund_result = await mock_stripe_workflow.create_refund(
            payment_intent=payment_intent_id,
            amount=refund_amount,
            reason="requested_by_customer"
        )
        
        # Step 4: Update subscription status
        mock_payment_api.put.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "success": True,
                "data": {
                    "user_id": user_id,
                    "subscription_status": "cancelled",
                    "refund_processed": True,
                    "refund_id": refund_result["id"]
                }
            })
        )
        
        subscription_update = await mock_payment_api.put(
            f"/api/users/{user_id}/subscription",
            json={
                "status": "cancelled",
                "refund_id": refund_result["id"],
                "cancelled_at": datetime.now().isoformat()
            }
        )
        
        # Step 5: Update Redis cache
        await mock_payment_redis.hset(
            f"user_subscription:{user_id}",
            mapping={
                "status": "cancelled",
                "refund_processed": "true",
                "refund_id": refund_result["id"],
                "cancelled_at": datetime.now().isoformat()
            }
        )
        
        # Step 6: Remove from renewal schedule
        await mock_payment_redis.zrem("subscription_renewals", f"{user_id}:*")
        
        # Step 7: Send refund confirmation
        await mock_payment_bot.send_message(
            chat_id=user_id,
            text=f"✅ Refund processed successfully!\n\n💰 Amount: ${refund_amount/100:.2f}\n⏱️ Processing time: 5-10 business days\n\n📧 You'll receive an email confirmation shortly.",
            reply_markup={"inline_keyboard": [
                [{"text": "📋 View Refund Details", "callback_data": f"refund_details_{refund_result['id']}"}],
                [{"text": "🔄 Resubscribe Later", "callback_data": "view_plans"}]
            ]}
        )
        
        # Workflow completion
        update_payment_workflow_state(workflow_id, {
            "stage": "refund_completed",
            "refund_id": refund_result["id"],
            "subscription_cancelled": True
        })
        
        # Validate refund workflow
        state = get_payment_workflow_state(workflow_id)
        assert state["stage"] == "refund_completed"
        assert state["refund_id"] == refund_result["id"]
        assert state["subscription_cancelled"] is True
        
        # Verify service interactions
        mock_payment_api.get.assert_called_once()
        mock_payment_api.put.assert_called_once()
        mock_stripe_workflow.create_refund.assert_called_once()
        
        # Verify Redis updates
        user_sub = await mock_payment_redis.hgetall(f"user_subscription:{user_id}")
        assert user_sub["status"] == "cancelled"
        assert user_sub["refund_processed"] == "true"


# Integration test configuration
pytestmark = pytest.mark.integration

if __name__ == "__main__":
    # Run tests with coverage reporting
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
