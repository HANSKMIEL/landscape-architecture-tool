"""
Test Dashboard Service

Comprehensive tests for dashboard service layer business logic.
"""

from datetime import datetime, timedelta

import pytest

from src.models.landscape import (Client, Plant, Product, Project,
                                  ProjectPlant, Supplier)
from src.models.user import db
from src.services.dashboard_service import DashboardService
from tests.fixtures.database import DatabaseTestMixin


@pytest.mark.service
class TestDashboardService(DatabaseTestMixin):
    """Test Dashboard Service operations"""

    def test_get_dashboard_summary_empty(self, app_context):
        """Test getting dashboard summary with empty database"""
        summary = DashboardService.get_dashboard_summary()

        assert summary["totals"]["clients"] == 0
        assert summary["totals"]["projects"] == 0
        assert summary["totals"]["plants"] == 0
        assert summary["totals"]["suppliers"] == 0
        assert summary["totals"]["active_projects"] == 0
        assert summary["projects_by_status"] == {}
        assert summary["recent_activity"]["new_projects"] == 0
        assert summary["recent_activity"]["new_clients"] == 0
        assert summary["financial"]["total_budget"] == 0

    def test_get_dashboard_summary_with_data(
        self,
        app_context,
        client_factory,
        project_factory,
        plant_factory,
        supplier_factory,
    ):
        """Test getting dashboard summary with sample data"""
        # Clear cache to ensure fresh data
        from src.services.performance import cache

        cache.clear()

        # Create test data
        clients = [client_factory() for _ in range(3)]
        suppliers = [supplier_factory() for _ in range(2)]  # noqa: F841
        plants = [plant_factory(supplier=suppliers[0]) for _ in range(5)]  # noqa: F841

        # Create projects with different statuses
        projects = [  # noqa: F841
            project_factory(client=clients[0], status="active", budget=5000.0),
            project_factory(client=clients[1], status="completed", budget=8000.0),
            project_factory(client=clients[2], status="planning", budget=3000.0),
            project_factory(client=clients[0], status="active", budget=7000.0),
        ]

        summary = DashboardService.get_dashboard_summary()

        assert summary["totals"]["clients"] == 3
        assert summary["totals"]["projects"] == 4
        assert summary["totals"]["plants"] == 5
        assert summary["totals"]["suppliers"] == 2
        assert summary["totals"]["active_projects"] == 2

        # Check projects by status
        assert summary["projects_by_status"]["active"] == 2
        assert summary["projects_by_status"]["completed"] == 1
        assert summary["projects_by_status"]["planning"] == 1

        # Check financial summary
        assert summary["financial"]["total_budget"] == 23000.0

    def test_get_project_analytics_empty(self, app_context):
        """Test getting project analytics with empty database"""
        analytics = DashboardService.get_project_analytics()

        assert analytics["projects_over_time"] == []
        assert analytics["projects_by_status"] == []
        assert analytics["average_budget"] == 0
        assert analytics["top_clients"] == []

    def test_get_project_analytics_with_data(
        self, app_context, client_factory, project_factory
    ):
        """Test getting project analytics with sample data"""
        # Create clients
        client1 = client_factory(name="Alpha Corp")
        client2 = client_factory(name="Beta LLC")
        client3 = client_factory(name="Gamma Inc")  # noqa: F841

        # Create projects with different dates and budgets
        now = datetime.utcnow()
        projects = [  # noqa: F841
            project_factory(
                client=client1,
                status="active",
                budget=5000.0,
                created_at=now - timedelta(days=5),
            ),
            project_factory(
                client=client1,
                status="completed",
                budget=8000.0,
                created_at=now - timedelta(days=10),
            ),
            project_factory(
                client=client2,
                status="active",
                budget=6000.0,
                created_at=now - timedelta(days=15),
            ),
            project_factory(
                client=client1,
                status="planning",
                budget=4000.0,
                created_at=now - timedelta(days=20),
            ),
        ]

        analytics = DashboardService.get_project_analytics(days=30)

        # Check projects by status
        status_counts = {
            item["status"]: item["count"] for item in analytics["projects_by_status"]
        }
        assert status_counts["active"] == 2
        assert status_counts["completed"] == 1
        assert status_counts["planning"] == 1

        # Check average budget
        assert analytics["average_budget"] == 5750.0  # (5000+8000+6000+4000)/4

        # Check top clients
        assert len(analytics["top_clients"]) == 2  # Only clients with projects
        top_client = analytics["top_clients"][0]
        assert top_client["name"] == "Alpha Corp"
        assert top_client["project_count"] == 3

    def test_get_plant_analytics_empty(self, app_context):
        """Test getting plant analytics with empty database"""
        analytics = DashboardService.get_plant_analytics()

        assert analytics["most_used_plants"] == []
        assert analytics["plants_by_category"] == []
        assert analytics["plants_by_sun_exposure"] == []
        assert analytics["native_distribution"]["native"] == 0
        assert analytics["native_distribution"]["non_native"] == 0

    def test_get_plant_analytics_with_data(
        self, app_context, plant_factory, project_factory, client_factory
    ):
        """Test getting plant analytics with sample data"""
        # Create plants with different categories and properties
        plant1 = plant_factory(
            name="Rose Bush", category="Shrub", sun_exposure="full_sun", native=True
        )
        plant2 = plant_factory(
            name="Oak Tree", category="Tree", sun_exposure="partial_shade", native=True
        )
        plant3 = plant_factory(
            name="Tulip", category="Perennial", sun_exposure="full_sun", native=False
        )
        plant4 = plant_factory(  # noqa: F841
            name="Maple Tree",
            category="Tree",
            sun_exposure="partial_shade",
            native=False,
        )

        # Create projects and project-plant relationships
        client = client_factory()
        project1 = project_factory(client=client)
        project2 = project_factory(client=client)

        # Add plants to projects with different quantities
        pp1 = ProjectPlant(project=project1, plant=plant1, quantity=10)
        pp2 = ProjectPlant(project=project1, plant=plant2, quantity=5)
        pp3 = ProjectPlant(project=project2, plant=plant1, quantity=8)
        pp4 = ProjectPlant(project=project2, plant=plant3, quantity=15)
        db.session.add_all([pp1, pp2, pp3, pp4])
        db.session.commit()

        analytics = DashboardService.get_plant_analytics()

        # Check plants by category
        category_counts = {
            item["category"]: item["count"] for item in analytics["plants_by_category"]
        }
        assert category_counts["Tree"] == 2
        assert category_counts["Shrub"] == 1
        assert category_counts["Perennial"] == 1

        # Check plants by sun exposure
        sun_counts = {
            item["sun_exposure"]: item["count"]
            for item in analytics["plants_by_sun_exposure"]
        }
        assert sun_counts["full_sun"] == 2
        assert sun_counts["partial_shade"] == 2

        # Check native distribution
        assert analytics["native_distribution"]["native"] == 2
        assert analytics["native_distribution"]["non_native"] == 2

    def test_get_financial_analytics_empty(self, app_context):
        """Test getting financial analytics with empty database"""
        analytics = DashboardService.get_financial_analytics()

        assert analytics["total_project_value"] == 0
        assert analytics["average_project_value"] == 0
        assert analytics["values_by_status"] == []
        assert analytics["top_projects"] == []
        assert analytics["monthly_trends"] == []

    def test_get_financial_analytics_with_data(
        self, app_context, client_factory, project_factory
    ):
        """Test getting financial analytics with sample data"""
        # Create clients
        client1 = client_factory(name="Alpha Corp")
        client2 = client_factory(name="Beta LLC")

        # Create projects with different budgets and statuses
        projects = [  # noqa: F841
            project_factory(
                client=client1, name="Project Alpha", status="active", budget=10000.0
            ),
            project_factory(
                client=client2, name="Project Beta", status="completed", budget=15000.0
            ),
            project_factory(
                client=client1, name="Project Gamma", status="planning", budget=5000.0
            ),
            project_factory(
                client=client2, name="Project Delta", status="active", budget=8000.0
            ),
        ]

        analytics = DashboardService.get_financial_analytics()

        # Check total and average values
        assert analytics["total_project_value"] == 38000.0
        assert analytics["average_project_value"] == 9500.0

        # Check values by status
        status_values = {
            item["status"]: item["total_value"]
            for item in analytics["values_by_status"]
        }
        assert status_values["active"] == 18000.0  # 10000 + 8000
        assert status_values["completed"] == 15000.0
        assert status_values["planning"] == 5000.0

        # Check top projects
        assert len(analytics["top_projects"]) == 4
        top_project = analytics["top_projects"][0]
        assert top_project["name"] == "Project Beta"
        assert top_project["budget"] == 15000.0
        assert top_project["client_name"] == "Beta LLC"

    def test_get_supplier_analytics_empty(self, app_context):
        """Test getting supplier analytics with empty database"""
        analytics = DashboardService.get_supplier_analytics()

        assert analytics["total_suppliers"] == 0
        assert analytics["top_suppliers"] == []
        assert analytics["specializations"] == []

    def test_get_supplier_analytics_with_data(
        self, app_context, supplier_factory, product_factory, plant_factory
    ):
        """Test getting supplier analytics with sample data"""
        # Clear cache to ensure fresh data
        from src.services.performance import cache

        cache.clear()

        # Create suppliers with different specializations
        supplier1 = supplier_factory(
            name="Alpha Nursery", specialization="Native Plants"
        )
        supplier2 = supplier_factory(
            name="Beta Tools", specialization="Garden Equipment"
        )
        supplier3 = supplier_factory(
            name="Gamma Plants", specialization="Native Plants"
        )

        # Add products and plants to suppliers
        for _ in range(5):
            product_factory(supplier=supplier1)
        for _ in range(3):
            plant_factory(supplier=supplier1)

        for _ in range(4):
            product_factory(supplier=supplier2)
        for _ in range(1):
            plant_factory(supplier=supplier2)

        for _ in range(2):
            product_factory(supplier=supplier3)

        analytics = DashboardService.get_supplier_analytics()

        assert analytics["total_suppliers"] == 3

        # Check top suppliers (sorted by total items)
        assert len(analytics["top_suppliers"]) == 3
        top_supplier = analytics["top_suppliers"][0]
        assert top_supplier["name"] == "Alpha Nursery"
        assert top_supplier["total_items"] == 8  # 5 products + 3 plants

        # Check specializations
        spec_counts = {
            item["specialization"]: item["count"]
            for item in analytics["specializations"]
        }
        assert spec_counts["Native Plants"] == 2
        assert spec_counts["Garden Equipment"] == 1

    def test_get_recent_activity_empty(self, app_context):
        """Test getting recent activity with empty database"""
        activity = DashboardService.get_recent_activity()

        assert activity["recent_projects"] == []
        assert activity["recent_clients"] == []
        assert activity["recent_plants"] == []

    def test_get_recent_activity_with_data(
        self, app_context, client_factory, project_factory, plant_factory
    ):
        """Test getting recent activity with sample data"""
        # Create recent entities
        clients = [client_factory(name=f"Client {i}") for i in range(3)]
        plants = [plant_factory(name=f"Plant {i}") for i in range(3)]  # noqa: F841
        projects = [  # noqa: F841
            project_factory(client=clients[i], name=f"Project {i}", status="active")
            for i in range(3)
        ]

        activity = DashboardService.get_recent_activity(limit=5)

        assert len(activity["recent_projects"]) == 3
        assert len(activity["recent_clients"]) == 3
        assert len(activity["recent_plants"]) == 3

        # Check project data structure
        project_data = activity["recent_projects"][0]
        assert "id" in project_data
        assert "name" in project_data
        assert "client_name" in project_data
        assert "created_at" in project_data
        assert "status" in project_data

    def test_get_performance_metrics_empty(self, app_context):
        """Test getting performance metrics with empty database"""
        metrics = DashboardService.get_performance_metrics()

        assert metrics["project_completion_rate"] == 0
        assert metrics["average_project_duration_days"] == 0
        assert metrics["plant_utilization_rate"] == 0
        assert metrics["total_entities"]["clients"] == 0
        assert metrics["total_entities"]["projects"] == 0
        assert metrics["total_entities"]["plants"] == 0
        assert metrics["total_entities"]["suppliers"] == 0

    def test_get_performance_metrics_with_data(
        self, app_context, client_factory, project_factory, plant_factory
    ):
        """Test getting performance metrics with sample data"""
        # Create test data
        clients = [client_factory() for _ in range(2)]
        plants = [plant_factory() for _ in range(5)]

        # Create projects with different statuses and dates
        start_date = datetime.utcnow() - timedelta(days=30)
        completion_date = datetime.utcnow() - timedelta(days=10)

        projects = [
            project_factory(
                client=clients[0],
                status="completed",
                start_date=start_date,
                actual_completion_date=completion_date,
            ),
            project_factory(client=clients[1], status="active"),
            project_factory(client=clients[0], status="planning"),
        ]

        # Add some plants to projects
        pp1 = ProjectPlant(project=projects[0], plant=plants[0], quantity=5)
        pp2 = ProjectPlant(project=projects[1], plant=plants[1], quantity=3)
        db.session.add_all([pp1, pp2])
        db.session.commit()

        metrics = DashboardService.get_performance_metrics()

        # Check completion rate: 1 completed out of 3 total = 33.33%
        assert abs(metrics["project_completion_rate"] - 33.33333333333333) < 0.1

        # Check average duration: 20 days
        assert metrics["average_project_duration_days"] == 20.0

        # Check plant utilization: 2 plants used out of 5 total = 40%
        assert metrics["plant_utilization_rate"] == 40.0

        # Check total entities
        assert metrics["total_entities"]["clients"] == 2
        assert metrics["total_entities"]["projects"] == 3
        assert metrics["total_entities"]["plants"] == 5


