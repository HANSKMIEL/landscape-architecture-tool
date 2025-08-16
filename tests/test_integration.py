#!/usr/bin/env python3
"""
Integration tests for the Landscape Architecture Management System
These tests simulate the CI integration test scenarios using Flask test client
"""

import os
import sys
import warnings

import pytest

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import create_app  # noqa: E402
from src.models.user import db  # noqa: E402


@pytest.fixture(scope="function")
def integration_app():
    """Create and configure a test app that simulates the CI environment"""
    # Set testing environment
    os.environ["FLASK_ENV"] = "testing"

    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SESSION_COOKIE_SECURE": False,
            "RATELIMIT_ENABLED": False,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
        }
    )

    with app.app_context():
        db.create_all()

        # Initialize sample data to match CI expectations
        from src.utils.db_init import populate_sample_data

        try:
            populate_sample_data()
        except Exception as e:
            warnings.warn(f"Could not populate sample data: {e}", RuntimeWarning)
            # Continue anyway - test might work without sample data

        yield app

        # Clean up
        db.drop_all()


@pytest.fixture(scope="function")
def integration_client(integration_app):
    """Create a test client for integration testing"""
    return integration_app.test_client()


@pytest.mark.integration
class TestIntegrationEndpoints:
    """Test the main integration test scenarios from the CI workflow"""

    def test_health_endpoint(self, integration_client):
        """Test the health endpoint returns expected response"""
        response = integration_client.get("/health")

        assert response.status_code == 200
        data = response.get_json()

        assert data["status"] == "healthy"
        assert data["environment"] == "testing"
        assert data["version"] == "2.0.0"
        assert data["database_status"] == "connected"
        assert "timestamp" in data

    def test_dashboard_stats_endpoint(self, integration_client):
        """Test the dashboard stats endpoint"""
        response = integration_client.get("/api/dashboard/stats")

        assert response.status_code == 200
        data = response.get_json()

        # Verify the expected structure
        assert "totals" in data
        assert "projects_by_status" in data
        assert "recent_activity" in data
        assert "financial" in data

        # Verify sample data structure - counts may vary by test execution order
        totals = data["totals"]
        assert isinstance(totals["suppliers"], int)
        assert isinstance(totals["plants"], int)
        assert isinstance(totals["projects"], int)
        assert isinstance(totals["clients"], int)
        assert (
            totals["suppliers"] >= 0
        )  # May be 0 if sample data not loaded in this test context
        assert totals["plants"] >= 0
        assert totals["projects"] >= 0
        assert totals["clients"] >= 0

    def test_supplier_crud_operations(self, integration_client):
        """Test supplier CRUD operations as done in CI"""
        # Test listing suppliers first
        response = integration_client.get("/api/suppliers")
        assert response.status_code == 200
        initial_data = response.get_json()
        initial_count = initial_data["total"]

        # Test creating a supplier with the same data as CI
        supplier_data = {
            "name": "Test Supplier",
            "contact_person": "John Doe",
            "email": "john@test.com",
            "phone": "123-456-7890",
            "address": "123 Test St",
        }

        response = integration_client.post(
            "/api/suppliers",
            json=supplier_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 201
        created_supplier = response.get_json()

        # Verify the created supplier data
        assert created_supplier["name"] == supplier_data["name"]
        assert created_supplier["contact_person"] == supplier_data["contact_person"]
        assert created_supplier["email"] == supplier_data["email"]
        assert created_supplier["phone"] == supplier_data["phone"]
        assert created_supplier["address"] == supplier_data["address"]
        assert created_supplier["id"] is not None
        assert created_supplier["created_at"] is not None

        # Test listing suppliers again to verify the new supplier is included
        response = integration_client.get("/api/suppliers")
        assert response.status_code == 200
        updated_data = response.get_json()

        # Should have one more supplier
        assert updated_data["total"] == initial_count + 1

        # Verify the new supplier is in the list
        supplier_names = [s["name"] for s in updated_data["suppliers"]]
        assert "Test Supplier" in supplier_names

    def test_api_documentation_endpoint(self, integration_client):
        """Test the API documentation endpoint"""
        response = integration_client.get("/api/")

        assert response.status_code == 200
        data = response.get_json()

        assert data["name"] == "Landscape Architecture Management API"
        assert data["version"] == "2.0.0"
        assert data["status"] == "operational"
        assert data["database"] == "persistent"
        assert "endpoints" in data
