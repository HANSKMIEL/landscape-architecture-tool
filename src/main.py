#!/usr/bin/env python3
"""
Landscape Architecture Management System - Backend
A comprehensive Flask application for managing landscape architecture projects.
"""

import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, date
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration
DATABASE = 'landscape_architecture.db'

def get_db_connection():
    """Get database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with tables and sample data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_person TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            postal_code TEXT,
            country TEXT DEFAULT 'Nederland',
            specialization TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            scientific_name TEXT,
            category TEXT,
            height_min REAL,
            height_max REAL,
            spread_min REAL,
            spread_max REAL,
            sun_requirements TEXT,
            water_requirements TEXT,
            soil_type TEXT,
            hardiness_zone TEXT,
            bloom_time TEXT,
            flower_color TEXT,
            foliage_color TEXT,
            growth_rate TEXT,
            maintenance_level TEXT,
            price REAL,
            supplier_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            unit TEXT,
            price REAL,
            stock_quantity INTEGER DEFAULT 0,
            supplier_id INTEGER,
            sku TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            contact_person TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            postal_code TEXT,
            country TEXT DEFAULT 'Nederland',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            client_id INTEGER,
            status TEXT DEFAULT 'Planning',
            start_date DATE,
            end_date DATE,
            budget REAL,
            location TEXT,
            area_size REAL,
            project_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM suppliers')
    if cursor.fetchone()[0] == 0:
        # Insert sample data
        logger.info("Initializing sample data...")
        
        # Sample suppliers
        suppliers_data = [
            ('Boomkwekerij Peters', 'Jan Peters', 'jan@peters-boomkwekerij.nl', '0123-456789', 'Kwekerslaan 15', 'Boskoop', '2771 AB', 'Nederland', 'Bomen en heesters'),
            ('Tuincentrum De Groene Vingers', 'Maria van der Berg', 'info@groenevingers.nl', '0456-789123', 'Tuinstraat 42', 'Aalsmeer', '1431 HG', 'Nederland', 'Tuinplanten en accessoires'),
            ('Kwekerij Bloembollen BV', 'Piet Jansen', 'verkoop@bloembollen.nl', '0789-123456', 'Bollenweg 8', 'Lisse', '2161 KM', 'Nederland', 'Bloembollen en vaste planten')
        ]
        
        cursor.executemany('''
            INSERT INTO suppliers (name, contact_person, email, phone, address, city, postal_code, country, specialization)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', suppliers_data)
        
        # Sample plants
        plants_data = [
            ('Acer platanoides', 'Acer platanoides', 'Boom', 15.0, 25.0, 8.0, 15.0, 'Zon tot halfschaduw', 'Matig', 'Alle grondsoorten', '4-7', 'April-Mei', 'Geel-groen', 'Groen, geel in herfst', 'Matig', 'Laag', 45.50, 1, 'Sterke schaduwboom, geschikt voor stedelijke omgeving'),
            ('Lavandula angustifolia', 'Lavandula angustifolia', 'Vaste plant', 0.3, 0.6, 0.4, 0.8, 'Volle zon', 'Droog', 'Goed doorlatend', '5-9', 'Juni-Augustus', 'Paars', 'Grijs-groen', 'Matig', 'Laag', 8.95, 2, 'Geurende plant, trekt bijen aan'),
            ('Buxus sempervirens', 'Buxus sempervirens', 'Heester', 1.0, 3.0, 1.0, 3.0, 'Zon tot schaduw', 'Matig', 'Alle grondsoorten', '6-8', 'Maart-April', 'Onopvallend', 'Donkergroen', 'Langzaam', 'Matig', 12.75, 1, 'Wintergroene heester, goed te snoeien')
        ]
        
        cursor.executemany('''
            INSERT INTO plants (name, scientific_name, category, height_min, height_max, spread_min, spread_max, 
                              sun_requirements, water_requirements, soil_type, hardiness_zone, bloom_time, 
                              flower_color, foliage_color, growth_rate, maintenance_level, price, supplier_id, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', plants_data)
        
        # Sample products
        products_data = [
            ('Tuinaarde Premium', 'Grond en substraat', 'Hoogwaardige tuinaarde voor alle toepassingen', 'zak 40L', 4.95, 150, 2, 'TA-PREM-40'),
            ('Compostvork RVS', 'Gereedschap', 'Professionele compostvork van roestvrij staal', 'stuk', 28.50, 25, 2, 'CF-RVS-001'),
            ('Druppelslang 25m', 'Irrigatie', 'Efficiënte druppelslang voor waterbesparend tuinieren', 'rol 25m', 19.95, 40, 3, 'DS-25M-001'),
            ('Tuinverlichting LED', 'Verlichting', 'Energiezuinige LED tuinverlichting', 'set 10 stuks', 89.99, 15, 3, 'TV-LED-10')
        ]
        
        cursor.executemany('''
            INSERT INTO products (name, category, description, unit, price, stock_quantity, supplier_id, sku)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', products_data)
        
        # Sample clients
        clients_data = [
            ('Gemeente Amsterdam', 'Overheid', 'Afdeling Groen en Water', 'groen@amsterdam.nl', '020-5551234', 'Amstel 1', 'Amsterdam', '1011 PN', 'Nederland'),
            ('Vondelpark Beheer', 'Stichting', 'Directeur Park Management', 'beheer@vondelpark.nl', '020-5555678', 'Vondelpark 1', 'Amsterdam', '1071 AA', 'Nederland'),
            ('Villa Rozenhof', 'Particulier', 'Familie van der Meer', 'info@villarozenhof.nl', '035-1234567', 'Rozenlaan 25', 'Hilversum', '1234 AB', 'Nederland')
        ]
        
        cursor.executemany('''
            INSERT INTO clients (name, type, contact_person, email, phone, address, city, postal_code, country)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', clients_data)
        
        # Sample projects
        projects_data = [
            ('Vondelpark Renovatie', 'Grootschalige renovatie van het historische Vondelpark', 2, 'In uitvoering', '2024-03-01', '2024-12-31', 250000.00, 'Vondelpark, Amsterdam', 47.0, 'Park renovatie'),
            ('Daktuin Villa Rozenhof', 'Ontwerp en aanleg van exclusieve daktuin', 3, 'Planning', '2024-06-01', '2024-08-31', 35000.00, 'Hilversum', 120.0, 'Daktuin'),
            ('Groenstrook Nieuw-West', 'Aanleg van groene corridor in stedelijk gebied', 1, 'Offerte', '2024-09-01', '2025-03-31', 180000.00, 'Amsterdam Nieuw-West', 2500.0, 'Stedelijk groen')
        ]
        
        cursor.executemany('''
            INSERT INTO projects (name, description, client_id, status, start_date, end_date, budget, location, area_size, project_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', projects_data)
        
        conn.commit()
        logger.info("Sample data initialized successfully!")
        logger.info("Created 3 suppliers, 3 plants, 4 products, 3 clients, and 3 projects.")
    
    conn.close()

# Custom JSON encoder for date objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def row_to_dict(row):
    """Convert sqlite3.Row to dictionary."""
    return dict(row) if row else None

def rows_to_dict_list(rows):
    """Convert list of sqlite3.Row to list of dictionaries."""
    return [dict(row) for row in rows]

# API Routes

@app.route('/api/', methods=['GET'])
def api_info():
    """API information endpoint."""
    return jsonify({
        'name': 'Landscape Architecture Management API',
        'version': '1.0.0',
        'description': 'RESTful API for managing landscape architecture projects',
        'endpoints': {
            'dashboard': '/api/dashboard/stats, /api/dashboard/recent-activity',
            'suppliers': '/api/suppliers',
            'plants': '/api/plants',
            'products': '/api/products',
            'clients': '/api/clients',
            'projects': '/api/projects'
        }
    })

# Dashboard endpoints
@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get counts
        cursor.execute('SELECT COUNT(*) as count FROM suppliers')
        suppliers_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM plants')
        plants_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM products')
        products_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM clients')
        clients_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM projects')
        projects_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM projects WHERE status = "In uitvoering"')
        active_projects = cursor.fetchone()['count']
        
        cursor.execute('SELECT SUM(budget) as total FROM projects WHERE status != "Geannuleerd"')
        total_budget = cursor.fetchone()['total'] or 0
        
        conn.close()
        
        return jsonify({
            'suppliers': suppliers_count,
            'plants': plants_count,
            'products': products_count,
            'clients': clients_count,
            'projects': projects_count,
            'active_projects': active_projects,
            'total_budget': total_budget
        })
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({'error': 'Failed to get dashboard statistics'}), 500

@app.route('/api/dashboard/recent-activity', methods=['GET'])
def get_recent_activity():
    """Get recent activity for dashboard."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get recent projects
        cursor.execute('''
            SELECT p.name, p.status, p.created_at, c.name as client_name
            FROM projects p
            LEFT JOIN clients c ON p.client_id = c.id
            ORDER BY p.created_at DESC
            LIMIT 5
        ''')
        recent_projects = rows_to_dict_list(cursor.fetchall())
        
        # Get recent suppliers
        cursor.execute('''
            SELECT name, specialization, created_at
            FROM suppliers
            ORDER BY created_at DESC
            LIMIT 3
        ''')
        recent_suppliers = rows_to_dict_list(cursor.fetchall())
        
        conn.close()
        
        return jsonify({
            'recent_projects': recent_projects,
            'recent_suppliers': recent_suppliers
        })
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return jsonify({'error': 'Failed to get recent activity'}), 500

