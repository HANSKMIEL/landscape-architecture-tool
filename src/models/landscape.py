from datetime import datetime
from typing import Any, Sequence, cast

from src.models.user import db


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    specialization = db.Column(db.String(200))
    website = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = db.relationship("Product", backref="supplier", lazy=True, cascade="all, delete-orphan")
    plants = db.relationship("Plant", backref="supplier", lazy=True)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def to_dict(self):
        products = cast(Sequence[Any], self.products or [])
        return {
            "id": self.id,
            "name": self.name,
            "contact_person": self.contact_person,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "specialization": self.specialization,
            "website": self.website,
            "notes": self.notes,
            "product_count": len(products),
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    unit = db.Column(db.String(20))
    sku = db.Column(db.String(50))
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"))
    stock_quantity = db.Column(db.Integer, default=0)
    weight = db.Column(db.Float)
    dimensions = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    photos = db.relationship("Photo", foreign_keys="Photo.material_id", back_populates="material", lazy=True)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def to_dict(self):
        supplier = cast("Supplier | None", getattr(self, "supplier", None))
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "price": self.price,
            "unit": self.unit,
            "sku": self.sku,
            "supplier_id": self.supplier_id,
            "supplier_name": supplier.name if supplier else None,
            "stock_quantity": self.stock_quantity,
            "weight": self.weight,
            "dimensions": self.dimensions,
            "notes": self.notes,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }


