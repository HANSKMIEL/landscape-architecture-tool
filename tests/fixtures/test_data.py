"""
Factory patterns for creating test data
"""

import factory
import pytest
from faker import Faker

from src.models.landscape import Client, Plant, Product, Project, ProjectPlant, Supplier
from src.models.user import User, db

fake = Faker()


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating User instances"""

    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")


class SupplierFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Supplier instances"""

    class Meta:
        model = Supplier
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("company")
    contact_person = factory.Faker("name")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    address = factory.Faker("street_address")
    city = factory.Faker("city")
    postal_code = factory.Faker("postcode")
    specialization = factory.Faker("catch_phrase")
    website = factory.Faker("url")
    notes = factory.Faker("text", max_nb_chars=200)


class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Product instances"""

    class Meta:
        model = Product
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("word")
    category = factory.Faker(
        "random_element", elements=["Tools", "Fertilizer", "Seeds", "Equipment"]
    )
    description = factory.Faker("text", max_nb_chars=200)
    price = factory.Faker("pyfloat", left_digits=2, right_digits=2, positive=True)
    unit = factory.Faker("random_element", elements=["piece", "kg", "liter", "meter"])
    sku = factory.Sequence(lambda n: f"SKU{n:04d}")
    supplier = factory.SubFactory(SupplierFactory)
    stock_quantity = factory.Faker("random_int", min=0, max=100)
    weight = factory.Faker("pyfloat", left_digits=1, right_digits=2, positive=True)
    dimensions = factory.Faker("pystr", max_chars=20)
    notes = factory.Faker("text", max_nb_chars=100)


class PlantFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Plant instances"""

    class Meta:
        model = Plant
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("word")
    common_name = factory.Faker("word")
    category = factory.Faker(
        "random_element", elements=["Tree", "Shrub", "Perennial", "Annual"]
    )
    height_min = factory.Faker("random_int", min=10, max=100)
    height_max = factory.Faker("random_int", min=100, max=500)
    width_min = factory.Faker("random_int", min=10, max=100)
    width_max = factory.Faker("random_int", min=100, max=300)
    hardiness_zone = factory.Faker(
        "random_element", elements=["3a", "3b", "4a", "4b", "5a", "5b"]
    )
    sun_requirements = factory.Faker(
        "random_element", elements=["full_sun", "partial_shade", "full_shade"]
    )
    sun_exposure = factory.Faker(
        "random_element", elements=["full_sun", "partial_shade", "full_shade"]
    )
    soil_type = factory.Faker(
        "random_element", elements=["clay", "sand", "loam", "silt"]
    )
    soil_ph_min = factory.Faker(
        "pyfloat",
        left_digits=1,
        right_digits=1,
        positive=True,
        min_value=4.0,
        max_value=6.0,
    )
    soil_ph_max = factory.Faker(
        "pyfloat",
        left_digits=1,
        right_digits=1,
        positive=True,
        min_value=7.0,
        max_value=9.0,
    )
    moisture_level = factory.Faker("random_element", elements=["low", "medium", "high"])
    bloom_time = factory.Faker(
        "random_element", elements=["spring", "summer", "fall", "winter"]
    )
    bloom_color = factory.Faker("color_name")
    maintenance = factory.Faker("random_element", elements=["low", "medium", "high"])
    price = factory.Faker("pyfloat", left_digits=2, right_digits=2, positive=True)
    notes = factory.Faker("text", max_nb_chars=200)
    native = factory.Faker("boolean")
    wildlife_value = factory.Faker("random_element", elements=["low", "medium", "high"])
    pollinator_friendly = factory.Faker("boolean")
    deer_resistant = factory.Faker("boolean")
    supplier = factory.SubFactory(SupplierFactory)


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Client instances"""

    class Meta:
        model = Client
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("company")  # For business/organization client names
    company = factory.Faker("company")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    address = factory.Faker("street_address")
    city = factory.Faker("city")
    postal_code = factory.Faker("postcode")
    notes = factory.Faker("text", max_nb_chars=200)


class ProjectFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Project instances"""

    class Meta:
        model = Project
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("catch_phrase")
    description = factory.Faker("text", max_nb_chars=500)
    location = factory.Faker("address")
    area_size = factory.Faker("pyfloat", left_digits=3, right_digits=2, positive=True)
    budget = factory.Faker("pyfloat", left_digits=5, right_digits=2, positive=True)
    status = factory.Faker(
        "random_element", elements=["planning", "active", "completed", "on_hold"]
    )
    start_date = factory.Faker("date_this_year")
    target_completion_date = factory.Faker("date_this_year")
    client = factory.SubFactory(ClientFactory)
    notes = factory.Faker("text", max_nb_chars=300)


class ProjectPlantFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating ProjectPlant instances"""

    class Meta:
        model = ProjectPlant
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    project = factory.SubFactory(ProjectFactory)
    plant = factory.SubFactory(PlantFactory)
    quantity = factory.Faker("random_int", min=1, max=50)
    unit_cost = factory.Faker("pyfloat", left_digits=2, right_digits=2, positive=True)
    notes = factory.Faker("text", max_nb_chars=100)


# Pytest fixtures for factories
@pytest.fixture
def user_factory():
    return UserFactory


@pytest.fixture
def supplier_factory():
    return SupplierFactory


@pytest.fixture
def product_factory():
    return ProductFactory


@pytest.fixture
def plant_factory():
    return PlantFactory


@pytest.fixture
def client_factory():
    return ClientFactory


@pytest.fixture
def project_factory():
    return ProjectFactory


@pytest.fixture
def project_plant_factory():
    return ProjectPlantFactory


@pytest.fixture
def sample_user(user_factory):
    """Create a sample user for testing"""
    return user_factory()


@pytest.fixture
def sample_supplier(supplier_factory):
    """Create a sample supplier for testing"""
    return supplier_factory()


@pytest.fixture
def sample_product(product_factory):
    """Create a sample product for testing"""
    return product_factory()


@pytest.fixture
def sample_plant(plant_factory):
    """Create a sample plant for testing"""
    return plant_factory()


@pytest.fixture
def sample_client(client_factory):
    """Create a sample client for testing"""
    return client_factory()


@pytest.fixture
def sample_project(project_factory):
    """Create a sample project for testing"""
    return project_factory()


@pytest.fixture
def sample_project_plant(project_plant_factory):
    """Create a sample project-plant relationship for testing"""
    return project_plant_factory()


@pytest.fixture
def sample_plants(plant_factory):
    """Create multiple sample plants for testing"""
    return [plant_factory() for _ in range(5)]


@pytest.fixture
def sample_projects(project_factory):
    """Create multiple sample projects for testing"""
    return [project_factory() for _ in range(3)]
