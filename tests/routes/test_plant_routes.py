"""
Test Plant Routes

Comprehensive tests for plant API endpoints.
"""

import json

import pytest

from src.models.landscape import Plant
from tests.fixtures.database import DatabaseTestMixin


@pytest.mark.api
class TestPlantRoutes(DatabaseTestMixin):
    """Test Plant API endpoints"""

    def test_get_plants_empty(self, client, app_context):
        """Test getting plants when database is empty"""
        response = client.get("/api/plants")

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)  # API returns structured response consistently
        assert "plants" in data
        assert data["plants"] == []
        assert data["total"] == 0
        assert data["current_page"] == 1
        assert data["pages"] == 0

    def test_get_plants_with_data(self, client, app_context, sample_plants):
        """Test getting plants with sample data"""
        response = client.get("/api/plants")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 5
        assert data["total"] == 5
        assert all("id" in plant for plant in data["plants"])
        assert all("name" in plant for plant in data["plants"])

    def test_get_plants_with_search(self, client, app_context, plant_factory):
        """Test getting plants with search parameter"""
        plant1 = plant_factory(name="Rose Garden", common_name="Red Rose")  # noqa: F841
        plant2 = plant_factory(name="Lily Pond", common_name="Water Lily")  # noqa: F841
        plant3 = plant_factory(name="Oak Tree", common_name="White Oak")  # noqa: F841

        # Search by name
        response = client.get("/api/plants?search=Rose")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 1
        assert data["plants"][0]["name"] == "Rose Garden"

        # Search by common name
        response = client.get("/api/plants?search=Lily")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 1
        assert data["plants"][0]["name"] == "Lily Pond"

    def test_get_plants_with_category_filter(self, client, app_context, plant_factory):
        """Test getting plants with category filter"""
        plant1 = plant_factory(category="Tree")  # noqa: F841
        plant2 = plant_factory(category="Shrub")  # noqa: F841
        plant3 = plant_factory(category="Tree")  # noqa: F841

        response = client.get("/api/plants?category=Tree")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 2
        assert all(plant["category"] == "Tree" for plant in data["plants"])

    def test_get_plants_with_sun_requirements_filter(
        self, client, app_context, plant_factory
    ):
        """Test getting plants with sun requirements filter"""
        plant1 = plant_factory(sun_exposure="full_sun")  # noqa: F841
        plant2 = plant_factory(sun_exposure="partial_shade")  # noqa: F841
        plant3 = plant_factory(sun_exposure="full_sun")  # noqa: F841

        response = client.get("/api/plants?sun_exposure=full_sun")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 2
        assert all(plant["sun_exposure"] == "full_sun" for plant in data["plants"])

    def test_get_plants_with_native_filter(self, client, app_context, plant_factory):
        """Test getting plants with native filter"""
        native_plant = plant_factory(native=True)  # noqa: F841
        non_native_plant = plant_factory(native=False)  # noqa: F841

        response = client.get("/api/plants?native_only=true")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 1
        assert data["plants"][0]["native"] is True

    def test_get_plants_pagination(self, client, app_context, plant_factory):
        """Test plants pagination"""
        # Create 15 plants
        for i in range(15):
            plant_factory(name=f"Plant {i}")

        # Test first page
        response = client.get("/api/plants?page=1&per_page=10")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 10
        assert data["total"] == 15
        assert data["pages"] == 2
        assert data["current_page"] == 1

        # Test second page
        response = client.get("/api/plants?page=2&per_page=10")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 5
        assert data["current_page"] == 2

    def test_get_plants_combined_filters(self, client, app_context, plant_factory):
        """Test getting plants with multiple filters combined"""
        _ = plant_factory(
            name="Native Oak", category="Tree", native=True, sun_exposure="full_sun"
        )
        plant2 = plant_factory(  # noqa: F841
            name="Import Rose", category="Shrub", native=False, sun_exposure="full_sun"
        )
        plant3 = plant_factory(  # noqa: F841
            name="Native Pine",
            category="Tree",
            native=True,
            sun_exposure="partial_shade",
        )

        # Filter by category and native status
        response = client.get("/api/plants?category=Tree&native_only=true")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 2
        assert all(
            plant["category"] == "Tree" and plant["native"] for plant in data["plants"]
        )

    def test_create_plant_success(self, client, app_context, sample_supplier):
        """Test creating a plant successfully"""
        plant_data = {
            "name": "Test Plant",
            "common_name": "Common Test Plant",
            "category": "Shrub",
            "height_min": 50.0,
            "height_max": 150.0,
            "sun_exposure": "full_sun",
            "price": 25.99,
            "supplier_id": sample_supplier.id,
        }

        response = client.post(
            "/api/plants", data=json.dumps(plant_data), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Test Plant"
        assert data["common_name"] == "Common Test Plant"
        assert data["category"] == "Shrub"
        assert data["price"] == 25.99

        # Verify in database
        self.assert_record_count(Plant, 1)

    def test_create_plant_minimal_data(self, client, app_context):
        """Test creating plant with minimal required data"""
        plant_data = {"name": "Minimal Plant", "category": "Tree"}

        response = client.post(
            "/api/plants", data=json.dumps(plant_data), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Minimal Plant"
        assert data["category"] == "Tree"

    def test_create_plant_missing_required_fields(self, client, app_context):
        """Test creating plant with missing required fields"""
        plant_data = {"common_name": "Missing Name Plant"}

        response = client.post(
            "/api/plants", data=json.dumps(plant_data), content_type="application/json"
        )

        assert response.status_code == 422
        data = response.get_json()
        assert "error" in data

    def test_create_plant_invalid_data_types(self, client, app_context):
        """Test creating plant with invalid data types"""
        plant_data = {
            "name": "Test Plant",
            "category": "Tree",
            "height_min": "not_a_number",
            "price": "invalid_price",
        }

        response = client.post(
            "/api/plants", data=json.dumps(plant_data), content_type="application/json"
        )

        assert response.status_code == 422
        data = response.get_json()
        assert "error" in data

    def test_get_plant_by_id_success(self, client, app_context, sample_plant):
        """Test getting a specific plant by ID"""
        response = client.get(f"/api/plants/{sample_plant.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == sample_plant.id
        assert data["name"] == sample_plant.name

    def test_get_plant_by_id_not_found(self, client, app_context):
        """Test getting plant by non-existent ID"""
        response = client.get("/api/plants/999")

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_update_plant_success(self, client, app_context, sample_plant):
        """Test updating a plant successfully"""
        update_data = {
            "name": "Updated Plant Name",
            "price": 35.99,
            "notes": "Updated notes",
        }

        response = client.put(
            f"/api/plants/{sample_plant.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Updated Plant Name"
        assert data["price"] == 35.99
        assert data["notes"] == "Updated notes"

    def test_update_plant_not_found(self, client, app_context):
        """Test updating non-existent plant"""
        update_data = {"name": "Updated Name"}

        response = client.put(
            "/api/plants/999",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_update_plant_invalid_data(self, client, app_context, sample_plant):
        """Test updating plant with invalid data"""
        update_data = {"height_min": 200.0, "height_max": 100.0}  # Invalid: max < min

        response = client.put(
            f"/api/plants/{sample_plant.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_delete_plant_success(self, client, app_context, sample_plant):
        """Test deleting a plant successfully"""
        plant_id = sample_plant.id

        response = client.delete(f"/api/plants/{plant_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Plant deleted successfully"

        # Verify deletion
        self.assert_record_count(Plant, 0)

    def test_delete_plant_not_found(self, client, app_context):
        """Test deleting non-existent plant"""
        response = client.delete("/api/plants/999")

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_delete_plant_with_project_associations(
        self, client, app_context, sample_plant, project_factory, client_factory
    ):
        """Test deleting plant that has project associations"""
        client_obj = client_factory()
        project = project_factory(client=client_obj)  # noqa: F841

        # Add plant to project (would need to create ProjectPlant relationship)
        # This test verifies business logic constraints

        response = client.delete(f"/api/plants/{sample_plant.id}")

        # Depending on business rules, this might succeed or fail
        # If cascading deletes are allowed, should succeed
        # If referential integrity is enforced, should fail
        assert response.status_code in [200, 400, 409]

    def test_get_plant_categories(self, client, app_context, plant_factory):
        """Test getting unique plant categories"""
        plant_factory(category="Tree")
        plant_factory(category="Shrub")
        plant_factory(category="Tree")  # Duplicate
        plant_factory(category="Perennial")

        response = client.get("/api/plants/categories")

        assert response.status_code == 200
        data = response.get_json()
        assert "categories" in data
        categories = data["categories"]
        assert len(categories) == 3
        assert "Tree" in categories
        assert "Shrub" in categories
        assert "Perennial" in categories

    def test_plant_search_suggestions(self, client, app_context, plant_factory):
        """Test plant search suggestions endpoint"""
        plant_factory(name="Rose Garden", common_name="Red Rose")
        plant_factory(name="Rose Bush", common_name="Pink Rose")
        plant_factory(name="Lily Pond", common_name="Water Lily")

        response = client.get("/api/plants/search-suggestions?q=Rose")

        assert response.status_code == 200
        data = response.get_json()
        assert "suggestions" in data
        suggestions = data["suggestions"]
        assert len(suggestions) == 2
        assert all("Rose" in suggestion["name"] for suggestion in suggestions)

    def test_plants_export(self, client, app_context, sample_plants):
        """Test exporting plants data"""
        response = client.get("/api/plants/export?format=json")

        assert response.status_code == 200
        data = response.get_json()
        assert "plants" in data
        assert len(data["plants"]) == 5

    def test_plants_bulk_import(self, client, app_context, sample_supplier):
        """Test bulk importing plants"""
        plants_data = {
            "plants": [
                {
                    "name": "Bulk Plant 1",
                    "category": "Tree",
                    "supplier_id": sample_supplier.id,
                },
                {
                    "name": "Bulk Plant 2",
                    "category": "Shrub",
                    "supplier_id": sample_supplier.id,
                },
            ]
        }

        response = client.post(
            "/api/plants/bulk-import",
            data=json.dumps(plants_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["imported_count"] == 2

        # Verify in database
        self.assert_record_count(Plant, 2)

    def test_plants_error_handling(self, client, app_context):
        """Test API error handling"""
        # Test invalid JSON
        response = client.post(
            "/api/plants", data="invalid json", content_type="application/json"
        )

        assert response.status_code == 400

        # Test missing content type
        response = client.post("/api/plants", data='{"name": "Test"}')

        assert response.status_code == 400

    def test_plants_validation_detailed(self, client, app_context):
        """Test detailed validation responses"""
        plant_data = {
            "name": "",  # Empty name
            "category": "InvalidCategory",
            "height_min": -10,  # Negative
            "height_max": 5,  # Less than min
            "price": "not_a_number",
        }

        response = client.post(
            "/api/plants", data=json.dumps(plant_data), content_type="application/json"
        )

        assert response.status_code == 422
        data = response.get_json()
        assert "validation_errors" in data
        errors = data["validation_errors"]
        assert len(errors) > 0


@pytest.mark.integration
class TestPlantRoutesIntegration(DatabaseTestMixin):
    """Integration tests for Plant API endpoints"""

    def test_full_plant_api_workflow(self, client, app_context, supplier_factory):
        """Test complete plant API workflow"""
        supplier = supplier_factory()

        # Create plant
        plant_data = {
            "name": "Workflow Test Plant",
            "common_name": "Test Plant",
            "category": "Tree",
            "height_min": 100.0,
            "height_max": 300.0,
            "supplier_id": supplier.id,
            "price": 45.99,
            "native": True,
        }

        # 1. Create plant
        response = client.post(
            "/api/plants", data=json.dumps(plant_data), content_type="application/json"
        )
        assert response.status_code == 201
        created_plant = response.get_json()
        plant_id = created_plant["id"]

        # 2. Get plant by ID
        response = client.get(f"/api/plants/{plant_id}")
        assert response.status_code == 200
        retrieved_plant = response.get_json()
        assert retrieved_plant["name"] == "Workflow Test Plant"

        # 3. Update plant
        update_data = {"price": 55.99, "notes": "Updated in workflow test"}
        response = client.put(
            f"/api/plants/{plant_id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        assert response.status_code == 200
        updated_plant = response.get_json()
        assert updated_plant["price"] == 55.99

        # 4. Search for plant
        response = client.get("/api/plants?search=Workflow")
        assert response.status_code == 200
        search_results = response.get_json()
        assert len(search_results["plants"]) == 1
        assert search_results["plants"][0]["id"] == plant_id

        # 5. Delete plant
        response = client.delete(f"/api/plants/{plant_id}")
        assert response.status_code == 200

        # 6. Verify deletion
        response = client.get(f"/api/plants/{plant_id}")
        assert response.status_code == 404

    def test_plant_filtering_combinations(self, client, app_context, plant_factory):
        """Test various combinations of plant filters"""
        # Create diverse plants
        plants = [  # noqa: F841
            plant_factory(
                name="Native Oak", category="Tree", native=True, sun_exposure="full_sun"
            ),
            plant_factory(
                name="Import Rose",
                category="Shrub",
                native=False,
                sun_exposure="full_sun",
            ),
            plant_factory(
                name="Native Pine",
                category="Tree",
                native=True,
                sun_exposure="partial_shade",
            ),
            plant_factory(
                name="Shade Fern",
                category="Perennial",
                native=True,
                sun_exposure="full_shade",
            ),
        ]

        # Test category + native filter
        response = client.get("/api/plants?category=Tree&native_only=true")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 2

        # Test sun exposure + native filter
        response = client.get("/api/plants?sun_exposure=full_sun&native_only=true")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 1
        assert data["plants"][0]["name"] == "Native Oak"

        # Test search + category filter
        response = client.get("/api/plants?search=Native&category=Tree")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 2

    def test_plant_pagination_edge_cases(self, client, app_context, plant_factory):
        """Test plant pagination edge cases"""
        # Create exactly 10 plants
        for i in range(10):
            plant_factory(name=f"Plant {i:02d}")

        # Test page beyond available data
        response = client.get("/api/plants?page=5&per_page=10")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 0
        assert data["current_page"] == 5

        # Test large per_page value
        response = client.get("/api/plants?per_page=1000")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 10

        # Test invalid page parameters
        response = client.get("/api/plants?page=-1")
        assert response.status_code == 422

        response = client.get("/api/plants?per_page=0")
        assert response.status_code == 422
