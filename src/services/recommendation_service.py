"""
Recommendation Service
Wrapper service for plant recommendations that provides a simplified interface
"""

from typing import Dict, List

from src.services.plant_recommendation import (PlantRecommendationEngine,
                                               RecommendationCriteria)


class RecommendationService:
    """
    Service class that wraps the PlantRecommendationEngine to provide
    a simplified interface for plant recommendations
    """

    def __init__(self):
        self.engine = PlantRecommendationEngine()
        self._cache = {}

    def get_recommendations(
        self, criteria: Dict, max_results: int = 10, min_score: float = 0.0
    ) -> List[Dict]:
        """
        Get plant recommendations based on criteria

        Args:
            criteria: Dictionary with search criteria
            max_results: Maximum number of recommendations
            min_score: Minimum score threshold

        Returns:
            List of recommendation dictionaries with plant, score, reasons, and criteria_match
        """
        # Check cache first
        cache_key = self._create_cache_key(criteria, max_results, min_score)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Convert dictionary criteria to RecommendationCriteria object
        recommendation_criteria = self._convert_criteria(criteria)

        # Get recommendations from engine
        plant_scores = self.engine.get_recommendations(
            recommendation_criteria, max_results=max_results, min_score=min_score
        )

        # Convert to expected format
        recommendations = []
        for plant_score in plant_scores:
            rec = {
                "plant": self._plant_to_dict(plant_score.plant),
                "score": plant_score.total_score,
                "reasons": plant_score.match_reasons,
                "criteria_match": self._create_criteria_match(plant_score, criteria),
            }
            recommendations.append(rec)

        # Cache results
        self._cache[cache_key] = recommendations

        return recommendations

    def _convert_criteria(self, criteria: Dict) -> RecommendationCriteria:
        """Convert dictionary criteria to RecommendationCriteria object"""
        # Map between test criteria names and RecommendationCriteria fields
        field_mapping = {
            "sun_requirements": "sun_exposure",
            "plant_type": None,  # Handle separately
            "height_range": None,  # Handle separately
            "spread_range": None,  # Handle separately
            "water_requirements": "moisture_level",
            "bloom_time": "bloom_season",
        }

        kwargs = {}

        # Map simple fields
        for test_field, criteria_field in field_mapping.items():
            if test_field in criteria and criteria_field:
                kwargs[criteria_field] = criteria[test_field]

        # Handle height range
        if "height_range" in criteria and isinstance(criteria["height_range"], list):
            if len(criteria["height_range"]) >= 2:
                kwargs["desired_height_min"] = criteria["height_range"][0]
                kwargs["desired_height_max"] = criteria["height_range"][1]

        # Handle spread/width range
        if "spread_range" in criteria and isinstance(criteria["spread_range"], list):
            if len(criteria["spread_range"]) >= 2:
                kwargs["desired_width_min"] = criteria["spread_range"][0]
                kwargs["desired_width_max"] = criteria["spread_range"][1]

        # Handle other direct mappings
        direct_fields = [
            "hardiness_zone",
            "soil_type",
            "soil_ph",
            "maintenance_level",
            "budget_range",
            "native_preference",
            "wildlife_friendly",
            "deer_resistant_required",
            "pollinator_friendly_required",
            "container_planting",
            "screening_purpose",
            "hedging_purpose",
            "groundcover_purpose",
            "slope_planting",
        ]

        for field in direct_fields:
            if field in criteria:
                kwargs[field] = criteria[field]

        return RecommendationCriteria(**kwargs)

    def _plant_to_dict(self, plant) -> Dict:
        """Convert plant object to dictionary"""
        return {
            "id": plant.id,
            "name": plant.name,
            "common_name": plant.common_name,
            "plant_type": plant.category,  # Map category to plant_type
            "sun_requirements": plant.sun_requirements,
            "soil_type": plant.soil_type,
            "height_min": plant.height_min,
            "height_max": plant.height_max,
            "width_min": plant.width_min,
            "width_max": plant.width_max,
            "hardiness_zone": plant.hardiness_zone,
            "water_needs": plant.water_needs,
            "bloom_time": plant.bloom_time,
            "bloom_color": plant.bloom_color,
            "foliage_color": plant.foliage_color,
            "maintenance": plant.maintenance,
            "native": plant.native,
            "wildlife_value": plant.wildlife_value,
            "pollinator_friendly": plant.pollinator_friendly,
            "deer_resistant": plant.deer_resistant,
            "price": plant.price,
        }

    def _create_criteria_match(self, plant_score, criteria: Dict) -> Dict:
        """Create criteria match dictionary based on plant score and criteria"""
        match = {}

        # Check individual criteria matches
        if "sun_requirements" in criteria:
            match["sun_requirements"] = self._check_sun_match(
                plant_score.plant.sun_requirements, criteria["sun_requirements"]
            )

        if "soil_type" in criteria:
            match["soil_type"] = self._check_soil_match(
                plant_score.plant.soil_type, criteria["soil_type"]
            )

        if "plant_type" in criteria:
            match["plant_type"] = plant_score.plant.category == criteria["plant_type"]

        if "height_range" in criteria:
            match["height_range"] = self._check_height_match(
                plant_score.plant.height_min,
                plant_score.plant.height_max,
                criteria["height_range"],
            )

        if "hardiness_zone" in criteria:
            match["hardiness_zone"] = self._check_hardiness_match(
                plant_score.plant.hardiness_zone, criteria["hardiness_zone"]
            )

        return match

    def _check_sun_match(self, plant_sun: str, criteria_sun: str) -> bool:
        """Check if sun requirements match"""
        if not plant_sun or not criteria_sun:
            return False
        return plant_sun.lower() == criteria_sun.lower()

    def _check_soil_match(self, plant_soil: str, criteria_soil: str) -> bool:
        """Check if soil types match"""
        if not plant_soil or not criteria_soil:
            return False
        # Split soil types into sets of individual components
        plant_soil_set = set(soil.strip().lower() for soil in plant_soil.split(","))
        criteria_soil_set = set(
            soil.strip().lower() for soil in criteria_soil.split(",")
        )
        # Check for any intersection between the two sets
        return not plant_soil_set.isdisjoint(criteria_soil_set)

    def _check_height_match(
        self, plant_min: float, plant_max: float, height_range: List
    ) -> bool:
        """Check if height ranges overlap"""
        if not plant_min or not plant_max or not height_range or len(height_range) < 2:
            return False

        criteria_min, criteria_max = height_range[0], height_range[1]

        # Check if ranges overlap
        return not (criteria_max < plant_min or criteria_min > plant_max)

    def _check_hardiness_match(self, plant_zone: str, criteria_zone: str) -> bool:
        """Check if hardiness zones overlap"""
        if not plant_zone or not criteria_zone:
            return False

        try:
            # Parse zones like "5-9" or "6-8"
            plant_min, plant_max = map(int, plant_zone.split("-"))
            criteria_min, criteria_max = map(int, criteria_zone.split("-"))

            # Check if zones overlap
            return not (criteria_max < plant_min or criteria_min > plant_max)
        except (ValueError, AttributeError):
            # Fallback to string comparison if parsing fails
            return plant_zone == criteria_zone

    def _create_cache_key(
        self, criteria: Dict, max_results: int, min_score: float
    ) -> str:
        """Create cache key from criteria"""
        import json

        criteria_str = json.dumps(criteria, sort_keys=True)
        return f"{criteria_str}_{max_results}_{min_score}"
