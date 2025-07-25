import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask_sqlalchemy import SQLAlchemy

from src.models.landscape import Client, Plant, Product, Project, Supplier
from src.models.user import db

logger = logging.getLogger(__name__)


class BaseService:
    """Base service class with common CRUD operations"""

    def __init__(self, model_class):
        self.model_class = model_class

    def get_all(
        self, search: str = None, page: int = 1, per_page: int = 50
    ) -> Dict[str, Any]:
        """Get all entities with optional search and pagination"""
        try:
            query = self.model_class.query

            if search and hasattr(self.model_class, "name"):
                query = query.filter(self.model_class.name.contains(search))

            paginated = query.order_by(self.model_class.id).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return {
                "items": [item.to_dict() for item in paginated.items],
                "total": paginated.total,
                "pages": paginated.pages,
                "current_page": page,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
            }
        except Exception as e:
            logger.error(f"Error getting all {self.model_class.__name__}: {str(e)}")
            raise

    def get_by_id(self, entity_id: int) -> Optional[Any]:
        """Get entity by ID"""
        try:
            entity = self.model_class.query.get(entity_id)
            return entity.to_dict() if entity else None
        except Exception as e:
            logger.error(
                f"Error getting {self.model_class.__name__} by ID {entity_id}: {str(e)}"
            )
            raise

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new entity"""
        try:
            entity = self.model_class(**data)
            db.session.add(entity)
            db.session.commit()
            logger.info(f"Created {self.model_class.__name__}: {entity.id}")
            return entity.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating {self.model_class.__name__}: {str(e)}")
            raise

    def update(self, entity_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update entity"""
        try:
            entity = self.model_class.query.get(entity_id)
            if not entity:
                return None

            for key, value in data.items():
                if hasattr(entity, key) and value is not None:
                    setattr(entity, key, value)

            db.session.commit()
            logger.info(f"Updated {self.model_class.__name__}: {entity_id}")
            return entity.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(
                f"Error updating {self.model_class.__name__} {entity_id}: {str(e)}"
            )
            raise

    def delete(self, entity_id: int) -> bool:
        """Delete entity"""
        try:
            entity = self.model_class.query.get(entity_id)
            if not entity:
                return False

            db.session.delete(entity)
            db.session.commit()
            logger.info(f"Deleted {self.model_class.__name__}: {entity_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(
                f"Error deleting {self.model_class.__name__} {entity_id}: {str(e)}"
            )
            raise


class SupplierService(BaseService):
    """Service for supplier operations"""

    def __init__(self):
        super().__init__(Supplier)

    def get_all(
        self, search: str = None, page: int = 1, per_page: int = 50
    ) -> Dict[str, Any]:
        """Get all suppliers with search functionality"""
        try:
            query = Supplier.query

            if search:
                query = query.filter(
                    Supplier.name.contains(search)
                    | Supplier.contact_person.contains(search)
                    | Supplier.city.contains(search)
                )

            paginated = query.order_by(Supplier.name).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return {
                "suppliers": [supplier.to_dict() for supplier in paginated.items],
                "total": paginated.total,
                "pages": paginated.pages,
                "current_page": page,
            }
        except Exception as e:
            logger.error(f"Error getting suppliers: {str(e)}")
            raise


class PlantService(BaseService):
    """Service for plant operations"""

    def __init__(self):
        super().__init__(Plant)

    def get_all(
        self, search: str = None, page: int = 1, per_page: int = 50
    ) -> Dict[str, Any]:
        """Get all plants with search functionality"""
        try:
            query = Plant.query

            if search:
                query = query.filter(
                    Plant.name.contains(search)
                    | Plant.common_name.contains(search)
                    | Plant.category.contains(search)
                )

            paginated = query.order_by(Plant.name).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return {
                "plants": [plant.to_dict() for plant in paginated.items],
                "total": paginated.total,
                "pages": paginated.pages,
                "current_page": page,
            }
        except Exception as e:
            logger.error(f"Error getting plants: {str(e)}")
            raise


