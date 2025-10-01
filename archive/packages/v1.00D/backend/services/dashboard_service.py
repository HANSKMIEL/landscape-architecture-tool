"""
Dashboard Service

Handles dashboard analytics and summary information.
Enhanced with performance caching for improved response times.
"""

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, func

from src.models.landscape import Client, Plant, Product, Project, ProjectPlant, Supplier
from src.models.user import db
from src.services.performance import (
    cache,
    cache_dashboard_stats,
    monitor_db_performance,
)

# Cache key constants
CACHE_KEY_DASHBOARD_SUMMARY = "dashboard_summary"

# Setup logger
logger = logging.getLogger(__name__)


class DashboardService:
    """Service class for dashboard operations and analytics"""

    @staticmethod
    @monitor_db_performance
    def get_dashboard_summary() -> dict:
        """Get main dashboard summary statistics"""
        # Try to get cached result first

        cache_key = CACHE_KEY_DASHBOARD_SUMMARY

        try:
            cached_result = cache.get(cache_key)
            if cached_result and isinstance(cached_result, dict) and "totals" in cached_result:
                return cached_result
        except Exception as e:
            # Cache error, proceed to generate fresh data
            logger.warning(f"Cache retrieval failed: {e}")

        # Count totals
        total_clients = Client.query.count()
        total_projects = Project.query.count()
        total_plants = Plant.query.count()
        total_suppliers = Supplier.query.count()

        # Active projects
        active_projects = Project.query.filter_by(status="active").count()

        # Projects by status
        projects_by_status = db.session.query(Project.status, func.count(Project.id)).group_by(Project.status).all()

        status_counts = dict(projects_by_status)

        # Recent activity (last 30 days)
        thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
        recent_projects = Project.query.filter(Project.created_at >= thirty_days_ago).count()

        recent_clients = Client.query.filter(Client.created_at >= thirty_days_ago).count()

        # Total budget across all projects
        total_budget = db.session.query(func.sum(Project.budget)).scalar() or 0

        result = {
            "totals": {
                "clients": total_clients,
                "projects": total_projects,
                "plants": total_plants,
                "suppliers": total_suppliers,
                "active_projects": active_projects,
            },
            "projects_by_status": status_counts,
            "recent_activity": {
                "new_projects": recent_projects,
                "new_clients": recent_clients,
            },
            "financial": {"total_budget": total_budget},
        }

        # Ensure all expected keys are present
        result.setdefault("totals", {})
        result.setdefault("recent_activity", {})

        # Cache the valid result
        try:
            cache.set(cache_key, result, timeout=120)
        except (ConnectionError, TimeoutError) as e:
            # Cache error, continue without caching
            logger.warning(f"Failed to set cache for key {cache_key}: {e}")

        return result

    @staticmethod
    def get_project_analytics(days: int = 30) -> dict:
        """Get project analytics for the specified number of days"""
        cutoff_date = datetime.now(UTC) - timedelta(days=days)

        # Projects created over time
        projects_by_date = (
            db.session.query(func.date(Project.created_at), func.count(Project.id))
            .filter(Project.created_at >= cutoff_date)
            .group_by(func.date(Project.created_at))
            .all()
        )

        # Projects by status
        projects_by_status = db.session.query(Project.status, func.count(Project.id)).group_by(Project.status).all()

        # Average project budget
        avg_budget = db.session.query(func.avg(Project.budget)).scalar() or 0

        # Top clients by project count
        top_clients = (
            db.session.query(Client.name, func.count(Project.id))
            .join(Project)
            .group_by(Client.id, Client.name)
            .order_by(desc(func.count(Project.id)))
            .limit(5)
            .all()
        )

        result = {
            "projects_over_time": [{"date": str(date), "count": count} for date, count in projects_by_date],
            "projects_by_status": [{"status": status, "count": count} for status, count in projects_by_status],
            "average_budget": avg_budget,
            "top_clients": [{"name": name, "project_count": count} for name, count in top_clients],
        }

        # Ensure all expected keys are present with appropriate defaults
        result.setdefault("projects_over_time", [])
        result.setdefault("projects_by_status", [])
        result.setdefault("top_clients", [])

        return result

    @staticmethod
    def get_plant_analytics() -> dict:
        """Get plant usage analytics"""
        # Most used plants
        most_used_plants = (
            db.session.query(
                Plant.name,
                Plant.common_name,
                func.sum(ProjectPlant.quantity).label("total_quantity"),
                func.count(ProjectPlant.project_id.distinct()).label("project_count"),
            )
            .join(ProjectPlant)
            .group_by(Plant.id, Plant.name, Plant.common_name)
            .order_by(desc(func.sum(ProjectPlant.quantity)))
            .limit(10)
            .all()
        )

        # Plants by category
        plants_by_category = db.session.query(Plant.category, func.count(Plant.id)).group_by(Plant.category).all()

        # Plants by sun exposure
        plants_by_sun = db.session.query(Plant.sun_exposure, func.count(Plant.id)).group_by(Plant.sun_exposure).all()

        # Native vs non-native plants
        native_count = Plant.query.filter_by(native=True).count()
        non_native_count = Plant.query.filter_by(native=False).count()

        result = {
            "most_used_plants": [
                {
                    "name": name,
                    "common_name": common_name,
                    "total_quantity": int(total_quantity),
                    "project_count": int(project_count),
                }
                for name, common_name, total_quantity, project_count in most_used_plants
            ],
            "plants_by_category": [
                {"category": category, "count": count} for category, count in plants_by_category if category
            ],
            "plants_by_sun_exposure": [
                {"sun_exposure": exposure, "count": count} for exposure, count in plants_by_sun if exposure
            ],
            "native_distribution": {
                "native": native_count,
                "non_native": non_native_count,
            },
        }

        # Ensure all expected keys are present with appropriate defaults
        result.setdefault("most_used_plants", [])
        result.setdefault("plants_by_category", [])
        result.setdefault("plants_by_sun_exposure", [])
        result.setdefault("native_distribution", {"native": 0, "non_native": 0})

        return result

    @staticmethod
    def get_financial_analytics() -> dict:
        """Get financial analytics"""
        # Total project value
        total_project_value = db.session.query(func.sum(Project.budget)).scalar() or 0

        # Average project value
        avg_project_value = db.session.query(func.avg(Project.budget)).scalar() or 0

        # Project values by status
        values_by_status = db.session.query(Project.status, func.sum(Project.budget)).group_by(Project.status).all()

        # Top projects by budget
        top_projects = (
            db.session.query(Project.name, Project.budget, Client.name.label("client_name"))
            .join(Client)
            .filter(Project.budget.isnot(None))
            .order_by(desc(Project.budget))
            .limit(5)
            .all()
        )

        # Monthly project value trends (last 12 months)
        twelve_months_ago = datetime.now(UTC) - timedelta(days=365)
        monthly_values = (
            db.session.query(
                func.strftime("%Y-%m", Project.created_at).label("month"),
                func.sum(Project.budget).label("total_value"),
            )
            .filter(Project.created_at >= twelve_months_ago, Project.budget.isnot(None))
            .group_by(func.strftime("%Y-%m", Project.created_at))
            .order_by("month")
            .all()
        )

        result = {
            "total_project_value": total_project_value,
            "average_project_value": avg_project_value,
            "values_by_status": [
                {"status": status, "total_value": float(total) if total else 0} for status, total in values_by_status
            ],
            "top_projects": [
                {
                    "name": name,
                    "budget": float(budget) if budget else 0,
                    "client_name": client_name,
                }
                for name, budget, client_name in top_projects
            ],
            "monthly_trends": [
                {
                    "month": str(month),
                    "total_value": float(total_value) if total_value else 0,
                }
                for month, total_value in monthly_values
            ],
        }

        # Ensure all expected keys are present with appropriate defaults
        result.setdefault("values_by_status", [])
        result.setdefault("top_projects", [])
        result.setdefault("monthly_trends", [])

        return result

    @staticmethod
    def get_supplier_analytics() -> dict:
        """Get supplier analytics"""
        # Total suppliers
        total_suppliers = Supplier.query.count()

        # Use separate subqueries to avoid Cartesian product
        # Product counts subquery
        product_counts = (
            db.session.query(
                Supplier.id.label("supplier_id"),
                func.count(Product.id).label("product_count"),
            )
            .outerjoin(Product)
            .group_by(Supplier.id)
            .subquery()
        )

        # Plant counts subquery
        plant_counts = (
            db.session.query(
                Supplier.id.label("supplier_id"),
                func.count(Plant.id).label("plant_count"),
            )
            .outerjoin(Plant)
            .group_by(Supplier.id)
            .subquery()
        )

        # Main query combining both counts
        suppliers_by_products = (
            db.session.query(
                Supplier.name,
                func.coalesce(product_counts.c.product_count, 0).label("product_count"),
                func.coalesce(plant_counts.c.plant_count, 0).label("plant_count"),
            )
            .outerjoin(product_counts, Supplier.id == product_counts.c.supplier_id)
            .outerjoin(plant_counts, Supplier.id == plant_counts.c.supplier_id)
            .order_by(
                desc(func.coalesce(product_counts.c.product_count, 0) + func.coalesce(plant_counts.c.plant_count, 0))
            )
            .limit(5)
            .all()
        )

        # Suppliers by specialization
        specializations = (
            db.session.query(Supplier.specialization, func.count(Supplier.id))
            .filter(Supplier.specialization.isnot(None))
            .group_by(Supplier.specialization)
            .all()
        )

        result = {
            "total_suppliers": total_suppliers,
            "top_suppliers": [
                {
                    "name": name,
                    "product_count": int(product_count),
                    "plant_count": int(plant_count),
                    "total_items": int(product_count) + int(plant_count),
                }
                for name, product_count, plant_count in suppliers_by_products
            ],
            "specializations": [{"specialization": spec, "count": count} for spec, count in specializations if spec],
        }

        # Ensure all expected keys are present with appropriate defaults
        result.setdefault("top_suppliers", [])
        result.setdefault("specializations", [])

        return result

    @staticmethod
    @cache_dashboard_stats
    @monitor_db_performance
    def get_recent_activity(limit: int = 10) -> dict:
        """Get recent activity across the system"""
        # Recent projects
        recent_projects = Project.query.order_by(desc(Project.created_at)).limit(limit).all()

        # Recent clients
        recent_clients = Client.query.order_by(desc(Client.created_at)).limit(limit).all()

        # Recent plants
        recent_plants = Plant.query.order_by(desc(Plant.created_at)).limit(limit).all()

        result = {
            "recent_projects": [
                {
                    "id": project.id,
                    "name": project.name,
                    "client_name": project.client.name if project.client else None,
                    "created_at": (project.created_at.isoformat() if project.created_at else None),
                    "status": project.status,
                }
                for project in recent_projects
            ],
            "recent_clients": [
                {
                    "id": client.id,
                    "name": client.name,
                    "company": client.company,
                    "created_at": (client.created_at.isoformat() if client.created_at else None),
                }
                for client in recent_clients
            ],
            "recent_plants": [
                {
                    "id": plant.id,
                    "name": plant.name,
                    "common_name": plant.common_name,
                    "category": plant.category,
                    "created_at": (plant.created_at.isoformat() if plant.created_at else None),
                }
                for plant in recent_plants
            ],
        }

        # Ensure all expected keys are present with appropriate defaults
        result.setdefault("recent_projects", [])
        result.setdefault("recent_clients", [])
        result.setdefault("recent_plants", [])

        return result

    @staticmethod
    def get_performance_metrics() -> dict:
        """Get system performance metrics"""
        # Calculate completion rates
        total_projects = Project.query.count()
        completed_projects = Project.query.filter_by(status="completed").count()
        completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0

        # Average project duration (for completed projects)
        completed_with_dates = Project.query.filter(
            Project.status == "completed",
            Project.start_date.isnot(None),
            Project.actual_completion_date.isnot(None),
        ).all()

        total_duration = 0
        valid_projects = 0
        for project in completed_with_dates:
            try:
                # Handle the fact that start_date is a string and
                # actual_completion_date is a date
                if isinstance(project.start_date, str):
                    start_date = datetime.fromisoformat(project.start_date).date()
                else:
                    start_date = project.start_date

                if isinstance(project.actual_completion_date, str):
                    end_date = datetime.fromisoformat(project.actual_completion_date).date()
                else:
                    end_date = project.actual_completion_date

                duration = (end_date - start_date).days
                if duration > 0:
                    total_duration += duration
                    valid_projects += 1
            except (ValueError, TypeError, AttributeError):
                continue

        avg_duration = (total_duration / valid_projects) if valid_projects > 0 else 0

        # Plant utilization rate
        total_plants = Plant.query.count()
        used_plants = db.session.query(ProjectPlant.plant_id).distinct().count()
        plant_utilization = (used_plants / total_plants * 100) if total_plants > 0 else 0

        result = {
            "project_completion_rate": completion_rate,
            "average_project_duration_days": avg_duration,
            "plant_utilization_rate": plant_utilization,
            "total_entities": {
                "clients": Client.query.count(),
                "projects": total_projects,
                "plants": total_plants,
                "suppliers": Supplier.query.count(),
            },
        }

        # Ensure all expected keys are present with appropriate defaults
        result.setdefault("total_entities", {})

        return result

    @staticmethod
    def get_stats() -> dict:
        """Get dashboard statistics (alias for get_dashboard_summary)"""
        return DashboardService.get_dashboard_summary()
