import pytest
import json
from unittest.mock import patch, Mock
from src.main import create_app

class TestPlantRoutes:
    
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
        # Mock authentication headers
        return {
            'Authorization': 'Bearer mock_jwt_token',
            'Content-Type': 'application/json'
        }
    
    @pytest.fixture
    def sample_plant_data(self):
        return {
            'name': 'Test Rose',
            'scientific_name': 'Rosa testicus',
            'plant_type': 'shrub',
            'height_min': 50,
            'height_max': 150,
            'sun_requirements': 'full_sun',
            'soil_type': 'well_drained'
        }
    
    def test_get_plants_success(self, client):
        """Test GET /api/plants returns plant list"""
        mock_plants = [
            {'id': 1, 'name': 'Rose'},
            {'id': 2, 'name': 'Lavender'}
        ]
        
        with patch('src.services.PlantService.get_all') as mock_service:
            mock_service.return_value = {
                'plants': mock_plants,
                'total': 2,
                'page': 1,
                'per_page': 10
            }
            
            response = client.get('/api/plants')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
    
    def test_get_plants_with_search(self, client):
        """Test GET /api/plants with search parameter"""
        mock_plants = [
            {'id': 1, 'name': 'Rose'}
        ]
        
        with patch('src.services.PlantService.get_all') as mock_service:
            mock_service.return_value = {
                'plants': mock_plants,
                'total': 1,
                'page': 1,
                'per_page': 10
            }
            
            response = client.get('/api/plants?search=rose')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            mock_service.assert_called_once_with(search='rose')
    
    def test_create_plant_success(self, client, sample_plant_data):
        """Test POST /api/plants creates new plant"""
        mock_plant = {
            'id': 1,
            **sample_plant_data
        }
        
        with patch('src.services.PlantService.create') as mock_service:
            mock_service.return_value = mock_plant
            
            response = client.post(
                '/api/plants',
                data=json.dumps(sample_plant_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['name'] == sample_plant_data['name']
            assert data['id'] == 1
    
    def test_create_plant_validation_error(self, client):
        """Test POST /api/plants with invalid data"""
        invalid_data = {'name': ''}  # Missing required fields
        
        response = client.post(
            '/api/plants',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # Pydantic validation will return 400
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_plant_success(self, client):
        """Test PUT /api/plants/<id> updates plant"""
        update_data = {'name': 'Updated Rose'}
        mock_plant = {
            'id': 1,
            'name': 'Updated Rose'
        }
        
        with patch('src.services.PlantService.update') as mock_service:
            mock_service.return_value = mock_plant
            
            response = client.put(
                '/api/plants/1',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['name'] == 'Updated Rose'
    
    def test_update_plant_not_found(self, client):
        """Test PUT /api/plants/<id> with non-existent plant"""
        update_data = {'name': 'Updated Rose'}
        
        with patch('src.services.PlantService.update') as mock_service:
            mock_service.return_value = None
            
            response = client.put(
                '/api/plants/999',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
            assert 'not found' in data['error'].lower()
    
    def test_delete_plant_success(self, client):
        """Test DELETE /api/plants/<id> deletes plant"""
        with patch('src.services.PlantService.delete') as mock_service:
            mock_service.return_value = True
            
            response = client.delete('/api/plants/1')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert 'deleted' in data['message'].lower()
    
    def test_delete_plant_not_found(self, client):
        """Test DELETE /api/plants/<id> with non-existent plant"""
        with patch('src.services.PlantService.delete') as mock_service:
            mock_service.return_value = False
            
            response = client.delete('/api/plants/999')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
            assert 'not found' in data['error'].lower()
    
    def test_get_plants_pagination(self, client):
        """Test GET /api/plants with pagination parameters"""
        mock_result = {
            'plants': [{'id': i} for i in range(5)],
            'total': 25,
            'page': 2,
            'per_page': 5
        }
        
        with patch('src.services.PlantService.get_all') as mock_service:
            mock_service.return_value = {
                'plants': mock_result['plants'],
                'total': mock_result['total'],
                'pages': 5,
                'current_page': mock_result['page']
            }
            
            response = client.get('/api/plants?page=2&per_page=5')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
    
    def test_get_plants_error_handling(self, client):
        """Test GET /api/plants handles service errors"""
        with patch('src.services.PlantService.get_all') as mock_service:
            mock_service.side_effect = Exception('Database error')
            
            response = client.get('/api/plants')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data