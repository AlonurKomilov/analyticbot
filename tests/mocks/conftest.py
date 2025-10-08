"""
Mock Configuration for Tests
============================

Pytest configuration and utilities for all testing mocks.
Provides centralized mock setup and teardown for consistent testing.
"""

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture
def mock_analytics_service() -> Generator[Mock, None, None]:
    """Provide a mock analytics service for tests"""
    mock_service = AsyncMock()
    mock_service.get_channel_analytics.return_value = {
        "views": 1000,
        "engagement": 85,
        "growth": 12.5,
    }
    mock_service.get_post_performance.return_value = [
        {"id": "post_1", "views": 500, "engagement": 92},
        {"id": "post_2", "views": 300, "engagement": 78},
    ]
    yield mock_service


@pytest.fixture
def mock_auth_service() -> Generator[Mock, None, None]:
    """Provide a mock auth service for tests"""
    mock_service = AsyncMock()
    mock_service.authenticate_user.return_value = {
        "user_id": 1,
        "email": "test@example.com",
        "permissions": ["read", "write"],
    }
    mock_service.is_demo_user.return_value = False
    yield mock_service


@pytest.fixture
def mock_payment_service() -> Generator[Mock, None, None]:
    """Provide a mock payment service for tests"""
    mock_service = AsyncMock()
    mock_service.process_payment.return_value = {
        "transaction_id": "txn_123",
        "status": "completed",
        "amount": 99.99,
    }
    yield mock_service


@pytest.fixture
def mock_ai_service() -> Generator[Mock, None, None]:
    """Provide a mock AI service for tests"""
    mock_service = AsyncMock()
    mock_service.generate_content_suggestions.return_value = [
        {"topic": "AI Trends", "confidence": 0.95},
        {"topic": "Tech Updates", "confidence": 0.87},
    ]
    yield mock_service


@pytest.fixture
def mock_telegram_service() -> Generator[Mock, None, None]:
    """Provide a mock Telegram service for tests"""
    mock_service = AsyncMock()
    mock_service.send_message.return_value = {"message_id": 123, "status": "sent"}
    mock_service.get_channel_info.return_value = {
        "id": 456,
        "title": "Test Channel",
        "subscribers": 1000,
    }
    yield mock_service


@pytest.fixture
def mock_database_adapter() -> Generator[Mock, None, None]:
    """Provide a mock database adapter for tests"""
    mock_adapter = AsyncMock()
    mock_adapter.connect.return_value = True
    mock_adapter.execute_query.return_value = [{"id": 1, "name": "Test"}]
    mock_adapter.close.return_value = None
    yield mock_adapter


@pytest.fixture
def mock_redis_adapter() -> Generator[Mock, None, None]:
    """Provide a mock Redis adapter for tests"""
    mock_adapter = AsyncMock()
    mock_adapter.get.return_value = '{"cached": "data"}'
    mock_adapter.set.return_value = True
    mock_adapter.delete.return_value = 1
    yield mock_adapter


# Test data fixtures
@pytest.fixture
def sample_user_data() -> dict:
    """Provide sample user data for tests"""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "created_at": "2024-01-01T00:00:00Z",
        "is_active": True,
    }


@pytest.fixture
def sample_analytics_data() -> dict:
    """Provide sample analytics data for tests"""
    return {
        "channel_id": 1,
        "views": 5000,
        "engagement_rate": 12.5,
        "top_posts": [
            {"id": "post_1", "views": 1000, "engagement": 95},
            {"id": "post_2", "views": 800, "engagement": 87},
        ],
    }


@pytest.fixture
def sample_ai_recommendations() -> list:
    """Provide sample AI recommendations for tests"""
    return [
        {
            "id": "rec_1",
            "type": "content",
            "title": "Test Recommendation",
            "priority": "high",
            "impact_score": 8.5,
        },
        {
            "id": "rec_2",
            "type": "timing",
            "title": "Timing Optimization",
            "priority": "medium",
            "impact_score": 7.2,
        },
    ]


# Mock configuration helpers
class MockConfig:
    """Configuration helper for consistent mock behavior"""

    @staticmethod
    def setup_service_mocks(container):
        """Setup all service mocks in DI container"""
        # This would be called in test setup to configure
        # the DI container with mock services
        pass

    @staticmethod
    def reset_all_mocks(*mocks):
        """Reset all provided mocks to clean state"""
        for mock in mocks:
            if hasattr(mock, "reset_mock"):
                mock.reset_mock()


# Mock response templates
MOCK_API_RESPONSES = {
    "success": {"success": True, "data": {}, "message": "Operation completed"},
    "error": {"success": False, "error": "Mock error for testing", "code": 400},
    "not_found": {"success": False, "error": "Resource not found", "code": 404},
    "unauthorized": {"success": False, "error": "Unauthorized access", "code": 401},
}


def get_mock_response(response_type: str, data: Any = None) -> dict:
    """Get a standardized mock API response"""
    response = MOCK_API_RESPONSES.get(response_type, MOCK_API_RESPONSES["success"]).copy()
    if data and "data" in response:
        response["data"] = data
    return response
