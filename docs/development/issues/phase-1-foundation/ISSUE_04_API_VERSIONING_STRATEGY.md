# Issue 04: API Versioning Strategy - Update 20250901

**Original Issue**: #257  
**Priority**: CRITICAL - Phase 1 Foundation  
**Estimated Effort**: 8-10 hours  
**Dependencies**: Issues 01-03 (Standards, Architecture, Error Handling)  
**Copilot Automation**: Ready

## Current State Assessment

**API Versioning Analysis**:
- ❌ **URL Versioning**: No `/api/v1/` prefix structure
- ❌ **Version Management**: No systematic approach to API evolution
- ❌ **Backward Compatibility**: No compatibility preservation strategy
- ❌ **Documentation Versioning**: No version-specific API docs
- ⚠️ **Current Routes**: Using `/api/` without version indicators

## Implementation Plan

### Step 1: API Version URL Structure
```bash
# Create versioned API blueprint structure
mkdir -p src/api/v1
cat > src/api/__init__.py << 'EOF'
"""
API versioning package for Landscape Architecture Tool
"""
EOF

cat > src/api/v1/__init__.py << 'EOF'
"""
API Version 1 - Initial landscape architecture tool API
"""
from flask import Blueprint

# Create versioned blueprint
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Import and register route modules
from . import (
    dashboard,
    suppliers, 
    plants,
    products,
    clients,
    projects,
    health
)
EOF
```

### Step 2: Version Management System
```bash
# Create API version management
cat > src/api/version_manager.py << 'EOF'
"""
API Version Management System
Handles version routing, compatibility, and deprecation
"""
from typing import Dict, List, Optional, Callable
from flask import Flask, Blueprint, request, jsonify
from datetime import datetime, timedelta
from dataclasses import dataclass
import re

@dataclass
class APIVersion:
    """API version definition."""
    version: str
    release_date: datetime
    deprecation_date: Optional[datetime] = None
    end_of_life_date: Optional[datetime] = None
    is_supported: bool = True
    breaking_changes: List[str] = None
    
    def __post_init__(self):
        if self.breaking_changes is None:
            self.breaking_changes = []

class VersionManager:
    """Manages API versions and routing."""
    
    def __init__(self):
        self.versions: Dict[str, APIVersion] = {}
        self.blueprints: Dict[str, Blueprint] = {}
        self.default_version = None
        self.latest_version = None
    
    def register_version(
        self, 
        version: str, 
        blueprint: Blueprint,
        release_date: datetime,
        deprecation_date: Optional[datetime] = None,
        end_of_life_date: Optional[datetime] = None
    ):
        """Register a new API version."""
        api_version = APIVersion(
            version=version,
            release_date=release_date,
            deprecation_date=deprecation_date,
            end_of_life_date=end_of_life_date
        )
        
        self.versions[version] = api_version
        self.blueprints[version] = blueprint
        
        # Update latest version
        if not self.latest_version or version > self.latest_version:
            self.latest_version = version
        
        # Set first version as default
        if not self.default_version:
            self.default_version = version
    
    def get_version_from_request(self) -> str:
        """Extract version from request path or headers."""
        # Check URL path first (/api/v1/...)
        path_match = re.match(r'/api/v(\d+(?:\.\d+)?)/.*', request.path)
        if path_match:
            return path_match.group(1)
        
        # Check Accept header for version preference
        accept_header = request.headers.get('Accept', '')
        version_match = re.search(r'version=(\d+(?:\.\d+)?)', accept_header)
        if version_match:
            return version_match.group(1)
        
        # Check custom version header
        version_header = request.headers.get('API-Version')
        if version_header:
            return version_header
        
        # Return default version
        return self.default_version
    
    def is_version_supported(self, version: str) -> bool:
        """Check if version is currently supported."""
        if version not in self.versions:
            return False
        
        api_version = self.versions[version]
        now = datetime.utcnow()
        
        # Check if past end of life
        if api_version.end_of_life_date and now > api_version.end_of_life_date:
            return False
        
        return api_version.is_supported
    
    def get_deprecation_warning(self, version: str) -> Optional[Dict[str, str]]:
        """Get deprecation warning for version."""
        if version not in self.versions:
            return None
        
        api_version = self.versions[version]
        now = datetime.utcnow()
        
        # Check if deprecated
        if api_version.deprecation_date and now > api_version.deprecation_date:
            warning = {
                'warning': f'API version {version} is deprecated',
                'deprecated_since': api_version.deprecation_date.isoformat(),
                'latest_version': self.latest_version
            }
            
            if api_version.end_of_life_date:
                warning['end_of_life'] = api_version.end_of_life_date.isoformat()
            
            return warning
        
        return None
    
    def register_with_app(self, app: Flask):
        """Register version manager with Flask app."""
        # Register all blueprints
        for version, blueprint in self.blueprints.items():
            app.register_blueprint(blueprint)
        
        # Add version info endpoint
        @app.route('/api/versions')
        def get_api_versions():
            versions_info = {}
            for version, api_version in self.versions.items():
                versions_info[version] = {
                    'version': version,
                    'release_date': api_version.release_date.isoformat(),
                    'is_supported': self.is_version_supported(version),
                    'deprecation_date': api_version.deprecation_date.isoformat() if api_version.deprecation_date else None,
                    'end_of_life_date': api_version.end_of_life_date.isoformat() if api_version.end_of_life_date else None,
                    'breaking_changes': api_version.breaking_changes
                }
            
            return jsonify({
                'versions': versions_info,
                'default_version': self.default_version,
                'latest_version': self.latest_version
            })
        
        # Add before_request handler for version validation
        @app.before_request
        def validate_api_version():
            if request.path.startswith('/api/v'):
                version = self.get_version_from_request()
                
                if not self.is_version_supported(version):
                    return jsonify({
                        'success': False,
                        'error': 'UNSUPPORTED_API_VERSION',
                        'message': f'API version {version} is not supported',
                        'supported_versions': list(self.versions.keys()),
                        'latest_version': self.latest_version
                    }), 400
        
        # Add after_request handler for deprecation warnings
        @app.after_request
        def add_deprecation_warnings(response):
            if request.path.startswith('/api/v'):
                version = self.get_version_from_request()
                warning = self.get_deprecation_warning(version)
                
                if warning and response.status_code < 400:
                    response.headers['X-API-Deprecation-Warning'] = warning['warning']
                    response.headers['X-API-Latest-Version'] = self.latest_version
            
            return response

# Global version manager instance
version_manager = VersionManager()
EOF
```

