from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from apps.bot.container import container
from apps.bot.database.repositories import ChannelRepository
from apps.bot.services.subscription_service import SubscriptionService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def mock_plan_repo():
    return AsyncMock()


@pytest.fixture
def mock_channel_repo():
    return AsyncMock(spec=ChannelRepository)


@pytest.fixture
def subscription_service(mock_channel_repo):
    return SubscriptionService(repository=mock_channel_repo)


@pytest.fixture
def setup_mocks(monkeypatch, mock_user_repo, mock_plan_repo):
    """Mocks for container dependencies."""
    monkeypatch.setattr(
        container,
        "resolve",
        MagicMock(
            side_effect=lambda dep: {
                "UserRepository": mock_user_repo,
                "PlanRepository": mock_plan_repo,
            }.get(dep.__name__, MagicMock())
        ),
    )


async def test_check_channel_limit_allow(
    subscription_service: SubscriptionService,
    setup_mocks,
    mock_user_repo,
    mock_plan_repo,
    mock_channel_repo,
):
    """Foydalanuvchi kanal qo'sha olishi kerak (limitdan oshmagan)."""
    mock_user_repo.get_user_plan_name.return_value = "free"
    mock_plan_repo.get_plan_by_name.return_value = {"max_channels": 3}
    mock_channel_repo.count_user_channels.return_value = 2
    await subscription_service.check_channel_limit(user_id=123)


async def test_check_channel_limit_deny(
    subscription_service: SubscriptionService,
    setup_mocks,
    mock_user_repo,
    mock_plan_repo,
    mock_channel_repo,
):
    """Foydalanuvchi kanal qo'sha olmasligi kerak (limitga yetgan)."""
    mock_user_repo.get_user_plan_name.return_value = "free"
    mock_plan_repo.get_plan_by_name.return_value = {"max_channels": 3}
    mock_channel_repo.count_user_channels.return_value = 3
    with pytest.raises(HTTPException) as exc_info:
        await subscription_service.check_channel_limit(user_id=123)
    assert exc_info.value.status_code == 403


async def test_check_channel_limit_unlimited(
    subscription_service: SubscriptionService,
    setup_mocks,
    mock_user_repo,
    mock_plan_repo,
):
    """Foydalanuvchi cheksiz kanal qo'sha olishi kerak."""
    mock_user_repo.get_user_plan_name.return_value = "premium"
    mock_plan_repo.get_plan_by_name.return_value = {"max_channels": None}
    await subscription_service.check_channel_limit(user_id=123)


@pytest.fixture
def mock_scheduler_repo():
    return AsyncMock()


@pytest.fixture
def setup_full_mocks(monkeypatch, mock_user_repo, mock_plan_repo, mock_scheduler_repo):
    """Mocks for container dependencies, including scheduler."""

    def resolve_mock(dep):
        if "UserRepository" in str(dep):
            return mock_user_repo
        if "PlanRepository" in str(dep):
            return mock_plan_repo
        if "SchedulerRepository" in str(dep):
            return mock_scheduler_repo
        return MagicMock()

    monkeypatch.setattr(container, "resolve", MagicMock(side_effect=resolve_mock))


async def test_check_post_limit_allow(
    subscription_service: SubscriptionService,
    setup_full_mocks,
    mock_user_repo,
    mock_plan_repo,
    mock_scheduler_repo,
):
    """User should be able to post (under limit)."""
    mock_user_repo.get_user_plan_name.return_value = "free"
    mock_plan_repo.get_plan_by_name.return_value = {"max_posts_per_month": 30}
    mock_scheduler_repo.count_user_posts_this_month.return_value = 10
    await subscription_service.check_post_limit(user_id=123)


async def test_check_post_limit_deny(
    subscription_service: SubscriptionService,
    setup_full_mocks,
    mock_user_repo,
    mock_plan_repo,
    mock_scheduler_repo,
):
    """User should not be able to post (at limit)."""
    mock_user_repo.get_user_plan_name.return_value = "free"
    mock_plan_repo.get_plan_by_name.return_value = {"max_posts_per_month": 30}
    mock_scheduler_repo.count_user_posts_this_month.return_value = 30
    with pytest.raises(HTTPException) as exc_info:
        await subscription_service.check_post_limit(user_id=123)
    assert exc_info.value.status_code == 403


async def test_check_post_limit_unlimited(
    subscription_service: SubscriptionService,
    setup_full_mocks,
    mock_user_repo,
    mock_plan_repo,
):
    """User with unlimited plan can post."""
    mock_user_repo.get_user_plan_name.return_value = "premium"
    mock_plan_repo.get_plan_by_name.return_value = {"max_posts_per_month": None}
    await subscription_service.check_post_limit(user_id=123)


async def test_get_usage_status(
    subscription_service: SubscriptionService,
    setup_full_mocks,
    mock_user_repo,
    mock_plan_repo,
    mock_channel_repo,
    mock_scheduler_repo,
):
    """Should return correct usage status."""
    mock_user_repo.get_user_plan_name.return_value = "pro"
    mock_plan_repo.get_plan_by_name.return_value = {
        "name": "pro",
        "max_channels": 5,
        "max_posts_per_month": 100,
    }
    mock_channel_repo.count_user_channels.return_value = 3
    mock_scheduler_repo.count_user_posts_this_month.return_value = 42
    status = await subscription_service.get_usage_status(user_id=123)
    assert status.plan_name == "pro"
    assert status.current_channels == 3
    assert status.max_channels == 5
    assert status.current_posts_this_month == 42
    assert status.max_posts_per_month == 100
