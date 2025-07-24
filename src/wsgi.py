#!/usr/bin/env python3
"""
WSGI entry point for production servers (Waitress, Gunicorn, etc.)
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.main import app

# Expose application for WSGI servers
application = app

if __name__ == "__main__":
    # For direct execution, run with Waitress
    try:
        from waitress import serve
        serve(application, host='0.0.0.0', port=8080)
    except ImportError:
        print("Waitress not installed. Install with: pip install waitress")
        application.run(host='0.0.0.0', port=8080)