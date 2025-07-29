"""
Project Service

Handles all project-related business logic and database operations.
"""

from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import or_

from src.models.landscape import Project, Client, ProjectPlant, Plant
from src.models.user import db


class ProjectService:
    """Service class for project operations"""

    @staticmethod
    def get_all_projects(
        search: str = "",
        status: str = "",
        client_id: int = None,
        page: int = 1,
        per_page: int = 50
    ) -> Dict:
        """Get all projects with optional filtering and pagination"""
        query = Project.query.join(Client)

        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Project.name.ilike(search_term),
                    Project.description.ilike(search_term),
                    Project.location.ilike(search_term),
                    Client.name.ilike(search_term)
                )
            )

        if status:
            query = query.filter(Project.status == status)

        if client_id:
            query = query.filter(Project.client_id == client_id)

        # Execute query with pagination
        projects = query.order_by(Project.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            "projects": [project.to_dict() for project in projects.items],
            "total": projects.total,
            "pages": projects.pages,
            "current_page": projects.page,
            "per_page": projects.per_page,
        }

    @staticmethod
    def get_project_by_id(project_id: int) -> Optional[Project]:
        """Get a project by ID"""
        return Project.query.get(project_id)

    @staticmethod
    def create_project(project_data: Dict) -> Project:
        """Create a new project"""
        project = Project(**project_data)
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def update_project(project_id: int, project_data: Dict) -> Optional[Project]:
        """Update an existing project"""
        project = Project.query.get(project_id)
        if not project:
            return None

        for key, value in project_data.items():
            if hasattr(project, key):
                setattr(project, key, value)

        project.updated_at = datetime.utcnow()
        db.session.commit()
        return project

    @staticmethod
    def delete_project(project_id: int) -> bool:
        """Delete a project"""
        project = Project.query.get(project_id)
        if not project:
            return False

        db.session.delete(project)
        db.session.commit()
        return True

    @staticmethod
    def get_projects_by_client(client_id: int) -> List[Project]:
        """Get all projects for a specific client"""
        return Project.query.filter_by(client_id=client_id).order_by(Project.created_at.desc()).all()

    @staticmethod
    def get_projects_by_status(status: str) -> List[Project]:
        """Get all projects with a specific status"""
        return Project.query.filter_by(status=status).order_by(Project.created_at.desc()).all()

    @staticmethod
    def add_plant_to_project(project_id: int, plant_id: int, quantity: int, unit_price: float = None) -> bool:
        """Add a plant to a project"""
        project = Project.query.get(project_id)
        plant = Plant.query.get(plant_id)
        
        if not project or not plant:
            return False

        # Check if plant already exists in project
        existing = ProjectPlant.query.filter_by(
            project_id=project_id, 
            plant_id=plant_id
        ).first()

        if existing:
            existing.quantity += quantity
        else:
            project_plant = ProjectPlant(
                project_id=project_id,
                plant_id=plant_id,
                quantity=quantity,
                unit_price=unit_price or plant.price
            )
            db.session.add(project_plant)

        db.session.commit()
        return True

    @staticmethod
    def remove_plant_from_project(project_id: int, plant_id: int) -> bool:
        """Remove a plant from a project"""
        project_plant = ProjectPlant.query.filter_by(
            project_id=project_id, 
            plant_id=plant_id
        ).first()

        if not project_plant:
            return False

        db.session.delete(project_plant)
        db.session.commit()
        return True

    @staticmethod
    def get_project_plants(project_id: int) -> List[Dict]:
        """Get all plants associated with a project"""
        project_plants = ProjectPlant.query.filter_by(project_id=project_id).all()
        result = []
        
        for project_plant in project_plants:
            plant_data = project_plant.plant.to_dict()
            plant_data.update({
                'quantity': project_plant.quantity,
                'unit_price': project_plant.unit_price,
                'total_price': project_plant.quantity * (project_plant.unit_price or 0),
                'notes': project_plant.notes
            })
            result.append(plant_data)
            
        return result

    @staticmethod
    def calculate_project_cost(project_id: int) -> Dict:
        """Calculate total cost for a project"""
        project_plants = ProjectPlant.query.filter_by(project_id=project_id).all()
        
        total_cost = 0
        plant_costs = []
        
        for project_plant in project_plants:
            unit_price = project_plant.unit_price or 0
            line_total = project_plant.quantity * unit_price
            total_cost += line_total
            
            plant_costs.append({
                'plant_name': project_plant.plant.name,
                'quantity': project_plant.quantity,
                'unit_price': unit_price,
                'line_total': line_total
            })
        
        return {
            'total_cost': total_cost,
            'plant_costs': plant_costs,
            'plant_count': len(plant_costs)
        }

    @staticmethod
    def update_project_status(project_id: int, status: str) -> Optional[Project]:
        """Update project status"""
        project = Project.query.get(project_id)
        if not project:
            return None

        project.status = status
        project.updated_at = datetime.utcnow()
        
        # Set completion date if status is completed
        if status == 'completed':
            project.actual_completion_date = datetime.utcnow()

        db.session.commit()
        return project

    @staticmethod
    def validate_project_data(project_data: Dict) -> List[str]:
        """Validate project data and return list of validation errors"""
        errors = []

        # Required fields
        required_fields = ['name', 'client_id']
        for field in required_fields:
            if not project_data.get(field):
                errors.append(f"{field} is required")

        # Check if client exists
        if project_data.get('client_id'):
            client = Client.query.get(project_data['client_id'])
            if not client:
                errors.append("Invalid client_id")

        # Numeric field validation
        numeric_fields = ['area_size', 'budget']
        for field in numeric_fields:
            value = project_data.get(field)
            if value is not None:
                try:
                    float(value)
                    if float(value) < 0:
                        errors.append(f"{field} must be non-negative")
                except (ValueError, TypeError):
                    errors.append(f"{field} must be a valid number")

        # Date validation
        date_fields = ['start_date', 'target_completion_date']
        for field in date_fields:
            value = project_data.get(field)
            if value:
                try:
                    if isinstance(value, str):
                        datetime.fromisoformat(value)
                except ValueError:
                    errors.append(f"{field} must be a valid ISO date")

        # Status validation
        valid_statuses = ['planning', 'active', 'completed', 'on_hold', 'cancelled']
        if project_data.get('status') and project_data['status'] not in valid_statuses:
            errors.append(f"status must be one of: {', '.join(valid_statuses)}")

        return errors