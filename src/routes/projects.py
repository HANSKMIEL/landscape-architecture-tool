# Projects API Routes
# File location: src/routes/projects.py
# This file handles all project management operations

from datetime import datetime

from flask import Blueprint, jsonify, request

from src.models.landscape import (Client, Plant, Product, Project, db,
                                  project_plants, project_products)

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/api/projects", methods=["GET"])
def get_projects():
    """Get all projects with optional filtering"""
    try:
        # Get query parameters
        search = request.args.get("search", "")
        status = request.args.get("status", "")
        client_id = request.args.get("client_id", "")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))

        # Build query with client join
        query = Project.query.join(Client, Project.client_id == Client.id)

        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    Project.name.ilike(f"%{search}%"),
                    Project.description.ilike(f"%{search}%"),
                    Project.location.ilike(f"%{search}%"),
                    Client.name.ilike(f"%{search}%"),
                )
            )

        if status:
            query = query.filter(Project.status == status)

        if client_id:
            query = query.filter(Project.client_id == int(client_id))

        # Execute query with pagination
        projects = query.paginate(page=page, per_page=per_page, error_out=False)

        # Format response
        projects_data = []
        for project in projects.items:
            # Get associated plants and products
            plants = (
                db.session.query(Plant)
                .join(project_plants)
                .filter(project_plants.c.project_id == project.id)
                .all()
            )

            products = (
                db.session.query(Product)
                .join(project_products)
                .filter(project_products.c.project_id == project.id)
                .all()
            )

            projects_data.append(
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "status": project.status,
                    "budget": (float(project.budget) if project.budget else None),
                    "spent": float(project.spent) if project.spent else None,
                    "location": project.location,
                    "area_size": (
                        float(project.area_size) if project.area_size else None
                    ),
                    "start_date": (
                        project.start_date.isoformat() if project.start_date else None
                    ),
                    "end_date": (
                        project.end_date.isoformat() if project.end_date else None
                    ),
                    "notes": project.notes,
                    "client_id": project.client_id,
                    "client_name": project.client.name,
                    "client_company": project.client.company,
                    "plants": [
                        {
                            "id": p.id,
                            "name": p.name,
                            "scientific_name": p.scientific_name,
                        }
                        for p in plants
                    ],
                    "products": [
                        {"id": p.id, "name": p.name, "category": p.category}
                        for p in products
                    ],
                    "created_at": (
                        project.created_at.isoformat() if project.created_at else None
                    ),
                    "updated_at": (
                        project.updated_at.isoformat() if project.updated_at else None
                    ),
                }
            )

        return jsonify(
            {
                "projects": projects_data,
                "pagination": {
                    "page": projects.page,
                    "pages": projects.pages,
                    "per_page": projects.per_page,
                    "total": projects.total,
                    "has_next": projects.has_next,
                    "has_prev": projects.has_prev,
                },
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/api/projects", methods=["POST"])
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get("name"):
            return jsonify({"error": "Project name is required"}), 400

        if not data.get("client_id"):
            return jsonify({"error": "Client is required"}), 400

        # Verify client exists
        client = Client.query.get(int(data["client_id"]))
        if not client:
            return jsonify({"error": "Client not found"}), 404

        # Create new project
        project = Project(
            name=data["name"],
            description=data.get("description"),
            status=data.get("status", "planning"),
            budget=float(data["budget"]) if data.get("budget") else None,
            spent=float(data["spent"]) if data.get("spent") else None,
            location=data.get("location"),
            area_size=(float(data["area_size"]) if data.get("area_size") else None),
            start_date=(
                datetime.fromisoformat(data["start_date"])
                if data.get("start_date")
                else None
            ),
            end_date=(
                datetime.fromisoformat(data["end_date"])
                if data.get("end_date")
                else None
            ),
            notes=data.get("notes"),
            client_id=int(data["client_id"]),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.session.add(project)
        db.session.flush()  # Get the project ID

        # Add plants if provided
        if data.get("selected_plants"):
            for plant_id in data["selected_plants"]:
                plant = Plant.query.get(int(plant_id))
                if plant:
                    project.plants.append(plant)

        # Add products if provided
        if data.get("selected_products"):
            for product_id in data["selected_products"]:
                product = Product.query.get(int(product_id))
                if product:
                    project.products.append(product)

        db.session.commit()

        return (
            jsonify(
                {
                    "id": project.id,
                    "name": project.name,
                    "client_name": client.name,
                    "message": "Project created successfully",
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/api/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    """Get a specific project with full details"""
    try:
        project = Project.query.get_or_404(project_id)

        # Get associated plants and products
        plants = (
            db.session.query(Plant)
            .join(project_plants)
            .filter(project_plants.c.project_id == project.id)
            .all()
        )

        products = (
            db.session.query(Product)
            .join(project_products)
            .filter(project_products.c.project_id == project.id)
            .all()
        )

        plants_data = []
        for plant in plants:
            plants_data.append(
                {
                    "id": plant.id,
                    "name": plant.name,
                    "scientific_name": plant.scientific_name,
                    "category": plant.category,
                    "sun_requirements": plant.sun_requirements,
                    "water_requirements": plant.water_requirements,
                    "hardiness_zone": plant.hardiness_zone,
                    "mature_height": plant.mature_height,
                    "mature_width": plant.mature_width,
                    "bloom_time": plant.bloom_time,
                    "flower_color": plant.flower_color,
                }
            )

        products_data = []
        for product in products:
            products_data.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "category": product.category,
                    "price": float(product.price) if product.price else None,
                    "unit": product.unit,
                    "sku": product.sku,
                }
            )

        return jsonify(
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "budget": float(project.budget) if project.budget else None,
                "spent": float(project.spent) if project.spent else None,
                "location": project.location,
                "area_size": (float(project.area_size) if project.area_size else None),
                "start_date": (
                    project.start_date.isoformat() if project.start_date else None
                ),
                "end_date": (
                    project.end_date.isoformat() if project.end_date else None
                ),
                "notes": project.notes,
                "client": {
                    "id": project.client.id,
                    "name": project.client.name,
                    "email": project.client.email,
                    "company": project.client.company,
                },
                "plants": plants_data,
                "products": products_data,
                "created_at": (
                    project.created_at.isoformat() if project.created_at else None
                ),
                "updated_at": (
                    project.updated_at.isoformat() if project.updated_at else None
                ),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/api/projects/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    """Update an existing project"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()

        # Update basic fields
        if "name" in data:
            project.name = data["name"]
        if "description" in data:
            project.description = data["description"]
        if "status" in data:
            project.status = data["status"]
        if "budget" in data:
            project.budget = float(data["budget"]) if data["budget"] else None
        if "spent" in data:
            project.spent = float(data["spent"]) if data["spent"] else None
        if "location" in data:
            project.location = data["location"]
        if "area_size" in data:
            project.area_size = float(data["area_size"]) if data["area_size"] else None
        if "start_date" in data:
            project.start_date = (
                datetime.fromisoformat(data["start_date"])
                if data["start_date"]
                else None
            )
        if "end_date" in data:
            project.end_date = (
                datetime.fromisoformat(data["end_date"]) if data["end_date"] else None
            )
        if "notes" in data:
            project.notes = data["notes"]
        if "client_id" in data:
            project.client_id = int(data["client_id"])

        # Update plants if provided
        if "selected_plants" in data:
            # Clear existing plants
            project.plants.clear()
            # Add new plants
            for plant_id in data["selected_plants"]:
                plant = Plant.query.get(int(plant_id))
                if plant:
                    project.plants.append(plant)

        # Update products if provided
        if "selected_products" in data:
            # Clear existing products
            project.products.clear()
            # Add new products
            for product_id in data["selected_products"]:
                product = Product.query.get(int(product_id))
                if product:
                    project.products.append(product)

        project.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify(
            {
                "id": project.id,
                "name": project.name,
                "message": "Project updated successfully",
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/api/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    """Delete a project"""
    try:
        project = Project.query.get_or_404(project_id)

        # Clear many-to-many relationships
        project.plants.clear()
        project.products.clear()

        db.session.delete(project)
        db.session.commit()

        return jsonify({"message": "Project deleted successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/api/projects/stats", methods=["GET"])
def get_project_stats():
    """Get project statistics for dashboard"""
    try:
        total_projects = Project.query.count()

        # Status distribution
        status_stats = (
            db.session.query(Project.status, db.func.count(Project.id))
            .group_by(Project.status)
            .all()
        )

        status_distribution = {status: count for status, count in status_stats}

        # Budget statistics
        budget_stats = (
            db.session.query(
                db.func.sum(Project.budget),
                db.func.sum(Project.spent),
                db.func.avg(Project.budget),
            )
            .filter(Project.budget.isnot(None))
            .first()
        )

        total_budget = float(budget_stats[0]) if budget_stats[0] else 0
        total_spent = float(budget_stats[1]) if budget_stats[1] else 0
        avg_budget = float(budget_stats[2]) if budget_stats[2] else 0

        # Recent projects (last 30 days)
        from datetime import timedelta

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_projects = Project.query.filter(
            Project.created_at >= thirty_days_ago
        ).count()

        # Projects by client
        client_stats = (
            db.session.query(
                Client.name, db.func.count(Project.id).label("project_count")
            )
            .join(Project)
            .group_by(Client.id, Client.name)
            .order_by(db.desc("project_count"))
            .limit(5)
            .all()
        )

        top_clients = [
            {"name": name, "project_count": count} for name, count in client_stats
        ]

        # Monthly project creation trend (last 6 months)
        monthly_stats = (
            db.session.query(
                db.func.date_trunc("month", Project.created_at).label("month"),
                db.func.count(Project.id).label("count"),
            )
            .filter(Project.created_at >= datetime.utcnow() - timedelta(days=180))
            .group_by("month")
            .order_by("month")
            .all()
        )

        monthly_trend = [
            {"month": month.strftime("%Y-%m") if month else "", "count": count}
            for month, count in monthly_stats
        ]

        return jsonify(
            {
                "total_projects": total_projects,
                "status_distribution": status_distribution,
                "budget_stats": {
                    "total_budget": total_budget,
                    "total_spent": total_spent,
                    "avg_budget": avg_budget,
                    "utilization_rate": (
                        (total_spent / total_budget * 100) if total_budget > 0 else 0
                    ),
                },
                "recent_projects": recent_projects,
                "top_clients": top_clients,
                "monthly_trend": monthly_trend,
                "completed_projects": status_distribution.get("completed", 0),
                "in_progress_projects": status_distribution.get("in_progress", 0),
                "planning_projects": status_distribution.get("planning", 0),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/api/projects/<int:project_id>/plants", methods=["POST"])
def add_plant_to_project(project_id):
    """Add a plant to a project"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()

        plant_id = data.get("plant_id")
        if not plant_id:
            return jsonify({"error": "Plant ID is required"}), 400

        plant = Plant.query.get_or_404(int(plant_id))

        # Check if plant is already in project
        if plant in project.plants:
            return jsonify({"error": "Plant is already in this project"}), 400

        project.plants.append(plant)
        project.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify(
            {"message": f'Plant "{plant.name}" added to project "{project.name}"'}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@projects_bp.route(
    "/api/projects/<int:project_id>/plants/<int:plant_id>", methods=["DELETE"]
)
def remove_plant_from_project(project_id, plant_id):
    """Remove a plant from a project"""
    try:
        project = Project.query.get_or_404(project_id)
        plant = Plant.query.get_or_404(plant_id)

        if plant not in project.plants:
            return jsonify({"error": "Plant is not in this project"}), 400

        project.plants.remove(plant)
        project.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify(
            {"message": f'Plant "{plant.name}" removed from project "{project.name}"'}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/api/projects/<int:project_id>/products", methods=["POST"])
def add_product_to_project(project_id):
    """Add a product to a project"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()

        product_id = data.get("product_id")
        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400

        product = Product.query.get_or_404(int(product_id))

        # Check if product is already in project
        if product in project.products:
            return (
                jsonify({"error": "Product is already in this project"}),
                400,
            )

        project.products.append(product)
        project.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify(
            {"message": f'Product "{product.name}" added to project "{project.name}"'}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@projects_bp.route(
    "/api/projects/<int:project_id>/products/<int:product_id>",
    methods=["DELETE"],
)
def remove_product_from_project(project_id, product_id):
    """Remove a product from a project"""
    try:
        project = Project.query.get_or_404(project_id)
        product = Product.query.get_or_404(product_id)

        if product not in project.products:
            return jsonify({"error": "Product is not in this project"}), 400

        project.products.remove(product)
        project.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify(
            {
                "message": f'Product "{product.name}" removed from project "{project.name}"'
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
