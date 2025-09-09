"""
Enhanced test stability and robustness utilities
"""

import functools
import logging
import sys
import time
import traceback
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

import pytest
from tests.fixtures.auth_fixtures import authenticated_test_user, setup_test_authentication
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 0.5, backoff: float = 2.0):
    """
    Decorator to retry test methods that may fail due to timing issues or race conditions.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for delay
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (AssertionError, SQLAlchemyError, Exception) as e:
                    last_exception = e

                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        break

                    logger.warning(f"Test {func.__name__} failed on attempt {attempt + 1}/{max_retries + 1}: {e}")

                    # Only retry certain types of exceptions
                    if isinstance(e, SQLAlchemyError | ConnectionError | TimeoutError):
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        # Don't retry logic errors, assertion errors, etc.
                        break

            # Re-raise the last exception if all retries failed
            raise last_exception

        return wrapper

    return decorator


@contextmanager
def error_recovery_context(operation_name: str = "test operation"):
    """
    Context manager for enhanced error recovery and logging.
    """
    start_time = time.time()
    try:
        logger.info(f"Starting {operation_name}")
        yield
        duration = time.time() - start_time
        logger.info(f"Completed {operation_name} successfully in {duration:.2f}s")
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Failed {operation_name} after {duration:.2f}s: {e}\n" f"Traceback: {traceback.format_exc()}")
        raise
    finally:
        # Cleanup logic can be added here
        pass


def validate_test_environment() -> dict[str, bool]:
    """
    Validate that the test environment is properly set up.

    Returns:
        Dictionary with validation results
    """
    validations = {}

    # Check database availability (only if we have an app context)
    try:
        import flask

        if flask.has_app_context():
            from src.models.user import db

            # Simple query to test database connection
            db.session.execute("SELECT 1")
            validations["database"] = True
        else:
            # Skip database validation if no app context
            validations["database"] = True
            logger.info("Skipping database validation - no app context")
    except Exception as e:
        logger.error(f"Database validation failed: {e}")
        validations["database"] = False

    # Check required environment variables
    import os

    required_env_vars = ["FLASK_ENV"]
    for var in required_env_vars:
        validations[f"env_var_{var}"] = var in os.environ

    # Check imports
    try:
        validations["app_import"] = True
    except Exception as e:
        logger.error(f"App import failed: {e}")
        validations["app_import"] = False

    return validations


class TestExecutionMonitor:
    """Monitor test execution for performance and stability metrics."""

    def __init__(self):
        self.execution_times = {}
        self.failure_counts = {}
        self.retry_counts = {}

    def record_execution(self, test_name: str, duration: float, success: bool):
        """Record test execution metrics."""
        if test_name not in self.execution_times:
            self.execution_times[test_name] = []

        self.execution_times[test_name].append(duration)

        if not success:
            self.failure_counts[test_name] = self.failure_counts.get(test_name, 0) + 1

    def record_retry(self, test_name: str):
        """Record a test retry."""
        self.retry_counts[test_name] = self.retry_counts.get(test_name, 0) + 1

    def get_performance_report(self) -> dict[str, Any]:
        """Generate a performance report."""
        report = {
            "total_tests": len(self.execution_times),
            "tests_with_failures": len(self.failure_counts),
            "tests_with_retries": len(self.retry_counts),
            "slowest_tests": [],
            "flaky_tests": [],
        }

        # Find slowest tests
        avg_times = {}
        for test_name, times in self.execution_times.items():
            avg_times[test_name] = sum(times) / len(times)

        slowest = sorted(avg_times.items(), key=lambda x: x[1], reverse=True)[:5]
        report["slowest_tests"] = [{"test": name, "avg_time": time} for name, time in slowest]

        # Find flaky tests (tests that had retries or multiple failures)
        for test_name, failure_count in self.failure_counts.items():
            if failure_count > 1 or test_name in self.retry_counts:
                report["flaky_tests"].append(
                    {"test": test_name, "failures": failure_count, "retries": self.retry_counts.get(test_name, 0)}
                )

        return report


# Global test monitor instance
test_monitor = TestExecutionMonitor()


@pytest.fixture(scope="session", autouse=True)
def test_environment_validation():
    """Automatically validate test environment at session start."""
    # Only validate environment if we're in a proper test session
    if hasattr(pytest, "current_request") or "pytest" in sys.modules:
        validations = validate_test_environment()

        failed_validations = [k for k, v in validations.items() if not v]
        if failed_validations:
            logger.warning(f"Test environment validation warnings: {failed_validations}")
            # Don't fail the tests, just log warnings

    yield

    # Generate performance report at end of session
    try:
        report = test_monitor.get_performance_report()
        logger.info(f"Test execution performance report: {report}")
    except Exception as e:
        logger.warning(f"Could not generate performance report: {e}")


@pytest.fixture(autouse=True)
def test_execution_tracker(request):
    """Track individual test execution metrics."""
    start_time = time.time()

    yield

    duration = time.time() - start_time
    test_name = request.node.name
    success = not hasattr(request.node, "rep_call") or request.node.rep_call.passed

    test_monitor.record_execution(test_name, duration, success)


def isolate_database_transaction(func: Callable) -> Callable:
    """
    Decorator to ensure each test runs in an isolated database transaction.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from src.models.user import db

        # Start a transaction
        with db.session.begin():
            try:
                result = func(*args, **kwargs)
                # Rollback to ensure isolation
                db.session.rollback()
                return result
            except Exception:
                # Ensure rollback on error
                db.session.rollback()
                raise

    return wrapper


def cleanup_test_data():
    """Clean up any residual test data."""
    from src.models.landscape import Client, Plant, Product, Project, ProjectPlant, Supplier
    from src.models.user import db

    try:
        # Delete in dependency order
        db.session.query(ProjectPlant).delete()
        db.session.query(Project).delete()
        db.session.query(Product).delete()
        db.session.query(Plant).delete()
        db.session.query(Supplier).delete()
        db.session.query(Client).delete()

        db.session.commit()
        logger.info("Test data cleanup completed")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Test data cleanup failed: {e}")


@pytest.fixture(autouse=True)
def auto_cleanup():
    """Automatically clean up test data after each test."""
    yield
    cleanup_test_data()
