"""
Basic health check tests for the API.
"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_ping_endpoint():
    """Test the ping endpoint returns pong."""
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_root_endpoint():
    """Test the root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_api_docs_accessible():
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    # Check that it returns HTML
    assert "text/html" in response.headers.get("content-type", "")