### Step 3: Migrate Existing Routes to V1
```bash
# Create V1 versions of existing routes
cat > src/api/v1/suppliers.py << 'EOF'
"""
API V1 - Suppliers endpoints
Versioned wrapper for supplier operations
"""
from flask import jsonify, request
from src.api.v1 import api_v1
from src.routes.suppliers import suppliers_bp
from src.services.core.base_service import BaseService
from src.models.landscape import Supplier
from src.exceptions import ValidationError, ResourceNotFoundError

# Import existing functionality
suppliers_service = BaseService(Supplier)

@api_v1.route('/suppliers', methods=['GET'])
def get_suppliers_v1():
    """Get all suppliers - API V1."""
    try:
        suppliers = suppliers_service.get_all()
        return jsonify({
            'success': True,
            'suppliers': [supplier.to_dict() for supplier in suppliers],
            'total': len(suppliers),
            'api_version': '1.0'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'api_version': '1.0'
        }), 500

@api_v1.route('/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier_v1(supplier_id):
    """Get specific supplier - API V1."""
    try:
        supplier = suppliers_service.get_by_id(supplier_id)
        return jsonify({
            'success': True,
            'supplier': supplier.to_dict(),
            'api_version': '1.0'
        })
    except ResourceNotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'api_version': '1.0'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'api_version': '1.0'
        }), 500

@api_v1.route('/suppliers', methods=['POST'])
def create_supplier_v1():
    """Create new supplier - API V1."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError('request_body', None, 'JSON data required')
        
        supplier = suppliers_service.create(**data)
        return jsonify({
            'success': True,
            'supplier': supplier.to_dict(),
            'message': 'Supplier created successfully',
            'api_version': '1.0'
        }), 201
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'api_version': '1.0'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'api_version': '1.0'
        }), 500
EOF

# Create similar V1 files for other resources
echo "Creating V1 API endpoints for all resources..."
for resource in plants products clients projects dashboard health; do
    cat > src/api/v1/${resource}.py << EOF
"""
API V1 - ${resource^} endpoints
Versioned wrapper for ${resource} operations
"""
from flask import jsonify
from src.api.v1 import api_v1

@api_v1.route('/${resource}', methods=['GET'])
def get_${resource}_v1():
    """Get ${resource} - API V1."""
    return jsonify({
        'success': True,
        'message': '${resource^} endpoint V1 - Implementation pending',
        'api_version': '1.0'
    })
EOF
done
```

