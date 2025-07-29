"""
Test Analytics Service

Comprehensive tests for analytics service layer business logic.
"""

import pytest
from datetime import datetime, timedelta

from src.services.analytics import AnalyticsService
from src.models.landscape import Plant, Project, ProjectPlant, Client, PlantRecommendationRequest
from src.models.user import db
from tests.fixtures.database import DatabaseTestMixin


@pytest.mark.service
class TestAnalyticsService(DatabaseTestMixin):
    """Test Analytics Service operations"""

    def test_get_plant_usage_analytics_empty(self, app_context):
        """Test getting plant usage analytics with empty database"""
        analytics = AnalyticsService()
        result = analytics.get_plant_usage_analytics()
        
        assert result['most_used_plants'] == []
        assert result['total_plants_used'] == 0
        assert result['total_projects_with_plants'] == 0

    def test_get_plant_usage_analytics_with_data(self, app_context, plant_factory, project_factory, client_factory):
        """Test getting plant usage analytics with sample data"""
        analytics = AnalyticsService()
        
        # Create test data
        client = client_factory()
        plants = [
            plant_factory(name="Rose Bush", category="Shrub"),
            plant_factory(name="Oak Tree", category="Tree"),
            plant_factory(name="Tulip", category="Perennial"),
        ]
        
        projects = [
            project_factory(client=client, name="Project 1"),
            project_factory(client=client, name="Project 2"),
            project_factory(client=client, name="Project 3"),
        ]
        
        # Create project-plant relationships with different usage patterns
        # Rose Bush: used in 2 projects, total quantity 25
        pp1 = ProjectPlant(project=projects[0], plant=plants[0], quantity=15)
        pp2 = ProjectPlant(project=projects[1], plant=plants[0], quantity=10)
        
        # Oak Tree: used in 1 project, total quantity 5
        pp3 = ProjectPlant(project=projects[0], plant=plants[1], quantity=5)
        
        # Tulip: used in 3 projects, total quantity 50
        pp4 = ProjectPlant(project=projects[0], plant=plants[2], quantity=20)
        pp5 = ProjectPlant(project=projects[1], plant=plants[2], quantity=15)
        pp6 = ProjectPlant(project=projects[2], plant=plants[2], quantity=15)
        
        # Add to database
        from src.models.user import db
        db.session.add_all([pp1, pp2, pp3, pp4, pp5, pp6])
        db.session.commit()
        
        result = analytics.get_plant_usage_analytics()
        
        # Most used plants should be sorted by total quantity
        most_used = result['most_used_plants']
        assert len(most_used) == 3
        
        # Tulip should be first (highest total quantity: 50)
        assert most_used[0]['name'] == "Tulip"
        assert most_used[0]['total_quantity'] == 50
        assert most_used[0]['project_count'] == 3
        
        # Rose Bush should be second (total quantity: 25)
        assert most_used[1]['name'] == "Rose Bush"
        assert most_used[1]['total_quantity'] == 25
        assert most_used[1]['project_count'] == 2

    def test_get_plant_usage_analytics_with_date_range(self, app_context, plant_factory, project_factory, client_factory):
        """Test getting plant usage analytics with date range filter"""
        analytics = AnalyticsService()
        
        client = client_factory()
        plant = plant_factory(name="Test Plant")
        
        # Create projects at different dates
        now = datetime.utcnow()
        old_project = project_factory(
            client=client,
            created_at=now - timedelta(days=60)
        )
        recent_project = project_factory(
            client=client,
            created_at=now - timedelta(days=10)
        )
        
        # Add plant to both projects
        old_project_plant = ProjectPlant(project=old_project, plant=plant, quantity=10)
        recent_project_plant = ProjectPlant(project=recent_project, plant=plant, quantity=5)
        db.session.add(old_project_plant)
        db.session.add(recent_project_plant)
        db.session.commit()
        
        # Test with 30-day range (should only include recent project)
        start_date = (now - timedelta(days=30)).isoformat()
        end_date = now.isoformat()
        
        result = analytics.get_plant_usage_analytics(date_range=(start_date, end_date))
        
        # Should only include the recent project's data
        assert len(result['most_used_plants']) == 1
        assert result['most_used_plants'][0]['total_quantity'] == 5
        assert result['most_used_plants'][0]['project_count'] == 1

    def test_get_project_performance_analytics_empty(self, app_context):
        """Test getting project performance analytics with empty database"""
        analytics = AnalyticsService()
        result = analytics.get_project_performance_analytics()
        
        assert result['total_projects'] == 0
        assert result['completion_rate'] == 0
        assert result['average_duration'] == 0
        assert result['projects_by_status'] == {}

    def test_get_project_performance_analytics_with_data(self, app_context, project_factory, client_factory):
        """Test getting project performance analytics with sample data"""
        analytics = AnalyticsService()
        
        client = client_factory()
        now = datetime.utcnow()
        
        # Create projects with different statuses and durations
        projects = [
            project_factory(
                client=client,
                status="completed",
                start_date=now - timedelta(days=30),
                actual_completion_date=now - timedelta(days=10),
                budget=5000.0
            ),
            project_factory(
                client=client,
                status="completed",
                start_date=now - timedelta(days=40),
                actual_completion_date=now - timedelta(days=20),
                budget=8000.0
            ),
            project_factory(
                client=client,
                status="active",
                start_date=now - timedelta(days=15),
                budget=6000.0
            ),
            project_factory(
                client=client,
                status="planning",
                budget=3000.0
            ),
        ]
        
        result = analytics.get_project_performance_analytics()
        
        assert result['total_projects'] == 4
        assert result['completion_rate'] == 50.0  # 2 out of 4 completed
        
        # Average duration: (20 + 20) / 2 = 20 days
        assert result['average_duration'] == 20.0
        
        # Check projects by status
        assert result['projects_by_status']['completed'] == 2
        assert result['projects_by_status']['active'] == 1
        assert result['projects_by_status']['planning'] == 1
        
        # Check budget analytics
        assert result['total_budget'] == 22000.0
        assert result['average_budget'] == 5500.0

    def test_get_client_analytics_empty(self, app_context):
        """Test getting client analytics with empty database"""
        analytics = AnalyticsService()
        result = analytics.get_client_analytics()
        
        assert result['total_clients'] == 0
        assert result['top_clients_by_projects'] == []
        assert result['top_clients_by_budget'] == []
        assert result['client_distribution'] == {}

    def test_get_client_analytics_with_data(self, app_context, client_factory, project_factory):
        """Test getting client analytics with sample data"""
        analytics = AnalyticsService()
        
        # Create clients with different project counts and budgets
        clients = [
            client_factory(name="Alpha Corp"),
            client_factory(name="Beta LLC"),
            client_factory(name="Gamma Inc"),
        ]
        
        # Alpha Corp: 3 projects, $18,000 total budget
        for i in range(3):
            project_factory(client=clients[0], budget=6000.0)
        
        # Beta LLC: 2 projects, $25,000 total budget
        project_factory(client=clients[1], budget=15000.0)
        project_factory(client=clients[1], budget=10000.0)
        
        # Gamma Inc: 1 project, $5,000 total budget
        project_factory(client=clients[2], budget=5000.0)
        
        result = analytics.get_client_analytics()
        
        assert result['total_clients'] == 3
        
        # Top clients by project count
        top_by_projects = result['top_clients_by_projects']
        assert len(top_by_projects) == 3
        assert top_by_projects[0]['client_name'] == "Alpha Corp"
        assert top_by_projects[0]['project_count'] == 3
        
        # Top clients by budget
        top_by_budget = result['top_clients_by_budget']
        assert len(top_by_budget) == 3
        assert top_by_budget[0]['client_name'] == "Beta LLC"
        assert top_by_budget[0]['total_budget'] == 25000.0

    def test_get_recommendation_analytics_empty(self, app_context):
        """Test getting recommendation analytics with empty database"""
        analytics = AnalyticsService()
        result = analytics.get_recommendation_analytics()
        
        assert result['total_requests'] == 0
        assert result['feedback_rate'] == 0
        assert result['average_satisfaction'] == 0
        assert result['popular_criteria'] == []

    def test_get_recommendation_analytics_with_data(self, app_context, client_factory):
        """Test getting recommendation analytics with sample data"""
        analytics = AnalyticsService()
        
        client = client_factory()
        now = datetime.utcnow()
        
        # Create recommendation requests with different feedback
        requests = []
        for i in range(5):
            request = PlantRecommendationRequest(
                client_id=client.id,
                criteria={
                    'hardiness_zone': '5a',
                    'sun_exposure': 'full_sun',
                    'plant_type': 'tree'
                },
                results=[],
                feedback_rating=4 if i < 3 else None,  # 3 out of 5 have feedback
                created_at=now - timedelta(days=i)
            )
            db.session.add(request)
            requests.append(request)
        
        db.session.commit()
        
        result = analytics.get_recommendation_analytics()
        
        assert result['total_requests'] == 5
        assert result['feedback_rate'] == 60.0  # 3 out of 5
        assert result['average_satisfaction'] == 4.0  # Average of the 3 ratings

    def test_get_seasonal_analytics_empty(self, app_context):
        """Test getting seasonal analytics with empty database"""
        analytics = AnalyticsService()
        result = analytics.get_seasonal_analytics()
        
        assert result['projects_by_month'] == []
        assert result['plant_usage_by_season'] == {}
        assert result['peak_seasons'] == []

    def test_get_seasonal_analytics_with_data(self, app_context, plant_factory, project_factory, client_factory):
        """Test getting seasonal analytics with sample data"""
        analytics = AnalyticsService()
        
        client = client_factory()
        
        # Create plants with different bloom seasons
        spring_plant = plant_factory(name="Spring Flower", bloom_time="spring")
        summer_plant = plant_factory(name="Summer Flower", bloom_time="summer")
        fall_plant = plant_factory(name="Fall Flower", bloom_time="fall")
        
        # Create projects in different months
        now = datetime.utcnow()
        spring_project = project_factory(
            client=client,
            created_at=datetime(now.year, 3, 15)  # March
        )
        summer_project = project_factory(
            client=client,
            created_at=datetime(now.year, 7, 15)  # July
        )
        
        # Add seasonal plants to projects
        db.session.add(ProjectPlant(project=spring_project, plant=spring_plant, quantity=10))
        db.session.add(ProjectPlant(project=summer_project, plant=summer_plant, quantity=15))
        db.session.add(ProjectPlant(project=summer_project, plant=fall_plant, quantity=5))
        db.session.commit()
        
        result = analytics.get_seasonal_analytics()
        
        # Check projects by month
        projects_by_month = {item['month']: item['count'] for item in result['projects_by_month']}
        assert projects_by_month.get('March', 0) == 1
        assert projects_by_month.get('July', 0) == 1
        
        # Check plant usage by season
        season_usage = result['plant_usage_by_season']
        assert season_usage.get('spring', 0) == 10
        assert season_usage.get('summer', 0) == 15
        assert season_usage.get('fall', 0) == 5

    def test_get_geographic_analytics_empty(self, app_context):
        """Test getting geographic analytics with empty database"""
        analytics = AnalyticsService()
        result = analytics.get_geographic_analytics()
        
        assert result['projects_by_location'] == []
        assert result['regional_plant_preferences'] == {}
        assert result['coverage_areas'] == []

    def test_get_geographic_analytics_with_data(self, app_context, project_factory, client_factory, plant_factory):
        """Test getting geographic analytics with sample data"""
        analytics = AnalyticsService()
        
        client = client_factory()
        
        # Create projects in different locations
        projects = [
            project_factory(client=client, location="Springfield, IL"),
            project_factory(client=client, location="Springfield, MA"),
            project_factory(client=client, location="Chicago, IL"),
        ]
        
        # Create plants
        oak_tree = plant_factory(name="Oak Tree")
        maple_tree = plant_factory(name="Maple Tree")
        
        # Add plants to projects
        ProjectPlant(project=projects[0], plant=oak_tree, quantity=5)
        ProjectPlant(project=projects[1], plant=maple_tree, quantity=3)
        ProjectPlant(project=projects[2], plant=oak_tree, quantity=8)
        
        result = analytics.get_geographic_analytics()
        
        # Check projects by location
        locations = [item['location'] for item in result['projects_by_location']]
        assert "Springfield, IL" in locations
        assert "Springfield, MA" in locations
        assert "Chicago, IL" in locations


