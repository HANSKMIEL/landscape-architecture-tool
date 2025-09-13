# 🔧 Configuration Directory

This directory contains all configuration files for the Landscape Architecture Tool.

## 📋 Configuration Files

### `gunicorn.conf.py`
**Purpose**: Gunicorn WSGI server configuration  
**Usage**: Production deployment configuration for the Flask backend  
**Features**:
- Worker process configuration
- Logging settings
- Performance tuning
- Security settings

### `wsgi.py`
**Purpose**: WSGI application entry point  
**Usage**: Production deployment with Gunicorn or other WSGI servers  
**Features**:
- Flask application factory integration
- Environment configuration
- Production-ready setup

## 🔗 Related Files

### Environment Configuration
- `.env.example` - Environment variables template (root directory)
- `.env` - Local environment variables (not in repository)

### Docker Configuration
- `docker-compose.yml` - Development environment (root directory)
- `docker-compose.production.yml` - Production environment (root directory)
- `docker-compose.n8n.yml` - N8n workflow integration (root directory)

### Python Configuration
- `pyproject.toml` - Python project configuration (root directory)
- `requirements.txt` - Production dependencies (root directory)
- `requirements-dev.txt` - Development dependencies (root directory)

## 🚀 Usage Examples

### Gunicorn Production Deployment
```bash
# Using the configuration file
gunicorn --config config/gunicorn.conf.py config.wsgi:application

# Or with explicit settings
gunicorn --bind 0.0.0.0:5000 --workers 3 config.wsgi:application
```

### WSGI Application
```python
# Import the WSGI application
from config.wsgi import application

# Use with any WSGI server
```

## 📁 Directory Structure

```
config/
├── README.md           # This file
├── gunicorn.conf.py    # Gunicorn configuration
└── wsgi.py            # WSGI entry point
```

---
**Last Updated**: September 13, 2025  
**V1.00D Status**: ✅ Clean Configuration Structure
