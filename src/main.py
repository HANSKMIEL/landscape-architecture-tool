"""
Corrected main.py with proper imports
Replace your current src/main.py with this version
"""

from flask import Flask, jsonify
from flask_cors import CORS
from src.models.landscape import db
from src.utils.sample_data import initialize_sample_data
import os

def create_app():
    app = Flask(__name__)
    
    # Configure database
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "landscape.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # Enable CORS for all routes
    CORS(app, origins="*")
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        initialize_sample_data()
    
    # Import and register blueprints
    from src.routes.suppliers import suppliers_bp
    from src.routes.plants import plants_bp
    
    app.register_blueprint(suppliers_bp, url_prefix='/api')
    app.register_blueprint(plants_bp, url_prefix='/api')
    
    # Dashboard routes
    @app.route('/api/dashboard/stats', methods=['GET'])
    def get_dashboard_stats():
        """Get dashboard statistics"""
        try:
            from src.models.landscape import Supplier, Product, Plant, Client, Project
            
            # Count all entities
            suppliers_count = Supplier.query.count()
            plants_count = Plant.query.count()
            products_count = Product.query.count() if hasattr(Product, 'query') else 0
            clients_count = Client.query.count() if hasattr(Client, 'query') else 0
            projects_count = Project.query.count() if hasattr(Project, 'query') else 0
            
            # Calculate project statistics
            active_projects = 0
            completed_projects = 0
            try:
                if hasattr(Project, 'query'):
                    active_projects = Project.query.filter_by(status='in_progress').count()
                    completed_projects = Project.query.filter_by(status='completed').count()
            except:
                pass
            
            # Calculate budget statistics
            total_budget = 50000  # Sample data
            total_spent = 32000   # Sample data
            
            stats = {
                'suppliers': suppliers_count,
                'plants': plants_count,
                'products': products_count,
                'clients': clients_count,
                'projects': projects_count,
                'active_projects': active_projects,
                'completed_projects': completed_projects,
                'total_budget': total_budget,
                'total_spent': total_spent,
                'budget_remaining': total_budget - total_spent
            }
            
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/dashboard/recent-activity', methods=['GET'])
    def get_recent_activity():
        """Get recent activity feed"""
        try:
            from src.models.landscape import Supplier, Plant
            from datetime import datetime, timedelta
            
            activities = []
            
            # Get recent suppliers
            recent_suppliers = Supplier.query.order_by(Supplier.date_added.desc()).limit(3).all()
            for supplier in recent_suppliers:
                activities.append({
                    'type': 'supplier_added',
                    'title': f'New supplier added: {supplier.name}',
                    'description': f'Contact: {supplier.contact_person}',
                    'date': supplier.date_added.isoformat(),
                    'icon': 'building'
                })
            
            # Get recent plants
            recent_plants = Plant.query.order_by(Plant.id.desc()).limit(3).all()
            for plant in recent_plants:
                activities.append({
                    'type': 'plant_added',
                    'title': f'New plant added: {plant.common_name}',
                    'description': f'Scientific name: {plant.scientific_name}',
                    'date': datetime.utcnow().isoformat(),
                    'icon': 'leaf'
                })
            
            # Add some sample project activities
            activities.extend([
                {
                    'type': 'project_updated',
                    'title': 'Project: Vondelpark Renovation',
                    'description': 'Status: In Progress',
                    'date': datetime.utcnow().isoformat(),
                    'icon': 'briefcase'
                },
                {
                    'type': 'project_completed',
                    'title': 'Project: Private Garden Design',
                    'description': 'Successfully completed',
                    'date': (datetime.utcnow() - timedelta(days=1)).isoformat(),
                    'icon': 'check-circle'
                }
            ])
            
            # Sort activities by date (most recent first)
            activities.sort(key=lambda x: x['date'], reverse=True)
            
            return jsonify({'activities': activities[:10]})
        except Exception as e:
            return jsonify({'error': str(e), 'activities': []}), 500
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'Landscape Architecture API is running'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting Landscape Architecture Backend...")
    print("Backend will be available at: http://127.0.0.1:5001")
    print("API endpoints:")
    print("  - http://127.0.0.1:5001/api/suppliers")
    print("  - http://127.0.0.1:5001/api/plants")
    print("  - http://127.0.0.1:5001/api/dashboard/stats")
    print("  - http://127.0.0.1:5001/api/dashboard/recent-activity")
    app.run(host='0.0.0.0', port=5001, debug=True)

