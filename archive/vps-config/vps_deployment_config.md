# VPS Deployment Configuration

## Production Environment Setup

### Server Details
- **VPS IP**: 72.60.176.200
- **Domain**: optura.nl
- **SSL**: Let's Encrypt (configured)
- **Web Server**: Nginx
- **Application Server**: Gunicorn with 3 workers

### Environment Variables
```bash
SECRET_KEY=landscape-tool-production-secret-key-12345
FLASK_ENV=production
```

### Systemd Service Configuration
**File**: `/etc/systemd/system/landscape-backend.service`
```ini
[Unit]
Description=Landscape Architecture Tool Backend API
After=network.target

[Service]
Type=forking
User=root
WorkingDirectory=/var/www/landscape-architecture-tool
Environment="SECRET_KEY=landscape-tool-production-secret-key-12345"
EnvironmentFile=/etc/environment
ExecStart=/var/www/landscape-architecture-tool/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 3 --timeout 120 wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration
**File**: `/etc/nginx/sites-available/optura.nl`
```nginx
server {
    listen 80;
    server_name optura.nl www.optura.nl;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name optura.nl www.optura.nl;

    ssl_certificate /etc/letsencrypt/live/optura.nl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/optura.nl/privkey.pem;

    root /var/www/landscape-architecture-tool/frontend/dist;
    index index.html;

    # Frontend static files
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy to backend
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Database Configuration
- **Type**: SQLite (production ready)
- **Location**: `/var/www/landscape-architecture-tool/instance/landscape.db`
- **Initialization**: Automatic on first run

### Default Users Created
1. **Admin User**
   - Username: `admin`
   - Password: `admin123`
   - Role: `admin`
   - Email: `admin@optura.nl`

2. **Demo User**
   - Username: `demo`
   - Password: `demo123`
   - Role: `user`
   - Email: `demo@optura.nl`

3. **Client User**
   - Username: `client`
   - Password: `client123`
   - Role: `client`
   - Email: `client@optura.nl`

### Deployment Commands
```bash
# Update application
cd /var/www/landscape-architecture-tool
git pull origin main

# Install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Build frontend
cd frontend
npm install
npm run build

# Restart services
systemctl restart landscape-backend
systemctl restart nginx

# Check status
systemctl status landscape-backend
curl https://optura.nl/health
```

### Monitoring and Logs
```bash
# Backend service logs
journalctl -u landscape-backend -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Service status
systemctl status landscape-backend
systemctl status nginx
```

### Security Features
- SSL/TLS encryption (Let's Encrypt)
- Password hashing with Werkzeug
- Session management with Flask-Session
- Account lockout after failed attempts
- Role-based access control
- CORS protection
- Rate limiting

### Backup Recommendations
```bash
# Database backup
cp /var/www/landscape-architecture-tool/instance/landscape.db /backup/landscape-$(date +%Y%m%d).db

# Application backup
tar -czf /backup/landscape-app-$(date +%Y%m%d).tar.gz /var/www/landscape-architecture-tool
```
