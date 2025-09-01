import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

# Use a dedicated test DB URL and NEVER touch prod/dev DBs.
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv(
    "DATABASE_URL", "sqlite+pysqlite:///:memory:"
)


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
def engine():
    # Basic safety check to prevent running against a production DB
    assert (
        "prod" not in TEST_DATABASE_URL.lower()
    ), "Refusing to run tests against a DB that looks like production"
    eng = _make_engine(TEST_DATABASE_URL)
    return eng


@pytest.fixture(scope="session")
def connection(engine):
    conn = engine.connect()
    # Apply a per-session statement timeout for tests (Postgres only)
    try:
        conn.execute(text("SET SESSION statement_timeout = '15s'"))
    except Exception:
        # SQLite or engines that don't support this — ignore
        pass

    # Create database tables for the test session
    from src.models.user import db as flask_db

    # Create all tables in the test database
    flask_db.metadata.create_all(bind=engine)

    # For SQLAlchemy 2.0, handle transactions properly
    if conn.in_transaction():
        # If already in transaction, ensure proper cleanup
        try:
            yield conn
        finally:
            # Roll back to ensure clean state for next session
            if conn.in_transaction():
                conn.rollback()
            # Ensure connection is properly closed
            if not conn.closed:
                conn.close()
    else:
        # Start a new transaction
        outer_tx = conn.begin()
        try:
            yield conn
        finally:
            # Rollback transaction and ensure proper cleanup
            if outer_tx.is_active:
                outer_tx.rollback()
            # Ensure connection is properly closed
            if not conn.closed:
                conn.close()


@pytest.fixture(scope="session")
def Session(connection):
    # Bind a sessionmaker to a single connection to enable SAVEPOINT-based isolation per test
    return scoped_session(
        sessionmaker(
            bind=connection, expire_on_commit=False, autoflush=False, future=True
        )
    )


@pytest.fixture(autouse=True)
def db_session(Session, connection, app):
    # Each test runs inside a nested transaction (SAVEPOINT) and rolls it back after the test
    nested = connection.begin_nested()

    # Bind the Flask app's db session to our test session for proper isolation
    from src.models.user import db as flask_db

    with app.app_context():
        # Replace the Flask-SQLAlchemy session with our test session
        flask_db.session = Session

        try:
            yield Session
        finally:
            # Clean up the session first
            Session.remove()
            # Then rollback the nested transaction
            if nested.is_active:
                nested.rollback()


@pytest.fixture(scope="session")
def app():
    """Create Flask app for testing"""
    from src.main import create_app
    from src.models.user import db as flask_db

    app = create_app()
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

    # Initialize database schema with Flask app context
    with app.app_context():
        flask_db.create_all()

    return app


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner"""
    return app.test_cli_runner()


@pytest.fixture
def app_context(app):
    """Create application context for tests that need it"""
    return app
