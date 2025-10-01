"""
Centralized authentication fixtures for tests
Addresses GitHub Copilot feedback about code duplication
"""

import pytest

from src.models.user import User


@pytest.fixture
def authenticated_test_user(client, db_session):
    """
    Fixture to create a test user and set up authentication in session.
    This replaces the duplicated authentication setup code across test files.
    """
    # Create a test user in the database

    test_user = User(username="test_user", email="test@example.com", role="admin")
    test_user.set_password("password")
    db_session.add(test_user)
    db_session.commit()

    # Set up authentication in session
    with client.session_transaction() as sess:
        sess["user_id"] = test_user.id
        sess["username"] = test_user.username
        sess["role"] = test_user.role

    return test_user


@pytest.fixture
def authenticated_admin_user(client, db_session):
    """
    Fixture to create an admin test user and set up authentication in session.
    """

    admin_user = User(username="admin_user", email="admin@example.com", role="admin")
    admin_user.set_password("admin_password")
    db_session.add(admin_user)
    db_session.commit()

    # Set up authentication in session
    with client.session_transaction() as sess:
        sess["user_id"] = admin_user.id
        sess["username"] = admin_user.username
        sess["role"] = admin_user.role

    return admin_user


@pytest.fixture
def authenticated_regular_user(client, db_session):
    """
    Fixture to create a regular test user and set up authentication in session.
    """

    regular_user = User(username="regular_user", email="regular@example.com", role="user")
    regular_user.set_password("user_password")
    db_session.add(regular_user)
    db_session.commit()

    # Set up authentication in session
    with client.session_transaction() as sess:
        sess["user_id"] = regular_user.id
        sess["username"] = regular_user.username
        sess["role"] = regular_user.role

    return regular_user


def setup_test_authentication(client, db_session, username="test_user", email="test@example.com", role="admin"):
    """
    Helper function to set up test authentication.
    Can be used when fixtures are not suitable.

    Args:
        client: Flask test client
        db_session: Database session
        username: Username for test user
        email: Email for test user
        role: Role for test user

    Returns:
        User: Created test user
    """

    test_user = User(username=username, email=email, role=role)
    test_user.set_password("password")
    db_session.add(test_user)
    db_session.commit()

    # Set up authentication in session
    with client.session_transaction() as sess:
        sess["user_id"] = test_user.id
        sess["username"] = test_user.username
        sess["role"] = test_user.role

    return test_user
