#!/usr/bin/env python3
"""
Landscape Architecture Management System - Backend API
Fixed version with proper database initialization and error handling
"""

import os
import sys
import logging
from datetime import datetime, date
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:5174", "http://127.0.0.1:5174"])

# In-memory database (for development)
database = {
    'suppliers': [],
    'plants': [],
    'products': [],
    'clients': [],
    'projects': []
}

def initialize_sample_data():
    """Initialize the database with comprehensive Dutch sample data"""
    logger.info("Initializing sample data...")
    
    # Clear existing data
    for key in database:
        database[key] = []
    
    # Sample Suppliers
    database['suppliers'] = [
        {
            'id': 1,
            'name': 'Boomkwekerij Peters',
            'contact_person': 'Jan Peters',
            'email': 'jan@boomkwekerijpeters.nl',
            'phone': '+31 6 12345678',
            'address': 'Kwekerslaan 15',
            'city': 'Boskoop',
            'postal_code': '2771 AA',
            'specialization': 'Bomen en heesters',
            'website': 'www.boomkwekerijpeters.nl',
            'notes': 'Gespecialiseerd in inheemse boomsoorten'
        },
        {
            'id': 2,
            'name': 'Tuincentrum De Groene Vingers',
            'contact_person': 'Maria van der Berg',
            'email': 'maria@groenevinger.nl',
            'phone': '+31 20 7654321',
            'address': 'Tuinstraat 88',
            'city': 'Amsterdam',
            'postal_code': '1012 AB',
            'specialization': 'Vaste planten en seizoensplanten',
            'website': 'www.groenevinger.nl',
            'notes': 'Breed assortiment vaste planten'
        },
        {
            'id': 3,
            'name': 'Kwekerij Groen & Co',
            'contact_person': 'Piet Groen',
            'email': 'info@groenco.nl',
            'phone': '+31 30 9876543',
            'address': 'Plantsoenweg 42',
            'city': 'Utrecht',
            'postal_code': '3521 XY',
            'specialization': 'Biologische planten en kruiden',
            'website': 'www.groenco.nl',
            'notes': 'Gecertificeerd biologisch'
        }
    ]
    
    # Sample Plants
    database['plants'] = [
        {
            'id': 1,
            'name': 'Acer platanoides',
            'common_name': 'Noorse esdoorn',
            'category': 'Boom',
            'height_min': 15.0,
            'height_max': 25.0,
            'width_min': 8.0,
            'width_max': 15.0,
            'sun_requirements': 'Zon tot halfschaduw',
            'soil_type': 'Alle grondsoorten',
            'water_needs': 'Matig',
            'hardiness_zone': '4-7',
            'bloom_time': 'April-Mei',
            'bloom_color': 'Geel-groen',
            'foliage_color': 'Groen, geel in herfst',
            'native': True,
            'supplier_id': 1,
            'price': 45.50,
            'availability': 'Voorradig',
            'planting_season': 'Herfst/Voorjaar',
            'maintenance': 'Laag',
            'notes': 'Sterke stadsboom, geschikt voor lanen'
        },
        {
            'id': 2,
            'name': 'Lavandula angustifolia',
            'common_name': 'Echte lavendel',
            'category': 'Vaste plant',
            'height_min': 0.3,
            'height_max': 0.6,
            'width_min': 0.4,
            'width_max': 0.8,
            'sun_requirements': 'Volle zon',
            'soil_type': 'Goed doorlatend, kalkrijk',
            'water_needs': 'Droog tot matig',
            'hardiness_zone': '5-9',
            'bloom_time': 'Juni-Augustus',
            'bloom_color': 'Paars-blauw',
            'foliage_color': 'Grijs-groen',
            'native': False,
            'supplier_id': 2,
            'price': 8.95,
            'availability': 'Voorradig',
            'planting_season': 'Voorjaar',
            'maintenance': 'Laag',
            'notes': 'Geurend, trekt bijen aan, droogteresistent'
        },
        {
            'id': 3,
            'name': 'Buxus sempervirens',
            'common_name': 'Gewone buxus',
            'category': 'Heester',
            'height_min': 0.5,
            'height_max': 3.0,
            'width_min': 0.5,
            'width_max': 2.0,
            'sun_requirements': 'Zon tot schaduw',
            'soil_type': 'Alle grondsoorten',
            'water_needs': 'Matig',
            'hardiness_zone': '6-8',
            'bloom_time': 'Maart-April',
            'bloom_color': 'Onopvallend geel-groen',
            'foliage_color': 'Donkergroen, wintergroen',
            'native': False,
            'supplier_id': 1,
            'price': 12.50,
            'availability': 'Beperkt voorradig',
            'planting_season': 'Herfst/Voorjaar',
            'maintenance': 'Matig',
            'notes': 'Uitstekend voor hagen en topiary'
        }
    ]
    
    # Sample Products
    database['products'] = [
        {
            'id': 1,
            'name': 'Premium Tuinaarde',
            'description': 'Hoogwaardige tuinaarde voor alle toepassingen',
            'category': 'Grond en substraat',
            'price': 3.50,
            'unit': 'per 40L zak',
            'supplier_id': 2,
            'stock_quantity': 150,
            'sku': 'TA-PREM-40L',
            'weight': 25.0,
            'dimensions': '60x40x15 cm',
            'notes': 'Geschikt voor groenten, bloemen en heesters'
        },
        {
            'id': 2,
            'name': 'Automatisch Druppelsysteem',
            'description': 'Complete druppelirrigatie set voor 20m²',
            'category': 'Irrigatie',
            'price': 89.95,
            'unit': 'per set',
            'supplier_id': 3,
            'stock_quantity': 25,
            'sku': 'IRR-AUTO-20M',
            'weight': 3.5,
            'dimensions': '30x20x15 cm',
            'notes': 'Inclusief timer en alle benodigde onderdelen'
        },
        {
            'id': 3,
            'name': 'Professionele Snoeischaar',
            'description': 'Bypass snoeischaar voor takken tot 25mm',
            'category': 'Gereedschap',
            'price': 34.50,
            'unit': 'per stuk',
            'supplier_id': 1,
            'stock_quantity': 40,
            'sku': 'TOOL-SNOE-25MM',
            'weight': 0.8,
            'dimensions': '25x8x3 cm',
            'notes': 'Ergonomische handgrepen, anti-slip coating'
        },
        {
            'id': 4,
            'name': 'LED Tuinverlichting Set',
            'description': 'Energiezuinige LED spots voor tuinverlichting',
            'category': 'Verlichting',
            'price': 125.00,
            'unit': 'per 6-delige set',
            'supplier_id': 2,
            'stock_quantity': 18,
            'sku': 'LED-TUIN-6SET',
            'weight': 2.1,
            'dimensions': '35x25x10 cm',
            'notes': 'Waterdicht IP65, warm wit licht, 5 jaar garantie'
        }
    ]
    
    # Sample Clients
    database['clients'] = [
        {
            'id': 1,
            'name': 'Gemeente Amsterdam',
            'contact_person': 'Ing. Sarah de Vries',
            'email': 'sarah.devries@amsterdam.nl',
            'phone': '+31 20 5551234',
            'address': 'Amstel 1',
            'city': 'Amsterdam',
            'postal_code': '1011 PN',
            'client_type': 'Overheid',
            'budget_range': '€50.000 - €200.000',
            'notes': 'Verantwoordelijk voor openbare groenvoorzieningen',
            'registration_date': '2024-01-15'
        },
        {
            'id': 2,
            'name': 'Vondelpark Beheer BV',
            'contact_person': 'Drs. Mark Janssen',
            'email': 'mark.janssen@vondelpark.nl',
            'phone': '+31 20 5559876',
            'address': 'Vondelpark 1',
            'city': 'Amsterdam',
            'postal_code': '1071 AA',
            'client_type': 'Commercieel',
            'budget_range': '€20.000 - €100.000',
            'notes': 'Beheer en onderhoud historische parken',
            'registration_date': '2024-02-03'
        },
        {
            'id': 3,
            'name': 'Villa Rozenhof',
            'contact_person': 'Mevr. Elisabeth van Houten',
            'email': 'e.vanhouten@rozenhof.nl',
            'phone': '+31 35 5554567',
            'address': 'Rozenlaan 45',
            'city': 'Hilversum',
            'postal_code': '1234 AB',
            'client_type': 'Particulier',
            'budget_range': '€10.000 - €50.000',
            'notes': 'Exclusieve privé-tuin met historische elementen',
            'registration_date': '2024-03-12'
        }
    ]
    
    # Sample Projects
    database['projects'] = [
        {
            'id': 1,
            'name': 'Vondelpark Renovatie Fase 2',
            'description': 'Herinrichting van de zuidelijke zone van het Vondelpark',
            'client_id': 2,
            'status': 'In uitvoering',
            'start_date': '2024-04-01',
            'end_date': '2024-10-31',
            'budget': 75000.00,
            'location': 'Vondelpark Zuid, Amsterdam',
            'project_type': 'Renovatie',
            'area_size': 2500.0,
            'notes': 'Focus op duurzame beplanting en waterretentie',
            'project_manager': 'Hans Kmiel'
        },
        {
            'id': 2,
            'name': 'Daktuin Nieuwbouw Centrum',
            'description': 'Extensieve daktuin voor nieuwbouwproject',
            'client_id': 1,
            'status': 'Planning',
            'start_date': '2024-08-15',
            'end_date': '2024-12-20',
            'budget': 45000.00,
            'location': 'Centrum Amsterdam',
            'project_type': 'Nieuwbouw',
            'area_size': 800.0,
            'notes': 'Sedum-dak met biodiversiteit focus',
            'project_manager': 'Hans Kmiel'
        },
        {
            'id': 3,
            'name': 'Privé Tuin Rozenhof',
            'description': 'Complete herinrichting van historische privé-tuin',
            'client_id': 3,
            'status': 'Afgerond',
            'start_date': '2024-03-01',
            'end_date': '2024-06-30',
            'budget': 32000.00,
            'location': 'Hilversum',
            'project_type': 'Renovatie',
            'area_size': 1200.0,
            'notes': 'Behoud van historische elementen, nieuwe rozentuin',
            'project_manager': 'Hans Kmiel'
        }
    ]
    
    logger.info(f"Sample data initialized successfully!")
    logger.info(f"Created {len(database['suppliers'])} suppliers, {len(database['plants'])} plants, {len(database['products'])} products, {len(database['clients'])} clients, and {len(database['projects'])} projects.")

