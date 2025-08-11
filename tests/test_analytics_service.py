import pytest
from unittest.mock import Mock, MagicMock
from bot.services.analytics_service import AnalyticsService

@pytest.fixture
def mock_analytics_repo() -> MagicMock:
    return MagicMock()

@pytest.fixture
def analytics_service(mock_analytics_repo: MagicMock) -> AnalyticsService:
    # This is the line with the bug that needs to be fixed.
    return AnalyticsService(analytics_repository=mock_analytics_repo)

def test_get_total_users_count(
    analytics_service: AnalyticsService,
    mock_analytics_repo: MagicMock
):
    expected_user_count = 123
    mock_analytics_repo.get_total_count.return_value = expected_user_count
    actual_user_count = analytics_service.get_total_users_count()
    assert actual_user_count == expected_user_count
    mock_analytics_repo.get_total_count.assert_called_once()
