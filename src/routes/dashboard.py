from flask import Blueprint, jsonify

from src.models.landscape import Client, Plant, Product, Project, Supplier

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/stats", methods=["GET"])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = {
            "suppliers": Supplier.query.count(),
            "products": Product.query.count(),
            "plants": Plant.query.count(),
            "clients": Client.query.count(),
            "projects": Project.query.count(),
            "active_projects": Project.query.filter_by(status="In Progress").count(),
            "completed_projects": Project.query.filter_by(status="Completed").count(),
            "monthly_revenue": 15420.50,  # This would be calculated from actual project data
        }

        # Get project status distribution
        project_statuses = {}
        for status in ["Planning", "In Progress", "Completed", "On Hold"]:
            count = Project.query.filter_by(status=status).count()
            if count > 0:
                project_statuses[status] = count

        stats["project_status_distribution"] = project_statuses

        # Get product categories
        product_categories = {}
        products = Product.query.all()
        for product in products:
            category = product.category or "Uncategorized"
            product_categories[category] = product_categories.get(category, 0) + 1

        stats["product_categories"] = product_categories

        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/recent-activity", methods=["GET"])
def get_recent_activity():
    """Get recent activity for dashboard"""
    try:
        activities = []

        # Get recent projects
        recent_projects = (
            Project.query.order_by(Project.created_at.desc()).limit(5).all()
        )
        for project in recent_projects:
            activities.append(
                {
                    "type": "project",
                    "message": f'New project "{project.name}" created for {project.client.name}',
                    "timestamp": project.created_at.isoformat(),
                    "icon": "folder",
                }
            )

        # Get recent clients
        recent_clients = Client.query.order_by(Client.created_at.desc()).limit(3).all()
        for client in recent_clients:
            activities.append(
                {
                    "type": "client",
                    "message": f'New client "{client.name}" added',
                    "timestamp": client.created_at.isoformat(),
                    "icon": "user",
                }
            )

        # Sort by timestamp
        activities.sort(key=lambda x: x["timestamp"], reverse=True)

        return jsonify(activities[:10])  # Return top 10 most recent
    except Exception as e:
        return jsonify({"error": str(e)}), 500
