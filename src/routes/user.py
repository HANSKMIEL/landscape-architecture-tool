from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, jsonify, request, session
from pydantic import BaseModel, ValidationError
from werkzeug.security import generate_password_hash

from src.models.user import User, db

user_bp = Blueprint("user", __name__)


# Pydantic schemas for validation
class LoginSchema(BaseModel):
    username: str
    password: str


class UserCreateSchema(BaseModel):
    username: str
    email: str
    password: str
    role: str = "employee"


class UserUpdateSchema(BaseModel):
    username: str | None = None
    email: str | None = None
    role: str | None = None
    is_active: bool | None = None


def login_required(f):
    """Decorator to require authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401

        user = User.query.get(session["user_id"])
        if not user or not user.can_access_admin():
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)

    return decorated_function


def data_access_required(f):
    """Decorator to require data management access (admin or employee)"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401

        user = User.query.get(session["user_id"])
        if not user or not user.can_manage_data():
            return jsonify({"error": "Data management access required"}), 403
        return f(*args, **kwargs)

    return decorated_function


@user_bp.route("/auth/login", methods=["POST"])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        schema = LoginSchema(**data)

        user = User.query.filter_by(username=schema.username).first()

        if user and user.check_password(schema.password) and user.is_active:
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            session.permanent = True

            return jsonify({"message": "Login successful", "user": user.to_dict()}), 200
        return jsonify({"error": "Invalid credentials"}), 401

    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400


@user_bp.route("/auth/logout", methods=["POST"])
@login_required
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@user_bp.route("/auth/me", methods=["GET"])
@login_required
def get_current_user():
    """Get current user information"""
    user = User.query.get(session["user_id"])
    if not user:
        session.clear()
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user.to_dict()}), 200


@user_bp.route("/auth/status", methods=["GET"])
def auth_status():
    """Check authentication status"""
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user and user.is_active:
            return jsonify({"authenticated": True, "user": user.to_dict()}), 200

    return jsonify({"authenticated": False}), 200


@user_bp.route("/users", methods=["GET"])
@admin_required
def get_users():
    """Get all users (admin only)"""
    users = User.query.all()
    return jsonify({"users": [user.to_dict() for user in users]})


@user_bp.route("/users", methods=["POST"])
@admin_required
def create_user():
    """Create new user (admin only)"""
    try:
        data = request.get_json()
        schema = UserCreateSchema(**data)

        # Check if user already exists
        existing_user = User.query.filter((User.username == schema.username) | (User.email == schema.email)).first()

        if existing_user:
            return jsonify({"error": "User with this username or email already exists"}), 409

        user = User(username=schema.username, email=schema.email, role=schema.role)
        user.set_password(schema.password)

        db.session.add(user)
        db.session.commit()

        return jsonify({"user": user.to_dict()}), 201

    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400


@user_bp.route("/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    """Get specific user (admin only)"""
    user = User.query.get_or_404(user_id)
    return jsonify({"user": user.to_dict()})


@user_bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    """Update user (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        schema = UserUpdateSchema(**data)

        if schema.username is not None:
            user.username = schema.username
        if schema.email is not None:
            user.email = schema.email
        if schema.role is not None:
            user.role = schema.role
        if schema.is_active is not None:
            user.is_active = schema.is_active

        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({"user": user.to_dict()})

    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400


@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    user = User.query.get_or_404(user_id)

    # Prevent deletion of the last admin user
    if user.role == "admin":
        admin_count = User.query.filter_by(role="admin", is_active=True).count()
        if admin_count <= 1:
            return jsonify({"error": "Cannot delete the last admin user"}), 400

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200


@user_bp.route("/auth/change-password", methods=["POST"])
@login_required
def change_password():
    """Change user's password"""
    try:
        data = request.get_json()
        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not current_password or not new_password:
            return jsonify({"error": "Current and new passwords are required"}), 400

        user = User.query.get(session["user_id"])
        if not user.check_password(current_password):
            return jsonify({"error": "Current password is incorrect"}), 400

        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({"message": "Password changed successfully"}), 200

    except Exception:
        return jsonify({"error": "Failed to change password"}), 500
