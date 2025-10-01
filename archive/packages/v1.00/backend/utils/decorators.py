"""Centralized authentication and authorization decorators."""

from functools import wraps

from flask import jsonify, session

from src.models.user import User, db


def login_required(f):
    """Decorator to require user login."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required"}), 401

        user = db.session.get(User, session["user_id"])
        if not user or not user.is_active:
            session.pop("user_id", None)
            return jsonify({"error": "User not found or inactive"}), 401

        return f(*args, **kwargs)

    return decorated_function


def data_access_required(f):
    """Decorator to require admin or employee role."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required"}), 401

        user = db.session.get(User, session["user_id"])
        if not user or not user.is_active:
            session.pop("user_id", None)
            return jsonify({"error": "User not found or inactive"}), 401

        if user.role not in ["admin", "employee"]:
            return jsonify({"error": "Insufficient permissions"}), 403

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Decorator to require admin role."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required"}), 401

        user = db.session.get(User, session["user_id"])
        if not user or not user.is_active:
            session.pop("user_id", None)
            return jsonify({"error": "User not found or inactive"}), 401

        if user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return f(*args, **kwargs)

    return decorated_function
