import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.models.landscape import Plant, Project, Client
from src.models.user import User
from src.tests.database.factories import (
    create_test_plant, create_test_project, 
    create_test_client, create_test_user
)

class TestDatabaseOperations:
    
    def test_plant_crud_operations(self, db_session):
        """Test basic CRUD operations for Plant model"""
        # Create
        plant = create_test_plant(name='Test Rose', common_name='Rose')
        db_session.add(plant)
        db_session.commit()
        
        assert plant.id is not None
        assert plant.name == 'Test Rose'
        
        # Read
        retrieved_plant = db_session.query(Plant).filter_by(name='Test Rose').first()
        assert retrieved_plant is not None
        assert retrieved_plant.common_name == 'Rose'
        
        # Update
        retrieved_plant.height_max = 200
        db_session.commit()
        
        updated_plant = db_session.query(Plant).get(plant.id)
        assert updated_plant.height_max == 200
        
        # Delete
        db_session.delete(updated_plant)
        db_session.commit()
        
        deleted_plant = db_session.query(Plant).get(plant.id)
        assert deleted_plant is None
    
    def test_project_client_relationship(self, db_session):
        """Test relationship between Project and Client models"""
        # Create client and project
        client = create_test_client(name='Test Client')
        project = create_test_project(name='Test Project', client=client)
        
        db_session.add(client)
        db_session.add(project)
        db_session.commit()
        
        # Test relationship
        assert project.client.name == 'Test Client'
        assert client.projects[0].name == 'Test Project'
        
        # Test cascade behavior - deleting client should handle projects appropriately
        project_id = project.id
        client_id = client.id
        db_session.delete(client)
        db_session.commit()
        
        # Project should be deleted due to cascade
        remaining_project = db_session.query(Project).get(project_id)
        assert remaining_project is None
    
    def test_database_constraints(self, db_session):
        """Test database constraints and validation"""
        # Test unique constraint on user email by creating objects manually
        from src.models.user import User
        
        user1 = User(username='user1', email='test@example.com')
        user2 = User(username='user2', email='test@example.com')
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
    
    def test_plant_search_functionality(self, db_session):
        """Test plant search and filtering"""
        # Create test plants with different characteristics
        rose = create_test_plant(
            name='Rose',
            category='shrub',
            sun_requirements='full_sun',
            height_min=50,
            height_max=150
        )
        lavender = create_test_plant(
            name='Lavender',
            category='perennial',
            sun_requirements='full_sun',
            height_min=30,
            height_max=60
        )
        hosta = create_test_plant(
            name='Hosta',
            category='perennial',
            sun_requirements='partial_shade',
            height_min=20,
            height_max=80
        )
        
        db_session.add_all([rose, lavender, hosta])
        db_session.commit()
        
        # Test filtering by sun requirements
        full_sun_plants = db_session.query(Plant).filter_by(sun_requirements='full_sun').all()
        assert len(full_sun_plants) == 2
        assert all(p.sun_requirements == 'full_sun' for p in full_sun_plants)
        
        # Test filtering by height range
        short_plants = db_session.query(Plant).filter(Plant.height_max <= 100).all()
        assert len(short_plants) == 2  # lavender and hosta
        
        # Test complex filtering
        full_sun_shrubs = db_session.query(Plant).filter(
            Plant.sun_requirements == 'full_sun',
            Plant.category == 'shrub'
        ).all()
        assert len(full_sun_shrubs) == 1
        assert full_sun_shrubs[0].name == 'Rose'
    
    def test_project_status_transitions(self, db_session):
        """Test project status transitions and business logic"""
        project = create_test_project(status='Planning')
        db_session.add(project)
        db_session.commit()
        
        # Test status transition
        project.status = 'Active'
        db_session.commit()
        
        updated_project = db_session.query(Project).get(project.id)
        assert updated_project.status == 'Active'
        
        # Test completion
        project.status = 'Completed'
        db_session.commit()
        
        completed_project = db_session.query(Project).get(project.id)
        assert completed_project.status == 'Completed'
    
    def test_database_performance(self, db_session):
        """Test database performance with larger datasets"""
        import time
        
        # Create multiple plants for performance testing
        plants = [create_test_plant() for _ in range(100)]
        
        start_time = time.time()
        db_session.add_all(plants)
        db_session.commit()
        insert_time = time.time() - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert insert_time < 5.0, f"Bulk insert took {insert_time:.2f} seconds"
        
        # Test query performance
        start_time = time.time()
        results = db_session.query(Plant).filter(Plant.category == 'shrub').all()
        query_time = time.time() - start_time
        
        assert query_time < 1.0, f"Query took {query_time:.2f} seconds"
    
    def test_transaction_rollback(self, db_session):
        """Test transaction rollback functionality"""
        initial_count = db_session.query(Plant).count()
        
        try:
            # Create plants manually without using factories (to avoid auto-commit)
            plant1 = Plant(name='Plant 1', common_name='Plant 1')
            plant2 = Plant(name='Plant 2', common_name='Plant 2')
            
            db_session.add(plant1)
            db_session.add(plant2)
            
            # Don't commit yet - simulate an error before commit
            raise Exception("Simulated error")
            
        except Exception:
            db_session.rollback()
        
        # Count should be unchanged since we never committed
        final_count = db_session.query(Plant).count()
        assert final_count == initial_count

    def test_client_crud_operations(self, db_session):
        """Test basic CRUD operations for Client model"""
        # Create
        client = create_test_client(name='Test Company', email='test@company.com')
        db_session.add(client)
        db_session.commit()
        
        assert client.id is not None
        assert client.name == 'Test Company'
        
        # Read
        retrieved_client = db_session.query(Client).filter_by(name='Test Company').first()
        assert retrieved_client is not None
        assert retrieved_client.email == 'test@company.com'
        
        # Update
        retrieved_client.phone = '555-1234'
        db_session.commit()
        
        updated_client = db_session.query(Client).get(client.id)
        assert updated_client.phone == '555-1234'
        
        # Delete
        db_session.delete(updated_client)
        db_session.commit()
        
        deleted_client = db_session.query(Client).get(client.id)
        assert deleted_client is None

    def test_supplier_plant_relationship(self, db_session):
        """Test relationship between Supplier and Plant models"""
        from src.tests.database.factories import create_test_supplier
        
        # Create supplier and plant
        supplier = create_test_supplier(name='Test Nursery')
        plant = create_test_plant(name='Test Plant', supplier=supplier)
        
        db_session.add(supplier)
        db_session.add(plant)
        db_session.commit()
        
        # Test relationship
        assert plant.supplier.name == 'Test Nursery'
        assert supplier.plants[0].name == 'Test Plant'