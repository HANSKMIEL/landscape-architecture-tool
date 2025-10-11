"""
Test Plant Service

Comprehensive tests for plant service layer business logic.
"""

import pytest

from src.models.landscape import Plant
from src.models.photo import Photo
from src.models.user import db
from src.services.plant_service import PlantService
from tests.fixtures.auth_fixtures import authenticated_test_user
from tests.fixtures.database import DatabaseTestMixin

pytestmark = pytest.mark.usefixtures("app_context", "authenticated_test_user")


@pytest.mark.service
class TestPlantService(DatabaseTestMixin):
    """Test Plant Service operations"""

    def test_get_all_plants_empty(self):
        """Should return an empty structure when no plants exist"""
        result = PlantService.get_all_plants()

        assert result["plants"] == []
        assert result["total"] == 0
        assert result["pages"] == 0
        assert result["current_page"] == 1

    def test_get_all_plants_with_data(self, plant_factory):
        """Plants created via factory should be returned with pagination metadata"""
        plant_factory.create_batch(4, category="Shrub")

        result = PlantService.get_all_plants()

        assert len(result["plants"]) == 4
        assert result["total"] == 4
        assert result["pages"] == 1
        assert all("id" in plant for plant in result["plants"])
        assert all("name" in plant for plant in result["plants"])

    def test_get_all_plants_with_search(self, plant_factory):
        """Search term should match against name and common name"""
        plant_factory(name="Rose Garden", common_name="Red Rose")
        plant_factory(name="Lily Pond", common_name="Water Lily")
        plant_factory(name="Oak Tree", common_name="White Oak")

        result = PlantService.get_all_plants(search="Rose")
        assert [plant["name"] for plant in result["plants"]] == ["Rose Garden"]

        result = PlantService.get_all_plants(search="Lily")
        assert [plant["name"] for plant in result["plants"]] == ["Lily Pond"]

    def test_get_all_plants_with_category_filter(self, plant_factory):
        """Category filter should limit results"""
        plant_factory(category="Tree")
        plant_factory(category="Shrub")
        plant_factory(category="Tree")

        result = PlantService.get_all_plants(category="Tree")

        assert len(result["plants"]) == 2
        assert all(plant["category"] == "Tree" for plant in result["plants"])

    def test_get_all_plants_with_native_filter(self, plant_factory):
        """Native filter should only return native species"""
        plant_factory(native=True)
        plant_factory(native=False)

        result = PlantService.get_all_plants(native_only=True)

        assert [plant["native"] for plant in result["plants"]] == [True]

    def test_get_all_plants_pagination(self, plant_factory):
        """Pagination should respect page and per_page arguments"""
        plant_factory.create_batch(25)

        first_page = PlantService.get_all_plants(page=1, per_page=10)
        assert len(first_page["plants"]) == 10
        assert first_page["total"] == 25
        assert first_page["pages"] == 3
        assert first_page["current_page"] == 1

        second_page = PlantService.get_all_plants(page=2, per_page=10)
        assert len(second_page["plants"]) == 10
        assert second_page["current_page"] == 2

    def test_get_plant_by_id_success(self, plant_factory):
        """Should fetch an existing plant by id"""
        plant_instance = plant_factory()

        plant = PlantService.get_plant_by_id(plant_instance.id)

        assert plant is not None
        assert plant.id == plant_instance.id
        assert plant.name == plant_instance.name

    def test_get_plant_by_id_not_found(self):
        """Should return None when plant does not exist"""
        assert PlantService.get_plant_by_id(999) is None

    def test_create_plant_success(self):
        """Creating a plant with full data should persist it"""
        plant_data = {
            "name": "Test Plant",
            "common_name": "Common Test Plant",
            "category": "Shrub",
            "height_min": 50.0,
            "height_max": 150.0,
            "price": 25.99,
        }

        plant = PlantService.create_plant(plant_data)

        assert plant.id is not None
        assert plant.name == "Test Plant"
        assert plant.common_name == "Common Test Plant"
        assert plant.category == "Shrub"
        assert plant.price == 25.99
        self.assert_record_count(Plant, 1)

    def test_create_plant_minimal_data(self):
        """Minimal required data should succeed"""
        plant = PlantService.create_plant({"name": "Minimal Plant", "category": "Tree"})

        assert plant.id is not None
        assert plant.name == "Minimal Plant"
        assert plant.category == "Tree"

    def test_update_plant_success(self, plant_factory):
        """Updating an existing plant should persist new values"""
        plant_instance = plant_factory()
        update_data = {"name": "Updated Plant Name", "price": 35.99}

        updated_plant = PlantService.update_plant(plant_instance.id, update_data)

        assert updated_plant is not None
        assert updated_plant.name == "Updated Plant Name"
        assert updated_plant.price == 35.99
        assert updated_plant.id == plant_instance.id

    def test_update_plant_not_found(self):
        """Updating a missing plant should return None"""
        assert PlantService.update_plant(999, {"name": "Updated Name"}) is None

    def test_delete_plant_success(self, plant_factory):
        """Deleting an existing plant should remove it"""
        plant_instance = plant_factory()

        assert db.session.query(Photo).count() == 0
        assert PlantService.delete_plant(plant_instance.id)
        self.assert_record_count(Plant, 0)
        assert db.session.get(Plant, plant_instance.id) is None

    def test_delete_plant_not_found(self):
        """Deleting a missing plant should return False"""
        assert PlantService.delete_plant(999) is False

    def test_get_plants_by_category(self, plant_factory):
        """Category helper should return matching ORM models"""
        plant_factory(category="Tree")
        plant_factory(category="Tree")
        plant_factory(category="Shrub")

        trees = PlantService.get_plants_by_category("Tree")

        assert len(trees) == 2
        assert all(plant.category == "Tree" for plant in trees)

    def test_search_plants(self, plant_factory):
        """Legacy search method should return ORM entities"""
        plant_factory(name="Rose Garden", common_name="Red Rose")
        plant_factory(name="Lily Pond", common_name="Water Lily")
        plant_factory(name="Oak Tree", common_name="White Oak")

        results = PlantService.search_plants("Rose")
        assert [plant.name for plant in results] == ["Rose Garden"]

        results = PlantService.search_plants("Oak")
        assert [plant.name for plant in results] == ["Oak Tree"]

    def test_get_plant_categories(self, plant_factory):
        """Unique categories should be returned without duplicates"""
        plant_factory(category="Tree")
        plant_factory(category="Shrub")
        plant_factory(category="Tree")
        plant_factory(category="Perennial")

        categories = PlantService.get_plant_categories()

        assert set(categories) == {"Tree", "Shrub", "Perennial"}

    def test_validate_plant_data_success(self):
        """Valid data should produce no validation errors"""
        valid_data = {
            "name": "Valid Plant",
            "category": "Tree",
            "height_min": 100.0,
            "height_max": 200.0,
            "price": 25.99,
        }

        assert PlantService.validate_plant_data(valid_data) == []

    def test_validate_plant_data_missing_required(self):
        """Missing required fields should be reported"""
        errors = PlantService.validate_plant_data({})

        assert "name is required" in errors
        assert "category is required" in errors

    def test_validate_plant_data_negative_numbers(self):
        """Negative numeric values should be rejected"""
        invalid_data = {
            "name": "Test Plant",
            "category": "Tree",
            "height_min": -10.0,
            "price": -5.99,
        }

        errors = PlantService.validate_plant_data(invalid_data)

        assert "height_min must be non-negative" in errors
        assert "price must be non-negative" in errors

    def test_validate_plant_data_height_range_invalid(self):
        """height_min cannot exceed height_max"""
        invalid_data = {
            "name": "Test Plant",
            "category": "Tree",
            "height_min": 200.0,
            "height_max": 100.0,
        }

        errors = PlantService.validate_plant_data(invalid_data)

        assert "height_min cannot be greater than height_max" in errors

    def test_validate_plant_data_invalid_ph_range(self):
        """soil_ph_min cannot exceed soil_ph_max"""
        invalid_data = {
            "name": "Test Plant",
            "category": "Tree",
            "soil_ph_min": 8.0,
            "soil_ph_max": 6.0,
        }

        errors = PlantService.validate_plant_data(invalid_data)

        assert "soil_ph_min cannot be greater than soil_ph_max" in errors

    def test_validate_plant_data_ph_out_of_range(self):
        """pH values must be between 0 and 14"""
        invalid_data = {
            "name": "Test Plant",
            "category": "Tree",
            "soil_ph_min": -1.0,
            "soil_ph_max": 15.0,
        }

        errors = PlantService.validate_plant_data(invalid_data)

        assert "pH values must be between 0 and 14" in errors

    def test_validate_plant_data_invalid_number_format(self):
        """Non-numeric inputs should raise validation errors"""
        invalid_data = {
            "name": "Test Plant",
            "category": "Tree",
            "height_min": "not_a_number",
            "price": "invalid_price",
        }

        errors = PlantService.validate_plant_data(invalid_data)

        assert "height_min must be a valid number" in errors
        assert "price must be a valid number" in errors