class Plant(db.Model):
    __tablename__ = "plants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    common_name = db.Column(db.String(200))
    category = db.Column(db.String(50))  # Tree, Shrub, Perennial, Annual, etc.

    # Size attributes
    height_min = db.Column(db.Float)
    height_max = db.Column(db.Float)
    width_min = db.Column(db.Float)
    width_max = db.Column(db.Float)

    # Basic care requirements
    sun_requirements = db.Column(db.String(50))
    sun_exposure = db.Column(db.String(50))
    soil_type = db.Column(db.String(100))
    water_needs = db.Column(db.String(50))
    moisture_level = db.Column(db.String(50))
    hardiness_zone = db.Column(db.String(20))
    bloom_time = db.Column(db.String(100))
    bloom_color = db.Column(db.String(100))
    foliage_color = db.Column(db.String(100))
    native = db.Column(db.Boolean, default=False)

    # Extended climate attributes
    temperature_min = db.Column(db.Float)  # Min temperature tolerance (°C)
    temperature_max = db.Column(db.Float)  # Max temperature tolerance (°C)
    humidity_preference = db.Column(db.String(50))  # Low, Medium, High
    wind_tolerance = db.Column(db.String(50))  # Low, Medium, High

    # Extended soil attributes
    soil_ph_min = db.Column(db.Float)  # Minimum pH preference
    soil_ph_max = db.Column(db.Float)  # Maximum pH preference
    soil_drainage = db.Column(db.String(50))  # Poor, Good, Excellent
    soil_fertility = db.Column(db.String(50))  # Low, Medium, High

    # Maintenance attributes
    maintenance = db.Column(db.String(50))
    pruning_needs = db.Column(db.String(50))  # None, Light, Moderate, Heavy
    fertilizer_needs = db.Column(db.String(50))  # None, Light, Moderate, Heavy
    pest_resistance = db.Column(db.String(50))  # Low, Medium, High
    disease_resistance = db.Column(db.String(50))  # Low, Medium, High

    # Aesthetics attributes
    plant_form = db.Column(db.String(50))  # Upright, Spreading, Weeping, etc.
    foliage_texture = db.Column(db.String(50))  # Fine, Medium, Coarse
    seasonal_interest = db.Column(db.String(200))  # Spring flowers, Fall color, etc.
    fragrance = db.Column(db.Boolean, default=False)

    # Spatial attributes
    growth_rate = db.Column(db.String(50))  # Slow, Medium, Fast
    mature_spread = db.Column(db.Float)  # Final spread in meters
    root_system = db.Column(db.String(50))  # Shallow, Deep, Fibrous, Taproot

    # Ecological attributes
    wildlife_value = db.Column(db.String(50))  # Low, Medium, High
    pollinator_friendly = db.Column(db.Boolean, default=False)
    deer_resistant = db.Column(db.Boolean, default=False)
    invasive_potential = db.Column(db.String(50))  # None, Low, Medium, High

    # Project context attributes
    suitable_for_containers = db.Column(db.Boolean, default=False)
    suitable_for_hedging = db.Column(db.Boolean, default=False)
    suitable_for_screening = db.Column(db.Boolean, default=False)
    suitable_for_groundcover = db.Column(db.Boolean, default=False)
    suitable_for_slopes = db.Column(db.Boolean, default=False)

    # Existing attributes
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"))
    price = db.Column(db.Float)
    availability = db.Column(db.String(50))
    planting_season = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    photos = db.relationship("Photo", foreign_keys="Photo.plant_id", back_populates="plant", lazy=True)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def to_dict(self):
        supplier = cast("Supplier | None", getattr(self, "supplier", None))
        return {
            "id": self.id,
            "name": self.name,
            "common_name": self.common_name,
            "category": self.category,
            # Size attributes
            "height_min": self.height_min,
            "height_max": self.height_max,
            "width_min": self.width_min,
            "width_max": self.width_max,
            # Basic care requirements
            "sun_requirements": self.sun_requirements,
            "sun_exposure": self.sun_exposure,
            "soil_type": self.soil_type,
            "water_needs": self.water_needs,
            "moisture_level": self.moisture_level,
            "hardiness_zone": self.hardiness_zone,
            "bloom_time": self.bloom_time,
            "bloom_color": self.bloom_color,
            "foliage_color": self.foliage_color,
            "native": self.native,
            # Extended climate attributes
            "temperature_min": self.temperature_min,
            "temperature_max": self.temperature_max,
            "humidity_preference": self.humidity_preference,
            "wind_tolerance": self.wind_tolerance,
            # Extended soil attributes
            "soil_ph_min": self.soil_ph_min,
            "soil_ph_max": self.soil_ph_max,
            "soil_drainage": self.soil_drainage,
            "soil_fertility": self.soil_fertility,
            # Maintenance attributes
            "maintenance": self.maintenance,
            "pruning_needs": self.pruning_needs,
            "fertilizer_needs": self.fertilizer_needs,
            "pest_resistance": self.pest_resistance,
            "disease_resistance": self.disease_resistance,
            # Aesthetics attributes
            "plant_form": self.plant_form,
            "foliage_texture": self.foliage_texture,
            "seasonal_interest": self.seasonal_interest,
            "fragrance": self.fragrance,
            # Spatial attributes
            "growth_rate": self.growth_rate,
            "mature_spread": self.mature_spread,
            "root_system": self.root_system,
            # Ecological attributes
            "wildlife_value": self.wildlife_value,
            "pollinator_friendly": self.pollinator_friendly,
            "deer_resistant": self.deer_resistant,
            "invasive_potential": self.invasive_potential,
            # Project context attributes
            "suitable_for_containers": self.suitable_for_containers,
            "suitable_for_hedging": self.suitable_for_hedging,
            "suitable_for_screening": self.suitable_for_screening,
            "suitable_for_groundcover": self.suitable_for_groundcover,
            "suitable_for_slopes": self.suitable_for_slopes,
            # Existing attributes
            "supplier_id": self.supplier_id,
            "supplier_name": supplier.name if supplier else None,
            "price": self.price,
            "availability": self.availability,
            "planting_season": self.planting_season,
            "notes": self.notes,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }


