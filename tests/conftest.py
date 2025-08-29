import os
import sys

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import create_app
from src.models.user import db as flask_db

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


@pytest.fixture(scope="session")
def app():
    """Create and configure a test app for the entire test session"""
    # Set testing environment
    os.environ["FLASK_ENV"] = "testing"

    app = create_app()

    # Basic safety check to prevent running against a production DB
    assert "prod" not in TEST_DATABASE_URL.lower(), "Refusing to run tests against a DB that looks like production"

    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URL,
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "pool_pre_ping": True,
                "future": True,
            },
            "SESSION_COOKIE_SECURE": False,
            "RATELIMIT_ENABLED": False,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
        }
    )

    return app


@pytest.fixture(scope="session")
def engine(app):
    """Create SQLAlchemy engine for tests"""
    with app.app_context():
        eng = _make_engine(TEST_DATABASE_URL)
        flask_db.metadata.create_all(bind=eng)
        return eng


@pytest.fixture(scope="session")
def connection(engine):
    """Create a connection for the test session"""
    conn = engine.connect()
    # Apply a per-session statement timeout for tests (Postgres only)
    try:
        conn.execute(text("SET SESSION statement_timeout = '15s'"))
    except Exception:
        # SQLite or engines that don't support this — ignore
        pass

    yield conn
    conn.close()


@pytest.fixture(scope="session")
def Session(connection):
    """Bind a sessionmaker to a single connection to enable SAVEPOINT-based isolation per test"""
    return scoped_session(sessionmaker(bind=connection, expire_on_commit=False, autoflush=False, future=True))


@pytest.fixture(autouse=True)
def db_session(app, Session, connection):
    """Each test runs inside a nested transaction (SAVEPOINT) and rolls it back after the test"""
    with app.app_context():
        # Replace the Flask-SQLAlchemy session with our session
        flask_db.session = Session

        # Each test runs inside a nested transaction (SAVEPOINT) and rolls it back after the test
        nested = connection.begin_nested()

        @event.listens_for(Session, "after_transaction_end")
        def end_savepoint(session, transaction):
            if connection.closed:
                return

            if not connection.in_nested_transaction():
                connection.begin_nested()

        try:
            yield Session
        finally:
            Session.remove()
            nested.rollback()


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner"""
    return app.test_cli_runner()
