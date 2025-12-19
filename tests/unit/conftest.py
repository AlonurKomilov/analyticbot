"""
Unit Tests Conftest
===================

Simple conftest for unit tests that don't require the full application stack.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timedelta
from uuid import uuid4


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return {
        'id': 12345,
        'username': 'test_user',
        'telegram_id': 123456789,
        'credits': 500,
        'created_at': datetime.utcnow().isoformat(),
    }


@pytest.fixture
def mock_marketplace_item():
    """Create a mock marketplace item."""
    return {
        'id': str(uuid4()),
        'name': 'Test Service',
        'service_key': 'test_service',
        'category': 'bot_service',
        'credits_per_month': 50,
        'description': 'A test service',
        'is_active': True,
        'features': ['Feature 1', 'Feature 2'],
    }


@pytest.fixture
def mock_subscription():
    """Create a mock subscription."""
    return {
        'id': str(uuid4()),
        'user_id': 12345,
        'service_key': 'test_service',
        'status': 'active',
        'started_at': datetime.utcnow().isoformat(),
        'expires_at': (datetime.utcnow() + timedelta(days=30)).isoformat(),
        'auto_renew': True,
    }


@pytest.fixture
def mock_quota():
    """Create a mock quota."""
    return {
        'service_key': 'ai_test_service',
        'daily_limit': 100,
        'used_today': 25,
        'reset_at': (datetime.utcnow() + timedelta(hours=12)).isoformat(),
    }


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session
