"""
Tests for User model
"""

from src.models.user import User, db


class TestUserModel:
    """Test User model functionality"""

    def test_user_creation(self, app_context):
        """Test basic user creation"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "employee"
        assert user.password_hash is not None

    def test_user_repr(self, app_context):
        """Test user string representation"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        expected = "<User testuser>"
        assert repr(user) == expected

    def test_password_hashing(self, app_context):
        """Test password hashing and verification"""
        user = User(username="testuser", email="test@example.com", role="employee")
        test_password = "mysecretpassword"  # noqa: S105
        user.set_password(test_password)

        # Password should be hashed, not stored in plain text
        assert user.password_hash != test_password
        assert user.password_hash is not None

        # Should be able to verify correct password
        assert user.check_password(test_password) is True

        # Should reject incorrect password
        assert user.check_password("wrongpassword") is False

    def test_user_roles(self, app_context):
        """Test user role functionality"""
        admin_user = User(username="admin", email="admin@test.com", role="admin")
        employee_user = User(username="employee", email="employee@test.com", role="employee")
        client_user = User(username="client", email="client@test.com", role="client")

        # Test role checking
        assert admin_user.has_role("admin") is True
        assert admin_user.has_role("employee") is False
        assert employee_user.has_role("employee") is True
        assert client_user.has_role("client") is True

        # Test admin access
        assert admin_user.can_access_admin() is True
        assert employee_user.can_access_admin() is False
        assert client_user.can_access_admin() is False

        # Test data management access
        assert admin_user.can_manage_data() is True
        assert employee_user.can_manage_data() is True
        assert client_user.can_manage_data() is False

    def test_create_admin_user(self, app_context):
        """Test admin user creation utility"""
        # Authentication handled by authenticated_test_user fixture
        admin_user = User.create_admin_user(password="admin123")

        assert admin_user.username == "admin"
        assert admin_user.email == "admin@landscape.com"
        assert admin_user.role == "admin"
        assert admin_user.check_password("admin123") is True

    def test_create_admin_user_custom(self, app_context):
        """Test admin user creation with custom parameters"""
        # Authentication handled by authenticated_test_user fixture
        test_password = "custompass123"  # noqa: S105
        admin_user = User.create_admin_user(username="custom_admin", email="custom@test.com", password=test_password)

        assert admin_user.username == "custom_admin"
        assert admin_user.email == "custom@test.com"
        assert admin_user.role == "admin"
        assert admin_user.check_password(test_password) is True

    def test_user_to_dict(self, app_context):
        """Test user dictionary conversion"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        user_dict = user.to_dict()
        expected = {
            "id": user.id,
            "username": "testuser",
            "email": "test@example.com",
            "role": "employee",
            "is_active": True,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
        assert user_dict == expected
