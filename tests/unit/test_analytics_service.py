from unittest.mock import MagicMock

import pytest
from aiogram import Bot
from src.services.analytics_service import AnalyticsService

from infra.db.repositories.analytics_repository import AsyncpgAnalyticsRepository


@pytest.fixture
def mock_bot() -> MagicMock:
    """
    aiogram.Bot'ning soxta (mock) obyektini yaratadi.
    """
    return MagicMock(spec=Bot)


@pytest.fixture
def mock_analytics_repo() -> MagicMock:
    """
    AnalyticsRepository'ning soxta (mock) obyektini yaratadi.
    Bu obyekt haqiqiy ma'lumotlar bazasiga ulanmaydi.
    """
    return MagicMock(spec=AsyncpgAnalyticsRepository)


@pytest.fixture
def analytics_service(mock_bot: MagicMock, mock_analytics_repo: MagicMock) -> AnalyticsService:
    return AnalyticsService(bot=mock_bot, analytics_repository=mock_analytics_repo)


@pytest.mark.asyncio
async def test_get_total_users_count(
    analytics_service: AnalyticsService, mock_analytics_repo: MagicMock
):
    """
    get_total_users_count metodi to'g'ri ishlashini tekshiradi.
    """
    expected_user_count = 123
    mock_analytics_repo.get_total_users_count.return_value = expected_user_count
    actual_user_count = await analytics_service.get_total_users_count()
    assert actual_user_count == expected_user_count
    mock_analytics_repo.get_total_users_count.assert_called_once()


@pytest.mark.asyncio
async def test_get_total_channels_count(
    analytics_service: AnalyticsService, mock_analytics_repo: MagicMock
):
    """
    get_total_channels_count metodi to'g'ri ishlashini tekshiradi.
    """
    expected_channel_count = 42
    mock_analytics_repo.get_total_channels_count.return_value = expected_channel_count
    actual_channel_count = await analytics_service.get_total_channels_count()
    assert actual_channel_count == expected_channel_count
    mock_analytics_repo.get_total_channels_count.assert_called_once()


@pytest.mark.asyncio
async def test_get_total_posts_count(
    analytics_service: AnalyticsService, mock_analytics_repo: MagicMock
):
    """
    get_total_posts_count metodi to'g'ri ishlashini tekshiradi.
    """
    expected_post_count = 1024
    mock_analytics_repo.get_total_posts_count.return_value = expected_post_count
    actual_post_count = await analytics_service.get_total_posts_count()
    assert actual_post_count == expected_post_count
    mock_analytics_repo.get_total_posts_count.assert_called_once()
