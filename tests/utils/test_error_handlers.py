"""
Tests for error handling utilities
"""

import json

import pytest
from pydantic import ValidationError

from src.main import create_app
from src.utils.error_handlers import (
    DatabaseError,
    LandscapeError,
    LandscapeValidationError,
    NotFoundError,
    handle_errors,
    handle_generic_error,
    handle_landscape_error,
    handle_validation_error,
    register_error_handlers,
)
from tests.fixtures.auth_fixtures import authenticated_test_user, setup_test_authentication


@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestLandscapeExceptions:
    """Test custom exception classes"""

    def test_landscape_error_basic(self):
        """Test basic LandscapeError"""
        error = LandscapeError("Test error")

        assert error.message == "Test error"
        assert error.status_code == 500
        assert error.payload is None

        error_dict = error.to_dict()
        assert error_dict == {"error": "Test error"}

    def test_landscape_error_with_payload(self):
        """Test LandscapeError with payload"""
        payload = {"detail": "Additional info"}
        error = LandscapeError("Test error", status_code=400, payload=payload)

        assert error.status_code == 400
        assert error.payload == payload

        error_dict = error.to_dict()
        assert error_dict == {"error": "Test error", "detail": "Additional info"}

    def test_landscape_validation_error(self):
        """Test LandscapeValidationError"""
        errors = ["Field is required", "Invalid format"]
        error = LandscapeValidationError("Validation failed", errors=errors)

        assert error.message == "Validation failed"
        assert error.status_code == 400
        assert error.payload == {"validation_errors": errors}

        error_dict = error.to_dict()
        assert error_dict == {"error": "Validation failed", "validation_errors": errors}

    def test_landscape_validation_error_no_errors(self):
        """Test LandscapeValidationError without specific errors"""
        error = LandscapeValidationError("Validation failed")

        assert error.payload == {"validation_errors": None}

    def test_not_found_error_basic(self):
        """Test NotFoundError without ID"""
        error = NotFoundError("Plant")

        assert error.message == "Plant not found"
        assert error.status_code == 404

    def test_not_found_error_with_id(self):
        """Test NotFoundError with ID"""
        error = NotFoundError("Plant", resource_id=123)

        assert error.message == "Plant not found with ID 123"
        assert error.status_code == 404

    def test_database_error(self):
        """Test DatabaseError"""
        error = DatabaseError("Connection failed")

        assert error.message == "Database error: Connection failed"
        assert error.status_code == 500


class TestErrorHandlers:
    """Test error handlers"""

    def test_handle_landscape_error(self, app):
        """Test handling of LandscapeError"""
        with app.app_context():
            error = LandscapeError("Test error", status_code=400)
            response = handle_landscape_error(error)

            assert response[1] == 400
            data = json.loads(response[0].data.decode())
            assert data["error"] == "Test error"

    def test_handle_validation_error_pydantic(self, app):
        """Test handling of Pydantic ValidationError"""
        with app.app_context():
            # Create a minimal pydantic validation error
            from pydantic import BaseModel, Field

            class TestModel(BaseModel):
                name: str = Field(min_length=1)
                age: int = Field(gt=0)

            try:
                TestModel(name="", age=-1)
            except ValidationError as e:
                response = handle_validation_error(e)

                assert response[1] == 400
                data = json.loads(response[0].data.decode())
                assert "error" in data
                assert "validation_errors" in data

    def test_handle_validation_error_generic(self, app):
        """Test handling of generic validation errors (non-pydantic)"""
        with app.app_context():
            # Create a non-pydantic validation error
            error = ValueError("Generic validation error")
            response = handle_validation_error(error)

            assert response[1] == 400
            data = json.loads(response[0].data.decode())
            assert data["error"] == "Generic validation error"

    def test_handle_not_found_error(self, app):
        """Test not found error handler"""
        with app.app_context():
            # The 404 handler is registered with the app, not a standalone function
            # We'll test it through the app's error handling
            with app.test_client() as client:
                response = client.get("/nonexistent-route")
                assert response.status_code == 404

                data = json.loads(response.data.decode())
                assert "not found" in data["error"].lower()

    def test_handle_database_error_via_decorator(self, app):
        """Test database error handling via the decorator"""
        with app.app_context():
            # Test the handle_errors decorator
            @handle_errors
            def test_function():
                raise DatabaseError("Connection timeout")

            response = test_function()

            assert response[1] == 500
            data = json.loads(response[0].data.decode())
            assert "database error" in data["error"].lower()

    def test_handle_generic_error(self, app):
        """Test generic error handler"""
        with app.app_context():
            error = Exception("Something went wrong")
            response = handle_generic_error(error)

            assert response[1] == 500
            data = json.loads(response[0].data.decode())
            assert "internal server error" in data["error"].lower()


class TestErrorHandlerDecorator:
    """Test the handle_errors decorator"""

    def test_decorator_with_landscape_error(self, app):
        """Test decorator handling LandscapeError"""
        with app.app_context():

            @handle_errors
            def test_function():
                raise LandscapeValidationError("Invalid data")

            response = test_function()
            assert response[1] == 400

            data = json.loads(response[0].data.decode())
            assert "Invalid data" in data["error"]

    def test_decorator_with_validation_error(self, app):
        """Test decorator handling ValidationError"""
        with app.app_context():

            @handle_errors
            def test_function():
                from pydantic import BaseModel, Field

                class TestModel(BaseModel):
                    name: str = Field(min_length=1)

                TestModel(name="")  # This will raise ValidationError

            response = test_function()
            assert response[1] == 400

    def test_decorator_with_generic_error(self, app):
        """Test decorator handling generic Exception"""
        with app.app_context():

            @handle_errors
            def test_function():
                raise Exception("Generic error")

            response = test_function()
            assert response[1] == 500

            data = json.loads(response[0].data.decode())
            assert "internal server error" in data["error"].lower()

    def test_decorator_success_case(self, app):
        """Test decorator when function succeeds"""
        with app.app_context():

            @handle_errors
            def test_function():
                return "Success"

            result = test_function()
            assert result == "Success"


class TestErrorHandlerRegistration:
    """Test error handler registration"""

    def test_register_error_handlers(self, app):
        """Test that error handlers can be registered"""
        # The function should not raise an error
        register_error_handlers(app)

        # Test that handlers are registered by triggering them
        with app.test_client() as client:
            # Test 404 handler
            response = client.get("/nonexistent")
            assert response.status_code == 404

            data = json.loads(response.data.decode())
            assert "error" in data
