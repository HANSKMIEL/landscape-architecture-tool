"""
Fixed Sample Data for Landscape Architecture Application
Matches the database model fields exactly
"""

from src.models.landscape import db, Supplier, Product, Plant, Client, Project
from datetime import datetime, date

def initialize_sample_data():
    """Initialize sample data for the landscape architecture application"""
    print("Initializing sample data...")
    
    try:
        # Check if data already exists
        if Supplier.query.count() > 0:
            print("Sample data already exists, skipping initialization.")
            return
        
        # Create Suppliers (matching the Supplier model fields exactly)
        suppliers_data = [
            {
                'name': 'Boomkwekerij Peters',
                'contact_person': 'Jan Peters',
                'email': 'info@peters-bomen.nl',
                'phone': '+31 40 123 4567',
                'address': 'Hoofdstraat 123, 5611 AB Eindhoven',
                'website': 'www.peters-bomen.nl',
                'notes': 'Specialist in native Dutch trees and shrubs'
            },
            {
                'name': 'Van der Berg Tuinmaterialen',
                'contact_person': 'Marie van der Berg',
                'email': 'marie@vandenberg-tuin.nl',
                'phone': '+31 20 987 6543',
                'address': 'Tuinweg 45, 1012 CD Amsterdam',
                'website': 'www.vandenberg-tuin.nl',
                'notes': 'Complete garden materials and landscaping supplies'
            },
            {
                'name': 'GreenScape Supplies',
                'contact_person': 'Erik Janssen',
                'email': 'orders@greenscape.nl',
                'phone': '+31 40 555 7890',
                'address': 'Groenstraat 88, 5611 CL Eindhoven',
                'website': 'www.greenscape-supplies.nl',
                'notes': 'Professional landscape supplies and irrigation systems'
            }
        ]
        
        suppliers = []
        for supplier_data in suppliers_data:
            supplier = Supplier(**supplier_data)
            db.session.add(supplier)
            suppliers.append(supplier)
        
        db.session.flush()  # Get IDs for suppliers
        
        # Create Plants (matching the Plant model fields exactly)
        plants_data = [
            {
                'name': 'Acer platanoides',
                'scientific_name': 'Acer platanoides',
                'category': 'Tree',
                'description': 'Large deciduous tree, excellent for urban environments',
                'price': 45.50,
                'size': '6-8cm trunk',
                'supplier_id': suppliers[0].id,
                'care_instructions': 'Plant in well-drained soil, water regularly first year',
                'sunlight_requirements': 'Full Sun',
                'water_requirements': 'Medium',
                'soil_type': 'Well-drained, fertile soil',
                'hardiness_zone': '3-7',
                'mature_height': '15-20m',
                'mature_width': '12-15m',
                'bloom_time': 'April-May',
                'flower_color': 'Yellow-green',
                'foliage_color': 'Green, yellow fall color',
                'native_region': 'Europe'
            },
            {
                'name': 'Lavandula angustifolia',
                'scientific_name': 'Lavandula angustifolia',
                'category': 'Perennial',
                'description': 'Aromatic herb with purple flowers, drought tolerant',
                'price': 8.95,
                'size': '15cm pot',
                'supplier_id': suppliers[1].id,
                'care_instructions': 'Plant in sunny location, minimal water once established',
                'sunlight_requirements': 'Full Sun',
                'water_requirements': 'Low',
                'soil_type': 'Well-drained, sandy soil',
                'hardiness_zone': '5-9',
                'mature_height': '60cm',
                'mature_width': '60cm',
                'bloom_time': 'June-August',
                'flower_color': 'Purple',
                'foliage_color': 'Silver-green',
                'native_region': 'Mediterranean'
            },
            {
                'name': 'Buxus sempervirens',
                'scientific_name': 'Buxus sempervirens',
                'category': 'Shrub',
                'description': 'Evergreen shrub, excellent for hedging and topiary',
                'price': 12.75,
                'size': '20-30cm',
                'supplier_id': suppliers[0].id,
                'care_instructions': 'Plant in partial shade, regular watering',
                'sunlight_requirements': 'Partial Shade',
                'water_requirements': 'Medium',
                'soil_type': 'Well-drained, alkaline soil',
                'hardiness_zone': '6-8',
                'mature_height': '1-4m',
                'mature_width': '1-4m',
                'bloom_time': 'March-May',
                'flower_color': 'Inconspicuous',
                'foliage_color': 'Dark green',
                'native_region': 'Europe, Asia, Africa'
            }
        ]
        
        plants = []
        for plant_data in plants_data:
            plant = Plant(**plant_data)
            db.session.add(plant)
            plants.append(plant)
        
        db.session.flush()
        
        # Create Products (matching the Product model fields exactly)
        products_data = [
            {
                'name': 'Garden Soil Premium',
                'category': 'Soil',
                'description': 'High-quality garden soil mix for planting',
                'price': 25.00,
                'unit': 'cubic meter',
                'supplier_id': suppliers[1].id,
                'sku': 'SOIL-PREM-001',
                'in_stock': True
            },
            {
                'name': 'Mulch Bark Chips',
                'category': 'Mulch',
                'description': 'Natural bark chips for garden mulching',
                'price': 18.50,
                'unit': 'cubic meter',
                'supplier_id': suppliers[1].id,
                'sku': 'MULCH-BARK-001',
                'in_stock': True
            },
            {
                'name': 'Irrigation Drip Kit',
                'category': 'Irrigation',
                'description': 'Complete drip irrigation system for gardens',
                'price': 89.99,
                'unit': 'kit',
                'supplier_id': suppliers[2].id,
                'sku': 'IRR-DRIP-001',
                'in_stock': True
            },
            {
                'name': 'Natural Stone Pavers',
                'category': 'Hardscape',
                'description': 'Natural stone pavers for pathways and patios',
                'price': 45.00,
                'unit': 'square meter',
                'supplier_id': suppliers[1].id,
                'sku': 'STONE-PAV-001',
                'in_stock': True
            }
        ]
        
        products = []
        for product_data in products_data:
            product = Product(**product_data)
            db.session.add(product)
            products.append(product)
        
        db.session.flush()
        
        # Create Clients (matching the Client model fields exactly)
        clients_data = [
            {
                'name': 'Gemeente Amsterdam',
                'contact_person': 'Lisa Janssen',
                'email': 'l.janssen@amsterdam.nl',
                'phone': '+31 20 111 1111',
                'address': 'Stadhuis, Dam 1',
                'city': 'Amsterdam',
                'postal_code': '1012 JS',
                'country': 'Nederland',
                'company_type': 'government',
                'notes': 'Municipal landscaping projects'
            },
            {
                'name': 'Villa Roosendaal',
                'contact_person': 'Peter Smit',
                'email': 'p.smit@villa-roosendaal.nl',
                'phone': '+31 165 222 222',
                'address': 'Laan van Brabant 15',
                'city': 'Roosendaal',
                'postal_code': '4701 BP',
                'country': 'Nederland',
                'company_type': 'residential',
                'notes': 'Private residential garden design'
            },
            {
                'name': 'Bedrijventerrein Westpoort',
                'contact_person': 'Anna de Jong',
                'email': 'a.dejong@westpoort.nl',
                'phone': '+31 20 333 3333',
                'address': 'Westpoortweg 100',
                'city': 'Amsterdam',
                'postal_code': '1014 AK',
                'country': 'Nederland',
                'company_type': 'commercial',
                'notes': 'Commercial landscaping for business park'
            }
        ]
        
        clients = []
        for client_data in clients_data:
            client = Client(**client_data)
            db.session.add(client)
            clients.append(client)
        
        db.session.flush()
        
        # Create Projects (matching the Project model fields exactly)
        projects_data = [
            {
                'name': 'Vondelpark Renovation',
                'description': 'Complete renovation of historic park areas',
                'client_id': clients[0].id,
                'status': 'in_progress',
                'budget': 150000.00,
                'start_date': date(2024, 3, 1),
                'end_date': date(2024, 10, 31),
                'location': 'Vondelpark, Amsterdam',
                'project_type': 'public',
                'area_size': '5000 m²',
                'notes': 'Historic park renovation with sustainable practices'
            },
            {
                'name': 'Private Garden Design',
                'description': 'Modern garden design for luxury villa',
                'client_id': clients[1].id,
                'status': 'planning',
                'budget': 35000.00,
                'start_date': date(2024, 5, 1),
                'end_date': date(2024, 8, 15),
                'location': 'Roosendaal',
                'project_type': 'residential',
                'area_size': '800 m²',
                'notes': 'Contemporary design with water features'
            },
            {
                'name': 'Business Park Landscaping',
                'description': 'Corporate landscaping for office complex',
                'client_id': clients[2].id,
                'status': 'completed',
                'budget': 75000.00,
                'start_date': date(2024, 1, 15),
                'end_date': date(2024, 4, 30),
                'location': 'Amsterdam Westpoort',
                'project_type': 'commercial',
                'area_size': '2500 m²',
                'notes': 'Low-maintenance corporate landscaping'
            }
        ]
        
        projects = []
        for project_data in projects_data:
            project = Project(**project_data)
            db.session.add(project)
            projects.append(project)
        
        # Commit all data
        db.session.commit()
        
        print("Sample data initialized successfully!")
        print(f"Created {len(suppliers)} suppliers, {len(plants)} plants, {len(products)} products, {len(clients)} clients, and {len(projects)} projects.")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing sample data: {e}")
        raise e

