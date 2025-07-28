import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import create_app
from src.models.user import db
from src.models.landscape import Plant, Project, Client, Supplier
from src.models.user import User

@pytest.fixture(scope='session')
def test_database():
    """Create a temporary test database for the session"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    test_db_url = f'sqlite:///{db_path}'
    
    yield test_db_url
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='session')
def app(test_database):
    """Create application with test database"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = test_database
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def app_context(app):
    """Provide application context for tests"""
    with app.app_context():
        yield app

@pytest.fixture
def db_session(app_context):
    """Provide database session with transaction rollback"""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Configure session to use the connection
    session_factory = sessionmaker(bind=connection)
    session = session_factory()
    
    # Replace the default session
    original_session = db.session
    db.session = session
    
    # Configure factories to use this session
    from src.tests.database.factories import (
        UserFactory, ClientFactory, SupplierFactory, PlantFactory, ProjectFactory
    )
    for factory_class in [UserFactory, ClientFactory, SupplierFactory, PlantFactory, ProjectFactory]:
        factory_class._meta.sqlalchemy_session = session
    
    yield session
    
    # Rollback transaction and cleanup
    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()
    db.session = original_session

@pytest.fixture
def client(app):
    """Provide test client"""
    return app.test_client()