"""
Test suite for Plant Recommendation Engine

Tests the multi-criteria recommendation algorithm, API endpoints,
and integration with the database.
"""

import json

import pytest

from src.main import create_app
from src.models.landscape import Plant, PlantRecommendationRequest
from src.models.user import db
from src.services.plant_recommendation import (
    PlantRecommendationEngine,
    RecommendationCriteria,
)


@pytest.fixture
def app():
    """Create test app with test configuration"""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def db_setup(app):
    """Setup test database with sample plants"""
    with app.app_context():
        db.create_all()

        # Create test plants with extended attributes
        plants = [
            Plant(
                name="Acer platanoides",
                common_name="Norway Maple",
                category="Tree",
                height_min=15.0,
                height_max=25.0,
                width_min=12.0,
                width_max=20.0,
                sun_requirements="Full Sun to Partial Shade",
                soil_type="Well-drained loam",
                water_needs="Medium",
                hardiness_zone="4-7",
                bloom_time="Spring",
                bloom_color="Yellow-green",
                foliage_color="Green, yellow fall color",
                native=False,
                maintenance="Low",
                price=75.0,
                # Extended attributes
                temperature_min=-30.0,
                temperature_max=35.0,
                humidity_preference="Medium",
                wind_tolerance="High",
                soil_ph_min=6.0,
                soil_ph_max=7.5,
                soil_drainage="Good",
                soil_fertility="Medium",
                pruning_needs="Light",
                fertilizer_needs="Low",
                pest_resistance="Medium",
                disease_resistance="Medium",
                plant_form="Upright",
                foliage_texture="Medium",
                seasonal_interest="Fall color",
                fragrance=False,
                growth_rate="Medium",
                mature_spread=18.0,
                root_system="Deep",
                wildlife_value="Medium",
                pollinator_friendly=True,
                deer_resistant=False,
                invasive_potential="Medium",
                suitable_for_containers=False,
                suitable_for_hedging=False,
                suitable_for_screening=True,
                suitable_for_groundcover=False,
                suitable_for_slopes=False,
            ),
            Plant(
                name="Lavandula angustifolia",
                common_name="English Lavender",
                category="Perennial",
                height_min=0.3,
                height_max=0.8,
                width_min=0.3,
                width_max=0.6,
                sun_requirements="Full Sun",
                soil_type="Sandy, well-drained",
                water_needs="Low",
                hardiness_zone="5-9",
                bloom_time="Summer",
                bloom_color="Purple",
                foliage_color="Silver-green",
                native=False,
                maintenance="Low",
                price=15.0,
                # Extended attributes
                temperature_min=-20.0,
                temperature_max=40.0,
                humidity_preference="Low",
                wind_tolerance="Medium",
                soil_ph_min=6.5,
                soil_ph_max=8.0,
                soil_drainage="Excellent",
                soil_fertility="Low",
                pruning_needs="Moderate",
                fertilizer_needs="None",
                pest_resistance="High",
                disease_resistance="High",
                plant_form="Mounding",
                foliage_texture="Fine",
                seasonal_interest="Summer flowers, fragrance",
                fragrance=True,
                growth_rate="Medium",
                mature_spread=0.5,
                root_system="Fibrous",
                wildlife_value="High",
                pollinator_friendly=True,
                deer_resistant=True,
                invasive_potential="None",
                suitable_for_containers=True,
                suitable_for_hedging=True,
                suitable_for_screening=False,
                suitable_for_groundcover=False,
                suitable_for_slopes=True,
            ),
            Plant(
                name="Buxus sempervirens",
                common_name="Common Boxwood",
                category="Shrub",
                height_min=1.0,
                height_max=4.0,
                width_min=1.0,
                width_max=4.0,
                sun_requirements="Full Sun to Partial Shade",
                soil_type="Well-drained",
                water_needs="Medium",
                hardiness_zone="5-8",
                bloom_time="Spring",
                bloom_color="Inconspicuous",
                foliage_color="Dark green",
                native=False,
                maintenance="Medium",
                price=35.0,
                # Extended attributes
                temperature_min=-25.0,
                temperature_max=35.0,
                humidity_preference="Medium",
                wind_tolerance="Medium",
                soil_ph_min=6.0,
                soil_ph_max=7.5,
                soil_drainage="Good",
                soil_fertility="Medium",
                pruning_needs="Heavy",
                fertilizer_needs="Light",
                pest_resistance="Low",
                disease_resistance="Medium",
                plant_form="Dense",
                foliage_texture="Fine",
                seasonal_interest="Evergreen foliage",
                fragrance=False,
                growth_rate="Slow",
                mature_spread=3.0,
                root_system="Shallow",
                wildlife_value="Low",
                pollinator_friendly=False,
                deer_resistant=False,
                invasive_potential="None",
                suitable_for_containers=True,
                suitable_for_hedging=True,
                suitable_for_screening=True,
                suitable_for_groundcover=False,
                suitable_for_slopes=False,
            ),
        ]

        for plant in plants:
            db.session.add(plant)

        db.session.commit()
        yield
        db.session.close()


