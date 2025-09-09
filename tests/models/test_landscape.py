"""
Tests for landscape models
"""

from src.models.landscape import PlantRecommendationRequest
from src.models.user import db


class TestPlantRecommendationRequest:
    """Test PlantRecommendationRequest model functionality"""

    def test_plant_recommendation_request_to_dict(self, app_context):
        """Test PlantRecommendationRequest to_dict method"""
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
        
        request = PlantRecommendationRequest(
            project_type="Garden",
            hardiness_zone="5-8",
            sun_exposure="Full Sun",
            soil_type="Loamy",
            soil_ph=7.0,
            moisture_level="Moderate",
        )
        db.session.add(request)
        db.session.commit()

        request_dict = request.to_dict()

        assert request_dict["id"] == request.id
        assert request_dict["project_type"] == "Garden"
        assert request_dict["hardiness_zone"] == "5-8"
        assert request_dict["sun_exposure"] == "Full Sun"
        assert request_dict["soil_type"] == "Loamy"
        assert request_dict["soil_ph"] == 7.0
        assert request_dict["moisture_level"] == "Moderate"
