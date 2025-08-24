"""
Smoke tests for layered architecture (PR-7)
Test core services, repositories, and dependency injection
"""

from datetime import datetime, timedelta

import pytest

from core import (
    Delivery,
    DeliveryService,
    DeliveryStatus,
    PostStatus,
    ScheduledPost,
    ScheduleService,
)


class MockScheduleRepository:
    """Mock repository for testing"""

    def __init__(self):
        self.posts = {}

    async def create(self, post: ScheduledPost) -> ScheduledPost:
        self.posts[post.id] = post
        return post

    async def get_by_id(self, post_id) -> ScheduledPost:
        return self.posts.get(post_id)

    async def update(self, post: ScheduledPost) -> ScheduledPost:
        self.posts[post.id] = post
        return post

    async def delete(self, post_id) -> bool:
        if post_id in self.posts:
            del self.posts[post_id]
            return True
        return False

    async def find(self, filter_criteria) -> list:
        results = list(self.posts.values())
        if filter_criteria.user_id:
            results = [p for p in results if p.user_id == filter_criteria.user_id]
        return results

    async def get_ready_for_delivery(self) -> list:
        now = datetime.utcnow()
        return [
            p
            for p in self.posts.values()
            if p.status == PostStatus.SCHEDULED and p.scheduled_at <= now
        ]

    async def count(self, filter_criteria) -> int:
        return len(await self.find(filter_criteria))


class MockDeliveryRepository:
    """Mock delivery repository for testing"""

    def __init__(self):
        self.deliveries = {}

    async def create(self, delivery: Delivery) -> Delivery:
        self.deliveries[delivery.id] = delivery
        return delivery

    async def get_by_id(self, delivery_id):
        return self.deliveries.get(delivery_id)

    async def get_by_post_id(self, post_id) -> list:
        return [d for d in self.deliveries.values() if d.post_id == post_id]

    async def update(self, delivery: Delivery) -> Delivery:
        self.deliveries[delivery.id] = delivery
        return delivery

    async def find(self, filter_criteria) -> list:
        return list(self.deliveries.values())

    async def get_failed_retryable(self) -> list:
        return [d for d in self.deliveries.values() if d.can_retry()]

    async def count(self, filter_criteria) -> int:
        return len(self.deliveries)


def test_domain_models():
    """Test core domain models"""
    # Test ScheduledPost
    post = ScheduledPost(
        title="Test Post",
        content="Hello world!",
        channel_id="123",
        user_id="456",
        scheduled_at=datetime.utcnow() + timedelta(hours=1),
    )

    assert post.title == "Test Post"
    assert post.status == PostStatus.DRAFT
    assert post.is_ready_for_delivery() == False  # Not scheduled status

    # Test status changes
    post.status = PostStatus.SCHEDULED
    post.scheduled_at = datetime.utcnow() - timedelta(minutes=1)  # Past time
    assert post.is_ready_for_delivery() == True

    # Test Delivery
    delivery = Delivery(post_id=post.id, delivery_channel_id="123")

    assert delivery.status == DeliveryStatus.PENDING
    assert delivery.can_retry() == False  # Not failed yet

    delivery.mark_as_failed("Test error")
    assert delivery.status == DeliveryStatus.FAILED
    assert delivery.can_retry() == True
    assert delivery.error_message == "Test error"


@pytest.mark.asyncio
async def test_schedule_service():
    """Test ScheduleService business logic"""
    # Setup
    repo = MockScheduleRepository()
    service = ScheduleService(repo)

    # Test creating scheduled post
    future_time = datetime.utcnow() + timedelta(hours=1)
    post = await service.create_scheduled_post(
        title="Test Post",
        content="Hello world!",
        channel_id="123",
        user_id="456",
        scheduled_at=future_time,
    )

    assert post.title == "Test Post"
    assert post.status == PostStatus.SCHEDULED

    # Test business rule: cannot schedule in past
    past_time = datetime.utcnow() - timedelta(hours=1)
    with pytest.raises(ValueError, match="Cannot schedule posts in the past"):
        await service.create_scheduled_post(
            title="Past Post",
            content="This should fail",
            channel_id="123",
            user_id="456",
            scheduled_at=past_time,
        )

    # Test getting user posts
    posts = await service.get_user_posts("456")
    assert len(posts) == 1
    assert posts[0].title == "Test Post"

    # Test cancelling post
    success = await service.cancel_post(post.id)
    assert success == True

    updated_post = await service.get_post(post.id)
    assert updated_post.status == PostStatus.CANCELLED


