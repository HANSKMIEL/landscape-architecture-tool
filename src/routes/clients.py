# Clients API Routes
# File location: src/routes/clients.py
# This file handles all client management operations

from flask import Blueprint, request, jsonify
from src.models.landscape import Client, Project, db
from datetime import datetime

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/api/clients', methods=['GET'])
def get_clients():
    """Get all clients with optional filtering"""
    try:
        # Get query parameters
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # Build query
        query = Client.query
        
        # Apply search filter
        if search:
            query = query.filter(
                db.or_(
                    Client.name.ilike(f'%{search}%'),
                    Client.email.ilike(f'%{search}%'),
                    Client.company.ilike(f'%{search}%'),
                    Client.phone.ilike(f'%{search}%')
                )
            )
        
        # Execute query with pagination
        clients = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format response with project counts
        clients_data = []
        for client in clients.items:
            project_count = Project.query.filter_by(client_id=client.id).count()
            active_projects = Project.query.filter_by(
                client_id=client.id,
                status='in_progress'
            ).count()
            
            clients_data.append({
                'id': client.id,
                'name': client.name,
                'email': client.email,
                'phone': client.phone,
                'company': client.company,
                'address': client.address,
                'city': client.city,
                'postal_code': client.postal_code,
                'country': client.country,
                'notes': client.notes,
                'project_count': project_count,
                'active_projects': active_projects,
                'created_at': client.created_at.isoformat() if client.created_at else None,
                'updated_at': client.updated_at.isoformat() if client.updated_at else None
            })
        
        return jsonify({
            'clients': clients_data,
            'pagination': {
                'page': clients.page,
                'pages': clients.pages,
                'per_page': clients.per_page,
                'total': clients.total,
                'has_next': clients.has_next,
                'has_prev': clients.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/api/clients', methods=['POST'])
def create_client():
    """Create a new client"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Client name is required'}), 400
        
        if not data.get('email'):
            return jsonify({'error': 'Client email is required'}), 400
        
        # Check if email already exists
        existing_client = Client.query.filter_by(email=data['email']).first()
        if existing_client:
            return jsonify({'error': 'Client with this email already exists'}), 400
        
        # Create new client
        client = Client(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            company=data.get('company'),
            address=data.get('address'),
            city=data.get('city'),
            postal_code=data.get('postal_code'),
            country=data.get('country', 'Netherlands'),
            notes=data.get('notes'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(client)
        db.session.commit()
        
        return jsonify({
            'id': client.id,
            'name': client.name,
            'email': client.email,
            'message': 'Client created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/api/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """Get a specific client with their projects"""
    try:
        client = Client.query.get_or_404(client_id)
        
        # Get client's projects
        projects = Project.query.filter_by(client_id=client_id).all()
        projects_data = []
        
        for project in projects:
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'status': project.status,
                'budget': float(project.budget) if project.budget else None,
                'spent': float(project.spent) if project.spent else None,
                'location': project.location,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'created_at': project.created_at.isoformat() if project.created_at else None
            })
        
        return jsonify({
            'id': client.id,
            'name': client.name,
            'email': client.email,
            'phone': client.phone,
            'company': client.company,
            'address': client.address,
            'city': client.city,
            'postal_code': client.postal_code,
            'country': client.country,
            'notes': client.notes,
            'projects': projects_data,
            'project_count': len(projects_data),
            'created_at': client.created_at.isoformat() if client.created_at else None,
            'updated_at': client.updated_at.isoformat() if client.updated_at else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/api/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    """Update an existing client"""
    try:
        client = Client.query.get_or_404(client_id)
        data = request.get_json()
        
        # Check if email is being changed and if it already exists
        if 'email' in data and data['email'] != client.email:
            existing_client = Client.query.filter_by(email=data['email']).first()
            if existing_client:
                return jsonify({'error': 'Client with this email already exists'}), 400
        
        # Update fields
        if 'name' in data:
            client.name = data['name']
        if 'email' in data:
            client.email = data['email']
        if 'phone' in data:
            client.phone = data['phone']
        if 'company' in data:
            client.company = data['company']
        if 'address' in data:
            client.address = data['address']
        if 'city' in data:
            client.city = data['city']
        if 'postal_code' in data:
            client.postal_code = data['postal_code']
        if 'country' in data:
            client.country = data['country']
        if 'notes' in data:
            client.notes = data['notes']
        
        client.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'id': client.id,
            'name': client.name,
            'email': client.email,
            'message': 'Client updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/api/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Delete a client and all associated projects"""
    try:
        client = Client.query.get_or_404(client_id)
        
        # Check if client has projects
        project_count = Project.query.filter_by(client_id=client_id).count()
        
        if project_count > 0:
            # Delete all associated projects first
            Project.query.filter_by(client_id=client_id).delete()
        
        db.session.delete(client)
        db.session.commit()
        
        return jsonify({
            'message': f'Client and {project_count} associated projects deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/api/clients/stats', methods=['GET'])
def get_client_stats():
    """Get client statistics for dashboard"""
    try:
        total_clients = Client.query.count()
        
        # Clients with active projects
        active_clients = db.session.query(Client.id).join(Project).filter(
            Project.status.in_(['planning', 'in_progress'])
        ).distinct().count()
        
        # Recent clients (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_clients = Client.query.filter(
            Client.created_at >= thirty_days_ago
        ).count()
        
        # Top clients by project count
        top_clients = db.session.query(
            Client.name,
            db.func.count(Project.id).label('project_count')
        ).join(Project, Client.id == Project.client_id, isouter=True).group_by(
            Client.id, Client.name
        ).order_by(db.desc('project_count')).limit(5).all()
        
        top_clients_data = [
            {'name': name, 'project_count': count} 
            for name, count in top_clients
        ]
        
        # Geographic distribution
        location_stats = db.session.query(
            Client.city,
            db.func.count(Client.id)
        ).filter(
            Client.city.isnot(None),
            Client.city != ''
        ).group_by(Client.city).order_by(
            db.desc(db.func.count(Client.id))
        ).limit(10).all()
        
        location_distribution = {city: count for city, count in location_stats}
        
        return jsonify({
            'total_clients': total_clients,
            'active_clients': active_clients,
            'recent_clients': recent_clients,
            'top_clients': top_clients_data,
            'location_distribution': location_distribution
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/api/clients/search', methods=['GET'])
def search_clients():
    """Search clients by name, email, or company"""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'clients': []})
        
        clients = Client.query.filter(
            db.or_(
                Client.name.ilike(f'%{query}%'),
                Client.email.ilike(f'%{query}%'),
                Client.company.ilike(f'%{query}%')
            )
        ).limit(limit).all()
        
        clients_data = []
        for client in clients:
            clients_data.append({
                'id': client.id,
                'name': client.name,
                'email': client.email,
                'company': client.company,
                'display_name': f"{client.name} ({client.company})" if client.company else client.name
            })
        
        return jsonify({'clients': clients_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/api/clients/export', methods=['GET'])
def export_clients():
    """Export all clients to JSON"""
    try:
        clients = Client.query.all()
        
        clients_data = []
        for client in clients:
            project_count = Project.query.filter_by(client_id=client.id).count()
            
            clients_data.append({
                'name': client.name,
                'email': client.email,
                'phone': client.phone,
                'company': client.company,
                'address': client.address,
                'city': client.city,
                'postal_code': client.postal_code,
                'country': client.country,
                'notes': client.notes,
                'project_count': project_count,
                'created_at': client.created_at.isoformat() if client.created_at else None
            })
        
        return jsonify({
            'clients': clients_data,
            'count': len(clients_data),
            'exported_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

