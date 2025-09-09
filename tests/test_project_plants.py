"""
Tests for Project-Plant Relationship Management

Comprehensive test suite for project-plant functionality including
CRUD operations, cost calculations, and business logic validation.
"""

import json

import pytest
from tests.fixtures.auth_fixtures import authenticated_test_user, setup_test_authentication

from src.main import create_app
from src.models.landscape import Client, Plant, Project, Supplier
from src.models.user import db
from src.services.project_plant import ProjectPlantService


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def init_database(app):
    """Initialize database with test data"""
    with app.app_context():
        # Create test supplier
        supplier = Supplier(
            name="Test Nursery",
            contact_person="John Doe",
            email="john@testnursery.com",
            phone="555-0123",
        )
        db.session.add(supplier)
        db.session.flush()

        # Create test client
        test_client = Client(name="Test Client", email="client@test.com", phone="555-0456")
        db.session.add(test_client)
        db.session.flush()

        # Create test project
        project = Project(
            name="Test Garden Project",
            description="A beautiful test garden",
            client_id=test_client.id,
            budget=5000.0,
        )
        db.session.add(project)
        db.session.flush()

        # Create test plants
        plant1 = Plant(
            name="Rosa rugosa",
            common_name="Beach Rose",
            category="Shrub",
            price=25.99,
            supplier_id=supplier.id,
        )
        plant2 = Plant(
            name="Lavandula angustifolia",
            common_name="English Lavender",
            category="Perennial",
            price=12.50,
            supplier_id=supplier.id,
        )
        db.session.add_all([plant1, plant2])
        db.session.commit()

        return {
            "supplier_id": supplier.id,
            "client_id": test_client.id,
            "project_id": project.id,
            "plant1_id": plant1.id,
            "plant2_id": plant2.id,
        }


