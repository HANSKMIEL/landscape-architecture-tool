import pytest
import json
from unittest.mock import patch, Mock
from src.main import create_app

class TestDashboardRoutes:
    
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
    
    def test_get_dashboard_stats_success(self, client):
        """Test GET /api/dashboard/stats returns dashboard statistics"""
        mock_stats = {
            'total_plants': 150,
            'total_projects': 12,
            'active_projects': 8,
            'total_clients': 25,
            'suppliers': 15,
            'products': 45,
            'completed_projects': 4,
            'total_budget': 50000.00,
            'last_updated': '2024-01-15T10:30:00'
        }
        
        with patch('src.services.DashboardService.get_stats') as mock_service:
            mock_service.return_value = mock_stats
            
            response = client.get('/api/dashboard/stats')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['total_plants'] == 150
            assert data['total_projects'] == 12
            assert data['active_projects'] == 8
            assert data['total_budget'] == 50000.00
    
    def test_get_dashboard_recent_activity_success(self, client):
        """Test GET /api/dashboard/recent-activity returns recent activity"""
        mock_activities = [
            {
                'id': 1,
                'type': 'project_update',
                'title': 'Project Garden Redesign updated',
                'description': 'Status changed to "In Progress"',
                'timestamp': '2024-01-15T10:30:00',
                'user': 'Hans Kmiel'
            },
            {
                'id': 2,
                'type': 'client_added',
                'title': 'New client added',
                'description': 'Villa Rozenhof registered',
                'timestamp': '2024-01-14T14:15:00',
                'user': 'Hans Kmiel'
            }
        ]
        
        with patch('src.services.DashboardService.get_recent_activity') as mock_service:
            mock_service.return_value = mock_activities
            
            response = client.get('/api/dashboard/recent-activity')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]['type'] == 'project_update'
            assert data[1]['type'] == 'client_added'
    
    def test_dashboard_stats_error_handling(self, client):
        """Test dashboard stats endpoint handles service errors"""
        with patch('src.services.DashboardService.get_stats') as mock_service:
            mock_service.side_effect = Exception('Database error')
            
            response = client.get('/api/dashboard/stats')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_dashboard_recent_activity_error_handling(self, client):
        """Test recent activity endpoint handles service errors"""
        with patch('src.services.DashboardService.get_recent_activity') as mock_service:
            mock_service.side_effect = Exception('Database error')
            
            response = client.get('/api/dashboard/recent-activity')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_dashboard_stats_empty_response(self, client):
        """Test dashboard stats with empty/zero values"""
        mock_stats = {
            'total_plants': 0,
            'total_projects': 0,
            'active_projects': 0,
            'total_clients': 0,
            'suppliers': 0,
            'products': 0,
            'completed_projects': 0,
            'total_budget': 0.00,
            'last_updated': '2024-01-15T10:30:00'
        }
        
        with patch('src.services.DashboardService.get_stats') as mock_service:
            mock_service.return_value = mock_stats
            
            response = client.get('/api/dashboard/stats')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['total_plants'] == 0
            assert data['total_budget'] == 0.00
    
    def test_dashboard_recent_activity_empty_list(self, client):
        """Test recent activity with empty activity list"""
        with patch('src.services.DashboardService.get_recent_activity') as mock_service:
            mock_service.return_value = []
            
            response = client.get('/api/dashboard/recent-activity')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 0