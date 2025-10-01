"""
Security documentation routes with admin-only access protection
"""

import logging
from pathlib import Path

from flask import Blueprint, current_app, jsonify, send_file
from werkzeug.exceptions import NotFound

from src.routes.auth import require_role

logger = logging.getLogger(__name__)

security_docs_bp = Blueprint(
    "security_docs", __name__, url_prefix="/api/security"
)


@security_docs_bp.route("/reports/<path:filename>", methods=["GET"])
@require_role("admin")
def get_security_report(filename):
    """
    Get security report - ADMIN ONLY
    
    Only admin users can access security reports and documentation.
    This endpoint is protected by the @require_role('admin') decorator.
    """
    try:
        # Validate filename to prevent directory traversal
        if ".." in filename or filename.startswith("/"):
            return jsonify({"error": "Invalid filename"}), 400
        
        # Build safe path
        base_path = Path(current_app.root_path).parent
        reports_dir = base_path / "reports" / "security"
        file_path = reports_dir / filename
        
        # Verify path is within reports/security directory
        if not str(file_path.resolve()).startswith(str(reports_dir.resolve())):
            return jsonify({"error": "Access denied"}), 403
        
        # Check file exists
        if not file_path.exists():
            return jsonify({"error": "Report not found"}), 404
        
        logger.info(f"Admin user accessing security report: {filename}")
        return send_file(file_path, as_attachment=False)
        
    except NotFound:
        return jsonify({"error": "Report not found"}), 404
    except Exception as e:
        logger.error(f"Error serving security report: {e}")
        return jsonify({"error": "Internal server error"}), 500


@security_docs_bp.route("/reports", methods=["GET"])
@require_role("admin")
def list_security_reports():
    """
    List all security reports - ADMIN ONLY
    
    Only admin users can list available security reports.
    """
    try:
        base_path = Path(current_app.root_path).parent
        reports_dir = base_path / "reports" / "security"
        
        if not reports_dir.exists():
            return jsonify({"reports": []}), 200
        
        reports = []
        for file_path in reports_dir.glob("*.md"):
            stat = file_path.stat()
            reports.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "url": f"/api/security/reports/{file_path.name}"
            })
        
        # Sort by modification time, newest first
        reports.sort(key=lambda x: x["modified"], reverse=True)
        
        logger.info(
            f"Admin user listing security reports: {len(reports)} found"
        )
        return jsonify({"reports": reports}), 200
        
    except Exception as e:
        logger.error(f"Error listing security reports: {e}")
        return jsonify({"error": "Internal server error"}), 500


@security_docs_bp.route("/documentation/<path:filename>", methods=["GET"])
@require_role("admin")
def get_security_documentation(filename):
    """
    Get security documentation - ADMIN ONLY
    
    Only admin users can access security-related documentation.
    """
    try:
        # Validate filename
        if ".." in filename or filename.startswith("/"):
            return jsonify({"error": "Invalid filename"}), 400
        
        # Build safe path - check docs/security or docs/api directories
        docs_dir = Path(current_app.root_path).parent / "docs"
        
        # Try docs/security first
        file_path = docs_dir / "security" / filename
        if not file_path.exists():
            # Try docs/api for API security docs
            file_path = docs_dir / "api" / filename
        
        # Verify path is within docs directory
        if not str(file_path.resolve()).startswith(str(docs_dir.resolve())):
            return jsonify({"error": "Access denied"}), 403
        
        # Check file exists
        if not file_path.exists():
            return jsonify({"error": "Documentation not found"}), 404
        
        logger.info(f"Admin user accessing security documentation: {filename}")
        return send_file(file_path, as_attachment=False)
        
    except NotFound:
        return jsonify({"error": "Documentation not found"}), 404
    except Exception as e:
        logger.error(f"Error serving security documentation: {e}")
        return jsonify({"error": "Internal server error"}), 500
