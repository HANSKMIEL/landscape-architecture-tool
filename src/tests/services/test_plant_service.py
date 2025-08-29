from unittest.mock import Mock, patch

import pytest

from src.services import PlantService


class TestPlantService:

    @pytest.fixture
    def plant_service(self):
        return PlantService()

    @pytest.fixture
    def sample_plant_data(self):
        return {
            "name": "Test Rose",
            "common_name": "Common Test Rose",
            "category": "shrub",
            "height_min": 50.0,
            "height_max": 150.0,
            "width_min": 40.0,
            "width_max": 100.0,
            "sun_requirements": "full_sun",
            "soil_type": "well_drained",
            "water_needs": "moderate",
            "hardiness_zone": "5-9",
            "price": 25.99,
        }

    @pytest.fixture
    def mock_plant(self):
        plant = Mock()
        plant.id = 1
        plant.name = "Test Rose"
        plant.common_name = "Common Test Rose"
        plant.category = "shrub"
        plant.price = 25.99
        plant.to_dict.return_value = {
            "id": 1,
            "name": "Test Rose",
            "common_name": "Common Test Rose",
            "category": "shrub",
            "price": 25.99,
        }
        return plant

    def test_create_plant_success(self, app_context, plant_service, sample_plant_data):
        """Test successful plant creation"""
        with patch("src.models.user.db.session") as mock_session:

            # Mock the plant instance that would be created
            mock_plant = Mock()
            mock_plant.id = 1
            mock_plant.to_dict.return_value = sample_plant_data

            # Mock the model class on the service instance
            with patch.object(plant_service, "model_class") as mock_model_class:
                mock_model_class.return_value = mock_plant
                mock_model_class.__name__ = "Plant"

                result = plant_service.create(sample_plant_data)

                mock_model_class.assert_called_once_with(**sample_plant_data)
                mock_session.add.assert_called_once_with(mock_plant)
                mock_session.commit.assert_called_once()
                assert result == sample_plant_data

    def test_create_plant_validation_error(self, app_context, plant_service):
        """Test plant creation with invalid data"""
        invalid_data = {"name": ""}  # Empty name should be invalid

        with patch("src.models.user.db.session") as mock_session:

            # Mock the model class to raise validation error
            with patch.object(plant_service, "model_class") as mock_model_class:
                mock_model_class.side_effect = ValueError("Name cannot be empty")
                mock_model_class.__name__ = "Plant"

                with pytest.raises(ValueError):
                    plant_service.create(invalid_data)

                mock_session.rollback.assert_called_once()

    def test_get_plant_by_id_success(self, app_context, plant_service, mock_plant):
        """Test retrieving plant by ID"""
        with patch("src.models.landscape.Plant.query") as mock_query:
            mock_query.get.return_value = mock_plant

            result = plant_service.get_by_id(1)

            assert result == mock_plant.to_dict.return_value
            mock_query.get.assert_called_once_with(1)

    def test_get_plant_not_found(self, app_context, plant_service):
        """Test retrieving non-existent plant"""
        with patch("src.models.landscape.Plant.query") as mock_query:
            mock_query.get.return_value = None

            result = plant_service.get_by_id(999)

            assert result is None
            mock_query.get.assert_called_once_with(999)

    def test_update_plant_success(self, app_context, plant_service, mock_plant):
        """Test successful plant update"""
        update_data = {"name": "Updated Rose Name", "price": 30.99}

        with (
            patch("src.models.landscape.Plant.query") as mock_query,
            patch("src.models.user.db.session") as mock_session,
        ):

            mock_query.get.return_value = mock_plant
            mock_plant.to_dict.return_value = {
                **mock_plant.to_dict.return_value,
                **update_data,
            }

            result = plant_service.update(1, update_data)

            # Verify attributes were set
            assert mock_plant.name == "Updated Rose Name"
            assert mock_plant.price == 30.99
            mock_session.commit.assert_called_once()
            assert result is not None

    def test_update_plant_not_found(self, app_context, plant_service):
        """Test updating non-existent plant"""
        with patch("src.models.landscape.Plant.query") as mock_query:
            mock_query.get.return_value = None

            result = plant_service.update(999, {"name": "Test"})

            assert result is None

    def test_delete_plant_success(self, app_context, plant_service, mock_plant):
        """Test successful plant deletion"""
        with (
            patch("src.models.landscape.Plant.query") as mock_query,
            patch("src.models.user.db.session") as mock_session,
        ):

            mock_query.get.return_value = mock_plant

            result = plant_service.delete(1)

            assert result is True
            mock_session.delete.assert_called_once_with(mock_plant)
            mock_session.commit.assert_called_once()

    def test_delete_plant_not_found(self, app_context, plant_service):
        """Test deleting non-existent plant"""
        with patch("src.models.landscape.Plant.query") as mock_query:
            mock_query.get.return_value = None

            result = plant_service.delete(999)

            assert result is False

    def test_get_all_plants_empty(self, app_context, plant_service):
        """Test getting all plants when database is empty"""
        with patch("src.models.landscape.Plant.query") as mock_query:
            mock_pagination = Mock()
            mock_pagination.items = []
            mock_pagination.total = 0
            mock_pagination.pages = 0
            mock_pagination.has_next = False
            mock_pagination.has_prev = False

            mock_query.order_by.return_value.paginate.return_value = mock_pagination

            result = plant_service.get_all()

            assert result["plants"] == []
            assert result["total"] == 0
            assert result["current_page"] == 1

    def test_get_all_plants_with_data(self, app_context, plant_service):
        """Test getting all plants with data"""
        mock_plants = [Mock() for _ in range(3)]
        for i, plant in enumerate(mock_plants):
            plant.to_dict.return_value = {"id": i + 1, "name": f"Plant {i+1}"}

        with patch("src.models.landscape.Plant.query") as mock_query:
            mock_pagination = Mock()
            mock_pagination.items = mock_plants
            mock_pagination.total = 3
            mock_pagination.pages = 1
            mock_pagination.has_next = False
            mock_pagination.has_prev = False

            mock_query.order_by.return_value.paginate.return_value = mock_pagination

            result = plant_service.get_all()

            assert len(result["plants"]) == 3
            assert result["total"] == 3
            assert result["current_page"] == 1

    def test_get_all_plants_with_search(self, app_context, plant_service):
        """Test getting plants with search functionality"""
        mock_plants = [Mock()]
        mock_plants[0].to_dict.return_value = {"id": 1, "name": "Rose Plant"}

        with patch("src.models.landscape.Plant.query") as mock_query:
            mock_pagination = Mock()
            mock_pagination.items = mock_plants
            mock_pagination.total = 1
            mock_pagination.pages = 1
            mock_pagination.has_next = False
            mock_pagination.has_prev = False

            mock_filtered_query = Mock()
            mock_filtered_query.order_by.return_value.paginate.return_value = mock_pagination
            mock_query.filter.return_value = mock_filtered_query

            result = plant_service.get_all(search="Rose")

            assert len(result["plants"]) == 1
            assert result["plants"][0]["name"] == "Rose Plant"
            mock_query.filter.assert_called_once()

    def test_get_all_plants_pagination(self, app_context, plant_service):
        """Test paginated plant retrieval"""
        mock_plants = [Mock() for _ in range(10)]
        for i, plant in enumerate(mock_plants):
            plant.to_dict.return_value = {"id": i + 1, "name": f"Plant {i+1}"}

        with patch("src.models.landscape.Plant.query") as mock_query:
            mock_pagination = Mock()
            mock_pagination.items = mock_plants
            mock_pagination.total = 25
            mock_pagination.pages = 3
            mock_pagination.has_next = True
            mock_pagination.has_prev = False

            mock_query.order_by.return_value.paginate.return_value = mock_pagination

            result = plant_service.get_all(page=1, per_page=10)

            assert len(result["plants"]) == 10
            assert result["total"] == 25
            assert result["pages"] == 3
            assert result["current_page"] == 1
            mock_query.order_by.return_value.paginate.assert_called_once_with(page=1, per_page=10, error_out=False)

    def test_database_error_handling(self, app_context, plant_service, sample_plant_data):
        """Test database error handling"""
        with patch("src.models.user.db.session") as mock_session:

            mock_session.commit.side_effect = Exception("Database error")

            # Mock the model class
            with patch.object(plant_service, "model_class") as mock_model_class:
                mock_plant = Mock()
                mock_model_class.return_value = mock_plant
                mock_model_class.__name__ = "Plant"

                with pytest.raises(Exception):
                    plant_service.create(sample_plant_data)

                mock_session.rollback.assert_called_once()