class PlantRecommendationRequest(db.Model):
    __tablename__ = "plant_recommendation_requests"

    id = db.Column(db.Integer, primary_key=True)

    # Request criteria
    project_type = db.Column(db.String(100))  # Garden, Landscape, Commercial, etc.
    site_conditions = db.Column(db.JSON)  # Store complex site data as JSON

    # Environmental criteria
    hardiness_zone = db.Column(db.String(20))
    sun_exposure = db.Column(db.String(50))  # Full Sun, Partial, Shade
    soil_type = db.Column(db.String(100))
    soil_ph = db.Column(db.Float)
    moisture_level = db.Column(db.String(50))

    # Design criteria
    desired_height_min = db.Column(db.Float)
    desired_height_max = db.Column(db.Float)
    desired_width_min = db.Column(db.Float)
    desired_width_max = db.Column(db.Float)
    color_preferences = db.Column(db.String(200))
    bloom_season = db.Column(db.String(100))

    # Maintenance criteria
    maintenance_level = db.Column(db.String(50))  # Low, Medium, High
    budget_range = db.Column(db.String(50))

    # Special requirements
    native_preference = db.Column(db.Boolean, default=False)
    wildlife_friendly = db.Column(db.Boolean, default=False)
    deer_resistant_required = db.Column(db.Boolean, default=False)
    pollinator_friendly_required = db.Column(db.Boolean, default=False)

    # Project context
    container_planting = db.Column(db.Boolean, default=False)
    screening_purpose = db.Column(db.Boolean, default=False)
    hedging_purpose = db.Column(db.Boolean, default=False)
    groundcover_purpose = db.Column(db.Boolean, default=False)
    slope_planting = db.Column(db.Boolean, default=False)

    # Request metadata
    user_id = db.Column(db.String(100))  # Optional user identifier
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))  # Optional client association
    session_id = db.Column(db.String(100))  # Session tracking
    ip_address = db.Column(db.String(45))  # For analytics

    # Results and feedback
    recommended_plants = db.Column(db.JSON)  # Store recommendation results
    user_feedback = db.Column(db.JSON)  # Store user feedback for learning
    feedback_rating = db.Column(db.Integer)  # Overall rating 1-5

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "project_type": self.project_type,
            "site_conditions": self.site_conditions,
            "hardiness_zone": self.hardiness_zone,
            "sun_exposure": self.sun_exposure,
            "soil_type": self.soil_type,
            "soil_ph": self.soil_ph,
            "moisture_level": self.moisture_level,
            "desired_height_min": self.desired_height_min,
            "desired_height_max": self.desired_height_max,
            "desired_width_min": self.desired_width_min,
            "desired_width_max": self.desired_width_max,
            "color_preferences": self.color_preferences,
            "bloom_season": self.bloom_season,
            "maintenance_level": self.maintenance_level,
            "budget_range": self.budget_range,
            "native_preference": self.native_preference,
            "wildlife_friendly": self.wildlife_friendly,
            "deer_resistant_required": self.deer_resistant_required,
            "pollinator_friendly_required": self.pollinator_friendly_required,
            "container_planting": self.container_planting,
            "screening_purpose": self.screening_purpose,
            "hedging_purpose": self.hedging_purpose,
            "groundcover_purpose": self.groundcover_purpose,
            "slope_planting": self.slope_planting,
            "user_id": self.user_id,
            "client_id": self.client_id,
            "session_id": self.session_id,
            "recommended_plants": self.recommended_plants,
            "user_feedback": self.user_feedback,
            "feedback_rating": self.feedback_rating,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(200))
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    client_type = db.Column(db.String(50))
    budget_range = db.Column(db.String(100))
    notes = db.Column(db.Text)
    registration_date = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = db.relationship("Project", backref="client", lazy=True, cascade="all, delete-orphan")
    photos = db.relationship("Photo", foreign_keys="Photo.client_id", back_populates="client", lazy=True)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "company": self.company,
            "contact_person": self.contact_person,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "client_type": self.client_type,
            "budget_range": self.budget_range,
            "notes": self.notes,
            "registration_date": self.registration_date,
            "project_count": len(cast(Sequence[Any], self.projects or [])),
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    status = db.Column(db.String(50), default="Planning")
    project_type = db.Column(db.String(50))
    start_date = db.Column(db.String(20))  # ISO date string
    end_date = db.Column(db.String(20))  # ISO date string
    target_completion_date = db.Column(db.Date)
    actual_completion_date = db.Column(db.Date)
    budget = db.Column(db.Float)
    location = db.Column(db.Text)
    area_size = db.Column(db.Float)  # in square meters
    notes = db.Column(db.Text)
    project_manager = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project_plants = db.relationship("ProjectPlant", backref="project", lazy=True, cascade="all, delete-orphan")
    photos = db.relationship("Photo", foreign_keys="Photo.project_id", back_populates="project", lazy=True)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def to_dict(self):
        client = cast("Client | None", getattr(self, "client", None))
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "client_id": self.client_id,
            "client_name": client.name if client else None,
            "status": self.status,
            "project_type": self.project_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "target_completion_date": (
                self.target_completion_date.isoformat() if self.target_completion_date else None
            ),
            "actual_completion_date": (
                self.actual_completion_date.isoformat() if self.actual_completion_date else None
            ),
            "budget": self.budget,
            "location": self.location,
            "area_size": self.area_size,
            "notes": self.notes,
            "project_manager": self.project_manager,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }


