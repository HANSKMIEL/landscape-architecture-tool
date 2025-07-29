"""
Test Client Service

Comprehensive tests for client service layer business logic.
"""

import pytest

from src.services.client_service import ClientService
from src.models.landscape import Client, Project
from src.models.user import db
from tests.fixtures.database import DatabaseTestMixin


@pytest.mark.service
class TestClientService(DatabaseTestMixin):
    """Test Client Service operations"""

    def test_get_all_clients_empty(self, app_context):
        """Test getting clients when database is empty"""
        result = ClientService.get_all_clients()
        
        assert result['clients'] == []
        assert result['total'] == 0
        assert result['pages'] == 0
        assert result['current_page'] == 1

    def test_get_all_clients_with_data(self, app_context, client_factory, project_factory):
        """Test getting clients with sample data including project counts"""
        client1 = client_factory(name="Client One")
        client2 = client_factory(name="Client Two")
        
        # Add projects to client1
        project_factory(client=client1, status="active")
        project_factory(client=client1, status="completed")
        
        result = ClientService.get_all_clients()
        
        assert len(result['clients']) == 2
        assert result['total'] == 2
        assert result['pages'] == 1
        
        # Check project counts are included
        client1_data = next(c for c in result['clients'] if c['name'] == "Client One")
        assert client1_data['project_count'] == 2
        assert client1_data['active_projects'] == 1

    def test_get_all_clients_with_search(self, app_context, client_factory):
        """Test getting clients with search filter"""
        client1 = client_factory(name="Alpha Corp", email="contact@alpha.com")
        client2 = client_factory(name="Beta LLC", email="info@beta.com")
        client3 = client_factory(name="Gamma Inc", phone="555-123-4567")
        
        # Search by name
        result = ClientService.get_all_clients(search="Alpha")
        assert len(result['clients']) == 1
        assert result['clients'][0]['name'] == "Alpha Corp"
        
        # Search by email
        result = ClientService.get_all_clients(search="beta.com")
        assert len(result['clients']) == 1
        assert result['clients'][0]['name'] == "Beta LLC"
        
        # Search by phone
        result = ClientService.get_all_clients(search="555-123")
        assert len(result['clients']) == 1
        assert result['clients'][0]['name'] == "Gamma Inc"

    def test_get_all_clients_pagination(self, app_context, client_factory):
        """Test clients pagination"""
        # Create 15 clients
        for i in range(15):
            client_factory(name=f"Client {i}")
        
        # Test first page
        result = ClientService.get_all_clients(page=1, per_page=10)
        assert len(result['clients']) == 10
        assert result['total'] == 15
        assert result['pages'] == 2
        assert result['current_page'] == 1
        
        # Test second page
        result = ClientService.get_all_clients(page=2, per_page=10)
        assert len(result['clients']) == 5
        assert result['current_page'] == 2

    def test_get_client_by_id_success(self, app_context, sample_client):
        """Test getting client by ID successfully"""
        client = ClientService.get_client_by_id(sample_client.id)
        assert client is not None
        assert client.id == sample_client.id
        assert client.name == sample_client.name

    def test_get_client_by_id_not_found(self, app_context):
        """Test getting client by non-existent ID"""
        client = ClientService.get_client_by_id(999)
        assert client is None

    def test_create_client_success(self, app_context):
        """Test creating a client successfully"""
        client_data = {
            'name': 'Test Client',
            'company': 'Test Company',
            'email': 'test@example.com',
            'phone': '555-123-4567',
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345'
        }
        
        client = ClientService.create_client(client_data)
        
        assert client.id is not None
        assert client.name == 'Test Client'
        assert client.company == 'Test Company'
        assert client.email == 'test@example.com'
        
        # Verify it's in the database
        self.assert_record_count(Client, 1)

    def test_create_client_minimal_data(self, app_context):
        """Test creating client with minimal required data"""
        client_data = {
            'name': 'Minimal Client'
        }
        
        client = ClientService.create_client(client_data)
        
        assert client.id is not None
        assert client.name == 'Minimal Client'

    def test_update_client_success(self, app_context, sample_client):
        """Test updating a client successfully"""
        update_data = {
            'name': 'Updated Client Name',
            'email': 'updated@example.com',
            'phone': '555-999-8888'
        }
        
        updated_client = ClientService.update_client(sample_client.id, update_data)
        
        assert updated_client is not None
        assert updated_client.name == 'Updated Client Name'
        assert updated_client.email == 'updated@example.com'
        assert updated_client.phone == '555-999-8888'
        assert updated_client.id == sample_client.id

    def test_update_client_not_found(self, app_context):
        """Test updating non-existent client"""
        update_data = {'name': 'Updated Name'}
        result = ClientService.update_client(999, update_data)
        assert result is None

    def test_delete_client_success(self, app_context, sample_client):
        """Test deleting a client successfully"""
        client_id = sample_client.id
        
        result = ClientService.delete_client(client_id)
        
        assert result is True
        self.assert_record_count(Client, 0)
        
        # Verify client is gone
        deleted_client = Client.query.get(client_id)
        assert deleted_client is None

    def test_delete_client_with_active_projects(self, app_context, sample_client, project_factory):
        """Test deleting client with active projects should fail"""
        # Add active project to client
        project_factory(client=sample_client, status="active")
        
        result = ClientService.delete_client(sample_client.id)
        
        assert result is False
        # Client should still exist
        self.assert_record_count(Client, 1)

    def test_delete_client_with_inactive_projects(self, app_context, sample_client, project_factory):
        """Test deleting client with only inactive projects should succeed"""
        # Add completed project to client
        project_factory(client=sample_client, status="completed")
        
        result = ClientService.delete_client(sample_client.id)
        
        assert result is True
        self.assert_record_count(Client, 0)

    def test_delete_client_not_found(self, app_context):
        """Test deleting non-existent client"""
        result = ClientService.delete_client(999)
        assert result is False

    def test_get_client_projects(self, app_context, sample_client, project_factory):
        """Test getting projects for a client"""
        project1 = project_factory(client=sample_client, name="Project 1")
        project2 = project_factory(client=sample_client, name="Project 2")
        other_client = project_factory().client
        project3 = project_factory(client=other_client, name="Project 3")
        
        client_projects = ClientService.get_client_projects(sample_client.id)
        
        assert len(client_projects) == 2
        project_names = [project.name for project in client_projects]
        assert "Project 1" in project_names
        assert "Project 2" in project_names
        assert "Project 3" not in project_names

    def test_get_client_statistics(self, app_context, sample_client, project_factory):
        """Test getting statistical information for a client"""
        # Create projects with different statuses and budgets
        project_factory(client=sample_client, status="active", budget=5000.0, area_size=100.0)
        project_factory(client=sample_client, status="completed", budget=8000.0, area_size=150.0)
        project_factory(client=sample_client, status="planning", budget=3000.0, area_size=75.0)
        
        stats = ClientService.get_client_statistics(sample_client.id)
        
        assert stats['client_id'] == sample_client.id
        assert stats['client_name'] == sample_client.name
        assert stats['total_projects'] == 3
        assert stats['active_projects'] == 1
        assert stats['completed_projects'] == 1
        assert stats['total_budget'] == 16000.0
        assert stats['total_area'] == 325.0
        assert stats['average_project_budget'] == 16000.0 / 3

    def test_get_client_statistics_no_projects(self, app_context, sample_client):
        """Test getting statistics for client with no projects"""
        stats = ClientService.get_client_statistics(sample_client.id)
        
        assert stats['total_projects'] == 0
        assert stats['average_project_budget'] == 0

    def test_get_client_statistics_not_found(self, app_context):
        """Test getting statistics for non-existent client"""
        stats = ClientService.get_client_statistics(999)
        assert stats == {}

    def test_search_clients(self, app_context, client_factory):
        """Test searching clients"""
        client1 = client_factory(name="Alpha Corp", email="alpha@test.com")
        client2 = client_factory(name="Beta LLC", company="Beta Solutions")
        client3 = client_factory(name="Gamma Inc", phone="555-GAMMA")
        
        # Search by name
        results = ClientService.search_clients("Alpha")
        assert len(results) == 1
        assert results[0].name == "Alpha Corp"
        
        # Search by email
        results = ClientService.search_clients("alpha@test")
        assert len(results) == 1
        assert results[0].name == "Alpha Corp"
        
        # Search by company
        results = ClientService.search_clients("Solutions")
        assert len(results) == 1
        assert results[0].name == "Beta LLC"

    def test_validate_client_data_success(self, app_context):
        """Test validating correct client data"""
        valid_data = {
            'name': 'Valid Client',
            'email': 'valid@example.com',
            'phone': '555-123-4567'
        }
        
        errors = ClientService.validate_client_data(valid_data)
        assert errors == []

    def test_validate_client_data_missing_required(self, app_context):
        """Test validating client data with missing required fields"""
        invalid_data = {}
        
        errors = ClientService.validate_client_data(invalid_data)
        assert 'name is required' in errors

    def test_validate_client_data_invalid_email(self, app_context):
        """Test validating client data with invalid email"""
        invalid_data = {
            'name': 'Test Client',
            'email': 'invalid-email-format'
        }
        
        errors = ClientService.validate_client_data(invalid_data)
        assert 'Invalid email format' in errors

    def test_validate_client_data_duplicate_email(self, app_context, sample_client):
        """Test validating client data with duplicate email"""
        invalid_data = {
            'name': 'New Client',
            'email': sample_client.email
        }
        
        errors = ClientService.validate_client_data(invalid_data)
        assert 'Email already exists' in errors

    def test_validate_client_data_invalid_phone(self, app_context):
        """Test validating client data with invalid phone number"""
        invalid_data = {
            'name': 'Test Client',
            'phone': 'not-a-phone-number'
        }
        
        errors = ClientService.validate_client_data(invalid_data)
        assert 'Invalid phone number format' in errors

    def test_get_clients_by_company(self, app_context, client_factory):
        """Test getting clients by company"""
        client1 = client_factory(company="ABC Corp")
        client2 = client_factory(company="ABC Corp")
        client3 = client_factory(company="XYZ Inc")
        
        abc_clients = ClientService.get_clients_by_company("ABC Corp")
        assert len(abc_clients) == 2
        assert all(client.company == "ABC Corp" for client in abc_clients)

    def test_get_top_clients_by_projects(self, app_context, client_factory, project_factory):
        """Test getting top clients by number of projects"""
        client1 = client_factory(name="Client 1")
        client2 = client_factory(name="Client 2")
        client3 = client_factory(name="Client 3")
        
        # Client 1: 3 projects, Client 2: 2 projects, Client 3: 1 project
        for _ in range(3):
            project_factory(client=client1)
        for _ in range(2):
            project_factory(client=client2)
        project_factory(client=client3)
        
        top_clients = ClientService.get_top_clients_by_projects(limit=2)
        
        assert len(top_clients) == 2
        assert top_clients[0]['client']['name'] == "Client 1"
        assert top_clients[0]['project_count'] == 3
        assert top_clients[1]['client']['name'] == "Client 2"
        assert top_clients[1]['project_count'] == 2

    def test_get_top_clients_by_budget(self, app_context, client_factory, project_factory):
        """Test getting top clients by total budget"""
        client1 = client_factory(name="Client 1")
        client2 = client_factory(name="Client 2")
        
        # Client 1: $15000 total, Client 2: $10000 total
        project_factory(client=client1, budget=10000.0)
        project_factory(client=client1, budget=5000.0)
        project_factory(client=client2, budget=10000.0)
        
        top_clients = ClientService.get_top_clients_by_budget(limit=2)
        
        assert len(top_clients) == 2
        assert top_clients[0]['client']['name'] == "Client 1"
        assert top_clients[0]['total_budget'] == 15000.0
        assert top_clients[1]['client']['name'] == "Client 2"
        assert top_clients[1]['total_budget'] == 10000.0


