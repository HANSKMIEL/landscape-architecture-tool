import os
import sys
from unittest.mock import Mock

import pytest

# Add project root to Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.main import create_app
from src.models.user import db


@pytest.fixture
def app():
    """Create application for testing"""
    # Set testing environment
    os.environ["FLASK_ENV"] = "testing"

    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SESSION_COOKIE_SECURE": False,
            "RATELIMIT_ENABLED": False,
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Create application context"""
    with app.app_context():
        yield app


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.delete = Mock()
    return session


@pytest.fixture
def mock_query():
    """Mock database query"""
    query = Mock()
    query.get = Mock()
    query.filter = Mock()
    query.filter_by = Mock()
    query.order_by = Mock()
    query.paginate = Mock()
    query.all = Mock()
    query.first = Mock()
    return query


@pytest.fixture
def mock_pagination():
    """Mock pagination object"""
    pagination = Mock()
    pagination.items = []
    pagination.total = 0
    pagination.pages = 0
    pagination.page = 1
    pagination.per_page = 50
    pagination.has_next = False
    pagination.has_prev = False
    return pagination


@pytest.fixture
def db_session(app_context):
    """Database session for testing"""
    return db.session
