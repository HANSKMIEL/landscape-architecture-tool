"""API routes for photo upload and management."""

import os
from functools import wraps

from flask import Blueprint, current_app, jsonify, request, send_file, session
from flask_cors import cross_origin
from werkzeug.exceptions import RequestEntityTooLarge

from src.models.photo import PhotoCategory
from src.models.user import User
from src.services.photo_service import PhotoService

photos_bp = Blueprint("photos", __name__)


def get_photo_service():
    """Get photo service instance (lazy initialization)"""
    return PhotoService()


def login_required(f):
    """Decorator to require authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)

    return decorated_function


def get_current_user():
    """Get current authenticated user"""
    if "user_id" not in session:
        return None
    return User.query.get(session["user_id"])


@photos_bp.route("/upload", methods=["POST"])
@cross_origin(supports_credentials=True)
@login_required
def upload_photo():
    """Upload a photo with metadata."""
    try:
        # Check if file is present
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Get form data
        category_str = request.form.get("category", "example")
        entity_id = request.form.get("entity_id", type=int)
        title = request.form.get("title")
        description = request.form.get("description")
        is_primary = request.form.get("is_primary", "false").lower() == "true"

        # Validate category
        try:
            category = PhotoCategory(category_str)
        except ValueError:
            return jsonify({"error": f"Invalid category: {category_str}"}), 400

        # Get current user
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "Authentication required"}), 401

        # Upload photo
        result = get_photo_service().upload_photo(
            file=file,
            category=category,
            entity_id=entity_id,
            title=title,
            description=description,
            uploaded_by_id=current_user.id,
            is_primary=is_primary,
        )

        if result["success"]:
            return jsonify(result), 201
        return jsonify({"error": result["error"]}), 400

    except RequestEntityTooLarge:
        return jsonify({"error": "File too large"}), 413
    except Exception as e:
        current_app.logger.error(f"Photo upload error: {e!s}")
        return jsonify({"error": "Upload failed"}), 500


@photos_bp.route("/", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_photos():
    """Get photos with optional filtering."""
    try:
        # Get query parameters
        category_str = request.args.get("category")
        entity_id = request.args.get("entity_id", type=int)
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)

        # Validate category if provided
        category = None
        if category_str:
            try:
                category = PhotoCategory(category_str)
            except ValueError:
                return jsonify({"error": f"Invalid category: {category_str}"}), 400

        # Get photos
        photos = get_photo_service().get_photos(
            category=category, entity_id=entity_id, limit=min(limit, 100), offset=offset  # Max 100 photos per request
        )

        return jsonify({"photos": photos, "count": len(photos), "offset": offset, "limit": limit})

    except Exception as e:
        current_app.logger.error(f"Error fetching photos: {e!s}")
        return jsonify({"error": "Failed to fetch photos"}), 500


@photos_bp.route("/<int:photo_id>", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_photo(photo_id):
    """Get specific photo metadata."""
    try:
        from src.models.photo import Photo

        photo = Photo.query.get(photo_id)
        if not photo:
            return jsonify({"error": "Photo not found"}), 404

        return jsonify({"photo": photo.to_dict()})

    except Exception as e:
        current_app.logger.error(f"Error fetching photo {photo_id}: {e!s}")
        return jsonify({"error": "Failed to fetch photo"}), 500


@photos_bp.route("/file/<int:photo_id>", methods=["GET"])
@cross_origin(supports_credentials=True)
def serve_photo(photo_id):
    """Serve photo file."""
    try:
        from src.models.photo import Photo

        photo = Photo.query.get(photo_id)
        if not photo:
            return jsonify({"error": "Photo not found"}), 404

        # Check if file exists
        if not photo.file_path or not os.path.exists(photo.file_path):
            return jsonify({"error": "Photo file not found"}), 404

        return send_file(
            photo.file_path, mimetype=photo.mime_type, as_attachment=False, download_name=photo.original_filename
        )

    except Exception as e:
        current_app.logger.error(f"Error serving photo {photo_id}: {e!s}")
        return jsonify({"error": "Failed to serve photo"}), 500


@photos_bp.route("/thumbnail/<int:photo_id>", methods=["GET"])
@cross_origin(supports_credentials=True)
def serve_thumbnail(photo_id):
    """Serve photo thumbnail."""
    try:
        from src.models.photo import Photo

        photo = Photo.query.get(photo_id)
        if not photo:
            return jsonify({"error": "Photo not found"}), 404

        # Check if thumbnail exists
        if not photo.thumbnail_path or not os.path.exists(photo.thumbnail_path):
            # Fall back to original file if thumbnail doesn't exist
            if photo.file_path and os.path.exists(photo.file_path):
                return send_file(
                    photo.file_path,
                    mimetype=photo.mime_type,
                    as_attachment=False,
                    download_name=f"thumb_{photo.original_filename}",
                )
            return jsonify({"error": "Thumbnail not found"}), 404

        return send_file(
            photo.thumbnail_path,
            mimetype="image/jpeg",
            as_attachment=False,
            download_name=f"thumb_{photo.original_filename}",
        )

    except Exception as e:
        current_app.logger.error(f"Error serving thumbnail {photo_id}: {e!s}")
        return jsonify({"error": "Failed to serve thumbnail"}), 500


@photos_bp.route("/<int:photo_id>", methods=["PUT"])
@cross_origin(supports_credentials=True)
@login_required
def update_photo(photo_id):
    """Update photo metadata."""
    try:
        from src.models.photo import Photo
        from src.models.user import db

        photo = Photo.query.get(photo_id)
        if not photo:
            return jsonify({"error": "Photo not found"}), 404

        # Get current user
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "Authentication required"}), 401

        # Check if user can edit (owner or admin)
        if photo.uploaded_by_id != current_user.id and current_user.role != "admin":
            return jsonify({"error": "Permission denied"}), 403

        data = request.get_json()

        # Update allowed fields
        if "title" in data:
            photo.title = data["title"]
        if "description" in data:
            photo.description = data["description"]
        if "alt_text" in data:
            photo.alt_text = data["alt_text"]
        if "is_public" in data:
            photo.is_public = data["is_public"]

        db.session.commit()

        return jsonify({"photo": photo.to_dict(), "message": "Photo updated successfully"})

    except Exception as e:
        from src.models.user import db

        db.session.rollback()
        current_app.logger.error(f"Error updating photo {photo_id}: {e!s}")
        return jsonify({"error": "Failed to update photo"}), 500


@photos_bp.route("/<int:photo_id>/primary", methods=["POST"])
@cross_origin(supports_credentials=True)
@login_required
def set_primary_photo(photo_id):
    """Set photo as primary for its entity."""
    try:
        from src.models.photo import Photo

        photo = Photo.query.get(photo_id)
        if not photo:
            return jsonify({"error": "Photo not found"}), 404

        # Get current user
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "Authentication required"}), 401

        # Determine entity ID based on category
        entity_id = None
        if photo.category == PhotoCategory.PLANT and photo.plant_id:
            entity_id = photo.plant_id
        elif photo.category == PhotoCategory.MATERIAL and photo.material_id:
            entity_id = photo.material_id
        elif photo.category == PhotoCategory.PROPERTY and photo.client_id:
            entity_id = photo.client_id
        elif photo.category == PhotoCategory.PROJECT and photo.project_id:
            entity_id = photo.project_id

        if not entity_id:
            return jsonify({"error": "Photo not associated with any entity"}), 400

        # Set as primary
        result = get_photo_service().set_primary_photo(photo_id, entity_id, photo.category)

        if result["success"]:
            return jsonify(result)
        return jsonify({"error": result["error"]}), 400

    except Exception as e:
        current_app.logger.error(f"Error setting primary photo {photo_id}: {e!s}")
        return jsonify({"error": "Failed to set primary photo"}), 500


@photos_bp.route("/<int:photo_id>", methods=["DELETE"])
@cross_origin(supports_credentials=True)
@login_required
def delete_photo(photo_id):
    """Delete photo."""
    try:
        from src.models.photo import Photo

        photo = Photo.query.get(photo_id)
        if not photo:
            return jsonify({"error": "Photo not found"}), 404

        # Get current user
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "Authentication required"}), 401

        # Check if user can delete (owner or admin)
        if photo.uploaded_by_id != current_user.id and current_user.role != "admin":
            return jsonify({"error": "Permission denied"}), 403

        # Delete photo
        result = get_photo_service().delete_photo(photo_id)

        if result["success"]:
            return jsonify(result)
        return jsonify({"error": result["error"]}), 400

    except Exception as e:
        current_app.logger.error(f"Error deleting photo {photo_id}: {e!s}")
        return jsonify({"error": "Failed to delete photo"}), 500


@photos_bp.route("/categories", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_photo_categories():
    """Get available photo categories."""
    return jsonify(
        {"categories": [{"value": category.value, "label": category.value.title()} for category in PhotoCategory]}
    )


# Error handlers
@photos_bp.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({"error": "File too large"}), 413