@pytest.mark.integration
class TestClientServiceIntegration(DatabaseTestMixin):
    """Integration tests for Client Service"""

    def test_full_client_lifecycle(self, app_context, project_factory):
        """Test complete client lifecycle from creation to deletion"""
        # Create client
        client_data = {
            'name': 'Lifecycle Test Client',
            'company': 'Test Company',
            'email': 'lifecycle@test.com',
            'phone': '555-LIFECYCLE',
            'address': '123 Lifecycle St'
        }
        
        client = ClientService.create_client(client_data)
        assert client.id is not None
        
        # Add projects to client
        project1 = project_factory(client=client, status="completed", budget=5000.0)
        project2 = project_factory(client=client, status="completed", budget=8000.0)
        
        # Get client statistics
        stats = ClientService.get_client_statistics(client.id)
        assert stats['total_projects'] == 2
        assert stats['total_budget'] == 13000.0
        
        # Search for client
        search_results = ClientService.search_clients("Lifecycle")
        assert len(search_results) == 1
        assert search_results[0].id == client.id
        
        # Update client
        update_data = {'email': 'updated@test.com', 'phone': '555-UPDATED'}
        updated_client = ClientService.update_client(client.id, update_data)
        assert updated_client.email == 'updated@test.com'
        
        # Delete client (should succeed since no active projects)
        delete_result = ClientService.delete_client(client.id)
        assert delete_result is True
        
        # Verify deletion
        deleted_client = ClientService.get_client_by_id(client.id)
        assert deleted_client is None

    def test_client_project_relationship_management(self, app_context, client_factory, project_factory):
        """Test complex client-project relationship scenarios"""
        client = client_factory(name="Relationship Test Client")
        
        # Create projects with different statuses
        active_project = project_factory(client=client, status="active", budget=10000.0)
        completed_project = project_factory(client=client, status="completed", budget=15000.0)
        planning_project = project_factory(client=client, status="planning", budget=5000.0)
        
        # Test client projects retrieval
        client_projects = ClientService.get_client_projects(client.id)
        assert len(client_projects) == 3
        
        # Test client statistics
        stats = ClientService.get_client_statistics(client.id)
        assert stats['total_projects'] == 3
        assert stats['active_projects'] == 1
        assert stats['completed_projects'] == 1
        assert stats['total_budget'] == 30000.0
        
        # Test client filtering by project count
        top_clients = ClientService.get_top_clients_by_projects(limit=5)
        client_entry = next((c for c in top_clients if c['client']['id'] == client.id), None)
        assert client_entry is not None
        assert client_entry['project_count'] == 3
        
        # Try to delete client with active project (should fail)
        delete_result = ClientService.delete_client(client.id)
        assert delete_result is False
        
        # Update active project to completed
        active_project.status = "completed"
        db.session.commit()
        
        # Now deletion should succeed
        delete_result = ClientService.delete_client(client.id)
        assert delete_result is True

    def test_client_search_and_pagination_complex(self, app_context, client_factory):
        """Test complex search and pagination scenarios"""
        # Create diverse clients
        clients_data = [
            {'name': 'Alpha Construction', 'email': 'contact@alpha.com', 'company': 'Alpha Corp'},
            {'name': 'Beta Landscaping', 'email': 'info@beta.com', 'company': 'Beta LLC'},
            {'name': 'Gamma Design', 'email': 'hello@gamma.com', 'company': 'Gamma Inc'},
            {'name': 'Alpha Services', 'email': 'services@alpha.com', 'company': 'Alpha Corp'},
            {'name': 'Delta Solutions', 'email': 'contact@delta.com', 'company': 'Delta Co'},
        ]
        
        for data in clients_data:
            client_factory(**data)
        
        # Test search by company
        alpha_clients = ClientService.get_all_clients(search="Alpha Corp")
        assert len(alpha_clients['clients']) == 2
        
        # Test search by partial name
        alpha_names = ClientService.get_all_clients(search="Alpha")
        assert len(alpha_names['clients']) == 2
        
        # Test pagination with search
        all_clients = ClientService.get_all_clients(per_page=3)
        assert len(all_clients['clients']) == 3
        assert all_clients['total'] == 5
        assert all_clients['pages'] == 2
        
        # Test second page
        second_page = ClientService.get_all_clients(page=2, per_page=3)
        assert len(second_page['clients']) == 2
        assert second_page['current_page'] == 2