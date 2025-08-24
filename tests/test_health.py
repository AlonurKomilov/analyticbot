"""
Test health endpoint functionality
"""
import pytest
from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test that /health endpoint returns 200 with correct response"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_headers():
    """Test that /health endpoint has proper headers"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")


@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "PATCH"])
def test_health_endpoint_methods_not_allowed(method):
    """Test that /health endpoint only accepts GET requests"""
    response = client.request(method, "/health")
    
    # Should return 405 Method Not Allowed for other methods
    assert response.status_code == 405
