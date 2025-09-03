import logging
import os
import time

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from tests.fixtures.test_stability import (
    cleanup_test_data,
    error_recovery_context,
    test_monitor,
    validate_test_environment,
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use a dedicated test DB URL and NEVER touch prod/dev DBs.
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")


def _make_engine(url: str):
    if url.startswith("sqlite"):
        # For in-memory SQLite, ensure single connection via StaticPool so SAVEPOINTs work.
        connect_args = {"check_same_thread": False}
        pool = StaticPool if ":memory:" in url else None
        return create_engine(
            url,
            connect_args=connect_args,
            poolclass=pool,
            future=True,
        )
    # Postgres or other RDBMS
    return create_engine(url, pool_pre_ping=True, future=True)


@pytest.fixture(scope="session", autouse=True)
def test_session_setup():
    """Session-level setup with comprehensive validation and monitoring."""
    start_time = time.time()

    # Validate test environment
    validations = validate_test_environment()
    failed_validations = [k for k, v in validations.items() if not v]

    if failed_validations:
        logger.error(f"Test environment validation failed: {failed_validations}")
        pytest.exit("Test environment is not properly configured", 1)

    logger.info("Test session starting with validated environment")

    yield

    # Session cleanup and reporting
    duration = time.time() - start_time
    performance_report = test_monitor.get_performance_report()

    logger.info(f"Test session completed in {duration:.2f}s")
    logger.info(f"Performance report: {performance_report}")

    # Final cleanup
    try:
        cleanup_test_data()
    except Exception as e:
        logger.warning(f"Final cleanup warning: {e}")


@pytest.fixture(scope="session")
def engine():
    # Enhanced safety checks
    assert "prod" not in TEST_DATABASE_URL.lower(), "Refusing to run tests against a DB that looks like production"
    assert "production" not in TEST_DATABASE_URL.lower(), "Production database detected in URL"

    with error_recovery_context("database engine creation"):
        eng = _make_engine(TEST_DATABASE_URL)

        # Test database connectivity
        try:
            with eng.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Database engine created successfully: {TEST_DATABASE_URL}")
        except Exception as e:
            logger.error(f"Database connectivity test failed: {e}")
            raise

        return eng


@pytest.fixture(scope="session")
def connection(engine):
    with error_recovery_context("database connection setup"):
        conn = engine.connect()

        # Apply a per-session statement timeout for tests (Postgres only)
        try:
            conn.execute(text("SET SESSION statement_timeout = '30s'"))
            logger.info("Applied statement timeout for session")
        except Exception:
            # SQLite or engines that don't support this — ignore
            pass

        # Create database tables for the test session
        from src.models.user import db as flask_db

        # Create all tables in the test database
        flask_db.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Enhanced transaction handling that ensures reversible outer transaction
        # even when conn.in_transaction() is already true (addresses issue #306)
        outer_tx = None

        # Always create a reversible outer transaction for consistent isolation
        if conn.in_transaction():
            # Connection already in transaction - create savepoint for isolation
            outer_tx = conn.begin_nested()
            logger.debug("Created nested transaction (savepoint) on existing transaction")

            try:
                yield conn
            finally:
                # Enhanced cleanup with consistent rollback behavior
                try:
                    if outer_tx and outer_tx.is_active:
                        outer_tx.rollback()
                        logger.debug("Rolled back nested transaction (savepoint)")
                except Exception as e:
                    logger.warning(f"Nested transaction rollback warning: {e}")

                try:
                    if not conn.closed:
                        conn.close()
                        logger.debug("Connection closed successfully")
                except Exception as e:
                    logger.warning(f"Connection close warning: {e}")
        else:
            # Connection not in transaction - create regular transaction
            outer_tx = conn.begin()
            logger.debug("Created new outer transaction")

            try:
                yield conn
            finally:
                # Enhanced cleanup with consistent rollback behavior
                try:
                    if outer_tx and outer_tx.is_active:
                        outer_tx.rollback()
                        logger.debug("Rolled back outer transaction")
                except Exception as e:
                    logger.warning(f"Transaction rollback warning: {e}")

                try:
                    if not conn.closed:
                        conn.close()
                        logger.debug("Connection closed successfully")
                except Exception as e:
                    logger.warning(f"Connection close warning: {e}")


@pytest.fixture(scope="session")
def Session(connection):
    # Bind a sessionmaker to a single connection with enhanced configuration
    return scoped_session(
        sessionmaker(bind=connection, expire_on_commit=False, autoflush=False, future=True, autocommit=False)
    )


@pytest.fixture(autouse=True)
def db_session(Session, connection, app):
    """Enhanced database session with better isolation and cleanup."""
    # Start performance tracking
    start_time = time.time()

    # Each test runs inside a nested transaction (SAVEPOINT) and rolls it back after the test
    nested = connection.begin_nested()

    # Bind the Flask app's db session to our test session for proper isolation
    from src.models.user import db as flask_db

    with app.app_context():
        # Replace the Flask-SQLAlchemy session with our test session
        original_session = flask_db.session
        flask_db.session = Session

        try:
            yield Session
        except Exception as e:
            logger.error(f"Test session error: {e}")
            # Record failure in monitor
            if hasattr(pytest, "current_test_name"):
                test_monitor.record_retry(pytest.current_test_name)
            raise
        finally:
            # Enhanced cleanup with error handling
            duration = time.time() - start_time

            try:
                # Clean up the session first
                Session.remove()
                logger.debug("Session removed successfully")
            except Exception as e:
                logger.warning(f"Session removal warning: {e}")

            try:
                # Restore original session
                flask_db.session = original_session
            except Exception as e:
                logger.warning(f"Session restoration warning: {e}")

            try:
                # Then rollback the nested transaction
                if nested.is_active:
                    nested.rollback()
                    logger.debug("Nested transaction rolled back")
            except Exception as e:
                logger.warning(f"Nested transaction rollback warning: {e}")

            # Performance tracking
            if duration > 5.0:  # Log slow tests
                logger.warning(f"Slow test detected: {duration:.2f}s")


@pytest.fixture(scope="session")
def app():
    """Create Flask app for testing with enhanced configuration"""
    with error_recovery_context("Flask app creation"):
        from src.main import create_app
        from src.models.user import db as flask_db

        app = create_app()

        # Enhanced test configuration
        app.config.update(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URL,
                "SQLALCHEMY_ENGINE_OPTIONS": {
                    "pool_pre_ping": True,
                    "future": True,
                    "pool_recycle": 3600,  # Recycle connections after 1 hour
                    "pool_timeout": 30,  # 30 second timeout for getting connection
                },
                "SESSION_COOKIE_SECURE": False,
                "RATELIMIT_ENABLED": False,
                "WTF_CSRF_ENABLED": False,
                "SECRET_KEY": "test-secret-key-enhanced-stability",
                "PROPAGATE_EXCEPTIONS": True,
                "PRESERVE_CONTEXT_ON_EXCEPTION": False,
            }
        )

        # Initialize database schema with Flask app context
        with app.app_context():
            try:
                flask_db.create_all()
                logger.info("Flask app created and database initialized successfully")
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                raise

        return app


@pytest.fixture
def client(app):
    """Create a test client with enhanced error handling"""
    with error_recovery_context("test client creation"):
        client = app.test_client()
        # Configure client for better error reporting
        client.testing = True
        return client


@pytest.fixture
def runner(app):
    """Create a test runner with enhanced configuration"""
    return app.test_cli_runner()


@pytest.fixture
def app_context(app):
    """Create application context for tests that need it"""
    return app


# Enhanced test result reporting
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Enhanced test result reporting with performance tracking."""
    outcome = yield
    report = outcome.get_result()

    # Store test result for monitoring
    test_name = item.name

    if call.when == "call":
        duration = call.duration if hasattr(call, "duration") else 0
        success = report.outcome == "passed"

        test_monitor.record_execution(test_name, duration, success)

        if not success:
            logger.warning(f"Test failed: {test_name} - {report.longrepr}")


# Enhanced fixture for handling flaky tests
@pytest.fixture
def retry_on_failure_fixture():
    """Fixture that can be used to mark tests for retry on failure."""

    def retry_decorator(max_retries=3):
        from tests.fixtures.test_stability import retry_on_failure

        return retry_on_failure(max_retries=max_retries)

    return retry_decorator
