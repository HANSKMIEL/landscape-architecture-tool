"""
Test Project Service

Comprehensive tests for project service layer business logic.
"""

from datetime import datetime, timedelta

import pytest

from src.models.landscape import Project, ProjectPlant
from src.models.user import db
from src.services.project_service import ProjectService
from tests.fixtures.database import DatabaseTestMixin


@pytest.mark.service
class TestProjectService(DatabaseTestMixin):
    """Test Project Service operations"""

    def test_get_all_projects_empty(self, app_context):
        """Test getting projects when database is empty"""
        result = ProjectService.get_all_projects()

        assert result["projects"] == []
        assert result["total"] == 0
        assert result["pages"] == 0
        assert result["current_page"] == 1

    def test_get_all_projects_with_data(self, app_context, sample_projects):
        """Test getting projects with sample data"""
        result = ProjectService.get_all_projects()

        assert len(result["projects"]) == 3
        assert result["total"] == 3
        assert result["pages"] == 1
        assert all("id" in project for project in result["projects"])
        assert all("name" in project for project in result["projects"])

    def test_get_all_projects_with_search(
        self, app_context, project_factory, client_factory
    ):
        """Test getting projects with search filter"""
        client = client_factory(name="Test Client")
        project1 = project_factory(name="Garden Renovation", client=client)
        project2 = project_factory(name="Landscape Design", client=client)
        project3 = project_factory(name="Pool Installation", client=client)

        # Search by project name
        result = ProjectService.get_all_projects(search="Garden")
        assert len(result["projects"]) == 1
        assert result["projects"][0]["name"] == "Garden Renovation"

        # Search by client name
        result = ProjectService.get_all_projects(search="Test Client")
        assert len(result["projects"]) == 3

    def test_get_all_projects_with_status_filter(
        self, app_context, project_factory, client_factory
    ):
        """Test getting projects with status filter"""
        client = client_factory()
        project1 = project_factory(status="active", client=client)
        project2 = project_factory(status="completed", client=client)
        project3 = project_factory(status="active", client=client)

        result = ProjectService.get_all_projects(status="active")
        assert len(result["projects"]) == 2
        assert all(project["status"] == "active" for project in result["projects"])

    def test_get_all_projects_with_client_filter(
        self, app_context, project_factory, client_factory
    ):
        """Test getting projects with client filter"""
        client1 = client_factory(name="Client 1")
        client2 = client_factory(name="Client 2")
        project1 = project_factory(client=client1)
        project2 = project_factory(client=client1)
        project3 = project_factory(client=client2)

        result = ProjectService.get_all_projects(client_id=client1.id)
        assert len(result["projects"]) == 2
        assert all(project["client_id"] == client1.id for project in result["projects"])

    def test_get_project_by_id_success(self, app_context, sample_project):
        """Test getting project by ID successfully"""
        project = ProjectService.get_project_by_id(sample_project.id)
        assert project is not None
        assert project.id == sample_project.id
        assert project.name == sample_project.name

    def test_get_project_by_id_not_found(self, app_context):
        """Test getting project by non-existent ID"""
        project = ProjectService.get_project_by_id(999)
        assert project is None

    def test_create_project_success(self, app_context, sample_client):
        """Test creating a project successfully"""
        project_data = {
            "name": "Test Project",
            "description": "A test project description",
            "location": "123 Test Street",
            "area_size": 500.0,
            "budget": 10000.0,
            "status": "planning",
            "client_id": sample_client.id,
        }

        project = ProjectService.create_project(project_data)

        assert project.id is not None
        assert project.name == "Test Project"
        assert project.description == "A test project description"
        assert project.budget == 10000.0
        assert project.client_id == sample_client.id

        # Verify it's in the database
        self.assert_record_count(Project, 1)

    def test_create_project_minimal_data(self, app_context, sample_client):
        """Test creating project with minimal required data"""
        project_data = {"name": "Minimal Project", "client_id": sample_client.id}

        project = ProjectService.create_project(project_data)

        assert project.id is not None
        assert project.name == "Minimal Project"
        assert project.client_id == sample_client.id

    def test_update_project_success(self, app_context, sample_project):
        """Test updating a project successfully"""
        update_data = {
            "name": "Updated Project Name",
            "budget": 15000.0,
            "status": "active",
        }

        updated_project = ProjectService.update_project(sample_project.id, update_data)

        assert updated_project is not None
        assert updated_project.name == "Updated Project Name"
        assert updated_project.budget == 15000.0
        assert updated_project.status == "active"
        assert updated_project.id == sample_project.id

    def test_update_project_not_found(self, app_context):
        """Test updating non-existent project"""
        update_data = {"name": "Updated Name"}
        result = ProjectService.update_project(999, update_data)
        assert result is None

    def test_delete_project_success(self, app_context, sample_project):
        """Test deleting a project successfully"""
        project_id = sample_project.id

        result = ProjectService.delete_project(project_id)

        assert result is True
        self.assert_record_count(Project, 0)

        # Verify project is gone
        deleted_project = Project.query.get(project_id)
        assert deleted_project is None

    def test_delete_project_not_found(self, app_context):
        """Test deleting non-existent project"""
        result = ProjectService.delete_project(999)
        assert result is False

    def test_get_projects_by_client(self, app_context, project_factory, client_factory):
        """Test getting projects by client"""
        client1 = client_factory()
        client2 = client_factory()

        project1 = project_factory(client=client1)
        project2 = project_factory(client=client1)
        project3 = project_factory(client=client2)

        client1_projects = ProjectService.get_projects_by_client(client1.id)
        assert len(client1_projects) == 2
        assert all(project.client_id == client1.id for project in client1_projects)

    def test_get_projects_by_status(self, app_context, project_factory, client_factory):
        """Test getting projects by status"""
        client = client_factory()
        project1 = project_factory(status="active", client=client)
        project2 = project_factory(status="completed", client=client)
        project3 = project_factory(status="active", client=client)

        active_projects = ProjectService.get_projects_by_status("active")
        assert len(active_projects) == 2
        assert all(project.status == "active" for project in active_projects)

    def test_add_plant_to_project_success(
        self, app_context, sample_project, sample_plant
    ):
        """Test adding a plant to a project successfully"""
        result = ProjectService.add_plant_to_project(
            sample_project.id, sample_plant.id, quantity=5, unit_cost=25.99
        )

        assert result is True

        # Verify the relationship was created
        project_plant = ProjectPlant.query.filter_by(
            project_id=sample_project.id, plant_id=sample_plant.id
        ).first()

        assert project_plant is not None
        assert project_plant.quantity == 5
        assert project_plant.unit_cost == 25.99

    def test_add_plant_to_project_existing_plant(
        self, app_context, sample_project, sample_plant
    ):
        """Test adding a plant that already exists in project (should increase quantity)"""
        # Add plant first time
        ProjectService.add_plant_to_project(
            sample_project.id, sample_plant.id, quantity=3
        )

        # Add same plant again
        result = ProjectService.add_plant_to_project(
            sample_project.id, sample_plant.id, quantity=2
        )

        assert result is True

        # Should have combined quantity
        project_plant = ProjectPlant.query.filter_by(
            project_id=sample_project.id, plant_id=sample_plant.id
        ).first()

        assert project_plant.quantity == 5

    def test_add_plant_to_project_invalid_project(self, app_context, sample_plant):
        """Test adding plant to non-existent project"""
        result = ProjectService.add_plant_to_project(999, sample_plant.id, quantity=1)
        assert result is False

    def test_add_plant_to_project_invalid_plant(self, app_context, sample_project):
        """Test adding non-existent plant to project"""
        result = ProjectService.add_plant_to_project(sample_project.id, 999, quantity=1)
        assert result is False

    def test_remove_plant_from_project_success(
        self, app_context, sample_project, sample_plant
    ):
        """Test removing a plant from project successfully"""
        # First add the plant
        ProjectService.add_plant_to_project(
            sample_project.id, sample_plant.id, quantity=5
        )

        # Then remove it
        result = ProjectService.remove_plant_from_project(
            sample_project.id, sample_plant.id
        )

        assert result is True

        # Verify it's gone
        project_plant = ProjectPlant.query.filter_by(
            project_id=sample_project.id, plant_id=sample_plant.id
        ).first()

        assert project_plant is None

    def test_remove_plant_from_project_not_found(
        self, app_context, sample_project, sample_plant
    ):
        """Test removing plant that's not in project"""
        result = ProjectService.remove_plant_from_project(
            sample_project.id, sample_plant.id
        )
        assert result is False

    def test_get_project_plants(self, app_context, sample_project, plant_factory):
        """Test getting plants associated with a project"""
        plant1 = plant_factory(name="Plant 1", price=10.0)
        plant2 = plant_factory(name="Plant 2", price=20.0)

        # Add plants to project
        ProjectService.add_plant_to_project(
            sample_project.id, plant1.id, quantity=5, unit_cost=12.0
        )
        ProjectService.add_plant_to_project(
            sample_project.id, plant2.id, quantity=3, unit_cost=25.0
        )

        project_plants = ProjectService.get_project_plants(sample_project.id)

        assert len(project_plants) == 2

        # Check first plant data
        plant1_data = next(p for p in project_plants if p["name"] == "Plant 1")
        assert plant1_data["quantity"] == 5
        assert plant1_data["unit_cost"] == 12.0
        assert plant1_data["total_price"] == 60.0

    def test_calculate_project_cost(self, app_context, sample_project, plant_factory):
        """Test calculating total cost for a project"""
        plant1 = plant_factory(name="Plant 1")
        plant2 = plant_factory(name="Plant 2")

        # Add plants with different quantities and prices
        ProjectService.add_plant_to_project(
            sample_project.id, plant1.id, quantity=5, unit_cost=10.0
        )
        ProjectService.add_plant_to_project(
            sample_project.id, plant2.id, quantity=3, unit_cost=20.0
        )

        cost_analysis = ProjectService.calculate_project_cost(sample_project.id)

        assert cost_analysis["total_cost"] == 110.0  # (5*10) + (3*20)
        assert cost_analysis["plant_count"] == 2
        assert len(cost_analysis["plant_costs"]) == 2

        # Check individual plant costs
        plant1_cost = next(
            p for p in cost_analysis["plant_costs"] if p["plant_name"] == "Plant 1"
        )
        assert plant1_cost["line_total"] == 50.0

    def test_update_project_status(self, app_context, sample_project):
        """Test updating project status"""
        original_status = sample_project.status

        updated_project = ProjectService.update_project_status(
            sample_project.id, "completed"
        )

        assert updated_project is not None
        assert updated_project.status == "completed"
        assert updated_project.actual_completion_date is not None

    def test_update_project_status_not_found(self, app_context):
        """Test updating status of non-existent project"""
        result = ProjectService.update_project_status(999, "completed")
        assert result is None

    def test_validate_project_data_success(self, app_context, sample_client):
        """Test validating correct project data"""
        valid_data = {
            "name": "Valid Project",
            "client_id": sample_client.id,
            "budget": 5000.0,
            "area_size": 100.0,
            "status": "planning",
        }

        errors = ProjectService.validate_project_data(valid_data)
        assert errors == []

    def test_validate_project_data_missing_required(self, app_context):
        """Test validating project data with missing required fields"""
        invalid_data = {}

        errors = ProjectService.validate_project_data(invalid_data)
        assert "name is required" in errors
        assert "client_id is required" in errors

    def test_validate_project_data_invalid_client(self, app_context):
        """Test validating project data with invalid client ID"""
        invalid_data = {"name": "Test Project", "client_id": 999}  # Non-existent client

        errors = ProjectService.validate_project_data(invalid_data)
        assert "Invalid client_id" in errors

    def test_validate_project_data_negative_numbers(self, app_context, sample_client):
        """Test validating project data with negative numbers"""
        invalid_data = {
            "name": "Test Project",
            "client_id": sample_client.id,
            "budget": -1000.0,
            "area_size": -50.0,
        }

        errors = ProjectService.validate_project_data(invalid_data)
        assert "budget must be non-negative" in errors
        assert "area_size must be non-negative" in errors

    def test_validate_project_data_invalid_status(self, app_context, sample_client):
        """Test validating project data with invalid status"""
        invalid_data = {
            "name": "Test Project",
            "client_id": sample_client.id,
            "status": "invalid_status",
        }

        errors = ProjectService.validate_project_data(invalid_data)
        assert any("status must be one of:" in error for error in errors)