# Error handler decorator
def handle_errors(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500
    wrapper.__name__ = f.__name__
    return wrapper

# API Routes

@app.route('/api/', methods=['GET'])
@handle_errors
def api_documentation():
    """API documentation endpoint"""
    return jsonify({
        'name': 'Landscape Architecture Management API',
        'version': '1.0.0',
        'description': 'Backend API for landscape architecture project management',
        'endpoints': {
            'dashboard': {
                'stats': '/api/dashboard/stats',
                'recent_activity': '/api/dashboard/recent-activity'
            },
            'suppliers': '/api/suppliers',
            'plants': '/api/plants',
            'products': '/api/products',
            'clients': '/api/clients',
            'projects': '/api/projects'
        },
        'status': 'operational',
        'data_initialized': len(database['suppliers']) > 0
    })

# Dashboard endpoints
@app.route('/api/dashboard/stats', methods=['GET'])
@handle_errors
def get_dashboard_stats():
    """Get dashboard statistics"""
    stats = {
        'suppliers': len(database['suppliers']),
        'plants': len(database['plants']),
        'products': len(database['products']),
        'clients': len(database['clients']),
        'projects': len(database['projects']),
        'active_projects': len([p for p in database['projects'] if p['status'] == 'In uitvoering']),
        'completed_projects': len([p for p in database['projects'] if p['status'] == 'Afgerond']),
        'total_budget': sum([p['budget'] for p in database['projects']]),
        'last_updated': datetime.now().isoformat()
    }
    return jsonify(stats)

@app.route('/api/dashboard/recent-activity', methods=['GET'])
@handle_errors
def get_recent_activity():
    """Get recent activity for dashboard"""
    activities = [
        {
            'id': 1,
            'type': 'project_update',
            'title': 'Project Vondelpark Renovatie bijgewerkt',
            'description': 'Status gewijzigd naar "In uitvoering"',
            'timestamp': '2024-07-24T10:30:00',
            'user': 'Hans Kmiel'
        },
        {
            'id': 2,
            'type': 'client_added',
            'title': 'Nieuwe klant toegevoegd',
            'description': 'Villa Rozenhof geregistreerd',
            'timestamp': '2024-07-23T14:15:00',
            'user': 'Hans Kmiel'
        },
        {
            'id': 3,
            'type': 'product_updated',
            'title': 'Product voorraad bijgewerkt',
            'description': 'Premium Tuinaarde voorraad aangepast',
            'timestamp': '2024-07-22T09:45:00',
            'user': 'Hans Kmiel'
        }
    ]
    return jsonify(activities)

# Suppliers endpoints
@app.route('/api/suppliers', methods=['GET'])
@handle_errors
def get_suppliers():
    """Get all suppliers"""
    search = request.args.get('search', '').lower()
    suppliers = database['suppliers']
    
    if search:
        suppliers = [s for s in suppliers if 
                    search in s['name'].lower() or 
                    search in s['contact_person'].lower() or
                    search in s['city'].lower()]
    
    return jsonify(suppliers)

@app.route('/api/suppliers', methods=['POST'])
@handle_errors
def create_supplier():
    """Create new supplier"""
    data = request.get_json()
    
    # Generate new ID
    new_id = max([s['id'] for s in database['suppliers']], default=0) + 1
    
    supplier = {
        'id': new_id,
        'name': data.get('name', ''),
        'contact_person': data.get('contact_person', ''),
        'email': data.get('email', ''),
        'phone': data.get('phone', ''),
        'address': data.get('address', ''),
        'city': data.get('city', ''),
        'postal_code': data.get('postal_code', ''),
        'specialization': data.get('specialization', ''),
        'website': data.get('website', ''),
        'notes': data.get('notes', '')
    }
    
    database['suppliers'].append(supplier)
    logger.info(f"Created supplier: {supplier['name']}")
    
    return jsonify(supplier), 201

@app.route('/api/suppliers/<int:supplier_id>', methods=['PUT'])
@handle_errors
def update_supplier(supplier_id):
    """Update supplier"""
    data = request.get_json()
    
    for i, supplier in enumerate(database['suppliers']):
        if supplier['id'] == supplier_id:
            database['suppliers'][i].update(data)
            logger.info(f"Updated supplier: {database['suppliers'][i]['name']}")
            return jsonify(database['suppliers'][i])
    
    return jsonify({'error': 'Supplier not found'}), 404

@app.route('/api/suppliers/<int:supplier_id>', methods=['DELETE'])
@handle_errors
def delete_supplier(supplier_id):
    """Delete supplier"""
    for i, supplier in enumerate(database['suppliers']):
        if supplier['id'] == supplier_id:
            deleted_supplier = database['suppliers'].pop(i)
            logger.info(f"Deleted supplier: {deleted_supplier['name']}")
            return jsonify({'message': 'Supplier deleted successfully'})
    
    return jsonify({'error': 'Supplier not found'}), 404

# Plants endpoints
@app.route('/api/plants', methods=['GET'])
@handle_errors
def get_plants():
    """Get all plants"""
    search = request.args.get('search', '').lower()
    plants = database['plants']
    
    if search:
        plants = [p for p in plants if 
                 search in p['name'].lower() or 
                 search in p['common_name'].lower() or
                 search in p['category'].lower()]
    
    return jsonify(plants)

@app.route('/api/plants', methods=['POST'])
@handle_errors
def create_plant():
    """Create new plant"""
    data = request.get_json()
    
    # Generate new ID
    new_id = max([p['id'] for p in database['plants']], default=0) + 1
    
    plant = {
        'id': new_id,
        'name': data.get('name', ''),
        'common_name': data.get('common_name', ''),
        'category': data.get('category', ''),
        'height_min': float(data.get('height_min', 0)),
        'height_max': float(data.get('height_max', 0)),
        'width_min': float(data.get('width_min', 0)),
        'width_max': float(data.get('width_max', 0)),
        'sun_requirements': data.get('sun_requirements', ''),
        'soil_type': data.get('soil_type', ''),
        'water_needs': data.get('water_needs', ''),
        'hardiness_zone': data.get('hardiness_zone', ''),
        'bloom_time': data.get('bloom_time', ''),
        'bloom_color': data.get('bloom_color', ''),
        'foliage_color': data.get('foliage_color', ''),
        'native': data.get('native', False),
        'supplier_id': data.get('supplier_id'),
        'price': float(data.get('price', 0)),
        'availability': data.get('availability', ''),
        'planting_season': data.get('planting_season', ''),
        'maintenance': data.get('maintenance', ''),
        'notes': data.get('notes', '')
    }
    
    database['plants'].append(plant)
    logger.info(f"Created plant: {plant['name']}")
    
    return jsonify(plant), 201

@app.route('/api/plants/<int:plant_id>', methods=['PUT'])
@handle_errors
def update_plant(plant_id):
    """Update plant"""
    data = request.get_json()
    
    for i, plant in enumerate(database['plants']):
        if plant['id'] == plant_id:
            database['plants'][i].update(data)
            logger.info(f"Updated plant: {database['plants'][i]['name']}")
            return jsonify(database['plants'][i])
    
    return jsonify({'error': 'Plant not found'}), 404

@app.route('/api/plants/<int:plant_id>', methods=['DELETE'])
@handle_errors
def delete_plant(plant_id):
    """Delete plant"""
    for i, plant in enumerate(database['plants']):
        if plant['id'] == plant_id:
            deleted_plant = database['plants'].pop(i)
            logger.info(f"Deleted plant: {deleted_plant['name']}")
            return jsonify({'message': 'Plant deleted successfully'})
    
    return jsonify({'error': 'Plant not found'}), 404

# Products endpoints
@app.route('/api/products', methods=['GET'])
@handle_errors
def get_products():
    """Get all products"""
    search = request.args.get('search', '').lower()
    products = database['products']
    
    if search:
        products = [p for p in products if 
                   search in p['name'].lower() or 
                   search in p['category'].lower() or
                   search in p.get('description', '').lower()]
    
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
@handle_errors
def create_product():
    """Create new product"""
    data = request.get_json()
    
    # Generate new ID
    new_id = max([p['id'] for p in database['products']], default=0) + 1
    
    product = {
        'id': new_id,
        'name': data.get('name', ''),
        'description': data.get('description', ''),
        'category': data.get('category', ''),
        'price': float(data.get('price', 0)),
        'unit': data.get('unit', ''),
        'supplier_id': data.get('supplier_id'),
        'stock_quantity': int(data.get('stock_quantity', 0)),
        'sku': data.get('sku', ''),
        'weight': float(data.get('weight', 0)),
        'dimensions': data.get('dimensions', ''),
        'notes': data.get('notes', '')
    }
    
    database['products'].append(product)
    logger.info(f"Created product: {product['name']}")
    
    return jsonify(product), 201

@app.route('/api/products/<int:product_id>', methods=['PUT'])
@handle_errors
def update_product(product_id):
    """Update product"""
    data = request.get_json()
    
    for i, product in enumerate(database['products']):
        if product['id'] == product_id:
            database['products'][i].update(data)
            logger.info(f"Updated product: {database['products'][i]['name']}")
            return jsonify(database['products'][i])
    
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@handle_errors
def delete_product(product_id):
    """Delete product"""
    for i, product in enumerate(database['products']):
        if product['id'] == product_id:
            deleted_product = database['products'].pop(i)
            logger.info(f"Deleted product: {deleted_product['name']}")
            return jsonify({'message': 'Product deleted successfully'})
    
    return jsonify({'error': 'Product not found'}), 404

# Clients endpoints
@app.route('/api/clients', methods=['GET'])
@handle_errors
def get_clients():
    """Get all clients"""
    search = request.args.get('search', '').lower()
    clients = database['clients']
    
    if search:
        clients = [c for c in clients if 
                  search in c['name'].lower() or 
                  search in c['contact_person'].lower() or
                  search in c['city'].lower()]
    
    return jsonify(clients)

@app.route('/api/clients', methods=['POST'])
@handle_errors
def create_client():
    """Create new client"""
    data = request.get_json()
    
    # Generate new ID
    new_id = max([c['id'] for c in database['clients']], default=0) + 1
    
    client = {
        'id': new_id,
        'name': data.get('name', ''),
        'contact_person': data.get('contact_person', ''),
        'email': data.get('email', ''),
        'phone': data.get('phone', ''),
        'address': data.get('address', ''),
        'city': data.get('city', ''),
        'postal_code': data.get('postal_code', ''),
        'client_type': data.get('client_type', ''),
        'budget_range': data.get('budget_range', ''),
        'notes': data.get('notes', ''),
        'registration_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    database['clients'].append(client)
    logger.info(f"Created client: {client['name']}")
    
    return jsonify(client), 201

@app.route('/api/clients/<int:client_id>', methods=['PUT'])
@handle_errors
def update_client(client_id):
    """Update client"""
    data = request.get_json()
    
    for i, client in enumerate(database['clients']):
        if client['id'] == client_id:
            database['clients'][i].update(data)
            logger.info(f"Updated client: {database['clients'][i]['name']}")
            return jsonify(database['clients'][i])
    
    return jsonify({'error': 'Client not found'}), 404

@app.route('/api/clients/<int:client_id>', methods=['DELETE'])
@handle_errors
def delete_client(client_id):
    """Delete client"""
    for i, client in enumerate(database['clients']):
        if client['id'] == client_id:
            deleted_client = database['clients'].pop(i)
            logger.info(f"Deleted client: {deleted_client['name']}")
            return jsonify({'message': 'Client deleted successfully'})
    
    return jsonify({'error': 'Client not found'}), 404

# Projects endpoints
@app.route('/api/projects', methods=['GET'])
@handle_errors
def get_projects():
    """Get all projects"""
    search = request.args.get('search', '').lower()
    client_id = request.args.get('client_id')
    projects = database['projects']
    
    if client_id:
        projects = [p for p in projects if p['client_id'] == int(client_id)]
    
    if search:
        projects = [p for p in projects if 
                   search in p['name'].lower() or 
                   search in p['description'].lower() or
                   search in p['location'].lower()]
    
    return jsonify(projects)

@app.route('/api/projects', methods=['POST'])
@handle_errors
def create_project():
    """Create new project"""
    data = request.get_json()
    
    # Generate new ID
    new_id = max([p['id'] for p in database['projects']], default=0) + 1
    
    project = {
        'id': new_id,
        'name': data.get('name', ''),
        'description': data.get('description', ''),
        'client_id': data.get('client_id'),
        'status': data.get('status', 'Planning'),
        'start_date': data.get('start_date', ''),
        'end_date': data.get('end_date', ''),
        'budget': float(data.get('budget', 0)),
        'location': data.get('location', ''),
        'project_type': data.get('project_type', ''),
        'area_size': float(data.get('area_size', 0)),
        'notes': data.get('notes', ''),
        'project_manager': data.get('project_manager', 'Hans Kmiel')
    }
    
    database['projects'].append(project)
    logger.info(f"Created project: {project['name']}")
    
    return jsonify(project), 201

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@handle_errors
def update_project(project_id):
    """Update project"""
    data = request.get_json()
    
    for i, project in enumerate(database['projects']):
        if project['id'] == project_id:
            database['projects'][i].update(data)
            logger.info(f"Updated project: {database['projects'][i]['name']}")
            return jsonify(database['projects'][i])
    
    return jsonify({'error': 'Project not found'}), 404

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@handle_errors
def delete_project(project_id):
    """Delete project"""
    for i, project in enumerate(database['projects']):
        if project['id'] == project_id:
            deleted_project = database['projects'].pop(i)
            logger.info(f"Deleted project: {deleted_project['name']}")
            return jsonify({'message': 'Project deleted successfully'})
    
    return jsonify({'error': 'Project not found'}), 404

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'database_status': 'initialized' if len(database['suppliers']) > 0 else 'empty'
    })

if __name__ == '__main__':
    logger.info("Starting Landscape Architecture Management System...")
    logger.info("Backend API will be available at: http://127.0.0.1:5001")
    logger.info("API documentation available at: http://127.0.0.1:5001/api/")
    
    # Initialize sample data
    initialize_sample_data()
    
    # Start the Flask development server
    app.run(
        host='127.0.0.1',
        port=5001,
        debug=True,
        use_reloader=True
    )

