#!/usr/bin/env python3
"""
Enhanced test configuration with comprehensive fixtures and factory patterns
"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import text

from src.main import create_app
from src.models.user import db


@pytest.fixture(scope="session")
def app():
    """Create and configure a test app for the entire test session with enhanced database handling"""
    # Set testing environment
    os.environ["FLASK_ENV"] = "testing"

    app = create_app()

    # Enhanced database configuration for testing with better connection management
    database_url = os.environ.get("DATABASE_URL")
    if database_url and "postgresql" in database_url:
        # Enhanced PostgreSQL configuration for CI/CD stability
        if "?" in database_url:
            database_url += (
                "&pool_size=3&max_overflow=5&pool_timeout=20&pool_recycle=200"
                "&pool_pre_ping=true&connect_timeout=15"
            )
        else:
            database_url += (
                "?pool_size=3&max_overflow=5&pool_timeout=20&pool_recycle=200"
                "&pool_pre_ping=true&connect_timeout=15"
            )

    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": database_url or "sqlite:///:memory:",
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "pool_timeout": 20,
                "pool_recycle": 200,
                "pool_pre_ping": True,
                "echo": False,  # Disable SQL logging in tests for performance
                "connect_args": (
                    {
                        "connect_timeout": 15,
                        "application_name": "landscape_test",
                        "options": "-c statement_timeout=30000",  # 30 second statement timeout
                    }
                    if database_url and "postgresql" in database_url
                    else {"timeout": 10}  # SQLite timeout
                ),
            },
            "SESSION_COOKIE_SECURE": False,
            "RATELIMIT_ENABLED": False,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
            # Disable certain features during testing for stability
            "PRESERVE_CONTEXT_ON_EXCEPTION": False,
        }
    )

    return app


@pytest.fixture(scope="function", autouse=True)
def ensure_clean_database(app):
    """Automatically ensure clean database before and after each test"""
    with app.app_context():
        # Ensure tables exist
        db.create_all()

        # Clean before test
        _cleanup_database()

        yield

        # Clean after test
        _cleanup_database()


@pytest.fixture(scope="function")
def app_context(app, ensure_clean_database):
    """Create an application context for each test with enhanced isolation"""
    with app.app_context():
        yield app


def _cleanup_database():
    """Enhanced helper function to clean up database consistently with timeout handling"""
    import gc
    import threading

    # Force garbage collection before cleanup to free memory
    gc.collect()

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
    cleanup_thread = threading.Thread(target=cleanup_with_timeout, daemon=True)
    cleanup_thread.start()

    # Wait for completion with 25-second timeout (reduced from 30 for faster feedback)
    cleanup_success.wait(timeout=25.0)

    if cleanup_thread.is_alive():
        # Cleanup timed out - log and continue without failing tests
        import warnings

        warnings.warn("Database cleanup timed out after 25 seconds, continuing...")
        # Force cleanup thread termination attempt
        try:
            cleanup_thread.join(timeout=2.0)
        except Exception:
            pass
        return

    if cleanup_exception:
        # Log the exception but don't fail tests due to cleanup issues
        import warnings

        warnings.warn(f"Database cleanup failed with exception: {cleanup_exception}")


def _perform_database_cleanup():
    """Enhanced database cleanup operations with better isolation and error handling"""
    import gc
    import time

    try:
        # Force garbage collection before database operations
        gc.collect()

        # Close any active transactions first with enhanced error handling
        try:
            if hasattr(db.session, "is_active") and db.session.is_active:
                db.session.rollback()
            # Ensure session is properly closed
            if hasattr(db.session, "close"):
                db.session.close()
            # Remove session to ensure clean state
            if hasattr(db.session, "remove"):
                db.session.remove()
        except Exception:
            # If session operations fail, try to force a clean state
            try:
                db.session.expunge_all()
            except Exception:
                pass

        # Use faster truncation approach for PostgreSQL, or recreate tables for SQLite
        try:
            # Check if we're using PostgreSQL
            engine_name = str(db.engine.url).lower()
            if "postgresql" in engine_name:
                # Use TRUNCATE for faster cleanup in PostgreSQL with enhanced timeout
                with db.engine.connect() as conn:
                    # Set statement timeout for PostgreSQL operations
                    conn.execute(text("SET statement_timeout = '15s'"))

                    # Get all table names (excluding system tables)
                    result = conn.execute(
                        text(
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
                                    text(
                                        f'TRUNCATE TABLE "{table}" '
                                        f"RESTART IDENTITY CASCADE"
                                    )
                                )
                            except Exception:
                                pass

                        conn.commit()
            else:
                # For SQLite, use delete operations instead of drop/recreate for better stability
                try:
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

                    # Start new transaction for cleanup operations
                    db.session.begin()

                    # Delete in order to respect foreign key constraints with timeout control
                    cleanup_start = time.time()
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
                            # Check if cleanup is taking too long
                            if (
                                time.time() - cleanup_start > 8
                            ):  # 8 second total timeout
                                break

                            # Add timeout for each delete operation
                            operation_start = time.time()
                            # Use more efficient bulk delete
                            deleted_count = db.session.query(model).delete()

                            # Break if individual operation takes too long
                            if (
                                time.time() - operation_start > 2
                            ):  # 2 second timeout per operation
                                break

                        except Exception:
                            # Continue with other models if one fails
                            try:
                                db.session.rollback()
                                db.session.begin()
                            except Exception:
                                pass

                    db.session.commit()

                except Exception:
                    # If individual cleanup fails, try drop/recreate as last resort
                    try:
                        # Drop all tables
                        db.drop_all()
                        # Recreate all tables
                        db.create_all()
                        # Commit the changes
                        db.session.commit()
                    except Exception:
                        pass

        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass

        # Enhanced session cleanup with timeout protection
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

        # Final garbage collection
        gc.collect()

    except Exception:
        # Any exception during cleanup should not fail tests
        try:
            # Ensure tables exist for SQLite
            engine_name = str(db.engine.url).lower()
            if "sqlite" in engine_name:
                db.create_all()
            db.session.rollback()
            db.session.close()
            db.session.remove()
        except Exception:
            pass
        finally:
            # Ensure garbage collection happens even after errors
            gc.collect()


@pytest.fixture
def client(app_context):
    """Create a test client with enhanced isolation"""
    # Ensure database is clean before creating client
    _cleanup_database()
    return app_context.test_client()


@pytest.fixture
def runner(app_context):
    """Create a test runner with enhanced isolation"""
    # Ensure database is clean before creating runner
    _cleanup_database()
    return app_context.test_cli_runner()


@pytest.fixture
def clean_db(app_context):
    """Provide a clean database for each test with enhanced cleanup"""
    # Force cleanup before test
    _cleanup_database()

    # Start fresh transaction
    db.session.begin()
    yield db

    # Cleanup after test
    try:
        db.session.rollback()
        db.session.close()
    except Exception:
        pass
    finally:
        _cleanup_database()


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
