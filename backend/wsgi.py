#!/usr/bin/env python3
"""
WSGI entry point for production servers (Waitress, Gunicorn, etc.)
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.main import app  # noqa: E402

# Expose application for WSGI servers
application = app

if __name__ == "__main__":
    # For direct execution, run with Waitress
    # Use environment variable to control host binding for security
    host = (
        "0.0.0.0" if os.environ.get("ALLOW_ALL_INTERFACES", "").lower() == "true" else "127.0.0.1"
    )  # nosec B104 # Controlled by environment variable
    port = int(os.environ.get("PORT", 8080))

    try:
        from waitress import serve

        serve(application, host=host, port=port)
    except ImportError:
        print("Waitress not installed. Install with: pip install waitress")
        application.run(host=host, port=port)
