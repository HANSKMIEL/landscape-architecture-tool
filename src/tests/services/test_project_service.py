import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.services import ProjectService


class TestProjectService:
    
    @pytest.fixture
    def project_service(self):
        return ProjectService()
    
    @pytest.fixture
    def sample_project_data(self):
        return {
            'name': 'Test Garden Project',
            'description': 'A beautiful garden redesign',
            'client_id': 1,
            'status': 'active',
            'start_date': '2024-01-15',
            'budget': 5000.00,
            'location': 'Amsterdam, Netherlands',
            'project_type': 'Garden Design',
            'area_size': 250.0
        }
    
    @pytest.fixture
    def mock_project(self):
        project = Mock()
        project.id = 1
        project.name = 'Test Garden Project'
        project.client_id = 1
        project.status = 'active'
        project.budget = 5000.00
        project.to_dict.return_value = {
            'id': 1,
            'name': 'Test Garden Project',
            'client_id': 1,
            'status': 'active',
            'budget': 5000.00
        }
        return project
    
    @pytest.fixture
    def mock_client(self):
        client = Mock()
        client.id = 1
        client.name = 'Test Client'
        return client
    
    def test_create_project_success(self, app_context, project_service, sample_project_data, mock_client):
        """Test successful project creation"""
        with patch('src.models.user.db.session') as mock_session:
            
            # Mock the project instance that would be created
            mock_project = Mock()
            mock_project.id = 1
            mock_project.to_dict.return_value = sample_project_data
            
            # Mock the model class on the service instance
            with patch.object(project_service, 'model_class') as mock_model_class:
                mock_model_class.return_value = mock_project
                mock_model_class.__name__ = 'Project'
                
                result = project_service.create(sample_project_data)
                
                mock_model_class.assert_called_once_with(**sample_project_data)
                mock_session.add.assert_called_once_with(mock_project)
                mock_session.commit.assert_called_once()
                assert result == sample_project_data
    
    def test_create_project_database_error(self, app_context, project_service, sample_project_data):
        """Test project creation with database error"""
        with patch('src.models.user.db.session') as mock_session:
            
            # Simulate database error (like foreign key constraint)
            mock_session.commit.side_effect = Exception("Database constraint error")
            
            # Mock the model class 
            with patch.object(project_service, 'model_class') as mock_model_class:
                mock_project = Mock()
                mock_model_class.return_value = mock_project
                mock_model_class.__name__ = 'Project'
                
                with pytest.raises(Exception):
                    project_service.create(sample_project_data)
                
                mock_session.rollback.assert_called_once()
    
    def test_get_project_by_id_success(self, app_context, project_service, mock_project):
        """Test retrieving project by ID"""
        with patch('src.models.landscape.Project.query') as mock_query:
            mock_query.get.return_value = mock_project
            
            result = project_service.get_by_id(1)
            
            assert result == mock_project.to_dict.return_value
            mock_query.get.assert_called_once_with(1)
    
    def test_get_project_not_found(self, app_context, project_service):
        """Test retrieving non-existent project"""
        with patch('src.models.landscape.Project.query') as mock_query:
            mock_query.get.return_value = None
            
            result = project_service.get_by_id(999)
            
            assert result is None
            mock_query.get.assert_called_once_with(999)
    
    def test_update_project_success(self, app_context, project_service, mock_project):
        """Test successful project update"""
        update_data = {'status': 'completed', 'budget': 6000.00}
        
        with patch('src.models.landscape.Project.query') as mock_query, \
             patch('src.models.user.db.session') as mock_session:
            
            mock_query.get.return_value = mock_project
            mock_project.to_dict.return_value = {**mock_project.to_dict.return_value, **update_data}
            
            result = project_service.update(1, update_data)
            
            # Verify attributes were set
            assert mock_project.status == 'completed'
            assert mock_project.budget == 6000.00
            mock_session.commit.assert_called_once()
            assert result is not None
    
    def test_update_project_not_found(self, app_context, project_service):
        """Test updating non-existent project"""
        with patch('src.models.landscape.Project.query') as mock_query:
            mock_query.get.return_value = None
            
            result = project_service.update(999, {'status': 'completed'})
            
            assert result is None
    
    def test_delete_project_success(self, app_context, project_service, mock_project):
        """Test successful project deletion"""
        with patch('src.models.landscape.Project.query') as mock_query, \
             patch('src.models.user.db.session') as mock_session:
            
            mock_query.get.return_value = mock_project
            
            result = project_service.delete(1)
            
            assert result is True
            mock_session.delete.assert_called_once_with(mock_project)
            mock_session.commit.assert_called_once()
    
    def test_delete_project_not_found(self, app_context, project_service):
        """Test deleting non-existent project"""
        with patch('src.models.landscape.Project.query') as mock_query:
            mock_query.get.return_value = None
            
            result = project_service.delete(999)
            
            assert result is False
    
    def test_get_all_projects_empty(self, app_context, project_service):
        """Test getting all projects when database is empty"""
        with patch('src.models.landscape.Project.query') as mock_query:
            mock_pagination = Mock()
            mock_pagination.items = []
            mock_pagination.total = 0
            mock_pagination.pages = 0
            mock_pagination.has_next = False
            mock_pagination.has_prev = False
            
            mock_query.order_by.return_value.paginate.return_value = mock_pagination
            
            result = project_service.get_all()
            
            assert result['projects'] == []
            assert result['total'] == 0
            assert result['current_page'] == 1
    
    def test_get_all_projects_with_data(self, app_context, project_service):
        """Test getting all projects with data"""
        mock_projects = [Mock() for _ in range(3)]
        for i, project in enumerate(mock_projects):
            project.to_dict.return_value = {'id': i+1, 'name': f'Project {i+1}'}
        
        with patch('src.models.landscape.Project.query') as mock_query:
            mock_pagination = Mock()
            mock_pagination.items = mock_projects
            mock_pagination.total = 3
            mock_pagination.pages = 1
            mock_pagination.has_next = False
            mock_pagination.has_prev = False
            
            mock_query.order_by.return_value.paginate.return_value = mock_pagination
            
            result = project_service.get_all()
            
            assert len(result['projects']) == 3
            assert result['total'] == 3
            assert result['current_page'] == 1
    
    def test_get_projects_by_client(self, app_context, project_service):
        """Test retrieving projects by client"""
        mock_projects = [Mock() for _ in range(2)]
        for i, project in enumerate(mock_projects):
            project.to_dict.return_value = {'id': i+1, 'name': f'Project {i+1}', 'client_id': 1}
        
        with patch('src.models.landscape.Project.query') as mock_query:
            mock_pagination = Mock()
            mock_pagination.items = mock_projects
            mock_pagination.total = 2
            mock_pagination.pages = 1
            mock_pagination.has_next = False
            mock_pagination.has_prev = False
            
            mock_filtered_query = Mock()
            mock_filtered_query.order_by.return_value.paginate.return_value = mock_pagination
            mock_query.filter.return_value = mock_filtered_query
            
            result = project_service.get_all(client_id=1)
            
            assert len(result['projects']) == 2
            mock_query.filter.assert_called_once()
    
    def test_get_all_projects_with_search(self, app_context, project_service):
        """Test getting projects with search functionality"""
        mock_projects = [Mock()]
        mock_projects[0].to_dict.return_value = {'id': 1, 'name': 'Garden Project'}
        
        with patch('src.models.landscape.Project.query') as mock_query:
            mock_pagination = Mock()
            mock_pagination.items = mock_projects
            mock_pagination.total = 1
            mock_pagination.pages = 1
            mock_pagination.has_next = False
            mock_pagination.has_prev = False
            
            mock_filtered_query = Mock()
            mock_filtered_query.order_by.return_value.paginate.return_value = mock_pagination
            mock_query.filter.return_value = mock_filtered_query
            
            result = project_service.get_all(search='Garden')
            
            assert len(result['projects']) == 1
            assert result['projects'][0]['name'] == 'Garden Project'
            mock_query.filter.assert_called_once()
    
    def test_get_all_projects_pagination(self, app_context, project_service):
        """Test paginated project retrieval"""
        mock_projects = [Mock() for _ in range(10)]
        for i, project in enumerate(mock_projects):
            project.to_dict.return_value = {'id': i+1, 'name': f'Project {i+1}'}
        
        with patch('src.models.landscape.Project.query') as mock_query:
            mock_pagination = Mock()
            mock_pagination.items = mock_projects
            mock_pagination.total = 25
            mock_pagination.pages = 3
            mock_pagination.has_next = True
            mock_pagination.has_prev = False
            
            mock_query.order_by.return_value.paginate.return_value = mock_pagination
            
            result = project_service.get_all(page=1, per_page=10)
            
            assert len(result['projects']) == 10
            assert result['total'] == 25
            assert result['pages'] == 3
            assert result['current_page'] == 1
            mock_query.order_by.return_value.paginate.assert_called_once_with(
                page=1, per_page=10, error_out=False
            )
    
    def test_combined_search_and_client_filter(self, app_context, project_service):
        """Test combining search and client filtering"""
        mock_projects = [Mock()]
        mock_projects[0].to_dict.return_value = {
            'id': 1, 
            'name': 'Garden Project',
            'client_id': 1
        }
        
        with patch('src.models.landscape.Project.query') as mock_query:
            mock_pagination = Mock()
            mock_pagination.items = mock_projects
            mock_pagination.total = 1
            mock_pagination.pages = 1
            mock_pagination.has_next = False
            mock_pagination.has_prev = False
            
            # Chain the filter calls
            mock_client_filtered = Mock()
            mock_search_filtered = Mock()
            mock_search_filtered.order_by.return_value.paginate.return_value = mock_pagination
            mock_client_filtered.filter.return_value = mock_search_filtered
            mock_query.filter.return_value = mock_client_filtered
            
            result = project_service.get_all(search='Garden', client_id=1)
            
            assert len(result['projects']) == 1
            # Should call filter twice - once for client_id, once for search
            assert mock_query.filter.call_count == 1
            assert mock_client_filtered.filter.call_count == 1
    
    def test_database_error_handling(self, app_context, project_service, sample_project_data):
        """Test database error handling"""
        with patch('src.models.user.db.session') as mock_session:
            
            mock_session.commit.side_effect = Exception("Database error")
            
            # Mock the model class 
            with patch.object(project_service, 'model_class') as mock_model_class:
                mock_project = Mock()
                mock_model_class.return_value = mock_project
                mock_model_class.__name__ = 'Project'
                
                with pytest.raises(Exception):
                    project_service.create(sample_project_data)
                
                mock_session.rollback.assert_called_once()
    
    def test_project_status_validation(self, app_context, project_service, mock_project):
        """Test project status update scenarios"""
        valid_statuses = ['Planning', 'In uitvoering', 'Afgerond', 'On Hold']
        
        with patch('src.models.landscape.Project.query') as mock_query, \
             patch('src.models.user.db.session') as mock_session:
            
            mock_query.get.return_value = mock_project
            
            for status in valid_statuses:
                result = project_service.update(1, {'status': status})
                assert mock_project.status == status
                assert result is not None
    
    def test_budget_calculations(self, app_context, project_service, mock_project):
        """Test budget-related operations"""
        budget_scenarios = [0.0, 1000.50, 50000.00, 100000.00]
        
        with patch('src.models.landscape.Project.query') as mock_query, \
             patch('src.models.user.db.session') as mock_session:
            
            mock_query.get.return_value = mock_project
            
            for budget in budget_scenarios:
                result = project_service.update(1, {'budget': budget})
                assert mock_project.budget == budget
                assert result is not None