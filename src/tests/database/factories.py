import factory
from factory.alchemy import SQLAlchemyModelFactory
from datetime import datetime, timedelta, timezone
from src.models.user import db
from src.models.landscape import Plant, Project, Client, Supplier
from src.models.user import User

class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session_persistence = 'commit'
        abstract = True

class UserFactory(BaseFactory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    username = factory.Sequence(lambda n: f'user{n}')

class ClientFactory(BaseFactory):
    class Meta:
        model = Client
    
    name = factory.Faker('company')
    contact_person = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    postal_code = factory.Faker('zipcode')
    client_type = factory.Faker('random_element', elements=['residential', 'commercial', 'municipal'])
    budget_range = factory.Faker('random_element', elements=['$1,000-$5,000', '$5,000-$15,000', '$15,000-$50,000'])
    registration_date = factory.LazyFunction(lambda: datetime.now(timezone.utc).strftime('%Y-%m-%d'))
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

class SupplierFactory(BaseFactory):
    class Meta:
        model = Supplier
    
    name = factory.Faker('company')
    contact_person = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    postal_code = factory.Faker('zipcode')
    specialization = factory.Faker('random_element', elements=['plants', 'materials', 'tools', 'garden supplies'])
    website = factory.Faker('url')
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

class PlantFactory(BaseFactory):
    class Meta:
        model = Plant
    
    name = factory.Faker('word')
    common_name = factory.Faker('word')
    category = factory.Faker('random_element', elements=['tree', 'shrub', 'perennial', 'annual'])
    height_min = factory.Faker('random_int', min=10, max=50)
    height_max = factory.Faker('random_int', min=100, max=500)
    width_min = factory.Faker('random_int', min=10, max=50)
    width_max = factory.Faker('random_int', min=50, max=300)
    sun_requirements = factory.Faker('random_element', elements=['full_sun', 'partial_shade', 'full_shade'])
    soil_type = factory.Faker('random_element', elements=['well_drained', 'moist', 'wet', 'dry'])
    water_needs = factory.Faker('random_element', elements=['low', 'moderate', 'high'])
    hardiness_zone = factory.Faker('random_element', elements=['3-7', '4-8', '5-9', '6-10'])
    bloom_time = factory.Faker('random_element', elements=['spring', 'summer', 'fall', 'winter'])
    bloom_color = factory.Faker('color_name')
    foliage_color = factory.Faker('color_name')
    native = factory.Faker('boolean')
    maintenance = factory.Faker('random_element', elements=['low', 'moderate', 'high'])
    growth_rate = factory.Faker('random_element', elements=['slow', 'medium', 'fast'])
    pollinator_friendly = factory.Faker('boolean')
    deer_resistant = factory.Faker('boolean')
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

class ProjectFactory(BaseFactory):
    class Meta:
        model = Project
    
    name = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=200)
    status = factory.Faker('random_element', elements=['Planning', 'Active', 'Completed', 'On Hold'])
    project_type = factory.Faker('random_element', elements=['garden', 'landscape', 'commercial'])
    start_date = factory.LazyFunction(lambda: (datetime.now(timezone.utc) - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = factory.LazyFunction(lambda: (datetime.now(timezone.utc) + timedelta(days=90)).strftime('%Y-%m-%d'))
    budget = factory.Faker('random_int', min=1000, max=50000)
    location = factory.Faker('address')
    area_size = factory.Faker('random_int', min=100, max=5000)
    project_manager = factory.Faker('name')
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    
    # Foreign key relationships
    client = factory.SubFactory(ClientFactory)

# Utility functions for creating test data
def create_test_user(**kwargs):
    """Create a test user with optional overrides"""
    return UserFactory(**kwargs)

def create_test_client(**kwargs):
    """Create a test client with optional overrides"""
    return ClientFactory(**kwargs)

def create_test_plant(**kwargs):
    """Create a test plant with optional overrides"""
    return PlantFactory(**kwargs)

def create_test_project(**kwargs):
    """Create a test project with optional overrides"""
    return ProjectFactory(**kwargs)

def create_test_supplier(**kwargs):
    """Create a test supplier with optional overrides"""
    return SupplierFactory(**kwargs)