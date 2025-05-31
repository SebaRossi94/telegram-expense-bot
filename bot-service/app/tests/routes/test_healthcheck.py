from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.models.healthcheck import HealthcheckResponse
from app.settings import settings


def test_health_check_healthy(client: TestClient):
    """Test health check endpoint when database is healthy."""
    with patch("app.api.router.check_db_health", return_value=True):
        response = client.get("/health")
        assert response.status_code == 200

        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert health_data["service"] == settings.app_name
        assert health_data["version"] == settings.version
        assert health_data["database"] == "connected"
        assert health_data["expense_categories"] == settings.expense_categories


def test_health_check_unhealthy(client: TestClient):
    """Test health check endpoint when database is unhealthy."""
    with patch("app.api.router.check_db_health", return_value=False):
        response = client.get("/health")
        assert response.status_code == 200

        health_data = response.json()
        assert health_data["status"] == "unhealthy"
        assert health_data["service"] == settings.app_name
        assert health_data["version"] == settings.version
        assert health_data["database"] == "disconnected"
        assert health_data["expense_categories"] == settings.expense_categories


def test_health_check_response_model():
    """Test HealthcheckResponse model validation."""
    health_data = {
        "status": "healthy",
        "service": "Test Service",
        "version": "1.0.0",
        "database": "connected",
        "expense_categories": ["Food", "Transportation"],
    }

    health_response = HealthcheckResponse(**health_data)
    assert health_response.status == health_data["status"]
    assert health_response.service == health_data["service"]
    assert health_response.version == health_data["version"]
    assert health_response.database == health_data["database"]
    assert health_response.expense_categories == health_data["expense_categories"]


def test_health_check_response_model_validation():
    """Test HealthcheckResponse model validation with invalid data."""
    with pytest.raises(ValueError):
        HealthcheckResponse(
            status="invalid_status",  # Only "healthy" or "unhealthy" are valid
            service="Test Service",
            version="1.0.0",
            database="connected",
            expense_categories=["Food"],
        )
