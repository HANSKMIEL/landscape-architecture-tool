"""
Tests for landscape models
"""

from src.models.landscape import PlantRecommendationRequest
from src.models.user import db


class TestPlantRecommendationRequest:
    """Test PlantRecommendationRequest model functionality"""

    def test_plant_recommendation_request_to_dict(self, app_context):
        """Test PlantRecommendationRequest to_dict method"""
    # Authentication handled by authenticated_test_user fixture
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
