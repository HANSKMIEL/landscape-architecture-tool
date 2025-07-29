"""
Client Service

Handles all client-related business logic and database operations.
"""

from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import or_

from src.models.landscape import Client, Project
from src.models.user import db


class ClientService:
    """Service class for client operations"""

    @staticmethod
    def get_all_clients(
        search: str = "",
        page: int = 1,
        per_page: int = 50
    ) -> Dict:
        """Get all clients with optional filtering and pagination"""
        query = Client.query

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Client.name.ilike(search_term),
                    Client.email.ilike(search_term),
                    Client.company.ilike(search_term),
                    Client.phone.ilike(search_term)
                )
            )

        # Execute query with pagination
        clients = query.order_by(Client.name).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Add project counts to each client
        clients_data = []
        for client in clients.items:
            client_dict = client.to_dict()
            client_dict['project_count'] = Project.query.filter_by(client_id=client.id).count()
            client_dict['active_projects'] = Project.query.filter_by(
                client_id=client.id, 
                status='active'
            ).count()
            clients_data.append(client_dict)

        return {
            "clients": clients_data,
            "total": clients.total,
            "pages": clients.pages,
            "current_page": clients.page,
            "per_page": clients.per_page,
        }

    @staticmethod
    def get_client_by_id(client_id: int) -> Optional[Client]:
        """Get a client by ID"""
        return Client.query.get(client_id)

    @staticmethod
    def create_client(client_data: Dict) -> Client:
        """Create a new client"""
        client = Client(**client_data)
        db.session.add(client)
        db.session.commit()
        return client

    @staticmethod
    def update_client(client_id: int, client_data: Dict) -> Optional[Client]:
        """Update an existing client"""
        client = Client.query.get(client_id)
        if not client:
            return None

        for key, value in client_data.items():
            if hasattr(client, key):
                setattr(client, key, value)

        client.updated_at = datetime.utcnow()
        db.session.commit()
        return client

    @staticmethod
    def delete_client(client_id: int) -> bool:
        """Delete a client"""
        client = Client.query.get(client_id)
        if not client:
            return False

        # Check if client has active projects
        active_projects = Project.query.filter_by(
            client_id=client_id, 
            status='active'
        ).count()
        
        if active_projects > 0:
            return False  # Cannot delete client with active projects

        db.session.delete(client)
        db.session.commit()
        return True

    @staticmethod
    def get_client_projects(client_id: int) -> List[Project]:
        """Get all projects for a specific client"""
        return Project.query.filter_by(client_id=client_id).order_by(Project.created_at.desc()).all()

    @staticmethod
    def get_client_statistics(client_id: int) -> Dict:
        """Get statistical information for a client"""
        client = Client.query.get(client_id)
        if not client:
            return {}

        projects = Project.query.filter_by(client_id=client_id).all()
        
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.status == 'active'])
        completed_projects = len([p for p in projects if p.status == 'completed'])
        
        total_budget = sum(p.budget or 0 for p in projects)
        total_area = sum(p.area_size or 0 for p in projects)
        
        return {
            'client_id': client_id,
            'client_name': client.name,
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'total_budget': total_budget,
            'total_area': total_area,
            'average_project_budget': total_budget / total_projects if total_projects > 0 else 0
        }

    @staticmethod
    def search_clients(search_term: str) -> List[Client]:
        """Search clients by name, email, company, or phone"""
        search_term = f"%{search_term}%"
        return Client.query.filter(
            or_(
                Client.name.ilike(search_term),
                Client.email.ilike(search_term),
                Client.company.ilike(search_term),
                Client.phone.ilike(search_term)
            )
        ).order_by(Client.name).all()

    @staticmethod
    def validate_client_data(client_data: Dict) -> List[str]:
        """Validate client data and return list of validation errors"""
        errors = []

        # Required fields
        required_fields = ['name']
        for field in required_fields:
            if not client_data.get(field):
                errors.append(f"{field} is required")

        # Email validation
        if client_data.get('email'):
            email = client_data['email']
            if '@' not in email or '.' not in email:
                errors.append("Invalid email format")
            
            # Check for duplicate email
            existing_client = Client.query.filter_by(email=email).first()
            if existing_client and existing_client.id != client_data.get('id'):
                errors.append("Email already exists")

        # Phone validation
        if client_data.get('phone'):
            phone = client_data['phone'].replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not phone.replace('+', '').isdigit():
                errors.append("Invalid phone number format")

        return errors

    @staticmethod
    def get_clients_by_company(company: str) -> List[Client]:
        """Get all clients from a specific company"""
        return Client.query.filter_by(company=company).order_by(Client.name).all()

    @staticmethod
    def get_top_clients_by_projects(limit: int = 10) -> List[Dict]:
        """Get top clients by number of projects"""
        clients = Client.query.all()
        client_stats = []
        
        for client in clients:
            project_count = Project.query.filter_by(client_id=client.id).count()
            if project_count > 0:
                client_stats.append({
                    'client': client.to_dict(),
                    'project_count': project_count
                })
        
        # Sort by project count and limit
        client_stats.sort(key=lambda x: x['project_count'], reverse=True)
        return client_stats[:limit]

    @staticmethod
    def get_top_clients_by_budget(limit: int = 10) -> List[Dict]:
        """Get top clients by total project budget"""
        clients = Client.query.all()
        client_stats = []
        
        for client in clients:
            projects = Project.query.filter_by(client_id=client.id).all()
            total_budget = sum(p.budget or 0 for p in projects)
            
            if total_budget > 0:
                client_stats.append({
                    'client': client.to_dict(),
                    'total_budget': total_budget,
                    'project_count': len(projects)
                })
        
        # Sort by total budget and limit
        client_stats.sort(key=lambda x: x['total_budget'], reverse=True)
        return client_stats[:limit]