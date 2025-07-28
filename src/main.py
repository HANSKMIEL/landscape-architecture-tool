#!/usr/bin/env python3
"""
Landscape Architecture Management System - Backend API
Refactored modular version with persistent database
"""

import logging
import os
import sys
from datetime import datetime

from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configuration
from src.config import get_config

# Import models and database
from src.models.user import db

# Import schemas
from src.schemas import (
    ClientCreateSchema,
    ClientUpdateSchema,
    PlantCreateSchema,
    PlantUpdateSchema,
    ProductCreateSchema,
    ProductUpdateSchema,
    ProjectCreateSchema,
    ProjectUpdateSchema,
    ProjectPlantCreateSchema,
    ProjectPlantUpdateSchema,
    SupplierCreateSchema,
    SupplierUpdateSchema,
)

# Import services
from src.services import (
    ClientService,
    DashboardService,
    PlantService,
    ProductService,
    ProjectService,
    SupplierService,
)
from src.utils.db_init import initialize_database, populate_sample_data

# Import utilities
from src.utils.error_handlers import handle_errors, register_error_handlers

# Import route blueprints
from src.routes.plant_recommendations import plant_recommendations_bp
from src.routes.project_plants import project_plants_bp


# Configure logging
def configure_logging(app):
    """Configure logging based on environment"""
    log_level = getattr(logging, app.config["LOG_LEVEL"].upper())

    if not app.debug:
        # Production logging
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
        )
    else:
        # Development logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


