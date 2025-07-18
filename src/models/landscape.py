from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    country = db.Column(db.String(50), default='Netherlands')
    website = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='supplier', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'country': self.country,
            'website': self.website,
            'notes': self.notes,
            'product_count': len(self.products),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    unit = db.Column(db.String(20))
    sku = db.Column(db.String(50))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    in_stock = db.Column(db.Boolean, default=True)
    minimum_order = db.Column(db.Integer, default=1)
    delivery_time = db.Column(db.String(50))
    specifications = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'description': self.description,
            'price': self.price,
            'unit': self.unit,
            'sku': self.sku,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'in_stock': self.in_stock,
            'minimum_order': self.minimum_order,
            'delivery_time': self.delivery_time,
            'specifications': self.specifications,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Plant(db.Model):
    __tablename__ = 'plants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    scientific_name = db.Column(db.String(200))
    common_name = db.Column(db.String(200))
    category = db.Column(db.String(50))  # Tree, Shrub, Perennial, Annual, etc.
    sun_requirements = db.Column(db.String(50))  # Full Sun, Partial Sun, Shade
    water_requirements = db.Column(db.String(50))  # Low, Medium, High
    soil_type = db.Column(db.String(100))
    hardiness_zone = db.Column(db.String(20))
    mature_height = db.Column(db.String(50))
    mature_width = db.Column(db.String(50))
    bloom_time = db.Column(db.String(100))
    bloom_color = db.Column(db.String(100))
    foliage_color = db.Column(db.String(100))
    maintenance_level = db.Column(db.String(20))  # Low, Medium, High
    native_to_netherlands = db.Column(db.Boolean, default=False)
    deer_resistant = db.Column(db.Boolean, default=False)
    drought_tolerant = db.Column(db.Boolean, default=False)
    attracts_pollinators = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'scientific_name': self.scientific_name,
            'common_name': self.common_name,
            'category': self.category,
            'sun_requirements': self.sun_requirements,
            'water_requirements': self.water_requirements,
            'soil_type': self.soil_type,
            'hardiness_zone': self.hardiness_zone,
            'mature_height': self.mature_height,
            'mature_width': self.mature_width,
            'bloom_time': self.bloom_time,
            'bloom_color': self.bloom_color,
            'foliage_color': self.foliage_color,
            'maintenance_level': self.maintenance_level,
            'native_to_netherlands': self.native_to_netherlands,
            'deer_resistant': self.deer_resistant,
            'drought_tolerant': self.drought_tolerant,
            'attracts_pollinators': self.attracts_pollinators,
            'price': self.price,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))  # Individual, Business, Municipality
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    country = db.Column(db.String(50), default='Netherlands')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = db.relationship('Project', backref='client', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'country': self.country,
            'notes': self.notes,
            'project_count': len(self.projects),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    status = db.Column(db.String(50), default='Planning')  # Planning, In Progress, Completed, On Hold
    project_type = db.Column(db.String(50))  # Residential Garden, Commercial Landscape, Public Space
    site_area = db.Column(db.Float)  # in square meters
    budget = db.Column(db.Float)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    location = db.Column(db.Text)
    soil_conditions = db.Column(db.Text)
    sun_exposure = db.Column(db.String(50))
    special_requirements = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project_plants = db.relationship('ProjectPlant', backref='project', lazy=True, cascade='all, delete-orphan')
    project_products = db.relationship('ProjectProduct', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'client_id': self.client_id,
            'client_name': self.client.name if self.client else None,
            'status': self.status,
            'project_type': self.project_type,
            'site_area': self.site_area,
            'budget': self.budget,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'location': self.location,
            'soil_conditions': self.soil_conditions,
            'sun_exposure': self.sun_exposure,
            'special_requirements': self.special_requirements,
            'notes': self.notes,
            'plant_count': len(self.project_plants),
            'product_count': len(self.project_products),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProjectPlant(db.Model):
    __tablename__ = 'project_plants'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    location_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    plant = db.relationship('Plant', backref='project_plants')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'plant_id': self.plant_id,
            'plant_name': self.plant.name if self.plant else None,
            'quantity': self.quantity,
            'location_notes': self.location_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ProjectProduct(db.Model):
    __tablename__ = 'project_products'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='project_products')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