class TestPlantRecommendationEngine:
    """Test the core recommendation engine logic"""

    def test_basic_recommendation(self, app, db_setup):
        """Test basic plant recommendation functionality"""
        with app.app_context():
            engine = PlantRecommendationEngine()

            # Create basic criteria
            criteria = RecommendationCriteria(
                hardiness_zone="5-8",
                sun_exposure="Full Sun",
                maintenance_level="Low",
                desired_height_min=0.5,
                desired_height_max=2.0,
            )

            # Get recommendations
            recommendations = engine.get_recommendations(criteria, max_results=5)

            # Should return results
            assert len(recommendations) > 0

            # Should be sorted by score
            for i in range(len(recommendations) - 1):
                assert (
                    recommendations[i].total_score >= recommendations[i + 1].total_score
                )

            # Each recommendation should have required attributes
            for rec in recommendations:
                assert hasattr(rec, "plant")
                assert hasattr(rec, "total_score")
                assert hasattr(rec, "criteria_scores")
                assert hasattr(rec, "match_reasons")
                assert hasattr(rec, "warnings")
                assert 0 <= rec.total_score <= 1

    def test_specific_criteria_matching(self, app, db_setup):
        """Test that specific criteria are matched correctly"""
        with app.app_context():
            engine = PlantRecommendationEngine()

            # Test for small plants suitable for containers
            criteria = RecommendationCriteria(
                desired_height_max=1.0, container_planting=True, maintenance_level="Low"
            )

            recommendations = engine.get_recommendations(criteria)

            # Should prioritize lavender (small, container-suitable, low maintenance)
            lavender_rec = None
            for rec in recommendations:
                if "Lavender" in rec.plant.common_name:
                    lavender_rec = rec
                    break

            assert lavender_rec is not None
            assert lavender_rec.total_score > 0.5
            assert any(
                "container" in reason.lower() for reason in lavender_rec.match_reasons
            )

    def test_native_preference(self, app, db_setup):
        """Test native plant preference scoring"""
        with app.app_context():
            engine = PlantRecommendationEngine()

            # Add a native plant
            native_plant = Plant(
                name="Quercus alba",
                common_name="White Oak",
                category="Tree",
                height_min=20.0,
                height_max=30.0,
                native=True,
                maintenance="Low",
                hardiness_zone="3-9",
            )
            db.session.add(native_plant)
            db.session.commit()

            # Test with native preference
            criteria = RecommendationCriteria(
                native_preference=True, maintenance_level="Low"
            )

            recommendations = engine.get_recommendations(criteria)

            # Native plant should score higher
            native_rec = None
            non_native_rec = None

            for rec in recommendations:
                if rec.plant.native:
                    native_rec = rec
                elif not rec.plant.native:
                    non_native_rec = rec

            if native_rec and non_native_rec:
                # Native plant should have higher special criteria score
                assert (
                    native_rec.criteria_scores["special"]
                    > non_native_rec.criteria_scores["special"]
                )

    def test_recommendation_logging(self, app, db_setup):
        """Test that recommendation requests are logged properly"""
        with app.app_context():
            engine = PlantRecommendationEngine()

            criteria = RecommendationCriteria(
                hardiness_zone="5-8", sun_exposure="Full Sun"
            )

            recommendations = engine.get_recommendations(criteria)

            # Log the request
            logged_request = engine.log_recommendation_request(
                criteria=criteria,
                results=recommendations,
                user_id="test_user",
                session_id="test_session",
            )

            assert logged_request.id is not None
            assert logged_request.hardiness_zone == "5-8"
            assert logged_request.sun_exposure == "Full Sun"
            assert logged_request.user_id == "test_user"
            assert logged_request.session_id == "test_session"
            assert logged_request.recommended_plants is not None
            assert len(logged_request.recommended_plants) == len(recommendations)

    def test_feedback_saving(self, app, db_setup):
        """Test saving user feedback"""
        with app.app_context():
            engine = PlantRecommendationEngine()

            # Create a logged request first
            criteria = RecommendationCriteria(hardiness_zone="5-8")
            recommendations = engine.get_recommendations(criteria)
            logged_request = engine.log_recommendation_request(
                criteria, recommendations
            )

            # Save feedback
            feedback = {
                "helpful": True,
                "selected_plants": [1, 2],
                "comments": "Great recommendations!",
            }

            success = engine.save_user_feedback(
                request_id=logged_request.id, feedback=feedback, rating=4
            )

            assert success

            # Verify feedback was saved
            updated_request = db.session.get(
                PlantRecommendationRequest, logged_request.id
            )
            assert updated_request.user_feedback == feedback
            assert updated_request.feedback_rating == 4


