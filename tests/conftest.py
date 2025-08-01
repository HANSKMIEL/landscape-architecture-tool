#!/usr/bin/env python3
"""
Enhanced test configuration with comprehensive fixtures and factory patterns
"""

import os
import sys
import tempfile
from unittest.mock import patch

import pytest
from flask import Flask

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
        db.create_all()
        yield app
        # Ensure proper cleanup of all database state
        db.session.close()
        db.session.remove()
        db.drop_all()
        # Recreate the engine to ensure clean state
        db.engine.dispose()


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


from tests.fixtures.database import *

# Import factory fixtures
from tests.fixtures.test_data import *