logger = logging.getLogger(__name__)


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    config = get_config()
    app.config.from_object(config)

    # Configure logging
    configure_logging(app)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # CORS configuration
    CORS(app, origins=app.config["CORS_ORIGINS"])

    # Rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[app.config["RATELIMIT_DEFAULT"]],
    )
    limiter.init_app(app)

    # Register error handlers
    register_error_handlers(app)

    # Register route blueprints
    app.register_blueprint(plant_recommendations_bp)
    app.register_blueprint(project_plants_bp)

    # Initialize services
    supplier_service = SupplierService()
    plant_service = PlantService()
    product_service = ProductService()
    client_service = ClientService()
    project_service = ProjectService()
    dashboard_service = DashboardService()

    # API Routes
    @app.route("/api/", methods=["GET"])
    @handle_errors
    def api_documentation():
        """API documentation endpoint"""
        return jsonify(
            {
                "name": "Landscape Architecture Management API",
                "version": "2.0.0",
                "description": "Modular backend API with persistent database",
                "endpoints": {
                    "dashboard": {
                        "stats": "/api/dashboard/stats",
                        "recent_activity": "/api/dashboard/recent-activity",
                    },
                    "suppliers": "/api/suppliers",
                    "plants": "/api/plants",
                    "products": "/api/products",
                    "clients": "/api/clients",
                    "projects": "/api/projects",
                    "plant_recommendations": {
                        "recommendations": "/api/plant-recommendations",
                        "criteria_options": "/api/plant-recommendations/criteria-options",
                        "feedback": "/api/plant-recommendations/feedback",
                        "history": "/api/plant-recommendations/history",
                        "export": "/api/plant-recommendations/export",
                        "import": "/api/plant-recommendations/import"
                    },
                },
                "status": "operational",
                "database": "persistent",
            }
        )

    # Dashboard endpoints
    @app.route("/api/dashboard/stats", methods=["GET"])
    @handle_errors
    def get_dashboard_stats():
        """Get dashboard statistics"""
        stats = dashboard_service.get_stats()
        return jsonify(stats)

    @app.route("/api/dashboard/recent-activity", methods=["GET"])
    @handle_errors
    def get_recent_activity():
        """Get recent activity for dashboard"""
        activities = dashboard_service.get_recent_activity()
        return jsonify(activities)

    # Suppliers endpoints
    @app.route("/api/suppliers", methods=["GET"])
    @handle_errors
    def get_suppliers():
        """Get all suppliers"""
        from flask import request

        search = request.args.get("search", "")
        result = supplier_service.get_all(search=search)
        return jsonify(
            result["suppliers"] if "suppliers" in result else result["items"]
        )

    @app.route("/api/suppliers", methods=["POST"])
    @handle_errors
    def create_supplier():
        """Create new supplier"""
        from flask import request

        data = request.get_json()

        # Validate input
        schema = SupplierCreateSchema(**data)
        validated_data = schema.model_dump(exclude_unset=True)

        supplier = supplier_service.create(validated_data)
        return jsonify(supplier), 201

    @app.route("/api/suppliers/<int:supplier_id>", methods=["PUT"])
    @handle_errors
    def update_supplier(supplier_id):
        """Update supplier"""
        from flask import request

        data = request.get_json()

        # Validate input
        schema = SupplierUpdateSchema(**data)
        validated_data = schema.model_dump(exclude_unset=True)

        supplier = supplier_service.update(supplier_id, validated_data)
        if not supplier:
            return jsonify({"error": "Supplier not found"}), 404

        return jsonify(supplier)

    @app.route("/api/suppliers/<int:supplier_id>", methods=["DELETE"])
    @handle_errors
    def delete_supplier(supplier_id):
        """Delete supplier"""
        success = supplier_service.delete(supplier_id)
        if not success:
            return jsonify({"error": "Supplier not found"}), 404

        return jsonify({"message": "Supplier deleted successfully"})

    # Plants endpoints
    @app.route("/api/plants", methods=["GET"])
    @handle_errors
    def get_plants():
        """Get all plants"""
        from flask import request

        search = request.args.get("search", "")
        result = plant_service.get_all(search=search)
        return jsonify(
            result["plants"] if "plants" in result else result["items"]
        )

    @app.route("/api/plants", methods=["POST"])
    @handle_errors
    def create_plant():
        """Create new plant"""
        from flask import request

        data = request.get_json()

        # Validate input
        schema = PlantCreateSchema(**data)
        validated_data = schema.model_dump(exclude_unset=True)

        plant = plant_service.create(validated_data)
        return jsonify(plant), 201

    @app.route("/api/plants/<int:plant_id>", methods=["PUT"])
    @handle_errors
    def update_plant(plant_id):
        """Update plant"""
        from flask import request

        data = request.get_json()

        # Validate input
        schema = PlantUpdateSchema(**data)
        validated_data = schema.model_dump(exclude_unset=True)

        plant = plant_service.update(plant_id, validated_data)
        if not plant:
            return jsonify({"error": "Plant not found"}), 404

        return jsonify(plant)

    @app.route("/api/plants/<int:plant_id>", methods=["DELETE"])
    @handle_errors
    def delete_plant(plant_id):
        """Delete plant"""
        success = plant_service.delete(plant_id)
        if not success:
            return jsonify({"error": "Plant not found"}), 404

        return jsonify({"message": "Plant deleted successfully"})

    # Products endpoints
    @app.route("/api/products", methods=["GET"])
    @handle_errors
    def get_products():
        """Get all products"""
        from flask import request

        search = request.args.get("search", "")
        result = product_service.get_all(search=search)
        return jsonify(
            result["products"] if "products" in result else result["items"]
        )

    @app.route("/api/products", methods=["POST"])
    @handle_errors
    def create_product():
        """Create new product"""
        from flask import request

        data = request.get_json()

        # Validate input
        schema = ProductCreateSchema(**data)
        validated_data = schema.model_dump(exclude_unset=True)

        product = product_service.create(validated_data)
        return jsonify(product), 201

    @app.route("/api/products/<int:product_id>", methods=["PUT"])
    @handle_errors
    def update_product(product_id):
        """Update product"""
        from flask import request

        data = request.get_json()

        # Validate input
        schema = ProductUpdateSchema(**data)
        validated_data = schema.model_dump(exclude_unset=True)

        product = product_service.update(product_id, validated_data)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        return jsonify(product)

    @app.route("/api/products/<int:product_id>", methods=["DELETE"])
    @handle_errors
    def delete_product(product_id):
        """Delete product"""
        success = product_service.delete(product_id)
        if not success:
            return jsonify({"error": "Product not found"}), 404

        return jsonify({"message": "Product deleted successfully"})

    # Clients endpoints
    @app.route("/api/clients", methods=["GET"])
    @handle_errors
    def get_clients():
        """Get all clients"""
        from flask import request

        search = request.args.get("search", "")
        result = client_service.get_all(search=search)
        return jsonify(
            result["clients"] if "clients" in result else result["items"]
        )

    @app.route("/api/clients", methods=["POST"])
    @handle_errors
    def create_client():
        """Create new client"""
        from flask import request

        data = request.get_json()

        # Validate input
        schema = ClientCreateSchema(**data)
        validated_data = schema.model_dump(exclude_unset=True)

        # Add registration date if not provided
        if "registration_date" not in validated_data:
            validated_data["registration_date"] = datetime.now().strftime(
                "%Y-%m-%d"
            )

        client = client_service.create(validated_data)
        return jsonify(client), 201

    @app.route("/api/clients/<int:client_id>", methods=["PUT"])
    @handle_errors
    def update_client(client_id):
        """Update client"""
        from flask import request

        data = request.get_json()

        # Validate input
        schema = ClientUpdateSchema(**data)
        validated_data = schema.model_dump(exclude_unset=True)

        client = client_service.update(client_id, validated_data)
        if not client:
            return jsonify({"error": "Client not found"}), 404

        return jsonify(client)

    @app.route("/api/clients/<int:client_id>", methods=["DELETE"])
    @handle_errors
    def delete_client(client_id):
        """Delete client"""
        success = client_service.delete(client_id)
        if not success:
            return jsonify({"error": "Client not found"}), 404

        return jsonify({"message": "Client deleted successfully"})

    # Projects endpoints
    @app.route("/api/projects", methods=["GET"])
    @handle_errors
    def get_projects():
        """Get all projects"""
        from flask import request

        search = request.args.get("search", "")
        client_id = request.args.get("client_id")
        client_id = int(client_id) if client_id else None

        result = project_service.get_all(search=search, client_id=client_id)
        return jsonify(
            result["projects"] if "projects" in result else result["items"]
        )

    @app.route("/api/projects", methods=["POST"])
    @handle_errors
    def create_project():
        """Create new project"""
        from flask import request

        data = request.get_json()

        # Validate input
        schema = ProjectCreateSchema(**data)
        validated_data = schema.model_dump(exclude_unset=True)

        project = project_service.create(validated_data)
        return jsonify(project), 201

    @app.route("/api/projects/<int:project_id>", methods=["PUT"])
    @handle_errors
    def update_project(project_id):
        """Update project"""
        from flask import request

        data = request.get_json()

        # Validate input
        schema = ProjectUpdateSchema(**data)
        validated_data = schema.model_dump(exclude_unset=True)

        project = project_service.update(project_id, validated_data)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        return jsonify(project)

    @app.route("/api/projects/<int:project_id>", methods=["DELETE"])
    @handle_errors
    def delete_project(project_id):
        """Delete project"""
        success = project_service.delete(project_id)
        if not success:
            return jsonify({"error": "Project not found"}), 404

        return jsonify({"message": "Project deleted successfully"})

    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint"""
        return jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0",
                "database_status": "connected",
                "environment": os.environ.get("FLASK_ENV", "development"),
            }
        )

    # Add security headers
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        if app.config.get("SESSION_COOKIE_SECURE"):
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    return app


# Create the application only when run directly
def main():
    """Main entry point for development server"""
    app = create_app()

    logger.info("Starting Landscape Architecture Management System...")
    logger.info("Backend API will be available at: http://127.0.0.1:5001")
    logger.info("API documentation available at: http://127.0.0.1:5001/api/")

    with app.app_context():
        # Initialize database
        initialize_database()

        # Populate with sample data if empty
        populate_sample_data()

    # Start the Flask development server (only in development)
    if os.environ.get("FLASK_ENV", "development") == "development":
        app.run(host="127.0.0.1", port=5001, debug=True, use_reloader=True)
    else:
        logger.warning(
            "Use a production WSGI server (like Gunicorn) instead of Flask dev server"
        )
        print(
            "For production, use: gunicorn -c gunicorn.conf.py wsgi:application"
        )


# Create app instance for WSGI servers (like Waitress, Gunicorn)
app = create_app()


if __name__ == "__main__":
    main()
