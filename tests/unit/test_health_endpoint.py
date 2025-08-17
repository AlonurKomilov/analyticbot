from fastapi.testclient import TestClient

from health_app import app

client = TestClient(app)


def test_health_endpoint():
    """
    Tests that the /health endpoint returns a 200 OK response.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