@pytest.mark.integration
class TestAnalyticsServiceIntegration(DatabaseTestMixin):
    """Integration tests for Analytics Service"""

    def test_comprehensive_analytics_workflow(self, app_context, client_factory, project_factory, plant_factory):
        """Test comprehensive analytics workflow with realistic data"""
        analytics = AnalyticsService()
        
        # Create a realistic dataset spanning multiple months
        clients = [client_factory(name=f"Client {i}") for i in range(3)]
        
        # Create plants with diverse characteristics
        plants = [
            plant_factory(name="Red Oak", category="Tree", bloom_time="spring", native=True),
            plant_factory(name="Rose Bush", category="Shrub", bloom_time="summer", native=False),
            plant_factory(name="Tulip", category="Perennial", bloom_time="spring", native=False),
            plant_factory(name="Maple Tree", category="Tree", bloom_time="fall", native=True),
        ]
        
        # Create projects across different time periods
        now = datetime.utcnow()
        projects = []
        for i in range(6):
            project = project_factory(
                client=clients[i % 3],
                status="completed" if i < 4 else "active",
                created_at=now - timedelta(days=30*i),
                start_date=now - timedelta(days=30*i+5) if i < 4 else now - timedelta(days=15),
                actual_completion_date=now - timedelta(days=30*i-20) if i < 4 else None,
                budget=5000.0 + i*1000,
                location=f"City {i % 2}"
            )
            projects.append(project)
        
        # Create diverse project-plant relationships
        relationships = [
            (projects[0], plants[0], 10),  # Red Oak in project 0
            (projects[0], plants[1], 5),   # Rose Bush in project 0
            (projects[1], plants[0], 8),   # Red Oak in project 1
            (projects[1], plants[2], 15),  # Tulip in project 1
            (projects[2], plants[2], 20),  # Tulip in project 2
            (projects[3], plants[3], 3),   # Maple Tree in project 3
            (projects[4], plants[0], 12),  # Red Oak in project 4
            (projects[5], plants[1], 8),   # Rose Bush in project 5
        ]
        
        for project, plant, quantity in relationships:
            ProjectPlant(project=project, plant=plant, quantity=quantity)
        
        # Test plant usage analytics
        plant_analytics = analytics.get_plant_usage_analytics()
        
        # Red Oak should be most used (total: 30)
        most_used = plant_analytics['most_used_plants']
        assert most_used[0]['name'] == "Red Oak"
        assert most_used[0]['total_quantity'] == 30
        assert most_used[0]['project_count'] == 3
        
        # Test project performance analytics
        project_analytics = analytics.get_project_performance_analytics()
        assert project_analytics['total_projects'] == 6
        assert project_analytics['completion_rate'] == 66.67  # 4 out of 6 completed
        
        # Test client analytics
        client_analytics = analytics.get_client_analytics()
        assert client_analytics['total_clients'] == 3
        
        # Each client should have 2 projects
        top_clients = client_analytics['top_clients_by_projects']
        assert all(client['project_count'] == 2 for client in top_clients)
        
        # Test seasonal analytics
        seasonal_analytics = analytics.get_seasonal_analytics()
        
        # Should have spring, summer, and fall plants
        season_usage = seasonal_analytics['plant_usage_by_season']
        assert season_usage.get('spring', 0) > 0  # Red Oak + Tulip
        assert season_usage.get('summer', 0) > 0  # Rose Bush
        assert season_usage.get('fall', 0) > 0    # Maple Tree
        
        # Test geographic analytics
        geo_analytics = analytics.get_geographic_analytics()
        
        # Should have projects in City 0 and City 1
        locations = [item['location'] for item in geo_analytics['projects_by_location']]
        assert "City 0" in locations
        assert "City 1" in locations

    def test_analytics_with_date_filtering(self, app_context, client_factory, project_factory, plant_factory):
        """Test analytics with various date range filters"""
        analytics = AnalyticsService()
        
        client = client_factory()
        plant = plant_factory()
        now = datetime.utcnow()
        
        # Create projects at specific dates
        old_project = project_factory(
            client=client,
            created_at=now - timedelta(days=100)
        )
        recent_project = project_factory(
            client=client,
            created_at=now - timedelta(days=10)
        )
        
        # Add plants to projects
        ProjectPlant(project=old_project, plant=plant, quantity=5)
        ProjectPlant(project=recent_project, plant=plant, quantity=10)
        
        # Test different date ranges
        
        # Last 30 days - should only include recent project
        start_30 = (now - timedelta(days=30)).isoformat()
        end_30 = now.isoformat()
        
        analytics_30 = analytics.get_plant_usage_analytics(date_range=(start_30, end_30))
        assert analytics_30['most_used_plants'][0]['total_quantity'] == 10
        
        # Last 120 days - should include both projects
        start_120 = (now - timedelta(days=120)).isoformat()
        end_120 = now.isoformat()
        
        analytics_120 = analytics.get_plant_usage_analytics(date_range=(start_120, end_120))
        assert analytics_120['most_used_plants'][0]['total_quantity'] == 15

    def test_analytics_performance_with_large_dataset(self, app_context, client_factory, project_factory, plant_factory):
        """Test analytics performance with larger dataset"""
        analytics = AnalyticsService()
        
        # Create larger dataset
        clients = [client_factory() for _ in range(10)]
        plants = [plant_factory() for _ in range(20)]
        projects = [project_factory(client=clients[i % 10]) for i in range(50)]
        
        # Create many project-plant relationships
        import random
        for project in projects:
            # Each project gets 1-5 random plants
            num_plants = random.randint(1, 5)
            selected_plants = random.sample(plants, num_plants)
            for plant in selected_plants:
                ProjectPlant(
                    project=project,
                    plant=plant,
                    quantity=random.randint(1, 20)
                )
        
        # Test that analytics still work efficiently
        plant_analytics = analytics.get_plant_usage_analytics()
        assert len(plant_analytics['most_used_plants']) > 0
        
        project_analytics = analytics.get_project_performance_analytics()
        assert project_analytics['total_projects'] == 50
        
        client_analytics = analytics.get_client_analytics()
        assert client_analytics['total_clients'] == 10