class ProductService(BaseService):
    """Service for product operations"""

    def __init__(self):
        super().__init__(Product)

    def get_all(
        self, search: str = None, page: int = 1, per_page: int = 50
    ) -> Dict[str, Any]:
        """Get all products with search functionality"""
        try:
            query = Product.query

            if search:
                query = query.filter(
                    Product.name.contains(search)
                    | Product.category.contains(search)
                    | Product.description.contains(search)
                )

            paginated = query.order_by(Product.name).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return {
                "products": [product.to_dict() for product in paginated.items],
                "total": paginated.total,
                "pages": paginated.pages,
                "current_page": page,
            }
        except Exception as e:
            logger.error(f"Error getting products: {str(e)}")
            raise


class ClientService(BaseService):
    """Service for client operations"""

    def __init__(self):
        super().__init__(Client)

    def get_all(
        self, search: str = None, page: int = 1, per_page: int = 50
    ) -> Dict[str, Any]:
        """Get all clients with search functionality"""
        try:
            query = Client.query

            if search:
                query = query.filter(
                    Client.name.contains(search)
                    | Client.contact_person.contains(search)
                    | Client.city.contains(search)
                )

            paginated = query.order_by(Client.name).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return {
                "clients": [client.to_dict() for client in paginated.items],
                "total": paginated.total,
                "pages": paginated.pages,
                "current_page": page,
            }
        except Exception as e:
            logger.error(f"Error getting clients: {str(e)}")
            raise


class ProjectService(BaseService):
    """Service for project operations"""

    def __init__(self):
        super().__init__(Project)

    def get_all(
        self,
        search: str = None,
        client_id: int = None,
        page: int = 1,
        per_page: int = 50,
    ) -> Dict[str, Any]:
        """Get all projects with search and client filtering"""
        try:
            query = Project.query

            if client_id:
                query = query.filter(Project.client_id == client_id)

            if search:
                query = query.filter(
                    Project.name.contains(search)
                    | Project.description.contains(search)
                    | Project.location.contains(search)
                )

            paginated = query.order_by(Project.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return {
                "projects": [project.to_dict() for project in paginated.items],
                "total": paginated.total,
                "pages": paginated.pages,
                "current_page": page,
            }
        except Exception as e:
            logger.error(f"Error getting projects: {str(e)}")
            raise


class DashboardService:
    """Service for dashboard statistics and data"""

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            stats = {
                "suppliers": Supplier.query.count(),
                "plants": Plant.query.count(),
                "products": Product.query.count(),
                "clients": Client.query.count(),
                "projects": Project.query.count(),
                "active_projects": Project.query.filter(
                    Project.status == "In uitvoering"
                ).count(),
                "completed_projects": Project.query.filter(
                    Project.status == "Afgerond"
                ).count(),
                "total_budget": float(
                    db.session.query(db.func.sum(Project.budget)).scalar() or 0
                ),
                "last_updated": datetime.now().isoformat(),
            }
            logger.info("Dashboard stats generated successfully")
            return stats
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            raise

    @staticmethod
    def get_recent_activity() -> List[Dict[str, Any]]:
        """Get recent activity for dashboard"""
        try:
            # For now, return static activity data
            # In a real implementation, this would come from an activity log table
            activities = [
                {
                    "id": 1,
                    "type": "project_update",
                    "title": "Project Vondelpark Renovatie bijgewerkt",
                    "description": 'Status gewijzigd naar "In uitvoering"',
                    "timestamp": "2024-07-24T10:30:00",
                    "user": "Hans Kmiel",
                },
                {
                    "id": 2,
                    "type": "client_added",
                    "title": "Nieuwe klant toegevoegd",
                    "description": "Villa Rozenhof geregistreerd",
                    "timestamp": "2024-07-23T14:15:00",
                    "user": "Hans Kmiel",
                },
                {
                    "id": 3,
                    "type": "product_updated",
                    "title": "Product voorraad bijgewerkt",
                    "description": "Premium Tuinaarde voorraad aangepast",
                    "timestamp": "2024-07-22T09:45:00",
                    "user": "Hans Kmiel",
                },
            ]
            return activities
        except Exception as e:
            logger.error(f"Error getting recent activity: {str(e)}")
            raise
