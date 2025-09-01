"""
Recommendation Algorithm
Core algorithm logic for scoring and ranking plant recommendations
"""

from typing import Dict


class RecommendationAlgorithm:
    """
    Core algorithm class for plant recommendation scoring
    """

    def __init__(self):
        self.criteria_weights = {
            "sun_requirements": 0.25,
            "soil_type": 0.20,
            "plant_type": 0.15,
            "height_range": 0.15,
            "hardiness_zone": 0.20,
            "water_requirements": 0.05,
        }

    def calculate_score(self, plant_data: Dict, criteria: Dict) -> float:
        """
        Calculate overall compatibility score for a plant against criteria

        Args:
            plant_data: Dictionary with plant attributes
            criteria: Dictionary with search criteria

        Returns:
            Float score between 0.0 and 1.0
        """
        total_score = 0.0
        total_weight = 0.0

        # Score each criterion that exists in both plant and criteria
        for criterion, weight in self.criteria_weights.items():
            if criterion in criteria:
                if criterion == "height_range":
                    score = self._score_height_range(plant_data, criteria)
                elif criterion == "hardiness_zone":
                    score = self._score_hardiness_zone(plant_data, criteria)
                elif criterion in [
                    "sun_requirements",
                    "soil_type",
                    "plant_type",
                    "water_requirements",
                ]:
                    plant_value = plant_data.get(criterion)
                    criteria_value = criteria.get(criterion)
                    score = self._score_categorical(plant_value, criteria_value)
                else:
                    continue

                total_score += score * weight
                total_weight += weight

        # Return normalized score
        return total_score / total_weight if total_weight > 0 else 0.0

    def _score_height_range(self, plant_data: Dict, criteria: Dict) -> float:
        """Score height range compatibility"""
        height_range = criteria.get("height_range")
        if not height_range or len(height_range) < 2:
            return 1.0

        plant_min = plant_data.get("height_min")
        plant_max = plant_data.get("height_max")

        if plant_min is None or plant_max is None:
            return 0.5

        criteria_min, criteria_max = height_range[0], height_range[1]

        # Perfect overlap
        if criteria_min <= plant_min and plant_max <= criteria_max:
            return 1.0

        # Plant completely within criteria range
        if plant_min <= criteria_max and plant_max >= criteria_min:
            # Calculate overlap percentage
            overlap_min = max(plant_min, criteria_min)
            overlap_max = min(plant_max, criteria_max)
            overlap = overlap_max - overlap_min

            plant_range = plant_max - plant_min
            criteria_range = criteria_max - criteria_min

            if plant_range > 0 and criteria_range > 0:
                overlap_ratio = overlap / min(plant_range, criteria_range)
                return max(0.5, overlap_ratio)

        # No overlap
        return 0.0

    def _score_hardiness_zone(self, plant_data: Dict, criteria: Dict) -> float:
        """Score hardiness zone compatibility"""
        plant_zone = plant_data.get("hardiness_zone")
        criteria_zone = criteria.get("hardiness_zone")

        if not plant_zone or not criteria_zone:
            return 0.5

        try:
            # Parse zones like "5-9" or "6-8"
            plant_min, plant_max = map(int, plant_zone.split("-"))
            criteria_min, criteria_max = map(int, criteria_zone.split("-"))

            # Perfect match
            if plant_min == criteria_min and plant_max == criteria_max:
                return 1.0

            # Check overlap
            if plant_min <= criteria_max and plant_max >= criteria_min:
                # Calculate overlap score
                overlap_min = max(plant_min, criteria_min)
                overlap_max = min(plant_max, criteria_max)
                overlap = (
                    overlap_max - overlap_min + 1
                )  # +1 because zones are inclusive

                plant_range = plant_max - plant_min + 1
                criteria_range = criteria_max - criteria_min + 1

                overlap_ratio = overlap / min(plant_range, criteria_range)
                return max(0.6, overlap_ratio)

            # No overlap
            return 0.0

        except (ValueError, AttributeError):
            # Fallback to string comparison
            return 1.0 if plant_zone == criteria_zone else 0.0

    def _score_categorical(self, plant_value: str, criteria_value: str) -> float:
        """Score categorical field matches"""
        if not plant_value or not criteria_value:
            return 0.5

        # Exact match
        if plant_value.lower() == criteria_value.lower():
            return 1.0

        # Partial matches for sun requirements
        if self._is_sun_requirement_field(plant_value, criteria_value):
            return self._score_sun_compatibility(plant_value, criteria_value)

        # Partial matches for soil type
        if self._is_soil_field(plant_value, criteria_value):
            if criteria_value.lower() in plant_value.lower():
                return 0.8
            return 0.3

        # No match
        return 0.0

    def _is_sun_requirement_field(self, plant_value: str, criteria_value: str) -> bool:
        """Check if values are sun requirement related"""
        sun_values = ["full_sun", "partial_shade", "full_shade", "partial_sun"]
        return (
            plant_value.lower().replace(" ", "_") in sun_values
            or criteria_value.lower().replace(" ", "_") in sun_values
        )

    def _is_soil_field(self, plant_value: str, criteria_value: str) -> bool:
        """Check if values are soil type related"""
        soil_values = ["well_drained", "moist", "wet", "dry", "sandy", "clay", "loam"]
        return any(
            soil in plant_value.lower() or soil in criteria_value.lower()
            for soil in soil_values
        )

    def _score_sun_compatibility(self, plant_sun: str, criteria_sun: str) -> float:
        """Score sun requirement compatibility with partial matches"""
        sun_compatibility = {
            "full_sun": {
                "full_sun": 1.0,
                "partial_sun": 0.7,
                "partial_shade": 0.3,
                "full_shade": 0.0,
            },
            "partial_sun": {
                "full_sun": 0.7,
                "partial_sun": 1.0,
                "partial_shade": 0.8,
                "full_shade": 0.3,
            },
            "partial_shade": {
                "full_sun": 0.3,
                "partial_sun": 0.8,
                "partial_shade": 1.0,
                "full_shade": 0.7,
            },
            "full_shade": {
                "full_sun": 0.0,
                "partial_sun": 0.3,
                "partial_shade": 0.7,
                "full_shade": 1.0,
            },
        }

        plant_key = plant_sun.lower().replace(" ", "_")
        criteria_key = criteria_sun.lower().replace(" ", "_")

        if (
            plant_key in sun_compatibility
            and criteria_key in sun_compatibility[plant_key]
        ):
            return sun_compatibility[plant_key][criteria_key]

        return 0.5  # Default for unknown combinations

    def get_criteria_weights(self) -> Dict[str, float]:
        """Get the criteria importance weights"""
        return self.criteria_weights.copy()
