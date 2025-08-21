#!/usr/bin/env python3
"""
Landscape Architecture Management System - Backend API
Refactored modular version with persistent database
"""

import logging
import os
import sys
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Validate critical dependencies before importing Flask components
from src.utils.dependency_validator import DependencyValidator  # noqa: E402

# Ensure critical production dependencies are available
dependency_validator = DependencyValidator()
dependency_validator.ensure_critical_dependencies()

from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

from src.config import get_config  # noqa: E402
from src.models.user import db  # noqa: E402
from src.routes.plant_recommendations import plant_recommendations_bp  # noqa: E402
from src.routes.project_plants import project_plants_bp  # noqa: E402
from src.routes.reports import reports_bp  # noqa: E402
from src.schemas import ClientCreateSchema  # noqa: E402
from src.schemas import ClientUpdateSchema  # noqa: E402
from src.schemas import (
    PlantCreateSchema,
    PlantUpdateSchema,
    ProductCreateSchema,
    ProductUpdateSchema,
    ProjectCreateSchema,
    ProjectUpdateSchema,
    SupplierCreateSchema,
    SupplierUpdateSchema,
)
from src.services import ClientService  # noqa: E402
from src.services import PlantService  # noqa: E402
from src.services import ProductService, ProjectService, SupplierService
from src.services.analytics import AnalyticsService  # noqa: E402
from src.services.dashboard_service import DashboardService  # noqa: E402
from src.utils.db_init import initialize_database  # noqa: E402
from src.utils.db_init import populate_sample_data
from src.utils.error_handlers import handle_errors  # noqa: E402
from src.utils.error_handlers import register_error_handlers  # noqa: E402


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
logger.setLevel(logging.ERROR)


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

    # Rate limiting - configure properly based on storage type
    storage_url = app.config.get("RATELIMIT_STORAGE_URL", "memory://")

    if storage_url.startswith("redis://"):
        # Try Redis connection, fall back to memory if Redis unavailable
        try:
            import redis

            # Test Redis connection
            r = redis.from_url(storage_url)
            r.ping()
            limiter = Limiter(
                key_func=get_remote_address,
                default_limits=[app.config["RATELIMIT_DEFAULT"]],
            )
        except (
            ImportError,
            redis.ConnectionError,
            redis.RedisError,
            ConnectionError,
            OSError,
            Exception,
        ):
            logger.info("Redis unavailable, using in-memory rate limiting")
            limiter = Limiter(
                key_func=get_remote_address,
                default_limits=[app.config["RATELIMIT_DEFAULT"]],
                storage_uri="memory://",
            )
    else:
        # Use memory storage without warnings
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[app.config["RATELIMIT_DEFAULT"]],
            storage_uri="memory://",
        )

    limiter.init_app(app)

    # Register error handlers
    register_error_handlers(app)

    # Register route blueprints
    app.register_blueprint(plant_recommendations_bp)
    app.register_blueprint(project_plants_bp)
    app.register_blueprint(reports_bp)

    # Register performance monitoring blueprint
    from src.routes.performance import performance_bp

    app.register_blueprint(performance_bp)

    # Initialize services
    supplier_service = SupplierService()
    plant_service = PlantService()
    product_service = ProductService()
    client_service = ClientService()
    project_service = ProjectService()
    dashboard_service = DashboardService()
    analytics_service = AnalyticsService()

    # Health check endpoint with dependency validation
    @app.route("/health", methods=["GET"])
    @handle_errors
    def health_check():
        """
        Enhanced health check endpoint that validates both system health
        and critical dependency availability.
        """
        from src.utils.dependency_validator import DependencyValidator

        validator = DependencyValidator()
        critical_ok, missing_critical = validator.validate_critical_dependencies()
        available_optional, missing_optional = (
            validator.validate_optional_dependencies()
        )

        # Database connectivity check
        db_status = "unknown"
        try:
            # Simple database connectivity test
            db.session.execute(text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            db_status = "error"
            logger.warning(f"Database connectivity issue in health check: {e}")

        health_data = {
            "status": "healthy" if critical_ok else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {
                "critical": {
                    "status": "ok" if critical_ok else "missing",
                    "missing": missing_critical,
                    "total": len(validator.CRITICAL_DEPENDENCIES),
                    "available": len(validator.CRITICAL_DEPENDENCIES)
                    - len(missing_critical),
                },
                "optional": {
                    "total": len(validator.OPTIONAL_DEPENDENCIES),
                    "available": available_optional,
                    "missing": missing_optional,
                },
            },
            "database": {"status": db_status},
            "services": {
                "web_server": "running",
                "rate_limiting": "active" if limiter else "disabled",
            },
        }

        if not critical_ok:
            # Return 503 Service Unavailable if critical dependencies are missing
            health_data["message"] = (
                "Critical dependencies missing - application may not function properly"
            )
            return jsonify(health_data), 503
        elif missing_optional:
            health_data["message"] = (
                "Some optional features may be limited due to missing dependencies"
            )

        return jsonify(health_data)

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
                    "analytics": {
                        "plant_usage": "/api/analytics/plant-usage",
                        "project_performance": "/api/analytics/project-performance",
                        "client_insights": "/api/analytics/client-insights",
                        "financial": "/api/analytics/financial",
                        "recommendation_effectiveness": (
                            "/api/analytics/recommendation-effectiveness"
                        ),
                    },
                    "suppliers": "/api/suppliers",
                    "plants": "/api/plants",
                    "products": "/api/products",
                    "clients": "/api/clients",
                    "projects": "/api/projects",
                    "plant_recommendations": {
                        "recommendations": "/api/plant-recommendations",
                        "criteria_options": (
                            "/api/plant-recommendations/criteria-options"
                        ),
                        "feedback": "/api/plant-recommendations/feedback",
                        "history": "/api/plant-recommendations/history",
                        "export": "/api/plant-recommendations/export",
                        "import": "/api/plant-recommendations/import",
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

    # Analytics endpoints
    @app.route("/api/analytics/plant-usage", methods=["GET"])
    @handle_errors
    def get_plant_usage_analytics():
        """Get plant usage analytics"""
        from flask import request

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        date_range = (start_date, end_date) if start_date or end_date else None

        analytics = analytics_service.get_plant_usage_analytics(date_range)
        return jsonify(analytics)

    @app.route("/api/analytics/project-performance", methods=["GET"])
    @handle_errors
    def get_project_performance_analytics():
        """Get project performance analytics"""
        from flask import request

        project_id = request.args.get("project_id")
        project_id = int(project_id) if project_id else None

        analytics = analytics_service.get_project_performance_metrics(project_id)
        return jsonify(analytics)

    @app.route("/api/analytics/client-insights", methods=["GET"])
    @handle_errors
    def get_client_insights_analytics():
        """Get client relationship insights"""
        analytics = analytics_service.get_client_relationship_insights()
        return jsonify(analytics)

    @app.route("/api/analytics/financial", methods=["GET"])
    @handle_errors
    def get_financial_analytics():
        """Get financial analytics"""
        from flask import request

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if not start_date or not end_date:
            # Default to last 12 months
            from datetime import datetime, timedelta

            end_date = datetime.now().isoformat()
            start_date = (datetime.now() - timedelta(days=365)).isoformat()

        analytics = analytics_service.get_financial_reporting((start_date, end_date))
        return jsonify(analytics)

    @app.route("/api/analytics/recommendation-effectiveness", methods=["GET"])
    @handle_errors
    def get_recommendation_effectiveness_analytics():
        """Get recommendation system effectiveness analytics"""
        analytics = analytics_service.get_recommendation_effectiveness()
        return jsonify(analytics)

    # Suppliers endpoints
    @app.route("/api/suppliers", methods=["GET"])
    @handle_errors
    def get_suppliers():
        """Get all suppliers"""
        from flask import request

        search = request.args.get("search", "")
        specialization = request.args.get("specialization", "")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)

        # Handle specialization filter
        if specialization:
            # Filter suppliers by specialization manually for now
            from sqlalchemy import or_

            from src.models.landscape import Supplier

            query = Supplier.query
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Supplier.name.ilike(search_term),
                        Supplier.contact_person.ilike(search_term),
                        Supplier.email.ilike(search_term),
                        Supplier.city.ilike(search_term),
                    )
                )

            query = query.filter(Supplier.specialization.ilike(f"%{specialization}%"))

            paginated = query.order_by(Supplier.name).paginate(
                page=page, per_page=per_page, error_out=False
            )

            result = {
                "suppliers": [supplier.to_dict() for supplier in paginated.items],
                "total": paginated.total,
                "pages": paginated.pages,
                "current_page": page,
            }
        else:
            result = supplier_service.get_all(
                search=search, page=page, per_page=per_page
            )

        return jsonify(result)

    @app.route("/api/suppliers/<int:supplier_id>", methods=["GET"])
    @handle_errors
    def get_supplier(supplier_id):
        """Get specific supplier by ID"""
        from src.models.landscape import Supplier

        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return jsonify({"error": "Supplier not found"}), 404

        return jsonify(supplier.to_dict())

    @app.route("/api/suppliers", methods=["POST"])
    @handle_errors
    def create_supplier():
        """Create new supplier"""
        from flask import request
        from pydantic import ValidationError

        data = request.get_json()

        try:
            # Validate input
            schema = SupplierCreateSchema(**data)
            validated_data = schema.model_dump(exclude_unset=True)

            supplier = supplier_service.create(validated_data)
            return jsonify(supplier), 201
        except ValidationError as e:
            # Convert Pydantic errors to string format for consistency
            error_messages = [error.get("msg", str(error)) for error in e.errors()]
            return (
                jsonify(
                    {"error": "Validation failed", "validation_errors": error_messages}
                ),
                422,
            )
        except ValueError as e:
            logger.error("Validation error occurred: %s", str(e))
            return (
                jsonify({"error": "Validation failed", "validation_errors": [str(e)]}),
                422,
            )

    @app.route("/api/suppliers/<int:supplier_id>", methods=["PUT"])
    @handle_errors
    def update_supplier(supplier_id):
        """Update supplier"""
        from flask import request
        from pydantic import ValidationError

        data = request.get_json()

        try:
            # Validate input
            schema = SupplierUpdateSchema(**data)
            validated_data = schema.model_dump(exclude_unset=True)

            supplier = supplier_service.update(supplier_id, validated_data)
            if not supplier:
                return jsonify({"error": "Supplier not found"}), 404

            return jsonify(supplier)
        except ValidationError as e:
            # Convert Pydantic errors to string format for consistency
            error_messages = [error.get("msg", str(error)) for error in e.errors()]
            return (
                jsonify(
                    {"error": "Validation failed", "validation_errors": error_messages}
                ),
                422,
            )
        except ValueError as e:
            return (
                jsonify({"error": "Validation failed", "validation_errors": [str(e)]}),
                422,
            )

    @app.route("/api/suppliers/<int:supplier_id>", methods=["DELETE"])
    @handle_errors
    def delete_supplier(supplier_id):
        """Delete supplier"""
        try:
            success = supplier_service.delete(supplier_id)
            if not success:
                return jsonify({"error": "Supplier not found"}), 404

            return jsonify({"message": "Supplier deleted successfully"})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    # Additional supplier endpoints
    @app.route("/api/suppliers/<int:supplier_id>/products", methods=["GET"])
    @handle_errors
    def get_supplier_products(supplier_id):
        """Get products for a specific supplier"""
        from src.models.landscape import Product, Supplier

        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return jsonify({"error": "Supplier not found"}), 404

        products = Product.query.filter_by(supplier_id=supplier_id).all()
        return jsonify({"products": [product.to_dict() for product in products]})

    @app.route("/api/suppliers/<int:supplier_id>/products", methods=["POST"])
    @handle_errors
    def add_product_to_supplier(supplier_id):
        """Add a product to a specific supplier"""
        from flask import request
        from pydantic import ValidationError

        from src.models.landscape import Supplier

        # Check if supplier exists
        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return jsonify({"error": "Supplier not found"}), 404

        data = request.get_json()

        try:
            # Add supplier_id to the data
            data["supplier_id"] = supplier_id

            # Validate input
            schema = ProductCreateSchema(**data)
            validated_data = schema.model_dump(exclude_unset=True)

            product = product_service.create(validated_data)
            return jsonify(product), 201
        except ValidationError as e:
            # Convert Pydantic errors to string format for consistency
            error_messages = [error.get("msg", str(error)) for error in e.errors()]
            return (
                jsonify(
                    {"error": "Validation failed", "validation_errors": error_messages}
                ),
                422,
            )

    @app.route("/api/suppliers/<int:supplier_id>/plants", methods=["GET"])
    @handle_errors
    def get_supplier_plants(supplier_id):
        """Get plants for a specific supplier"""
        from src.models.landscape import Plant, Supplier

        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return jsonify({"error": "Supplier not found"}), 404

        plants = Plant.query.filter_by(supplier_id=supplier_id).all()
        return jsonify({"plants": [plant.to_dict() for plant in plants]})

    @app.route("/api/suppliers/<int:supplier_id>/statistics", methods=["GET"])
    @handle_errors
    def get_supplier_statistics(supplier_id):
        """Get statistics for a specific supplier"""
        from sqlalchemy import func  # noqa: F401

        from src.models.landscape import Plant, Product, Supplier

        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return jsonify({"error": "Supplier not found"}), 404

        # Count products and plants
        product_count = Product.query.filter_by(supplier_id=supplier_id).count()
        plant_count = Plant.query.filter_by(supplier_id=supplier_id).count()

        # Calculate inventory value (products only, since they have stock_quantity)
        products = Product.query.filter_by(supplier_id=supplier_id).all()
        total_inventory_value = sum(
            (product.price or 0) * (product.stock_quantity or 0) for product in products
        )

        # Calculate average prices
        product_prices = [product.price for product in products if product.price]
        average_product_price = (
            sum(product_prices) / len(product_prices) if product_prices else 0
        )

        plants = Plant.query.filter_by(supplier_id=supplier_id).all()
        plant_prices = [plant.price for plant in plants if plant.price]
        average_plant_price = (
            sum(plant_prices) / len(plant_prices) if plant_prices else 0
        )

        return jsonify(
            {
                "supplier_id": supplier_id,
                "supplier_name": supplier.name,
                "product_count": product_count,
                "plant_count": plant_count,
                "total_items": product_count + plant_count,
                "total_products": product_count,  # For backward compatibility
                "total_plants": plant_count,  # For backward compatibility
                "total_inventory_value": total_inventory_value,
                "average_product_price": average_product_price,
                "average_plant_price": average_plant_price,
            }
        )

    @app.route("/api/suppliers/specializations", methods=["GET"])
    @handle_errors
    def get_supplier_specializations():
        """Get all unique supplier specializations"""
        from sqlalchemy import distinct

        from src.models.landscape import Supplier

        specializations = (
            db.session.query(distinct(Supplier.specialization))
            .filter(Supplier.specialization.isnot(None))
            .all()
        )

        return jsonify({"specializations": [spec[0] for spec in specializations]})

    @app.route("/api/suppliers/top", methods=["GET"])
    @handle_errors
    def get_top_suppliers():
        """Get top suppliers by product/plant count"""
        from flask import request
        from sqlalchemy import func  # noqa: F401

        from src.models.landscape import Plant, Product, Supplier

        limit = request.args.get("limit", 10, type=int)

        # Get suppliers with their item counts using subqueries

        # Subquery for product counts
        product_counts = (
            db.session.query(
                Product.supplier_id, func.count(Product.id).label("product_count")
            )
            .group_by(Product.supplier_id)
            .subquery()
        )

        # Subquery for plant counts
        plant_counts = (
            db.session.query(
                Plant.supplier_id, func.count(Plant.id).label("plant_count")
            )
            .group_by(Plant.supplier_id)
            .subquery()
        )

        # Main query
        top_suppliers = (
            db.session.query(
                Supplier,
                func.coalesce(product_counts.c.product_count, 0).label("product_count"),
                func.coalesce(plant_counts.c.plant_count, 0).label("plant_count"),
            )
            .outerjoin(product_counts, Supplier.id == product_counts.c.supplier_id)
            .outerjoin(plant_counts, Supplier.id == plant_counts.c.supplier_id)
            .order_by(
                (
                    func.coalesce(product_counts.c.product_count, 0)
                    + func.coalesce(plant_counts.c.plant_count, 0)
                ).desc()
            )
            .limit(limit)
            .all()
        )

        suppliers_list = []
        for supplier, product_count, plant_count in top_suppliers:
            suppliers_list.append(
                {
                    "supplier": supplier.to_dict(),
                    "product_count": product_count,
                    "plant_count": plant_count,
                    "total_items": product_count + plant_count,
                }
            )

        return jsonify({"suppliers": suppliers_list})

    @app.route("/api/suppliers/<int:supplier_id>/contact", methods=["GET"])
    @handle_errors
    def get_supplier_contact(supplier_id):
        """Get contact information for a specific supplier"""
        from src.models.landscape import Supplier

        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return jsonify({"error": "Supplier not found"}), 404

        # Build full address
        address_parts = []
        if supplier.address:
            address_parts.append(supplier.address)
        if supplier.city:
            address_parts.append(supplier.city)
        if supplier.postal_code:
            # Add postal code with just a space (no comma)
            if address_parts:
                address_parts[-1] = f"{address_parts[-1]} {supplier.postal_code}"
            else:
                address_parts.append(supplier.postal_code)

        full_address = ", ".join(address_parts)

        return jsonify(
            {
                "id": supplier.id,
                "name": supplier.name,
                "contact_person": supplier.contact_person,
                "email": supplier.email,
                "phone": supplier.phone,
                "address": supplier.address,
                "city": supplier.city,
                "postal_code": supplier.postal_code,
                "website": supplier.website,
                "full_address": full_address,  # Add the missing field
            }
        )

    @app.route("/api/suppliers/export", methods=["GET"])
    @handle_errors
    def export_suppliers():
        """Export suppliers data"""
        from flask import request

        format_type = request.args.get("format", "json").lower()
        suppliers = supplier_service.get_all()

        if format_type == "json":
            return jsonify(suppliers)
        else:
            return jsonify({"error": "Unsupported format"}), 400

    @app.route("/api/suppliers/bulk-import", methods=["POST"])
    @handle_errors
    def bulk_import_suppliers():
        """Bulk import suppliers"""
        from flask import request
        from pydantic import ValidationError

        data = request.get_json()

        if not data or "suppliers" not in data:
            return jsonify({"error": "Missing suppliers data"}), 422

        suppliers_data = data["suppliers"]
        imported_suppliers = []
        errors = []

        for i, supplier_data in enumerate(suppliers_data):
            try:
                schema = SupplierCreateSchema(**supplier_data)
                validated_data = schema.model_dump(exclude_unset=True)
                supplier = supplier_service.create(validated_data)
                imported_suppliers.append(supplier)
            except ValidationError as e:
                errors.append({"index": i, "data": supplier_data, "errors": e.errors()})
            except Exception as e:
                errors.append({"index": i, "data": supplier_data, "error": str(e)})

        response_data = {
            "imported": imported_suppliers,
            "imported_count": len(imported_suppliers),
            "errors": errors,
            "error_count": len(errors),
        }

        status_code = 201 if len(imported_suppliers) > 0 else 400
        return jsonify(response_data), status_code

    # Plants endpoints
    @app.route("/api/plants", methods=["GET"])
    @handle_errors
    def get_plants():
        """Get all plants"""
        from flask import request
        from sqlalchemy import and_

        from src.models.landscape import Plant

        search = request.args.get("search", "")
        category = request.args.get("category", "")
        sun_exposure = request.args.get("sun_exposure", "")
        native_only = request.args.get("native_only", "").lower() == "true"
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)

        # Validate pagination parameters
        if page < 1 or per_page < 1:
            return jsonify({"error": "Invalid pagination parameters"}), 422

        # Build query with filters
        query = Plant.query

        # Apply filters
        filters = []
        if search:
            filters.append(
                Plant.name.contains(search)
                | Plant.common_name.contains(search)
                | Plant.category.contains(search)
            )

        if category:
            filters.append(Plant.category == category)

        if sun_exposure:
            filters.append(Plant.sun_exposure == sun_exposure)

        if native_only:
            filters.append(Plant.native.is_(True))

        if filters:
            query = query.filter(and_(*filters))

        # Apply pagination
        paginated = query.order_by(Plant.name).paginate(
            page=page, per_page=per_page, error_out=False
        )

        result = {
            "plants": [plant.to_dict() for plant in paginated.items],
            "total": paginated.total,
            "pages": paginated.pages,
            "current_page": page,
        }

        # Always return structured response for consistency
        return jsonify(result)

    @app.route("/api/plants", methods=["POST"])
    @handle_errors
    def create_plant():
        """Create new plant"""
        from flask import request
        from pydantic import ValidationError

        try:
            data = request.get_json()
            if data is None:
                return (
                    jsonify({"error": "Invalid JSON or missing content-type header"}),
                    422,
                )
        except Exception:
            return jsonify({"error": "Invalid JSON format"}), 400

        try:
            # Validate input
            schema = PlantCreateSchema(**data)
            validated_data = schema.model_dump(exclude_unset=True)

            plant = plant_service.create(validated_data)
            return jsonify(plant), 201
        except ValidationError as e:
            # Convert Pydantic errors to string format for consistency
            error_messages = [error.get("msg", str(error)) for error in e.errors()]
            return (
                jsonify(
                    {"error": "Validation failed", "validation_errors": error_messages}
                ),
                422,
            )

    @app.route("/api/plants/<int:plant_id>", methods=["GET"])
    @handle_errors
    def get_plant(plant_id):
        """Get specific plant by ID"""
        from src.models.landscape import Plant

        plant = db.session.get(Plant, plant_id)
        if not plant:
            return jsonify({"error": "Plant not found"}), 404

        return jsonify(plant.to_dict())

    @app.route("/api/plants/<int:plant_id>", methods=["PUT"])
    @handle_errors
    def update_plant(plant_id):
        """Update plant"""
        from flask import request
        from pydantic import ValidationError

        data = request.get_json()

        try:
            # Validate input
            schema = PlantUpdateSchema(**data)
            validated_data = schema.model_dump(exclude_unset=True)

            plant = plant_service.update(plant_id, validated_data)
            if not plant:
                return jsonify({"error": "Plant not found"}), 404

            return jsonify(plant)
        except ValidationError as e:
            # Convert Pydantic errors to string format for consistency
            error_messages = [error.get("msg", str(error)) for error in e.errors()]
            return (
                jsonify(
                    {"error": "Validation failed", "validation_errors": error_messages}
                ),
                422,
            )
        except ValueError as e:
            logger.error("ValueError occurred: %s", str(e), exc_info=True)
            return jsonify({"error": "An internal error occurred"}), 400

    @app.route("/api/plants/<int:plant_id>", methods=["DELETE"])
    @handle_errors
    def delete_plant(plant_id):
        """Delete plant"""
        success = plant_service.delete(plant_id)
        if not success:
            return jsonify({"error": "Plant not found"}), 404

        return jsonify({"message": "Plant deleted successfully"})

    # Additional plant endpoints
    @app.route("/api/plants/categories", methods=["GET"])
    @handle_errors
    def get_plant_categories():
        """Get unique plant categories"""
        from sqlalchemy import distinct

        from src.models.landscape import Plant

        categories = (
            db.session.query(distinct(Plant.category))
            .filter(Plant.category.isnot(None))
            .all()
        )

        return jsonify({"categories": [cat[0] for cat in categories]})

    @app.route("/api/plants/search-suggestions", methods=["GET"])
    @handle_errors
    def plant_search_suggestions():
        """Get plant search suggestions"""
        from flask import request
        from sqlalchemy import or_

        from src.models.landscape import Plant

        query = request.args.get("q", "")
        if not query:
            return jsonify({"suggestions": []})

        # Search in name and common_name with limit
        plants = (
            Plant.query.filter(
                or_(
                    Plant.name.ilike(f"%{query}%"),
                    Plant.common_name.ilike(f"%{query}%"),
                )
            )
            .limit(10)
            .all()
        )

        suggestions = [
            {
                "id": plant.id,
                "name": plant.name,
                "common_name": plant.common_name,
                "category": plant.category,
            }
            for plant in plants
        ]

        return jsonify({"suggestions": suggestions})

    @app.route("/api/plants/export", methods=["GET"])
    @handle_errors
    def export_plants():
        """Export plants data"""
        from flask import request

        format_type = request.args.get("format", "json").lower()
        plants = plant_service.get_all(per_page=1000)  # Get all plants

        if format_type == "json":
            return jsonify({"plants": plants["plants"]})
        else:
            return jsonify({"error": "Unsupported format"}), 400

    @app.route("/api/plants/bulk-import", methods=["POST"])
    @handle_errors
    def bulk_import_plants():
        """Bulk import plants"""
        from flask import request
        from pydantic import ValidationError

        data = request.get_json()

        if not data or "plants" not in data:
            return jsonify({"error": "Missing plants data"}), 422

        plants_data = data["plants"]
        imported_plants = []
        errors = []

        for i, plant_data in enumerate(plants_data):
            try:
                schema = PlantCreateSchema(**plant_data)
                validated_data = schema.model_dump(exclude_unset=True)
                plant = plant_service.create(validated_data)
                imported_plants.append(plant)
            except ValidationError as e:
                errors.append({"index": i, "data": plant_data, "errors": e.errors()})
            except Exception as e:
                errors.append({"index": i, "data": plant_data, "error": str(e)})

        response_data = {
            "imported": imported_plants,
            "imported_count": len(imported_plants),
            "errors": errors,
            "error_count": len(errors),
        }

        status_code = 201 if len(imported_plants) > 0 else 400
        return jsonify(response_data), status_code

    # Products endpoints
    @app.route("/api/products", methods=["GET"])
    @handle_errors
    def get_products():
        """Get all products"""
        from flask import request

        search = request.args.get("search", "")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        result = product_service.get_all(search=search, page=page, per_page=per_page)
        return jsonify(result)

    @app.route("/api/products", methods=["POST"])
    @handle_errors
    def create_product():
        """Create new product"""
        from flask import request
        from pydantic import ValidationError

        data = request.get_json()

        try:
            # Validate input
            schema = ProductCreateSchema(**data)
            validated_data = schema.model_dump(exclude_unset=True)

            product = product_service.create(validated_data)
            return jsonify(product), 201
        except ValidationError as e:
            # Convert Pydantic errors to string format for consistency
            error_messages = [error.get("msg", str(error)) for error in e.errors()]
            return (
                jsonify(
                    {"error": "Validation failed", "validation_errors": error_messages}
                ),
                422,
            )

    @app.route("/api/products/<int:product_id>", methods=["PUT"])
    @handle_errors
    def update_product(product_id):
        """Update product"""
        from flask import request
        from pydantic import ValidationError

        data = request.get_json()

        try:
            # Validate input
            schema = ProductUpdateSchema(**data)
            validated_data = schema.model_dump(exclude_unset=True)

            product = product_service.update(product_id, validated_data)
            if not product:
                return jsonify({"error": "Product not found"}), 404

            return jsonify(product)
        except ValidationError as e:
            # Convert Pydantic errors to string format for consistency
            error_messages = [error.get("msg", str(error)) for error in e.errors()]
            return (
                jsonify(
                    {"error": "Validation failed", "validation_errors": error_messages}
                ),
                422,
            )

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
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        result = client_service.get_all(search=search, page=page, per_page=per_page)
        return jsonify(result)

    @app.route("/api/clients", methods=["POST"])
    @handle_errors
    def create_client():
        """Create new client"""
        from flask import request
        from pydantic import ValidationError

        data = request.get_json()

        try:
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
        except ValidationError as e:
            # Convert Pydantic errors to string format for consistency
            error_messages = [error.get("msg", str(error)) for error in e.errors()]
            return (
                jsonify(
                    {"error": "Validation failed", "validation_errors": error_messages}
                ),
                422,
            )

    @app.route("/api/clients/<int:client_id>", methods=["PUT"])
    @handle_errors
    def update_client(client_id):
        """Update client"""
        from flask import request
        from pydantic import ValidationError

        data = request.get_json()

        try:
            # Validate input
            schema = ClientUpdateSchema(**data)
            validated_data = schema.model_dump(exclude_unset=True)

            client = client_service.update(client_id, validated_data)
            if not client:
                return jsonify({"error": "Client not found"}), 404

            return jsonify(client)
        except ValidationError as e:
            # Convert Pydantic errors to string format for consistency
            error_messages = [error.get("msg", str(error)) for error in e.errors()]
            return (
                jsonify(
                    {"error": "Validation failed", "validation_errors": error_messages}
                ),
                422,
            )

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
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        client_id = int(client_id) if client_id else None

        result = project_service.get_all(
            search=search, client_id=client_id, page=page, per_page=per_page
        )
        return jsonify(result)

    @app.route("/api/projects", methods=["POST"])
    @handle_errors
    def create_project():
        """Create new project"""
        from flask import request
        from pydantic import ValidationError

        data = request.get_json()

        try:
            # Validate input
            schema = ProjectCreateSchema(**data)
            validated_data = schema.model_dump(exclude_unset=True)

            project = project_service.create(validated_data)
            return jsonify(project), 201
        except ValidationError as e:
            # Convert Pydantic errors to string format for consistency
            error_messages = [error.get("msg", str(error)) for error in e.errors()]
            return (
                jsonify(
                    {"error": "Validation failed", "validation_errors": error_messages}
                ),
                422,
            )

    @app.route("/api/projects/<int:project_id>", methods=["PUT"])
    @handle_errors
    def update_project(project_id):
        """Update project"""
        from flask import request
        from pydantic import ValidationError

        data = request.get_json()

        try:
            # Validate input
            schema = ProjectUpdateSchema(**data)
            validated_data = schema.model_dump(exclude_unset=True)

            project = project_service.update(project_id, validated_data)
            if not project:
                return jsonify({"error": "Project not found"}), 404

            return jsonify(project)
        except ValidationError as e:
            # Convert Pydantic errors to string format for consistency
            error_messages = [error.get("msg", str(error)) for error in e.errors()]
            return (
                jsonify(
                    {"error": "Validation failed", "validation_errors": error_messages}
                ),
                422,
            )

    @app.route("/api/projects/<int:project_id>", methods=["DELETE"])
    @handle_errors
    def delete_project(project_id):
        """Delete project"""
        success = project_service.delete(project_id)
        if not success:
            return jsonify({"error": "Project not found"}), 404

        return jsonify({"message": "Project deleted successfully"})

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
    try:
        app = create_app()

        flask_env = os.environ.get("FLASK_ENV", "development")
        port = int(os.environ.get("PORT", 5000))
        # Use 0.0.0.0 for testing to allow CI container access,
        # 127.0.0.1 for development
        host = "0.0.0.0" if flask_env == "testing" else "127.0.0.1"

        logger.info("Starting Landscape Architecture Management System...")
        logger.info(f"Backend API will be available at: http://{host}:{port}")
        logger.info(f"API documentation available at: http://{host}:{port}/api/")

        with app.app_context():
            # Initialize database with error handling
            try:
                initialize_database()
                logger.info("Database initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize database: {str(e)}")
                raise

            # Populate with sample data if empty
            try:
                populate_sample_data()
                logger.info("Sample data population completed")
            except Exception as e:
                logger.error(f"Failed to populate sample data: {str(e)}")
                # Don't fail if sample data population fails
                pass

        # Start the Flask development server (development or integration testing)
        if flask_env in ["development", "testing"]:
            # For testing, disable reloader to avoid issues in CI
            debug_mode = flask_env == "development"
            use_reloader = flask_env == "development"
            logger.info(f"Starting Flask server on {host}:{port} (env: {flask_env})")
            app.run(host=host, port=port, debug=debug_mode, use_reloader=use_reloader)
        else:
            logger.warning(
                "Use a production WSGI server (like Gunicorn) instead of "
                "Flask dev server"
            )
            print("For production, use: gunicorn -c gunicorn.conf.py wsgi:application")

    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise


# Create app instance for WSGI servers (like Waitress, Gunicorn)
app = create_app()


if __name__ == "__main__":
    main()
