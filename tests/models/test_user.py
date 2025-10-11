"""Tests for User model."""

from datetime import datetime, timedelta

import pytest

from src.models.user import User, UserSession, db


@pytest.mark.usefixtures("app_context")
class TestUserModel:
    """Test User model functionality"""

    def test_user_creation(self):
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

    def test_user_repr(self):
        """Test user string representation"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        expected = "<User testuser>"
        assert repr(user) == expected

    def test_password_hashing(self):
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

    def test_user_roles(self):
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

    def test_create_admin_user(self):
        """Test admin user creation utility"""
        # Authentication handled by authenticated_test_user fixture
        admin_user = User.create_admin_user(password="admin123")  # noqa: S106 - test credential

        assert admin_user.username == "admin"
        assert admin_user.email == "admin@landscape.com"
        assert admin_user.role == "admin"
        assert admin_user.check_password("admin123") is True

    def test_create_admin_user_custom(self):
        """Test admin user creation with custom parameters"""
        # Authentication handled by authenticated_test_user fixture
        test_password = "custompass123"  # noqa: S105
        admin_user = User.create_admin_user(username="custom_admin", email="custom@test.com", password=test_password)

        assert admin_user.username == "custom_admin"
        assert admin_user.email == "custom@test.com"
        assert admin_user.role == "admin"
        assert admin_user.check_password(test_password) is True

    def test_user_to_dict(self):
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
            "first_name": None,
            "last_name": None,
            "full_name": "testuser",
            "phone": None,
            "company": None,
            "notes": None,
            "is_active": True,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login": None,
        }
        assert user_dict == expected

    def test_user_to_dict_with_sensitive(self):
        """Test user dictionary conversion with sensitive data"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        # Record a failed login to test sensitive data
        user.record_failed_login()
        db.session.commit()

        user_dict = user.to_dict(include_sensitive=True)

        # Check that sensitive fields are included
        assert "failed_login_attempts" in user_dict
        assert "is_locked" in user_dict
        assert "locked_until" in user_dict
        assert user_dict["failed_login_attempts"] == 1
        assert user_dict["is_locked"] is False

    def test_generate_temporary_password(self):
        """Test temporary password generation"""
        user = User(username="testuser", email="test@example.com", role="employee")
        temp_password = user.generate_temporary_password()

        # Temporary password should be a non-empty string
        assert isinstance(temp_password, str)
        assert len(temp_password) > 0

        # Each generated password should be unique
        temp_password2 = user.generate_temporary_password()
        assert temp_password != temp_password2

    def test_password_reset_token_generation(self):
        """Test password reset token generation"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        # Generate reset token
        token = user.generate_reset_token()

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        assert user.reset_token == token
        assert user.reset_token_expires is not None

    def test_password_reset_token_verification(self):
        """Test password reset token verification"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        # Generate reset token
        token = user.generate_reset_token()
        db.session.commit()

        # Valid token should verify
        assert user.verify_reset_token(token) is True

        # Invalid token should not verify
        assert user.verify_reset_token("invalid_token") is False

        # Missing token should not verify
        user.clear_reset_token()
        db.session.commit()
        assert user.verify_reset_token(token) is False

    def test_password_reset_token_expiration(self):
        """Test password reset token expiration"""
        from datetime import datetime, timedelta

        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        # Generate reset token
        token = user.generate_reset_token()

        # Set token to expired
        user.reset_token_expires = datetime.utcnow() - timedelta(hours=1)
        db.session.commit()

        # Expired token should not verify
        assert user.verify_reset_token(token) is False

    def test_clear_reset_token(self):
        """Test clearing password reset token"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        # Generate reset token
        user.generate_reset_token()
        db.session.commit()

        assert user.reset_token is not None
        assert user.reset_token_expires is not None

        # Clear the token
        user.clear_reset_token()
        db.session.commit()

        assert user.reset_token is None
        assert user.reset_token_expires is None

    def test_record_successful_login(self):
        """Test recording successful login"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        # Record failed logins first
        user.failed_login_attempts = 3
        db.session.commit()

        # Record successful login
        user.record_successful_login()
        db.session.commit()

        assert user.last_login is not None
        assert user.failed_login_attempts == 0
        assert user.locked_until is None

    def test_record_failed_login(self):
        """Test recording failed login attempts"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        # Record failed logins
        for i in range(3):
            user.record_failed_login()
            db.session.commit()
            assert user.failed_login_attempts == i + 1

    def test_account_locking(self):
        """Test account locking after failed login attempts"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        # Account should not be locked initially
        assert user.is_account_locked() is False

        # Record 5 failed login attempts (triggers lock)
        for _ in range(5):
            user.record_failed_login()
        db.session.commit()

        # Account should be locked now
        assert user.is_account_locked() is True
        assert user.locked_until is not None

    def test_has_permission(self):
        """Test permission level checking"""
        client_user = User(username="client", email="client@test.com", role="client")
        user_user = User(username="user", email="user@test.com", role="user")
        employee_user = User(username="employee", email="employee@test.com", role="employee")
        admin_user = User(username="admin", email="admin@test.com", role="admin")
        sysadmin_user = User(username="sysadmin", email="sysadmin@test.com", role="sysadmin")
        developer_user = User(username="developer", email="developer@test.com", role="developer")

        # Test client permissions (level 1)
        assert client_user.has_permission("client") is True
        assert client_user.has_permission("user") is False
        assert client_user.has_permission("admin") is False

        # Test user/employee permissions (level 2)
        assert user_user.has_permission("client") is True
        assert user_user.has_permission("user") is True
        assert user_user.has_permission("admin") is False

        assert employee_user.has_permission("client") is True
        assert employee_user.has_permission("employee") is True
        assert employee_user.has_permission("admin") is False

        # Test admin permissions (level 3)
        assert admin_user.has_permission("client") is True
        assert admin_user.has_permission("user") is True
        assert admin_user.has_permission("admin") is True
        assert admin_user.has_permission("sysadmin") is False

        # Test sysadmin permissions (level 4)
        assert sysadmin_user.has_permission("admin") is True
        assert sysadmin_user.has_permission("sysadmin") is True
        assert sysadmin_user.has_permission("developer") is False

        # Test developer permissions (level 5 - highest)
        assert developer_user.has_permission("admin") is True
        assert developer_user.has_permission("sysadmin") is True
        assert developer_user.has_permission("developer") is True

    def test_full_name_property(self):
        """Test full_name property with different scenarios"""
        # Test with both first and last name
        user1 = User(username="user1", email="user1@test.com", role="employee")
        user1.first_name = "John"
        user1.last_name = "Doe"
        assert user1.full_name == "John Doe"

        # Test with only first name
        user2 = User(username="user2", email="user2@test.com", role="employee")
        user2.first_name = "Jane"
        assert user2.full_name == "Jane"

        # Test with only last name
        user3 = User(username="user3", email="user3@test.com", role="employee")
        user3.last_name = "Smith"
        assert user3.full_name == "Smith"

        # Test with no names (should return username)
        user4 = User(username="user4", email="user4@test.com", role="employee")
        assert user4.full_name == "user4"

    def test_user_init_with_kwargs(self):
        """Test User initialization with additional kwargs"""
        user = User(
            username="testuser",
            email="test@example.com",
            role="employee",
            first_name="Test",
            last_name="User",
            phone="123-456-7890",
            company="Test Company",
            notes="Test notes",
        )
        db.session.add(user)
        db.session.commit()

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "employee"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.phone == "123-456-7890"
        assert user.company == "Test Company"
        assert user.notes == "Test notes"

    def test_user_init_without_password(self):
        """Test User initialization without password generates temporary password"""
        user = User(username="testuser", email="test@example.com", role="employee")

        # Should have a password hash even without explicit password
        assert user.password_hash is not None
        assert len(user.password_hash) > 0


