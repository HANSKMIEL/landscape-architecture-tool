"""
Tests for User model
"""

from src.models.user import User, db


class TestUserModel:
    """Test User model functionality"""

    def test_user_creation(self, app_context):
        """Test basic user creation"""
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_user_repr(self, app_context):
        """Test user string representation"""
        user = User(username="testuser", email="test@example.com")
        expected = "<User testuser>"
        assert repr(user) == expected

    def test_user_to_dict(self, app_context):
        """Test user dictionary conversion"""
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()

        user_dict = user.to_dict()
        expected = {"id": user.id, "username": "testuser", "email": "test@example.com"}
        assert user_dict == expected