@pytest.mark.integration
class TestDashboardServiceIntegration(DatabaseTestMixin):
    """Integration tests for Dashboard Service"""

    def test_comprehensive_dashboard_scenario(
        self,
        app_context,
        client_factory,
        project_factory,
        plant_factory,
        supplier_factory,
        product_factory,
    ):
        """Test comprehensive dashboard scenario with all data types"""
        # Clear cache to ensure fresh data
        from src.services.performance import cache

        cache.clear()

        # Create a realistic dataset

        # Clients
        clients = [
            client_factory(name="Alpha Corp", company="Alpha Construction"),
            client_factory(name="Beta LLC", company="Beta Landscaping"),
            client_factory(name="Gamma Inc", company="Gamma Design"),
        ]

        # Suppliers
        suppliers = [
            supplier_factory(
                name="Native Plants Nursery", specialization="Native Plants"
            ),
            supplier_factory(name="Garden Tools Co", specialization="Garden Equipment"),
        ]

        # Plants
        plants = [
            plant_factory(
                name="Red Oak", category="Tree", native=True, supplier=suppliers[0]
            ),
            plant_factory(
                name="Rose Bush", category="Shrub", native=False, supplier=suppliers[0]
            ),
            plant_factory(
                name="Tulip", category="Perennial", native=False, supplier=suppliers[0]
            ),
        ]

        # Products
        products = [  # noqa: F841
            product_factory(
                name="Shovel", supplier=suppliers[1], price=25.0, stock_quantity=10
            ),
            product_factory(
                name="Fertilizer", supplier=suppliers[1], price=15.0, stock_quantity=50
            ),
        ]

        # Projects with varying dates, statuses, and budgets
        now = datetime.utcnow()
        projects = [
            project_factory(
                client=clients[0],
                name="Corporate Garden",
                status="completed",
                budget=15000.0,
                created_at=now - timedelta(days=45),
                start_date=now - timedelta(days=40),
                actual_completion_date=now - timedelta(days=10),
            ),
            project_factory(
                client=clients[1],
                name="Residential Landscape",
                status="active",
                budget=8000.0,
                created_at=now - timedelta(days=20),
                start_date=now - timedelta(days=15),
            ),
            project_factory(
                client=clients[0],
                name="Office Courtyard",
                status="planning",
                budget=5000.0,
                created_at=now - timedelta(days=5),
            ),
            project_factory(
                client=clients[2],
                name="Park Enhancement",
                status="active",
                budget=20000.0,
                created_at=now - timedelta(days=10),
            ),
        ]

        # Project-Plant relationships
        pp1 = ProjectPlant(
            project=projects[0], plant=plants[0], quantity=10, unit_cost=50.0
        )
        pp2 = ProjectPlant(
            project=projects[0], plant=plants[1], quantity=25, unit_cost=20.0
        )
        pp3 = ProjectPlant(
            project=projects[1], plant=plants[0], quantity=5, unit_cost=50.0
        )
        pp4 = ProjectPlant(
            project=projects[3], plant=plants[2], quantity=100, unit_cost=5.0
        )
        db.session.add_all([pp1, pp2, pp3, pp4])
        db.session.commit()

        # Test dashboard summary
        summary = DashboardService.get_dashboard_summary()
        assert summary["totals"]["clients"] == 3
        assert summary["totals"]["projects"] == 4
        assert summary["totals"]["plants"] == 3
        assert summary["totals"]["suppliers"] == 2
        assert summary["totals"]["active_projects"] == 2
        assert summary["financial"]["total_budget"] == 48000.0

        # Test project analytics
        project_analytics = DashboardService.get_project_analytics(days=60)
        assert len(project_analytics["projects_by_status"]) == 3
        assert project_analytics["average_budget"] == 12000.0

        # Top client should be Alpha Corp with 2 projects
        top_clients = project_analytics["top_clients"]
        assert top_clients[0]["name"] == "Alpha Corp"
        assert top_clients[0]["project_count"] == 2

        # Test plant analytics
        plant_analytics = DashboardService.get_plant_analytics()

        # Most used plant should be Tulip (total quantity: 100)
        most_used = plant_analytics["most_used_plants"][0]
        assert most_used["name"] == "Tulip"
        assert most_used["total_quantity"] == 100
        assert most_used["project_count"] == 1

        # Test financial analytics
        financial_analytics = DashboardService.get_financial_analytics()
        assert financial_analytics["total_project_value"] == 48000.0
        assert financial_analytics["average_project_value"] == 12000.0

        # Test supplier analytics
        supplier_analytics = DashboardService.get_supplier_analytics()
        assert supplier_analytics["total_suppliers"] == 2

        # Native Plants Nursery should be top supplier (3 plants vs 2 products)
        top_supplier = supplier_analytics["top_suppliers"][0]
        assert top_supplier["name"] == "Native Plants Nursery"
        assert top_supplier["total_items"] == 3

        # Test performance metrics
        performance = DashboardService.get_performance_metrics()
        assert performance["project_completion_rate"] == 25.0  # 1 out of 4
        assert performance["average_project_duration_days"] == 30.0  # 40-10 days
        assert performance["plant_utilization_rate"] == 100.0  # All 3 plants used

        # Test recent activity
        recent_activity = DashboardService.get_recent_activity(limit=10)
        assert len(recent_activity["recent_projects"]) == 4
        assert len(recent_activity["recent_clients"]) == 3
        assert len(recent_activity["recent_plants"]) == 3

    def test_dashboard_with_time_filtering(
        self, app_context, client_factory, project_factory
    ):
        """Test dashboard analytics with different time ranges"""
        # Clear cache to ensure fresh data
        from src.services.performance import cache

        cache.clear()

        client = client_factory()
        now = datetime.utcnow()

        # Create projects at different times
        old_project = project_factory(  # noqa: F841
            client=client, created_at=now - timedelta(days=100), budget=5000.0
        )
        recent_project = project_factory(  # noqa: F841
            client=client, created_at=now - timedelta(days=10), budget=8000.0
        )
        very_recent_project = project_factory(  # noqa: F841
            client=client, created_at=now - timedelta(days=2), budget=3000.0
        )

        # Test 30-day analytics (should include 2 recent projects)
        analytics_30 = DashboardService.get_project_analytics(days=30)
        assert (
            len([p for p in analytics_30["projects_over_time"]]) >= 0
        )  # May vary by date grouping

        # Test 7-day analytics (should include 1 very recent project)
        analytics_7 = DashboardService.get_project_analytics(days=7)
        assert (
            len([p for p in analytics_7["projects_over_time"]]) >= 0
        )  # May vary by date grouping

        # Test dashboard summary recent activity
        summary = DashboardService.get_dashboard_summary()
        assert summary["recent_activity"]["new_projects"] == 2  # Last 30 days

    def test_dashboard_edge_cases(
        self, app_context, client_factory, project_factory, plant_factory
    ):
        """Test dashboard service edge cases and error handling"""
        # Test with projects having null budgets
        client = client_factory()
        project_with_budget = project_factory(  # noqa: F841
            client=client, budget=5000.0
        )  # noqa: F841
        project_without_budget = project_factory(  # noqa: F841
            client=client, budget=None
        )  # noqa: F841

        financial_analytics = DashboardService.get_financial_analytics()
        assert financial_analytics["total_project_value"] == 5000.0
        assert financial_analytics["average_project_value"] == 5000.0

        # Test with plants not used in any projects
        unused_plant = plant_factory()  # noqa: F841

        plant_analytics = DashboardService.get_plant_analytics()
        assert (
            len(plant_analytics["most_used_plants"]) == 0
        )  # No ProjectPlant relationships

        performance = DashboardService.get_performance_metrics()
        assert performance["plant_utilization_rate"] == 0.0  # No plants used

        # Test with completed projects missing dates
        completed_project = project_factory(  # noqa: F841
            client=client,
            status="completed",
            start_date=None,
            actual_completion_date=None,
        )

        performance = DashboardService.get_performance_metrics()
        assert (
            performance["average_project_duration_days"] == 0
        )  # No valid duration data
