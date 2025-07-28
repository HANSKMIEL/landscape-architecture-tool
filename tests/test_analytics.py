import pytest
from src.main import create_app
from src.models.user import db
from src.models.landscape import Project, Plant, Client, Supplier, project_plants


class TestAnalyticsAPI:
    @pytest.fixture
    def app(self):
        """Create application for testing"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            # Create sample data for testing
            supplier = Supplier(name="Test Supplier", email="test@example.com")
            db.session.add(supplier)
            db.session.flush()
            
            client = Client(name="Test Client", email="client@example.com")
            db.session.add(client)
            db.session.flush()
            
            plant = Plant(
                name="Test Plant",
                common_name="Test Common",
                category="Test Category",
                supplier_id=supplier.id
            )
            db.session.add(plant)
            db.session.flush()
            
            project = Project(
                name="Test Project",
                client_id=client.id,
                budget=10000.0,
                status="Planning"
            )
            db.session.add(project)
            db.session.flush()
            
            # Add plant to project
            db.session.execute(
                project_plants.insert().values(
                    project_id=project.id,
                    plant_id=plant.id,
                    quantity=5
                )
            )
            
            db.session.commit()
            
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    def test_analytics_overview_endpoint(self, client):
        """Test analytics overview endpoint"""
        response = client.get('/api/analytics/overview')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'generated_at' in data
        assert 'plant_usage' in data
        assert 'project_performance' in data
        assert 'client_insights' in data
        assert 'financial_reporting' in data
        assert 'recommendation_effectiveness' in data

    def test_plant_usage_analytics_endpoint(self, client):
        """Test plant usage analytics endpoint"""
        response = client.get('/api/analytics/plant-usage')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'popular_plants' in data
        assert 'category_distribution' in data
        assert 'usage_trends' in data
        assert 'native_vs_non_native' in data

    def test_project_performance_analytics_endpoint(self, client):
        """Test project performance analytics endpoint"""
        response = client.get('/api/analytics/project-performance')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'status_distribution' in data
        assert 'budget_performance' in data
        assert 'type_distribution' in data
        assert 'creation_trends' in data

    def test_client_insights_endpoint(self, client):
        """Test client insights endpoint"""
        response = client.get('/api/analytics/client-insights')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'top_clients' in data
        assert 'client_type_distribution' in data
        assert 'acquisition_trends' in data
        assert 'retention_metrics' in data

    def test_financial_reporting_endpoint(self, client):
        """Test financial reporting endpoint"""
        response = client.get('/api/analytics/financial-reporting')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'financial_summary' in data
        assert 'monthly_revenue' in data
        assert 'revenue_by_type' in data
        assert 'budget_distribution' in data

    def test_recommendation_effectiveness_endpoint(self, client):
        """Test recommendation effectiveness endpoint"""
        response = client.get('/api/analytics/recommendation-effectiveness')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'total_requests' in data
        assert 'requests_with_feedback' in data
        assert 'avg_rating' in data