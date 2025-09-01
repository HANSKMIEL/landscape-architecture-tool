#!/usr/bin/env python3
"""
Basic test suite for the Landscape Architecture Management System
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to Python path using relative paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import create_app  # noqa: E402


class TestHealthEndpoint:
    """Test the health check endpoint"""

    def test_health_endpoint(self, client):
        """Test that health endpoint returns expected response"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "2.0.0"
        assert data["database_status"] == "connected"


class TestAPIDocumentation:
    """Test the API documentation endpoint"""

    def test_api_documentation(self, client):
        """Test that API documentation endpoint works"""
        response = client.get("/api/")
        assert response.status_code == 200

        data = response.get_json()
        assert data["name"] == "Landscape Architecture Management API"
        assert data["version"] == "2.0.0"
        assert "endpoints" in data
        assert data["status"] == "operational"


class TestSupplierEndpoints:
    """Test supplier-related endpoints"""

    def test_get_suppliers_empty(self, client):
        """Test getting suppliers when database is empty"""
        response = client.get("/api/suppliers")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert "suppliers" in data
        assert data["suppliers"] == []
        assert data["total"] == 0

    def test_create_supplier_valid(self, client):
        """Test creating a valid supplier"""
        supplier_data = {
            "name": "Test Supplier",
            "contact_person": "John Doe",
            "email": "john@testsupplier.com",
            "phone": "123-456-7890",
            "address": "123 Test St",
        }

        response = client.post("/api/suppliers", json=supplier_data)
        assert response.status_code == 201

        data = response.get_json()
        assert data["name"] == supplier_data["name"]
        assert data["email"] == supplier_data["email"]

    def test_create_supplier_invalid(self, client):
        """Test creating supplier with invalid data"""
        invalid_data = {
            "name": "",  # Empty name should be invalid
            "email": "invalid-email",  # Invalid email format
        }

        response = client.post("/api/suppliers", json=invalid_data)
        assert response.status_code in [400, 422]  # Should return validation error


class TestPlantEndpoints:
    """Test plant-related endpoints"""

    def test_get_plants_empty(self, client):
        """Test getting plants when database is empty"""
        response = client.get("/api/plants")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert "plants" in data
        assert data["plants"] == []
        assert data["total"] == 0

    def test_create_plant_valid(self, client):
        """Test creating a valid plant"""
        plant_data = {
            "name": "Testicus planticus",
            "common_name": "Test Plant",
            "category": "Perennial",
            "price": 15.99,
            "notes": "A test plant for testing",
        }

        response = client.post("/api/plants", json=plant_data)
        assert response.status_code == 201

        data = response.get_json()
        assert data["name"] == plant_data["name"]
        assert data["common_name"] == plant_data["common_name"]


class TestProductionConfiguration:
    """Test production-specific configurations"""

    def test_production_config_loaded(self):
        """Test that production configuration is properly loaded"""
        with patch.dict("os.environ", {"FLASK_ENV": "production"}):
            app = create_app()
            assert not app.config["DEBUG"]
            assert app.config["SESSION_COOKIE_SECURE"]
            assert app.config["SESSION_COOKIE_HTTPONLY"]

    def test_security_headers_present(self, client):
        """Test that security headers are added to responses"""
        response = client.get("/health")

        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "X-XSS-Protection" in response.headers


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limiting_enabled(self, app):
        """Test that rate limiting is properly configured"""
        # In a real test, you would make multiple requests to trigger rate limiting
        # For this basic test, we just verify the limiter is configured
        assert hasattr(app, "limiter") or "flask_limiter" in str(app.extensions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
