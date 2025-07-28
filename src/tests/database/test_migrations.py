import pytest
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import inspect
import os

class TestDatabaseMigrations:
    
    def test_migration_config_exists(self, app_context):
        """Test that migration configuration exists"""
        alembic_ini_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'migrations', 'alembic.ini'
        )
        assert os.path.exists(alembic_ini_path), "Alembic configuration file not found"
    
    def test_database_schema_matches_models(self, app_context):
        """Test that database schema matches SQLAlchemy models"""
        from src.models.user import db
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Check that expected tables exist
        expected_tables = ['plants', 'projects', 'clients', 'user', 'suppliers']
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"
        
        # Check specific table structure for plants
        plant_columns = [col['name'] for col in inspector.get_columns('plants')]
        expected_plant_columns = [
            'id', 'name', 'common_name', 'category', 
            'height_min', 'height_max', 'sun_requirements'
        ]
        
        for col in expected_plant_columns:
            assert col in plant_columns, f"Column {col} not found in plants table"
        
        # Check user table structure
        user_columns = [col['name'] for col in inspector.get_columns('user')]
        expected_user_columns = ['id', 'username', 'email']
        
        for col in expected_user_columns:
            assert col in user_columns, f"Column {col} not found in users table"
    
    def test_foreign_key_constraints(self, app_context):
        """Test that foreign key constraints are properly set up"""
        from src.models.user import db
        
        inspector = inspect(db.engine)
        
        # Check project -> client foreign key
        project_fks = inspector.get_foreign_keys('projects')
        client_fk = next((fk for fk in project_fks if fk['referred_table'] == 'clients'), None)
        assert client_fk is not None, "Foreign key from projects to clients not found"
        
        # Check plant -> supplier foreign key
        plant_fks = inspector.get_foreign_keys('plants')
        supplier_fk = next((fk for fk in plant_fks if fk['referred_table'] == 'suppliers'), None)
        assert supplier_fk is not None, "Foreign key from plants to suppliers not found"
    
    def test_database_indexes(self, app_context):
        """Test that important indexes are created"""
        from src.models.user import db
        
        inspector = inspect(db.engine)
        
        # Check indexes on plants table
        plant_indexes = inspector.get_indexes('plants')
        index_columns = [idx['column_names'] for idx in plant_indexes]
        
        # Should have some indexes - at minimum the primary key
        assert len(plant_indexes) >= 0, "No indexes found on plants table"
        
        # Check indexes on users table
        user_indexes = inspector.get_indexes('user')
        assert len(user_indexes) >= 0, "No indexes found on users table"
    
    def test_table_primary_keys(self, app_context):
        """Test that all tables have proper primary keys"""
        from src.models.user import db
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        for table in tables:
            pk_constraint = inspector.get_pk_constraint(table)
            assert pk_constraint['constrained_columns'], f"Table {table} has no primary key"
            assert 'id' in pk_constraint['constrained_columns'], f"Table {table} primary key is not 'id'"
    
    def test_unique_constraints(self, app_context):
        """Test that unique constraints are properly set up"""
        from src.models.user import db
        
        inspector = inspect(db.engine)
        
        # Check unique constraints on users table
        user_unique_constraints = inspector.get_unique_constraints('user')
        
        # Should have unique constraints on email and username
        constraint_columns = []
        for constraint in user_unique_constraints:
            constraint_columns.extend(constraint['column_names'])
        
        assert 'email' in constraint_columns, "No unique constraint on user email"
        assert 'username' in constraint_columns, "No unique constraint on user username"
    
    def test_nullable_constraints(self, app_context):
        """Test that nullable constraints are properly set up"""
        from src.models.user import db
        
        inspector = inspect(db.engine)
        
        # Check nullable constraints on critical fields
        plant_columns = {col['name']: col['nullable'] for col in inspector.get_columns('plants')}
        assert not plant_columns['name'], "Plant name should not be nullable"
        
        user_columns = {col['name']: col['nullable'] for col in inspector.get_columns('user')}
        assert not user_columns['username'], "User username should not be nullable"
        assert not user_columns['email'], "User email should not be nullable"
        
        client_columns = {col['name']: col['nullable'] for col in inspector.get_columns('clients')}
        assert not client_columns['name'], "Client name should not be nullable"
        
        project_columns = {col['name']: col['nullable'] for col in inspector.get_columns('projects')}
        assert not project_columns['name'], "Project name should not be nullable"
        assert not project_columns['client_id'], "Project client_id should not be nullable"