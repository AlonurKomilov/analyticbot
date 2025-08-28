"""
Minimal conftest for simple unit tests
No database or external service dependencies
"""
import pytest


def pytest_collection_modifyitems(config, items):
    """
    Remove markers that would cause tests to be skipped
    """
    for item in items:
        # Remove integration markers from simple tests
        if "test_simple" in item.nodeid or "test_domain_basic" in item.nodeid:
            # Clear any markers that might cause skips
            item.own_markers = []


# Override the problematic autouse fixtures for simple tests
@pytest.fixture(autouse=True)
def simple_test_setup():
    """Simple test setup without database"""
    # Just pass - no complex setup needed
    yield


# Mock any database-dependent autouse fixtures
@pytest.fixture(autouse=True)
def override_reset_test_data():
    """Override the database reset fixture for simple tests"""
    # No database operations needed for simple tests
    yield
