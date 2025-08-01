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
from sqlalchemy.exc import SQLAlchemyError

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
        # First, try to rollback any pending transactions
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
        db.session.query(ProjectPlant).delete()
        db.session.query(Project).delete()
        db.session.query(PlantRecommendationRequest).delete()
        db.session.query(Plant).delete()
        db.session.query(Product).delete()
        db.session.query(Client).delete()
        db.session.query(Supplier).delete()
        db.session.query(User).delete()
        db.session.commit()
    except Exception:
        db.session.rollback()

    try:
        # Close and remove the session
        db.session.close()
        db.session.remove()
    except Exception:
        pass

    try:
        # Dispose of engine connections
        db.engine.dispose()
    except SQLAlchemyError:
        pass


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


# Import factory fixtures
from tests.fixtures.test_data import *
