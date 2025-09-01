# N8n Integration Implementation Guide for Landscape Architecture Tool

## 🎯 Implementation Overview

This guide provides step-by-step instructions for integrating N8n workflow automation with the Landscape Architecture Tool, including deployment to Hostinger VPS.

## 📋 Prerequisites

### System Requirements
- Ubuntu 22.04 LTS server (Hostinger VPS or similar)
- Docker and Docker Compose installed
- Domain name with DNS pointing to your server
- SSL certificate (Let's Encrypt recommended)
- At least 4GB RAM and 2 CPU cores

### Development Environment
```bash
# Verify Docker installation
docker --version
docker-compose --version

# Verify current application is working
cd /path/to/landscape-architecture-tool
make backend-test
make build
```

## 🔧 Phase 1: Backend API Extensions

### Step 1.1: Create Webhook Routes

Create the webhook routes for N8n integration:

```bash
# Create new webhook routes file
touch src/routes/webhooks.py
```

**File: `src/routes/webhooks.py`**
```python
"""
Webhook routes for N8n integration.
These endpoints allow the Landscape Tool to trigger N8n workflows.
"""

from flask import Blueprint, request, jsonify, current_app
from src.utils.error_handlers import handle_errors
from src.models.landscape import db
import requests
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')

def trigger_n8n_workflow(webhook_url, data):
    """
    Helper function to trigger N8n workflows via webhook
    """
    try:
        n8n_base_url = current_app.config.get('N8N_BASE_URL', 'http://localhost:5678')
        full_url = f"{n8n_base_url}/webhook/{webhook_url}"
        
        response = requests.post(
            full_url,
            json=data,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully triggered N8n workflow: {webhook_url}")
            return True
        else:
            logger.error(f"Failed to trigger N8n workflow: {webhook_url}, Status: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        logger.error(f"Error triggering N8n workflow {webhook_url}: {str(e)}")
        return False

@bp.route('/n8n/project-created', methods=['POST'])
@handle_errors
def trigger_project_created():
    """
    Trigger N8n workflow when a new project is created
    Expected payload: {'project_id': int, 'client_id': int, 'project_name': str}
    """
    data = request.get_json()
    
    if not data or 'project_id' not in data:
        return jsonify({'error': 'project_id is required'}), 400
    
    # Prepare data for N8n workflow
    workflow_data = {
        'event': 'project_created',
        'project_id': data['project_id'],
        'client_id': data.get('client_id'),
        'project_name': data.get('project_name'),
        'timestamp': data.get('timestamp'),
        'created_by': data.get('created_by')
    }
    
    success = trigger_n8n_workflow('project-created', workflow_data)
    
    if success:
        return jsonify({'status': 'workflow_triggered', 'webhook': 'project-created'}), 200
    else:
        return jsonify({'status': 'workflow_failed', 'webhook': 'project-created'}), 500

@bp.route('/n8n/client-updated', methods=['POST'])
@handle_errors
def trigger_client_updated():
    """
    Trigger N8n workflow when client information is updated
    Expected payload: {'client_id': int, 'updated_fields': list, 'client_data': dict}
    """
    data = request.get_json()
    
    if not data or 'client_id' not in data:
        return jsonify({'error': 'client_id is required'}), 400
    
    workflow_data = {
        'event': 'client_updated',
        'client_id': data['client_id'],
        'updated_fields': data.get('updated_fields', []),
        'client_data': data.get('client_data', {}),
        'timestamp': data.get('timestamp')
    }
    
    success = trigger_n8n_workflow('client-updated', workflow_data)
    
    if success:
        return jsonify({'status': 'workflow_triggered', 'webhook': 'client-updated'}), 200
    else:
        return jsonify({'status': 'workflow_failed', 'webhook': 'client-updated'}), 500

@bp.route('/n8n/project-milestone', methods=['POST'])
@handle_errors
def trigger_project_milestone():
    """
    Trigger N8n workflow when a project reaches a milestone
    Expected payload: {'project_id': int, 'milestone': str, 'status': str}
    """
    data = request.get_json()
    
    if not data or 'project_id' not in data or 'milestone' not in data:
        return jsonify({'error': 'project_id and milestone are required'}), 400
    
    workflow_data = {
        'event': 'project_milestone',
        'project_id': data['project_id'],
        'milestone': data['milestone'],
        'status': data.get('status'),
        'completion_percentage': data.get('completion_percentage'),
        'timestamp': data.get('timestamp')
    }
    
    success = trigger_n8n_workflow('project-milestone', workflow_data)
    
    if success:
        return jsonify({'status': 'workflow_triggered', 'webhook': 'project-milestone'}), 200
    else:
        return jsonify({'status': 'workflow_failed', 'webhook': 'project-milestone'}), 500

@bp.route('/n8n/inventory-alert', methods=['POST'])
@handle_errors
def trigger_inventory_alert():
    """
    Trigger N8n workflow for low inventory alerts
    Expected payload: {'plant_id': int, 'current_stock': int, 'minimum_threshold': int}
    """
    data = request.get_json()
    
    if not data or 'plant_id' not in data:
        return jsonify({'error': 'plant_id is required'}), 400
    
    workflow_data = {
        'event': 'inventory_alert',
        'plant_id': data['plant_id'],
        'plant_name': data.get('plant_name'),
        'current_stock': data.get('current_stock', 0),
        'minimum_threshold': data.get('minimum_threshold', 0),
        'supplier_id': data.get('supplier_id'),
        'timestamp': data.get('timestamp')
    }
    
    success = trigger_n8n_workflow('inventory-alert', workflow_data)
    
    if success:
        return jsonify({'status': 'workflow_triggered', 'webhook': 'inventory-alert'}), 200
    else:
        return jsonify({'status': 'workflow_failed', 'webhook': 'inventory-alert'}), 500
```

### Step 1.2: Create N8n Receiver Routes

Create routes to receive data from N8n workflows:

```bash
# Create N8n receiver routes file
touch src/routes/n8n_receivers.py
```

**File: `src/routes/n8n_receivers.py`**
```python
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
```

### Step 1.3: Register New Routes

Update the main application to register the new routes:

**Update: `src/main.py`**
```python
# Add these imports at the top
from src.routes import webhooks, n8n_receivers

# Add these registrations in the create_app() function after existing blueprints
def create_app():
    # ... existing code ...
    
    # Register existing blueprints
    # ... existing registrations ...
    
    # Register N8n integration blueprints
    app.register_blueprint(webhooks.bp)
    app.register_blueprint(n8n_receivers.bp)
    
    # ... rest of existing code ...
```

### Step 1.4: Add Configuration Variables

**Update: `src/config.py`**
```python
# Add N8n configuration variables
class Config:
    # ... existing configuration ...
    
    # N8n Integration Configuration
    N8N_BASE_URL = os.environ.get('N8N_BASE_URL', 'http://localhost:5678')
    N8N_WEBHOOK_SECRET = os.environ.get('N8N_WEBHOOK_SECRET')
    N8N_BASIC_AUTH_USER = os.environ.get('N8N_BASIC_AUTH_USER', 'admin')
    N8N_BASIC_AUTH_PASSWORD = os.environ.get('N8N_BASIC_AUTH_PASSWORD')
    
    # Webhook timeout settings
    N8N_WEBHOOK_TIMEOUT = int(os.environ.get('N8N_WEBHOOK_TIMEOUT', '30'))
```

## 🐳 Phase 2: Docker Compose Integration

### Step 2.1: Update Docker Compose Configuration

**Update: `docker-compose.yml`**
```yaml
version: '3.8'

services:
  # Existing services...
  landscape-backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://landscape_user:landscape_password@postgres:5432/landscape_architecture_prod
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=your-secret-key-here
      - FLASK_ENV=production
      # N8n integration environment variables
      - N8N_BASE_URL=http://n8n:5678
      - N8N_WEBHOOK_SECRET=your-webhook-secret-here
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=secure-n8n-password
    depends_on:
      - postgres
      - redis
      - n8n
    networks:
      - landscape-network

  landscape-frontend:
    build: ./frontend
    ports:
      - "5174:80"
    depends_on:
      - landscape-backend
    networks:
      - landscape-network

  # New N8n service
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      # Database configuration
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n_db
      - DB_POSTGRESDB_USER=n8n_user
      - DB_POSTGRESDB_PASSWORD=n8n_password
      
      # Basic authentication
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=secure-n8n-password
      
      # Webhook configuration
      - WEBHOOK_URL=https://yourdomain.com/
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      
      # Timezone and locale
      - GENERIC_TIMEZONE=Europe/Amsterdam
      - N8N_DEFAULT_LOCALE=en
      
      # Security settings
      - N8N_SECURE_COOKIE=false
      - N8N_COOKIES_SECURE=false
      
      # Execution settings
      - EXECUTIONS_PROCESS=main
      - EXECUTIONS_TIMEOUT=3600
      - EXECUTIONS_TIMEOUT_MAX=7200
      
    volumes:
      - n8n_data:/home/node/.n8n
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - postgres
    networks:
      - landscape-network
    restart: unless-stopped

  # Enhanced Nginx with N8n routing
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-n8n.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
    depends_on:
      - landscape-frontend
      - landscape-backend
      - n8n
    networks:
      - landscape-network
    restart: unless-stopped

  # Enhanced PostgreSQL with N8n database
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=landscape_architecture_prod
      - POSTGRES_USER=landscape_user
      - POSTGRES_PASSWORD=landscape_password
      # Multiple database support
      - POSTGRES_MULTIPLE_DATABASES=n8n_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-multiple-databases.sh:/docker-entrypoint-initdb.d/init-multiple-databases.sh:ro
    ports:
      - "5432:5432"
    networks:
      - landscape-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - landscape-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  n8n_data:

networks:
  landscape-network:
    driver: bridge
```

### Step 2.2: Create Database Initialization Script

**Create: `scripts/init-multiple-databases.sh`**
```bash
#!/bin/bash
set -e
set -u

function create_user_and_database() {
    local database=$1
    local user=$2
    local password=$3
    echo "Creating user '$user' and database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        CREATE USER $user WITH PASSWORD '$password';
        CREATE DATABASE $database;
        GRANT ALL PRIVILEGES ON DATABASE $database TO $user;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    
    # Create N8n database and user
    create_user_and_database "n8n_db" "n8n_user" "n8n_password"
    
    echo "Multiple databases created"
fi
```

### Step 2.3: Create Enhanced Nginx Configuration

**Create: `nginx-n8n.conf`**
```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 50M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Upstream definitions
    upstream landscape_backend {
        server landscape-backend:5000;
    }
    
    upstream n8n_service {
        server n8n:5678;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=webhook:10m rate=30r/s;
    
    # HTTP server (redirect to HTTPS)
    server {
        listen 80;
        server_name _;
        
        # Allow Let's Encrypt challenges
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        # Redirect all other HTTP traffic to HTTPS
        location / {
            return 301 https://$host$request_uri;
        }
    }
    
    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name _;
        
        # SSL Configuration (update paths for your certificates)
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_stapling on;
        ssl_stapling_verify on;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
        
        # Landscape Architecture Tool API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://landscape_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        # Health check endpoint
        location /health {
            proxy_pass http://landscape_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Webhooks (outgoing from Landscape Tool to N8n)
        location /webhooks/ {
            limit_req zone=webhook burst=50 nodelay;
            
            proxy_pass http://landscape_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # N8n Interface (secured with basic auth)
        location /n8n/ {
            # Optional: Add IP whitelist for N8n admin interface
            # allow 192.168.1.0/24;
            # deny all;
            
            proxy_pass http://n8n_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for N8n
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            # Increased timeouts for long-running workflows
            proxy_connect_timeout 300s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }
        
        # N8n Webhooks (incoming from external systems to N8n)
        location /webhook/ {
            limit_req zone=webhook burst=100 nodelay;
            
            proxy_pass http://n8n_service/webhook/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Allow larger payloads for webhook data
            client_max_body_size 10M;
        }
        
        # Landscape Frontend (catch-all)
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
            
            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }
    }
}
```

## 📊 Phase 3: Sample N8n Workflows

### Step 3.1: Client Onboarding Workflow

**N8n Workflow JSON (import into N8n):**
```json
{
  "name": "Client Onboarding Automation",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "/webhook/client-onboarding",
        "responseMode": "responseNode",
        "options": {}
      },
      "id": "webhook-client-created",
      "name": "Webhook - Client Created",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [100, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json.client_email}}",
              "operation": "isNotEmpty"
            }
          ]
        }
      },
      "id": "check-email-exists",
      "name": "Check Email Exists",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [300, 300]
    },
    {
      "parameters": {
        "fromEmail": "noreply@landscapetool.com",
        "toEmail": "={{$json.client_email}}",
        "subject": "Welcome to our Landscape Architecture Services",
        "text": "Dear {{$json.client_name}},\n\nWelcome to our landscape architecture services! We're excited to work with you on your project.\n\nNext steps:\n1. We'll schedule an initial consultation\n2. Our team will prepare a project proposal\n3. You'll receive a detailed timeline and quote\n\nBest regards,\nLandscape Architecture Team",
        "options": {}
      },
      "id": "send-welcome-email",
      "name": "Send Welcome Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [500, 200]
    },
    {
      "parameters": {
        "url": "http://landscape-backend:5000/api/n8n/receive/email-sent",
        "sendBody": true,
        "bodyContentType": "json",
        "jsonBody": "{\n  \"email_type\": \"welcome\",\n  \"recipient\": \"{{$json.client_email}}\",\n  \"client_id\": {{$json.client_id}},\n  \"status\": \"sent\",\n  \"timestamp\": \"{{$now}}\"\n}",
        "options": {}
      },
      "id": "notify-backend-email-sent",
      "name": "Notify Backend Email Sent",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [700, 200]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "{\n  \"status\": \"success\",\n  \"message\": \"Client onboarding workflow completed\",\n  \"client_id\": {{$json.client_id}}\n}"
      },
      "id": "respond-success",
      "name": "Respond Success",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [900, 300]
    }
  ],
  "connections": {
    "Webhook - Client Created": {
      "main": [
        [
          {
            "node": "Check Email Exists",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Check Email Exists": {
      "main": [
        [
          {
            "node": "Send Welcome Email",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Respond Success",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Send Welcome Email": {
      "main": [
        [
          {
            "node": "Notify Backend Email Sent",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Notify Backend Email Sent": {
      "main": [
        [
          {
            "node": "Respond Success",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## 🌐 Phase 4: Hostinger VPS Deployment

### Step 4.1: Server Preparation

```bash
# Connect to your Hostinger VPS
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create application directory
mkdir -p /opt/landscape-architecture-tool
cd /opt/landscape-architecture-tool
```

### Step 4.2: Environment Configuration

**Create: `.env.production`**
```bash
# Database Configuration
DATABASE_URL=postgresql://landscape_user:CHANGE_THIS_PASSWORD@postgres:5432/landscape_architecture_prod
REDIS_URL=redis://redis:6379/0

# Application Security
SECRET_KEY=CHANGE_THIS_TO_VERY_LONG_RANDOM_STRING
FLASK_ENV=production
DEBUG=false

# N8n Integration
N8N_BASE_URL=http://n8n:5678
N8N_WEBHOOK_SECRET=CHANGE_THIS_WEBHOOK_SECRET
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=CHANGE_THIS_N8N_PASSWORD

# Domain Configuration
DOMAIN_NAME=yourdomain.com
SSL_EMAIL=your-email@domain.com

# PostgreSQL Configuration
POSTGRES_DB=landscape_architecture_prod
POSTGRES_USER=landscape_user
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD

# N8n Database Configuration  
N8N_DB_USER=n8n_user
N8N_DB_PASSWORD=CHANGE_THIS_N8N_DB_PASSWORD
```

### Step 4.3: SSL Certificate Setup

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Create webroot directory
mkdir -p /var/www/certbot

# Initial certificate generation (after DNS is pointed to your server)
certbot certonly --webroot --webroot-path=/var/www/certbot --email your-email@domain.com --agree-tos --no-eff-email -d yourdomain.com

# Copy certificates to nginx directory
mkdir -p /opt/landscape-architecture-tool/ssl
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/landscape-architecture-tool/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/landscape-architecture-tool/ssl/key.pem

# Set up auto-renewal
(crontab -l 2>/dev/null; echo "0 2 * * * certbot renew --post-hook 'docker-compose -f /opt/landscape-architecture-tool/docker-compose.yml restart nginx'") | crontab -
```

### Step 4.4: Deploy Application

```bash
# Clone your repository
git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git .

# Make scripts executable
chmod +x scripts/init-multiple-databases.sh

# Deploy with production configuration
docker-compose -f docker-compose.yml --env-file .env.production up -d

# Check deployment status
docker-compose ps
docker-compose logs -f
```

### Step 4.5: Firewall Configuration

```bash
# Configure UFW firewall
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

# Optional: Restrict N8n access to specific IPs
# ufw allow from YOUR_IP_ADDRESS to any port 5678
```

## 🔍 Phase 5: Testing and Validation

### Step 5.1: Test Application Endpoints

```bash
# Test landscape tool health
curl https://yourdomain.com/health

# Test API endpoint
curl https://yourdomain.com/api/

# Test N8n integration status
curl https://yourdomain.com/api/n8n/status
```

### Step 5.2: Test N8n Integration

```bash
# Test webhook trigger (replace with real data)
curl -X POST https://yourdomain.com/webhooks/n8n/project-created \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "client_id": 1,
    "project_name": "Test Project",
    "timestamp": "2024-01-01T12:00:00Z"
  }'

# Check N8n interface
# Navigate to https://yourdomain.com/n8n/
# Login with your configured credentials
```

## 📋 Phase 6: Monitoring and Maintenance

### Step 6.1: Set Up Monitoring

**Create: `docker-compose.monitoring.yml`**
```yaml
version: '3.8'

services:
  # Add monitoring services
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - landscape-network

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - landscape-network

volumes:
  grafana_data:

networks:
  landscape-network:
    external: true
```

### Step 6.2: Backup Strategy

```bash
#!/bin/bash
# backup.sh - Create daily backups

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL databases
docker exec landscape-architecture-tool_postgres_1 pg_dump -U landscape_user landscape_architecture_prod > $BACKUP_DIR/landscape_$DATE.sql
docker exec landscape-architecture-tool_postgres_1 pg_dump -U n8n_user n8n_db > $BACKUP_DIR/n8n_$DATE.sql

# Backup N8n workflows and data
docker exec landscape-architecture-tool_n8n_1 tar -czf - /home/node/.n8n > $BACKUP_DIR/n8n_data_$DATE.tar.gz

# Backup application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /opt/landscape-architecture-tool --exclude='node_modules' --exclude='.git'

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

## 📚 Documentation and User Guide

### API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/webhooks/n8n/project-created` | POST | Trigger workflow when project is created |
| `/webhooks/n8n/client-updated` | POST | Trigger workflow when client is updated |
| `/webhooks/n8n/project-milestone` | POST | Trigger workflow for project milestones |
| `/webhooks/n8n/inventory-alert` | POST | Trigger workflow for inventory alerts |
| `/api/n8n/receive/email-sent` | POST | Receive email notification from N8n |
| `/api/n8n/receive/task-completed` | POST | Receive task completion from N8n |
| `/api/n8n/receive/external-data` | POST | Receive external system data via N8n |
| `/api/n8n/status` | GET | Check N8n integration status |

### Workflow Examples

1. **Client Onboarding**: Automated welcome emails and setup
2. **Project Milestones**: Progress notifications and reporting
3. **Inventory Management**: Low stock alerts and reordering
4. **Invoice Processing**: Automated invoice generation and sending
5. **External Integrations**: CRM, accounting, and communication tools

## 🎯 Success Metrics

After implementation, measure:
- **Automation Rate**: Percentage of manual tasks automated
- **Time Savings**: Hours saved per week through automation
- **Error Reduction**: Decrease in manual process errors
- **Client Satisfaction**: Improved communication and response times
- **Team Productivity**: Increased focus on core landscape architecture work

---

*This implementation guide provides comprehensive steps for integrating N8n with your Landscape Architecture Tool, enabling powerful workflow automation while maintaining security and performance standards.*