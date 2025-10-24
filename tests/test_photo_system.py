"""Tests for photo upload and management system."""

from io import BytesIO

import pytest
from PIL import Image

from src.models.photo import Photo, PhotoCategory
from tests.fixtures.auth_fixtures import authenticated_test_user


@pytest.fixture
def authenticated_client(client, authenticated_test_user, tmp_path):
    """Authenticated client with isolated upload folder for photo tests."""

    client.application.config["UPLOAD_FOLDER"] = str(tmp_path)
    return client


def create_test_image():
    """Create a test image file."""
    image = Image.new("RGB", (100, 100), color="red")
    img_bytes = BytesIO()
    image.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes


class TestPhotoUpload:
    """Test photo upload functionality."""

    def test_upload_without_auth(self, client):
        """Test upload requires authentication."""
        img_data = create_test_image()

        response = client.post("/api/photos/upload", data={"file": (img_data, "test.jpg"), "category": "example"})

        assert response.status_code == 401

    def test_upload_success(self, authenticated_client, app_context):
        """Test successful photo upload."""
        img_data = create_test_image()

        response = authenticated_client.post(
            "/api/photos/upload",
            data={
                "file": (img_data, "test.jpg"),
                "category": "example",
                "title": "Test Photo",
                "description": "A test photo",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert "photo" in data

        # Check database
        with app_context.app_context():
            photo = Photo.query.first()
            assert photo is not None
            assert photo.title == "Test Photo"
            assert photo.description == "A test photo"
            assert photo.category == PhotoCategory.EXAMPLE

    def test_upload_invalid_category(self, authenticated_client):
        """Test upload with invalid category."""
        img_data = create_test_image()

        response = authenticated_client.post(
            "/api/photos/upload", data={"file": (img_data, "test.jpg"), "category": "invalid_category"}
        )

        assert response.status_code == 400

    def test_upload_no_file(self, authenticated_client):
        """Test upload without file."""
        response = authenticated_client.post("/api/photos/upload", data={"category": "example"})

        assert response.status_code == 400

    def test_upload_with_entity_id(self, authenticated_client, app_context):
        """Test upload with entity association."""
        img_data = create_test_image()

        response = authenticated_client.post(
            "/api/photos/upload",
            data={"file": (img_data, "plant.jpg"), "category": "plant", "entity_id": "1", "title": "Plant Photo"},
        )

        assert response.status_code == 201

        # Check database
        with app_context.app_context():
            photo = Photo.query.first()
            assert photo is not None
            assert photo.plant_id == 1
            assert photo.category == PhotoCategory.PLANT


class TestPhotoAPI:
    """Test photo API endpoints."""

    def test_get_photos_empty(self, authenticated_client):
        """Test getting photos when none exist."""
        response = authenticated_client.get("/api/photos/")

        assert response.status_code == 200
        data = response.get_json()
        assert data["photos"] == []
        assert data["count"] == 0

    def test_get_photos_with_data(self, authenticated_client, app_context):
        """Test getting photos with data."""
        # Upload a photo first
        img_data = create_test_image()
        upload_response = authenticated_client.post(
            "/api/photos/upload", data={"file": (img_data, "test.jpg"), "category": "example", "title": "Test Photo"}
        )
        assert upload_response.status_code == 201

        # Get photos
        response = authenticated_client.get("/api/photos/")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["photos"]) == 1
        assert data["count"] == 1
        assert data["photos"][0]["title"] == "Test Photo"

    def test_get_photos_by_category(self, authenticated_client):
        """Test filtering photos by category."""
        # Upload photos with different categories
        img_data1 = create_test_image()
        authenticated_client.post(
            "/api/photos/upload", data={"file": (img_data1, "plant.jpg"), "category": "plant", "title": "Plant Photo"}
        )

        img_data2 = create_test_image()
        authenticated_client.post(
            "/api/photos/upload",
            data={"file": (img_data2, "material.jpg"), "category": "material", "title": "Material Photo"},
        )

        # Get plant photos only
        response = authenticated_client.get("/api/photos/?category=plant")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["photos"]) == 1
        assert data["photos"][0]["category"] == "plant"

    def test_get_photo_by_id(self, authenticated_client, app_context):
        """Test getting specific photo by ID."""
        # Upload a photo first
        img_data = create_test_image()
        upload_response = authenticated_client.post(
            "/api/photos/upload", data={"file": (img_data, "test.jpg"), "category": "example", "title": "Test Photo"}
        )

        photo_id = upload_response.get_json()["photo"]["id"]

        # Get photo by ID
        response = authenticated_client.get(f"/api/photos/{photo_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["photo"]["id"] == photo_id
        assert data["photo"]["title"] == "Test Photo"

    def test_get_nonexistent_photo(self, authenticated_client):
        """Test getting photo that doesn't exist."""
        response = authenticated_client.get("/api/photos/999")

        assert response.status_code == 404

    def test_delete_photo(self, authenticated_client, app_context):
        """Test deleting photo."""
        # Authentication handled by authenticated_test_user fixture
        # Upload a photo first
        img_data = create_test_image()
        upload_response = authenticated_client.post(
            "/api/photos/upload", data={"file": (img_data, "test.jpg"), "category": "example"}
        )

        photo_id = upload_response.get_json()["photo"]["id"]

        # Delete photo
        response = authenticated_client.delete(f"/api/photos/{photo_id}")

        assert response.status_code == 200

        # Verify it's gone
        get_response = authenticated_client.get(f"/api/photos/{photo_id}")
        assert get_response.status_code == 404

    def test_get_photo_categories(self, authenticated_client):
        """Test getting available photo categories."""
        response = authenticated_client.get("/api/photos/categories")

        assert response.status_code == 200
        data = response.get_json()
        assert "categories" in data
        assert len(data["categories"]) > 0

        # Check that all expected categories are present
        category_values = [cat["value"] for cat in data["categories"]]
        expected_categories = ["plant", "material", "property", "project", "example", "inspiration", "reference"]
        for cat in expected_categories:
            assert cat in category_values


class TestPhotoService:
    """Test photo service functionality."""

    def test_photo_service_initialization(self, app):
        """Test photo service initializes correctly."""
        from src.services.photo_service import PhotoService

        with app.app_context():
            service = PhotoService()
            assert service.upload_folder is not None
            assert {"png", "jpg", "jpeg", "gif", "webp"} == service.ALLOWED_EXTENSIONS

    def test_allowed_file_validation(self, app):
        """Test file extension validation."""
        from src.services.photo_service import PhotoService

        with app.app_context():
            service = PhotoService()

            assert service.allowed_file("test.jpg") is True
            assert service.allowed_file("test.png") is True
            assert service.allowed_file("test.gif") is True
            assert service.allowed_file("test.txt") is False
            assert service.allowed_file("test") is False

    def test_generate_filename(self, app):
        """Test filename generation."""
        from src.services.photo_service import PhotoService

        with app.app_context():
            service = PhotoService()

            filename, extension = service.generate_filename("test.jpg")
            assert filename.endswith(".jpg")
            assert extension == "jpg"
            assert len(filename) > 10  # Should include timestamp and UUID

    def test_get_category_folder(self, app):
        """Test category folder path generation."""
        from src.services.photo_service import PhotoService

        with app.app_context():
            service = PhotoService()

            plant_folder = service.get_category_folder(PhotoCategory.PLANT)
            assert "plants" in plant_folder

            material_folder = service.get_category_folder(PhotoCategory.MATERIAL)
            assert "materials" in material_folder
