#!/usr/bin/env python3
"""
Enhanced test configuration with comprehensive fixtures and factory patterns
"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.main import create_app
from src.models.user import db


@pytest.fixture(scope="session")
def app():
    """Create and configure a test app for the entire test session"""
    # Set testing environment
    os.environ["FLASK_ENV"] = "testing"

    app = create_app()

    # Enhanced database configuration for testing
    database_url = os.environ.get("DATABASE_URL")
    if database_url and "postgresql" in database_url:
        # Add connection pooling and timeout parameters for PostgreSQL
        if "?" in database_url:
            database_url += (
                "&pool_size=5&max_overflow=10&pool_timeout=30&pool_recycle=300"
            )
        else:
            database_url += (
                "?pool_size=5&max_overflow=10&pool_timeout=30&pool_recycle=300"
            )

    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": database_url or "sqlite:///:memory:",
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "pool_timeout": 30,
                "pool_recycle": 300,
                "pool_pre_ping": True,
                "connect_args": (
                    {"connect_timeout": 30, "application_name": "landscape_test"}
                    if database_url and "postgresql" in database_url
                    else {}
                ),
            },
            "SESSION_COOKIE_SECURE": False,
            "RATELIMIT_ENABLED": False,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
        }
    )

    return app


@pytest.fixture(scope="function")
def app_context(app):
    """Create an application context for each test with enhanced isolation"""
    with app.app_context():
        # Pre-test cleanup to ensure clean state
        _cleanup_database()

        # Verify database connection before proceeding
        max_retries = 3
        for attempt in range(max_retries):
            try:
                db.create_all()
                # Test the connection with a simple query
                db.session.execute(db.text("SELECT 1")).fetchone()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    # Last attempt failed, but continue with testing
                    # This prevents the entire test suite from failing due to
                    # DB setup issues
                    import warnings

                    warnings.warn(
                        f"Database setup failed after {max_retries} attempts: {e}"
                    )
                else:
                    # Wait before retry
                    import time

                    time.sleep(1)

        yield app

        # Post-test cleanup with timeout protection
        _cleanup_database()


def _cleanup_database():
    """Helper function to clean up database consistently with timeout handling"""
    import threading

    # Use threading-based timeout instead of signal (works in all thread contexts)
    cleanup_success = threading.Event()
    cleanup_exception = None

    def cleanup_with_timeout():
        nonlocal cleanup_exception
        try:
            _perform_database_cleanup()
            cleanup_success.set()
        except Exception as e:
            cleanup_exception = e

    # Start cleanup in a separate thread to enable timeout
    cleanup_thread = threading.Thread(target=cleanup_with_timeout)
    cleanup_thread.daemon = True
    cleanup_thread.start()

    # Wait for completion with 30-second timeout
    cleanup_success.wait(timeout=30.0)

    if cleanup_thread.is_alive():
        # Cleanup timed out - log and continue without failing tests
        import warnings

        warnings.warn("Database cleanup timed out after 30 seconds, continuing...")
        return

    if cleanup_exception:
        # Log the exception but don't fail tests due to cleanup issues
        import warnings

        warnings.warn(f"Database cleanup failed with exception: {cleanup_exception}")


def _perform_database_cleanup():
    """Perform the actual database cleanup operations"""

    try:
        # Close any active transactions first
        try:
            if hasattr(db.session, "is_active") and db.session.is_active:
                db.session.rollback()
        except Exception:
            pass

        # Use faster truncation approach for PostgreSQL, fallback to delete for others
        try:
            # Check if we're using PostgreSQL
            engine_name = str(db.engine.url).lower()
            if "postgresql" in engine_name:
                # Use TRUNCATE for faster cleanup in PostgreSQL
                with db.engine.connect() as conn:
                    # Get all table names (excluding system tables)
                    result = conn.execute(
                        db.text(
                            """
                        SELECT tablename FROM pg_tables 
                        WHERE schemaname = 'public' 
                        AND tablename NOT LIKE 'alembic%'
                    """
                        )
                    )

                    tables = [row[0] for row in result]

                    # Truncate all tables with CASCADE to handle foreign keys
                    if tables:
                        for table in tables:
                            try:
                                conn.execute(
                                    db.text(
                                        f'TRUNCATE TABLE "{table}" '
                                        f"RESTART IDENTITY CASCADE"
                                    )
                                )
                            except Exception:
                                pass

                        conn.commit()
            else:
                # Fallback to delete for SQLite and other databases
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
                        # Add timeout for each delete operation
                        import time

                        start_time = time.time()
                        db.session.query(model).delete()
                        if (
                            time.time() - start_time > 5
                        ):  # 5 second timeout per operation
                            break
                    except Exception:
                        pass

                db.session.commit()

        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass

        # Clean up session with timeout protection
        try:
            if hasattr(db.session, "close"):
                db.session.close()
        except Exception:
            pass

        try:
            if hasattr(db.session, "remove"):
                db.session.remove()
        except Exception:
            pass

    except Exception:
        # Any exception during cleanup should not fail tests
        try:
            db.session.rollback()
            db.session.close()
            db.session.remove()
        except Exception:
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
