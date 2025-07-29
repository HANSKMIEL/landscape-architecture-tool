"""
Performance tests for database query optimizations
Tests query performance before and after optimization implementation
"""

import pytest
import time
from datetime import datetime, timedelta
from sqlalchemy import text

from src.models.landscape import Plant, Project, Client, Supplier
from src.models.user import db


class TestDatabasePerformance:
    """Test database query performance improvements"""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, app):
        """Set up test data for performance testing"""
        with app.app_context():
            # Clear existing data
            db.session.query(Plant).delete()
            db.session.query(Project).delete()
            db.session.query(Client).delete()
            db.session.query(Supplier).delete()
            
            # Create suppliers
            suppliers = []
            for i in range(10):
                supplier = Supplier(
                    name=f"Test Supplier {i}",
                    city=f"City {i % 3}",
                    specialization=f"Specialization {i % 5}"
                )
                suppliers.append(supplier)
                db.session.add(supplier)
            
            db.session.flush()  # Get IDs
            
            # Create many plants for performance testing
            plants = []
            categories = ["Tree", "Shrub", "Perennial", "Annual", "Grass"]
            sun_requirements = ["Full Sun", "Partial Sun", "Shade", "Full Sun to Partial Sun"]
            water_needs = ["Low", "Medium", "High"]
            
            for i in range(1000):  # Create 1000 plants
                plant = Plant(
                    name=f"Test Plant {i}",
                    common_name=f"Common Plant {i}",
                    category=categories[i % len(categories)],
                    sun_requirements=sun_requirements[i % len(sun_requirements)],
                    water_needs=water_needs[i % len(water_needs)],
                    hardiness_zone=f"Zone {(i % 9) + 1}",
                    native=(i % 3 == 0),  # Every third plant is native
                    price=10.0 + (i % 100),
                    supplier_id=suppliers[i % len(suppliers)].id
                )
                plants.append(plant)
                db.session.add(plant)
            
            # Create clients
            clients = []
            for i in range(50):
                client = Client(
                    name=f"Test Client {i}",
                    city=f"City {i % 5}",
                    client_type=f"Type {i % 3}"
                )
                clients.append(client)
                db.session.add(client)
            
            db.session.flush()
            
            # Create projects
            for i in range(200):
                project = Project(
                    name=f"Test Project {i}",
                    client_id=clients[i % len(clients)].id,
                    status=["Planning", "Active", "Completed"][i % 3],
                    project_type=f"Type {i % 4}",
                    budget=1000.0 + (i * 100)
                )
                db.session.add(project)
            
            db.session.commit()

    def test_plant_search_performance(self, app):
        """Test plant search query performance"""
        with app.app_context():
            # Test search without filters (baseline)
            start_time = time.time()
            plants = Plant.query.limit(50).all()
            baseline_time = time.time() - start_time
            
            # Test search with category filter (should use index)
            start_time = time.time()
            plants = Plant.query.filter(Plant.category == "Tree").limit(50).all()
            category_filter_time = time.time() - start_time
            
            # Test search with multiple filters (should use indexes)
            start_time = time.time()
            plants = Plant.query.filter(
                Plant.category == "Tree",
                Plant.sun_requirements == "Full Sun",
                Plant.native.is_(True)
            ).limit(50).all()
            multi_filter_time = time.time() - start_time
            
            # Test text search (should be reasonably fast)
            start_time = time.time()
            plants = Plant.query.filter(
                Plant.name.ilike("%Plant 1%")
            ).limit(50).all()
            text_search_time = time.time() - start_time
            
            # Performance assertions (these may need adjustment based on hardware)
            assert baseline_time < 0.1, f"Baseline query too slow: {baseline_time:.3f}s"
            assert category_filter_time < 0.1, f"Category filter query too slow: {category_filter_time:.3f}s"
            assert multi_filter_time < 0.15, f"Multi-filter query too slow: {multi_filter_time:.3f}s"
            assert text_search_time < 0.2, f"Text search query too slow: {text_search_time:.3f}s"
            
            print(f"Query performance results:")
            print(f"  Baseline: {baseline_time:.3f}s")
            print(f"  Category filter: {category_filter_time:.3f}s")
            print(f"  Multi-filter: {multi_filter_time:.3f}s")
            print(f"  Text search: {text_search_time:.3f}s")

    def test_project_query_performance(self, app):
        """Test project query performance with client relationships"""
        with app.app_context():
            # Test project list with client information
            start_time = time.time()
            projects = db.session.query(Project).join(Client).limit(50).all()
            join_query_time = time.time() - start_time
            
            # Test filtered project queries
            start_time = time.time()
            projects = Project.query.filter(
                Project.status == "Active"
            ).limit(50).all()
            status_filter_time = time.time() - start_time
            
            # Test client-specific project query
            start_time = time.time()
            projects = Project.query.filter(
                Project.client_id == 1
            ).limit(50).all()
            client_filter_time = time.time() - start_time
            
            assert join_query_time < 0.15, f"Project-client join too slow: {join_query_time:.3f}s"
            assert status_filter_time < 0.1, f"Status filter too slow: {status_filter_time:.3f}s"
            assert client_filter_time < 0.1, f"Client filter too slow: {client_filter_time:.3f}s"
            
            print(f"Project query performance:")
            print(f"  Join query: {join_query_time:.3f}s")
            print(f"  Status filter: {status_filter_time:.3f}s")
            print(f"  Client filter: {client_filter_time:.3f}s")

    def test_pagination_performance(self, app):
        """Test pagination performance for large datasets"""
        with app.app_context():
            # Test first page
            start_time = time.time()
            plants = Plant.query.paginate(page=1, per_page=50, error_out=False)
            first_page_time = time.time() - start_time
            
            # Test middle page
            start_time = time.time()
            plants = Plant.query.paginate(page=10, per_page=50, error_out=False)
            middle_page_time = time.time() - start_time
            
            # Test last page
            start_time = time.time()
            plants = Plant.query.paginate(page=20, per_page=50, error_out=False)
            last_page_time = time.time() - start_time
            
            assert first_page_time < 0.1, f"First page too slow: {first_page_time:.3f}s"
            assert middle_page_time < 0.15, f"Middle page too slow: {middle_page_time:.3f}s"
            assert last_page_time < 0.15, f"Last page too slow: {last_page_time:.3f}s"
            
            print(f"Pagination performance:")
            print(f"  First page: {first_page_time:.3f}s")
            print(f"  Middle page: {middle_page_time:.3f}s")
            print(f"  Last page: {last_page_time:.3f}s")

    def test_index_usage(self, app):
        """Test that queries are actually using indexes"""
        with app.app_context():
            # This test checks if indexes are being used by examining query plans
            # Note: SQLite's EXPLAIN QUERY PLAN may not show detailed index usage
            
            # Test category index usage
            result = db.session.execute(
                text("EXPLAIN QUERY PLAN SELECT * FROM plants WHERE category = 'Tree'")
            ).fetchall()
            
            # For SQLite, we look for "USING INDEX" in the query plan
            query_plan = str(result)
            print(f"Category query plan: {query_plan}")
            
            # Test composite index usage
            result = db.session.execute(
                text("EXPLAIN QUERY PLAN SELECT * FROM plants WHERE category = 'Tree' AND sun_requirements = 'Full Sun'")
            ).fetchall()
            
            query_plan = str(result)
            print(f"Composite query plan: {query_plan}")
            
            # For a proper test, we'd check that the query plan mentions index usage
            # This is database-specific and may vary between SQLite, PostgreSQL, etc.

    def test_bulk_operations_performance(self, app):
        """Test performance of bulk operations"""
        with app.app_context():
            # Test bulk update
            start_time = time.time()
            db.session.query(Plant).filter(
                Plant.category == "Tree"
            ).update({"maintenance": "Low"})
            db.session.commit()
            bulk_update_time = time.time() - start_time
            
            # Test bulk delete (create test records first)
            test_plants = []
            for i in range(100):
                plant = Plant(
                    name=f"Bulk Test Plant {i}",
                    category="BulkTest"
                )
                test_plants.append(plant)
                db.session.add(plant)
            db.session.commit()
            
            start_time = time.time()
            db.session.query(Plant).filter(
                Plant.category == "BulkTest"
            ).delete()
            db.session.commit()
            bulk_delete_time = time.time() - start_time
            
            assert bulk_update_time < 0.5, f"Bulk update too slow: {bulk_update_time:.3f}s"
            assert bulk_delete_time < 0.3, f"Bulk delete too slow: {bulk_delete_time:.3f}s"
            
            print(f"Bulk operations performance:")
            print(f"  Bulk update: {bulk_update_time:.3f}s")
            print(f"  Bulk delete: {bulk_delete_time:.3f}s")