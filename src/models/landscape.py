from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

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
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    products = db.relationship(
        "Product", backref="supplier", lazy=True, cascade="all, delete-orphan"
    )
    plants = db.relationship("Plant", backref="supplier", lazy=True)

    def to_dict(self):
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
            "product_count": len(self.products) if self.products else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
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
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "price": self.price,
            "unit": self.unit,
            "sku": self.sku,
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier.name if self.supplier else None,
            "stock_quantity": self.stock_quantity,
            "weight": self.weight,
            "dimensions": self.dimensions,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Plant(db.Model):
    __tablename__ = "plants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    common_name = db.Column(db.String(200))
    category = db.Column(db.String(50))  # Tree, Shrub, Perennial, Annual, etc.
    height_min = db.Column(db.Float)
    height_max = db.Column(db.Float)
    width_min = db.Column(db.Float)
    width_max = db.Column(db.Float)
    sun_requirements = db.Column(db.String(50))
    soil_type = db.Column(db.String(100))
    water_needs = db.Column(db.String(50))
    hardiness_zone = db.Column(db.String(20))
    bloom_time = db.Column(db.String(100))
    bloom_color = db.Column(db.String(100))
    foliage_color = db.Column(db.String(100))
    native = db.Column(db.Boolean, default=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"))
    price = db.Column(db.Float)
    availability = db.Column(db.String(50))
    planting_season = db.Column(db.String(100))
    maintenance = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "common_name": self.common_name,
            "category": self.category,
            "height_min": self.height_min,
            "height_max": self.height_max,
            "width_min": self.width_min,
            "width_max": self.width_max,
            "sun_requirements": self.sun_requirements,
            "soil_type": self.soil_type,
            "water_needs": self.water_needs,
            "hardiness_zone": self.hardiness_zone,
            "bloom_time": self.bloom_time,
            "bloom_color": self.bloom_color,
            "foliage_color": self.foliage_color,
            "native": self.native,
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier.name if self.supplier else None,
            "price": self.price,
            "availability": self.availability,
            "planting_season": self.planting_season,
            "maintenance": self.maintenance,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
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
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    projects = db.relationship(
        "Project", backref="client", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
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
            "project_count": len(self.projects) if self.projects else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
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
    budget = db.Column(db.Float)
    location = db.Column(db.Text)
    area_size = db.Column(db.Float)  # in square meters
    notes = db.Column(db.Text)
    project_manager = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "client_id": self.client_id,
            "client_name": self.client.name if self.client else None,
            "status": self.status,
            "project_type": self.project_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "budget": self.budget,
            "location": self.location,
            "area_size": self.area_size,
            "notes": self.notes,
            "project_manager": self.project_manager,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
