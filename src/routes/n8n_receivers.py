"""
N8n receiver routes for handling callbacks from N8n workflows.
These endpoints receive updates and data from N8n workflow executions.
"""

from flask import Blueprint, request, jsonify, current_app
from src.utils.error_handlers import handle_errors
from src.models.landscape import db, Project, Client
from functools import wraps
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('n8n_receivers', __name__, url_prefix='/api/n8n')

def validate_n8n_signature(f):
    """
    Decorator to validate N8n webhook signatures for security
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config.get('N8N_WEBHOOK_SECRET'):
            # If no secret is configured, skip validation (development only)
            logger.warning("N8N_WEBHOOK_SECRET not configured - skipping signature validation")
            return f(*args, **kwargs)
        
        signature = request.headers.get('X-N8N-Signature')
        if not signature:
            logger.error("Missing N8n signature in webhook request")
            return jsonify({'error': 'Missing signature'}), 401
            
        body = request.get_data()
        expected_signature = hmac.new(
            current_app.config['N8N_WEBHOOK_SECRET'].encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(f"sha256={expected_signature}", signature):
            logger.error("Invalid N8n signature in webhook request")
            return jsonify({'error': 'Invalid signature'}), 401
            
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/receive/email-sent', methods=['POST'])
@handle_errors
@validate_n8n_signature
def receive_email_notification():
    """
    Receive notification from N8n about sent emails
    Expected payload: {
        'email_type': str,
        'recipient': str,
        'project_id': int (optional),
        'client_id': int (optional),
        'status': 'sent'|'failed',
        'message_id': str (optional)
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    logger.info(f"Received email notification from N8n: {data}")
    
    # Store email notification in database or update project status
    if data.get('project_id'):
        project = Project.query.get(data['project_id'])
        if project:
            # Update project with email notification info
            # This could be stored in a separate notifications table
            logger.info(f"Email {data.get('status', 'unknown')} for project {project.id}")
    
    return jsonify({'status': 'received', 'message': 'Email notification processed'}), 200

@bp.route('/receive/task-completed', methods=['POST'])
@handle_errors
@validate_n8n_signature
def receive_task_completion():
    """
    Receive task completion status from external workflows
    Expected payload: {
        'task_id': str,
        'task_type': str,
        'status': 'completed'|'failed',
        'project_id': int (optional),
        'result_data': dict (optional),
        'error_message': str (optional)
    }
    """
    data = request.get_json()
    
    if not data or 'task_id' not in data:
        return jsonify({'error': 'task_id is required'}), 400
    
    logger.info(f"Received task completion from N8n: {data}")
    
    # Process task completion based on task type
    task_type = data.get('task_type')
    status = data.get('status')
    
    if task_type == 'document_generation' and status == 'completed':
        # Handle document generation completion
        project_id = data.get('project_id')
        if project_id:
            project = Project.query.get(project_id)
            if project:
                logger.info(f"Document generation completed for project {project.id}")
                # Update project status or add notification
    
    elif task_type == 'invoice_processing' and status == 'completed':
        # Handle invoice processing completion
        logger.info("Invoice processing completed")
        # Update financial records or project billing status
    
    return jsonify({'status': 'received', 'message': 'Task completion processed'}), 200

@bp.route('/receive/external-data', methods=['POST'])
@handle_errors
@validate_n8n_signature
def receive_external_data():
    """
    Receive data from external systems via N8n workflows
    Expected payload: {
        'source_system': str,
        'data_type': str,
        'payload': dict,
        'timestamp': str
    }
    """
    data = request.get_json()
    
    if not data or 'source_system' not in data:
        return jsonify({'error': 'source_system is required'}), 400
    
    logger.info(f"Received external data from {data['source_system']}: {data}")
    
    source_system = data['source_system']
    data_type = data.get('data_type')
    payload = data.get('payload', {})
    
    # Process data based on source system and type
    if source_system == 'crm' and data_type == 'new_lead':
        # Process new lead from CRM system
        logger.info("Processing new lead from CRM")
        # Create new client or update existing client data
        
    elif source_system == 'accounting' and data_type == 'payment_received':
        # Process payment notification from accounting system
        logger.info("Processing payment notification")
        # Update project financial status
        
    return jsonify({'status': 'received', 'message': 'External data processed'}), 200

@bp.route('/status', methods=['GET'])
@handle_errors
def n8n_integration_status():
    """
    Check N8n integration status and connectivity
    """
    try:
        import requests
        n8n_base_url = current_app.config.get('N8N_BASE_URL', 'http://localhost:5678')
        
        # Try to ping N8n
        response = requests.get(f"{n8n_base_url}/healthz", timeout=5)
        n8n_available = response.status_code == 200
        
    except Exception as e:
        logger.error(f"Error checking N8n status: {str(e)}")
        n8n_available = False
    
    return jsonify({
        'n8n_integration': 'enabled',
        'n8n_available': n8n_available,
        'n8n_base_url': current_app.config.get('N8N_BASE_URL', 'not_configured'),
        'webhook_secret_configured': bool(current_app.config.get('N8N_WEBHOOK_SECRET'))
    }), 200