@pytest.mark.usefixtures("app_context")
class TestUserSessionModel:
    """Test UserSession model functionality"""

    def test_user_session_creation(self):
        """Test basic user session creation"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        session = UserSession(user_id=user.id, ip_address="192.168.1.1", user_agent="Mozilla/5.0 Test Browser")
        db.session.add(session)
        db.session.commit()

        assert session.id is not None
        assert session.user_id == user.id
        assert session.ip_address == "192.168.1.1"
        assert session.user_agent == "Mozilla/5.0 Test Browser"
        assert session.session_token is not None
        assert len(session.session_token) > 0
        assert session.is_active is True
        assert session.expires_at is not None

    def test_user_session_token_uniqueness(self):
        """Test that session tokens are unique"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        session1 = UserSession(user_id=user.id)
        session2 = UserSession(user_id=user.id)

        # Session tokens should be unique
        assert session1.session_token != session2.session_token

    def test_user_session_is_expired(self):
        """Test session expiration checking"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        session = UserSession(user_id=user.id)
        db.session.add(session)
        db.session.commit()

        # New session should not be expired
        assert session.is_expired() is False

        # Set session to expired
        session.expires_at = datetime.utcnow() - timedelta(hours=1)
        db.session.commit()

        # Session should now be expired
        assert session.is_expired() is True

    def test_user_session_extend_session(self):
        """Test extending session expiration"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        session = UserSession(user_id=user.id)
        db.session.add(session)
        db.session.commit()

        original_expires = session.expires_at

        # Extend session by 48 hours
        session.extend_session(hours=48)
        db.session.commit()

        # New expiration should be later than original
        assert session.expires_at > original_expires

    def test_user_session_to_dict(self):
        """Test user session dictionary conversion"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        session = UserSession(user_id=user.id, ip_address="192.168.1.1", user_agent="Mozilla/5.0 Test Browser")
        db.session.add(session)
        db.session.commit()

        session_dict = session.to_dict()

        assert session_dict["id"] == session.id
        assert session_dict["user_id"] == user.id
        assert session_dict["session_token"] == session.session_token
        assert session_dict["ip_address"] == "192.168.1.1"
        assert session_dict["user_agent"] == "Mozilla/5.0 Test Browser"
        assert session_dict["is_active"] is True
        assert session_dict["is_expired"] is False
        assert "created_at" in session_dict
        assert "expires_at" in session_dict

    def test_user_session_relationship(self):
        """Test relationship between User and UserSession"""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        session1 = UserSession(user_id=user.id, ip_address="192.168.1.1")
        session2 = UserSession(user_id=user.id, ip_address="192.168.1.2")
        db.session.add_all([session1, session2])
        db.session.commit()

        # User should have access to their sessions
        assert len(user.sessions) == 2
        assert session1 in user.sessions
        assert session2 in user.sessions

        # Sessions should have reference to user
        assert session1.user == user
        assert session2.user == user