class ProjectPlant(db.Model):
    """Association table for Project-Plant relationships with additional data"""

    __tablename__ = "project_plants"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey("plants.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_cost = db.Column(db.Float)  # Cost per plant
    status = db.Column(db.String(50), default="planned")  # planned, ordered, planted, completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    plant = db.relationship("Plant", backref="project_plants", lazy=True)

    # Unique constraint to prevent duplicate plant entries per project
    __table_args__ = (db.UniqueConstraint("project_id", "plant_id", name="unique_project_plant"),)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "plant_id": self.plant_id,
            "plant": self.plant.to_dict() if self.plant else None,
            "quantity": self.quantity,
            "unit_cost": self.unit_cost,
            "total_cost": (self.unit_cost * self.quantity) if self.unit_cost else None,
            "status": self.status,
            "notes": self.notes,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }


# Database Performance Optimization - Indexes for frequently queried fields
# These indexes significantly improve query performance for large datasets

# Plant indexes for search and filtering
plant_name_idx = db.Index("idx_plant_name", Plant.name)
plant_category_idx = db.Index("idx_plant_category", Plant.category)
plant_sun_requirements_idx = db.Index("idx_plant_sun_requirements", Plant.sun_requirements)
plant_water_needs_idx = db.Index("idx_plant_water_needs", Plant.water_needs)
plant_hardiness_zone_idx = db.Index("idx_plant_hardiness_zone", Plant.hardiness_zone)
plant_native_idx = db.Index("idx_plant_native", Plant.native)
plant_supplier_idx = db.Index("idx_plant_supplier_id", Plant.supplier_id)
plant_price_idx = db.Index("idx_plant_price", Plant.price)

# Composite indexes for common query patterns
plant_category_sun_idx = db.Index("idx_plant_category_sun", Plant.category, Plant.sun_requirements)
plant_native_category_idx = db.Index("idx_plant_native_category", Plant.native, Plant.category)

# Project indexes for filtering and search
project_client_idx = db.Index("idx_project_client_id", Project.client_id)
project_status_idx = db.Index("idx_project_status", Project.status)
project_type_idx = db.Index("idx_project_project_type", Project.project_type)
project_start_date_idx = db.Index("idx_project_start_date", Project.start_date)
project_budget_idx = db.Index("idx_project_budget", Project.budget)

# Composite indexes for project queries
project_status_client_idx = db.Index("idx_project_status_client", Project.status, Project.client_id)
project_type_status_idx = db.Index("idx_project_type_status", Project.project_type, Project.status)

# Supplier indexes
supplier_name_idx = db.Index("idx_supplier_name", Supplier.name)
supplier_city_idx = db.Index("idx_supplier_city", Supplier.city)
supplier_specialization_idx = db.Index("idx_supplier_specialization", Supplier.specialization)

# Client indexes
client_name_idx = db.Index("idx_client_name", Client.name)
client_city_idx = db.Index("idx_client_city", Client.city)
client_type_idx = db.Index("idx_client_type", Client.client_type)

# ProjectPlant indexes for relationships
project_plant_project_idx = db.Index("idx_project_plant_project", ProjectPlant.project_id)
project_plant_plant_idx = db.Index("idx_project_plant_plant", ProjectPlant.plant_id)
project_plant_status_idx = db.Index("idx_project_plant_status", ProjectPlant.status)
