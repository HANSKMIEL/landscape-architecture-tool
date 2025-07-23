"""
Fixed Landscape Architecture Database Models
Includes all required association tables for many-to-many relationships
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Association tables for many-to-many relationships
project_plants = db.Table('project_plants',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('plant_id', db.Integer, db.ForeignKey('plant.id'), primary_key=True),
    db.Column('quantity', db.Integer, default=1),
    db.Column('date_added', db.DateTime, default=datetime.utcnow)
)

project_products = db.Table('project_products',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('quantity', db.Integer, default=1),
    db.Column('date_added', db.DateTime, default=datetime.utcnow)
)

class Supplier(db.Model):
    """Supplier model for landscape architecture suppliers"""
    __tablename__ = 'supplier'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    website = db.Column(db.String(200))
    notes = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='supplier', lazy=True)
    plants = db.relationship('Plant', backref='supplier', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'website': self.website,
            'notes': self.notes,
            'date_added': self.date_added.isoformat() if self.date_added else None
        }

class Product(db.Model):
    """Product model for landscape architecture products"""
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    unit = db.Column(db.String(50))
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    sku = db.Column(db.String(100))
    in_stock = db.Column(db.Boolean, default=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'price': self.price,
            'unit': self.unit,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'sku': self.sku,
            'in_stock': self.in_stock,
            'date_added': self.date_added.isoformat() if self.date_added else None
        }

class Plant(db.Model):
    """Plant model for landscape architecture plants"""
    __tablename__ = 'plant'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    scientific_name = db.Column(db.String(200))
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    size = db.Column(db.String(50))
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    care_instructions = db.Column(db.Text)
    sunlight_requirements = db.Column(db.String(100))
    water_requirements = db.Column(db.String(100))
    soil_type = db.Column(db.String(100))
    hardiness_zone = db.Column(db.String(20))
    mature_height = db.Column(db.String(50))
    mature_width = db.Column(db.String(50))
    bloom_time = db.Column(db.String(100))
    flower_color = db.Column(db.String(100))
    foliage_color = db.Column(db.String(100))
    native_region = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'scientific_name': self.scientific_name,
            'category': self.category,
            'description': self.description,
            'price': self.price,
            'size': self.size,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'care_instructions': self.care_instructions,
            'sunlight_requirements': self.sunlight_requirements,
            'water_requirements': self.water_requirements,
            'soil_type': self.soil_type,
            'hardiness_zone': self.hardiness_zone,
            'mature_height': self.mature_height,
            'mature_width': self.mature_width,
            'bloom_time': self.bloom_time,
            'flower_color': self.flower_color,
            'foliage_color': self.foliage_color,
            'native_region': self.native_region,
            'date_added': self.date_added.isoformat() if self.date_added else None
        }

class Client(db.Model):
    """Client model for landscape architecture clients"""
    __tablename__ = 'client'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    company_type = db.Column(db.String(100))  # business, individual, etc.
    notes = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    projects = db.relationship('Project', backref='client', lazy=True)
    
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
            'company_type': self.company_type,
            'notes': self.notes,
            'project_count': len(self.projects),
            'date_added': self.date_added.isoformat() if self.date_added else None
        }

class Project(db.Model):
    """Project model for landscape architecture projects"""
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    status = db.Column(db.String(50), default='planning')  # planning, in_progress, completed, on_hold
    budget = db.Column(db.Float)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    location = db.Column(db.Text)
    project_type = db.Column(db.String(100))  # residential, commercial, public, etc.
    area_size = db.Column(db.String(50))
    notes = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Many-to-many relationships
    plants = db.relationship('Plant', secondary=project_plants, lazy='subquery',
                           backref=db.backref('projects', lazy=True))
    products = db.relationship('Product', secondary=project_products, lazy='subquery',
                             backref=db.backref('projects', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'client_id': self.client_id,
            'client_name': self.client.name if self.client else None,
            'status': self.status,
            'budget': self.budget,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'location': self.location,
            'project_type': self.project_type,
            'area_size': self.area_size,
            'notes': self.notes,
            'plant_count': len(self.plants),
            'product_count': len(self.products),
            'date_created': self.date_created.isoformat() if self.date_created else None
        }

def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Add sample data if tables are empty
        if Supplier.query.count() == 0:
            add_sample_data()

def add_sample_data():
    """Add sample data to the database"""
    try:
        # Sample suppliers
        suppliers = [
            Supplier(name="Boomkwekerij Peters", contact_person="Jan Peters", 
                    email="info@peters-bomen.nl", phone="+31-40-1234567",
                    address="Hoofdstraat 123, 5611 AB Eindhoven", website="www.peters-bomen.nl"),
            Supplier(name="Van der Berg Tuinmaterialen", contact_person="Marie van der Berg",
                    email="marie@vandenberg-tuin.nl", phone="+31-20-9876543",
                    address="Tuinweg 45, 1012 CD Amsterdam", website="www.vandenberg-tuin.nl"),
            Supplier(name="GreenScape Supplies", contact_person="Tom de Vries",
                    email="tom@greenscape.nl", phone="+31-30-5555666",
                    address="Groenstraat 78, 3511 EF Utrecht", website="www.greenscape.nl")
        ]
        
        for supplier in suppliers:
            db.session.add(supplier)
        
        db.session.commit()
        
        # Sample clients
        clients = [
            Client(name="Gemeente Amsterdam", contact_person="Lisa Janssen",
                  email="l.janssen@amsterdam.nl", phone="+31-20-1111111",
                  address="Stadhuis, Dam 1", city="Amsterdam", postal_code="1012 JS",
                  country="Nederland", company_type="government"),
            Client(name="Villa Roosendaal", contact_person="Peter Smit",
                  email="p.smit@villa-roosendaal.nl", phone="+31-165-222222",
                  address="Laan van Brabant 15", city="Roosendaal", postal_code="4701 BP",
                  country="Nederland", company_type="residential"),
            Client(name="Bedrijventerrein Westpoort", contact_person="Anna de Jong",
                  email="a.dejong@westpoort.nl", phone="+31-20-3333333",
                  address="Westpoortweg 100", city="Amsterdam", postal_code="1014 AK",
                  country="Nederland", company_type="commercial")
        ]
        
        for client in clients:
            db.session.add(client)
        
        db.session.commit()
        
        print("Sample data added successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding sample data: {e}")