### Step 4: Backward Compatibility Layer
```bash
# Create compatibility layer for existing /api/ routes
cat > src/api/compatibility.py << 'EOF'
"""
Backward compatibility layer for existing API routes
Redirects /api/ calls to /api/v1/ with warnings
"""
from flask import Blueprint, request, redirect, url_for, jsonify
from urllib.parse import urljoin

compatibility_bp = Blueprint('api_compatibility', __name__, url_prefix='/api')

@compatibility_bp.before_request
def handle_unversioned_requests():
    """Handle requests to unversioned /api/ endpoints."""
    # Get the path after /api/
    remaining_path = request.path[5:]  # Remove '/api/' prefix
    
    # Construct V1 URL
    v1_url = f'/api/v1{remaining_path}'
    
    # For GET requests, redirect to V1
    if request.method == 'GET':
        return redirect(v1_url, code=301)
    
    # For other methods, return deprecation notice
    return jsonify({
        'success': False,
        'error': 'DEPRECATED_API_ENDPOINT',
        'message': 'Unversioned API endpoints are deprecated. Please use versioned endpoints.',
        'deprecated_endpoint': request.path,
        'recommended_endpoint': v1_url,
        'migration_guide': '/api/versions',
        'deprecation_date': '2025-12-01',
        'end_of_life_date': '2026-06-01'
    }), 400
EOF
```

### Step 5: API Documentation Versioning
```bash
# Create versioned API documentation
mkdir -p docs/api/v1
cat > docs/api/v1/README.md << 'EOF'
# Landscape Architecture Tool API v1.0

## Overview
This is version 1.0 of the Landscape Architecture Tool API, providing comprehensive endpoints for managing landscape architecture projects, plants, suppliers, and related data.

## Base URL
```
https://your-domain.com/api/v1/
```

## Version Information
- **Version**: 1.0
- **Release Date**: September 1, 2025
- **Status**: Stable
- **Deprecation**: Not planned
- **End of Life**: Not planned

## Authentication
All API endpoints require proper authentication headers.

## Common Response Format
All API responses follow a consistent format:

```json
{
  "success": true|false,
  "data": {...},
  "message": "optional message",
  "api_version": "1.0",
  "timestamp": "2025-09-01T12:00:00Z"
}
```

## Error Handling
Errors are returned with appropriate HTTP status codes and detailed error information:

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Human readable error message",
  "details": {...},
  "recovery_suggestions": [...],
  "api_version": "1.0"
}
```

## Endpoints

### Suppliers
- `GET /api/v1/suppliers` - List all suppliers
- `GET /api/v1/suppliers/{id}` - Get specific supplier
- `POST /api/v1/suppliers` - Create new supplier
- `PUT /api/v1/suppliers/{id}` - Update supplier
- `DELETE /api/v1/suppliers/{id}` - Delete supplier

### Plants
- `GET /api/v1/plants` - List all plants
- `GET /api/v1/plants/{id}` - Get specific plant
- `POST /api/v1/plants` - Create new plant
- `PUT /api/v1/plants/{id}` - Update plant
- `DELETE /api/v1/plants/{id}` - Delete plant

### Projects
- `GET /api/v1/projects` - List all projects
- `GET /api/v1/projects/{id}` - Get specific project
- `POST /api/v1/projects` - Create new project
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Version Information
- `GET /api/versions` - Get all available API versions

## Deprecation Policy
- Deprecation warnings are provided 6 months before removal
- End-of-life timeline is communicated clearly
- Migration guides are provided for breaking changes

## Rate Limiting
- Standard rate limits apply
- Limits are communicated via response headers

## Changelog
### v1.0 (2025-09-01)
- Initial API version
- Core CRUD operations for all resources
- Comprehensive error handling
- Standardized response format
EOF
```

## Validation Commands

### After Each Step
```bash
# Test version manager
python -c "
from src.api.version_manager import VersionManager
from datetime import datetime

vm = VersionManager()
vm.register_version('1.0', None, datetime.utcnow())
print(f'Version manager working: latest={vm.latest_version}')
"

# Test V1 API structure
find src/api/v1 -name "*.py" | head -10
python -c "from src.api.v1 import api_v1; print(f'V1 Blueprint: {api_v1.name}')"
```

### Final Validation
```bash
# Comprehensive API versioning validation
python -c "
from src.api.version_manager import version_manager, VersionManager
from src.api.v1 import api_v1
from datetime import datetime

# Test version registration
version_manager.register_version('1.0', api_v1, datetime.utcnow())

