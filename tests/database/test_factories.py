"""
Tests for database factories
"""

from src.models.landscape import Plant
from tests.database.factories import create_test_plant


class TestPlantFactory:
    """Test the plant factory function"""

    def test_create_test_plant_default_values(self):
        """Test creating a plant with default values"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        plant = create_test_plant()

        assert isinstance(plant, Plant)
        assert plant.name is not None
        assert plant.common_name is not None
        assert plant.category is not None
        assert plant.sun_requirements is not None
        assert plant.soil_type is not None
        assert plant.height_min is not None
        assert plant.height_max is not None
        assert plant.width_min is not None
        assert plant.width_max is not None
        assert plant.hardiness_zone is not None
        assert plant.water_needs is not None
        assert plant.bloom_time is not None
        assert plant.bloom_color is not None
        assert plant.foliage_color is not None
        assert plant.maintenance is not None
        assert plant.native is not None
        assert plant.wildlife_value is not None
        assert plant.pollinator_friendly is not None
        assert plant.deer_resistant is not None
        assert plant.price is not None

        # Verify that height_max is greater than height_min
        assert plant.height_max > plant.height_min
        assert plant.width_max > plant.width_min

    def test_create_test_plant_with_custom_values(self):
        """Test creating a plant with custom values"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        custom_values = {
            "name": "Custom Rose",
            "common_name": "Beautiful Rose",
            "category": "shrub",
            "sun_requirements": "full_sun",
            "soil_type": "well_drained",
            "height_min": 1.0,
            "height_max": 2.0,
            "width_min": 0.8,
            "width_max": 1.5,
            "hardiness_zone": "5-9",
            "water_needs": "moderate",
            "bloom_time": "summer",
            "bloom_color": "red",
            "foliage_color": "green",
            "maintenance": "low",
            "native": True,
            "wildlife_value": "high",
            "pollinator_friendly": True,
            "deer_resistant": False,
            "price": 25.99,
        }

        plant = create_test_plant(**custom_values)

        assert plant.name == "Custom Rose"
        assert plant.common_name == "Beautiful Rose"
        assert plant.category == "shrub"
        assert plant.sun_requirements == "full_sun"
        assert plant.soil_type == "well_drained"
        assert plant.height_min == 1.0
        assert plant.height_max == 2.0
        assert plant.width_min == 0.8
        assert plant.width_max == 1.5
        assert plant.hardiness_zone == "5-9"
        assert plant.water_needs == "moderate"
        assert plant.bloom_time == "summer"
        assert plant.bloom_color == "red"
        assert plant.foliage_color == "green"
        assert plant.maintenance == "low"
        assert plant.native is True
        assert plant.wildlife_value == "high"
        assert plant.pollinator_friendly is True
        assert plant.deer_resistant is False
        assert plant.price == 25.99

    def test_create_test_plant_with_spread_values(self):
        """Test creating a plant with spread values (compatibility)"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        plant = create_test_plant(spread_min=1.2, spread_max=2.5)

        # Should map spread values to width values
        assert plant.width_min == 1.2
        assert plant.width_max == 2.5

    def test_create_test_plant_with_water_requirements(self):
        """Test creating a plant with water_requirements (compatibility)"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        plant = create_test_plant(water_requirements="high")

        # Should map water_requirements to water_needs
        assert plant.water_needs == "high"

    def test_create_test_plant_random_generation(self):
        """Test that multiple plants have different values"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        plants = [create_test_plant() for _ in range(5)]

        # At least some plants should have different names
        names = [plant.name for plant in plants]
        assert len(set(names)) > 1, "All plants have the same name"

        # Heights should vary
        heights = [plant.height_min for plant in plants]
        assert len(set(heights)) > 1, "All plants have the same height"

    def test_create_test_plant_plant_type_compatibility(self):
        """Test the plant_type compatibility property"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        plant = create_test_plant(plant_type="tree")

        # Should have plant_type attribute set
        assert hasattr(plant, "plant_type")
        assert plant.plant_type == "tree"

    def test_create_test_plant_ph_values(self):
        """Test pH range values"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        plant = create_test_plant()

        assert plant.soil_ph_min is not None
        assert plant.soil_ph_max is not None
        assert plant.soil_ph_max > plant.soil_ph_min
        assert 4.0 <= plant.soil_ph_min <= 8.0
        assert 5.0 <= plant.soil_ph_max <= 9.0

    def test_create_test_plant_boolean_fields(self):
        """Test boolean field generation"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        plant = create_test_plant()

        boolean_fields = [
            "native",
            "pollinator_friendly",
            "deer_resistant",
            "suitable_for_containers",
            "suitable_for_hedging",
            "suitable_for_screening",
            "suitable_for_groundcover",
            "suitable_for_slopes",
        ]

        for field in boolean_fields:
            value = getattr(plant, field)
            assert isinstance(value, bool), f"{field} should be boolean, got {type(value)}"

    def test_create_test_plant_choice_fields(self):
        """Test fields with specific choice values"""
                # Create a test user in the database
        from src.models.user import User, db
        
        test_user = User(username='test_user', email='test@example.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Set up authentication in session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['role'] = test_user.role
        
        plant = create_test_plant()

        # Test sun requirements
        assert plant.sun_requirements in ["full_sun", "partial_shade", "full_shade"]

        # Test soil type
        assert plant.soil_type in ["well_drained", "moist", "wet", "dry"]

        # Test water needs
        assert plant.water_needs in ["low", "moderate", "high"]

        # Test maintenance
        assert plant.maintenance in ["low", "medium", "high"]

        # Test bloom time
        assert plant.bloom_time in ["spring", "summer", "fall", "winter"]

        # Test resistance levels
        assert plant.pest_resistance in ["low", "medium", "high"]
        assert plant.disease_resistance in ["low", "medium", "high"]

        # Test wildlife value
        assert plant.wildlife_value in ["low", "medium", "high"]
