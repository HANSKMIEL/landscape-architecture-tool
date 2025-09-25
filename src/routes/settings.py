"""API routes for application settings management."""

import json
import os
from datetime import datetime
from flask import Blueprint, jsonify, request, session
from flask_cors import cross_origin

from src.models.user import User
from src.utils.decorators import login_required

settings_bp = Blueprint("settings", __name__)

# Default settings structure
DEFAULT_SETTINGS = {
    "appearance": {
        "theme": "light",
        "language": "en",
        "primary_color": "#3b82f6",
        "font_size": "medium",
        "branding": {
            "company_name": "Landscape Architecture Tool",
            "logo_url": "",
            "custom_css": ""
        }
    },
    "data_management": {
        "auto_backup": True,
        "backup_frequency": "weekly",
        "excel_import": {
            "default_supplier": "",
            "auto_validate": True,
            "duplicate_handling": "skip"
        },
        "ai_assistant": {
            "enabled": True,
            "auto_suggestions": True,
            "confidence_threshold": 0.8
        }
    },
    "integrations": {
        "apis": {
            "vectorworks": {
                "enabled": False,
                "api_key": "",
                "endpoint": ""
            },
            "crm": {
                "enabled": False,
                "type": "",
                "credentials": {}
            }
        },
        "n8n": {
            "enabled": True,
            "webhook_url": "",
            "workflows": {
                "client_onboarding": True,
                "project_updates": True,
                "inventory_alerts": True
            }
        }
    },
    "reports": {
        "default_format": "pdf",
        "auto_generation": {
            "business_summary": "monthly",
            "plant_usage": "quarterly",
            "supplier_performance": "monthly"
        },
        "templates": {
            "company_header": True,
            "watermark": False,
            "custom_footer": ""
        }
    },
    "security": {
        "session_timeout": 8,  # hours
        "password_policy": {
            "min_length": 8,
            "require_uppercase": True,
            "require_numbers": True,
            "require_symbols": False
        },
        "two_factor": {
            "enabled": False,
            "method": "email"
        }
    }
}

def get_settings_file_path():
    """Get the path to the settings file"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'settings.json')

def load_settings():
    """Load settings from file or return defaults"""
    settings_file = get_settings_file_path()
    
    try:
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                return merge_settings(DEFAULT_SETTINGS, settings)
        else:
            return DEFAULT_SETTINGS.copy()
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to file"""
    settings_file = get_settings_file_path()
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        
        # Add metadata
        settings['_metadata'] = {
            'updated_at': datetime.now().isoformat(),
            'updated_by': session.get('user_id'),
            'version': '1.0'
        }
        
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def merge_settings(defaults, user_settings):
    """Recursively merge user settings with defaults"""
    result = defaults.copy()
    
    for key, value in user_settings.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_settings(result[key], value)
        else:
            result[key] = value
    
    return result

@settings_bp.route("/api/settings", methods=["GET"])
@login_required
def get_settings():
    """Get application settings"""
    try:
        settings = load_settings()
        
        # Remove sensitive information for client
        client_settings = settings.copy()
        if 'security' in client_settings:
            # Only send non-sensitive security settings
            client_settings['security'] = {
                'session_timeout': client_settings['security'].get('session_timeout', 8),
                'two_factor': {
                    'enabled': client_settings['security'].get('two_factor', {}).get('enabled', False)
                }
            }
        
        # Remove API keys and credentials
        if 'integrations' in client_settings:
            for integration_type, config in client_settings['integrations'].items():
                if isinstance(config, dict):
                    for service, service_config in config.items():
                        if isinstance(service_config, dict):
                            # Remove sensitive keys
                            for key in ['api_key', 'credentials', 'secret', 'token']:
                                if key in service_config:
                                    service_config[key] = '***' if service_config[key] else ''
        
        return jsonify({
            "settings": client_settings,
            "status": "success"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@settings_bp.route("/api/settings", methods=["POST"])
@login_required
def update_settings():
    """Update application settings"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Load current settings
        current_settings = load_settings()
        
        # Update with new settings
        updated_settings = merge_settings(current_settings, data)
        
        # Validate settings (basic validation)
        if 'appearance' in updated_settings:
            appearance = updated_settings['appearance']
            if 'theme' in appearance and appearance['theme'] not in ['light', 'dark', 'auto']:
                return jsonify({"error": "Invalid theme value"}), 400
            if 'language' in appearance and appearance['language'] not in ['en', 'nl']:
                return jsonify({"error": "Invalid language value"}), 400
        
        # Save settings
        if save_settings(updated_settings):
            return jsonify({
                "message": "Settings updated successfully",
                "status": "success"
            }), 200
        else:
            return jsonify({"error": "Failed to save settings"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@settings_bp.route("/api/settings/reset", methods=["POST"])
@login_required
def reset_settings():
    """Reset settings to defaults"""
    try:
        if save_settings(DEFAULT_SETTINGS.copy()):
            return jsonify({
                "message": "Settings reset to defaults",
                "status": "success"
            }), 200
        else:
            return jsonify({"error": "Failed to reset settings"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@settings_bp.route("/api/settings/export", methods=["GET"])
@login_required
def export_settings():
    """Export current settings"""
    try:
        settings = load_settings()
        
        # Remove sensitive information
        export_settings = settings.copy()
        if 'integrations' in export_settings:
            for integration_type, config in export_settings['integrations'].items():
                if isinstance(config, dict):
                    for service, service_config in config.items():
                        if isinstance(service_config, dict):
                            # Remove sensitive keys
                            for key in ['api_key', 'credentials', 'secret', 'token']:
                                if key in service_config:
                                    del service_config[key]
        
        return jsonify({
            "settings": export_settings,
            "exported_at": datetime.now().isoformat(),
            "version": "1.0"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@settings_bp.route("/api/settings/import", methods=["POST"])
@login_required
def import_settings():
    """Import settings from uploaded data"""
    try:
        data = request.get_json()
        
        if not data or 'settings' not in data:
            return jsonify({"error": "No settings data provided"}), 400
        
        imported_settings = data['settings']
        
        # Validate imported settings structure
        if not isinstance(imported_settings, dict):
            return jsonify({"error": "Invalid settings format"}), 400
        
        # Merge with current settings (preserving sensitive data)
        current_settings = load_settings()
        merged_settings = merge_settings(current_settings, imported_settings)
        
        # Save merged settings
        if save_settings(merged_settings):
            return jsonify({
                "message": "Settings imported successfully",
                "status": "success"
            }), 200
        else:
            return jsonify({"error": "Failed to import settings"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500