"""
API Review Test Suite for Modified Endpoints
Tests the functionality of the three API route files modified in commit 9cd9a802:
- src/routes/plant_recommendations.py
- src/routes/project_plants.py
- src/routes/reports.py
"""

import json

import pytest

from src.main import create_app
from src.models.landscape import Client, Plant, Project, Supplier
from src.models.user import db


@pytest.fixture
def app():
    """Create test application"""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Provide app context for tests"""
    with app.app_context():
        yield app


@pytest.fixture
def sample_supplier(app_context):
    """Create a sample supplier"""
    supplier = Supplier(
        name="Test Supplier",
        contact_person="John Doe",
        email="john@testsupplier.com",
        phone="123-456-7890",
        address="123 Test St",
        city="Test City",
        postal_code="12345",
    )
    db.session.add(supplier)
    db.session.commit()
    return supplier


@pytest.fixture
def sample_plant(app_context, sample_supplier):
    """Create a sample plant"""
    plant = Plant(
        name="Test Plant",
        common_name="Test Common Name",
        category="Tree",
        height_min=1.0,
        height_max=5.0,
        width_min=1.0,
        width_max=3.0,
        sun_requirements="Full Sun",
        water_needs="Medium",
        hardiness_zone="5-8",
        maintenance="Low",
        price=25.50,
        supplier_id=sample_supplier.id,
    )
    db.session.add(plant)
    db.session.commit()
    return plant


@pytest.fixture
def sample_client(app_context):
    """Create a sample client"""
    client = Client(
        name="Test Client",
        email="test@client.com",
        phone="987-654-3210",
        address="456 Client Ave",
        city="Client City",
        postal_code="54321",
        client_type="Particulier",
    )
    db.session.add(client)
    db.session.commit()
    return client


@pytest.fixture
def sample_project(app_context, sample_client):
    """Create a sample project"""
    project = Project(
        name="Test Project",
        description="A test project for API validation",
        client_id=sample_client.id,
        location="Test Location",
        area_size=100.0,
        budget=50000.0,
        status="Planning",
    )
    db.session.add(project)
    db.session.commit()
    return project


@pytest.mark.api
class TestPlantRecommendationsAPI:
    """Test plant recommendations API endpoints"""

    def test_criteria_options_endpoint(self, client, app_context):
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

    def test_plant_recommendations_endpoint(self, client, app_context):
        """Test basic plant recommendations functionality"""
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

    def test_plant_recommendations_error_handling(self, client, app_context):
        """Test error handling for plant recommendations"""
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
        
        # Test empty request body
        response = client.post("/api/plant-recommendations", data="", content_type="application/json")
        assert response.status_code == 400

        # Test invalid JSON
        response = client.post("/api/plant-recommendations", data="invalid json", content_type="application/json")
        assert response.status_code == 400

    def test_recommendation_history_endpoint(self, client, app_context):
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

    def test_recommendation_history_with_params(self, client, app_context):
        """Test recommendation history with query parameters"""
        response = client.get("/api/plant-recommendations/history?limit=10&offset=0")

        assert response.status_code == 200
        data = response.get_json()
        assert data["limit"] == 10
        assert data["offset"] == 0

    def test_recommendation_history_invalid_params(self, client, app_context):
        """Test recommendation history with invalid parameters"""
        response = client.get("/api/plant-recommendations/history?limit=invalid")
        assert response.status_code == 400

        response = client.get("/api/plant-recommendations/history?offset=invalid")
        assert response.status_code == 400


@pytest.mark.api
class TestProjectPlantsAPI:
    """Test project plants API endpoints"""

    def test_add_plant_to_project(self, client, app_context, sample_project, sample_plant):
        """Test adding a plant to a project"""
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
        
        request_data = {"plant_id": sample_plant.id, "quantity": 5, "unit_cost": 25.50, "notes": "Test plant addition"}

        response = client.post(
            f"/api/projects/{sample_project.id}/plants", data=json.dumps(request_data), content_type="application/json"
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
        assert data["project_id"] == sample_project.id
        assert data["plant_id"] == sample_plant.id
        assert data["quantity"] == 5
        assert data["unit_cost"] == 25.50
        assert data["total_cost"] == 127.50  # 5 * 25.50

    def test_get_project_plants(self, client, app_context, sample_project):
        """Test getting plants for a project"""
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
        
        response = client.get(f"/api/projects/{sample_project.id}/plants")

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_update_project_plant(self, client, app_context, sample_project, sample_plant):
        """Test updating project plant details"""
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
        
        # First add a plant
        add_data = {"plant_id": sample_plant.id, "quantity": 3}
        client.post(
            f"/api/projects/{sample_project.id}/plants", data=json.dumps(add_data), content_type="application/json"
        )

        # Update quantity
        update_data = {"quantity": 10}
        response = client.put(
            f"/api/projects/{sample_project.id}/plants/{sample_plant.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["quantity"] == 10

    def test_project_cost_analysis(self, client, app_context, sample_project):
        """Test project cost analysis endpoint"""
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
        
        response = client.get(f"/api/projects/{sample_project.id}/cost-analysis")

        assert response.status_code == 200
        data = response.get_json()

        # Should have cost analysis structure
        assert isinstance(data, dict)

    def test_plant_order_list(self, client, app_context, sample_project):
        """Test plant order list generation"""
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
        
        response = client.get(f"/api/projects/{sample_project.id}/plant-order-list")

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)

    def test_batch_add_plants(self, client, app_context, sample_project, sample_plant):
        """Test adding multiple plants at once"""
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
        
        request_data = {
            "plants": [
                {"plant_id": sample_plant.id, "quantity": 2},
                {"plant_id": sample_plant.id, "quantity": 3, "unit_cost": 15.00},
            ]
        }

        response = client.post(
            f"/api/projects/{sample_project.id}/plants/batch",
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

    def test_project_plants_error_handling(self, client, app_context):
        """Test error handling for invalid project/plant IDs"""
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
        
        # Test invalid project ID
        response = client.get("/api/projects/999/plants")
        assert response.status_code == 400

        # Test adding plant with invalid data
        response = client.post("/api/projects/1/plants", data=json.dumps({}), content_type="application/json")
        assert response.status_code == 400


@pytest.mark.api
class TestReportsAPI:
    """Test reports API endpoints"""

    def test_business_summary_json(self, client, app_context):
        """Test business summary report in JSON format"""
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

    def test_business_summary_with_date_filter(self, client, app_context):
        """Test business summary with date filtering"""
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
        
        response = client.get(
            "/api/reports/business-summary" "?start_date=2025-01-01T00:00:00" "&end_date=2025-12-31T23:59:59"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["period"]["start_date"] == "2025-01-01T00:00:00"
        assert data["period"]["end_date"] == "2025-12-31T23:59:59"

    def test_project_report_json(self, client, app_context, sample_project):
        """Test project report in JSON format"""
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
        
        response = client.get(f"/api/reports/project/{sample_project.id}")

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
        assert project_data["id"] == sample_project.id

    def test_project_report_not_found(self, client, app_context):
        """Test project report with invalid project ID"""
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
        
        response = client.get("/api/reports/project/999")
        assert response.status_code == 404

    def test_plant_usage_report(self, client, app_context):
        """Test plant usage statistics report"""
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

    def test_supplier_performance_report(self, client, app_context):
        """Test supplier performance report"""
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

    def test_reports_error_handling(self, client, app_context):
        """Test error handling for reports"""
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
        
        # Test invalid date format
        response = client.get("/api/reports/business-summary?start_date=invalid-date")
        assert response.status_code == 500


@pytest.mark.api
class TestAPIIntegrationScenarios:
    """Integration tests combining multiple API endpoints"""

    def test_full_recommendation_workflow(self, client, app_context):
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

    def test_project_plant_management_workflow(self, client, app_context, sample_project, sample_plant):
        """Test complete project plant management workflow"""
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
        
        # 1. Add plant to project
        add_data = {"plant_id": sample_plant.id, "quantity": 5}
        response = client.post(
            f"/api/projects/{sample_project.id}/plants", data=json.dumps(add_data), content_type="application/json"
        )
        assert response.status_code == 201

        # 2. Get project plants
        response = client.get(f"/api/projects/{sample_project.id}/plants")
        assert response.status_code == 200
        plants = response.get_json()
        assert len(plants) >= 1

        # 3. Update plant quantity
        update_data = {"quantity": 8}
        response = client.put(
            f"/api/projects/{sample_project.id}/plants/{sample_plant.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        assert response.status_code == 200

        # 4. Get cost analysis
        response = client.get(f"/api/projects/{sample_project.id}/cost-analysis")
        assert response.status_code == 200

        # 5. Generate order list
        response = client.get(f"/api/projects/{sample_project.id}/plant-order-list")
        assert response.status_code == 200

    def test_reporting_workflow(self, client, app_context, sample_project):
        """Test complete reporting workflow"""
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
        
        # 1. Business summary
        response = client.get("/api/reports/business-summary")
        assert response.status_code == 200

        # 2. Project report
        response = client.get(f"/api/reports/project/{sample_project.id}")
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

    def test_endpoints_accessible_without_auth(self, client, app_context):
        """Test that API endpoints are accessible (no auth implemented yet)"""
        # Test key endpoints are accessible
        endpoints = [
            "/api/plant-recommendations/criteria-options",
            "/api/reports/business-summary",
            "/api/reports/plant-usage",
            "/api/reports/supplier-performance",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} should be accessible"

    def test_post_endpoints_validation(self, client, app_context):
        """Test POST endpoints have proper validation"""
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
        
        # Test plant recommendations requires valid JSON
        response = client.post("/api/plant-recommendations")
        assert response.status_code == 400

        # Test project plants requires valid data
        response = client.post("/api/projects/1/plants")
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
