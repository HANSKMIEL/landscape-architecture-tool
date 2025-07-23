# Updated Main Application File
# File location: src/main.py
# This file includes all the new API routes and configurations

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.landscape import db
from src.utils.sample_data import initialize_sample_data

def create_app():
    app = Flask(__name__, static_folder='../static', static_url_path='')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///landscape.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Enable CORS for all routes
    CORS(app, origins=['*'])
    
    # Initialize database
    db.init_app(app)
    
    # Import and register blueprints
    from src.routes.dashboard import dashboard_bp
    from src.routes.suppliers import suppliers_bp
    from src.routes.plants import plants_bp
    from src.routes.products import products_bp
    from src.routes.clients import clients_bp
    from src.routes.projects import projects_bp
    from src.routes.reports import reports_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(plants_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(reports_bp)
    
    # Serve React frontend
    @app.route('/')
    def serve_frontend():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_static_files(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    # Create tables and initialize sample data
    with app.app_context():
        db.create_all()
        initialize_sample_data()
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)

