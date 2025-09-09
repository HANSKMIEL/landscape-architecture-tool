"""
Test Plant Service

Comprehensive tests for plant service layer business logic.
"""

import pytest

from src.models.landscape import Plant
from src.models.user import db
from src.services.plant_service import PlantService
from tests.fixtures.database import DatabaseTestMixin


@pytest.mark.service
class TestPlantService(DatabaseTestMixin):
    """Test Plant Service operations"""

    def test_get_all_plants_empty(self, app_context):
        """Test getting plants when database is empty"""
        result = PlantService.get_all_plants()

        assert result["plants"] == []
        assert result["total"] == 0
        assert result["pages"] == 0
        assert result["current_page"] == 1

    def test_get_all_plants_with_data(self, app_context, sample_plants):
        """Test getting plants with sample data"""
        result = PlantService.get_all_plants()

        assert len(result["plants"]) == 5
        assert result["total"] == 5
        assert result["pages"] == 1
        assert all("id" in plant for plant in result["plants"])
        assert all("name" in plant for plant in result["plants"])

    def test_get_all_plants_with_search(self, app_context, plant_factory):
        """Test getting plants with search filter"""
        # Create plants with specific names
        plant1 = plant_factory(name="Rose Garden", common_name="Red Rose")  # noqa: F841
        plant2 = plant_factory(name="Lily Pond", common_name="Water Lily")  # noqa: F841
        plant3 = plant_factory(name="Oak Tree", common_name="White Oak")  # noqa: F841

        # Search by name
        result = PlantService.get_all_plants(search="Rose")
        assert len(result["plants"]) == 1
        assert result["plants"][0]["name"] == "Rose Garden"

        # Search by common name
        result = PlantService.get_all_plants(search="Lily")
        assert len(result["plants"]) == 1
        assert result["plants"][0]["name"] == "Lily Pond"

    def test_get_all_plants_with_category_filter(self, app_context, plant_factory):
        """Test getting plants with category filter"""
        plant1 = plant_factory(category="Tree")  # noqa: F841
        plant2 = plant_factory(category="Shrub")  # noqa: F841
        plant3 = plant_factory(category="Tree")  # noqa: F841

        result = PlantService.get_all_plants(category="Tree")
        assert len(result["plants"]) == 2
        assert all(plant["category"] == "Tree" for plant in result["plants"])

    def test_get_all_plants_with_native_filter(self, app_context, plant_factory):
        """Test getting plants with native filter"""
        native_plant = plant_factory(native=True)  # noqa: F841
        non_native_plant = plant_factory(native=False)  # noqa: F841

        result = PlantService.get_all_plants(native_only=True)
        assert len(result["plants"]) == 1
        assert result["plants"][0]["native"] is True

    def test_get_all_plants_pagination(self, app_context, plant_factory):
        """Test plants pagination"""
        # Create 25 plants
        for i in range(25):
            plant_factory(name=f"Plant {i}")

        # Test first page
        result = PlantService.get_all_plants(page=1, per_page=10)
        assert len(result["plants"]) == 10
        assert result["total"] == 25
        assert result["pages"] == 3
        assert result["current_page"] == 1

        # Test second page
        result = PlantService.get_all_plants(page=2, per_page=10)
        assert len(result["plants"]) == 10
        assert result["current_page"] == 2

    def test_get_plant_by_id_success(self, app_context, sample_plant):
        """Test getting plant by ID successfully"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        plant = PlantService.get_plant_by_id(sample_plant.id)
        assert plant is not None
        assert plant.id == sample_plant.id
        assert plant.name == sample_plant.name

    def test_get_plant_by_id_not_found(self, app_context):
        """Test getting plant by non-existent ID"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        plant = PlantService.get_plant_by_id(999)
        assert plant is None

    def test_create_plant_success(self, app_context):
        """Test creating a plant successfully"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
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

        # Verify it's in the database
        self.assert_record_count(Plant, 1)

    def test_create_plant_minimal_data(self, app_context):
        """Test creating plant with minimal required data"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        plant_data = {"name": "Minimal Plant", "category": "Tree"}

        plant = PlantService.create_plant(plant_data)

        assert plant.id is not None
        assert plant.name == "Minimal Plant"
        assert plant.category == "Tree"

    def test_update_plant_success(self, app_context, sample_plant):
        """Test updating a plant successfully"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        update_data = {"name": "Updated Plant Name", "price": 35.99}

        updated_plant = PlantService.update_plant(sample_plant.id, update_data)

        assert updated_plant is not None
        assert updated_plant.name == "Updated Plant Name"
        assert updated_plant.price == 35.99
        assert updated_plant.id == sample_plant.id

    def test_update_plant_not_found(self, app_context):
        """Test updating non-existent plant"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        update_data = {"name": "Updated Name"}
        result = PlantService.update_plant(999, update_data)
        assert result is None

    def test_delete_plant_success(self, app_context, sample_plant):
        """Test deleting a plant successfully"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        plant_id = sample_plant.id

        result = PlantService.delete_plant(plant_id)

        assert result is True
        self.assert_record_count(Plant, 0)

        # Verify plant is gone
        deleted_plant = db.session.get(Plant, plant_id)
        assert deleted_plant is None

    def test_delete_plant_not_found(self, app_context):
        """Test deleting non-existent plant"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        result = PlantService.delete_plant(999)
        assert result is False

    def test_get_plants_by_category(self, app_context, plant_factory):
        """Test getting plants by category"""
        tree1 = plant_factory(category="Tree")  # noqa: F841
        tree2 = plant_factory(category="Tree")  # noqa: F841
        shrub = plant_factory(category="Shrub")  # noqa: F841

        trees = PlantService.get_plants_by_category("Tree")
        assert len(trees) == 2
        assert all(plant.category == "Tree" for plant in trees)

    def test_search_plants(self, app_context, plant_factory):
        """Test searching plants"""
        plant1 = plant_factory(name="Rose Garden", common_name="Red Rose")  # noqa: F841
        plant2 = plant_factory(name="Lily Pond", common_name="Water Lily")  # noqa: F841
        plant3 = plant_factory(name="Oak Tree", common_name="White Oak")  # noqa: F841

        # Search for "Rose"
        results = PlantService.search_plants("Rose")
        assert len(results) == 1
        assert results[0].name == "Rose Garden"

        # Search for "Oak"
        results = PlantService.search_plants("Oak")
        assert len(results) == 1
        assert results[0].name == "Oak Tree"

    def test_get_plant_categories(self, app_context, plant_factory):
        """Test getting unique plant categories"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        plant_factory(category="Tree")
        plant_factory(category="Shrub")
        plant_factory(category="Tree")  # Duplicate
        plant_factory(category="Perennial")

        categories = PlantService.get_plant_categories()
        assert len(categories) == 3
        assert "Tree" in categories
        assert "Shrub" in categories
        assert "Perennial" in categories

    def test_validate_plant_data_success(self, app_context):
        """Test validating correct plant data"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        valid_data = {
            "name": "Valid Plant",
            "category": "Tree",
            "height_min": 100.0,
            "height_max": 200.0,
            "price": 25.99,
        }

        errors = PlantService.validate_plant_data(valid_data)
        assert errors == []

    def test_validate_plant_data_missing_required(self, app_context):
        """Test validating plant data with missing required fields"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        invalid_data = {}

        errors = PlantService.validate_plant_data(invalid_data)
        assert "name is required" in errors
        assert "category is required" in errors

    def test_validate_plant_data_negative_numbers(self, app_context):
        """Test validating plant data with negative numbers"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        invalid_data = {
            "name": "Test Plant",
            "category": "Tree",
            "height_min": -10.0,
            "price": -5.99,
        }

        errors = PlantService.validate_plant_data(invalid_data)
        assert "height_min must be non-negative" in errors
        assert "price must be non-negative" in errors

    def test_validate_plant_data_height_range_invalid(self, app_context):
        """Test validating plant data with invalid height range"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        invalid_data = {
            "name": "Test Plant",
            "category": "Tree",
            "height_min": 200.0,
            "height_max": 100.0,  # max < min
        }

        errors = PlantService.validate_plant_data(invalid_data)
        assert "height_min cannot be greater than height_max" in errors

    def test_validate_plant_data_invalid_ph_range(self, app_context):
        """Test validating plant data with invalid pH range"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        invalid_data = {
            "name": "Test Plant",
            "category": "Tree",
            "soil_ph_min": 8.0,
            "soil_ph_max": 6.0,  # max < min
        }

        errors = PlantService.validate_plant_data(invalid_data)
        assert "soil_ph_min cannot be greater than soil_ph_max" in errors

    def test_validate_plant_data_ph_out_of_range(self, app_context):
        """Test validating plant data with pH values out of range"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        invalid_data = {
            "name": "Test Plant",
            "category": "Tree",
            "soil_ph_min": -1.0,
            "soil_ph_max": 15.0,
        }

        errors = PlantService.validate_plant_data(invalid_data)
        assert "pH values must be between 0 and 14" in errors

    def test_validate_plant_data_invalid_number_format(self, app_context):
        """Test validating plant data with invalid number formats"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
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

    def test_full_plant_lifecycle(self, app_context, supplier_factory):
        """Test complete plant lifecycle from creation to deletion"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        supplier = supplier_factory()

        # Create plant
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

        # Read plant
        retrieved_plant = PlantService.get_plant_by_id(plant.id)
        assert retrieved_plant.name == "Lifecycle Test Plant"

        # Update plant
        update_data = {"price": 55.99, "height_max": 350.0}
        updated_plant = PlantService.update_plant(plant.id, update_data)
        assert updated_plant.price == 55.99
        assert updated_plant.height_max == 350.0

        # Search for plant
        search_results = PlantService.search_plants("Lifecycle")
        assert len(search_results) == 1
        assert search_results[0].id == plant.id

        # Delete plant
        delete_result = PlantService.delete_plant(plant.id)
        assert delete_result is True

        # Verify deletion
        deleted_plant = PlantService.get_plant_by_id(plant.id)
        assert deleted_plant is None

    def test_complex_filtering_scenario(self, app_context, plant_factory):
        """Test complex filtering scenarios"""
        # Create diverse plants
        plant_factory(name="Oak Tree", category="Tree", sun_exposure="full_sun", native=True)
        tree2 = plant_factory(  # noqa: F841
            name="Maple Tree",
            category="Tree",
            sun_exposure="partial_shade",
            native=False,
        )
        plant_factory(name="Rose Bush", category="Shrub", sun_exposure="full_sun", native=True)

        # Filter by category and native status
        result = PlantService.get_all_plants(category="Tree", native_only=True)
        assert len(result["plants"]) == 1
        assert result["plants"][0]["name"] == "Oak Tree"

        # Filter by sun exposure
        result = PlantService.get_all_plants(sun_exposure="full_sun")
        assert len(result["plants"]) == 2

        # Search with category filter
        result = PlantService.get_all_plants(search="Tree", category="Tree")
        assert len(result["plants"]) == 2
