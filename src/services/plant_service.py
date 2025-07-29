"""
Plant Service

Handles all plant-related business logic and database operations.
"""

from typing import Dict, List, Optional
from sqlalchemy import or_

from src.models.landscape import Plant
from src.models.user import db


class PlantService:
    """Service class for plant operations"""

    @staticmethod
    def get_all_plants(
        search: str = "",
        category: str = "",
        sun_exposure: str = "",
        moisture_level: str = "",
        native_only: bool = False,
        page: int = 1,
        per_page: int = 50
    ) -> Dict:
        """Get all plants with optional filtering and pagination"""
        query = Plant.query

        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Plant.name.ilike(search_term),
                    Plant.common_name.ilike(search_term)
                )
            )

        if category:
            query = query.filter(Plant.category == category)

        if sun_exposure:
            query = query.filter(Plant.sun_exposure == sun_exposure)

        if moisture_level:
            query = query.filter(Plant.moisture_level == moisture_level)

        if native_only:
            query = query.filter(Plant.native.is_(True))

        # Execute query with pagination
        plants = query.order_by(Plant.name).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            "plants": [plant.to_dict() for plant in plants.items],
            "total": plants.total,
            "pages": plants.pages,
            "current_page": plants.page,
            "per_page": plants.per_page,
        }

    @staticmethod
    def get_plant_by_id(plant_id: int) -> Optional[Plant]:
        """Get a plant by ID"""
        return Plant.query.get(plant_id)

    @staticmethod
    def create_plant(plant_data: Dict) -> Plant:
        """Create a new plant"""
        plant = Plant(**plant_data)
        db.session.add(plant)
        db.session.commit()
        return plant

    @staticmethod
    def update_plant(plant_id: int, plant_data: Dict) -> Optional[Plant]:
        """Update an existing plant"""
        plant = Plant.query.get(plant_id)
        if not plant:
            return None

        for key, value in plant_data.items():
            if hasattr(plant, key):
                setattr(plant, key, value)

        db.session.commit()
        return plant

    @staticmethod
    def delete_plant(plant_id: int) -> bool:
        """Delete a plant"""
        plant = Plant.query.get(plant_id)
        if not plant:
            return False

        db.session.delete(plant)
        db.session.commit()
        return True

    @staticmethod
    def get_plants_by_category(category: str) -> List[Plant]:
        """Get all plants in a specific category"""
        return Plant.query.filter_by(category=category).order_by(Plant.name).all()

    @staticmethod
    def search_plants(search_term: str) -> List[Plant]:
        """Search plants by name or common name"""
        search_term = f"%{search_term}%"
        return Plant.query.filter(
            or_(
                Plant.name.ilike(search_term),
                Plant.common_name.ilike(search_term)
            )
        ).order_by(Plant.name).all()

    @staticmethod
    def get_plant_categories() -> List[str]:
        """Get all unique plant categories"""
        categories = db.session.query(Plant.category).distinct().all()
        return [category[0] for category in categories if category[0]]

    @staticmethod
    def validate_plant_data(plant_data: Dict) -> List[str]:
        """Validate plant data and return list of validation errors"""
        errors = []

        # Required fields
        required_fields = ['name', 'category']
        for field in required_fields:
            if not plant_data.get(field):
                errors.append(f"{field} is required")

        # Numeric field validation
        numeric_fields = ['height_min', 'height_max', 'width_min', 'width_max', 'price']
        for field in numeric_fields:
            value = plant_data.get(field)
            if value is not None:
                try:
                    float(value)
                    if float(value) < 0:
                        errors.append(f"{field} must be non-negative")
                except (ValueError, TypeError):
                    errors.append(f"{field} must be a valid number")

        # Height/width validation
        if (plant_data.get('height_min') and plant_data.get('height_max') and 
            plant_data['height_min'] > plant_data['height_max']):
            errors.append("height_min cannot be greater than height_max")

        if (plant_data.get('width_min') and plant_data.get('width_max') and 
            plant_data['width_min'] > plant_data['width_max']):
            errors.append("width_min cannot be greater than width_max")

        # pH validation
        if plant_data.get('soil_ph_min') and plant_data.get('soil_ph_max'):
            ph_min = plant_data['soil_ph_min']
            ph_max = plant_data['soil_ph_max']
            if ph_min > ph_max:
                errors.append("soil_ph_min cannot be greater than soil_ph_max")
            if ph_min < 0 or ph_min > 14 or ph_max < 0 or ph_max > 14:
                errors.append("pH values must be between 0 and 14")

        return errors