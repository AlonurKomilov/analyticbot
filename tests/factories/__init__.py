"""
Test data factories for generating realistic test data
Uses factory_boy pattern for consistent, related test data generation
"""

import random
from datetime import datetime, timedelta
from typing import Any, Dict
from uuid import uuid4

import factory
from factory import Faker, LazyFunction, SubFactory


class UserFactory(factory.Factory):
    """Factory for generating test user data"""
    
    class Meta:
        model = dict
    
    id = Faker('random_int', min=100000, max=999999999)
    telegram_id = factory.LazyAttribute(lambda obj: obj.id)
    username = Faker('user_name')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    plan_id = 1  # Default to free plan
    subscription_tier = "free"
    created_at = Faker('date_time_this_year')
    is_active = True
    language_code = Faker('random_element', elements=['en', 'uz', 'ru'])


class AdminUserFactory(UserFactory):
    """Factory for admin users"""
    
    plan_id = 3  # Admin plan
    subscription_tier = "admin"
    is_admin = True


class PremiumUserFactory(UserFactory):
    """Factory for premium users"""
    
    plan_id = 2  # Premium plan
    subscription_tier = "pro"


class ChannelFactory(factory.Factory):
    """Factory for generating test channel data"""
    
    class Meta:
        model = dict
    
    id = Faker('random_int', min=-1000000000000, max=-1)
    telegram_id = factory.LazyAttribute(lambda obj: obj.id)
    title = Faker('company')
    username = Faker('user_name')
    type = "channel"
    member_count = Faker('random_int', min=100, max=100000)
    user_id = SubFactory(UserFactory, id=True)
    description = Faker('text', max_nb_chars=100)
    invite_link = factory.LazyAttribute(lambda obj: f"https://t.me/{obj.username}")
    created_at = Faker('date_time_this_year')
    is_active = True


class PrivateChannelFactory(ChannelFactory):
    """Factory for private channels"""
    
    type = "private"
    username = None
    invite_link = Faker('url')


class ScheduledPostFactory(factory.Factory):
    """Factory for generating scheduled post data"""
    
    class Meta:
        model = dict
    
    id = LazyFunction(uuid4)
    channel_id = SubFactory(ChannelFactory, id=True)
    user_id = SubFactory(UserFactory, id=True)
    text = Faker('text', max_nb_chars=200)
    media_type = Faker('random_element', elements=['text', 'photo', 'video', 'document'])
    media_url = factory.Maybe(
        'media_type',
        yes_declaration=Faker('url'),
        no_declaration=None
    )
    scheduled_time = Faker('future_datetime', end_date='+30d')
    status = Faker('random_element', elements=['pending', 'sent', 'failed', 'cancelled'])
    views = Faker('random_int', min=0, max=10000)
    created_at = Faker('past_datetime', start_date='-30d')
    buttons = factory.LazyFunction(lambda: [] if random.random() > 0.3 else [
        {"text": "Visit Website", "url": "https://example.com"},
        {"text": "Learn More", "url": "https://example.com/learn"}
    ])


class DeliveryFactory(factory.Factory):
    """Factory for generating delivery tracking data"""
    
    class Meta:
        model = dict
    
    id = LazyFunction(uuid4)
    post_id = SubFactory(ScheduledPostFactory, id=True)
    channel_id = SubFactory(ChannelFactory, id=True)
    message_id = Faker('random_int', min=1, max=999999)
    status = Faker('random_element', elements=['pending', 'sent', 'failed', 'retry'])
    attempt_count = Faker('random_int', min=1, max=3)
    error_message = factory.Maybe(
        'status',
        yes_declaration=Faker('text', max_nb_chars=100),
        no_declaration=None
    )
    sent_at = factory.Maybe(
        'status',
        yes_declaration=Faker('past_datetime', start_date='-7d'),
        no_declaration=None
    )
    created_at = Faker('past_datetime', start_date='-7d')


class PaymentFactory(factory.Factory):
    """Factory for generating payment data"""
    
    class Meta:
        model = dict
    
    id = LazyFunction(uuid4)
    user_id = SubFactory(UserFactory, id=True)
    amount = Faker('random_int', min=1000, max=50000)  # Amount in cents
    currency = Faker('random_element', elements=['USD', 'UZS'])
    provider = Faker('random_element', elements=['stripe', 'payme', 'click'])
    provider_payment_id = Faker('uuid4')
    plan_id = Faker('random_int', min=1, max=3)
    status = Faker('random_element', elements=['pending', 'completed', 'failed', 'cancelled'])
    payment_method = Faker('random_element', elements=['card', 'bank_transfer', 'mobile'])
    metadata = factory.LazyFunction(lambda: {
        "user_agent": "Test Browser",
        "ip_address": "127.0.0.1"
    })
    created_at = Faker('past_datetime', start_date='-30d')
    completed_at = factory.Maybe(
        'status',
        yes_declaration=Faker('past_datetime', start_date='-30d'),
        no_declaration=None
    )


class SuccessfulPaymentFactory(PaymentFactory):
    """Factory for successful payments"""
    
    status = "completed"
    completed_at = Faker('past_datetime', start_date='-30d')


