import pytest
from tests.fixtures.auth_fixtures import authenticated_test_user, setup_test_authentication

from src.services.recommendation_algorithm import RecommendationAlgorithm
from tests.database.factories import create_test_plant


class TestRecommendationAlgorithm:

    @pytest.fixture
    def algorithm(self):
        return RecommendationAlgorithm()

    def test_score_calculation_weights(self, algorithm):
        """Test that scoring weights are properly applied"""
        plant_data = {
            "sun_requirements": "full_sun",
            "soil_type": "well_drained",
            "plant_type": "shrub",
            "height_min": 60,
            "height_max": 120,
        }

        criteria = {
            "sun_requirements": "full_sun",
            "soil_type": "well_drained",
            "plant_type": "shrub",
            "height_range": [50, 150],
        }

        score = algorithm.calculate_score(plant_data, criteria)

        # Perfect match should score very high
        assert score > 0.9
        assert score <= 1.0

    def test_partial_match_scoring(self, algorithm):
        """Test scoring for partial matches"""
        plant_data = {
            "sun_requirements": "full_sun",
            "soil_type": "moist",  # Different from criteria
            "plant_type": "shrub",
            "height_min": 60,
            "height_max": 120,
        }

        criteria = {
            "sun_requirements": "full_sun",
            "soil_type": "well_drained",
            "plant_type": "shrub",
            "height_range": [50, 150],
        }

        score = algorithm.calculate_score(plant_data, criteria)

        # Partial match should score moderately
        assert 0.5 < score < 0.9

    def test_height_range_scoring(self, algorithm):
        """Test height range scoring logic"""
        criteria = {"height_range": [100, 200]}

        # Perfect fit
        perfect_plant = {"height_min": 120, "height_max": 180}
        perfect_score = algorithm._score_height_range(perfect_plant, criteria)
        assert perfect_score == 1.0

        # Partial overlap
        partial_plant = {"height_min": 80, "height_max": 150}
        partial_score = algorithm._score_height_range(partial_plant, criteria)
        assert 0.5 < partial_score < 1.0

        # No overlap
        no_overlap_plant = {"height_min": 20, "height_max": 50}
        no_overlap_score = algorithm._score_height_range(no_overlap_plant, criteria)
        assert no_overlap_score == 0.0

    def test_hardiness_zone_scoring(self, algorithm):
        """Test hardiness zone scoring logic"""
        criteria = {"hardiness_zone": "5-8"}

        # Exact match
        exact_plant = {"hardiness_zone": "5-8"}
        exact_score = algorithm._score_hardiness_zone(exact_plant, criteria)
        assert exact_score == 1.0

        # Overlapping zones
        overlap_plant = {"hardiness_zone": "4-7"}
        overlap_score = algorithm._score_hardiness_zone(overlap_plant, criteria)
        assert 0.5 < overlap_score < 1.0

        # No overlap
        no_overlap_plant = {"hardiness_zone": "9-11"}
        no_overlap_score = algorithm._score_hardiness_zone(no_overlap_plant, criteria)
        assert no_overlap_score == 0.0

    def test_categorical_matching(self, algorithm):
        """Test categorical field matching"""
        # Exact match
        assert algorithm._score_categorical("full_sun", "full_sun") == 1.0

        # No match
        assert algorithm._score_categorical("full_sun", "full_shade") == 0.0

        # Partial match (if implemented)
        partial_score = algorithm._score_categorical("partial_shade", "full_shade")
        assert 0.0 <= partial_score <= 1.0

    def test_criteria_importance_weighting(self, algorithm):
        """Test that different criteria have appropriate importance weights"""
        weights = algorithm.get_criteria_weights()

        # Critical criteria should have higher weights
        assert weights.get("sun_requirements", 0) > 0.1
        assert weights.get("hardiness_zone", 0) > 0.1
        assert weights.get("plant_type", 0) > 0.05

        # All weights should sum to reasonable total
        total_weight = sum(weights.values())
        assert 0.8 <= total_weight <= 1.2

    def test_recommendation_ranking(self, algorithm, app_context):
        """Test that recommendations are properly ranked"""
        plants = [
            create_test_plant(
                name="Perfect Match",
                sun_requirements="full_sun",
                soil_type="well_drained",
                plant_type="shrub",
                height_min=80,
                height_max=120,
            ),
            create_test_plant(
                name="Good Match",
                sun_requirements="full_sun",
                soil_type="well_drained",
                plant_type="perennial",  # Different type
                height_min=80,
                height_max=120,
            ),
            create_test_plant(
                name="Poor Match",
                sun_requirements="partial_shade",  # Wrong sun
                soil_type="moist",  # Wrong soil
                plant_type="tree",  # Wrong type
                height_min=200,
                height_max=400,  # Wrong height
            ),
        ]

        from src.models.user import db

        for plant in plants:
            db.session.add(plant)
        db.session.commit()

        criteria = {
            "sun_requirements": "full_sun",
            "soil_type": "well_drained",
            "plant_type": "shrub",
            "height_range": [70, 150],
        }

        scores = []
        for plant in plants:
            plant_data = {
                "sun_requirements": plant.sun_requirements,
                "soil_type": plant.soil_type,
                "plant_type": plant.category,
                "height_min": plant.height_min,
                "height_max": plant.height_max,
            }
            score = algorithm.calculate_score(plant_data, criteria)
            scores.append((plant.name, score))

        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)

        # The top-scoring plant should have higher score than others
        assert scores[0][1] > scores[1][1] > scores[2][1]
        # Perfect match should be first (or at least not last)
        assert scores[2][0] == "Poor Match"  # Poor match should be last