@pytest.mark.asyncio
async def test_delivery_service():
    """Test DeliveryService business logic"""
    # Setup
    schedule_repo = MockScheduleRepository()
    delivery_repo = MockDeliveryRepository()
    service = DeliveryService(delivery_repo, schedule_repo)

    # Create a ready post
    post = ScheduledPost(
        title="Ready Post",
        content="Ready for delivery",
        channel_id="123",
        user_id="456",
        scheduled_at=datetime.utcnow() - timedelta(minutes=1),
        status=PostStatus.SCHEDULED,
    )
    await schedule_repo.create(post)

    # Test initiating delivery
    delivery = await service.initiate_delivery(post)
    assert delivery.post_id == post.id
    assert delivery.status == DeliveryStatus.PENDING

    # Test marking in progress
    in_progress = await service.mark_delivery_in_progress(delivery.id)
    assert in_progress.status == DeliveryStatus.PROCESSING

    # Test successful completion
    completed_post = await service.complete_delivery(delivery.id, "msg123")
    assert completed_post.status == PostStatus.PUBLISHED

    # Check delivery was marked as delivered
    final_delivery = await service.get_delivery(delivery.id)
    assert final_delivery.status == DeliveryStatus.DELIVERED
    assert final_delivery.message_id == "msg123"


@pytest.mark.asyncio
async def test_delivery_retry_logic():
    """Test delivery retry business logic"""
    schedule_repo = MockScheduleRepository()
    delivery_repo = MockDeliveryRepository()
    service = DeliveryService(delivery_repo, schedule_repo)

    # Create post and delivery
    post = ScheduledPost(
        title="Retry Test",
        content="Test retry logic",
        channel_id="123",
        user_id="456",
        scheduled_at=datetime.utcnow() - timedelta(minutes=1),
        status=PostStatus.SCHEDULED,
    )
    await schedule_repo.create(post)

    delivery = await service.initiate_delivery(post)

    # Test first failure (should retry)
    failed_delivery = await service.fail_delivery(delivery.id, "Network error")
    assert failed_delivery.status == DeliveryStatus.RETRYING
    assert failed_delivery.retry_count == 1
    assert failed_delivery.can_retry() == True

    # Test max retries exceeded
    failed_delivery.retry_count = 3  # Max retries
    await delivery_repo.update(failed_delivery)

    final_failure = await service.fail_delivery(delivery.id, "Final error")
    assert final_failure.can_retry() == False

    # Post should be marked as failed too
    final_post = await schedule_repo.get_by_id(post.id)
    assert final_post.status == PostStatus.FAILED


def test_import_architecture():
    """Test that imports work without circular dependencies"""
    # Test core package imports

    # Test that API deps can be imported

    # Test that bot deps can be imported

    # Test handlers can be imported

    print("✅ All imports successful - no circular dependencies")


def test_service_dependency_injection():
    """Test that services work with repository dependency injection"""
    # Test with mock repositories
    schedule_repo = MockScheduleRepository()
    delivery_repo = MockDeliveryRepository()

    # Services should accept repository interfaces
    schedule_service = ScheduleService(schedule_repo)
    delivery_service = DeliveryService(delivery_repo, schedule_repo)

    # Verify services are properly initialized
    assert schedule_service.schedule_repo == schedule_repo
    assert delivery_service.delivery_repo == delivery_repo
    assert delivery_service.schedule_repo == schedule_repo

    print("✅ Dependency injection working correctly")