@pytest.mark.integration
class TestProjectServiceIntegration(DatabaseTestMixin):
    """Integration tests for Project Service"""

    def test_full_project_lifecycle(self, app_context, client_factory, plant_factory):
        """Test complete project lifecycle from creation to deletion"""
        client = client_factory()
        plant = plant_factory(price=15.0)

        # Create project
        project_data = {
            "name": "Lifecycle Test Project",
            "description": "Test project for lifecycle testing",
            "client_id": client.id,
            "budget": 5000.0,
            "status": "planning",
        }

        project = ProjectService.create_project(project_data)
        assert project.id is not None

        # Add plants to project
        ProjectService.add_plant_to_project(
            project.id, plant.id, quantity=10, unit_cost=20.0
        )

        # Check project plants
        project_plants = ProjectService.get_project_plants(project.id)
        assert len(project_plants) == 1

        # Calculate cost
        cost_analysis = ProjectService.calculate_project_cost(project.id)
        assert cost_analysis["total_cost"] == 200.0

        # Update project status
        ProjectService.update_project_status(project.id, "active")
        updated_project = ProjectService.get_project_by_id(project.id)
        assert updated_project.status == "active"

        # Remove plant
        ProjectService.remove_plant_from_project(project.id, plant.id)
        project_plants = ProjectService.get_project_plants(project.id)
        assert len(project_plants) == 0

        # Delete project
        delete_result = ProjectService.delete_project(project.id)
        assert delete_result is True

        # Verify deletion
        deleted_project = ProjectService.get_project_by_id(project.id)
        assert deleted_project is None

    def test_complex_project_plant_management(
        self, app_context, project_factory, plant_factory, client_factory
    ):
        """Test complex project-plant relationship management"""
        client = client_factory()
        project = project_factory(client=client)

        # Create multiple plants
        plants = [
            plant_factory(name=f"Plant {i}", price=float(i * 10)) for i in range(1, 6)
        ]

        # Add plants with different quantities
        for i, plant in enumerate(plants, 1):
            ProjectService.add_plant_to_project(
                project.id, plant.id, quantity=i * 2, unit_cost=plant.price + 5.0
            )

        # Verify all plants added
        project_plants = ProjectService.get_project_plants(project.id)
        assert len(project_plants) == 5

        # Check cost calculation
        cost_analysis = ProjectService.calculate_project_cost(project.id)
        expected_total = sum((i * 2) * (i * 10 + 5.0) for i in range(1, 6))
        assert cost_analysis["total_cost"] == expected_total

        # Remove middle plant
        ProjectService.remove_plant_from_project(project.id, plants[2].id)
        project_plants = ProjectService.get_project_plants(project.id)
        assert len(project_plants) == 4

        # Verify cost updated
        new_cost_analysis = ProjectService.calculate_project_cost(project.id)
        assert new_cost_analysis["total_cost"] < cost_analysis["total_cost"]

    def test_project_search_and_filtering(
        self, app_context, project_factory, client_factory
    ):
        """Test complex search and filtering scenarios"""
        # Create clients
        client1 = client_factory(name="Alpha Corp")
        client2 = client_factory(name="Beta LLC")

        # Create projects
        project1 = project_factory(
            name="Garden Design Alpha",
            status="active",
            client=client1,
            description="Beautiful garden design",
        )
        project2 = project_factory(
            name="Landscape Beta",
            status="completed",
            client=client1,
            description="Complete landscape renovation",
        )
        project3 = project_factory(
            name="Pool Installation",
            status="active",
            client=client2,
            description="Swimming pool with landscaping",
        )

        # Test status filtering
        active_projects = ProjectService.get_all_projects(status="active")
        assert len(active_projects["projects"]) == 2

        # Test client filtering
        client1_projects = ProjectService.get_all_projects(client_id=client1.id)
        assert len(client1_projects["projects"]) == 2

        # Test search by project name
        garden_projects = ProjectService.get_all_projects(search="Garden")
        assert len(garden_projects["projects"]) == 1
        assert garden_projects["projects"][0]["name"] == "Garden Design Alpha"

        # Test search by client name
        alpha_projects = ProjectService.get_all_projects(search="Alpha")
        assert len(alpha_projects["projects"]) == 2

        # Test combined filters
        active_alpha_projects = ProjectService.get_all_projects(
            status="active", client_id=client1.id
        )
        assert len(active_alpha_projects["projects"]) == 1
        assert active_alpha_projects["projects"][0]["name"] == "Garden Design Alpha"
