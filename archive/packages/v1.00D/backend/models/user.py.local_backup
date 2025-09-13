"""
Enhanced User model with comprehensive user management features
"""
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from src import db

Base = declarative_base()

class User(db.Model):
    """Enhanced User model with role-based access control and password reset"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role-based access control
    role = db.Column(db.String(20), nullable=False, default='user')
    # Roles: developer, sysadmin, admin, user, client
    
    # User status and metadata
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Password reset functionality
    reset_token = db.Column(db.String(100), nullable=True, index=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Additional user information
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    company = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Login tracking
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, username, email, password=None, role='user', **kwargs):
        self.username = username
        self.email = email
        self.role = role
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.phone = kwargs.get('phone')
        self.company = kwargs.get('company')
        self.notes = kwargs.get('notes')
        
        if password:
            self.set_password(password)
        else:
            # Generate temporary password if none provided
            temp_password = self.generate_temporary_password()
            self.set_password(temp_password)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
        self.updated_at = datetime.utcnow()
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def generate_temporary_password(self):
        """Generate a secure temporary password"""
        return secrets.token_urlsafe(12)
    
    def generate_reset_token(self):
        """Generate password reset token"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        self.updated_at = datetime.utcnow()
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Verify password reset token"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        
        if datetime.utcnow() > self.reset_token_expires:
            self.clear_reset_token()
            return False
        
        return self.reset_token == token
    
    def clear_reset_token(self):
        """Clear password reset token"""
        self.reset_token = None
        self.reset_token_expires = None
        self.updated_at = datetime.utcnow()
    
    def is_account_locked(self):
        """Check if account is locked due to failed login attempts"""
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        return False
    
    def record_failed_login(self):
        """Record failed login attempt"""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts for 30 minutes
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        self.updated_at = datetime.utcnow()
    
    def record_successful_login(self):
        """Record successful login"""
        self.last_login = datetime.utcnow()
        self.failed_login_attempts = 0
        self.locked_until = None
        self.updated_at = datetime.utcnow()
    
    def has_permission(self, required_role):
        """Check if user has required permission level"""
        role_hierarchy = {
            'client': 1,
            'user': 2,
            'admin': 3,
            'sysadmin': 4,
            'developer': 5
        }
        
        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def get_full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'company': self.company,
            'full_name': self.get_full_name(),
            'is_locked': self.is_account_locked()
        }
        
        if include_sensitive:
            data.update({
                'failed_login_attempts': self.failed_login_attempts,
                'locked_until': self.locked_until.isoformat() if self.locked_until else None,
                'notes': self.notes
            })
        
        return data
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

    @staticmethod
    def create_admin_user(username="admin", email="admin@landscape.com", password=None):
        """Create default admin user for initial setup"""
        if password is None:
            import os
            import secrets
            import string

            # Use environment variable or generate secure random password
            password = os.getenv("DEFAULT_ADMIN_PASSWORD")
            if not password:
                # Generate a secure random password if none provided
                alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
                password = "".join(secrets.choice(alphabet) for _ in range(16))

                # Only print the password in non-production environments
                if os.getenv("FLASK_ENV", "production") != "production":
                    print(f"IMPORTANT: Generated admin password: {password}")
                    print("Please save this password securely and set DEFAULT_ADMIN_PASSWORD environment variable.")
                else:
                    print(
                        "IMPORTANT: Admin password was generated automatically. Please set the DEFAULT_ADMIN_PASSWORD environment variable securely in production."
                    )
        user = User(username=username, email=email, role="admin")
        user.set_password(password)
        return user


class UserSession(db.Model):
    """User session tracking"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __init__(self, user_id, ip_address=None, user_agent=None, duration_hours=24):
        self.user_id = user_id
        self.session_token = secrets.token_urlsafe(32)
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
    
    def is_valid(self):
        """Check if session is still valid"""
        return self.is_active and datetime.utcnow() < self.expires_at
    
    def extend_session(self, hours=24):
        """Extend session expiration"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
    
    def invalidate(self):
        """Invalidate session"""
        self.is_active = False
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_token': self.session_token,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_active': self.is_active
        }
