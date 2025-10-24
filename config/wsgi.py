#!/usr/bin/env python3
"""
WSGI entry point for Gunicorn production server
"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import create_app, initialize_database, populate_sample_data

# Create the application with environment configuration
flask_env = os.environ.get("FLASK_ENV", "production")

# Override database URL for this demo if not explicitly set
if flask_env == "production" and not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///landscape_architecture_prod.db"

application = create_app()

# Initialize database for production
with application.app_context():
    initialize_database()
    populate_sample_data()

if __name__ == "__main__":
    application.run()
