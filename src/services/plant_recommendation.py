"""
Plant Recommendation Engine Service

Implements a multi-criteria weighted algorithm for plant recommendations
based on environmental conditions, design requirements, and project context.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from src.models.landscape import Plant, PlantRecommendationRequest
from src.models.user import db


@dataclass
class RecommendationCriteria:
    """Data class for recommendation criteria with weights"""

    # Environmental criteria
    hardiness_zone: Optional[str] = None
    sun_exposure: Optional[str] = None
    soil_type: Optional[str] = None
    soil_ph: Optional[float] = None
    moisture_level: Optional[str] = None

    # Design criteria
    desired_height_min: Optional[float] = None
    desired_height_max: Optional[float] = None
    desired_width_min: Optional[float] = None
    desired_width_max: Optional[float] = None
    color_preferences: Optional[List[str]] = None
    bloom_season: Optional[str] = None

    # Maintenance criteria
    maintenance_level: Optional[str] = None
    budget_range: Optional[str] = None

    # Special requirements
    native_preference: bool = False
    wildlife_friendly: bool = False
    deer_resistant_required: bool = False
    pollinator_friendly_required: bool = False

    # Project context
    container_planting: bool = False
    screening_purpose: bool = False
    hedging_purpose: bool = False
    groundcover_purpose: bool = False
    slope_planting: bool = False

    # Criteria weights (sum should be 1.0)
    weights: Dict[str, float] = None

    def __post_init__(self):
        if self.weights is None:
            self.weights = {
                "environmental": 0.30,  # Climate, soil, hardiness
                "design": 0.25,  # Size, color, aesthetics
                "maintenance": 0.20,  # Care requirements, budget
                "special": 0.15,  # Native, wildlife, etc.
                "context": 0.10,  # Project specific needs
            }

        if self.color_preferences is None:
            self.color_preferences = []


@dataclass
class PlantScore:
    """Data class for plant recommendation scores"""

    plant: Plant
    total_score: float
    criteria_scores: Dict[str, float]
    match_reasons: List[str]
    warnings: List[str]


class PlantRecommendationEngine:
    """
    Multi-criteria plant recommendation engine using weighted scoring algorithm
    """

    def __init__(self):
        # Value mappings for categorical attributes
        self.sun_exposure_map = {
            "full_sun": ["Full Sun", "Full sun"],
            "partial_sun": ["Partial Sun", "Partial sun", "Part Sun"],
            "partial_shade": ["Partial Shade", "Partial shade", "Part Shade"],
            "full_shade": ["Shade", "Full Shade", "Full shade"],
        }

        self.maintenance_map = {
            "low": ["Low", "Easy", "Minimal"],
            "medium": ["Medium", "Moderate", "Average"],
            "high": ["High", "Intensive", "Regular"],
        }

        self.moisture_map = {
            "low": ["Low", "Dry", "Drought"],
            "medium": ["Medium", "Moderate", "Average"],
            "high": ["High", "Moist", "Wet"],
        }

    def get_recommendations(
        self,
        criteria: RecommendationCriteria,
        max_results: int = 10,
        min_score: float = 0.5,
    ) -> List[PlantScore]:
        """
        Get plant recommendations based on criteria

        Args:
            criteria: RecommendationCriteria object with search parameters
            max_results: Maximum number of recommendations to return
            min_score: Minimum score threshold for recommendations

        Returns:
            List of PlantScore objects sorted by score (highest first)
        """
        # Get all plants from database
        plants = Plant.query.all()

        if not plants:
            return []

        # Score each plant against criteria
        scored_plants = []
        for plant in plants:
            score = self._score_plant(plant, criteria)
            if score.total_score >= min_score:
                scored_plants.append(score)

        # Sort by total score (descending) and return top results
        scored_plants.sort(key=lambda x: x.total_score, reverse=True)
        return scored_plants[:max_results]

    def _score_plant(self, plant: Plant, criteria: RecommendationCriteria) -> PlantScore:
        """
        Score a single plant against the criteria

        Args:
            plant: Plant object to score
            criteria: RecommendationCriteria to match against

        Returns:
            PlantScore object with detailed scoring information
        """
        criteria_scores = {}
        match_reasons = []
        warnings = []

        # Environmental scoring
        env_score = self._score_environmental(plant, criteria, match_reasons, warnings)
        criteria_scores["environmental"] = env_score

        # Design scoring
        design_score = self._score_design(plant, criteria, match_reasons, warnings)
        criteria_scores["design"] = design_score

        # Maintenance scoring
        maintenance_score = self._score_maintenance(plant, criteria, match_reasons, warnings)
        criteria_scores["maintenance"] = maintenance_score

        # Special requirements scoring
        special_score = self._score_special(plant, criteria, match_reasons, warnings)
        criteria_scores["special"] = special_score

        # Context scoring
        context_score = self._score_context(plant, criteria, match_reasons, warnings)
        criteria_scores["context"] = context_score

        # Calculate weighted total score
        total_score = (
            criteria_scores["environmental"] * criteria.weights["environmental"]
            + criteria_scores["design"] * criteria.weights["design"]
            + criteria_scores["maintenance"] * criteria.weights["maintenance"]
            + criteria_scores["special"] * criteria.weights["special"]
            + criteria_scores["context"] * criteria.weights["context"]
        )

        return PlantScore(
            plant=plant,
            total_score=total_score,
            criteria_scores=criteria_scores,
            match_reasons=match_reasons,
            warnings=warnings,
        )

    def _score_environmental(
        self,
        plant: Plant,
        criteria: RecommendationCriteria,
        match_reasons: List[str],
        warnings: List[str],
    ) -> float:
        """Score environmental compatibility"""
        score = 0.0
        total_factors = 0

        # Hardiness zone matching
        if criteria.hardiness_zone and plant.hardiness_zone:
            total_factors += 1
            if criteria.hardiness_zone in plant.hardiness_zone:
                score += 1.0
                match_reasons.append(f"Compatible hardiness zone ({plant.hardiness_zone})")
            else:
                warnings.append(
                    f"Hardiness zone mismatch: plant {plant.hardiness_zone}, " f"site {criteria.hardiness_zone}"
                )

        # Sun exposure matching
        if criteria.sun_exposure and plant.sun_requirements:
            total_factors += 1
            if self._match_sun_exposure(criteria.sun_exposure, plant.sun_requirements):
                score += 1.0
                match_reasons.append(f"Suitable sun exposure ({plant.sun_requirements})")
            else:
                score += 0.3  # Partial compatibility
                warnings.append(
                    f"Sun exposure concern: plant needs {plant.sun_requirements}, " f"site has {criteria.sun_exposure}"
                )

        # Soil type matching
        if criteria.soil_type and plant.soil_type:
            total_factors += 1
            if criteria.soil_type.lower() in plant.soil_type.lower():
                score += 1.0
                match_reasons.append(f"Compatible soil type ({plant.soil_type})")
            else:
                score += 0.5  # Different but possibly compatible

        # Soil pH matching
        if criteria.soil_ph and plant.soil_ph_min and plant.soil_ph_max:
            total_factors += 1
            if plant.soil_ph_min <= criteria.soil_ph <= plant.soil_ph_max:
                score += 1.0
                match_reasons.append(f"Compatible pH ({plant.soil_ph_min}-{plant.soil_ph_max})")
            else:
                score += 0.2
                warnings.append(
                    f"pH concern: plant prefers {plant.soil_ph_min}-" f"{plant.soil_ph_max}, site is {criteria.soil_ph}"
                )

        # Moisture level matching
        if criteria.moisture_level and plant.water_needs:
            total_factors += 1
            if self._match_moisture_level(criteria.moisture_level, plant.water_needs):
                score += 1.0
                match_reasons.append(f"Compatible water needs ({plant.water_needs})")
            else:
                score += 0.4
                warnings.append(
                    f"Water needs mismatch: plant needs {plant.water_needs}, " f"site has {criteria.moisture_level}"
                )

        return score / total_factors if total_factors > 0 else 0.5

    def _score_design(
        self,
        plant: Plant,
        criteria: RecommendationCriteria,
        match_reasons: List[str],
        warnings: List[str],
    ) -> float:
        """Score design compatibility"""
        score = 0.0
        total_factors = 0

        # Height matching
        if (criteria.desired_height_min is not None or criteria.desired_height_max is not None) and (
            plant.height_min is not None or plant.height_max is not None
        ):
            total_factors += 1

            plant_height_avg = self._get_average_size(plant.height_min, plant.height_max)
            criteria_height_avg = self._get_average_range(criteria.desired_height_min, criteria.desired_height_max)

            if self._size_compatible(
                criteria.desired_height_min,
                criteria.desired_height_max,
                plant.height_min,
                plant.height_max,
            ):
                score += 1.0
                match_reasons.append(f"Suitable height ({plant.height_min}-{plant.height_max}m)")
            elif abs(plant_height_avg - criteria_height_avg) <= 1.0:  # Within 1m tolerance
                score += 0.7
                match_reasons.append(f"Close height match ({plant.height_min}-{plant.height_max}m)")
            else:
                score += 0.3
                warnings.append(
                    f"Height difference: plant {plant.height_min}-{plant.height_max}m, "
                    f"desired {criteria.desired_height_min}-"
                    f"{criteria.desired_height_max}m"
                )

        # Width matching
        if (criteria.desired_width_min is not None or criteria.desired_width_max is not None) and (
            plant.width_min is not None or plant.width_max is not None
        ):
            total_factors += 1

            if self._size_compatible(
                criteria.desired_width_min,
                criteria.desired_width_max,
                plant.width_min,
                plant.width_max,
            ):
                score += 1.0
                match_reasons.append(f"Suitable width ({plant.width_min}-{plant.width_max}m)")
            else:
                score += 0.4

        # Color preferences
        if criteria.color_preferences and (plant.bloom_color or plant.foliage_color):
            total_factors += 1
            color_match = False
            for pref_color in criteria.color_preferences:
                if (plant.bloom_color and pref_color.lower() in plant.bloom_color.lower()) or (
                    plant.foliage_color and pref_color.lower() in plant.foliage_color.lower()
                ):
                    color_match = True
                    match_reasons.append(f"Matching color preference ({pref_color})")
                    break

            score += 1.0 if color_match else 0.3

        # Bloom season matching
        if criteria.bloom_season and plant.bloom_time:
            total_factors += 1
            if criteria.bloom_season.lower() in plant.bloom_time.lower():
                score += 1.0
                match_reasons.append(f"Blooms in desired season ({plant.bloom_time})")
            else:
                score += 0.5

        return score / total_factors if total_factors > 0 else 0.5

    def _score_maintenance(
        self,
        plant: Plant,
        criteria: RecommendationCriteria,
        match_reasons: List[str],
        warnings: List[str],
    ) -> float:
        """Score maintenance compatibility"""
        score = 0.0
        total_factors = 0

        # Maintenance level matching
        if criteria.maintenance_level and plant.maintenance:
            total_factors += 1
            if self._match_maintenance_level(criteria.maintenance_level, plant.maintenance):
                score += 1.0
                match_reasons.append(f"Suitable maintenance level ({plant.maintenance})")
            else:
                score += 0.4
                warnings.append(
                    f"Maintenance mismatch: plant needs {plant.maintenance}, "
                    f"preference is {criteria.maintenance_level}"
                )

        # Budget considerations (simplified)
        if criteria.budget_range and plant.price:
            total_factors += 1
            budget_compatible = self._check_budget_compatibility(criteria.budget_range, plant.price)
            if budget_compatible:
                score += 1.0
                match_reasons.append(f"Within budget (${plant.price})")
            else:
                score += 0.2
                warnings.append(f"Price concern: ${plant.price} may exceed " f"{criteria.budget_range} budget")

        # Pest and disease resistance
        if plant.pest_resistance or plant.disease_resistance:
            total_factors += 1
            resistance_score = 0
            if plant.pest_resistance and plant.pest_resistance.lower() in [
                "high",
                "medium",
            ]:
                resistance_score += 0.5
                match_reasons.append(f"Good pest resistance ({plant.pest_resistance})")
            if plant.disease_resistance and plant.disease_resistance.lower() in [
                "high",
                "medium",
            ]:
                resistance_score += 0.5
                match_reasons.append(f"Good disease resistance ({plant.disease_resistance})")
            score += resistance_score

        return score / total_factors if total_factors > 0 else 0.5

    def _score_special(
        self,
        plant: Plant,
        criteria: RecommendationCriteria,
        match_reasons: List[str],
        warnings: List[str],
    ) -> float:
        """Score special requirements"""
        score = 0.0
        total_factors = 0

        # Native preference
        if criteria.native_preference:
            total_factors += 1
            if plant.native:
                score += 1.0
                match_reasons.append("Native plant species")
            else:
                score += 0.3
                warnings.append("Not a native species")

        # Wildlife friendly
        if criteria.wildlife_friendly:
            total_factors += 1
            if plant.wildlife_value and plant.wildlife_value.lower() in [
                "high",
                "medium",
            ]:
                score += 1.0
                match_reasons.append(f"Good wildlife value ({plant.wildlife_value})")
            else:
                score += 0.4

        # Deer resistant requirement
        if criteria.deer_resistant_required:
            total_factors += 1
            if plant.deer_resistant:
                score += 1.0
                match_reasons.append("Deer resistant")
            else:
                score += 0.1
                warnings.append("Not deer resistant")

        # Pollinator friendly requirement
        if criteria.pollinator_friendly_required:
            total_factors += 1
            if plant.pollinator_friendly:
                score += 1.0
                match_reasons.append("Pollinator friendly")
            else:
                score += 0.2
                warnings.append("Limited pollinator value")

        return score / total_factors if total_factors > 0 else 1.0

    def _score_context(
        self,
        plant: Plant,
        criteria: RecommendationCriteria,
        match_reasons: List[str],
        warnings: List[str],
    ) -> float:
        """Score project context compatibility"""
        score = 0.0
        total_factors = 0

        # Container planting
        if criteria.container_planting:
            total_factors += 1
            if plant.suitable_for_containers:
                score += 1.0
                match_reasons.append("Suitable for containers")
            else:
                score += 0.3
                warnings.append("May not be ideal for containers")

        # Screening purpose
        if criteria.screening_purpose:
            total_factors += 1
            if plant.suitable_for_screening:
                score += 1.0
                match_reasons.append("Good for screening")
            else:
                score += 0.4

        # Hedging purpose
        if criteria.hedging_purpose:
            total_factors += 1
            if plant.suitable_for_hedging:
                score += 1.0
                match_reasons.append("Suitable for hedging")
            else:
                score += 0.3

        # Groundcover purpose
        if criteria.groundcover_purpose:
            total_factors += 1
            if plant.suitable_for_groundcover:
                score += 1.0
                match_reasons.append("Good groundcover option")
            else:
                score += 0.2

        # Slope planting
        if criteria.slope_planting:
            total_factors += 1
            if plant.suitable_for_slopes:
                score += 1.0
                match_reasons.append("Suitable for slopes")
            else:
                score += 0.4

        return score / total_factors if total_factors > 0 else 1.0

    # Helper methods
    def _match_sun_exposure(self, criteria_sun: str, plant_sun: str) -> bool:
        """Check if sun exposure requirements match"""
        criteria_normalized = criteria_sun.lower().replace(" ", "_")
        for key, values in self.sun_exposure_map.items():
            if criteria_normalized in key or any(criteria_sun in val for val in values):
                return any(val in plant_sun for val in values)
        return criteria_sun.lower() in plant_sun.lower()

    def _match_maintenance_level(self, criteria_maintenance: str, plant_maintenance: str) -> bool:
        """Check if maintenance levels match"""
        criteria_normalized = criteria_maintenance.lower()
        for key, values in self.maintenance_map.items():
            if criteria_normalized in key or any(criteria_maintenance in val for val in values):
                return any(val.lower() in plant_maintenance.lower() for val in values)
        return criteria_maintenance.lower() in plant_maintenance.lower()

    def _match_moisture_level(self, criteria_moisture: str, plant_water: str) -> bool:
        """Check if moisture levels match"""
        criteria_normalized = criteria_moisture.lower()
        for key, values in self.moisture_map.items():
            if criteria_normalized in key or any(criteria_moisture in val for val in values):
                return any(val.lower() in plant_water.lower() for val in values)
        return criteria_moisture.lower() in plant_water.lower()

    def _size_compatible(
        self,
        criteria_min: Optional[float],
        criteria_max: Optional[float],
        plant_min: Optional[float],
        plant_max: Optional[float],
    ) -> bool:
        """Check if size ranges are compatible"""
        if not any([criteria_min, criteria_max, plant_min, plant_max]):
            return True

        criteria_min = criteria_min or 0
        criteria_max = criteria_max or float("inf")
        plant_min = plant_min or 0
        plant_max = plant_max or float("inf")

        # Check if ranges overlap
        return not (criteria_max < plant_min or criteria_min > plant_max)

    def _get_average_size(self, min_val: Optional[float], max_val: Optional[float]) -> float:
        """Get average of min/max values"""
        if min_val is not None and max_val is not None:
            return (min_val + max_val) / 2
        elif min_val is not None:
            return min_val
        elif max_val is not None:
            return max_val
        else:
            return 0

    def _get_average_range(self, min_val: Optional[float], max_val: Optional[float]) -> float:
        """Get average of criteria range"""
        if min_val is not None and max_val is not None:
            return (min_val + max_val) / 2
        elif min_val is not None:
            return min_val
        elif max_val is not None:
            return max_val
        else:
            return 0

    def _check_budget_compatibility(self, budget_range: str, plant_price: float) -> bool:
        """Check if plant price fits within budget range"""
        budget_map = {
            "low": (0, 50),
            "medium": (25, 150),
            "high": (100, 500),
            "premium": (300, float("inf")),
        }

        range_key = budget_range.lower()
        if range_key in budget_map:
            min_budget, max_budget = budget_map[range_key]
            return min_budget <= plant_price <= max_budget

        return True  # If budget range not recognized, assume compatible

    def log_recommendation_request(
        self,
        criteria: RecommendationCriteria,
        results: List[PlantScore],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> PlantRecommendationRequest:
        """
        Log a recommendation request for analytics and learning

        Args:
            criteria: The recommendation criteria used
            results: The recommendation results
            user_id: Optional user identifier
            session_id: Optional session identifier
            ip_address: Optional IP address for analytics

        Returns:
            PlantRecommendationRequest object that was saved
        """
        # Create recommendation request record
        request = PlantRecommendationRequest(
            project_type=getattr(criteria, "project_type", None),
            hardiness_zone=criteria.hardiness_zone,
            sun_exposure=criteria.sun_exposure,
            soil_type=criteria.soil_type,
            soil_ph=criteria.soil_ph,
            moisture_level=criteria.moisture_level,
            desired_height_min=criteria.desired_height_min,
            desired_height_max=criteria.desired_height_max,
            desired_width_min=criteria.desired_width_min,
            desired_width_max=criteria.desired_width_max,
            color_preferences=(",".join(criteria.color_preferences) if criteria.color_preferences else None),
            bloom_season=criteria.bloom_season,
            maintenance_level=criteria.maintenance_level,
            budget_range=criteria.budget_range,
            native_preference=criteria.native_preference,
            wildlife_friendly=criteria.wildlife_friendly,
            deer_resistant_required=criteria.deer_resistant_required,
            pollinator_friendly_required=criteria.pollinator_friendly_required,
            container_planting=criteria.container_planting,
            screening_purpose=criteria.screening_purpose,
            hedging_purpose=criteria.hedging_purpose,
            groundcover_purpose=criteria.groundcover_purpose,
            slope_planting=criteria.slope_planting,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            recommended_plants=[
                {
                    "plant_id": result.plant.id,
                    "plant_name": result.plant.name,
                    "total_score": result.total_score,
                    "criteria_scores": result.criteria_scores,
                    "match_reasons": result.match_reasons,
                    "warnings": result.warnings,
                }
                for result in results
            ],
        )

        try:
            db.session.add(request)
            db.session.commit()
            return request
        except Exception as e:
            db.session.rollback()
            raise e

    def save_user_feedback(self, request_id: int, feedback: Dict, rating: Optional[int] = None) -> bool:
        """
        Save user feedback for a recommendation request

        Args:
            request_id: ID of the recommendation request
            feedback: Dictionary containing user feedback
            rating: Optional overall rating (1-5)

        Returns:
            True if feedback was saved successfully
        """
        try:
            request = db.session.get(PlantRecommendationRequest, request_id)
            if request:
                request.user_feedback = feedback
                if rating is not None:
                    request.feedback_rating = rating
                db.session.commit()
                return True
            return False
        except Exception:
            db.session.rollback()
            return False