class TestPlantRecommendationAPI:
    """Test the API endpoints for plant recommendations"""

    def test_get_recommendations_endpoint(self, client, app, db_setup):
        """Test the main recommendations API endpoint"""
        with app.app_context():
            # Test request
            request_data = {
                "hardiness_zone": "5-8",
                "sun_exposure": "Full Sun",
                "maintenance_level": "Low",
                "desired_height_min": 0.5,
                "desired_height_max": 2.0,
                "max_results": 5,
            }

            response = client.post(
                "/api/plant-recommendations",
                data=json.dumps(request_data),
                content_type="application/json",
            )

            assert response.status_code == 200

            data = json.loads(response.data)
            assert "recommendations" in data
            assert "request_id" in data
            assert "criteria_summary" in data
            assert "total_plants_evaluated" in data

            # Should have recommendations
            assert len(data["recommendations"]) > 0

            # Each recommendation should have required structure
            for rec in data["recommendations"]:
                assert "plant" in rec
                assert "score" in rec
                assert "criteria_scores" in rec
                assert "match_reasons" in rec
                assert "warnings" in rec

                # Plant data should be complete
                plant = rec["plant"]
                assert "id" in plant
                assert "name" in plant
                assert "common_name" in plant

    def test_criteria_options_endpoint(self, client, app, db_setup):
        """Test the criteria options API endpoint"""
        with app.app_context():
            response = client.get("/api/plant-recommendations/criteria-options")

            assert response.status_code == 200

            data = json.loads(response.data)
            assert "hardiness_zones" in data
            assert "sun_exposures" in data
            assert "soil_types" in data
            assert "maintenance_levels" in data
            assert "budget_ranges" in data

            # Should contain expected values
            assert "Low" in data["maintenance_levels"]
            assert "Medium" in data["maintenance_levels"]
            assert "High" in data["maintenance_levels"]

    def test_feedback_endpoint(self, client, app, db_setup):
        """Test the feedback submission endpoint"""
        with app.app_context():
            # First get recommendations to get a request_id
            request_data = {"hardiness_zone": "5-8", "maintenance_level": "Low"}

            rec_response = client.post(
                "/api/plant-recommendations",
                data=json.dumps(request_data),
                content_type="application/json",
            )

            rec_data = json.loads(rec_response.data)
            request_id = rec_data["request_id"]

            # Submit feedback
            feedback_data = {
                "request_id": request_id,
                "feedback": {
                    "helpful": True,
                    "selected_plants": [1],
                    "comments": "Very helpful!",
                },
                "rating": 5,
            }

            feedback_response = client.post(
                "/api/plant-recommendations/feedback",
                data=json.dumps(feedback_data),
                content_type="application/json",
            )

            assert feedback_response.status_code == 200

            feedback_result = json.loads(feedback_response.data)
            assert "message" in feedback_result

    def test_invalid_request_handling(self, client, app, db_setup):
        """Test handling of invalid requests"""
        with app.app_context():
            # Test empty request
            response = client.post(
                "/api/plant-recommendations", data="", content_type="application/json"
            )
            assert response.status_code == 400

            # Test invalid feedback request
            feedback_response = client.post(
                "/api/plant-recommendations/feedback",
                data=json.dumps({"invalid": "data"}),
                content_type="application/json",
            )
            assert feedback_response.status_code == 400


class TestRecommendationIntegration:
    """Test integration between recommendation engine and database"""

    def test_full_workflow(self, client, app, db_setup):
        """Test complete recommendation workflow from request to feedback"""
        with app.app_context():
            # 1. Get criteria options
            options_response = client.get("/api/plant-recommendations/criteria-options")
            assert options_response.status_code == 200

            # 2. Get recommendations
            request_data = {
                "hardiness_zone": "5-8",
                "sun_exposure": "Full Sun",
                "maintenance_level": "Low",
                "native_preference": True,
                "pollinator_friendly_required": True,
            }

            rec_response = client.post(
                "/api/plant-recommendations",
                data=json.dumps(request_data),
                content_type="application/json",
            )

            assert rec_response.status_code == 200
            rec_data = json.loads(rec_response.data)

            # 3. Submit feedback
            feedback_data = {
                "request_id": rec_data["request_id"],
                "feedback": {
                    "helpful": True,
                    "improvements": "More native options would be great",
                },
                "rating": 4,
            }

            feedback_response = client.post(
                "/api/plant-recommendations/feedback",
                data=json.dumps(feedback_data),
                content_type="application/json",
            )

            assert feedback_response.status_code == 200

            # 4. Verify data persistence
            request_record = db.session.get(
                PlantRecommendationRequest, rec_data["request_id"]
            )
            assert request_record is not None
            assert request_record.feedback_rating == 4
            assert "improvements" in request_record.user_feedback
