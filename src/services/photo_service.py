"""Photo service for handling image uploads, processing, and management."""

import os
import uuid
from datetime import datetime
from typing import Any

from flask import current_app
from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from src.models.photo import Photo, PhotoCategory
from src.models.user import db


class PhotoService:
    """Service for managing photo uploads and processing."""

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    THUMBNAIL_SIZE = (300, 300)
    MEDIUM_SIZE = (800, 600)

    def __init__(self):
        self.upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
        self.ensure_upload_folders()

    def ensure_upload_folders(self):
        """Create upload folders if they don't exist."""
        folders = [
            os.path.join(self.upload_folder, "photos"),
            os.path.join(self.upload_folder, "photos", "plants"),
            os.path.join(self.upload_folder, "photos", "materials"),
            os.path.join(self.upload_folder, "photos", "properties"),
            os.path.join(self.upload_folder, "photos", "projects"),
            os.path.join(self.upload_folder, "photos", "examples"),
            os.path.join(self.upload_folder, "thumbnails"),
        ]

        for folder in folders:
            os.makedirs(folder, exist_ok=True)

    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        return "." in filename and filename.rsplit(".", 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def validate_file(self, file: FileStorage) -> dict[str, Any]:
        """Validate uploaded file."""
        if not file or not file.filename:
            return {"valid": False, "error": "No file provided"}

        if not self.allowed_file(file.filename):
            return {
                "valid": False,
                "error": f'File type not allowed. Allowed: {", ".join(self.ALLOWED_EXTENSIONS)}',
            }

        # Check file size (approximate)
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning

        if size > self.MAX_FILE_SIZE:
            return {
                "valid": False,
                "error": f"File too large. Maximum size: {self.MAX_FILE_SIZE // (1024*1024)}MB",
            }

        return {"valid": True, "size": size}

    def generate_filename(self, original_filename: str) -> tuple:
        """Generate unique filename while preserving extension."""
        extension = original_filename.rsplit(".", 1)[1].lower()
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{unique_id}.{extension}"
        return filename, extension

    def get_category_folder(self, category: PhotoCategory) -> str:
        """Get folder path for photo category."""
        category_folders = {
            PhotoCategory.PLANT: "plants",
            PhotoCategory.MATERIAL: "materials",
            PhotoCategory.PROPERTY: "properties",
            PhotoCategory.PROJECT: "projects",
            PhotoCategory.EXAMPLE: "examples",
            PhotoCategory.INSPIRATION: "examples",
            PhotoCategory.REFERENCE: "examples",
        }
        return os.path.join(self.upload_folder, "photos", category_folders.get(category, "general"))

    def process_image(self, file_path: str) -> dict[str, Any]:
        """Process image to get dimensions and create thumbnail."""
        try:
            with Image.open(file_path) as img:
                width, height = img.size

                # Create thumbnail
                thumbnail_path = self._create_thumbnail(img, file_path)

                return {"width": width, "height": height, "thumbnail_path": thumbnail_path}
        except Exception as e:
            current_app.logger.error(f"Error processing image {file_path}: {e!s}")
            return {"width": None, "height": None, "thumbnail_path": None}

    def _create_thumbnail(self, img: Image.Image, original_path: str) -> str | None:
        """Create thumbnail for image."""
        try:
            # Create thumbnail
            img_copy = img.copy()
            img_copy.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

            # Generate thumbnail filename
            base_name = os.path.basename(original_path)
            name, ext = os.path.splitext(base_name)
            thumbnail_name = f"thumb_{name}{ext}"
            thumbnail_path = os.path.join(self.upload_folder, "thumbnails", thumbnail_name)

            # Convert to RGB if necessary (for JPEG)
            if img_copy.mode in ("RGBA", "LA", "P"):
                img_copy = img_copy.convert("RGB")

            img_copy.save(thumbnail_path, "JPEG", quality=85)
            return thumbnail_path

        except Exception as e:
            current_app.logger.error(f"Error creating thumbnail: {e!s}")
            return None

    def upload_photo(
        self,
        file: FileStorage,
        category: PhotoCategory,
        entity_id: int | None = None,
        title: str | None = None,
        description: str | None = None,
        uploaded_by_id: int | None = None,
        is_primary: bool = False,
    ) -> dict[str, Any]:
        """Upload and process photo."""
        try:
            # Validate file
            validation = self.validate_file(file)
            if not validation["valid"]:
                return {"success": False, "error": validation["error"]}

            # Generate filename
            filename, extension = self.generate_filename(file.filename)

            # Get category folder
            category_folder = self.get_category_folder(category)
            file_path = os.path.join(category_folder, filename)

            # Save file
            file.save(file_path)

            # Process image
            image_info = self.process_image(file_path)

            # Create photo record
            photo_data = {
                "filename": filename,
                "original_filename": secure_filename(file.filename),
                "file_path": file_path,
                "thumbnail_path": image_info.get("thumbnail_path"),
                "file_size": validation["size"],
                "mime_type": file.content_type,
                "width": image_info.get("width"),
                "height": image_info.get("height"),
                "category": category,
                "title": title or file.filename,
                "description": description,
                "uploaded_by_id": uploaded_by_id,
                "is_primary": is_primary,
            }

            # Set entity relationship based on category
            if entity_id:
                if category == PhotoCategory.PLANT:
                    photo_data["plant_id"] = entity_id
                elif category == PhotoCategory.MATERIAL:
                    photo_data["material_id"] = entity_id
                elif category == PhotoCategory.PROPERTY:
                    photo_data["client_id"] = entity_id
                elif category == PhotoCategory.PROJECT:
                    photo_data["project_id"] = entity_id

            photo = Photo(**photo_data)
            db.session.add(photo)
            db.session.commit()

            return {
                "success": True,
                "photo": photo.to_dict(),
                "message": "Photo uploaded successfully",
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error uploading photo: {e!s}")

            # Clean up file if it was saved
            if "file_path" in locals() and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError as cleanup_error:
                    current_app.logger.error(f"Error cleaning up file {file_path}: {cleanup_error!s}")

            return {"success": False, "error": f"Upload failed: {e!s}"}

    def get_photos(
        self,
        category: PhotoCategory | None = None,
        entity_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get photos with optional filtering."""
        query = Photo.query

        if category:
            query = query.filter(Photo.category == category)

        if entity_id:
            if category == PhotoCategory.PLANT:
                query = query.filter(Photo.plant_id == entity_id)
            elif category == PhotoCategory.MATERIAL:
                query = query.filter(Photo.material_id == entity_id)
            elif category == PhotoCategory.PROPERTY:
                query = query.filter(Photo.client_id == entity_id)
            elif category == PhotoCategory.PROJECT:
                query = query.filter(Photo.project_id == entity_id)

        photos = query.order_by(Photo.uploaded_at.desc()).offset(offset).limit(limit).all()
        return [photo.to_dict() for photo in photos]

    def delete_photo(self, photo_id: int) -> dict[str, Any]:
        """Delete photo and associated files."""
        try:
            photo = Photo.query.get(photo_id)
            if not photo:
                return {"success": False, "error": "Photo not found"}

            # Delete files
            if photo.file_path and os.path.exists(photo.file_path):
                os.remove(photo.file_path)

            if photo.thumbnail_path and os.path.exists(photo.thumbnail_path):
                os.remove(photo.thumbnail_path)

            # Delete database record
            db.session.delete(photo)
            db.session.commit()

            return {"success": True, "message": "Photo deleted successfully"}

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting photo {photo_id}: {e!s}")
            return {"success": False, "error": f"Delete failed: {e!s}"}

    def set_primary_photo(self, photo_id: int, entity_id: int, category: PhotoCategory) -> dict[str, Any]:
        """Set photo as primary for an entity."""
        try:
            # Clear existing primary photos for this entity
            query = Photo.query.filter(Photo.category == category, Photo.is_primary)

            if category == PhotoCategory.PLANT:
                query = query.filter(Photo.plant_id == entity_id)
            elif category == PhotoCategory.MATERIAL:
                query = query.filter(Photo.material_id == entity_id)
            elif category == PhotoCategory.PROPERTY:
                query = query.filter(Photo.client_id == entity_id)
            elif category == PhotoCategory.PROJECT:
                query = query.filter(Photo.project_id == entity_id)

            # Clear existing primary flags
            query.update({"is_primary": False})

            # Set new primary photo
            photo = Photo.query.get(photo_id)
            if not photo:
                return {"success": False, "error": "Photo not found"}

            photo.is_primary = True
            db.session.commit()

            return {"success": True, "message": "Primary photo updated"}

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error setting primary photo: {e!s}")
            return {"success": False, "error": f"Update failed: {e!s}"}