# Suppliers endpoints
@app.route('/api/suppliers', methods=['GET', 'POST'])
def suppliers():
    """Handle suppliers - GET all or POST new."""
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM suppliers ORDER BY name')
            suppliers_list = rows_to_dict_list(cursor.fetchall())
            conn.close()
            return jsonify(suppliers_list)
        except Exception as e:
            logger.error(f"Error getting suppliers: {e}")
            return jsonify({'error': 'Failed to get suppliers'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO suppliers (name, contact_person, email, phone, address, city, postal_code, country, specialization)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('name'),
                data.get('contact_person'),
                data.get('email'),
                data.get('phone'),
                data.get('address'),
                data.get('city'),
                data.get('postal_code'),
                data.get('country', 'Nederland'),
                data.get('specialization')
            ))
            
            supplier_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({'id': supplier_id, 'message': 'Supplier created successfully'}), 201
        except Exception as e:
            logger.error(f"Error creating supplier: {e}")
            return jsonify({'error': 'Failed to create supplier'}), 500

@app.route('/api/suppliers/<int:supplier_id>', methods=['GET', 'PUT', 'DELETE'])
def supplier_detail(supplier_id):
    """Handle individual supplier operations."""
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM suppliers WHERE id = ?', (supplier_id,))
            supplier = row_to_dict(cursor.fetchone())
            conn.close()
            
            if supplier:
                return jsonify(supplier)
            else:
                return jsonify({'error': 'Supplier not found'}), 404
        except Exception as e:
            logger.error(f"Error getting supplier: {e}")
            return jsonify({'error': 'Failed to get supplier'}), 500
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE suppliers 
                SET name=?, contact_person=?, email=?, phone=?, address=?, city=?, postal_code=?, country=?, specialization=?
                WHERE id=?
            ''', (
                data.get('name'),
                data.get('contact_person'),
                data.get('email'),
                data.get('phone'),
                data.get('address'),
                data.get('city'),
                data.get('postal_code'),
                data.get('country', 'Nederland'),
                data.get('specialization'),
                supplier_id
            ))
            
            conn.commit()
            conn.close()
            
            return jsonify({'message': 'Supplier updated successfully'})
        except Exception as e:
            logger.error(f"Error updating supplier: {e}")
            return jsonify({'error': 'Failed to update supplier'}), 500
    
    elif request.method == 'DELETE':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM suppliers WHERE id = ?', (supplier_id,))
            conn.commit()
            conn.close()
            
            return jsonify({'message': 'Supplier deleted successfully'})
        except Exception as e:
            logger.error(f"Error deleting supplier: {e}")
            return jsonify({'error': 'Failed to delete supplier'}), 500

# Plants endpoints
@app.route('/api/plants', methods=['GET', 'POST'])
def plants():
    """Handle plants - GET all or POST new."""
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, s.name as supplier_name 
                FROM plants p 
                LEFT JOIN suppliers s ON p.supplier_id = s.id 
                ORDER BY p.name
            ''')
            plants_list = rows_to_dict_list(cursor.fetchall())
            conn.close()
            return jsonify(plants_list)
        except Exception as e:
            logger.error(f"Error getting plants: {e}")
            return jsonify({'error': 'Failed to get plants'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO plants (name, scientific_name, category, height_min, height_max, spread_min, spread_max,
                                  sun_requirements, water_requirements, soil_type, hardiness_zone, bloom_time,
                                  flower_color, foliage_color, growth_rate, maintenance_level, price, supplier_id, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('name'),
                data.get('scientific_name'),
                data.get('category'),
                data.get('height_min'),
                data.get('height_max'),
                data.get('spread_min'),
                data.get('spread_max'),
                data.get('sun_requirements'),
                data.get('water_requirements'),
                data.get('soil_type'),
                data.get('hardiness_zone'),
                data.get('bloom_time'),
                data.get('flower_color'),
                data.get('foliage_color'),
                data.get('growth_rate'),
                data.get('maintenance_level'),
                data.get('price'),
                data.get('supplier_id'),
                data.get('description')
            ))
            
            plant_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({'id': plant_id, 'message': 'Plant created successfully'}), 201
        except Exception as e:
            logger.error(f"Error creating plant: {e}")
            return jsonify({'error': 'Failed to create plant'}), 500

# Products endpoints
@app.route('/api/products', methods=['GET', 'POST'])
def products():
    """Handle products - GET all or POST new."""
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, s.name as supplier_name 
                FROM products p 
                LEFT JOIN suppliers s ON p.supplier_id = s.id 
                ORDER BY p.name
            ''')
            products_list = rows_to_dict_list(cursor.fetchall())
            conn.close()
            return jsonify(products_list)
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return jsonify({'error': 'Failed to get products'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO products (name, category, description, unit, price, stock_quantity, supplier_id, sku)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('name'),
                data.get('category'),
                data.get('description'),
                data.get('unit'),
                data.get('price'),
                data.get('stock_quantity', 0),
                data.get('supplier_id'),
                data.get('sku')
            ))
            
            product_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({'id': product_id, 'message': 'Product created successfully'}), 201
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            return jsonify({'error': 'Failed to create product'}), 500

# Clients endpoints
@app.route('/api/clients', methods=['GET', 'POST'])
def clients():
    """Handle clients - GET all or POST new."""
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients ORDER BY name')
            clients_list = rows_to_dict_list(cursor.fetchall())
            conn.close()
            return jsonify(clients_list)
        except Exception as e:
            logger.error(f"Error getting clients: {e}")
            return jsonify({'error': 'Failed to get clients'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO clients (name, type, contact_person, email, phone, address, city, postal_code, country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('name'),
                data.get('type'),
                data.get('contact_person'),
                data.get('email'),
                data.get('phone'),
                data.get('address'),
                data.get('city'),
                data.get('postal_code'),
                data.get('country', 'Nederland')
            ))
            
            client_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({'id': client_id, 'message': 'Client created successfully'}), 201
        except Exception as e:
            logger.error(f"Error creating client: {e}")
            return jsonify({'error': 'Failed to create client'}), 500

# Projects endpoints
@app.route('/api/projects', methods=['GET', 'POST'])
def projects():
    """Handle projects - GET all or POST new."""
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, c.name as client_name 
                FROM projects p 
                LEFT JOIN clients c ON p.client_id = c.id 
                ORDER BY p.created_at DESC
            ''')
            projects_list = rows_to_dict_list(cursor.fetchall())
            conn.close()
            return jsonify(projects_list)
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return jsonify({'error': 'Failed to get projects'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO projects (name, description, client_id, status, start_date, end_date, budget, location, area_size, project_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('name'),
                data.get('description'),
                data.get('client_id'),
                data.get('status', 'Planning'),
                data.get('start_date'),
                data.get('end_date'),
                data.get('budget'),
                data.get('location'),
                data.get('area_size'),
                data.get('project_type')
            ))
            
            project_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({'id': project_id, 'message': 'Project created successfully'}), 201
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return jsonify({'error': 'Failed to create project'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Initializing sample data...")
    init_database()
    logger.info("Starting Landscape Architecture Management System...")
    logger.info("Backend API will be available at: http://127.0.0.1:5001")
    logger.info("API documentation available at: http://127.0.0.1:5001/api/")
    
    app.run(host='127.0.0.1', port=5001, debug=True)