class FailedPaymentFactory(PaymentFactory):
    """Factory for failed payments"""
    
    status = "failed"
    error_message = Faker('text', max_nb_chars=100)


class AnalyticsDataFactory(factory.Factory):
    """Factory for generating analytics data"""
    
    class Meta:
        model = dict
    
    post_id = SubFactory(ScheduledPostFactory, id=True)
    channel_id = SubFactory(ChannelFactory, id=True)
    views = Faker('random_int', min=0, max=10000)
    clicks = Faker('random_int', min=0, max=1000)
    shares = Faker('random_int', min=0, max=500)
    engagement_rate = factory.LazyAttribute(lambda obj: (obj.clicks + obj.shares) / max(obj.views, 1))
    date = Faker('date_this_month')


class WebhookEventFactory(factory.Factory):
    """Factory for generating webhook test data"""
    
    class Meta:
        model = dict
    
    id = LazyFunction(uuid4)
    event_type = Faker('random_element', elements=['payment.completed', 'payment.failed', 'telegram.update'])
    provider = Faker('random_element', elements=['stripe', 'payme', 'telegram'])
    payload = factory.LazyFunction(lambda: {"test": True, "timestamp": datetime.now().isoformat()})
    signature = Faker('sha256')
    status = Faker('random_element', elements=['pending', 'processed', 'failed'])
    processed_at = factory.Maybe(
        'status',
        yes_declaration=Faker('past_datetime', start_date='-1d'),
        no_declaration=None
    )
    created_at = Faker('past_datetime', start_date='-1d')


# Factory sequences for related data generation
class RelatedDataFactory:
    """Helper for generating related test data sets"""
    
    @staticmethod
    def create_user_with_channels(channel_count: int = 3) -> dict[str, Any]:
        """Create a user with multiple channels"""
        user = UserFactory()
        channels = [ChannelFactory(user_id=user['id']) for _ in range(channel_count)]
        
        return {
            "user": user,
            "channels": channels
        }
    
    @staticmethod
    def create_channel_with_posts(post_count: int = 5) -> dict[str, Any]:
        """Create a channel with multiple scheduled posts"""
        user = UserFactory()
        channel = ChannelFactory(user_id=user['id'])
        posts = [
            ScheduledPostFactory(
                channel_id=channel['id'], 
                user_id=user['id']
            ) for _ in range(post_count)
        ]
        
        return {
            "user": user,
            "channel": channel,
            "posts": posts
        }
    
    @staticmethod
    def create_payment_flow_data() -> dict[str, Any]:
        """Create complete payment flow test data"""
        user = UserFactory()
        payment = PaymentFactory(user_id=user['id'])
        webhook = WebhookEventFactory(
            event_type='payment.completed',
            payload={
                "payment_id": payment['id'],
                "user_id": user['id'],
                "amount": payment['amount']
            }
        )
        
        return {
            "user": user,
            "payment": payment,
            "webhook": webhook
        }
    
    @staticmethod
    def create_analytics_scenario() -> dict[str, Any]:
        """Create analytics testing scenario"""
        user = UserFactory()
        channel = ChannelFactory(user_id=user['id'])
        
        # Create posts with varying performance
        high_performance_post = ScheduledPostFactory(
            channel_id=channel['id'],
            user_id=user['id'],
            views=5000,
            status='sent'
        )
        
        low_performance_post = ScheduledPostFactory(
            channel_id=channel['id'],
            user_id=user['id'],
            views=100,
            status='sent'
        )
        
        analytics_data = [
            AnalyticsDataFactory(
                post_id=high_performance_post['id'],
                channel_id=channel['id'],
                views=5000,
                clicks=250,
                shares=50
            ),
            AnalyticsDataFactory(
                post_id=low_performance_post['id'],
                channel_id=channel['id'],
                views=100,
                clicks=5,
                shares=1
            )
        ]
        
        return {
            "user": user,
            "channel": channel,
            "posts": [high_performance_post, low_performance_post],
            "analytics": analytics_data
        }


# Batch data generators
class BatchDataFactory:
    """Factory for generating large datasets for performance testing"""
    
    @staticmethod
    def create_users_batch(count: int = 100) -> list:
        """Create batch of users for load testing"""
        return [UserFactory() for _ in range(count)]
    
    @staticmethod
    def create_posts_batch(count: int = 1000) -> list:
        """Create batch of posts for performance testing"""
        return [ScheduledPostFactory() for _ in range(count)]
    
    @staticmethod
    def create_payments_batch(count: int = 100) -> list:
        """Create batch of payments for testing"""
        return [PaymentFactory() for _ in range(count)]


# Export all factories
__all__ = [
    'UserFactory',
    'AdminUserFactory', 
    'PremiumUserFactory',
    'ChannelFactory',
    'PrivateChannelFactory',
    'ScheduledPostFactory',
    'DeliveryFactory',
    'PaymentFactory',
    'SuccessfulPaymentFactory',
    'FailedPaymentFactory',
    'AnalyticsDataFactory',
    'WebhookEventFactory',
    'RelatedDataFactory',
    'BatchDataFactory'
]
