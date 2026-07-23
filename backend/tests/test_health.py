"""Health Check Endpoint Tests"""
import pytest


def test_health_check(client):
    """Test the health check endpoint returns healthy status"""
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "environment" in data