class TestProjectPlantService:
    """Test project-plant service functionality"""

    def test_add_plant_to_project(self, app, init_database):
        """Test adding a plant to a project"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            service = ProjectPlantService()
            data = init_database

            # Add plant to project
            project_plant = service.add_plant_to_project(
                project_id=data["project_id"],
                plant_id=data["plant1_id"],
                quantity=5,
                unit_cost=25.99,
                notes="Front border planting",
            )

            assert project_plant.project_id == data["project_id"]
            assert project_plant.plant_id == data["plant1_id"]
            assert project_plant.quantity == 5
            assert project_plant.unit_cost == 25.99
            assert project_plant.notes == "Front border planting"
            assert project_plant.status == "planned"

    def test_add_duplicate_plant_updates_quantity(self, app, init_database):
        """Test adding the same plant twice updates quantity"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            service = ProjectPlantService()
            data = init_database

            # Add plant first time
            service.add_plant_to_project(project_id=data["project_id"], plant_id=data["plant1_id"], quantity=3)

            # Add same plant again
            project_plant = service.add_plant_to_project(
                project_id=data["project_id"], plant_id=data["plant1_id"], quantity=2
            )

            # Should update quantity, not create duplicate
            assert project_plant.quantity == 5

    def test_update_plant_quantity(self, app, init_database):
        """Test updating plant quantities"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            service = ProjectPlantService()
            data = init_database

            # Add plant to project
            service.add_plant_to_project(project_id=data["project_id"], plant_id=data["plant1_id"], quantity=5)

            # Update quantity
            updated = service.update_plant_quantity(
                project_id=data["project_id"],
                plant_id=data["plant1_id"],
                new_quantity=10,
            )

            assert updated.quantity == 10

    def test_update_plant_status(self, app, init_database):
        """Test updating plant status"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            service = ProjectPlantService()
            data = init_database

            # Add plant to project
            service.add_plant_to_project(project_id=data["project_id"], plant_id=data["plant1_id"], quantity=5)

            # Update status
            updated = service.update_plant_status(
                project_id=data["project_id"],
                plant_id=data["plant1_id"],
                status="ordered",
            )

            assert updated.status == "ordered"

    def test_calculate_project_cost(self, app, init_database):
        """Test project cost calculations"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            service = ProjectPlantService()
            data = init_database

            # Add plants to project
            service.add_plant_to_project(
                project_id=data["project_id"],
                plant_id=data["plant1_id"],
                quantity=5,
                unit_cost=25.99,
            )
            service.add_plant_to_project(
                project_id=data["project_id"],
                plant_id=data["plant2_id"],
                quantity=10,
                unit_cost=12.50,
            )

            # Calculate cost
            cost_analysis = service.calculate_project_cost(data["project_id"])

            expected_total = (5 * 25.99) + (10 * 12.50)  # 129.95 + 125.00 = 254.95

            assert cost_analysis["total_cost"] == expected_total
            assert cost_analysis["plants_with_cost"] == 2
            assert cost_analysis["plants_without_cost"] == 0
            assert cost_analysis["total_plants"] == 2
            assert len(cost_analysis["cost_breakdown"]) == 2

    def test_generate_plant_order_list(self, app, init_database):
        """Test plant order list generation"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            service = ProjectPlantService()
            data = init_database

            # Add plants to project
            service.add_plant_to_project(
                project_id=data["project_id"],
                plant_id=data["plant1_id"],
                quantity=5,
                unit_cost=25.99,
                notes="Front border",
            )
            service.add_plant_to_project(
                project_id=data["project_id"],
                plant_id=data["plant2_id"],
                quantity=10,
                unit_cost=12.50,
                notes="Herb garden",
            )

            # Generate order list
            order_list = service.generate_plant_order_list(data["project_id"])

            assert len(order_list) == 1  # Both plants from same supplier
            supplier_order = order_list[0]
            assert supplier_order["supplier_name"] == "Test Nursery"
            assert len(supplier_order["plants"]) == 2
            assert supplier_order["total_cost"] == (5 * 25.99) + (10 * 12.50)

    def test_remove_plant_from_project(self, app, init_database):
        """Test removing a plant from project"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            service = ProjectPlantService()
            data = init_database

            # Add plant to project
            service.add_plant_to_project(project_id=data["project_id"], plant_id=data["plant1_id"], quantity=5)

            # Remove plant
            result = service.remove_plant_from_project(project_id=data["project_id"], plant_id=data["plant1_id"])

            assert result is True

            # Verify plant is removed
            plants = service.get_project_plant_list(data["project_id"])
            assert len(plants) == 0

    def test_invalid_operations(self, app, init_database):
        """Test error handling for invalid operations"""
        with app.app_context():
            service = ProjectPlantService()
            data = init_database

            # Test invalid project ID
            with pytest.raises(ValueError, match="Project with ID 999 not found"):
                service.add_plant_to_project(999, data["plant1_id"], 1)

            # Test invalid plant ID
            with pytest.raises(ValueError, match="Plant with ID 999 not found"):
                service.add_plant_to_project(data["project_id"], 999, 1)

            # Add a plant first for testing updates
            service.add_plant_to_project(project_id=data["project_id"], plant_id=data["plant1_id"], quantity=5)

            # Test invalid quantity
            with pytest.raises(ValueError, match="Quantity must be greater than 0"):
                service.update_plant_quantity(data["project_id"], data["plant1_id"], 0)

            # Test invalid status
            with pytest.raises(ValueError, match="Invalid status"):
                service.update_plant_status(data["project_id"], data["plant1_id"], "invalid")


class TestProjectPlantAPI:
    """Test project-plant API endpoints"""

    def test_add_plant_to_project_endpoint(self, client, init_database):
        """Test API endpoint for adding plant to project"""
    # Authentication handled by authenticated_test_user fixture
        data = init_database

        response = client.post(
            f'/api/projects/{data["project_id"]}/plants',
            data=json.dumps(
                {
                    "plant_id": data["plant1_id"],
                    "quantity": 5,
                    "unit_cost": 25.99,
                    "notes": "Test notes",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data["quantity"] == 5
        assert response_data["unit_cost"] == 25.99
        assert response_data["notes"] == "Test notes"

    def test_get_project_plants_endpoint(self, client, init_database):
        """Test API endpoint for getting project plants"""
    # Authentication handled by authenticated_test_user fixture
        data = init_database

        # Add plant first
        client.post(
            f'/api/projects/{data["project_id"]}/plants',
            data=json.dumps({"plant_id": data["plant1_id"], "quantity": 5}),
            content_type="application/json",
        )

        # Get plants
        response = client.get(f'/api/projects/{data["project_id"]}/plants')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 1
        assert response_data[0]["quantity"] == 5

    def test_update_project_plant_endpoint(self, client, init_database):
        """Test API endpoint for updating project plant"""
    # Authentication handled by authenticated_test_user fixture
        data = init_database

        # Add plant first
        client.post(
            f'/api/projects/{data["project_id"]}/plants',
            data=json.dumps({"plant_id": data["plant1_id"], "quantity": 5}),
            content_type="application/json",
        )

        # Update quantity
        response = client.put(
            f'/api/projects/{data["project_id"]}/plants/{data["plant1_id"]}',
            data=json.dumps({"quantity": 10}),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["quantity"] == 10

    def test_get_cost_analysis_endpoint(self, client, init_database):
        """Test API endpoint for cost analysis"""
        data = init_database

        # Add plants first
        client.post(
            f'/api/projects/{data["project_id"]}/plants',
            data=json.dumps({"plant_id": data["plant1_id"], "quantity": 5, "unit_cost": 25.99}),
            content_type="application/json",
        )

        # Get cost analysis
        response = client.get(f'/api/projects/{data["project_id"]}/cost-analysis')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["total_cost"] == 5 * 25.99
        assert response_data["total_plants"] == 1

    def test_get_plant_order_list_endpoint(self, client, init_database):
        """Test API endpoint for plant order list"""
    # Authentication handled by authenticated_test_user fixture
        data = init_database

        # Add plants first
        client.post(
            f'/api/projects/{data["project_id"]}/plants',
            data=json.dumps({"plant_id": data["plant1_id"], "quantity": 5, "unit_cost": 25.99}),
            content_type="application/json",
        )

        # Get order list
        response = client.get(f'/api/projects/{data["project_id"]}/plant-order-list')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert "suppliers" in response_data
        assert "project_id" in response_data
        assert "total_suppliers" in response_data
        assert len(response_data["suppliers"]) == 1
        assert response_data["suppliers"][0]["supplier_name"] == "Test Nursery"

    def test_remove_plant_endpoint(self, client, init_database):
        """Test API endpoint for removing plant from project"""
    # Authentication handled by authenticated_test_user fixture
        data = init_database

        # Add plant first
        client.post(
            f'/api/projects/{data["project_id"]}/plants',
            data=json.dumps({"plant_id": data["plant1_id"], "quantity": 5}),
            content_type="application/json",
        )

        # Remove plant
        response = client.delete(f'/api/projects/{data["project_id"]}/plants/{data["plant1_id"]}')

        assert response.status_code == 200

        # Verify plant is removed
        response = client.get(f'/api/projects/{data["project_id"]}/plants')
        response_data = json.loads(response.data)
        assert len(response_data) == 0

    def test_batch_add_plants_endpoint(self, client, init_database):
        """Test API endpoint for adding multiple plants"""
    # Authentication handled by authenticated_test_user fixture
        data = init_database

        response = client.post(
            f'/api/projects/{data["project_id"]}/plants/batch',
            data=json.dumps(
                {
                    "plants": [
                        {
                            "plant_id": data["plant1_id"],
                            "quantity": 5,
                            "unit_cost": 25.99,
                        },
                        {
                            "plant_id": data["plant2_id"],
                            "quantity": 10,
                            "unit_cost": 12.50,
                        },
                    ]
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data["total_added"] == 2
        assert response_data["total_errors"] == 0
        assert len(response_data["added_plants"]) == 2


class TestProjectPlantIntegration:
    """Test integration scenarios"""

    def test_full_project_workflow(self, client, init_database):
        """Test complete project-plant workflow"""
    # Authentication handled by authenticated_test_user fixture
        data = init_database

        # 1. Add plants to project
        response = client.post(
            f'/api/projects/{data["project_id"]}/plants/batch',
            data=json.dumps(
                {
                    "plants": [
                        {
                            "plant_id": data["plant1_id"],
                            "quantity": 5,
                            "unit_cost": 25.99,
                            "notes": "Border planting",
                        },
                        {
                            "plant_id": data["plant2_id"],
                            "quantity": 10,
                            "unit_cost": 12.50,
                            "notes": "Herb garden",
                        },
                    ]
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 201

        # 2. Check cost analysis
        response = client.get(f'/api/projects/{data["project_id"]}/cost-analysis')
        assert response.status_code == 200
        cost_data = json.loads(response.data)
        expected_total = (5 * 25.99) + (10 * 12.50)
        assert cost_data["total_cost"] == expected_total

        # 3. Update plant status to ordered
        response = client.put(
            f'/api/projects/{data["project_id"]}/plants/{data["plant1_id"]}',
            data=json.dumps({"status": "ordered"}),
            content_type="application/json",
        )
        assert response.status_code == 200

        # 4. Generate order list
        response = client.get(f'/api/projects/{data["project_id"]}/plant-order-list')
        assert response.status_code == 200
        order_data = json.loads(response.data)
        assert "suppliers" in order_data
        assert len(order_data["suppliers"]) == 1
        assert order_data["suppliers"][0]["supplier_name"] == "Test Nursery"

        # 5. Update remaining plants to planted
        response = client.put(
            f'/api/projects/{data["project_id"]}/plants/{data["plant2_id"]}',
            data=json.dumps({"status": "planted"}),
            content_type="application/json",
        )
        assert response.status_code == 200

        # 6. Final project plant list check
        response = client.get(f'/api/projects/{data["project_id"]}/plants')
        assert response.status_code == 200
        plants_data = json.loads(response.data)
        assert len(plants_data) == 2

        # Verify statuses
        statuses = {plant["plant_id"]: plant["status"] for plant in plants_data}
        assert statuses[data["plant1_id"]] == "ordered"
        assert statuses[data["plant2_id"]] == "planted"
