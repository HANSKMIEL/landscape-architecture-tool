import pytest
import json
from unittest.mock import patch, Mock
from datetime import datetime
from src.main import create_app

class TestProjectRoutes:
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['RATELIMIT_ENABLED'] = False
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self):
        return {
            'Authorization': 'Bearer mock_jwt_token',
            'Content-Type': 'application/json'
        }
    
    @pytest.fixture
    def sample_project_data(self):
        return {
            'name': 'Test Garden Project',
            'description': 'A beautiful garden redesign',
            'client_id': 1,
            'status': 'active',
            'budget': 5000.00
        }
    
    def test_get_projects_success(self, client):
        """Test GET /api/projects returns project list"""
        mock_projects = [
            {'id': 1, 'name': 'Garden Project'},
            {'id': 2, 'name': 'Park Design'}
        ]
        
        with patch('src.services.ProjectService.get_all') as mock_service:
            mock_service.return_value = {
                'projects': mock_projects,
                'total': 2,
                'pages': 1,
                'current_page': 1
            }
            
            response = client.get('/api/projects')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
    
    def test_get_projects_with_search(self, client):
        """Test GET /api/projects with search parameter"""
        mock_projects = [
            {'id': 1, 'name': 'Garden Project'}
        ]
        
        with patch('src.services.ProjectService.get_all') as mock_service:
            mock_service.return_value = {
                'projects': mock_projects,
                'total': 1,
                'pages': 1,
                'current_page': 1
            }
            
            response = client.get('/api/projects?search=garden')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            mock_service.assert_called_once_with(search='garden', client_id=None)
    
    def test_get_projects_with_client_filter(self, client):
        """Test GET /api/projects with client_id filter"""
        mock_projects = [
            {'id': 1, 'name': 'Garden Project', 'client_id': 1}
        ]
        
        with patch('src.services.ProjectService.get_all') as mock_service:
            mock_service.return_value = {
                'projects': mock_projects,
                'total': 1,
                'pages': 1,
                'current_page': 1
            }
            
            response = client.get('/api/projects?client_id=1')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            mock_service.assert_called_once_with(search='', client_id=1)
    
    def test_create_project_success(self, client, sample_project_data):
        """Test POST /api/projects creates new project"""
        mock_project = {
            'id': 1,
            **sample_project_data
        }
        
        with patch('src.services.ProjectService.create') as mock_service:
            mock_service.return_value = mock_project
            
            response = client.post(
                '/api/projects',
                data=json.dumps(sample_project_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['name'] == sample_project_data['name']
    
    def test_create_project_validation_error(self, client):
        """Test POST /api/projects with invalid data"""
        invalid_data = {'name': ''}  # Missing required fields
        
        response = client.post(
            '/api/projects',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # Pydantic validation will return 400 
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_project_success(self, client):
        """Test PUT /api/projects/<id> updates project"""
        update_data = {'name': 'Updated Project'}
        mock_project = {
            'id': 1,
            'name': 'Updated Project'
        }
        
        with patch('src.services.ProjectService.update') as mock_service:
            mock_service.return_value = mock_project
            
            response = client.put(
                '/api/projects/1',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['name'] == 'Updated Project'
    
    def test_update_project_not_found(self, client):
        """Test PUT /api/projects/<id> with non-existent project"""
        update_data = {'name': 'Updated Project'}
        
        with patch('src.services.ProjectService.update') as mock_service:
            mock_service.return_value = None
            
            response = client.put(
                '/api/projects/999',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
            assert 'not found' in data['error'].lower()
    
    def test_delete_project_success(self, client):
        """Test DELETE /api/projects/<id> deletes project"""
        with patch('src.services.ProjectService.delete') as mock_service:
            mock_service.return_value = True
            
            response = client.delete('/api/projects/1')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert 'deleted' in data['message'].lower()
    
    def test_delete_project_not_found(self, client):
        """Test DELETE /api/projects/<id> with non-existent project"""
        with patch('src.services.ProjectService.delete') as mock_service:
            mock_service.return_value = False
            
            response = client.delete('/api/projects/999')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
            assert 'not found' in data['error'].lower()
    
    def test_get_projects_error_handling(self, client):
        """Test GET /api/projects handles service errors"""
        with patch('src.services.ProjectService.get_all') as mock_service:
            mock_service.side_effect = Exception('Database error')
            
            response = client.get('/api/projects')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_create_project_error_handling(self, client, sample_project_data):
        """Test POST /api/projects handles service errors"""
        with patch('src.services.ProjectService.create') as mock_service:
            mock_service.side_effect = Exception('Database error')
            
            response = client.post(
                '/api/projects',
                data=json.dumps(sample_project_data),
                content_type='application/json'
            )
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data