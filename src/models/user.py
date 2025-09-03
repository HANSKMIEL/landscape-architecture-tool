from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User model with authentication capabilities"""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="employee")  # admin, employee, client
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role

    def can_access_admin(self):
        """Check if user can access admin features"""
        return self.role == "admin"

    def can_manage_data(self):
        """Check if user can manage business data (suppliers, plants, projects)"""
        return self.role in ["admin", "employee"]

    def to_dict(self, include_sensitive=False):
        """Convert to dictionary, optionally including sensitive fields"""
        result = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_sensitive:
            # Only include sensitive fields when explicitly requested (for admin use)
            pass  # password_hash should never be included in API responses
            
        return result

    @staticmethod
    def create_admin_user(username="admin", email="admin@landscape.com", password="admin123"):
        """Create default admin user for initial setup"""
        user = User(username=username, email=email, role="admin")
        user.set_password(password)
        return user
