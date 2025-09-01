"""
Comprehensive test infrastructure improvements.
Addresses race conditions, timing issues, and enhances overall test robustness.
"""

import gc
import logging
import os
import sqlite3
import sys
import time
from contextlib import contextmanager

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class TestPerformanceOptimizer:
    """Optimize test execution performance and reduce flakiness."""

    def __init__(self):
        self.slow_tests = set()
        self.flaky_tests = set()
        self.test_times = {}

    @contextmanager
    def measure_test_time(self, test_name: str):
        """Measure test execution time."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.test_times[test_name] = duration

            # Mark slow tests
            if duration > 5.0:
                self.slow_tests.add(test_name)
                logger.warning(f"Slow test detected: {test_name} took {duration:.2f}s")

    def optimize_database_connections(self, db_session):
        """Optimize database connection handling."""
        try:
            # Force connection pool cleanup
            if hasattr(db_session.bind, "pool"):
                db_session.bind.pool.dispose()

            # Explicit session cleanup
            db_session.expunge_all()
            db_session.rollback()

            # SQLite-specific optimizations
            if "sqlite" in str(db_session.bind.url):
                # Enable WAL mode for better concurrency
                db_session.execute(text("PRAGMA journal_mode=WAL"))
                # Increase timeout for busy database
                db_session.execute(text("PRAGMA busy_timeout=30000"))
                # Optimize SQLite performance
                db_session.execute(text("PRAGMA synchronous=NORMAL"))
                db_session.execute(text("PRAGMA cache_size=-64000"))  # 64MB cache
                db_session.commit()

        except Exception as e:
            logger.warning(f"Database optimization warning: {e}")

    def force_garbage_collection(self):
        """Force garbage collection to prevent memory leaks."""
        gc.collect()
        gc.collect()  # Call twice for better cleanup
        gc.collect()


class TestStabilityEnhancer:
    """Enhance test stability by addressing common failure patterns."""

    @staticmethod
    def wait_for_condition(condition_func, timeout=10, interval=0.1):
        """Wait for a condition to become true with timeout."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if condition_func():
                    return True
            except Exception:
                pass
            time.sleep(interval)
        return False

    @staticmethod
    def retry_database_operation(operation, max_retries=3, delay=0.5):
        """Retry database operations that might fail due to locking."""
        for attempt in range(max_retries):
            try:
                return operation()
            except (SQLAlchemyError, sqlite3.OperationalError) as e:
                if attempt == max_retries - 1:
                    raise

                if "database is locked" in str(e).lower() or "deadlock" in str(e).lower():
                    logger.warning(f"Database operation failed (attempt {attempt + 1}): {e}")
                    time.sleep(delay * (2**attempt))  # Exponential backoff
                else:
                    raise

    @staticmethod
    def ensure_clean_test_state():
        """Ensure clean state before test execution."""
        # Clear any cached imports that might cause issues
        import sys

        modules_to_clear = [m for m in sys.modules.keys() if m.startswith("tests.")]
        for module in modules_to_clear[:]:  # Create a copy to avoid dictionary changes during iteration
            if module in sys.modules:
                del sys.modules[module]

        # Force garbage collection
        gc.collect()

        # Reset any global state
        if hasattr(pytest, "_test_state"):
            pytest._test_state.clear()