@pytest.mark.integration
class TestPlantServiceIntegration(DatabaseTestMixin):
    """Integration tests for Plant Service"""

    def test_full_plant_lifecycle(self, supplier_factory):
        """End-to-end lifecycle should behave correctly"""
        supplier = supplier_factory()

        plant_data = {
            "name": "Lifecycle Test Plant",
            "common_name": "Test Plant",
            "category": "Tree",
            "height_min": 100.0,
            "height_max": 300.0,
            "supplier_id": supplier.id,
            "price": 45.99,
            "native": True,
        }

        plant = PlantService.create_plant(plant_data)
        assert plant.id is not None

        retrieved_plant = PlantService.get_plant_by_id(plant.id)
        assert retrieved_plant is not None
        assert retrieved_plant.name == "Lifecycle Test Plant"

        update_data = {"price": 55.99, "height_max": 350.0}
        updated_plant = PlantService.update_plant(plant.id, update_data)
        assert updated_plant is not None
        assert updated_plant.price == 55.99
        assert updated_plant.height_max == 350.0

        search_results = PlantService.search_plants("Lifecycle")
        assert len(search_results) == 1
        assert search_results[0].id == plant.id

        assert db.session.query(Photo).count() == 0
        assert PlantService.delete_plant(plant.id)
        assert PlantService.get_plant_by_id(plant.id) is None

    def test_complex_filtering_scenario(self, plant_factory):
        """Combined filters should narrow results appropriately"""
        plant_factory(name="Oak Tree", category="Tree", sun_exposure="full_sun", native=True)
        plant_factory(
            name="Maple Tree",
            category="Tree",
            sun_exposure="partial_shade",
            native=False,
        )
        plant_factory(name="Rose Bush", category="Shrub", sun_exposure="full_sun", native=True)

        result = PlantService.get_all_plants(category="Tree", native_only=True)
        assert [plant["name"] for plant in result["plants"]] == ["Oak Tree"]

        result = PlantService.get_all_plants(sun_exposure="full_sun")
        assert len(result["plants"]) == 2

        result = PlantService.get_all_plants(search="Tree", category="Tree")
        assert len(result["plants"]) == 2
