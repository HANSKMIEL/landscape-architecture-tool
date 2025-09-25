"""
Enhanced authentication routes with comprehensive user management
"""
import csv
import io
import logging
from datetime import datetime
from typing import List, Optional

from flask import Blueprint, current_app, jsonify, request, session
from pydantic import BaseModel, EmailStr, ValidationError
from werkzeug.utils import secure_filename

from src.models.user import User, UserSession, db

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

# Pydantic schemas for validation
class LoginSchema(BaseModel):
    username: str
    password: str

class PasswordResetRequestSchema(BaseModel):
    email: EmailStr

class PasswordResetSchema(BaseModel):
    token: str
    new_password: str

class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: Optional[str] = None
    role: str = "user"
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None

class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class BulkUserSchema(BaseModel):
    users: List[UserCreateSchema]

class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str

def require_auth(f):
    """Decorator to require authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user = User.query.get(session["user_id"])
        if not user or not user.is_active:
            session.clear()
            return jsonify({"error": "Invalid session"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_role(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return jsonify({"error": "Authentication required"}), 401
            
            user = User.query.get(session["user_id"])
            if not user or not user.is_active:
                session.clear()
                return jsonify({"error": "Invalid session"}), 401
            
            if not user.has_permission(required_role):
                return jsonify({"error": "Insufficient permissions"}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """Enhanced user login with account locking"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        schema = LoginSchema(**data)
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == schema.username) | (User.email == schema.username)
        ).first()
        
        if not user:
            logger.warning(f"Login attempt with non-existent user: {schema.username}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        if not user.is_active:
            logger.warning(f"Login attempt with inactive user: {user.username}")
            return jsonify({"error": "Account is deactivated"}), 401
        
        if user.is_account_locked():
            logger.warning(f"Login attempt with locked account: {user.username}")
            return jsonify({"error": "Account is temporarily locked due to failed login attempts"}), 423
        
        if not user.check_password(schema.password):
            user.record_failed_login()
            db.session.commit()
            logger.warning(f"Failed login attempt for user: {user.username}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Successful login
        user.record_successful_login()
        
        # Create session
        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role
        session.permanent = True
        
        # Create session tracking record
        user_session = UserSession(
            user_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent")
        )
        db.session.add(user_session)
        db.session.commit()
        
        logger.info(f"Successful login for user: {user.username}")
        
        return jsonify({
            "message": "Login successful",
            "user": user.to_dict(),
            "session_token": user_session.session_token
        }), 200
        
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/auth/logout", methods=["POST"])
@require_auth
def logout():
    """User logout"""
    try:
        user_id = session.get("user_id")
        
        # Invalidate all user sessions
        UserSession.query.filter_by(user_id=user_id, is_active=True).update({"is_active": False})
        db.session.commit()
        
        session.clear()
        
        return jsonify({"message": "Logout successful"}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/auth/me", methods=["GET"])
@require_auth
def get_current_user():
    """Get current user information"""
    try:
        user = User.query.get(session["user_id"])
        return jsonify({"user": user.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/auth/change-password", methods=["POST"])
@require_auth
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        schema = ChangePasswordSchema(**data)
        
        user = User.query.get(session["user_id"])
        
        if not user.check_password(schema.current_password):
            return jsonify({"error": "Current password is incorrect"}), 400
        
        user.set_password(schema.new_password)
        db.session.commit()
        
        logger.info(f"Password changed for user: {user.username}")
        
        return jsonify({"message": "Password changed successfully"}), 200
        
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/auth/forgot-password", methods=["POST"])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        schema = PasswordResetRequestSchema(**data)
        
        user = User.query.filter_by(email=schema.email).first()
        
        if user and user.is_active:
            reset_token = user.generate_reset_token()
            db.session.commit()
            
            # TODO: Send email with reset token
            # For now, we'll return the token (in production, this should be sent via email)
            logger.info(f"Password reset requested for user: {user.username}")
            
            # In production, don't return the token
            if current_app.config.get("TESTING") or current_app.config.get("DEBUG"):
                return jsonify({
                    "message": "Password reset token generated",
                    "reset_token": reset_token  # Only for testing
                }), 200
            else:
                return jsonify({
                    "message": "If the email exists, a password reset link has been sent"
                }), 200
        
        # Always return success to prevent email enumeration
        return jsonify({
            "message": "If the email exists, a password reset link has been sent"
        }), 200
        
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/auth/reset-password", methods=["POST"])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        schema = PasswordResetSchema(**data)
        
        user = User.query.filter_by(reset_token=schema.token).first()
        
        if not user or not user.verify_reset_token(schema.token):
            return jsonify({"error": "Invalid or expired reset token"}), 400
        
        user.set_password(schema.new_password)
        user.clear_reset_token()
        db.session.commit()
        
        logger.info(f"Password reset completed for user: {user.username}")
        
        return jsonify({"message": "Password reset successful"}), 200
        
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# User Management Routes (Admin only)

@auth_bp.route("/users", methods=["GET"])
@require_role("admin")
def list_users():
    """List all users (admin only)"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        search = request.args.get("search", "")
        role_filter = request.args.get("role", "")
        
        query = User.query
        
        if search:
            query = query.filter(
                (User.username.contains(search)) |
                (User.email.contains(search)) |
                (User.first_name.contains(search)) |
                (User.last_name.contains(search))
            )
        
        if role_filter:
            query = query.filter(User.role == role_filter)
        
        users = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "users": [user.to_dict(include_sensitive=True) for user in users.items],
            "total": users.total,
            "pages": users.pages,
            "current_page": page,
            "per_page": per_page
        }), 200
        
    except Exception as e:
        logger.error(f"List users error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/users", methods=["POST"])
@require_role("admin")
def create_user():
    """Create new user (admin only)"""
    try:
        data = request.get_json()
        schema = UserCreateSchema(**data)
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == schema.username) | (User.email == schema.email)
        ).first()
        
        if existing_user:
            return jsonify({"error": "Username or email already exists"}), 409
        
        # Create user
        user = User(
            username=schema.username,
            email=schema.email,
            password=schema.password,
            role=schema.role,
            first_name=schema.first_name,
            last_name=schema.last_name,
            phone=schema.phone,
            company=schema.company,
            notes=schema.notes
        )
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User created: {user.username} by {session.get('username')}")
        
        return jsonify({
            "message": "User created successfully",
            "user": user.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Create user error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/users/<int:user_id>", methods=["PUT"])
@require_role("admin")
def update_user(user_id):
    """Update user (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        schema = UserUpdateSchema(**data)
        
        # Update fields
        for field, value in schema.dict(exclude_unset=True).items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        db.session.commit()
        
        logger.info(f"User updated: {user.username} by {session.get('username')}")
        
        return jsonify({
            "message": "User updated successfully",
            "user": user.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@require_role("admin")
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting self
        if user.id == session.get("user_id"):
            return jsonify({"error": "Cannot delete your own account"}), 400
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        logger.info(f"User deleted: {username} by {session.get('username')}")
        
        return jsonify({"message": "User deleted successfully"}), 200
        
    except Exception as e:
        logger.error(f"Delete user error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/users/bulk-import", methods=["POST"])
@require_role("admin")
def bulk_import_users():
    """Bulk import users from CSV (admin only)"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.lower().endswith(".csv"):
            return jsonify({"error": "File must be a CSV"}), 400
        
        # Read CSV content
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        created_users = []
        errors = []
        
        for row_num, row in enumerate(csv_input, start=2):  # Start at 2 for header
            try:
                # Validate required fields
                if not row.get("username") or not row.get("email"):
                    errors.append(f"Row {row_num}: Username and email are required")
                    continue
                
                # Check if user already exists
                existing_user = User.query.filter(
                    (User.username == row["username"]) | (User.email == row["email"])
                ).first()
                
                if existing_user:
                    errors.append(f"Row {row_num}: Username or email already exists")
                    continue
                
                # Create user
                user = User(
                    username=row["username"],
                    email=row["email"],
                    password=row.get("password"),  # Will generate temp password if None
                    role=row.get("role", "user"),
                    first_name=row.get("first_name"),
                    last_name=row.get("last_name"),
                    phone=row.get("phone"),
                    company=row.get("company"),
                    notes=row.get("notes")
                )
                
                db.session.add(user)
                created_users.append(user.username)
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        if created_users:
            db.session.commit()
        
        logger.info(f"Bulk import completed: {len(created_users)} users created by {session.get('username')}")
        
        return jsonify({
            "message": f"Bulk import completed",
            "created_users": created_users,
            "errors": errors,
            "total_created": len(created_users),
            "total_errors": len(errors)
        }), 200
        
    except Exception as e:
        logger.error(f"Bulk import error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@require_role("admin")
def admin_reset_user_password(user_id):
    """Admin reset user password"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Generate new temporary password
        temp_password = user.generate_temporary_password()
        user.set_password(temp_password)
        db.session.commit()
        
        logger.info(f"Password reset for user: {user.username} by admin: {session.get('username')}")
        
        return jsonify({
            "message": "Password reset successfully",
            "temporary_password": temp_password  # In production, send via email
        }), 200
        
    except Exception as e:
        logger.error(f"Admin reset password error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/users/<int:user_id>/unlock", methods=["POST"])
@require_role("admin")
def unlock_user_account(user_id):
    """Unlock user account (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        
        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()
        
        logger.info(f"Account unlocked for user: {user.username} by admin: {session.get('username')}")
        
        return jsonify({"message": "Account unlocked successfully"}), 200
        
    except Exception as e:
        logger.error(f"Unlock account error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