class DatabaseTestManager:
    """Manage database testing with enhanced reliability."""

    def __init__(self, db_session):
        self.db_session = db_session
        self.optimizer = TestPerformanceOptimizer()
        self.enhancer = TestStabilityEnhancer()

    def setup_test_database(self):
        """Set up database for testing with optimizations."""
        try:
            self.optimizer.optimize_database_connections(self.db_session)

            # Ensure clean state
            self.cleanup_test_data()

            # Verify database connectivity
            self.db_session.execute(text("SELECT 1"))
            self.db_session.commit()

            logger.info("Database setup completed successfully")

        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise

    def cleanup_test_data(self):
        """Clean up test data with enhanced error handling."""

        def cleanup_operation():
            from src.models.landscape import Client, Plant, Product, Project, ProjectPlant, Supplier

            # Delete in correct dependency order
            tables_to_clean = [ProjectPlant, Project, Product, Plant, Supplier, Client]

            for table in tables_to_clean:
                try:
                    deleted_count = self.db_session.query(table).delete()
                    if deleted_count > 0:
                        logger.debug(f"Cleaned {deleted_count} records from {table.__name__}")
                except Exception as e:
                    logger.warning(f"Could not clean {table.__name__}: {e}")

            self.db_session.commit()

        # Retry cleanup operation in case of database locking
        try:
            self.enhancer.retry_database_operation(cleanup_operation)
        except Exception as e:
            logger.error(f"Test data cleanup failed: {e}")
            # Try to rollback to maintain database consistency
            try:
                self.db_session.rollback()
            except Exception as rollback_error:
                logger.error(f"Rollback also failed: {rollback_error}")

    def verify_test_isolation(self):
        """Verify that test isolation is working correctly."""
        from src.models.landscape import Supplier

        # Check that no test data exists
        supplier_count = self.db_session.query(Supplier).count()
        if supplier_count > 0:
            logger.warning(f"Test isolation issue: {supplier_count} suppliers found")
            self.cleanup_test_data()
            return False

        return True


class ConcurrencyTestManager:
    """Manage test concurrency and prevent race conditions."""

    @staticmethod
    def synchronize_test_execution():
        """Synchronize test execution to prevent race conditions."""
        # Simple file-based lock for test synchronization
        lock_file = "/tmp/landscape_test.lock"

        try:
            if os.path.exists(lock_file):
                # Wait for lock to be released
                wait_time = 0
                while os.path.exists(lock_file) and wait_time < 30:
                    time.sleep(0.1)
                    wait_time += 0.1

                if os.path.exists(lock_file):
                    logger.warning("Test lock timeout - proceeding anyway")

            # Create lock
            with open(lock_file, "w") as f:
                f.write(str(os.getpid()))

            return lock_file

        except Exception as e:
            logger.warning(f"Could not create test lock: {e}")
            return None

    @staticmethod
    def release_test_lock(lock_file):
        """Release test execution lock."""
        if lock_file and os.path.exists(lock_file):
            try:
                os.remove(lock_file)
            except Exception as e:
                logger.warning(f"Could not remove test lock: {e}")


# Enhanced pytest fixtures for improved stability
@pytest.fixture
def db_manager(db_session):
    """Provide enhanced database management for tests."""
    manager = DatabaseTestManager(db_session)
    manager.setup_test_database()

    yield manager

    # Cleanup after test
    manager.cleanup_test_data()
    manager.optimizer.force_garbage_collection()


@pytest.fixture
def performance_optimizer():
    """Provide performance optimization utilities."""
    return TestPerformanceOptimizer()


@pytest.fixture
def stability_enhancer():
    """Provide stability enhancement utilities."""
    return TestStabilityEnhancer()


@pytest.fixture(scope="function")
def isolated_test_execution():
    """Ensure isolated test execution with proper cleanup."""
    # Set up synchronization
    concurrency_manager = ConcurrencyTestManager()
    lock_file = concurrency_manager.synchronize_test_execution()

    # Ensure clean state
    TestStabilityEnhancer.ensure_clean_test_state()

    try:
        yield
    finally:
        # Cleanup
        concurrency_manager.release_test_lock(lock_file)
        gc.collect()


# Test markers for enhanced categorization
pytestmark = [pytest.mark.stability, pytest.mark.performance]


def enhance_test_reliability():
    """Apply comprehensive test reliability enhancements."""

    # Configure logging for better debugging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Set environment variables for better test behavior
    os.environ.setdefault("SQLALCHEMY_WARN_20", "1")
    os.environ.setdefault("SQLALCHEMY_SILENCE_UBER_WARNING", "1")

    # Configure test timeouts
    if "pytest-timeout" in sys.modules:
        os.environ.setdefault("PYTEST_TIMEOUT", "60")

    logger.info("Test reliability enhancements applied")


# Auto-apply enhancements when module is imported
enhance_test_reliability()
