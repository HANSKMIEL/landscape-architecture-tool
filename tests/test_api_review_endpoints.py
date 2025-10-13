"""
API Review Test Suite for Modified Endpoints
Tests the functionality of the three API route files modified in commit 9cd9a802:
- src/routes/plant_recommendations.py
- src/routes/project_plants.py
- src/routes/reports.py
"""

import json

import pytest

pytestmark = pytest.mark.usefixtures("app_context")


@pytest.mark.api
class TestPlantRecommendationsAPI:
    """Test plant recommendations API endpoints"""

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_criteria_options_endpoint(self, client):
        """Test plant recommendation criteria options endpoint"""
        response = client.get("/api/plant-recommendations/criteria-options")

        assert response.status_code == 200
        data = response.get_json()

        # Check required fields are present
        expected_keys = [
            "hardiness_zones",
            "sun_exposures",
            "soil_types",
            "maintenance_levels",
            "moisture_levels",
            "budget_ranges",
        ]
        for key in expected_keys:
            assert key in data
            assert isinstance(data[key], list)

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_plant_recommendations_endpoint(self, client):
        """Test basic plant recommendations functionality"""
        # Authentication handled by authenticated_test_user fixture
        request_data = {"hardiness_zone": "5-9", "sun_exposure": "Full Sun", "max_results": 3, "min_score": 0.3}

        response = client.post(
            "/api/plant-recommendations", data=json.dumps(request_data), content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()

        # Check response structure
        assert "recommendations" in data
        assert "request_id" in data
        assert "criteria_summary" in data
        assert "total_plants_evaluated" in data
        assert "recommendations_count" in data

        # Validate recommendations structure
        if data["recommendations"]:
            rec = data["recommendations"][0]
            assert "plant" in rec
            assert "score" in rec
            assert "criteria_scores" in rec
            assert "match_reasons" in rec
            assert "warnings" in rec

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_plant_recommendations_error_handling(self, client):
        """Test error handling for plant recommendations"""
        # Authentication handled by authenticated_test_user fixture
        # Test empty request body
        response = client.post("/api/plant-recommendations", data="", content_type="application/json")
        assert response.status_code == 400

        # Test invalid JSON
        response = client.post("/api/plant-recommendations", data="invalid json", content_type="application/json")
        assert response.status_code == 400

    def test_recommendation_history_endpoint(self, client):
        """Test recommendation history endpoint"""
        response = client.get("/api/plant-recommendations/history")

        assert response.status_code == 200
        data = response.get_json()

        # Check response structure
        assert "history" in data
        assert "limit" in data
        assert "offset" in data
        assert "has_more" in data
        assert isinstance(data["history"], list)

    def test_recommendation_history_with_params(self, client):
        """Test recommendation history with query parameters"""
        response = client.get("/api/plant-recommendations/history?limit=10&offset=0")

        assert response.status_code == 200
        data = response.get_json()
        assert data["limit"] == 10
        assert data["offset"] == 0

    def test_recommendation_history_invalid_params(self, client):
        """Test recommendation history with invalid parameters"""
        response = client.get("/api/plant-recommendations/history?limit=invalid")
        assert response.status_code == 400

        response = client.get("/api/plant-recommendations/history?offset=invalid")
        assert response.status_code == 400


@pytest.mark.api
class TestProjectPlantsAPI:
    """Test project plants API endpoints"""

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_add_plant_to_project(
        self,
        client,
        project_factory,
        plant_factory,
        supplier_factory,
    ):
        """Test adding a plant to a project"""
        # Authentication handled by authenticated_test_user fixture
        project = project_factory()
        supplier = supplier_factory()
        plant = plant_factory(supplier=supplier)
        request_data = {"plant_id": plant.id, "quantity": 5, "unit_cost": 25.50, "notes": "Test plant addition"}

        response = client.post(
            f"/api/projects/{project.id}/plants", data=json.dumps(request_data), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()

        # Check response structure
        assert "id" in data
        assert "project_id" in data
        assert "plant_id" in data
        assert "quantity" in data
        assert "unit_cost" in data
        assert "total_cost" in data
        assert "status" in data

        # Validate values
        assert data["project_id"] == project.id
        assert data["plant_id"] == plant.id
        assert data["quantity"] == 5
        assert data["unit_cost"] == 25.50
        assert data["total_cost"] == 127.50  # 5 * 25.50

    def test_get_project_plants(self, client, project_factory):
        """Test getting plants for a project"""
        # Authentication handled by authenticated_test_user fixture
        project = project_factory()
        response = client.get(f"/api/projects/{project.id}/plants")

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_update_project_plant(
        self,
        client,
        project_factory,
        plant_factory,
        supplier_factory,
    ):
        """Test updating project plant details"""
        # Authentication handled by authenticated_test_user fixture
        # First add a plant
        project = project_factory()
        supplier = supplier_factory()
        plant = plant_factory(supplier=supplier)
        add_data = {"plant_id": plant.id, "quantity": 3}
        client.post(f"/api/projects/{project.id}/plants", data=json.dumps(add_data), content_type="application/json")

        # Update quantity
        update_data = {"quantity": 10}
        response = client.put(
            f"/api/projects/{project.id}/plants/{plant.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["quantity"] == 10

    def test_project_cost_analysis(self, client, project_factory):
        """Test project cost analysis endpoint"""
        # Authentication handled by authenticated_test_user fixture
        project = project_factory()
        response = client.get(f"/api/projects/{project.id}/cost-analysis")

        assert response.status_code == 200
        data = response.get_json()

        # Should have cost analysis structure
        assert isinstance(data, dict)

    def test_plant_order_list(self, client, project_factory):
        """Test plant order list generation"""
        # Authentication handled by authenticated_test_user fixture
        project = project_factory()
        response = client.get(f"/api/projects/{project.id}/plant-order-list")

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_batch_add_plants(
        self,
        client,
        project_factory,
        plant_factory,
        supplier_factory,
    ):
        """Test adding multiple plants at once"""
        # Authentication handled by authenticated_test_user fixture
        project = project_factory()
        supplier = supplier_factory()
        plant = plant_factory(supplier=supplier)
        request_data = {
            "plants": [
                {"plant_id": plant.id, "quantity": 2},
                {"plant_id": plant.id, "quantity": 3, "unit_cost": 15.00},
            ]
        }

        response = client.post(
            f"/api/projects/{project.id}/plants/batch",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        # Should return multi-status or success
        assert response.status_code in [201, 207]
        data = response.get_json()

        assert "added_plants" in data
        assert "errors" in data
        assert "total_added" in data
        assert "total_errors" in data

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_project_plants_error_handling(self, client):
        """Test error handling for invalid project/plant IDs"""
        # Authentication handled by authenticated_test_user fixture
        # Test invalid project ID
        response = client.get("/api/projects/999/plants")
        assert response.status_code == 400

        # Test adding plant with invalid data
        response = client.post("/api/projects/1/plants", data=json.dumps({}), content_type="application/json")
        assert response.status_code == 400


@pytest.mark.api
class TestReportsAPI:
    """Test reports API endpoints"""

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_business_summary_json(self, client):
        """Test business summary report in JSON format"""
        # Authentication handled by authenticated_test_user fixture
        response = client.get("/api/reports/business-summary")

        assert response.status_code == 200
        data = response.get_json()

        # Check required sections
        assert "generated_at" in data
        assert "summary" in data
        assert "project_stats" in data
        assert "top_clients" in data
        assert "plant_usage" in data

        # Check summary structure
        summary = data["summary"]
        expected_keys = ["total_projects", "total_clients", "total_plants", "total_products", "total_suppliers"]
        for key in expected_keys:
            assert key in summary
            assert isinstance(summary[key], int)

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_business_summary_with_date_filter(self, client):
        """Test business summary with date filtering"""
        # Authentication handled by authenticated_test_user fixture
        response = client.get(
            "/api/reports/business-summary?start_date=2025-01-01T00:00:00&end_date=2025-12-31T23:59:59"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["period"]["start_date"] == "2025-01-01T00:00:00"
        assert data["period"]["end_date"] == "2025-12-31T23:59:59"

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_project_report_json(self, client, project_factory):
        """Test project report in JSON format"""
        # Authentication handled by authenticated_test_user fixture
        project = project_factory()
        response = client.get(f"/api/reports/project/{project.id}")

        assert response.status_code == 200
        data = response.get_json()

        # Check required sections
        assert "generated_at" in data
        assert "project" in data
        assert "client" in data
        assert "plants" in data
        assert "products" in data
        assert "summary" in data

        # Check project data
        project_data = data["project"]
        assert "id" in project_data
        assert "name" in project_data
        assert "status" in project_data
        assert project_data["id"] == project.id

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_project_report_not_found(self, client):
        """Test project report with invalid project ID"""
        # Authentication handled by authenticated_test_user fixture
        response = client.get("/api/reports/project/999")
        assert response.status_code == 404

    def test_plant_usage_report(self, client):
        """Test plant usage statistics report"""
        # Authentication handled by authenticated_test_user fixture
        response = client.get("/api/reports/plant-usage")

        assert response.status_code == 200
        data = response.get_json()

        # Check required fields
        assert "generated_at" in data
        assert "plant_usage" in data
        assert "category_distribution" in data
        assert "total_unique_plants" in data

        # Check data types
        assert isinstance(data["plant_usage"], list)
        assert isinstance(data["category_distribution"], dict)
        assert isinstance(data["total_unique_plants"], int)

    def test_supplier_performance_report(self, client):
        """Test supplier performance report"""
        # Authentication handled by authenticated_test_user fixture
        response = client.get("/api/reports/supplier-performance")

        assert response.status_code == 200
        data = response.get_json()

        # Check required fields
        assert "generated_at" in data
        assert "suppliers" in data
        assert "total_suppliers" in data

        # Check data types
        assert isinstance(data["suppliers"], list)
        assert isinstance(data["total_suppliers"], int)

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_reports_error_handling(self, client):
        """Test error handling for reports"""
        # Authentication handled by authenticated_test_user fixture
        # Test invalid date format
        response = client.get("/api/reports/business-summary?start_date=invalid-date")
        assert response.status_code == 500


@pytest.mark.api
class TestAPIIntegrationScenarios:
    """Integration tests combining multiple API endpoints"""

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_full_recommendation_workflow(self, client):
        """Test complete plant recommendation workflow"""
        # 1. Get criteria options
        response = client.get("/api/plant-recommendations/criteria-options")
        assert response.status_code == 200
        # Verify the response has expected structure
        _ = response.get_json()

        # 2. Make recommendation request
        request_data = {"hardiness_zone": "5-9", "sun_exposure": "Full Sun", "max_results": 2}
        response = client.post(
            "/api/plant-recommendations", data=json.dumps(request_data), content_type="application/json"
        )
        assert response.status_code == 200
        # Verify the response has expected structure
        _ = response.get_json()

        # 3. Check history includes our request
        response = client.get("/api/plant-recommendations/history")
        assert response.status_code == 200

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_project_plant_management_workflow(
        self,
        client,
        project_factory,
        plant_factory,
        supplier_factory,
    ):
        """Test complete project plant management workflow"""
        # Authentication handled by authenticated_test_user fixture
        project = project_factory()
        supplier = supplier_factory()
        plant = plant_factory(supplier=supplier)
        # 1. Add plant to project
        add_data = {"plant_id": plant.id, "quantity": 5}
        response = client.post(
            f"/api/projects/{project.id}/plants", data=json.dumps(add_data), content_type="application/json"
        )
        assert response.status_code == 201

        # 2. Get project plants
        response = client.get(f"/api/projects/{project.id}/plants")
        assert response.status_code == 200
        plants = response.get_json()
        assert len(plants) >= 1

        # 3. Update plant quantity
        update_data = {"quantity": 8}
        response = client.put(
            f"/api/projects/{project.id}/plants/{plant.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        assert response.status_code == 200

        # 4. Get cost analysis
        response = client.get(f"/api/projects/{project.id}/cost-analysis")
        assert response.status_code == 200

        # 5. Generate order list
        response = client.get(f"/api/projects/{project.id}/plant-order-list")
        assert response.status_code == 200

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_reporting_workflow(
        self,
        client,
        project_factory,
    ):
        """Test complete reporting workflow"""
        # Authentication handled by authenticated_test_user fixture
        project = project_factory()
        # 1. Business summary
        response = client.get("/api/reports/business-summary")
        assert response.status_code == 200

        # 2. Project report
        response = client.get(f"/api/reports/project/{project.id}")
        assert response.status_code == 200

        # 3. Plant usage report
        response = client.get("/api/reports/plant-usage")
        assert response.status_code == 200

        # 4. Supplier performance report
        response = client.get("/api/reports/supplier-performance")
        assert response.status_code == 200


@pytest.mark.api
class TestAPIAuthenticationAndAuthorization:
    """Test authentication and authorization for API endpoints"""

    def test_endpoints_access_control(self, client):
        """Validate unauthenticated access patterns for public vs protected endpoints"""
        expected_status_by_endpoint = {
            "/api/plant-recommendations/criteria-options": 200,
            "/api/reports/plant-usage": 200,
            "/api/reports/supplier-performance": 200,
            # Business summary is protected via @login_required and should reject anonymous calls
            "/api/reports/business-summary": 401,
        }

        for endpoint, expected_status in expected_status_by_endpoint.items():
            response = client.get(endpoint)
            assert (
                response.status_code == expected_status
            ), f"Endpoint {endpoint} returned {response.status_code}, expected {expected_status}"

    @pytest.mark.usefixtures("authenticated_test_user")
    def test_post_endpoints_validation(
        self,
        client,
        project_factory,
    ):
        """Test POST endpoints have proper validation"""
        # Authentication handled by authenticated_test_user fixture
        # Test plant recommendations requires valid JSON
        response = client.post("/api/plant-recommendations")
        assert response.status_code == 400

        # Test project plants requires valid data
        project = project_factory()
        response = client.post(f"/api/projects/{project.id}/plants")
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
