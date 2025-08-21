#!/usr/bin/env python3
"""
Enhanced test configuration with comprehensive fixtures and factory patterns
"""

import os
import sys

import pytest

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import create_app
from src.models.user import db


@pytest.fixture(scope="session")
def app():
    """Create and configure a test app for the entire test session"""
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

    return app


@pytest.fixture(scope="function")
def app_context(app):
    """Create an application context for each test"""
    with app.app_context():
        # Clean up before test to ensure clean state
        _cleanup_database()

        db.create_all()
        yield app

        # Comprehensive cleanup after test to ensure complete isolation
        _cleanup_database()


def _cleanup_database():
    """Helper function to clean up database consistently"""
    try:
        # Close any active transactions first
        if db.session.is_active:
            db.session.rollback()
    except Exception:
        pass

    try:
        # Clear all data from all tables (more reliable than drop_all/create_all)
        from src.models.landscape import (
            Client,
            Plant,
            PlantRecommendationRequest,
            Product,
            Project,
            ProjectPlant,
            Supplier,
        )
        from src.models.user import User

        # Delete in order to respect foreign key constraints
        for model in [
            ProjectPlant,
            Project,
            PlantRecommendationRequest,
            Plant,
            Product,
            Client,
            Supplier,
            User,
        ]:
            try:
                db.session.query(model).delete()
            except Exception:
                pass

        db.session.commit()
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass

    try:
        # Close the session
        db.session.close()
    except Exception:
        pass

    try:
        # Remove scoped session
        db.session.remove()
    except Exception:
        pass

    # Don't dispose engine for SQLite in-memory databases as it can cause issues


@pytest.fixture
def client(app_context):
    """Create a test client"""
    return app_context.test_client()


@pytest.fixture
def runner(app_context):
    """Create a test runner"""
    return app_context.test_cli_runner()


@pytest.fixture
def clean_db(app_context):
    """Provide a clean database for each test"""
    db.session.begin()
    yield db
    db.session.rollback()
    db.session.close()


# Import factory fixtures (optional - for development environments)
# Critical dependencies are validated at startup, but optional test dependencies
# like factory-boy may be missing in CI environments with network issues
try:
    from tests.fixtures.test_data import *  # noqa: F401,F403
except ImportError as e:
    # Factory-boy or other optional test dependencies not available
    # This is acceptable in CI environments with limited dependencies
    # Production dependencies are validated separately by DependencyValidator
    import warnings

    warnings.warn(
        f"Optional test fixtures not available: {e}. "
        "Advanced test features may be limited, but core functionality is unaffected. "
        "Install development dependencies with: pip install -r requirements-dev.txt",
        UserWarning,
    )