print('API Versioning Validation:')
print(f'- Latest version: {version_manager.latest_version}')
print(f'- Default version: {version_manager.default_version}')
print(f'- V1 supported: {version_manager.is_version_supported(\"1.0\")}')
print(f'- Blueprint registered: {api_v1.name}')
"
```

## Testing Requirements

### Unit Tests
```bash
# Create API versioning tests
cat > tests/test_api_versioning.py << 'EOF'
"""Tests for API versioning system."""
import pytest
from datetime import datetime, timedelta
from src.api.version_manager import VersionManager, APIVersion
from src.core.app_factory import create_app

def test_version_manager_registration():
    """Test version registration in version manager."""
    vm = VersionManager()
    
    vm.register_version('1.0', None, datetime.utcnow())
    assert '1.0' in vm.versions
    assert vm.latest_version == '1.0'
    assert vm.default_version == '1.0'

def test_version_support_check():
    """Test version support validation."""
    vm = VersionManager()
    now = datetime.utcnow()
    
    # Active version
    vm.register_version('1.0', None, now)
    assert vm.is_version_supported('1.0') is True
    
    # End-of-life version
    vm.register_version('0.9', None, now - timedelta(days=365), 
                       end_of_life_date=now - timedelta(days=30))
    assert vm.is_version_supported('0.9') is False

def test_deprecation_warning():
    """Test deprecation warning generation."""
    vm = VersionManager()
    now = datetime.utcnow()
    
    vm.register_version('1.0', None, now - timedelta(days=200),
                       deprecation_date=now - timedelta(days=30))
    
    warning = vm.get_deprecation_warning('1.0')
    assert warning is not None
    assert 'deprecated' in warning['warning']

def test_api_v1_endpoints():
    """Test V1 API endpoints respond correctly."""
    app = create_app('testing')
    
    with app.test_client() as client:
        # Test version info endpoint
        response = client.get('/api/versions')
        assert response.status_code == 200
        
        # Test V1 supplier endpoint
        response = client.get('/api/v1/suppliers')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['api_version'] == '1.0'
EOF

# Run API versioning tests
PYTHONPATH=. python -m pytest tests/test_api_versioning.py -v
```

### Integration Tests
```bash
# Test complete versioning system with Flask
PYTHONPATH=. python -c "
from src.core.app_factory import create_app
from src.api.version_manager import version_manager
from src.api.v1 import api_v1
from datetime import datetime

app = create_app('testing')

# Register versioning with app
version_manager.register_version('1.0', api_v1, datetime.utcnow())
version_manager.register_with_app(app)

with app.test_client() as client:
    # Test version info
    response = client.get('/api/versions')
    print(f'Version info: {response.status_code}')
    
    # Test V1 endpoint
    response = client.get('/api/v1/suppliers')
    print(f'V1 suppliers: {response.status_code}')
    
    # Test unversioned redirect
    response = client.get('/api/suppliers')
    print(f'Unversioned redirect: {response.status_code}')
"
```

## Success Criteria

- [ ] URL-based versioning implemented with `/api/v1/` structure
- [ ] Version manager system operational with deprecation handling
- [ ] All existing routes migrated to V1 with enhanced responses
- [ ] Backward compatibility layer for unversioned `/api/` calls
- [ ] Version information endpoint providing API status
- [ ] Comprehensive API documentation for V1
- [ ] All versioning tests passing
- [ ] Integration with error handling system

## Integration with Previous Issues

**Leverages**:
- **Issue 01**: Uses LICENSE and standards for API documentation
- **Issue 02**: Uses enhanced app factory for blueprint registration
- **Issue 03**: Uses centralized error handling for consistent error responses

## Dependencies for Next Issues

This completes Phase 1 foundation, enabling:
- **Phase 2 Issues**: All performance and optimization work
- **Issue 05**: Caching Strategy (requires versioned endpoints for cache keys)
- **Issue 12**: Plant Database Enhancement (requires stable API structure)

## Copilot Automation Instructions

1. Create version manager system with comprehensive deprecation handling
2. Implement V1 API structure with all existing endpoints
3. Add backward compatibility layer with clear migration path
4. Create versioned documentation and changelog
5. Test all endpoints maintain functionality with version information
6. Validate version routing and error handling integration

**Estimated Implementation Time**: 8-10 hours including comprehensive testing and documentation

---

**Phase 1 Complete**: This issue completes the foundation phase, establishing standards, architecture, error handling, and API versioning. All subsequent phases can now build upon this stable foundation.