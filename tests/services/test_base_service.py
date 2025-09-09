"""
Tests for base service functionality
"""

from unittest.mock import Mock, patch

import pytest
from tests.fixtures.auth_fixtures import authenticated_test_user, setup_test_authentication

from src.main import create_app
from src.models.landscape import Plant
from src.models.user import db
from src.services import BaseService
from tests.database.factories import create_test_plant


@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def db_setup(app):
    """Setup test database"""
    with app.app_context():
        db.create_all()
        yield
        db.session.close()


class TestBaseService:
    """Test the BaseService class"""

    def test_base_service_init(self):
        """Test BaseService initialization"""
        service = BaseService(Plant)
        assert service.model_class == Plant

    def test_get_all_basic(self, app, db_setup):
        """Test get_all method without parameters"""
        with app.app_context():
            # Create test plants
            plants = [
                create_test_plant(name="Plant A"),
                create_test_plant(name="Plant B"),
                create_test_plant(name="Plant C"),
            ]

            for plant in plants:
                db.session.add(plant)
            db.session.commit()

            service = BaseService(Plant)
            result = service.get_all()

            assert "items" in result
            assert "total" in result
            assert "pages" in result
            assert "current_page" in result
            assert "has_next" in result
            assert "has_prev" in result

            assert result["current_page"] == 1
            assert result["total"] >= 3
            assert len(result["items"]) >= 3

    def test_get_all_with_search(self, app, db_setup):
        """Test get_all method with search parameter"""
        with app.app_context():
            # Create test plants with specific names
            plants = [
                create_test_plant(name="Rose Bush"),
                create_test_plant(name="Oak Tree"),
                create_test_plant(name="Rose Flower"),
            ]

            for plant in plants:
                db.session.add(plant)
            db.session.commit()

            service = BaseService(Plant)
            result = service.get_all(search="Rose")

            # Should find plants with "Rose" in the name
            assert result["total"] >= 2
            rose_names = [item["name"] for item in result["items"]]
            assert any("Rose" in name for name in rose_names)

    def test_get_all_with_pagination(self, app, db_setup):
        """Test get_all method with pagination"""
        with app.app_context():
            # Create multiple test plants
            plants = [create_test_plant(name=f"Plant {i}") for i in range(10)]

            for plant in plants:
                db.session.add(plant)
            db.session.commit()

            service = BaseService(Plant)
            result = service.get_all(page=1, per_page=3)

            assert result["current_page"] == 1
            assert len(result["items"]) == 3
            assert result["total"] >= 10

            # Test second page
            result_page2 = service.get_all(page=2, per_page=3)
            assert result_page2["current_page"] == 2
            assert len(result_page2["items"]) == 3

    def test_get_all_search_no_results(self, app, db_setup):
        """Test get_all with search that returns no results"""
        with app.app_context():
            # Create test plants
            plants = [
                create_test_plant(name="Rose Bush"),
                create_test_plant(name="Oak Tree"),
            ]

            for plant in plants:
                db.session.add(plant)
            db.session.commit()

            service = BaseService(Plant)
            result = service.get_all(search="NonexistentPlant")

            assert result["total"] == 0
            assert len(result["items"]) == 0

    def test_get_by_id_success(self, app, db_setup):
        """Test get_by_id method with valid ID"""
        with app.app_context():
            plant = create_test_plant(name="Test Plant")
            db.session.add(plant)
            db.session.commit()

            service = BaseService(Plant)
            result = service.get_by_id(plant.id)

            assert result is not None
            assert result["id"] == plant.id
            assert result["name"] == "Test Plant"

    def test_get_by_id_not_found(self, app, db_setup):
        """Test get_by_id method with invalid ID"""
        with app.app_context():
            service = BaseService(Plant)
            result = service.get_by_id(99999)

            assert result is None

    def test_create_success(self, app, db_setup):
        """Test create method with valid data"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            service = BaseService(Plant)

            plant_data = {
                "name": "New Plant",
                "common_name": "Common Plant",
                "category": "Shrub",
            }

            result = service.create(plant_data)

            assert result is not None
            assert result["name"] == "New Plant"
            assert result["common_name"] == "Common Plant"
            assert "id" in result

            # Verify it was saved to database
            saved_plant = db.session.get(Plant, result["id"])
            assert saved_plant is not None
            assert saved_plant.name == "New Plant"

    def test_update_success(self, app, db_setup):
        """Test update method with valid data"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            # Create initial plant
            plant = create_test_plant(name="Original Plant")
            db.session.add(plant)
            db.session.commit()

            service = BaseService(Plant)

            updated_data = {"name": "Updated Plant"}
            result = service.update(plant.id, updated_data)

            assert result is not None
            assert result["name"] == "Updated Plant"

            # Verify database was updated
            updated_plant = db.session.get(Plant, plant.id)
            assert updated_plant.name == "Updated Plant"

    def test_update_not_found(self, app, db_setup):
        """Test update method with invalid ID"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            service = BaseService(Plant)
            result = service.update(99999, {"name": "Updated"})

            assert result is None

    def test_delete_success(self, app, db_setup):
        """Test delete method with valid ID"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            plant = create_test_plant(name="Plant to Delete")
            db.session.add(plant)
            db.session.commit()
            plant_id = plant.id

            service = BaseService(Plant)
            result = service.delete(plant_id)

            assert result is True

            # Verify plant was deleted
            deleted_plant = db.session.get(Plant, plant_id)
            assert deleted_plant is None

    def test_delete_not_found(self, app, db_setup):
        """Test delete method with invalid ID"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            service = BaseService(Plant)
            result = service.delete(99999)

            assert result is False

    def test_get_all_error_handling(self, app, db_setup):
        """Test get_all error handling"""
        with app.app_context():
            service = BaseService(Plant)

            # Mock the query to raise an exception during pagination
            with patch.object(Plant, "query") as mock_query:
                # Set up the mock chain properly
                mock_order_by = Mock()
                mock_order_by.paginate.side_effect = Exception("Database error")
                mock_query.order_by.return_value = mock_order_by

                with pytest.raises(Exception):  # noqa: B017
                    service.get_all()

    def test_get_by_id_error_handling(self, app, db_setup):
        """Test get_by_id error handling"""
        with app.app_context():
            service = BaseService(Plant)

            with patch("src.models.user.db.session.get") as mock_get:
                mock_get.side_effect = Exception("Database error")

                with pytest.raises(Exception):  # noqa: B017
                    service.get_by_id(1)

    def test_create_error_handling(self, app, db_setup):
        """Test create error handling"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            service = BaseService(Plant)

            with patch("src.models.user.db.session.add") as mock_add:
                mock_add.side_effect = Exception("Database error")

                with pytest.raises(Exception):  # noqa: B017
                    service.create({"name": "Test"})

    def test_update_error_handling(self, app, db_setup):
        """Test update error handling"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            # Create a plant first
            plant = create_test_plant(name="Test Plant")
            db.session.add(plant)
            db.session.commit()

            service = BaseService(Plant)

            with patch("src.models.user.db.session.commit") as mock_commit:
                mock_commit.side_effect = Exception("Database error")

                with pytest.raises(Exception):  # noqa: B017
                    service.update(plant.id, {"name": "Updated"})

    def test_delete_error_handling(self, app, db_setup):
        """Test delete error handling"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            # Create a plant first
            plant = create_test_plant(name="Test Plant")
            db.session.add(plant)
            db.session.commit()

            service = BaseService(Plant)

            with patch("src.models.user.db.session.delete") as mock_delete:
                mock_delete.side_effect = Exception("Database error")

                with pytest.raises(Exception):  # noqa: B017
                    service.delete(plant.id)


class TestBaseServiceWithDifferentModels:
    """Test BaseService with different model types"""

    def test_base_service_without_name_field(self, app, db_setup):
        """Test BaseService with model that doesn't have 'name' field"""
        from src.models.landscape import Client

        with app.app_context():
            # Create a client (which might not have searchable name field)
            service = BaseService(Client)

            # This should not crash even if the model doesn't have a name field
            result = service.get_all(search="test")

            # Should return results (possibly empty)
            assert "items" in result
            assert "total" in result
