# VPS Backend Service Fix Instructions

## Problem
The authentication is failing because the Flask backend service is not running properly on the VPS. The 502 Bad Gateway errors indicate that Nginx can't connect to the backend service.

## Solution
Run these commands directly on the VPS (72.60.176.200) as root:

### Step 1: Navigate to Application Directory
```bash
cd /var/www/landscape-architecture-tool || cd /root/landscape-architecture-tool || cd /home/landscape-architecture-tool
pwd  # Confirm you're in the right directory
```

### Step 2: Pull Latest Code from GitHub
```bash
git pull origin main
```

### Step 3: Set Up Virtual Environment
```bash
# If venv doesn't exist, create it
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update requirements
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Stop Any Existing Backend Processes
```bash
# Stop systemd service if it exists
systemctl stop landscape-backend 2>/dev/null || true

# Find and kill any gunicorn processes
ps aux | grep gunicorn
# If you see gunicorn processes, kill them:
# kill -9 [PID_NUMBER]
```

### Step 5: Test Backend Manually
```bash
# Set environment variables
export FLASK_ENV=production
export DATABASE_URL="sqlite:///landscape_architecture_prod.db"

# Test the application
python wsgi.py &
sleep 3

# Test if it responds
curl http://127.0.0.1:5000/api/health

# If it works, kill the test process
kill %1
```

### Step 6: Set Up Systemd Service
```bash
# Copy service file
cp landscape-backend.service /etc/systemd/system/

# Reload systemd and start service
systemctl daemon-reload
systemctl enable landscape-backend
systemctl start landscape-backend

# Check service status
systemctl status landscape-backend
```

### Step 7: Restart Nginx
```bash
systemctl restart nginx
systemctl status nginx
```

### Step 8: Test Authentication
```bash
# Test API endpoints
curl -X GET http://127.0.0.1:5000/api/health
curl -X GET https://optura.nl/api/health

# Test login endpoint
curl -X POST https://optura.nl/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

## Expected Results
- Backend service should be running on port 5000
- API endpoints should return JSON responses instead of 502 errors
- Authentication should work through the web interface

## Troubleshooting
If the service fails to start:
1. Check logs: `journalctl -u landscape-backend -f`
2. Check if port 5000 is in use: `netstat -tlnp | grep 5000`
3. Check application logs in the working directory
4. Verify all dependencies are installed: `pip list | grep -i flask`

## Service Management Commands
```bash
# Start service
systemctl start landscape-backend

# Stop service  
systemctl stop landscape-backend

# Restart service
systemctl restart landscape-backend

# Check status
systemctl status landscape-backend

# View logs
journalctl -u landscape-backend -f
```
