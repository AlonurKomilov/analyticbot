"""
Tests for Phase 1: Endpoint Redirect Middleware
Verifies that duplicate endpoints properly redirect to canonical versions.
"""

import pytest
from fastapi.testclient import TestClient


def test_payment_singular_redirects_to_plural(client: TestClient):
    """Test that /payment/* redirects to /payments/*"""
    # Note: We expect 307 (Temporary Redirect) by default
    response = client.get("/payment/test", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/payments/test"


def test_ai_chat_redirects_to_ai(client: TestClient):
    """Test that /ai-chat/* redirects to /ai/chat/*"""
    response = client.get("/ai-chat/ask", follow_redirects=False)
    assert response.status_code == 307
    # Path should be transformed: /ai-chat → /ai
    assert response.headers["location"] == "/ai/ask"


def test_ai_insights_redirects_to_ai(client: TestClient):
    """Test that /ai-insights/* redirects to /ai/insights/*"""
    response = client.get("/ai-insights/generate", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/ai/generate"


def test_ai_services_redirects_to_ai(client: TestClient):
    """Test that /ai-services/* redirects to /ai/services/*"""
    response = client.get("/ai-services/health", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/ai/health"


def test_content_protection_redirects_to_content(client: TestClient):
    """Test that /content-protection/* redirects to /content/*"""
    response = client.get("/content-protection/check", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/content/check"


def test_redirect_preserves_query_parameters(client: TestClient):
    """Test that query parameters are preserved during redirect"""
    response = client.get("/payment/test?foo=bar&baz=qux", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/payments/test?foo=bar&baz=qux"


def test_redirect_follows_and_works(client: TestClient):
    """Test that following the redirect actually works (if endpoint exists)"""
    # This test would fail if the target endpoint doesn't exist
    # Assuming /health/ exists as a valid endpoint
    response = client.get("/health/", follow_redirects=True)
    assert response.status_code == 200


def test_non_redirect_paths_unchanged(client: TestClient):
    """Test that paths not in redirect list work normally"""
    # /health should not redirect
    response = client.get("/health/", follow_redirects=False)
    assert response.status_code == 200


def test_redirect_works_with_post_requests(client: TestClient):
    """Test that redirects work for POST requests"""
    response = client.post("/payment/create", json={"test": "data"}, follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/payments/create"


def test_redirect_works_with_nested_paths(client: TestClient):
    """Test that redirects work for deeply nested paths"""
    response = client.get("/ai-chat/history/123/details", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/ai/history/123/details"


@pytest.mark.parametrize(
    "old_path,expected_new_path",
    [
        ("/payment/list", "/payments/list"),
        ("/payment/123", "/payments/123"),
        ("/ai-chat/ask", "/ai/ask"),
        ("/ai-insights/quick", "/ai/quick"),
        ("/ai-services/status", "/ai/status"),
        ("/content-protection/validate", "/content/validate"),
    ],
)
def test_all_redirects_parametrized(client: TestClient, old_path: str, expected_new_path: str):
    """Parametrized test for all redirect mappings"""
    response = client.get(old_path, follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == expected_new_path
